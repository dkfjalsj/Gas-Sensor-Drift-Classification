# 시기별 전문가의 누수·상호 보완성·Oracle·결합 및 보존 검사

import json
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import f1_score, precision_recall_fscore_support

from src.data import ROOT, FEATURES, GASES, load_dataset, read_config
from src.temporal_expansion import sha
from src.temporal_svm_ensemble import (
    OUT, FOLDS, EXPERTS, expert_rows, audit_model, complement, combine,
    gate_decision, summarize, verify, row_digest, digest,
)


def read(name):
    return pd.read_csv(OUT/f'{name}.csv')


def read_json(name):
    return json.loads((OUT/name).read_text(encoding='utf-8'))


@pytest.fixture(scope='module')
def state():
    frame, _ = load_dataset(read_config())
    return frame[frame.batch <= 8].copy(), read('expert_audit')


def test_complement_counts_and_oracle_fallback():
    y = np.array([1, 2, 3, 4, 6])
    pred = np.array([[1, 1, 1], [1, 2, 1], [3, 2, 3], [1, 2, 3], [4, 4, 4]])
    samples, correct = complement(y, pred)
    assert samples.all_correct.sum() == 1
    assert samples.some_correct.sum() == 2
    assert samples.all_wrong.sum() == 2
    assert samples.disagreement.sum() == 3
    assert samples.identical_wrong.sum() == 1
    np.testing.assert_array_equal(samples.oracle_pred, [1, 2, 3, 1, 4])
    np.testing.assert_array_equal(samples.correct_experts, correct.sum(axis=1))


def test_hard_vote_tie_uses_full_then_class_id():
    pred = np.array([[4, 6], [2, 3], [1, 2]])
    np.testing.assert_array_equal(combine(pred), [4, 2, 1])
    pred = np.array([[6, 1, 1, 2, 2], [6, 1, 1, 6, 2]])
    np.testing.assert_array_equal(combine(pred), [1, 6])


def test_rank_uses_order_and_full_rank_for_ties():
    scores = np.array([[[6, 5, 4, 3, 2, 1]], [[1, 2, 3, 4, 5, 6]]], dtype=float)
    pred = np.array([[1, 6]])
    assert combine(pred, scores, 'rank_equal').item() == 1
    scores[1] = scores[1]*1000+7
    assert combine(pred, scores, 'rank_equal').item() == 1


@pytest.mark.parametrize('scores', [np.zeros((2, 1, 15)), np.full((2, 1, 6), np.nan)])
def test_invalid_rank_format_rejected(scores):
    with pytest.raises(ValueError):
        combine(np.array([[1, 2]]), scores, 'rank_equal')


def test_plan_frozen_before_diagnostics():
    plan, lock = read_json('experiment_plan.json'), read_json('plan_lock.json')
    assert sha(OUT/'experiment_plan.json') == lock['plan_sha256']
    assert sha(OUT/'protocol.md') == lock['protocol_sha256']
    assert sha(OUT/'planned_rows.csv') == plan['plan_rows_sha256']
    assert sha(OUT/'expert_plan.csv') == plan['expert_plan_sha256']
    assert plan['seed'] == 42 and plan['candidates'] == ['hard_equal', 'rank_equal']
    assert not plan['independent_test'] and plan['future_batches_evaluated'] == []
    assert datetime.fromisoformat(plan['frozen_at']) <= datetime.fromisoformat(read_json('started.json')['started_at'])


def test_expert_rows_reproducible_past_only_and_same_validation(state):
    frame, audits = state
    planned = read('planned_rows')
    fingerprints = pd.util.hash_pandas_object(frame[FEATURES], index=False)
    for row in audits.itertuples():
        end, batch = FOLDS[row.fold]
        train = frame.loc[expert_rows(frame, end, row.expert)]
        validation = frame[frame.batch == batch]
        selected = planned[(planned.fold == row.fold) & (planned.expert == row.expert)]
        assert selected[selected.partition == 'train'].row_id.tolist() == train.row_id.tolist()
        assert selected[selected.partition == 'validation'].row_id.tolist() == validation.row_id.tolist()
        assert train.batch.max() <= end < batch
        assert set(train.row_id).isdisjoint(validation.row_id)
        assert set(fingerprints.loc[train.index]).isdisjoint(fingerprints.loc[validation.index])
        assert row.row_sha256 == row_digest(train.row_id) and row.input_sha256 == digest(train[FEATURES])
        assert row.validation_rows_sha256 == row_digest(validation.row_id)
    for fold in FOLDS:
        sub = audits[audits.fold == fold]
        assert sub.validation_rows_sha256.nunique() == 1


