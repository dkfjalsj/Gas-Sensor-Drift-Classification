# 시간순 분할·특징 선택·후보 동결과 저장 예측 재현 확인

import json
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.feature_selection import f_classif
from sklearn.metrics import f1_score, precision_recall_fscore_support
from threadpoolctl import threadpool_limits

from src.data import ROOT, FEATURES, load_dataset, read_config
from src.temporal_expansion import sha
from src.temporal_robustness import OUT, MODELS, FOLDS, choose, sha_rows, split_folds


@pytest.fixture(scope='module')
def dataset():
    return load_dataset(read_config())[0]


def read_json(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))


def test_fixed_folds_and_support(dataset):
    supports = split_folds(dataset)
    assert supports.groupby(['fold', 'partition']).n.sum().to_dict() == {
        ('A', 'train'): 3275, ('A', 'validation'): 2300,
        ('B', 'train'): 5933, ('B', 'validation'): 3613,
        ('C', 'train'): 9546, ('C', 'validation'): 294,
    }
    pd.testing.assert_frame_equal(supports, pd.read_csv(OUT / 'fold_support.csv'))
    for fold, (end, batch) in FOLDS.items():
        assert end < batch
        assert dataset[dataset.batch <= end].gas.nunique() == 6
        assert dataset[dataset.batch == batch].gas.nunique() == 6


def test_train_only_preprocessing_and_feature_inputs(dataset):
    for record in read_json('fit_records.json'):
        train = dataset[dataset.batch <= FOLDS[record['fold']][0]]
        model = joblib.load(ROOT / record['model_file'])
        selector = model.named_steps['selector']
        assert selector.n_samples_ == len(train) == record['train_n']
        assert selector.train_row_ids_sha256_ == sha_rows(train.row_id)
        assert selector.train_batches_ == sorted(train.batch.unique())
        assert list(model.feature_names_in_) == FEATURES
        assert set(selector.selected_features_).issubset(FEATURES)
        assert selector.selected_features_ == record['selected_features']
        np.testing.assert_allclose(model.named_steps['imputer'].statistics_, train[FEATURES].median())
        np.testing.assert_allclose(selector.training_mean_, train[FEATURES].mean())
        np.testing.assert_allclose(selector.training_std_, train[FEATURES].std(ddof=0))
        if record['family'] != 'RF':
            scaler = model.named_steps['scaler']
            selected = train[selector.selected_features_]
            assert scaler.n_samples_seen_ == len(train)
            np.testing.assert_allclose(scaler.mean_, selected.mean(), atol=1e-10)
            np.testing.assert_allclose(scaler.var_, selected.var(ddof=0), rtol=1e-9)


def test_feature_selection_uses_training_statistics(dataset):
    records = read_json('fit_records.json')
    for fold, (end, _) in FOLDS.items():
        train = dataset[dataset.batch <= end]
        values = train[FEATURES].to_numpy()
        for method in ['variance', 'correlation', 'stability64', 'kbest32', 'kbest64']:
            record = next(r for r in records if r['fold'] == fold and r['config_id'] == 'SVM_' + method)
            if method == 'variance':
                span = np.ptp(values, axis=0)
                score = np.var((values - values.min(axis=0)) / np.where(span == 0, 1, span), axis=0)
                indices = np.argsort(-score, kind='stable')[:115]
            elif method == 'correlation':
                corr = np.nan_to_num(np.corrcoef(values, rowvar=False), nan=0)
                indices = []
                for j in range(128):
                    if not indices or max(abs(corr[j, indices])) <= .98:
                        indices.append(j)
            elif method == 'stability64':
                shifts = []
                for _, gas_data in train.groupby('gas'):
                    if gas_data.batch.nunique() < 2:
                        continue
                    for _, group in gas_data.groupby('batch'):
                        shifts.append((group[FEATURES].mean() - gas_data[FEATURES].mean()).abs() /
                                      train[FEATURES].std(ddof=0))
                score = np.mean(shifts, axis=0)
                indices = np.argsort(score, kind='stable')[:64]
            else:
                score, _ = f_classif(values, train.gas)
                indices = np.argsort(score, kind='stable')[-int(method[5:]):]
            expected = [FEATURES[i] for i in sorted(indices)]
            assert expected == record['selected_features']
            for family in ['LR', 'RF']:
                other = next(r for r in records if r['fold'] == fold and
                             r['config_id'] == family + '_' + method)
                assert other['selected_features'] == expected


