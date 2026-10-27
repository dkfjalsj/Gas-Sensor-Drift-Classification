# 비선형 특징 변환의 누수·보호 기준·모델 재현 및 보존 검사

import json
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import precision_recall_fscore_support

from src.data import ROOT, FEATURES, GASES, load_dataset, read_config
from src.temporal_expansion import sha
from src.nonlinear_feature_transformation import (
    OUT, MODEL_DIR, METHODS, FOLDS, TrainTransform, digest, row_digest,
    score_predictions, judge, validate_splits, verify_preservation,
)


# 이번 단계 결과와 실제 학습 행 공유
@pytest.fixture(scope='module')
def state():
    frame, _ = load_dataset(read_config())
    return frame[frame.batch <= 8].copy(), pd.read_csv(OUT/'model_registry.csv')


def read(name):
    return pd.read_csv(OUT/f'{name}.csv')


def read_json(name):
    return json.loads((OUT/name).read_text(encoding='utf-8'))


# 음수·영·양수 부호와 특징 순서 유지
@pytest.mark.parametrize('method', ['signed_log', 'yeo_johnson'])
def test_signed_zero_positive_and_order(method):
    values = np.array([[-4., 0., -2.], [-1., 0., 0.], [0., 0., 1.], [5., 0., 7.]])
    transformer = TrainTransform(method).fit(values)
    result = transformer.transform(values)
    assert result.shape == values.shape and np.isfinite(result).all()
    assert (np.diff(result[:, 0]) > 0).all()
    assert result[0, 0] < 0 and result[2, 0] == 0 and result[3, 0] > 0
    np.testing.assert_array_equal(transformer.get_feature_names_out(['a', 'b', 'c']), ['a', 'b', 'c'])
    np.testing.assert_array_equal(result[:, 1], np.zeros(4))


def test_constant_and_tiny_scale_rules():
    values = np.array([[0., 3., 1e-300], [0., 3., -1e-300], [0., 3., 0.]])
    log = TrainTransform('signed_log').fit(values)
    assert (log.scale_ >= 1e-12).all()
    np.testing.assert_allclose(log.transform(values), np.sign(values)*np.log1p(np.abs(values)/log.scale_))
    yj = TrainTransform('yeo_johnson').fit(values)
    assert yj.status_[:2] == ['constant_identity', 'constant_identity']
    assert np.isfinite(yj.transform(values)).all()


def test_transform_does_not_update_on_future_values():
    values = np.arange(48., dtype=float).reshape(12, 4)-12
    for method in ['signed_log', 'yeo_johnson']:
        transformer = TrainTransform(method).fit(values)
        before = (transformer.fit_input_sha256_, transformer.scale_.copy(), transformer.lambdas_.copy())
        transformer.transform(values * 10)
        assert transformer.fit_input_sha256_ == before[0] == digest(values)
        np.testing.assert_array_equal(transformer.scale_, before[1])
        np.testing.assert_array_equal(transformer.lambdas_, before[2])


def test_invalid_inputs_rejected():
    with pytest.raises(ValueError):
        TrainTransform().fit([[np.nan, 2.]])
    transformer = TrainTransform().fit([[0., 2.], [1., 3.]])
    with pytest.raises(ValueError):
        transformer.transform([[1., 2., 3.]])
    with pytest.raises(ValueError):
        transformer.transform([[np.inf, 1.]])


def test_frozen_plan_budget_and_timing():
    plan = read_json('experiment_plan.json')
    lock = read_json('plan_lock.json')
    assert sha(OUT/'experiment_plan.json') == lock['plan_sha256']
    assert sha(OUT/'protocol.md') == lock['protocol_sha256']
    assert plan['methods'] == METHODS and plan['maximum_pipeline_evaluations'] == 9
    assert not plan['future_evaluation']
    assert datetime.fromisoformat(plan['frozen_at']) <= datetime.fromisoformat(read_json('run_started.json')['started_at'])
    assert sha(OUT/'split_assignments.csv') == plan['split_sha256']


