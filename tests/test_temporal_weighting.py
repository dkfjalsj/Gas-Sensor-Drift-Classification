# 가중치 계산·시간순 분할·Train 전처리와 저장 예측 재현 확인

import json
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import f1_score, precision_recall_fscore_support
from threadpoolctl import threadpool_limits

from src.data import ROOT, FEATURES, load_dataset, read_config
from src.temporal_expansion import sha
from src.temporal_robustness import FOLDS, sha_rows, split_folds
from src.temporal_weighting import OUT, MODELS, SCHEMES, select_candidate


@pytest.fixture(scope='module')
def dataset():
    return load_dataset(read_config())[0]


@pytest.fixture(scope='module')
def weights():
    return pd.read_csv(OUT / 'sample_weights.csv.gz')


def read_json(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))


def test_fixed_fold_counts_and_support(dataset):
    support = split_folds(dataset)
    pd.testing.assert_frame_equal(support, pd.read_csv(OUT / 'fold_support.csv'))
    assert support.groupby(['fold', 'partition']).n.sum().to_dict() == {
        ('A', 'train'): 3275, ('A', 'validation'): 2300,
        ('B', 'train'): 5933, ('B', 'validation'): 3613,
        ('C', 'train'): 9546, ('C', 'validation'): 294,
    }
    assert support.query('fold=="A" and partition=="train" and gas_id==6').n.iloc[0] == 79
    assert support.query('fold=="C" and partition=="validation" and gas_id==6').n.iloc[0] == 18


def test_weight_formulas_limits_and_actual_cells(dataset, weights):
    for (fold, scheme), group in weights.groupby(['fold', 'scheme']):
        train = dataset[dataset.batch <= FOLDS[fold][0]]
        np.testing.assert_array_equal(group.row_id, train.row_id)
        assert not set(group.row_id) & set(dataset[dataset.batch > FOLDS[fold][0]].row_id)
        counts = train.gas.value_counts()
        c = train.gas.map(len(train) / (6 * counts)).to_numpy()
        u = (train.batch.to_numpy() - train.batch.min()) / (train.batch.max() - train.batch.min())
        t, r, gas_factor = np.ones(len(train)), np.ones(len(train)), c.copy()
        if scheme in ['time_linear', 'time_class_shrink']:
            t = 1 + u
        elif scheme == 'time_exp':
            t = 2 ** u
        elif scheme == 'time_recent':
            t = np.where(train.batch >= train.batch.max() - 1, 1.75, 1)
        if scheme in ['gas_batch', 'time_gas_batch']:
            cells = train.groupby(['gas', 'batch']).size()
            n_batches = train.groupby('gas').batch.nunique()
            r = np.array([np.clip(np.sqrt(counts[g] / (n_batches[g] * cells[g, b])), .75, 1.5)
                          for g, b in zip(train.gas, train.batch)])
        if scheme == 'time_gas_batch':
            t = np.sqrt(1 + u)
        if scheme == 'time_class_shrink':
            gas_factor = np.sqrt(c)
        raw = gas_factor * t * r
        np.testing.assert_allclose(group.effective_weight, raw / raw.mean())
        np.testing.assert_allclose(group.applied_class_factor * group.sample_weight, group.effective_weight)
        assert group.effective_weight.mean() == pytest.approx(1)
        assert group.effective_weight.min() > 0
        assert group.temporal_factor.min() >= 1 - 1e-12 and group.temporal_factor.max() <= 2 + 1e-12
        assert group.cell_factor.min() >= .75 - 1e-12 and group.cell_factor.max() <= 1.5 + 1e-12
        assert len(group) == len(train)


def test_train_only_scaling_and_effective_class_weight(dataset, weights):
    for record in read_json('fit_records.json'):
        train = dataset[dataset.batch <= FOLDS[record['fold']][0]]
        model = joblib.load(ROOT / record['model_file'])
        group = weights[(weights.fold == record['fold']) & (weights.scheme == record['scheme'])]
        np.testing.assert_allclose(model.named_steps['imputer'].statistics_, train[FEATURES].median())
        scaler = model.named_steps['scaler']
        assert scaler.n_samples_seen_ == len(train)
        np.testing.assert_allclose(scaler.mean_, train[FEATURES].mean(), atol=1e-10)
        np.testing.assert_allclose(scaler.var_, train[FEATURES].var(ddof=0), rtol=1e-9)
        classifier = model.named_steps['classifier']
        assert classifier.C == 1 and classifier.gamma == 'scale' and classifier.kernel == 'rbf'
        actual = train.gas.map(pd.Series(classifier.class_weight_, index=classifier.classes_)).to_numpy()
        np.testing.assert_allclose(actual * group.sample_weight.to_numpy(), group.effective_weight)
        assert record['train_row_ids_sha256'] == sha_rows(train.row_id)
        assert classifier.fit_status_ == 0


def test_equivalence_control_and_concentration(weights):
    records = read_json('fit_records.json')
    for fold in FOLDS:
        a = weights[(weights.fold == fold) & (weights.scheme == 'class_balanced')]
        b = weights[(weights.fold == fold) & (weights.scheme == 'class_sample')]
        np.testing.assert_allclose(a.effective_weight, b.effective_weight)
    for record in records:
        group = weights[(weights.fold == record['fold']) & (weights.scheme == record['scheme'])]
        concentration = group.effective_weight.sum() ** 2 / np.square(group.effective_weight).sum()
        assert record['weight_concentration_n'] == pytest.approx(concentration)
        assert 0 < concentration <= len(group) + 1e-8