def test_fold_scores_and_candidate_selection():
    predictions = pd.read_csv(OUT / 'fold_predictions.csv.gz')
    metrics = pd.read_csv(OUT / 'fold_metrics.csv')
    cv = pd.read_csv(OUT / 'cv_summary.csv')
    for _, row in metrics.iterrows():
        subset = predictions[(predictions.config_id == row.config_id) & (predictions.fold == row.fold)]
        assert row.macro_f1 == pytest.approx(f1_score(subset.y_true, subset.y_pred, average='macro'))
    for _, row in cv.iterrows():
        part = metrics[metrics.config_id == row.config_id]
        assert row.mean_macro_f1 == pytest.approx(part.macro_f1.mean())
        assert row.sd_macro_f1 == pytest.approx(part.macro_f1.std(ddof=0))
    decision = read_json('selection_frozen.json')
    assert choose(cv, 'SVM_all')[0] == decision['selected_candidate']
    for family, config_id in decision['family_representatives'].items():
        assert choose(cv[cv.config_id.str.startswith(family + '_')], family + '_all')[0] == config_id


def test_serialized_fold_and_ensemble_predictions_reproduce(dataset):
    predictions = pd.read_csv(OUT / 'fold_predictions.csv.gz')
    for (config_id, fold), sub in predictions.groupby(['config_id', 'fold']):
        validation = dataset[dataset.batch == FOLDS[fold][1]]
        model = joblib.load(MODELS / fold / f'{config_id}.joblib')
        with threadpool_limits(limits=2):
            actual = model.predict(validation[FEATURES])
        np.testing.assert_array_equal(sub.row_id, validation.row_id)
        np.testing.assert_array_equal(actual, sub.y_pred)
    for record in read_json('fit_records.json'):
        assert sha(ROOT / record['model_file']) == record['sha256']


def test_evaluation_gate_and_baseline_reproduction(dataset):
    gate = read_json('evaluation_gate.json')
    decision = read_json('selection_frozen.json')
    assert datetime.fromisoformat(decision['frozen_at_seoul']) <= datetime.fromisoformat(
        gate['evaluation_started_at_seoul'])
    assert sha(OUT / 'selection_frozen.json') == gate['selection_sha256']
    assert not gate['evaluation_used_for_selection']
    pred = pd.read_csv(OUT / 'evaluation_predictions.csv.gz')
    for record in pd.read_csv(OUT / 'evaluation_model_hashes.csv').to_dict('records'):
        path = ROOT / record['model_file']
        assert sha(path) == record['sha256']
        model = joblib.load(path)
        future = dataset[dataset.batch >= 9]
        with threadpool_limits(limits=2):
            actual = model.predict(future[FEATURES])
        subset = pred[pred.config_id == record['config_id']]
        np.testing.assert_array_equal(actual, subset.y_pred)
    np.testing.assert_array_equal(pred[pred.config_id == 'SVM_all'].y_pred,
                                  pred[pred.config_id == 'stage6_saved_SVM'].y_pred)


def test_evaluation_metrics_all_six_classes():
    predictions = pd.read_csv(OUT / 'evaluation_predictions.csv.gz')
    classes = pd.read_csv(OUT / 'evaluation_class_metrics.csv', dtype={'fold': str})
    for (config_id, scope), group in classes.groupby(['config_id', 'fold']):
        sub = predictions[predictions.config_id == config_id]
        if scope != 'pooled':
            sub = sub[sub.batch == int(scope)]
        p, r, f, n = precision_recall_fscore_support(sub.y_true, sub.y_pred, labels=range(1, 7), zero_division=0)
        group = group.sort_values('gas_id')
        for column, expected in [('precision', p), ('recall', r), ('f1', f), ('support', n)]:
            np.testing.assert_allclose(group[column], expected)


def test_budget_and_frozen_model_bytes():
    plan = read_json('experiment_plan.json')
    assert plan['single_settings'] == 18 and plan['ensemble_settings'] == 4
    assert len(read_json('fit_records.json')) == 54
    assert len(pd.read_csv(OUT / 'cv_summary.csv')) == 22
    for model in read_json('selection_frozen.json')['selected_models'].values():
        assert sha(ROOT / model['path']) == model['sha256']
    assert read_json('selection_frozen.json')['final_train_batches'] == list(range(1, 7))


def test_existing_files_and_raw_preserved():
    state = read_json('run_manifest.json')
    assert state['before'] == state['after']
    for name, expected in state['before'].items():
        assert sha(ROOT / name) == expected
    for name, expected in state['raw_hashes'].items():
        assert sha(Path(read_config()['data_dir']) / name) == expected
    assert sha(OUT / 'experiment_plan.json') == state['plan_sha256']
    assert sha(ROOT / 'reports/temporal_robustness_protocol.md') == state['protocol_sha256']
    for name, expected in state['code_sha256'].items():
        assert sha(ROOT / 'src' / name) == expected


def test_report_and_exploratory_labels():
    report = (ROOT / 'reports/temporal_robustness_improvement_report.html').read_text(encoding='utf-8')
    assert report.count('<h2>') == 9
    assert report.count('data:image/png;base64,') == 4
    assert '탐색적' in report and '독립적인 최종 Test가 아니다' in report
