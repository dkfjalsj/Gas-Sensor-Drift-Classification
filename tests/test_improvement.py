# 개선 실험의 과거 Test 제외와 전처리·선정·저장 재현 검증
# 새 모델을 학습하지 않고 이미 저장한 결과만 대조

import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import precision_recall_fscore_support, accuracy_score

from src.data import ROOT, FEATURES, read_config, load_dataset
from src.improve_models import OUT, MODELS, choose_family, strict_split, FAMILIES, ABBR


@pytest.fixture(scope='module')
def inputs():
    frame, _ = load_dataset(read_config())
    old = pd.read_csv(ROOT / 'outputs/model_comparison/split_assignments.csv')
    parts, manifest = strict_split(frame, old)
    return frame, old, parts, manifest


# 과거 Test 합집합과 새 Train·Validation의 완전 분리 확인
def test_historical_test_exclusion_and_class_coverage(inputs):
    frame, old, parts, manifest = inputs
    excluded = set(old.loc[old.partition == 'test', 'row_id'])
    assert len(excluded) == 12518
    for part in ['train', 'validation']:
        subset = frame.iloc[parts[part]]
        assert not set(subset.row_id) & excluded
        assert set(subset.gas) == {1, 2, 3, 4, 5, 6}
    assert [len(parts[p]) for p in ['train', 'validation', 'test']] == [370, 1022, 12221]
    assert [(frame.iloc[parts[p]].gas == 6).sum() for p in ['train', 'validation', 'test']] == [59, 4, 1754]
    pd.testing.assert_frame_equal(pd.read_csv(OUT / 'split_assignments.csv'), manifest)
    assert manifest.partition.eq('excluded_historical_test').sum() == 297


# 새 분할 사이의 동일 특징 중복 차단 확인
def test_duplicate_guard(inputs):
    frame, old, parts, _ = inputs
    modified = frame.copy()
    modified.loc[parts['validation'][0], FEATURES] = modified.loc[parts['train'][0], FEATURES].to_numpy()
    with pytest.raises(ValueError, match='overlap'):
        strict_split(modified, old)


# 저장 모델의 전처리 통계가 Train 370개와 같은지 확인
def test_train_only_transformer_statistics(inputs):
    frame, _, parts, _ = inputs
    train = frame.iloc[parts['train']][FEATURES]
    records = json.loads((OUT / 'fit_records.json').read_text(encoding='utf-8'))
    assert len(records) == 14
    for record in records:
        pipeline = joblib.load(ROOT / record['model_file'])
        assert list(pipeline.feature_names_in_) == FEATURES
        assert np.allclose(pipeline.named_steps['imputer'].statistics_, train.median())
        assert record['train_n'] == len(train) == 370
        if record['scaler'] == 'standard':
            scaler = pipeline.named_steps['scaler']
            assert scaler.n_samples_seen_ == 370
            assert np.allclose(scaler.mean_, train.mean())
            assert np.allclose(scaler.var_, train.var(ddof=0))
        elif record['scaler'] == 'robust':
            scaler = pipeline.named_steps['scaler']
            expected = (train.quantile(.75) - train.quantile(.25)).to_numpy()
            expected[expected == 0] = 1
            assert np.allclose(scaler.center_, train.median())
            assert np.allclose(scaler.scale_, expected)
        else:
            assert 'scaler' not in pipeline.named_steps


