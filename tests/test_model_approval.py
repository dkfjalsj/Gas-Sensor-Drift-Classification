# 임시 운영 환경에서 승인·교체·복구 및 실패 후 상태 보존 검사
# 임시 합성 후보로 20-B 연계 검사이며 실제 성능 개선 검증 아님

import json

import numpy as np
import pandas as pd
import pytest

from src.common.hashing import sha256_bytes
from src.data import ROOT, FEATURES
from src.model_management import registry as r, runtime, ui
from src.retraining import datasets
from src.retraining.candidates import (
    json_bytes, train_candidate, MODEL_PATH, MODEL_SHA, DETECTOR_PATH, DETECTOR_SHA,
)
from src.webapp.data_preparation import load_training_reference
from src.webapp.service import analyze, read_upload, downloads
from tests.test_streamlit_integration import make_app
from tests.test_retraining_candidates import registered
from tests.test_retraining_candidates import synthetic_source, payload
from src.webapp.dataset_registry import register_dataset

EVIDENCE = dict(source='테스트용 생성 출처 확인 근거 기록', truth='생성 규칙 정답 확인 근거 기록',
                independence='서로 다른 합성 세션 확인 근거 기록')


@pytest.fixture(scope='module')
def reference():
    return load_training_reference()


@pytest.fixture
def manager(tmp_path, monkeypatch, reference, registered):
    candidates, data = tmp_path / 'candidates', tmp_path / 'data'
    data = registered[0]
    monkeypatch.setattr(datasets, 'load_training_reference', lambda: reference)
    item = train_candidate(registered[1], feature_contract_confirmed=True,
                           dataset_storage=data, candidate_storage=candidates, synthetic_only=True)
    manager = r.ModelRegistry(tmp_path / 'operating', candidates, data, testing=True)
    manager.test_candidate_id = item['metadata']['candidate_id']
    manager.test_dataset_id = registered[1]
    manager.initialize()
    return manager


def approve(manager, **kwargs):
    review = manager.review(manager.test_candidate_id, EVIDENCE)
    return manager.activate(manager.test_candidate_id, confirmed=True, evidence=EVIDENCE,
                            expected_version=review['active']['version_id'],
                            comparison_token=review['token'], **kwargs)


def test_initialize_is_idempotent_and_official(manager):
    before = manager.path.read_bytes()
    assert manager.initialize() == manager.read()
    assert manager.path.read_bytes() == before
    assert manager.current()['model']['kind'] == 'official'
    assert len(manager.read()['events']) == 1


def test_approve_switch_cache_rollback_and_preserve(manager):
    original = manager.current()
    frame = pd.read_csv(manager.datasets / 'datasets' / manager.test_dataset_id / 'validation.csv')
    data = read_upload(frame.to_csv(index=False).encode())
    old = analyze(data, runtime.active_bundle(manager))
    version = approve(manager, preflight=lambda v: runtime.load_bundle(v, manager))
    current = analyze(data, runtime.active_bundle(manager))
    assert current['summary']['classification_version'] == version['version_id']
    assert current['summary']['classification_sha256'] != MODEL_SHA
    assert old['summary']['classification_version'] == original['version_id']
    assert np.any(old['rows'].predicted_gas_id != current['rows'].predicted_gas_id)
    restored = manager.rollback(original['version_id'], confirmed=True,
                                expected_version=version['version_id'],
                                preflight=lambda v: runtime.load_bundle(v, manager))
    after = analyze(data, runtime.active_bundle(manager))
    np.testing.assert_array_equal(after['rows'].predicted_gas_id, old['rows'].predicted_gas_id)
    np.testing.assert_array_equal(after['windows'].score, old['windows'].score)
    assert restored['version_id'] not in [original['version_id'], version['version_id']]
    assert [e['action'] for e in manager.read()['events']] == ['initialize', 'activate', 'rollback']
    assert len(downloads(after)) == 3
    assert sha256_bytes(MODEL_PATH.read_bytes()) == MODEL_SHA
    assert sha256_bytes(DETECTOR_PATH.read_bytes()) == DETECTOR_SHA


