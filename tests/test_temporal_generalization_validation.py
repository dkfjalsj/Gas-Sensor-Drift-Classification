# 고정 예측·조건부 구간·한글 그래프와 이전 자료 보존 검증

import ast
import json
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest
from scipy.stats import binomtest
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support, accuracy_score
from threadpoolctl import threadpool_limits

from src.data import ROOT, FEATURES, load_dataset, read_config
from src.temporal_expansion import sha
from src.temporal_generalization_validation import OUT, bootstrap_uncertainty


def read_json(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))


@pytest.fixture(scope='module')
def dataset():
    return load_dataset(read_config())[0]


@pytest.fixture(scope='module')
def predictions():
    return pd.read_csv(OUT / 'predictions_comparison.csv')


def test_independence_inventory_and_exposure():
    config = read_json('experiment_config.json')
    assert config['confirmed_independent_rows'] == 0
    assert not config['independent_final_performance_measured']
    inventory = pd.read_csv(OUT / 'data_inventory.csv')
    assert not inventory.confirmed_independent.any()
    assert (inventory.role == 'known_original_batch').sum() == 10
    exposure = pd.read_csv(OUT / 'historical_row_exposure.csv')
    assert len(exposure) == 13910 and exposure.row_id.nunique() == 13910
    assert exposure.stage1_eda_observed.all()
    assert not exposure.confirmed_new_independent.any()
    assert set(exposure.stage2_A_random) == {'train', 'validation', 'test'}


def test_fixed_models_and_train_only_preprocessing(dataset, predictions):
    config = read_json('experiment_config.json')
    future = dataset[dataset.batch >= 8]
    assert len(future) == len(predictions) == 4364
    for name, end in [('A', 6), ('B', 7)]:
        meta = config['models'][name]
        path = ROOT / meta['path']
        assert sha(path) == meta['sha256']
        model = joblib.load(path)
        train = dataset[dataset.batch <= end]
        assert len(train) == (5933 if name == 'A' else 9546)
        assert model.named_steps['scaler'].n_samples_seen_ == len(train)
        np.testing.assert_allclose(model.named_steps['scaler'].mean_, train[FEATURES].mean(), atol=1e-10)
        np.testing.assert_allclose(model.named_steps['scaler'].var_, train[FEATURES].var(ddof=0), rtol=1e-9)
        assert list(model.feature_names_in_) == FEATURES
        assert model.named_steps['classifier'].C == 1
        assert model.named_steps['classifier'].gamma == 'scale'
        assert model.named_steps['classifier'].class_weight == 'balanced'
        with threadpool_limits(limits=2):
            actual = model.predict(future[FEATURES])
        np.testing.assert_array_equal(actual, predictions['pred_' + name])
        assert set(train.row_id).isdisjoint(future.row_id)
    assert config['models']['A']['official_main_candidate']
    assert not config['models']['B']['official_main_candidate']


def test_metrics_and_confusion_counts(predictions):
    metrics = pd.read_csv(OUT / 'evaluation_metrics.csv', dtype={'scope': str})
    classes = pd.read_csv(OUT / 'class_metrics.csv', dtype={'scope': str})
    matrices = pd.read_csv(OUT / 'confusion_matrices.csv', dtype={'scope': str})
    for _, row in metrics.iterrows():
        sub = predictions[predictions.batch >= 9] if row.scope == 'pooled_9_10' else predictions[predictions.batch == int(row.scope)]
        predicted = sub['pred_' + row.model]
        p, r, f, n = precision_recall_fscore_support(sub.gas, predicted, labels=range(1, 7), zero_division=0)
        assert row.accuracy == pytest.approx(accuracy_score(sub.gas, predicted))
        assert row.macro_precision == pytest.approx(p.mean())
        assert row.macro_recall == pytest.approx(r.mean())
        assert row.macro_f1 == pytest.approx(f.mean())
        assert row.weighted_f1 == pytest.approx(np.average(f, weights=n))
        per_class = classes[(classes.model == row.model) & (classes.scope == row.scope)].sort_values('gas_id')
        for column, expected in [('precision', p), ('recall', r), ('f1', f), ('support', n)]:
            np.testing.assert_allclose(per_class[column], expected)
        actual_cm = matrices[(matrices.model == row.model) & (matrices.scope == row.scope)].pivot(
            index='actual_id', columns='predicted_id', values='count').to_numpy()
        np.testing.assert_array_equal(actual_cm, confusion_matrix(sub.gas, predicted, labels=range(1, 7)))