# 압축 저장 모델의 전체 예측 재현 확인
def test_saved_models_replay_all_predictions(inputs):
    frame, _, _, _ = inputs
    lookup = frame.set_index('row_id')
    predictions = pd.read_csv(OUT / 'predictions.csv.gz')
    records = json.loads((OUT / 'fit_records.json').read_text(encoding='utf-8'))
    for record in records:
        path = ROOT / record['model_file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record['model_sha256']
        pipeline = joblib.load(path)
        selected = predictions[predictions.trial_id == record['trial_id']]
        actual = pipeline.predict(lookup.loc[selected.row_id, FEATURES])
        assert np.array_equal(actual, selected.y_pred)
    assert len(list(MODELS.glob('*.joblib'))) == 14
    assert len(list((ROOT / 'models').glob('*.joblib'))) == 9


# 후보 선정과 후속 탐색 부모가 Validation에서만 재현되는지 확인
def test_validation_decision_and_tuning_parent():
    validation = pd.read_csv(OUT / 'validation_metrics.csv')
    decision_path = OUT / 'validation_decisions.json'
    decision = json.loads(decision_path.read_text(encoding='utf-8'))
    records = json.loads((OUT / 'fit_records.json').read_text(encoding='utf-8'))
    expected = [choose_family(validation[validation.family == family].to_dict('records'),
                              f'{ABBR[family]}_base') for family in FAMILIES]
    assert decision['joint_candidates'] == expected
    for family in FAMILIES:
        initial = validation[(validation.family == family) & (validation.group != 'E_tuning')]
        parent = choose_family(initial.to_dict('records'), f'{ABBR[family]}_base')
        assert all(r['parent'] == parent for r in records
                   if r['family'] == family and r['group'] == 'E_tuning')
    gate = json.loads((OUT / 'evaluation_gate.json').read_text(encoding='utf-8'))
    assert gate['decision_sha256'] == hashlib.sha256(decision_path.read_bytes()).hexdigest()
    assert gate['selection_frozen_before_test'] and gate['selection_unchanged']
    assert not gate['test_used_for_selection'] and not decision['final_confirmed']


# 실제 예측에서 성능과 클래스별 지표 재계산
def test_metrics_computed_from_predictions():
    predictions = pd.read_csv(OUT / 'predictions.csv.gz')
    metrics = pd.read_csv(OUT / 'metrics.csv')
    for row in metrics.itertuples(index=False):
        subset = predictions[(predictions.trial_id == row.trial_id) & (predictions.partition == row.partition)]
        if row.scope == 'batch':
            subset = subset[subset.batch == row.batch]
        elif row.scope == 'common_6_10':
            subset = subset[subset.batch.isin([6, 7, 8, 9, 10])]
        p, r, f, n = precision_recall_fscore_support(
            subset.y_true, subset.y_pred, labels=[1, 2, 3, 4, 5, 6], zero_division=0)
        assert row.n == len(subset)
        assert row.accuracy == pytest.approx(accuracy_score(subset.y_true, subset.y_pred))
        assert row.macro_f1 == pytest.approx(f[n > 0].mean())
        assert row.weighted_f1 == pytest.approx(np.average(f, weights=n))
        assert row.toluene_support == n[5]
        if n[5]:
            assert row.toluene_recall == pytest.approx(r[5])
            assert row.toluene_f1 == pytest.approx(f[5])
        else:
            assert pd.isna(row.toluene_recall) and pd.isna(row.toluene_f1)


# 과거 파일·원본·사전 계획의 해시 보존 확인
def test_preservation_and_frozen_plan():
    state = json.loads((OUT / 'run_manifest.json').read_text(encoding='utf-8'))
    assert state['before'] == state['after'] and state['existing_files_unchanged']
    for name, expected in state['before'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected
    for name, expected in state['raw_hashes'].items():
        assert hashlib.sha256((Path(read_config()['data_dir']) / name).read_bytes()).hexdigest() == expected
    assert state['plan_sha256'] == hashlib.sha256((OUT / 'experiment_plan.json').read_bytes()).hexdigest()
    baseline = pd.read_csv(OUT / 'baseline_reproduction.csv')
    assert len(baseline) == 6 and baseline.exact_replay.all() and baseline.existing_metrics_match.all()


# 필수 보고서와 모든 실험 조건 생성 확인
def test_reports_and_budget():
    plan = json.loads((OUT / 'experiment_plan.json').read_text(encoding='utf-8'))
    records = json.loads((OUT / 'fit_records.json').read_text(encoding='utf-8'))
    assert len(records) == plan['max_new_fits'] == 14
    assert len([r for r in records if r['group'] == 'E_tuning']) == 6
    doc = (ROOT / 'reports/model_improvement_report.html').read_text(encoding='utf-8')
    assert doc.count('<section>') == 10
    assert '<meta charset="UTF-8">' in doc and '탐색적' in doc
    assert (ROOT / 'reports/model_selection_rationale.md').is_file()
