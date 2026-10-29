# 정답 데이터 품질·세션 분리·불변 저장 및 기존 추론 회귀 검증
# 합성 입력은 기능 검사 전용이며 산업 성능 검증이 아님

import ast
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import json

import numpy as np
import pandas as pd
import pytest

from src.data import ROOT, FEATURES
from src.webapp import dataset_registry as registry
from src.webapp import management_ui
from src.webapp.data_preparation import (
    TrainingReference, fingerprints, inspect_candidate, load_training_reference,
)
from src.webapp.management_ui import reset_preparation
from tests.test_streamlit_integration import synthetic, csv_bytes, make_app


@pytest.fixture
def reference():
    return TrainingReference(frozenset(), frozenset(), frozenset(), (), 0)


def sample(n=72):
    frame = synthetic(n, True)
    rows = np.arange(1, n + 1)
    sessions = pd.DataFrame({"input_row": rows, "session_id": np.where(rows <= n // 2, "early", "late"),
                             "measured_at": [(datetime(2026, 1, 1, tzinfo=timezone.utc)
                                              + timedelta(days=int(i >= n // 2), seconds=i)).isoformat()
                                             for i in range(n)]})
    return frame, sessions


def inspect(frame, sessions, reference, **kwargs):
    return inspect_candidate(csv_bytes(frame), csv_bytes(sessions) if sessions is not None else None,
                             kwargs.get("source", "synthetic_test"), kwargs.get("method", "synthetic_fixture_only"),
                             kwargs.get("confirmed", True), reference)


@pytest.mark.parametrize('kind', ['no_gas', 'bad_gas', 'fraction_gas', 'missing_feature',
                                 'duplicate_feature', 'nonnumeric', 'infinity', 'all_missing_row',
                                 'missing_source', 'unconfirmed_truth'])
def test_invalid_candidates_block_preparation(reference, kind):
    frame, sessions = sample()
    options = {}
    if kind == 'no_gas':
        frame = frame.drop(columns='gas')
    elif kind == 'bad_gas':
        frame.loc[0, 'gas'] = 7
    elif kind == 'fraction_gas':
        frame = frame.astype({'gas': float})
        frame.loc[0, 'gas'] = 1.5
    elif kind == 'missing_feature':
        frame = frame.drop(columns='f001')
    elif kind == 'duplicate_feature':
        frame.columns = ['f002', *frame.columns[1:]]
    elif kind == 'nonnumeric':
        frame = frame.astype(object)
        frame.loc[0, 'f001'] = 'invalid'
    elif kind == 'infinity':
        frame.loc[0, 'f001'] = np.inf
    elif kind == 'all_missing_row':
        frame.loc[0, FEATURES] = np.nan
    elif kind == 'missing_source':
        options['source'] = ''
    else:
        options['confirmed'] = False
    result = inspect(frame, sessions, reference, **options)
    assert result.errors and not result.ready


def test_partial_missing_records_warning_without_imputation(reference):
    frame, sessions = sample()
    frame.loc[0, 'f001'] = np.nan
    result = inspect(frame, sessions, reference)
    assert result.ready and result.warnings
    assert result.summary['missing_cells'] == 1
    assert pd.isna(result.data.features.loc[0, 'f001'])


def test_duplicate_conflicts_and_cross_session_groups(reference):
    frame, sessions = sample()
    frame.loc[6, FEATURES] = frame.loc[0, FEATURES]
    result = inspect(frame, sessions, reference)
    assert result.ready and result.summary['duplicate_extra'] == 1 and result.warnings
    frame.loc[6, 'gas'] = 2
    assert inspect(frame, sessions, reference).errors
    frame.loc[6, 'gas'] = 1
    frame.loc[36, FEATURES] = frame.loc[0, FEATURES]
    assert not inspect(frame, sessions, reference).ready


def test_imbalance_and_small_support_warning(reference):
    frame, sessions = sample(240)
    frame['gas'] = 1
    for start in [0, 120]:
        frame.loc[start:start + 5, 'gas'] = np.arange(1, 7)
    result = inspect(frame, sessions, reference)
    assert result.ready and result.summary['class_imbalance_ratio'] > 10
    assert len(result.warnings) >= 3


@pytest.mark.parametrize('kind', ['missing', 'one_session', 'overlap', 'no_timezone',
                                 'row_duplicate', 'missing_class', 'train_empty_feature'])
def test_incomplete_temporal_conditions_hold(reference, kind):
    frame, sessions = sample()
    if kind == 'missing':
        sessions = None
    elif kind == 'one_session':
        sessions['session_id'] = 'only_session'
    elif kind == 'overlap':
        sessions.loc[0, 'measured_at'] = sessions.loc[71, 'measured_at']
    elif kind == 'no_timezone':
        sessions.loc[0, 'measured_at'] = '2026-01-01T09:00:00'
    elif kind == 'row_duplicate':
        sessions.loc[0, 'input_row'] = 2
    elif kind == 'missing_class':
        frame.loc[36:, 'gas'] = 1
    else:
        frame.loc[:35, 'f001'] = np.nan
    result = inspect(frame, sessions, reference)
    assert not result.ready and result.holds


def test_deterministic_sessions_rows_and_feature_order(reference):
    frame, sessions = sample()
    a = inspect(frame, sessions, reference)
    b = inspect(frame[[*FEATURES[::-1], 'gas']], sessions.sample(frac=1, random_state=42), reference)
    assert a.ready and b.ready
    assert list(b.data.features) == FEATURES
    for result in [a, b]:
        train = result.assignments.query("partition == 'train'")
        valid = result.assignments.query("partition == 'validation'")
        assert set(train.input_row).isdisjoint(valid.input_row)
        assert set(train.session_id).isdisjoint(valid.session_id)
        assert set(train.feature_sha256).isdisjoint(valid.feature_sha256)
        assert train.measured_at.max() < valid.measured_at.min()
        assert train.input_row.tolist() == list(range(1, 37))
        assert valid.input_row.tolist() == list(range(37, 73))
    pd.testing.assert_series_equal(a.assignments.partition, b.assignments.partition)


def test_known_old_training_matches_and_unknown_reference(reference):
    frame, sessions = sample()
    exact, near = fingerprints(frame), fingerprints(frame, near=True)
    ref = replace(reference, exact=frozenset([exact[0]]), near=frozenset([near[0]]),
                  labeled=frozenset([(exact[0], 1)]), rows=1, values=frame.loc[[0], FEATURES].to_numpy())
    result = inspect(frame, sessions, ref)
    assert not result.ready and result.summary['old_near_matches'] == 1
    frame.loc[0, 'f001'] = np.nan
    result = inspect(frame, sessions, ref)
    assert not result.ready and result.summary['old_partial_possible_matches'] == 1
    assert not inspect(frame, sessions, None).ready


def test_actual_reference_only_uses_official_train():
    reference = load_training_reference()
    assert reference.rows == 5933
    assert [name for name, _ in reference.files] == [f'batch{i}.dat' for i in range(1, 7)]
    assert reference.values.shape == (5933, 128)
    assert not reference.values.flags.writeable


def test_actual_reference_detects_original_sample():
    reference = load_training_reference()
    frame, sessions = sample()
    frame.loc[0, FEATURES] = reference.values[0]
    result = inspect(frame, sessions, reference)
    assert not result.ready and result.errors


def test_immutable_registration_and_manifest_roundtrip(reference, monkeypatch, tmp_path):
    monkeypatch.setattr(registry, 'load_training_reference', lambda: reference)
    frame, sessions = sample()
    args = (csv_bytes(frame), csv_bytes(sessions), r'C:\private\input.csv',
            'synthetic_test', 'synthetic_fixture_only', True, True)
    receipt, created = registry.register_dataset(*args, storage=tmp_path)
    directory = tmp_path / 'datasets' / receipt['dataset_id']
    assert created and receipt['original_filename'] == 'input.csv'
    assert (directory / 'original.csv').read_bytes() == args[0]
    assert receipt['partition_rows'] == {'train': 36, 'validation': 36}
    assert not receipt['preprocessing_fitted'] and receipt['new_model_fits'] == 0
    train, valid = pd.read_csv(directory / 'train.csv'), pd.read_csv(directory / 'validation.csv')
    assert list(train) == [*FEATURES, 'gas']
    pd.testing.assert_frame_equal(train, frame.iloc[:36].reset_index(drop=True))
    pd.testing.assert_frame_equal(valid, frame.iloc[36:].reset_index(drop=True))
    before = {p.name: p.read_bytes() for p in directory.iterdir()}
    again, created = registry.register_dataset(*args, storage=tmp_path)
    assert not created and again == receipt
    assert before == {p.name: p.read_bytes() for p in directory.iterdir()}
    (directory / 'train.csv').write_bytes(b'tampered')
    with pytest.raises(ValueError):
        registry.register_dataset(*args, storage=tmp_path)


def test_registration_warnings_errors_and_lock_block(reference, monkeypatch, tmp_path):
    monkeypatch.setattr(registry, 'load_training_reference', lambda: reference)
    frame, sessions = sample()
    frame.loc[0, 'f001'] = np.nan
    args = (csv_bytes(frame), csv_bytes(sessions), 'input.csv', 'synthetic_test', 'synthetic_fixture_only', True)
    with pytest.raises(ValueError, match='경고'):
        registry.register_dataset(*args, False, storage=tmp_path)
    assert not (tmp_path / 'datasets').exists()
    (tmp_path / 'registration.lock').write_text('test_only')
    with pytest.raises(ValueError, match='잠금'):
        registry.register_dataset(*args, True, storage=tmp_path)


def test_prior_validation_cannot_become_new_train(reference, monkeypatch, tmp_path):
    monkeypatch.setattr(registry, 'load_training_reference', lambda: reference)
    frame, sessions = sample()
    registry.register_dataset(csv_bytes(frame), csv_bytes(sessions), 'a.csv',
                              'synthetic_test', 'synthetic_fixture_only', True, True, storage=tmp_path)
    future = synthetic(36, True) + 100
    future['gas'] = np.arange(36) % 6 + 1
    next_frame = pd.concat([frame.iloc[36:], future], ignore_index=True)
    _, next_sessions = sample()
    next_sessions.loc[:35, 'session_id'] = 'late'
    next_sessions.loc[36:, 'session_id'] = 'later'
    with pytest.raises(ValueError, match='검증'):
        registry.register_dataset(csv_bytes(next_frame), csv_bytes(next_sessions), 'b.csv',
                                  'synthetic_test', 'synthetic_fixture_only', True, True, storage=tmp_path)


def test_upload_change_resets_only_management_state():
    state = {'analysis': object(), 'preparation_token': 'old', 'preparation_check': object(),
             'preparation_receipt': object(), 'preparation_accepted': True}
    assert reset_preparation(state, 'new')
    assert 'analysis' in state
    assert 'preparation_check' not in state and 'preparation_receipt' not in state
    assert 'preparation_accepted' not in state
    assert not reset_preparation(state, 'new')


def test_management_ui_workflow_and_reset(reference, monkeypatch, tmp_path):
    monkeypatch.setattr(management_ui, 'load_training_reference', lambda: reference)
    monkeypatch.setattr(registry, 'load_training_reference', lambda: reference)
    monkeypatch.setattr(management_ui, 'LOCAL_ROOT', tmp_path)
    frame, sessions = sample()
    app = make_app()
    app.radio(key='page').set_value('모델 관리').run()
    app.file_uploader(key='preparation_csv').set_value(('candidate.csv', csv_bytes(frame), 'text/csv')).run()
    app.file_uploader(key='preparation_sessions').set_value(('sessions.csv', csv_bytes(sessions), 'text/csv')).run()
    app.text_input(key='preparation_source').set_value('synthetic_test').run()
    app.text_input(key='preparation_truth').set_value('synthetic_fixture_only').run()
    app.checkbox(key='preparation_confirmed').check().run()
    app.button(key='preparation_inspect').click().run()
    assert not app.exception and app.session_state['preparation_check'].ready
    app.button(key='preparation_save').click().run()
    assert not app.exception and 'preparation_receipt' in app.session_state
    assert len(list((tmp_path / 'datasets').glob('dataset_*'))) == 1
    app.file_uploader(key='preparation_csv').clear().run()
    assert 'preparation_check' not in app.session_state
    assert 'preparation_receipt' not in app.session_state
    assert not app.exception


def test_no_fit_calls_and_git_exclusion_and_preservation():
    for name in ['data_preparation.py', 'dataset_registry.py', 'management_ui.py']:
        tree = ast.parse((ROOT / 'src/webapp' / name).read_text(encoding='utf-8'))
        assert not [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr in {'fit', 'fit_transform', 'partial_fit', 'predict', 'predict_proba'}]
    assert 'data/' in (ROOT / '.gitignore').read_text().splitlines()
    assert management_ui.LOCAL_ROOT == ROOT / 'data/retraining'


def test_numeric_validation_session_reserved_with_new_rows(reference, monkeypatch, tmp_path):
    monkeypatch.setattr(registry, 'load_training_reference', lambda: reference)
    frame, sessions = sample()
    sessions.loc[36:, 'session_id'] = '001'
    registry.register_dataset(csv_bytes(frame), csv_bytes(sessions), 'a.csv',
                              'synthetic_test', 'synthetic_fixture_only', True, True, storage=tmp_path)
    next_frame = frame.copy()
    next_frame[FEATURES] += 100
    sessions.loc[:35, 'session_id'] = '001'
    sessions.loc[36:, 'session_id'] = 'later'
    with pytest.raises(ValueError, match='검증 세션'):
        registry.register_dataset(csv_bytes(next_frame), csv_bytes(sessions), 'b.csv',
                                  'synthetic_test', 'synthetic_fixture_only', True, True, storage=tmp_path)


def test_manifest_edit_is_detected(reference, monkeypatch, tmp_path):
    monkeypatch.setattr(registry, 'load_training_reference', lambda: reference)
    frame, sessions = sample()
    manifest, _ = registry.register_dataset(csv_bytes(frame), csv_bytes(sessions), 'a.csv',
                                           'synthetic_test', 'synthetic_fixture_only', True, True, storage=tmp_path)
    directory = tmp_path / 'datasets' / manifest['dataset_id']
    edited = dict(manifest, independent_final_test=True)
    (directory / 'manifest.json').write_text(json.dumps(edited), encoding='utf-8')
    with pytest.raises(ValueError, match='메타데이터 지문'):
        registry.read_manifest(directory)


def test_management_ui_missing_session_cannot_save(reference, monkeypatch):
    monkeypatch.setattr(management_ui, 'load_training_reference', lambda: reference)
    frame, _ = sample()
    app = make_app()
    app.radio(key='page').set_value('모델 관리').run()
    app.file_uploader(key='preparation_csv').set_value(('candidate.csv', csv_bytes(frame), 'text/csv')).run()
    app.text_input(key='preparation_source').set_value('synthetic_test').run()
    app.text_input(key='preparation_truth').set_value('synthetic_fixture_only').run()
    app.checkbox(key='preparation_confirmed').check().run()
    app.button(key='preparation_inspect').click().run()
    assert not app.exception
    assert not app.session_state['preparation_check'].ready
    assert app.button(key='preparation_save').disabled
    assert 'preparation_receipt' not in app.session_state