def test_synthetic_blocked_in_non_test_environment(manager, tmp_path):
    production = r.ModelRegistry(tmp_path / 'prod', manager.candidates, manager.datasets)
    production.initialize()
    before = production.path.read_bytes()
    review = production.review(manager.test_candidate_id, EVIDENCE)
    assert not review['eligible'] and any('합성' in s for s in review['reasons'])
    with pytest.raises(ValueError, match='합성'):
        production.activate(manager.test_candidate_id, confirmed=True, evidence=EVIDENCE,
                            expected_version=review['active']['version_id'], comparison_token=review['token'])
    assert production.path.read_bytes() == before


@pytest.mark.parametrize('reason', ['confirmation', 'evidence', 'stale', 'comparison', 'cache', 'save'])
def test_failed_approval_keeps_exact_pointer(manager, monkeypatch, reason):
    review = manager.review(manager.test_candidate_id, EVIDENCE)
    before = manager.path.read_bytes()
    kwargs = dict(confirmed=True, evidence=EVIDENCE, expected_version=review['active']['version_id'],
                  comparison_token=review['token'])
    if reason == 'confirmation':
        kwargs['confirmed'] = False
    elif reason == 'evidence':
        kwargs['evidence'] = None
    elif reason == 'stale':
        kwargs['expected_version'] = 'old_version'
    elif reason == 'comparison':
        kwargs['comparison_token'] = 'stale'
    elif reason == 'cache':
        kwargs['preflight'] = lambda v: (_ for _ in ()).throw(RuntimeError('cache failure'))
    elif reason == 'save':
        monkeypatch.setattr(r.os, 'replace', lambda *args: (_ for _ in ()).throw(OSError('save failure')))
    with pytest.raises((ValueError, RuntimeError, OSError)):
        manager.activate(manager.test_candidate_id, **kwargs)
    assert manager.path.read_bytes() == before
    assert len(manager.read()['events']) == 1
    assert not list(manager.root.glob('.pending_*'))
    assert not (manager.root / 'registry.lock').exists()


def test_duplicate_approval_and_unknown_rollback_blocked(manager):
    applied = approve(manager)
    before = manager.path.read_bytes()
    with pytest.raises(ValueError, match='이미'):
        approve(manager)
    with pytest.raises(ValueError, match='이력'):
        manager.rollback('unknown', confirmed=True, expected_version=applied['version_id'])
    with pytest.raises(ValueError, match='확인'):
        manager.rollback(manager.read()['events'][0]['version']['version_id'], confirmed=False,
                         expected_version=applied['version_id'])
    assert manager.path.read_bytes() == before


@pytest.mark.parametrize('kind', ['missing_model', 'model_hash', 'metadata_hash', 'dataset', 'metrics'])
def test_corrupted_candidate_or_validation_blocks_activation(manager, kind):
    folder = manager.candidates / manager.test_candidate_id
    before = manager.path.read_bytes()
    if kind == 'missing_model':
        (folder / 'model.joblib').unlink()
    elif kind == 'model_hash':
        (folder / 'model.joblib').write_bytes(b'broken')
    elif kind == 'metadata_hash':
        (folder / 'manifest.json').write_bytes(b'{}')
    elif kind == 'dataset':
        (manager.datasets / 'datasets' / manager.test_dataset_id / 'validation.csv').write_bytes(b'broken')
    else:
        meta = json.loads((folder / 'manifest.json').read_bytes())
        meta['metrics']['candidate']['macro_f1'] = 0.5
        raw = json_bytes(meta)
        (folder / 'manifest.json').write_bytes(raw)
        (folder / 'manifest.sha256').write_text(sha256_bytes(raw))
    with pytest.raises((ValueError, OSError, KeyError)):
        manager.review(manager.test_candidate_id, EVIDENCE)
    assert manager.path.read_bytes() == before


def test_damaged_active_candidate_can_rollback_to_model_a(manager):
    old = manager.current()
    applied = approve(manager)
    (manager.candidates / manager.test_candidate_id / 'model.joblib').write_bytes(b'broken')
    with pytest.raises(ValueError):
        manager.current()
    restored = manager.rollback(old['version_id'], confirmed=True, expected_version=applied['version_id'])
    assert restored['model']['kind'] == 'official'