def test_historical_predictions_and_metrics_exact():
    replay = pd.read_csv(OUT / 'historical_prediction_replay.csv')
    assert replay.predictions_exact.all() and replay.labels_exact.all() and replay.model_hashes_match.all()
    assert set(replay.source.str.replace('\\', '/', regex=False).str.split('/').str[1]) >= {
        'model_comparison', 'model_diagnostics', 'toluene_analysis', 'model_improvement',
        'temporal_expansion', 'temporal_failure_diagnostics', 'temporal_robustness', 'temporal_weighting'}
    metrics = pd.read_csv(OUT / 'historical_metric_replay.csv')
    assert metrics.match.all() and metrics.scalars_checked.min() > 0
    assert metrics.max_absolute_error.max() <= 1e-12


def test_paired_changes_and_focus_failure(predictions):
    pairs = pd.read_csv(OUT / 'paired_correctness.csv')
    for _, row in pairs.iterrows():
        sub = predictions[predictions.batch == row.batch]
        if row.gas_id:
            sub = sub[sub.gas == row.gas_id]
        a, b = sub.pred_A == sub.gas, sub.pred_B == sub.gas
        assert row.n == len(sub)
        assert row.A_only_correct == (a & ~b).sum()
        assert row.B_only_correct == (b & ~a).sum()
        assert row.both_wrong == (~a & ~b).sum()
    target = predictions[(predictions.batch == 9) & (predictions.gas == 6)]
    assert len(target) == 101 and (target.pred_A == 6).sum() == 0 and (target.pred_B == 6).sum() == 1


def test_conditional_bootstrap_reproducible(predictions):
    intervals, class_intervals, draws = bootstrap_uncertainty(predictions, repeats=2000, seed=42)
    saved = pd.read_csv(OUT / 'conditional_bootstrap_intervals.csv', dtype={'scope': str})
    pd.testing.assert_frame_equal(intervals, saved, check_exact=False, rtol=1e-12, atol=1e-12)
    saved_draws = pd.read_csv(OUT / 'bootstrap_replicates.csv.gz', dtype={'scope': str})
    pd.testing.assert_frame_equal(draws, saved_draws, check_exact=False, rtol=1e-12, atol=1e-12)
    assert len(class_intervals) == 4 * 3 * 3 * 6
    for scope in ['8', '9', '10', 'pooled_9_10', 'equal_9_10']:
        sub = saved_draws[saved_draws.scope == scope]
        assert len(sub) == 2000
        np.testing.assert_allclose(sub.delta, sub.macro_f1_B - sub.macro_f1_A, atol=1e-12)


def test_bootstrap_preserves_identical_prediction_pair(predictions):
    # 통계 함수의 동일 예측 쌍 검증용 복사본이며 연구 결과로 저장하지 않음
    identical = predictions.copy()
    identical['pred_B'] = identical.pred_A
    intervals, _, draws = bootstrap_uncertainty(identical, repeats=64, seed=42)
    assert np.allclose(draws.delta, 0)
    delta = intervals[intervals.model == 'B_minus_A']
    assert np.allclose(delta.lower, 0) and np.allclose(delta.upper, 0)


def test_wilson_intervals_and_support():
    rows = pd.read_csv(OUT / 'recall_wilson_intervals.csv')
    for _, row in rows.iterrows():
        expected = binomtest(int(row.correct_n), int(row.support)).proportion_ci(confidence_level=.95, method='wilson')
        assert row.wilson_lower == pytest.approx(expected.low, abs=1e-12)
        assert row.wilson_upper == pytest.approx(expected.high, abs=1e-12)
    assert (rows.support > 0).all()