def test_time_order_equal_rows_and_no_exact_overlap(state):
    frame, registry = state
    assignments, support = validate_splits(frame)
    pd.testing.assert_frame_equal(assignments, read('split_assignments'))
    pd.testing.assert_frame_equal(support, read('fold_support'))
    audit = read('train_only_audit')
    for fold, (end, batch) in FOLDS.items():
        sub = audit[audit.fold == fold]
        assert sub.train_row_sha256.nunique() == sub.validation_row_sha256.nunique() == 1
        assert sub.train_n.eq(len(frame[frame.batch <= end])).all()
        assert sub.feature_order_sha256.eq(row_digest(FEATURES)).all()
    assert len(registry) == 9


def test_preprocessing_train_only_and_feature_order(state):
    frame, registry = state
    for row in registry.itertuples():
        train = frame[frame.batch <= FOLDS[row.fold][0]]
        model = joblib.load(ROOT/row.path)
        np.testing.assert_array_equal(model.feature_names_in_, FEATURES)
        np.testing.assert_allclose(model['imputer'].statistics_, train[FEATURES].median())
        raw = model['imputer'].transform(train[FEATURES])
        if row.method != 'baseline':
            transform = model['transform']
            assert transform.n_samples_seen_ == len(train)
            assert transform.fit_input_sha256_ == digest(raw)
            assert transform.n_features_in_ == 128
            expected_scale = np.maximum(np.median(np.abs(raw), axis=0),
                                        np.maximum(1e-12, 1e-12*np.max(np.abs(raw), axis=0)))
            np.testing.assert_allclose(transform.scale_, expected_scale)
            raw = transform.transform(raw)
        assert raw.shape == (len(train), 128)
        assert model['scaler'].n_samples_seen_ == len(train)
        np.testing.assert_allclose(model['scaler'].mean_, raw.mean(axis=0), atol=1e-10)
        np.testing.assert_allclose(model['scaler'].var_, raw.var(axis=0), rtol=1e-9)
        assert model['classifier'].C == 1 and model['classifier'].gamma == 'scale'
        assert model['classifier'].class_weight == 'balanced'
        np.testing.assert_array_equal(model['classifier'].classes_, list(GASES))


def test_saved_models_prediction_reproduction(state):
    frame, registry = state
    expected = read('predictions')
    for row in registry.itertuples():
        assert sha(ROOT/row.path) == row.sha256
        model = joblib.load(ROOT/row.path)
        validation = frame[frame.batch == FOLDS[row.fold][1]]
        sub = expected[(expected.fold == row.fold) & (expected.method == row.method)]
        assert sub.row_id.tolist() == validation.row_id.tolist()
        np.testing.assert_array_equal(model.predict(validation[FEATURES]), sub.y_pred)
    assert set(expected.batch) == {6, 7, 8}


def test_baseline_reuse_matches_original_predictions():
    registry = read('model_registry')
    assert registry.new_fit.sum() == 6 and len(list(MODEL_DIR.glob('*.joblib'))) == 9
    actual = read('predictions')
    old = pd.read_csv(ROOT/'outputs/temporal_robustness/fold_predictions.csv.gz')
    for row in registry[registry.method == 'baseline'].itertuples():
        assert sha(ROOT/row.source_path) == row.source_sha256
        sub = actual[(actual.fold == row.fold) & (actual.method == 'baseline')]
        previous = old[(old.fold == row.fold) & (old.config_id == 'SVM_all')].set_index('row_id')
        np.testing.assert_array_equal(sub.y_pred, previous.loc[sub.row_id, 'y_pred'])


def test_gamma_records_match_actual_train_variance(state):
    frame, registry = state
    audits = read('train_only_audit').set_index(['fold', 'method'])
    for row in registry.itertuples():
        model = joblib.load(ROOT/row.path)
        train = frame[frame.batch <= FOLDS[row.fold][0]]
        transformed = model[:-1].transform(train[FEATURES])
        expected = 1/(128*np.var(transformed)) if np.var(transformed) else 1.
        assert model['classifier']._gamma == pytest.approx(expected)
        assert audits.loc[(row.fold, row.method), 'actual_gamma'] == pytest.approx(expected)


