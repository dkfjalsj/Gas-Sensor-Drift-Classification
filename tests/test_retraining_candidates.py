# 합성 정답 자료로 후보 학습·누수 차단·저장 복구 검증
# 실제 신규 센서 성능 검증이 아님

import hashlib
import json
from pathlib import Path
import shutil

import numpy as np
import pandas as pd
import pytest
from sklearn.pipeline import Pipeline

from src.data import FEATURES, ROOT
from src.retraining import candidates as c, datasets as d
from src.retraining.evaluation import evaluate_model
from src.webapp import dataset_registry as registry
from src.webapp.data_preparation import load_training_reference
from src.webapp.service import MODEL_PATH, MODEL_SHA, DETECTOR_PATH, DETECTOR_SHA


def payload(frame):
    return frame.to_csv(index=False).encode('utf-8-sig')


def synthetic_source(n=120, shift=0):
    target = np.arange(n) % 6 + 1
    values = np.random.default_rng(142 + shift).normal(0, 0.2, (n, 128))
    frame = pd.DataFrame(values + target[:, None] * 50 + shift, columns=FEATURES)
    frame['gas'] = target
    sessions = pd.DataFrame({
        'input_row': np.arange(1, n + 1),
        'session_id': ['synthetic_early'] * (n // 2) + ['synthetic_late'] * (n - n // 2),
        'measured_at': ['2026-01-01T00:00:00+00:00'] * (n // 2)
        + ['2026-01-02T00:00:00+00:00'] * (n - n // 2),
    })
    return frame, sessions


@pytest.fixture(scope='module')
def reference():
    return load_training_reference()


@pytest.fixture
def registered(tmp_path, monkeypatch, reference):
    monkeypatch.setattr(registry, 'load_training_reference', lambda: reference)
    monkeypatch.setattr(d, 'load_training_reference', lambda: reference)
    store = tmp_path / 'data'
    frame, sessions = synthetic_source()
    meta, _ = registry.register_dataset(
        payload(frame), payload(sessions), 'synthetic_only.csv',
        'synthetic_functional_test_only', 'known_generator_labels_not_AI',
        True, True, storage=store,
    )
    return store, meta['dataset_id'], frame, sessions


def train(registered, root, **kwargs):
    return c.train_candidate(
        registered[1], feature_contract_confirmed=True,
        dataset_storage=registered[0], candidate_storage=root,
        synthetic_only=True, **kwargs,
    )


# 저장 메타데이터까지 다시 쓰는 변조도 원본 재검증으로 차단
def resign(directory, update_identity=False):
    meta = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
    for name in meta['files']:
        meta['files'][name] = c.sha256_bytes((directory / name).read_bytes())
    if update_identity:
        original = (directory / 'original.csv').read_bytes()
        sessions = (directory / 'sessions_original.csv').read_bytes()
        dataset_id, provenance = registry.identity(
            original, sessions, meta['provenance']['source'], meta['provenance']['truth_method'])
        meta.update(dataset_id=dataset_id, dataset_version=dataset_id,
                    original_sha256=c.sha256_bytes(original), provenance=provenance)
        target = directory.with_name(dataset_id)
        directory.rename(target)
        directory = target
    (directory / 'manifest.json').write_bytes(c.json_bytes(meta))
    (directory / 'manifest.sha256').write_text(
        c.sha256_bytes((directory / 'manifest.json').read_bytes()), encoding='ascii')
    return directory


def test_normal_registered_data_revalidated(registered):
    loaded = d.load_training_data(registered[1], registered[0])
    assert loaded.train_x.shape == loaded.validation_x.shape == (60, 128)
    assert set(loaded.train_y) == set(loaded.validation_y) == set(range(1, 7))
    assert loaded.reference.rows == 5933
    assert not set(loaded.assignments.query("partition=='train'").session_id) & set(
        loaded.assignments.query("partition=='validation'").session_id)


@pytest.mark.parametrize('name', ['original.csv', 'train.csv', 'validation.csv',
                                 'assignments.csv', 'sessions.csv', 'manifest.json'])
def test_file_hash_tampering_rejected(registered, name):
    path = registered[0] / 'datasets' / registered[1] / name
    path.write_bytes(path.read_bytes() + b'\ncorrupt')
    with pytest.raises((ValueError, KeyError)):
        d.load_training_data(registered[1], registered[0])


@pytest.mark.parametrize('kind', ['missing_label', 'missing_feature', 'missing_class',
                                 'cross_duplicate', 'same_session', 'old_training_duplicate',
                                 'within_train_duplicate', 'near_duplicate'])
def test_rehashed_invalid_original_still_rejected(registered, reference, kind):
    store, dataset_id, frame, sessions = registered
    frame = frame.copy()
    if kind == 'missing_label':
        frame = frame.drop(columns='gas')
    elif kind == 'missing_feature':
        frame = frame.drop(columns='f128')
    elif kind == 'missing_class':
        frame.loc[60:, 'gas'] = 1
    elif kind == 'cross_duplicate':
        frame.loc[60, FEATURES] = frame.loc[0, FEATURES]
    elif kind == 'same_session':
        sessions['session_id'] = 'only_one'
    elif kind == 'old_training_duplicate':
        frame.loc[0, FEATURES] = reference.values[0]
    elif kind in {'within_train_duplicate', 'near_duplicate'}:
        frame.loc[6, FEATURES] = frame.loc[0, FEATURES]
        if kind == 'near_duplicate':
            frame.loc[6, FEATURES] += 1e-12
    directory = store / 'datasets' / dataset_id
    (directory / 'original.csv').write_bytes(payload(frame))
    (directory / 'sessions_original.csv').write_bytes(payload(sessions))
    directory = resign(directory, update_identity=True)
    with pytest.raises(ValueError):
        d.load_training_data(directory.name, store)


@pytest.mark.parametrize('kind', ['train_values', 'validation_values', 'feature_order',
                                 'session_assignment', 'reference_record', 'unconfirmed'])
def test_saved_values_checked_even_with_valid_file_hashes(registered, kind):
    directory = registered[0] / 'datasets' / registered[1]
    if kind in {'train_values', 'validation_values', 'feature_order'}:
        name = 'validation.csv' if kind == 'validation_values' else 'train.csv'
        frame = pd.read_csv(directory / name, float_precision='round_trip')
        if kind == 'feature_order':
            frame = frame[[*reversed(FEATURES), 'gas']]
        else:
            frame.loc[0, 'f001'] += 1
        (directory / name).write_bytes(payload(frame))
    elif kind == 'session_assignment':
        frame = pd.read_csv(directory / 'assignments.csv')
        frame.loc[0, 'partition'] = 'validation'
        (directory / 'assignments.csv').write_bytes(payload(frame))
    else:
        meta = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
        if kind == 'reference_record':
            meta['reference_rows'] = 0
        else:
            meta['truth_confirmed_by_operator'] = False
        (directory / 'manifest.json').write_bytes(c.json_bytes(meta))
    resign(directory)
    with pytest.raises(ValueError):
        d.load_training_data(registered[1], registered[0])


def test_explicit_feature_contract_required(registered, tmp_path):
    with pytest.raises(ValueError, match='단위'):
        c.train_candidate(registered[1], feature_contract_confirmed=False,
                          dataset_storage=registered[0], candidate_storage=tmp_path / 'models')


def test_fit_only_train_and_reload_equivalence(registered, tmp_path, monkeypatch):
    fitted = []
    original_fit = Pipeline.fit

    def fit_spy(self, features, target, **kwargs):
        fitted.append((features.copy(), target.copy()))
        return original_fit(self, features, target, **kwargs)

    monkeypatch.setattr(Pipeline, 'fit', fit_spy)
    root = tmp_path / 'models'
    item = train(registered, root)
    assert len(fitted) == 1 and len(fitted[0][0]) == 5993
    model, meta = item['model'], item['metadata']
    values = fitted[0][0].to_numpy()
    np.testing.assert_allclose(model.named_steps['imputer'].statistics_, np.nanmedian(values, axis=0))
    np.testing.assert_allclose(model.named_steps['scaler'].mean_,
                               model.named_steps['imputer'].transform(values).mean(axis=0))
    assert model.named_steps['scaler'].n_samples_seen_ == 5993
    assert meta['base_rows'] == 5933 and meta['new_train_rows'] == 60
    assert meta['validation_rows'] == 60 and not meta['validation_fitted']
    assert not set(meta['preprocessing_audit']['new_train_row_ids']) & set(meta['preprocessing_audit']['validation_row_ids'])
    assert meta['synthetic_only'] and meta['prediction_reload_exact']
    assert not meta['review']['approval_eligible'] and not meta['review']['automatic_replacement']
    assert c.sha256_bytes(MODEL_PATH.read_bytes()) == MODEL_SHA
    assert c.sha256_bytes(DETECTOR_PATH.read_bytes()) == DETECTOR_SHA
    for label in ['official', 'candidate']:
        metrics = item['class_metrics'].query('model==@label')
        assert list(metrics.gas_id) == list(range(1, 7)) and metrics.support.sum() == 60
        assert metrics.predicted_count.sum() == 60
        assert item['confusion'].query('model==@label').n.sum() == 60
    assert item['roc_auc'].auc.notna().sum() == 12
    assert item['roc_auc'].auc.between(0, 1).all()
    before = {p.name: p.read_bytes() for p in item['directory'].iterdir()}
    fitted.clear()
    repeat = train(registered, root)
    assert repeat['reused'] and not fitted
    assert before == {p.name: p.read_bytes() for p in item['directory'].iterdir()}


def test_failed_save_removes_own_staging_and_lock(registered, tmp_path, monkeypatch):
    root = tmp_path / 'models'

    def failing_dump(model, path, **kwargs):
        path.write_bytes(b'partial_test_only')
        raise OSError('synthetic disk failure')

    monkeypatch.setattr(c.joblib, 'dump', failing_dump)
    with pytest.raises(OSError, match='disk failure'):
        train(registered, root)
    assert not list(root.glob('.staging_*'))
    assert not list(root.glob('candidate_*'))
    assert not (root / 'training.lock').exists()
    assert c.sha256_bytes(MODEL_PATH.read_bytes()) == MODEL_SHA


def test_global_lock_blocks_duplicate_execution(registered, tmp_path):
    root = tmp_path / 'models'
    root.mkdir()
    (root / 'training.lock').write_text('other_request')
    with pytest.raises(ValueError, match='잠금'):
        train(registered, root)
    assert (root / 'training.lock').read_text() == 'other_request'


@pytest.mark.parametrize('file', ['model.joblib', 'metrics.csv', 'manifest.json'])
def test_saved_candidate_tampering_rejected(registered, tmp_path, file):
    item = train(registered, tmp_path / 'models')
    path = item['directory'] / file
    path.write_bytes(path.read_bytes() + b'corrupt')
    with pytest.raises(ValueError, match='지문'):
        c.read_candidate(item['metadata']['candidate_id'], tmp_path / 'models', load_model=True)


def test_roc_insufficient_support_and_ovo_guard(registered):
    data = d.load_training_data(registered[1], registered[0])
    from src.webapp.service import load_models

    model = load_models().classifier
    result = evaluate_model(model, data.validation_x.iloc[:6], data.validation_y[:6])
    assert result[4].auc.isna().all() and result[5].empty
    model.named_steps['classifier'].decision_function_shape = 'ovo'
    result = evaluate_model(model, data.validation_x, data.validation_y)
    assert result[4].auc.isna().all() and result[5].empty


def test_missing_dataset_and_path_escape(tmp_path):
    for name in ['../outside', 'dataset_' + 'a' * 24]:
        with pytest.raises(ValueError):
            d.load_training_data(name, tmp_path)
