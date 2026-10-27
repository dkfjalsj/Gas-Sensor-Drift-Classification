# 저장 예측·분포 거리·진단 집계와 기존 산출물 보존 확인

import ast
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest
from scipy.spatial.distance import cdist
from scipy.stats import wasserstein_distance
from sklearn.metrics import confusion_matrix, f1_score, precision_recall_fscore_support
from sklearn.pipeline import Pipeline
from threadpoolctl import threadpool_limits

from src.data import ROOT, FEATURES, load_dataset, read_config
from src.temporal_expansion import sha
from src.temporal_failure_diagnostics import TRIALS, OUT


# 원본 읽기 결과를 검사 사이에서 공유
@pytest.fixture(scope='module')
def dataset():
    return load_dataset(read_config())[0]


def read_json(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))


def test_replay_without_model_fit(dataset, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('Model fit forbidden in diagnostics')
    monkeypatch.setattr(Pipeline, 'fit', forbidden)
    wide = pd.read_csv(OUT / 'row_predictions.csv')
    future = dataset[dataset.batch >= 7]
    assert len(wide) == 7977
    np.testing.assert_array_equal(wide.row_id, future.row_id)
    decision = json.loads((ROOT / 'outputs/temporal_expansion/selection_frozen.json').read_text(encoding='utf-8'))
    for name, trial in TRIALS.items():
        meta = decision['selected_models'][trial]
        assert sha(ROOT / meta['path']) == meta['sha256']
        model = joblib.load(ROOT / meta['path'])
        with threadpool_limits(limits=2):
            predicted = model.predict(future[FEATURES])
        np.testing.assert_array_equal(predicted, wide[name])


def test_batch_confusion_and_class_metrics():
    wide = pd.read_csv(OUT / 'row_predictions.csv')
    matrices = pd.read_csv(OUT / 'confusion_counts.csv')
    classes = pd.read_csv(OUT / 'class_metrics.csv')
    metrics = pd.read_csv(OUT / 'batch_metrics.csv')
    for name in TRIALS:
        for batch, group in wide.groupby('batch'):
            cm = confusion_matrix(group.gas, group[name], labels=range(1, 7))
            actual = matrices[(matrices.model == name) & (matrices.batch == batch)].pivot(
                index='actual_id', columns='predicted_id', values='count').to_numpy()
            np.testing.assert_array_equal(cm, actual)
            p, r, f, n = precision_recall_fscore_support(
                group.gas, group[name], labels=range(1, 7), zero_division=0)
            rows = classes[(classes.model == name) & (classes.batch == batch)].sort_values('gas_id')
            for column, expected in [('precision', p), ('recall', r), ('f1', f), ('support', n)]:
                np.testing.assert_allclose(rows[column], expected)
            metric = metrics[(metrics.model == name) & (metrics.batch == batch)].iloc[0]
            assert metric.macro_f1 == pytest.approx(f.mean())
            assert metric.min_class_recall == pytest.approx(r.min())


def test_specific_failures_and_disagreement():
    wide = pd.read_csv(OUT / 'row_predictions.csv')
    tol = wide[(wide.batch == 9) & (wide.gas == 6)]
    assert len(tol) == 101 and (tol.SVM == 1).all()
    assert tol.LR.value_counts().to_dict() == {2: 57, 1: 44}
    assert tol.RF.value_counts().to_dict() == {3: 83, 1: 17, 2: 1}
    acl = wide[(wide.batch == 10) & (wide.gas == 4)]
    assert len(acl) == 600
    assert int((acl.SVM == 4).sum()) == 84
    assert int((acl.RF == 4).sum()) == 51
    assert int((acl.LR == 4).sum()) == 0
    assert int(((acl.RF == 4) & (acl.SVM == 4)).sum()) == 0
    agreement = pd.read_csv(OUT / 'model_agreement.csv')
    for _, row in agreement.iterrows():
        sub = wide[wide.batch == row.batch]
        if row.gas_id:
            sub = sub[sub.gas == row.gas_id]
        correct = sub[list(TRIALS)].eq(sub.gas, axis=0)
        assert row.all_wrong == (~correct.any(axis=1)).sum()
        assert row.disagree_rate == pytest.approx((sub[list(TRIALS)].nunique(axis=1) > 1).mean())
        for name in TRIALS:
            assert row[name + '_only_correct'] == (correct[name] & (correct.sum(axis=1) == 1)).sum()


def test_feature_stats_and_wasserstein(dataset):
    summaries = pd.read_csv(OUT / 'feature_summary.csv')
    shifts = pd.read_csv(OUT / 'feature_shifts.csv')
    assert len(shifts) == 7 * 4 * 128
    train = dataset[dataset.batch <= 6]
    for gas, batch in [(6, 9), (4, 10)]:
        for feature in ['f001', 'f042', 'f128']:
            a = train[train.gas == gas][feature]
            b = dataset[(dataset.batch == batch) & (dataset.gas == gas)][feature]
            row = shifts[(shifts.gas_id == gas) & (shifts.batch == batch) &
                         (shifts.feature == feature)].iloc[0]
            assert row.wasserstein_raw == pytest.approx(wasserstein_distance(a, b))
            assert row.wasserstein_same_gas_train_sd == pytest.approx(
                wasserstein_distance(a, b) / a.std(ddof=0))
            stats = summaries[(summaries.partition == f'batch{batch}') &
                              (summaries.gas_id == gas) & (summaries.feature == feature)].iloc[0]
            assert stats['mean'] == pytest.approx(b.mean())
            assert stats['std'] == pytest.approx(b.std(ddof=0))
            assert stats.train_z_mean == pytest.approx(
                (b.mean() - train[feature].mean()) / train[feature].std(ddof=0))


def test_objective_plot_feature_selection():
    selected = pd.read_csv(OUT / 'selected_plot_features.csv')
    shifts = pd.read_csv(OUT / 'feature_shifts.csv')
    assert len(selected) == 6
    for gas, batch in [(6, 9), (4, 10)]:
        expected = shifts[(shifts.gas_id == gas) & (shifts.batch == batch)].sort_values(
            ['wasserstein_same_gas_train_sd', 'feature'], ascending=[False, True]).head(3)
        actual = selected[(selected.gas_id == gas) & (selected.batch == batch)]
        assert actual.feature.tolist() == expected.feature.tolist()


def test_proximity_and_kernel_values(dataset):
    proximity = pd.read_csv(OUT / 'sample_proximity.csv')
    decision = json.loads((ROOT / 'outputs/temporal_expansion/selection_frozen.json').read_text(encoding='utf-8'))
    model = joblib.load(ROOT / decision['selected_models']['B_SVM_balanced']['path'])
    train = dataset[dataset.batch <= 6]
    reference = model[:-1].transform(train[FEATURES])
    indexed = dataset.set_index('row_id')
    samples = pd.concat([proximity.head(2), proximity[proximity.batch == 9].head(2),
                         proximity[proximity.batch == 10].tail(2)])
    for _, row in samples.iterrows():
        transformed = model[:-1].transform(indexed.loc[[row.row_id], FEATURES])
        squared = cdist(transformed, reference, metric='sqeuclidean')[0]
        assert row.nearest_train_distance == pytest.approx(np.sqrt(squared.min()), rel=1e-8)
        assert row.nearest_own_gas_distance == pytest.approx(
            np.sqrt(squared[train.gas == row.gas_id].min()), rel=1e-8)
        support_min = squared[model.named_steps['classifier'].support_].min()
        assert row.max_rbf_similarity_to_support == pytest.approx(
            np.exp(-model.named_steps['classifier']._gamma * support_min), rel=1e-8, abs=1e-12)


def test_no_new_fit_calls_or_new_model_files():
    for name in ['temporal_failure_diagnostics.py', 'temporal_failure_report.py']:
        tree = ast.parse((ROOT / 'src' / name).read_text(encoding='utf-8'))
        assert not any(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and
                       node.func.attr in ['fit', 'fit_transform', 'partial_fit'] for node in ast.walk(tree))
    state = read_json('run_manifest.json')
    assert state['new_model_fits'] == state['preprocessing_fits'] == 0
    old_models = {name for name in state['before'] if name.endswith('.joblib')}
    actual_models = {str(p.relative_to(ROOT)) for p in (ROOT / 'models').rglob('*.joblib')}
    assert old_models == actual_models


def test_prior_files_raw_and_report_preserved():
    state = read_json('run_manifest.json')
    assert state['before'] == state['after']
    for name, expected in state['before'].items():
        assert sha(ROOT / name) == expected
    for name, expected in state['raw_hashes'].items():
        assert sha(Path(read_config()['data_dir']) / name) == expected
    for name, expected in state['code_sha256'].items():
        assert sha(ROOT / 'src' / name) == expected
    report = (ROOT / 'reports/temporal_failure_diagnostic_report.html').read_text(encoding='utf-8')
    assert report.count('<h2>') == 8
    assert report.count('data:image/png;base64,') == 5
    assert '탐색적' in report and '미확인' in report
