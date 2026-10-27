# HGB 단독 대조의 동일 행·가중치·누수·보호 기준·보존 검사

import ast
from datetime import datetime
import json

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import f1_score, precision_recall_fscore_support

from src.data import ROOT, FEATURES, GASES, load_dataset, read_config
from src.temporal_expansion import sha
from src.nonlinear_feature_transformation import score_predictions
from src.hgb_algorithm_comparison import (
    OUT, MODEL_DIR, FOLDS, HGB_PARAMS, splits, error_agreement, judge,
    verify, row_digest, digest,
)


def read(name):
    return pd.read_csv(OUT/f'{name}.csv')


def read_json(name):
    return json.loads((OUT/name).read_text(encoding='utf-8'))


@pytest.fixture(scope='module')
def state():
    frame, _ = load_dataset(read_config())
    return frame[frame.batch <= 8].copy(), read_json('model_registry.json')


# 학습 없는 환경·함수 검사
def test_hgb_environment_supports_fixed_parameters():
    model = HistGradientBoostingClassifier(**HGB_PARAMS)
    model._validate_params()
    assert model.get_params() == HGB_PARAMS
    assert model.class_weight == 'balanced' and model.__sklearn_tags__().input_tags.allow_nan
    assert model.early_stopping is False and model.validation_fraction is None


def test_error_agreement_four_mutually_exclusive_categories():
    result = error_agreement([1,2,3,4], [1,2,1,1], [1,1,3,2])
    assert result.both_correct.sum() == 1 and result.svm_only.sum() == 1
    assert result.hgb_only.sum() == 1 and result.both_wrong.sum() == 1
    assert result.disagreement.sum() == 3
    assert result[['both_correct','svm_only','hgb_only','both_wrong']].sum(axis=1).eq(1).all()


def test_error_agreement_requires_same_rows():
    with pytest.raises(ValueError):
        error_agreement([1,2], [1], [1,2])


def test_absent_truth_class_not_zero_recall():
    metrics, classes, _ = score_predictions([1,1,2], [1,2,2])
    assert classes[classes.gas_id == 6].recall.isna().all()
    assert metrics['zero_recall'] == 0


def synthetic_scores(gain=.005):
    metrics, classes = [], []
    for model in ['SVM','HGB']:
        for fold in FOLDS:
            metrics.append(dict(model=model,fold=fold,macro_f1=.5+(gain if model == 'HGB' else 0)))
            for g in GASES:
                classes.append(dict(model=model,fold=fold,gas_id=g,precision=.5,
                                    recall=.45 if model == 'HGB' else .5,
                                    f1=.48 if model == 'HGB' else .5))
    return pd.DataFrame(metrics), pd.DataFrame(classes)


def test_protection_thresholds_inclusive_and_new_zero_rejected():
    metrics, classes = synthetic_scores()
    assert judge(metrics,classes)['all_passed']
    classes.loc[(classes.model == 'HGB')&(classes.fold == 'A')&(classes.gas_id == 6),'recall'] = 0
    assert not judge(metrics,classes)['checks']['no_new_zero_guard']


def test_negative_macro_with_no_f1_gain_is_category_c():
    metrics, classes = synthetic_scores(gain=-.01)
    assert judge(metrics,classes)['conclusion'] == 'C'
    classes.loc[(classes.model == 'HGB')&(classes.gas_id == 6),'f1'] = .51
    assert judge(metrics,classes)['conclusion'] == 'B'


def test_plan_lock_preflight_and_training_budget():
    plan, lock = read_json('experiment_plan.json'), read_json('plan_lock.json')
    assert sha(OUT/'experiment_plan.json') == lock['plan_sha256']
    assert sha(OUT/'protocol.md') == lock['protocol_sha256']
    assert sha(OUT/'split_assignments.csv') == plan['split_sha256']
    assert sha(OUT/'svm_preflight.json') == plan['svm_preflight_sha256']
    assert plan['hgb_parameters'] == HGB_PARAMS
    assert plan['budget']['maximum_new_HGB_fits'] == 3
    assert not plan['independent_test'] and plan['future_batches_evaluated'] == []
    assert datetime.fromisoformat(plan['frozen_at']) <= datetime.fromisoformat(read_json('started.json')['started_at'])
    assert all(row['can_reuse'] for row in read_json('svm_preflight.json'))


def test_ordered_rows_feature_hashes_and_temporal_separation(state):
    frame, _ = state
    planned, support = splits(frame)
    pd.testing.assert_frame_equal(planned,read('split_assignments'))
    pd.testing.assert_frame_equal(support,read('fold_support'))
    audits = read('train_only_audit')
    for fold,(end,batch) in FOLDS.items():
        sub = audits[audits.fold == fold]
        train, validation = frame[frame.batch <= end], frame[frame.batch == batch]
        assert sub.train_n.eq(len(train)).all()
        assert sub.train_row_sha256.eq(row_digest(train.row_id)).all()
        assert sub.train_input_sha256.eq(digest(train[FEATURES])).all()
        assert sub.validation_row_sha256.eq(row_digest(validation.row_id)).all()
        assert sub.feature_order_sha256.eq(row_digest(FEATURES)).all()
        assert train.batch.max() < validation.batch.min()