def test_recent_and_spread_have_equal_gas_budgets_and_no_future_dependence(state):
    frame, _ = state
    for fold, (end, _) in FOLDS.items():
        counts = []
        for expert in ['recent', 'spread']:
            ids = expert_rows(frame, end, expert)
            np.testing.assert_array_equal(ids, expert_rows(frame[frame.batch <= end], end, expert))
            counts.append(frame.loc[ids].gas.value_counts().sort_index().tolist())
        assert counts[0] == counts[1] == [127, 216, 91, 69, 301, 39]


def test_train_only_scaler_imputer_mapping_and_support_vectors(state):
    frame, audits = state
    for row in audits.itertuples():
        model = joblib.load(ROOT/row.model_path)
        train = frame.loc[expert_rows(frame, FOLDS[row.fold][0], row.expert)]
        checked = audit_model(model, train, FOLDS[row.fold][0])
        assert checked['train_n'] == row.train_n and checked['actual_gamma'] == pytest.approx(row.actual_gamma)
        assert len(model['imputer'].statistics_) == 128 and model['scaler'].n_features_in_ == 128
        np.testing.assert_array_equal(model['classifier'].classes_, list(GASES))


def test_reloaded_expert_predictions_and_rank_mapping(state):
    frame, audits = state
    predictions = read('predictions')
    for row in audits.itertuples():
        assert sha(ROOT/row.model_path) == row.sha256
        validation = frame[frame.batch == FOLDS[row.fold][1]]
        model = joblib.load(ROOT/row.model_path)
        sub = predictions[(predictions.fold == row.fold) & (predictions.model == row.expert)]
        assert sub.row_id.tolist() == validation.row_id.tolist()
        np.testing.assert_array_equal(model.predict(validation[FEATURES]), sub.y_pred)
        scores = model.decision_function(validation[FEATURES])
        assert scores.shape == (len(validation), 6) and np.isfinite(scores).all()
    conclusion = read_json('conclusion_frozen.json')
    assert conclusion['new_expert_fits'] == 0
    assert conclusion['new_svc_fits'] == conclusion['aborted_technical_fits'] <= 9


def test_sample_complementarity_and_focus_counts_reproduced():
    samples = read('sample_complementarity')
    for fold, sub in samples.groupby('fold'):
        stacked = sub[[f'{name}_pred' for name in EXPERTS]].to_numpy()
        computed, correct = complement(sub.y_true, stacked)
        for key in computed:
            np.testing.assert_array_equal(sub[key], computed[key])
        for i, name in enumerate(EXPERTS):
            np.testing.assert_array_equal(sub[f'{name}_only_correct'], correct[:, i] & (correct.sum(axis=1) == 1))
    assert len(samples[(samples.fold == 'A') & (samples.y_true == 6)]) == 467


def test_oracle_metrics_and_pairwise_counts():
    samples, metrics, pairs = read('sample_complementarity'), read('fold_metrics'), read('pairwise_complementarity')
    for fold, sub in samples.groupby('fold'):
        oracle = metrics[(metrics.fold == fold) & (metrics.model == 'oracle')].iloc[0]
        assert oracle.accuracy == pytest.approx((~sub.all_wrong).mean())
        assert oracle.macro_f1 == pytest.approx(f1_score(sub.y_true, sub.oracle_pred, average='macro'))
        assert oracle.accuracy >= metrics[(metrics.fold == fold) & (metrics.role == 'expert')].accuracy.max()
    assert (pairs.both_correct+pairs.left_only+pairs.right_only+pairs.both_wrong).eq(pairs.n).all()


