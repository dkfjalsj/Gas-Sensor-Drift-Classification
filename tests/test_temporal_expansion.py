# 시간순 분할·전처리·후보 선정과 저장 예측의 재현 여부 확인

import json
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import f1_score
from threadpoolctl import threadpool_limits

from src.data import ROOT, FEATURES, load_dataset, read_config
from src.temporal_expansion import prepare_split, sha, choose, rank_near

OUT = ROOT / 'outputs/temporal_expansion'


# 신규 실험 기록과 원본 자료 읽기
def read_json(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))


@pytest.fixture(scope='module')
def dataset():
    return load_dataset(read_config())[0]


def test_temporal_split_counts_and_classes(dataset):
    parts, manifest, audit = prepare_split(dataset)
    assert {k: len(v) for k, v in parts.items()} == {
        'A': 3275, 'B': 5933, 'validation': 3907, 'evaluation': 4070,
    }
    assert [r['toluene_n'] for r in audit] == [79, 546, 586, 701]
    assert [r['acetaldehyde_n'] for r in audit] == [379, 484, 777, 675]
    stored = pd.read_csv(OUT / 'split_assignments.csv')
    pd.testing.assert_frame_equal(manifest.reset_index(drop=True), stored)
    for condition in ['A', 'B']:
        assert set(parts[condition]).isdisjoint(parts['validation'])
        assert set(parts[condition]).isdisjoint(parts['evaluation'])


def test_duplicate_features_rejected(dataset):
    changed = dataset.copy()
    target = changed.index[changed.batch == 7][0]
    changed.loc[target, FEATURES] = changed.loc[0, FEATURES].to_numpy()
    with pytest.raises(ValueError, match='overlap'):
        prepare_split(changed)


def test_equal_batch_metric_and_scores():
    predictions = pd.read_csv(OUT / 'predictions.csv.gz')
    summary = pd.read_csv(OUT / 'summary_metrics.csv')
    for _, row in summary.iterrows():
        subset = predictions[(predictions.trial_id == row.trial_id) &
                             (predictions.partition == row.partition)]
        batch_scores = [f1_score(g.y_true, g.y_pred, average='macro', zero_division=0)
                        for _, g in subset.groupby('batch')]
        assert row.equal_batch_macro_f1 == pytest.approx(np.mean(batch_scores))
        assert row.batch_sd_macro_f1 == pytest.approx(np.std(batch_scores))
        assert row.pooled_macro_f1 == pytest.approx(
            f1_score(subset.y_true, subset.y_pred, average='macro', zero_division=0))
        for gas, field in [(6, 'toluene_recall'), (4, 'acetaldehyde_recall')]:
            mask = subset.y_true == gas
            assert row[field] == pytest.approx((subset.loc[mask, 'y_pred'] == gas).mean())


def test_frozen_validation_only_selection():
    validation = pd.read_csv(OUT / 'validation_metrics.csv')
    records = read_json('fit_records.json')
    decision = read_json('selection_frozen.json')
    selected = []
    for family, short in [('LogisticRegression', 'LR'), ('RandomForest', 'RF'), ('SVM_RBF', 'SVM')]:
        rows = validation[(validation.family == family) & (validation.condition == 'B')]
        selected.append(choose(rows.to_dict('records'), f'B_{short}_base'))
        initial = rows[rows.group != 'tuning']
        parent = choose(initial.to_dict('records'), f'B_{short}_base')
        assert all(r['parent'] == parent for r in records
                   if r['family'] == family and r['group'] == 'tuning')
    assert selected == decision['family_representatives']
    representatives = validation[validation.trial_id.isin(selected)]
    near = representatives[representatives.val_equal_batch_macro_f1 >=
                           representatives.val_equal_batch_macro_f1.max() - .005 - 1e-12]
    assert rank_near(near).iloc[0].trial_id == decision['priority_candidate']
    gate = read_json('evaluation_gate.json')
    assert datetime.fromisoformat(decision['frozen_at_seoul']) <= datetime.fromisoformat(
        gate['evaluation_started_at_seoul'])
    assert gate['selection_sha256'] == sha(OUT / 'selection_frozen.json')
    assert gate['selection_unchanged'] and not gate['evaluation_used_for_selection']


def test_preprocessing_fit_train_only(dataset):
    for record in read_json('fit_records.json'):
        train = dataset[dataset.batch <= (3 if record['condition'] == 'A' else 6)][FEATURES]
        model = joblib.load(ROOT / record['model_file'])
        imputer = model.named_steps['imputer']
        np.testing.assert_allclose(imputer.statistics_, train.median().to_numpy())
        assert model.n_features_in_ == 128
        if record['scaler'] == 'standard':
            scaler = model.named_steps['scaler']
            assert scaler.n_samples_seen_ == len(train)
            np.testing.assert_allclose(scaler.mean_, train.mean().to_numpy(), rtol=1e-10, atol=1e-10)
            np.testing.assert_allclose(scaler.var_, train.var(ddof=0).to_numpy(), rtol=1e-9)
        elif record['scaler'] == 'robust':
            scaler = model.named_steps['scaler']
            np.testing.assert_allclose(scaler.center_, train.median().to_numpy())
            np.testing.assert_allclose(scaler.scale_, (
                train.quantile(.75) - train.quantile(.25)).to_numpy())


def test_saved_model_predictions_reproduced(dataset):
    predictions = pd.read_csv(OUT / 'predictions.csv.gz')
    indexed = dataset.set_index('row_id')
    for record in read_json('fit_records.json'):
        path = ROOT / record['model_file']
        assert sha(path) == record['model_sha256']
        model = joblib.load(path)
        subset = predictions[predictions.trial_id == record['trial_id']]
        features = indexed.loc[subset.row_id, FEATURES]
        with threadpool_limits(limits=2):
            actual = model.predict(features)
        np.testing.assert_array_equal(actual, subset.y_pred)
    decision = read_json('selection_frozen.json')
    for record in decision['selected_models'].values():
        assert sha(ROOT / record['path']) == record['sha256']


def test_budget_and_fair_baselines():
    records = read_json('fit_records.json')
    assert len(records) == 17
    assert read_json('experiment_plan.json')['new_fits'] == 17
    for short in ['LR', 'RF', 'SVM']:
        a = next(r for r in records if r['trial_id'] == f'A_{short}_base')
        b = next(r for r in records if r['trial_id'] == f'B_{short}_base')
        assert a['params'] == b['params']
        assert a['scaler'] == b['scaler'] and a['class_weight'] == b['class_weight']
    assert all(r['condition'] == 'B' for r in records if r['group'] != 'range_baseline')


def test_preservation_and_reports():
    manifest = read_json('run_manifest.json')
    assert manifest['before'] == manifest['after']
    for name, value in manifest['before'].items():
        assert sha(ROOT / name) == value
    config = read_config()
    from pathlib import Path
    for name, value in manifest['raw_hashes'].items():
        assert sha(Path(config['data_dir']) / name) == value
    assert sha(OUT / 'experiment_plan.json') == manifest['plan_sha256']
    assert sha(ROOT / 'reports/temporal_expansion_protocol.md') == manifest['protocol_sha256']
    report = (ROOT / 'reports/temporal_expansion_report.html').read_text(encoding='utf-8')
    assert report.count('<h2>') == 10 and '탐색적' in report
    assert not manifest['independent_final_test'] and not manifest['final_model_confirmed']
