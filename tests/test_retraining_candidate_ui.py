# 후보 관리자 흐름과 독립적인 기존 자료 보존 검사

import json

import numpy as np
import pandas as pd
import pytest

from src.retraining import candidates as c, datasets as d
from src.retraining import ui
from src.retraining.preservation import verify
from src.webapp import dataset_registry as registry
from tests.test_retraining_candidates import payload, synthetic_source, reference, registered
from tests.test_streamlit_integration import make_app


@pytest.mark.skipif(
    not (ui.DATA_STORAGE.parent.parent / 'outputs/retraining_candidates/preservation_before.json').exists(),
    reason='로컬 보존 기록 필요; 합성 산출물과 보존 기록은 Git 제외',
)
def test_prior_research_and_20a_extension_preserved():
    result = verify()
    assert result['all_preserved'], result
    assert result['models'] == 325 and result['management_extension_only']


def test_candidate_state_change_does_not_clear_analysis():
    state = dict(analysis=object(), candidate_selection_token='old',
                 candidate_receipt='old', candidate_check='old', candidate_contract=True)
    assert ui.reset_candidate_state(state, 'new')
    assert 'analysis' in state and 'candidate_check' not in state
    assert 'candidate_receipt' not in state and 'candidate_contract' not in state


def test_management_no_dataset_disables_training(monkeypatch, tmp_path):
    monkeypatch.setattr(ui, 'DATA_STORAGE', tmp_path / 'data')
    monkeypatch.setattr(ui, 'CANDIDATE_STORAGE', tmp_path / 'models')
    app = make_app()
    app.radio(key='page').set_value('모델 관리').run()
    assert not app.exception and app.button(key='candidate_train').disabled
    assert not (tmp_path / 'models').exists()


def test_ui_trains_compares_and_keeps_official(registered, monkeypatch, tmp_path):
    monkeypatch.setattr(ui, 'DATA_STORAGE', registered[0])
    monkeypatch.setattr(ui, 'CANDIDATE_STORAGE', tmp_path / 'models')
    original_train = c.train_candidate

    def qa_train(*args, **kwargs):
        return original_train(*args, **kwargs, synthetic_only=True)

    monkeypatch.setattr(ui, 'train_candidate', qa_train)
    app = make_app()
    app.radio(key='page').set_value('모델 관리').run()
    assert not app.exception and app.button(key='candidate_train').disabled
    app.button(key='candidate_validate').click().run()
    assert not app.exception and app.session_state['candidate_check']
    assert app.button(key='candidate_train').disabled
    app.checkbox(key='candidate_contract').check().run()
    assert not app.button(key='candidate_train').disabled
    app.button(key='candidate_train').click().run()
    assert not app.exception and app.session_state['candidate_receipt']
    assert len(list((tmp_path / 'models').glob('candidate_*'))) == 1
    assert any('후보 Macro F1' in item.label for item in app.metric)
    assert any('합성' in item.value for item in app.warning)
    assert any('자동 승인' in item.value for item in app.info)
    assert len(app.get('download_button')) >= 1
    assert not app.session_state['candidate_busy']
    frame, sessions = synthetic_source(120, shift=1000)
    meta, _ = registry.register_dataset(payload(frame), payload(sessions), 'second.csv',
                                        'synthetic_functional_test_only', 'known_generator_labels_not_AI',
                                        True, True, storage=registered[0])
    app.button(key='candidate_refresh').click().run()
    app.selectbox(key='candidate_dataset').set_value(meta['dataset_id']).run()
    assert not app.exception
    assert app.button(key='candidate_train').disabled
    assert 'candidate_receipt' not in app.session_state


def test_prior_validation_reservation_rechecked(registered, reference):
    store, first_id, first_frame, _ = registered
    frame, sessions = synthetic_source(120, shift=1000)
    meta, _ = registry.register_dataset(payload(frame), payload(sessions), 'second.csv',
                                        'synthetic_functional_test_only', 'known_generator_labels_not_AI',
                                        True, True, storage=store)
    directory = store / 'datasets' / meta['dataset_id']
    frame.loc[:59, :] = first_frame.iloc[60:].to_numpy()
    (directory / 'original.csv').write_bytes(payload(frame))
    from tests.test_retraining_candidates import resign

    directory = resign(directory, update_identity=True)
    with pytest.raises(ValueError, match='검증'):
        d.load_training_data(directory.name, store)


def test_validation_extreme_values_never_used_for_scaler(registered, reference, tmp_path):
    frame, sessions = synthetic_source(120, shift=500)
    frame.loc[60:, 'f001'] = np.arange(60) + 1e12
    meta, _ = registry.register_dataset(payload(frame), payload(sessions), 'extreme_val.csv',
                                        'synthetic_extreme_validation_only', 'known_generator_labels_not_AI',
                                        True, True, storage=registered[0])
    result = c.train_candidate(meta['dataset_id'], feature_contract_confirmed=True,
                               dataset_storage=registered[0], candidate_storage=tmp_path / 'model',
                               synthetic_only=True)
    assert result['model'].named_steps['scaler'].mean_[0] < 1e9
    assert result['metadata']['fitted_rows'] == 5993


def test_small_support_is_insufficient_and_roc_skipped(registered, tmp_path):
    frame, sessions = synthetic_source(48, shift=1000)
    meta, _ = registry.register_dataset(payload(frame), payload(sessions), 'small.csv',
                                        'synthetic_small_support_only', 'known_generator_labels_not_AI',
                                        True, True, storage=registered[0])
    result = c.train_candidate(meta['dataset_id'], feature_contract_confirmed=True,
                               dataset_storage=registered[0], candidate_storage=tmp_path / 'model',
                               synthetic_only=True)
    assert result['class_metrics'].support.eq(4).all()
    assert result['roc_auc'].auc.isna().all() and result['roc_points'].empty
    assert any('5개 미만' in reason for reason in result['metadata']['review']['assessment_reasons'])
    assert not result['metadata']['review']['approval_eligible']


def test_invalid_metadata_disables_ui_instead_of_crashing(registered, monkeypatch, tmp_path):
    from src.common.hashing import sha256_bytes

    directory = registered[0] / 'datasets' / registered[1]
    manifest = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
    manifest.pop('provenance')
    raw = c.json_bytes(manifest)
    (directory / 'manifest.json').write_bytes(raw)
    (directory / 'manifest.sha256').write_text(sha256_bytes(raw), encoding='utf-8')
    monkeypatch.setattr(ui, 'DATA_STORAGE', registered[0])
    monkeypatch.setattr(ui, 'CANDIDATE_STORAGE', tmp_path / 'models')
    app = make_app()
    app.radio(key='page').set_value('모델 관리').run()
    assert not app.exception and app.error
    assert app.button(key='candidate_train').disabled