def test_damaged_rollback_target_keeps_pointer(manager, monkeypatch):
    first = manager.current()
    applied = approve(manager)
    before = manager.path.read_bytes()
    monkeypatch.setattr(manager, 'load_version', lambda v: (_ for _ in ()).throw(ValueError('broken target')))
    with pytest.raises(ValueError):
        manager.rollback(first['version_id'], confirmed=True, expected_version=applied['version_id'])
    assert manager.path.read_bytes() == before


def test_corrupt_ledger_no_silent_fallback(manager):
    manager.path.write_bytes(b'{}')
    with pytest.raises((KeyError, ValueError)):
        runtime.active_bundle(manager)


def test_lock_and_test_path_guards(manager):
    lock = manager.root / 'registry.lock'
    lock.write_text('other')
    with pytest.raises(ValueError, match='잠금'):
        approve(manager)
    assert lock.read_text() == 'other'
    with pytest.raises(ValueError, match='임시'):
        r.ModelRegistry(testing=True)


def test_ui_explicit_confirmation_old_analysis_unchanged_and_rollback(manager, monkeypatch):
    monkeypatch.setattr(ui, 'MANAGER_FACTORY', lambda: manager)
    original_bundle = runtime.active_bundle
    monkeypatch.setattr(runtime, 'active_bundle', lambda: original_bundle(manager))
    frame = pd.read_csv(manager.datasets / 'datasets' / manager.test_dataset_id / 'validation.csv')
    app = make_app()
    app.file_uploader(key='sensor_csv').set_value(('qa.csv', frame.to_csv(index=False).encode(), 'text/csv')).run()
    app.button(key='analyze').click().run()
    old_version = app.session_state['analysis']['summary']['classification_version']
    app.radio(key='page').set_value('모델 관리').run()
    assert not app.exception
    assert app.button(key='approval_apply').disabled
    assert any('approval_status' in table.value.columns for table in app.dataframe)
    for key in EVIDENCE:
        app.checkbox(key='approval_' + key + '_checked').check()
        app.text_input(key='approval_' + key).set_value(EVIDENCE[key])
    app.run()
    app.button(key='approval_validate').click().run()
    assert not app.exception and app.session_state['approval_review']['eligible']
    assert app.button(key='approval_apply').disabled
    app.checkbox(key='approval_confirm').check().run()
    app.button(key='approval_apply').click().run()
    assert not app.exception
    assert app.session_state['analysis']['summary']['classification_version'] == old_version
    app.radio(key='page').set_value('분석 결과').run()
    app.button(key='analyze').click().run()
    assert app.session_state['analysis']['summary']['classification_version'] != old_version
    app.radio(key='page').set_value('모델 관리').run()
    app.checkbox(key='rollback_confirm').check().run()
    app.button(key='rollback_apply').click().run()
    assert not app.exception and manager.current()['model']['kind'] == 'official'


def test_production_pointer_and_original_assets_never_changed():
    manager = r.ModelRegistry()
    assert manager.current()['model']['kind'] == 'official'
    assert len(manager.read()['events']) == 1
    assert sha256_bytes(MODEL_PATH.read_bytes()) == MODEL_SHA
    assert sha256_bytes(DETECTOR_PATH.read_bytes()) == DETECTOR_SHA


def test_lower_macro_f1_blocks_approval(manager, tmp_path):
    frame, sessions = synthetic_source(120)
    frame.loc[60:, 'gas'] = frame.loc[60:, 'gas'] % 6 + 1
    meta, _ = register_dataset(payload(frame), payload(sessions), 'synthetic_label_shift.csv',
                               'synthetic_policy_test', 'known_generator_test_labels',
                               True, True, storage=manager.datasets)
    item = train_candidate(meta['dataset_id'], feature_contract_confirmed=True,
                           dataset_storage=manager.datasets, candidate_storage=manager.candidates,
                           synthetic_only=True)
    before = manager.path.read_bytes()
    review = manager.review(item['metadata']['candidate_id'], EVIDENCE)
    assert review['candidate'][0]['macro_f1'] < review['current'][0]['macro_f1']
    assert not review['eligible']
    assert review['changes'].query('recall_delta < 0').shape[0] > 0
    with pytest.raises(ValueError, match='Macro F1'):
        manager.activate(item['metadata']['candidate_id'], confirmed=True, evidence=EVIDENCE,
                         expected_version=review['active']['version_id'], comparison_token=review['token'])
    assert manager.path.read_bytes() == before