def test_gas_metrics_and_error_directions():
    predictions = read('predictions')
    recorded = read('class_metrics')
    fold_metrics = read('fold_metrics')
    for (fold, method), sub in predictions.groupby(['fold', 'method']):
        metrics, classes, matrix = score_predictions(sub.y_true, sub.y_pred)
        actual = recorded[(recorded.fold == fold) & (recorded.method == method)].sort_values('gas_id')
        p, r, f, support = precision_recall_fscore_support(sub.y_true, sub.y_pred, labels=list(GASES), zero_division=0)
        np.testing.assert_allclose(actual[['precision', 'recall', 'f1']], np.column_stack([p, r, f]))
        np.testing.assert_array_equal(actual.support, support)
        row = fold_metrics[(fold_metrics.fold == fold) & (fold_metrics.method == method)].iloc[0]
        assert row.macro_f1 == pytest.approx(np.mean(f))
        assert row.toluene_to_acetaldehyde == ((sub.y_true == 6) & (sub.y_pred == 4)).sum()
        assert row.acetaldehyde_to_toluene == ((sub.y_true == 4) & (sub.y_pred == 6)).sum()


def test_absent_class_is_not_zero_recall():
    metrics, classes, _ = score_predictions([1, 1, 2], [1, 2, 2])
    assert classes.loc[classes.gas_id == 6, 'recall'].isna().all()
    assert metrics['zero_recall'] == 0


def test_protection_decisions_reproducible():
    metrics, classes = read('fold_metrics'), read('class_metrics')
    summary, guards = judge(metrics, classes)
    pd.testing.assert_frame_equal(summary, read('summary'), check_dtype=False, atol=1e-12)
    pd.testing.assert_frame_equal(guards, read('protection_checks'), check_dtype=False, atol=1e-12)
    for row in guards.itertuples():
        assert row.balanced_success == all([row.complete, row.macro_guard, row.gas_recall_guard,
                                          row.other_four_guard, row.zero_count_guard, row.no_new_zero_guard])


def test_guard_inclusive_threshold_and_new_zero():
    classes, metrics = [], []
    for method in METHODS:
        for fold in FOLDS:
            metrics.append(dict(method=method, fold=fold, status='ok', macro_f1=.5 if method == 'baseline' else .505,
                                accuracy=.5, weighted_f1=.5))
            for gas in GASES:
                classes.append(dict(method=method, fold=fold, gas_id=gas, precision=.5,
                                    recall=.5 if method == 'baseline' else .45,
                                    f1=.5 if method == 'baseline' else .48))
    _, guards = judge(pd.DataFrame(metrics), pd.DataFrame(classes))
    assert guards[guards.method == 'signed_log'].balanced_success.item()
    classes[-1]['recall'] = 0
    _, guards = judge(pd.DataFrame(metrics), pd.DataFrame(classes))
    assert not guards[guards.method == 'yeo_johnson'].no_new_zero_guard.item()


def test_original_files_raw_data_and_plan_preserved():
    verification = verify_preservation()
    assert verification['all_preserved'] and verification['raw_files'] == 10
    old = json.loads((ROOT/'outputs/temporal_generalization_validation/run_manifest.json').read_text(encoding='utf-8'))
    before = read_json('preservation_before.json')
    assert before['raw'] == old['raw_hashes']


def test_report_graphs_and_no_future_evaluation():
    report = (ROOT/'reports/nonlinear_feature_transformation_report.html').read_text(encoding='utf-8')
    assert report.count('data:image/png;base64,') == 8
    assert '새 독립 Test 없음' in report and '공식 Model A 유지' in report
    graph = read('graph_manifest')
    assert len(graph) == 8
    for row in graph.itertuples():
        assert sha(ROOT/row.path) == row.sha256
    assert read('distribution_examples').train_n.eq(3275).all()
    assert read_json('selection_frozen.json')['future_batches_evaluated'] == []