def test_train_only_imputation_and_hgb_input_order(state):
    frame, registry = state
    for entry in registry:
        model = joblib.load(ROOT/entry['path'])
        train = frame[frame.batch <= FOLDS[entry['fold']][0]]
        np.testing.assert_array_equal(model['imputer'].feature_names_in_,FEATURES)
        np.testing.assert_allclose(model['imputer'].statistics_,train[FEATURES].median())
        assert model['imputer'].transform(train[FEATURES]).shape == (len(train),128)
        if entry['model'] == 'HGB':
            assert list(model.named_steps) == ['imputer','classifier']
            assert model.training_input_sha256_ == digest(train[FEATURES])
            assert model.training_row_ids_sha256_ == row_digest(train.row_id)
            before = model['imputer'].statistics_.copy()
            model['imputer'].transform(train[FEATURES]*100)
            np.testing.assert_array_equal(before,model['imputer'].statistics_)
        np.testing.assert_array_equal(model['classifier'].classes_,list(GASES))


def test_balanced_class_weights_computed_only_from_train(state):
    frame, registry = state
    weights = read('class_weights')
    for entry in registry:
        train = frame[frame.batch <= FOLDS[entry['fold']][0]]
        model = joblib.load(ROOT/entry['path'])
        sub = weights[(weights.fold == entry['fold'])&(weights.model == entry['model'])].sort_values('gas_id')
        counts = train.gas.value_counts().sort_index()
        np.testing.assert_array_equal(sub.train_support,counts)
        np.testing.assert_allclose(sub.class_weight,len(train)/(6*counts))
        np.testing.assert_allclose(sub.sample_weight_sum,len(train)/6)
        if entry['model'] == 'HGB':
            actual = model['classifier']._finalize_sample_weight(None,train.gas.to_numpy())
            expected = np.array([len(train)/(6*counts[g]) for g in train.gas])
            np.testing.assert_allclose(actual,expected)


def test_no_internal_or_external_validation_fit(state):
    _, registry = state
    for entry in registry:
        if entry['model'] != 'HGB':
            continue
        model = joblib.load(ROOT/entry['path'])['classifier']
        assert model.get_params() == HGB_PARAMS and model.n_iter_ == 100
        assert not model.do_early_stopping_ and len(model.validation_score_) == 0
        assert model.validation_fraction is None and model.random_state == 42
    audit = read('train_only_audit')
    assert not audit.external_validation_passed.any() and not audit.sample_weight_passed.any()
    tree = ast.parse((ROOT/'src/hgb_algorithm_comparison.py').read_text(encoding='utf-8'))
    fits = [n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr == 'fit']
    assert len(fits) == 1 and not fits[0].keywords and len(fits[0].args) == 2
    assert ast.unparse(fits[0].args[0]) == 'train[FEATURES]' and ast.unparse(fits[0].args[1]) == 'train.gas'


def test_model_reload_matches_saved_predictions(state):
    frame, registry = state
    predictions = read('predictions')
    assert len(list(MODEL_DIR.glob('*.joblib'))) == 3
    assert sum(e['new_fit'] for e in registry) == 3
    for entry in registry:
        assert sha(ROOT/entry['path']) == entry['sha256']
        validation = frame[frame.batch == FOLDS[entry['fold']][1]]
        sub = predictions[(predictions.fold == entry['fold'])&(predictions.model == entry['model'])]
        assert sub.row_id.tolist() == validation.row_id.tolist()
        np.testing.assert_array_equal(joblib.load(ROOT/entry['path']).predict(validation[FEATURES]),sub.y_pred)
    assert set(predictions.batch) == {6,7,8}


def test_metrics_confusion_error_directions_and_agreement():
    predictions, metrics, classes = read('predictions'), read('fold_metrics'), read('class_metrics')
    matrix = read('confusion')
    for (fold,model),sub in predictions.groupby(['fold','model']):
        p,r,f,support = precision_recall_fscore_support(sub.y_true,sub.y_pred,labels=list(GASES),zero_division=0)
        actual = classes[(classes.fold == fold)&(classes.model == model)].sort_values('gas_id')
        np.testing.assert_allclose(actual[['precision','recall','f1']],np.column_stack([p,r,f]))
        np.testing.assert_array_equal(actual.support,support)
        row = metrics[(metrics.fold == fold)&(metrics.model == model)].iloc[0]
        assert row.macro_f1 == pytest.approx(f1_score(sub.y_true,sub.y_pred,average='macro'))
        assert row.toluene_to_acetaldehyde == ((sub.y_true == 6)&(sub.y_pred == 4)).sum()
        assert matrix[(matrix.fold == fold)&(matrix.model == model)].n.sum() == len(sub)
    for fold,sub in read('error_agreement').groupby('fold'):
        actual = error_agreement(sub.y_true,sub.svm_pred,sub.hgb_pred)
        for col in actual:
            np.testing.assert_array_equal(sub[col],actual[col])


def test_protection_judgement_reproduces_saved_conclusion():
    expected = read_json('conclusion_frozen.json')
    actual = judge(read('fold_metrics'),read('class_metrics'))
    assert actual['checks'] == expected['checks'] and actual['conclusion'] == expected['conclusion']
    assert actual['mean_macro_delta'] == pytest.approx(expected['mean_macro_delta'])
    assert expected['new_HGB_fits'] == 3 and expected['fallback_SVM_fits'] == 0


def test_prior_files_raw_models_preserved_and_graphs_complete():
    assert verify()['all_preserved']
    graph = read('graph_manifest')
    assert len(graph) == 8 and graph.batch_support_and_axes_labelled.all()
    for row in graph.itertuples():
        assert sha(ROOT/row.path) == row.sha256
    text = (ROOT/'reports/hgb_algorithm_comparison_report.html').read_text(encoding='utf-8')
    assert text.count('data:image/png;base64,') == 8
    assert '공식 Model A 유지' in text and '독립 Test가 아님' in text