def test_fold_prediction_reproduction_and_metrics(dataset):
    predictions = pd.read_csv(OUT / 'fold_predictions.csv.gz')
    cv = pd.read_csv(OUT / 'cv_summary.csv')
    metrics = pd.read_csv(OUT / 'fold_metrics.csv')
    for record in read_json('fit_records.json'):
        assert sha(ROOT / record['model_file']) == record['sha256']
        validation = dataset[dataset.batch == FOLDS[record['fold']][1]]
        model = joblib.load(ROOT / record['model_file'])
        subset = predictions[(predictions.config_id == record['scheme']) & (predictions.fold == record['fold'])]
        with threadpool_limits(limits=2):
            actual = model.predict(validation[FEATURES])
        np.testing.assert_array_equal(actual, subset.y_pred)
        row = metrics[(metrics.config_id == record['scheme']) & (metrics.fold == record['fold'])].iloc[0]
        assert row.macro_f1 == pytest.approx(f1_score(validation.gas, actual, average='macro'))
    for _, row in cv.iterrows():
        sub = metrics[metrics.config_id == row.config_id]
        assert row.mean_macro_f1 == pytest.approx(sub.macro_f1.mean())
        assert row.sd_macro_f1 == pytest.approx(sub.macro_f1.std(ddof=0))


def test_selection_guards_and_evaluation_gate():
    cv = pd.read_csv(OUT / 'cv_summary.csv')
    metrics = pd.read_csv(OUT / 'fold_metrics.csv')
    classes = pd.read_csv(OUT / 'fold_class_metrics.csv')
    candidate, guards = select_candidate(cv, metrics, classes)
    stored = pd.read_csv(OUT / 'guard_checks.csv').fillna('')
    pd.testing.assert_frame_equal(guards.fillna(''), stored)
    decision = read_json('selection_frozen.json')
    assert decision['selected_scheme'] == candidate
    assert decision['baseline_retained'] == (candidate == 'class_balanced')
    gate = read_json('evaluation_gate.json')
    assert datetime.fromisoformat(decision['frozen_at_seoul']) <= datetime.fromisoformat(gate['evaluation_started_at_seoul'])
    assert gate['selection_sha256'] == sha(OUT / 'selection_frozen.json')
    assert not gate['evaluation_used_for_selection']
    if decision['baseline_retained']:
        previous = json.loads((ROOT / 'outputs/temporal_expansion/selection_frozen.json').read_text(encoding='utf-8'))
        assert decision['selected_models']['6']['sha256'] == previous['selected_models']['B_SVM_balanced']['sha256']
    for record in decision['selected_models'].values():
        assert sha(ROOT / record['path']) == record['sha256']


def test_common_range_comparison_on_future_batch8(dataset):
    predictions = pd.read_csv(OUT / 'range_batch8_predictions.csv.gz', dtype={'fold': str})
    future = dataset[dataset.batch == 8]
    assert predictions.batch.unique().tolist() == [8]
    for (scheme, end), group in predictions.groupby(['config_id', 'fold']):
        fold = 'B' if end == '6' else 'C'
        model = joblib.load(MODELS / fold / f'{scheme}.joblib')
        with threadpool_limits(limits=2):
            actual = model.predict(future[FEATURES])
        np.testing.assert_array_equal(actual, group.y_pred)
        np.testing.assert_array_equal(group.row_id, future.row_id)
    assert (future.gas == 6).sum() == 18


def test_evaluation_reproduction_and_per_class_metrics(dataset):
    predictions = pd.read_csv(OUT / 'evaluation_predictions.csv.gz')
    classes = pd.read_csv(OUT / 'evaluation_classes.csv', dtype={'fold': str})
    future = dataset[dataset.batch >= 9]
    for record in pd.read_csv(OUT / 'evaluation_models.csv').to_dict('records'):
        path = ROOT / record['path']
        assert sha(path) == record['sha256']
        model = joblib.load(path)
        subset = predictions[predictions.config_id == record['model_id']]
        with threadpool_limits(limits=2):
            actual = model.predict(future[FEATURES])
        np.testing.assert_array_equal(actual, subset.y_pred)
    for (config_id, scope), group in classes.groupby(['config_id', 'fold']):
        sub = predictions[predictions.config_id == config_id]
        if scope != 'pooled':
            sub = sub[sub.batch == int(scope)]
        p, r, f, n = precision_recall_fscore_support(sub.y_true, sub.y_pred, labels=range(1, 7), zero_division=0)
        group = group.sort_values('gas_id')
        for column, expected in [('precision', p), ('recall', r), ('f1', f), ('support', n)]:
            np.testing.assert_allclose(group[column], expected)


def test_existing_files_and_raw_preserved():
    manifest = read_json('run_manifest.json')
    assert manifest['before'] == manifest['after']
    for name, expected in manifest['before'].items():
        assert sha(ROOT / name) == expected
    for name, expected in manifest['raw_hashes'].items():
        assert sha(Path(read_config()['data_dir']) / name) == expected
    assert sha(OUT / 'experiment_plan.json') == manifest['plan_sha256']
    assert sha(ROOT / 'reports/temporal_weighting_protocol.md') == manifest['protocol_sha256']
    for name, expected in manifest['code_sha256'].items():
        assert sha(ROOT / 'src' / name) == expected


def test_budget_and_report():
    assert len(read_json('fit_records.json')) == 24
    assert read_json('experiment_plan.json')['setting_count'] == len(SCHEMES) == 8
    assert len(pd.read_csv(OUT / 'evaluation_models.csv')) == 18
    report = (ROOT / 'reports/temporal_weighting_report.html').read_text(encoding='utf-8')
    assert report.count('<h2>') == 10
    assert report.count('data:image/png;base64,') == 5
    assert '독립적인 최종 Test 성능이 아니다' in report