def test_gate_reproduction_and_fixed_thresholds():
    computed = gate_decision(read('fold_metrics')[lambda x:x.role != 'ensemble'],
                             read('class_metrics')[lambda x:x.role != 'ensemble'],
                             read('sample_complementarity'))
    saved = read_json('diagnostic_gate.json')
    assert computed['checks'] == saved['checks'] and computed['passed'] == saved['passed']
    assert computed['oracle_macro_gain'] == pytest.approx(saved['oracle_macro_gain'])
    metrics, classes = [], []
    for model in ['full', 'recent', 'spread', 'oracle']:
        for fold in FOLDS:
            metrics.append(dict(model=model, fold=fold, role='oracle' if model == 'oracle' else 'expert',
                                macro_f1=.71 if model == 'oracle' else .70))
            classes.extend(dict(model=model, fold=fold, gas_id=g, recall=.62 if model == 'oracle' else .60) for g in GASES)
    samples = pd.DataFrame(dict(y_true=[6]*10, oracle_rescue=[True]*10,
                                disagreement=[True]*10, some_correct=[True]*10))
    assert gate_decision(pd.DataFrame(metrics), pd.DataFrame(classes), samples)['passed']
    samples['some_correct'] = False
    assert not gate_decision(pd.DataFrame(metrics), pd.DataFrame(classes), samples)['passed']


def test_ensemble_gate_execution_and_predictions(state):
    frame, audits = state
    status, predictions = read('ensemble_execution'), read('predictions')
    gate = read_json('diagnostic_gate.json')
    for row in status.itertuples():
        assert row.executed == (gate['passed'] and (row.candidate != 'rank_equal' or audits.rank_valid.all()))
        if not row.executed:
            assert not predictions.model.eq(row.candidate).any()
            continue
        for fold in FOLDS:
            samples = read('sample_complementarity')
            samples = samples[samples.fold == fold]
            stacked = samples[[f'{name}_pred' for name in EXPERTS]].to_numpy()
            validation = frame[frame.batch == FOLDS[fold][1]]
            scores = np.stack([joblib.load(ROOT/audits[(audits.fold == fold) & (audits.expert == expert)].model_path.iloc[0]).decision_function(validation[FEATURES]) for expert in EXPERTS])
            expected = predictions[(predictions.model == row.candidate) & (predictions.fold == fold)].y_pred
            np.testing.assert_array_equal(combine(stacked, scores, row.candidate), expected)


def test_gas_metrics_and_protection_checks():
    predictions, metrics, classes = read('predictions'), read('fold_metrics'), read('class_metrics')
    for (fold, model), sub in predictions.groupby(['fold', 'model']):
        p, r, f, support = precision_recall_fscore_support(sub.y_true, sub.y_pred, labels=list(GASES), zero_division=0)
        actual = classes[(classes.fold == fold) & (classes.model == model)].sort_values('gas_id')
        np.testing.assert_allclose(actual[['precision', 'recall', 'f1']], np.column_stack([p, r, f]))
        np.testing.assert_array_equal(actual.support, support)
    pd.testing.assert_frame_equal(summarize(metrics, classes), read('summary'), check_dtype=False, atol=1e-12)


def test_raw_models_sources_preserved_and_no_future_predictions():
    assert verify()['all_preserved']
    assert set(read('predictions').batch) == {6, 7, 8}
    assert read_json('conclusion_frozen.json')['future_batches_evaluated'] == []
    assert not any(read('expert_audit').new_fit)


def test_report_oracle_warning_graphs_and_class_counts():
    text = (ROOT/'reports/temporal_svm_ensemble_report.html').read_text(encoding='utf-8')
    assert '실제 배포 가능한 모델이 아님' in text and '공식 Model A 유지' in text
    graph = read('graph_manifest')
    assert len(graph) == (11 if read('ensemble_execution').executed.any() else 9)
    assert text.count('data:image/png;base64,') == len(graph)
    assert graph.axes_and_support_labelled.all()
    for row in graph.itertuples():
        assert sha(ROOT/row.path) == row.sha256