def test_graph_values_and_numeric_batch_order():
    checks = pd.read_csv(OUT / 'graph_value_checks.csv', dtype={'scope': str})
    metrics = pd.read_csv(OUT / 'evaluation_metrics.csv', dtype={'scope': str})
    classes = pd.read_csv(OUT / 'class_metrics.csv', dtype={'scope': str})
    matrices = pd.read_csv(OUT / 'confusion_matrices.csv', dtype={'scope': str})
    assert checks.matches.all()
    np.testing.assert_allclose(checks.displayed_value, checks.expected_value, atol=1e-10)
    numeric = checks[checks.scope.isin(['8', '9', '10'])]
    for _, group in numeric.groupby(['figure', 'series', 'model', 'gas_id', 'predicted_id', 'statistic'], sort=False):
        values = group.scope.astype(int).tolist()
        assert values == sorted(values)
    for _, row in numeric.iterrows():
        if row.statistic == 'macro_f1_pct':
            expected = metrics[(metrics.model == row.model) & (metrics.scope == row.scope)].macro_f1.iloc[0] * 100
        elif row.statistic == 'row_fraction_pct':
            expected = matrices[(matrices.model == row.model) & (matrices.scope == row.scope) &
                                (matrices.actual_id == row.gas_id) & (matrices.predicted_id == row.predicted_id)].row_fraction.iloc[0] * 100
        elif row.statistic == 'recall_delta_pp':
            sub = classes[(classes.scope == row.scope) & (classes.gas_id == row.gas_id)].set_index('model')
            expected = 100 * (sub.loc['B', 'recall'] - sub.loc['A', 'recall'])
        elif row.statistic == 'median_z':
            sensor = pd.read_csv(OUT / 'sensor_plot_statistics.csv', dtype={'partition': str})
            expected = sensor[(sensor.gas_id == row.gas_id) & (sensor.feature == row.series) &
                              (sensor.partition == row.scope)].median_z.iloc[0]
        else:
            sub = classes[(classes.model == row.model) & (classes.scope == row.scope) & (classes.gas_id == row.gas_id)].iloc[0]
            expected = sub.recall * 100 if row.statistic == 'recall_pct' else sub[row.statistic]
        assert row.displayed_value == pytest.approx(expected, abs=1e-10)


def test_korean_font_and_sensor_plot_statistics(dataset):
    font = read_json('korean_font_verification.json')
    assert font['font_family'] == 'Malgun Gothic' and font['missing_used_korean_glyphs'] == 0
    assert font['missing_used_glyphs'] == 0
    assert sha(font['font_file']) == font['font_sha256']
    metadata = pd.read_csv(OUT / 'graph_metadata.csv')
    assert len(metadata) == 8 and metadata.titles_axes_legends_present.all()
    assert (metadata.missing_korean_glyphs == 0).all()
    for row in metadata.to_dict('records'):
        assert sha(ROOT / row['path']) == row['sha256']
    model_A = joblib.load(ROOT / read_json('experiment_config.json')['models']['A']['path'])
    scaler = model_A.named_steps['scaler']
    for row in pd.read_csv(OUT / 'sensor_plot_statistics.csv').to_dict('records'):
        end = {'Train1–6': 6, 'Train1–7': 7}.get(row['partition'])
        sub = dataset[(dataset.batch <= end) & (dataset.gas == row['gas_id'])] if end else dataset[
            (dataset.batch == int(row['partition'])) & (dataset.gas == row['gas_id'])]
        j = FEATURES.index(row['feature'])
        z = (sub[row['feature']] - scaler.mean_[j]) / scaler.scale_[j]
        assert row['n'] == len(sub) and row['median_z'] == pytest.approx(z.median())


def test_existing_files_raw_and_model_inventory_preserved():
    manifest = read_json('run_manifest.json')
    assert manifest['before'] == manifest['after']
    for name, expected in manifest['before'].items():
        assert sha(ROOT / name) == expected
    for name, expected in manifest['raw_hashes'].items():
        assert sha(Path(read_config()['data_dir']) / name) == expected
    actual = {str(path.relative_to(ROOT)) for path in (ROOT / 'models').rglob('*.joblib')}
    old = {name for name in manifest['before'] if name.endswith('.joblib')}
    assert actual == old
    assert sha(OUT / 'experiment_config.json') == manifest['experiment_sha256']
    config = read_json('experiment_config.json')
    assert datetime.fromisoformat(config['frozen_at_seoul']) <= datetime.fromisoformat(manifest['evaluation_started_at_seoul'])


def test_no_new_fit_calls_and_report_structure():
    for name in ['temporal_generalization_validation.py', 'generalization_history.py',
                 'generalization_visuals.py', 'generalization_report.py']:
        source = (ROOT / 'src' / name).read_text(encoding='utf-8')
        tree = ast.parse(source)
        assert not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and
                       n.func.attr in ['fit', 'fit_transform', 'partial_fit'] for n in ast.walk(tree))
    assert read_json('run_manifest.json')['new_model_fits'] == 0
    report = (ROOT / 'reports/temporal_generalization_validation_report.html').read_text(encoding='utf-8')
    assert report.count('<h2>') == 12 and report.count('data:image/png;base64,') == 8
    assert '새 독립 Test 없음' in report and '독립적인 미래 Batch 일반화의 신뢰구간이 아니며' in report
