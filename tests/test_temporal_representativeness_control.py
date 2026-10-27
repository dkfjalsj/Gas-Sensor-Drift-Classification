# 대표성 통제 실험의 예산·표본·전처리·지표·보존 검사

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support

from src.data import ROOT, FEATURES, GASES, load_dataset, read_config
from src.temporal_expansion import sha
from src.temporal_representativeness_control import (
    OUT, MODEL_DIR, FOLDS, SEEDS, SETTINGS, FUTURE_SETTINGS, REPORTS,
    allocate, budgets, sample_rows,
)


# 실제 자료·고정 계획·표본 기록 공유
@pytest.fixture(scope='module')
def state():
    frame, _ = load_dataset(read_config())
    return frame, read_json('experiment_plan.json'), read('sample_assignments'), read('fit_records')


# 검사 대상 기록 불러오기
def read(name):
    return pd.read_csv(OUT / f'{name}.csv')


def read_json(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))


def test_frozen_budget_scope_and_exact_counts(state):
    frame, plan, _, _ = state
    expected = budgets(frame)
    assert [sum(expected[b].values()) for b in ['small', 'mid', 'max']] == [419, 843, 1689]
    assert expected['mid'] == {1: 127, 2: 216, 3: 91, 4: 69, 5: 301, 6: 39}
    assert plan['seeds'] == SEEDS and plan['classifier_fits'] == 120
    assert not plan['candidate_selection'] and plan['official_main_candidate'] == 'Model A'
    assert sha(OUT / 'sample_assignments.csv') == plan['sample_assignments_sha256']


def test_sampling_reproduces_all_120_subsets(state):
    frame, _, assignments, _ = state
    budget = budgets(frame)
    for fold, (end, target) in FOLDS.items():
        for setting, scheme, level, _, _, _ in SETTINGS:
            for seed in SEEDS:
                indices = sample_rows(frame, end, scheme, budget[level], seed)
                expected = frame.loc[indices]
                actual = assignments[(assignments.fold == fold) & (assignments.setting == setting) & (assignments.seed == seed)]
                assert actual.row_id.tolist() == expected.row_id.tolist()
                assert len(actual) == actual.row_id.nunique()
                assert actual.groupby('gas_id').size().to_dict() == budget[level]
                assert actual.batch.max() < target


def test_allocation_capacity_and_absent_cells(state):
    _, _, _, _ = state
    assert allocate({1: 74, 2: 5}, 39, 'spread') == {1: 34, 2: 5}
    cells = read('sample_composition')
    assert (cells.n <= cells.available).all()
    assert cells[cells.available == 0].n.eq(0).all()
    assert cells[~cells.eligible].n.eq(0).all()
    a_tol = cells[(cells.fold == 'A') & (cells.gas_id == 6) & (cells.batch == 3)]
    assert a_tol.available.eq(0).all()


def test_spread_budgets_are_nested_and_controls_share_rows(state):
    _, _, samples, _ = state
    for fold in FOLDS:
        for seed in SEEDS:
            sub = samples[(samples.fold == fold) & (samples.seed == seed)]
            rows = {setting: set(sub[sub.setting == setting].row_id) for setting, *_ in SETTINGS}
            assert rows['spread_small'] <= rows['spread_mid'] <= rows['spread_max']
            assert rows['spread_mid'] == rows['spread_mid_unit'] == rows['spread_mid_anchor'] == rows['spread_mid_anchor_unit']


def test_native_and_anchor_preprocessing_are_train_only(state):
    frame, _, samples, records = state
    indexed = frame.set_index('row_id')
    anchor = frame[frame.batch <= 2]
    anchor_audit = read_json('anchor_preprocessing.json')
    assert set(anchor_audit['rows']) == set(anchor.row_id)
    for row in records.itertuples():
        selected = samples[(samples.fold == row.fold) & (samples.setting == row.setting) & (samples.seed == row.seed)]
        reference = anchor if row.preprocessing == 'anchor' else indexed.loc[selected.row_id]
        model = joblib.load(ROOT / row.path)
        scaler = model.named_steps['scaler']
        assert scaler.n_samples_seen_ == len(reference) == row.preprocessing_n
        np.testing.assert_allclose(scaler.mean_, reference[FEATURES].mean(), atol=1e-10)
        np.testing.assert_allclose(scaler.var_, reference[FEATURES].var(ddof=0), rtol=1e-9)
        np.testing.assert_allclose(model.named_steps['imputer'].statistics_, reference[FEATURES].median())
        assert reference.batch.max() < row.validation_batch


def test_weights_depend_only_on_selected_training_labels():
    weights = read('class_weights')
    np.testing.assert_allclose(weights.class_weight, weights.expected_weight)
    for (_, _, _), sub in weights.groupby(['fold', 'setting', 'seed']):
        expected = np.ones(6) if 'unit' in sub.setting.iloc[0] else sub.n.sum() / (6 * sub.n)
        np.testing.assert_allclose(sub.class_weight, expected)
    subset = weights[weights.setting.isin(['early_mid', 'spread_mid', 'recent_mid'])]
    assert subset.groupby('gas_id').class_weight.nunique().eq(1).all()


def test_saved_models_parameters_and_predictions_reproduce(state):
    frame, _, _, records = state
    predictions = read('historical_predictions')
    indexed = frame.set_index('row_id')
    assert len(records) == 120 and len(list(MODEL_DIR.glob('*.joblib'))) == 120
    for row in records.itertuples():
        model = joblib.load(ROOT / row.path)
        assert sha(ROOT / row.path) == row.sha256
        classifier = model.named_steps['classifier']
        assert classifier.C == 1 and classifier.gamma == 'scale' and classifier.kernel == 'rbf'
        assert classifier.random_state == row.seed
        assert list(model.feature_names_in_) == FEATURES
        np.testing.assert_array_equal(model.classes_, list(GASES))
        sub = predictions[(predictions.fold == row.fold) & (predictions.setting == row.setting) &
                          (predictions.seed == row.seed)].iloc[:20]
        np.testing.assert_array_equal(model.predict(indexed.loc[sub.row_id, FEATURES]), sub.y_pred)


def test_historical_metrics_and_class_scores_against_predictions():
    predictions = read('historical_predictions')
    metrics = read('historical_metrics').set_index(['fold', 'setting', 'seed'])
    classes = read('historical_class_metrics')
    for key, sub in predictions.groupby(['fold', 'setting', 'seed']):
        row = metrics.loc[key]
        assert accuracy_score(sub.y_true, sub.y_pred) == pytest.approx(row.accuracy)
        assert f1_score(sub.y_true, sub.y_pred, labels=list(GASES), average='macro') == pytest.approx(row.macro_f1)
        p, r, f, n = precision_recall_fscore_support(sub.y_true, sub.y_pred, labels=list(GASES), zero_division=0)
        actual = classes[(classes.fold == key[0]) & (classes.setting == key[1]) & (classes.seed == key[2])].sort_values('gas_id')
        for field, expected in [('precision', p), ('recall', r), ('f1', f), ('support', n)]:
            np.testing.assert_allclose(actual[field], expected)


def test_seed_fold_averages_and_paired_effects():
    metrics = read('historical_metrics')
    seed = read('seed_summary').set_index(['setting', 'seed'])
    expected = metrics.groupby(['setting', 'seed']).macro_f1.mean()
    np.testing.assert_allclose(seed.loc[expected.index].equal_fold_macro_f1, expected)
    paired = read('paired_effects')
    indexed = metrics.set_index(['setting', 'fold', 'seed'])
    for row in paired.itertuples():
        expected = indexed.loc[(row.treatment, row.fold, row.seed), 'macro_f1'] - indexed.loc[(row.base, row.fold, row.seed), 'macro_f1']
        assert row.macro_delta == pytest.approx(expected)
    assert read('effect_summary').statistical_significance_established.eq(False).all()


def test_future_gate_predefined_settings_and_class_metrics():
    gate = read_json('exploratory_gate.json')
    frozen = read_json('historical_findings_frozen.json')
    assert gate['findings_frozen_before_evaluation']
    assert gate['findings_sha256'] == sha(OUT / 'historical_findings_frozen.json')
    assert frozen['historical_metrics_sha256'] == sha(OUT / 'historical_metrics.csv')
    predictions = pd.read_csv(OUT / 'exploratory_predictions.csv', dtype={'scope': str})
    assert set(predictions.setting) == set(FUTURE_SETTINGS)
    assert set(predictions.seed) == set(SEEDS)
    assert set(predictions.fold) == {'C'}
    assert set(predictions.batch) == {9, 10}
    metrics = pd.read_csv(OUT / 'exploratory_metrics.csv', dtype={'scope': str}).set_index(['setting', 'seed', 'scope'])
    for key, sub in predictions.groupby(['setting', 'seed', 'scope']):
        assert len(sub) == metrics.loc[key, 'n']
        assert f1_score(sub.y_true, sub.y_pred, average='macro', labels=list(GASES)) == pytest.approx(metrics.loc[key, 'macro_f1'])


def test_existing_model_reference_predictions_unchanged(state):
    frame, _, _, _ = state
    config = json.loads((ROOT / 'outputs/temporal_generalization_validation/experiment_config.json').read_text(encoding='utf-8'))
    past = pd.read_csv(ROOT / 'outputs/temporal_generalization_validation/predictions_comparison.csv').set_index('row_id')
    sub = frame[frame.batch >= 8]
    for name, meta in config['models'].items():
        assert sha(ROOT / meta['path']) == meta['sha256']
        model = joblib.load(ROOT / meta['path'])
        np.testing.assert_array_equal(model.predict(sub[FEATURES]), past.loc[sub.row_id, 'pred_' + name])


def test_prior_files_and_raw_hashes_preserved():
    manifest = read_json('run_manifest.json')
    for name, expected in manifest['before'].items():
        assert sha(ROOT / name) == expected
    for name, expected in manifest['raw_hashes'].items():
        assert sha(Path(read_config()['data_dir']) / name) == expected
    assert len([n for n in manifest['before'] if n.endswith('.joblib')]) == 140
    assert sha(OUT / 'experiment_plan.json') == manifest['plan_sha256']
    assert manifest['classifier_fits'] == 120 and not manifest['model_selection_changed']


def test_graph_values_fonts_and_numeric_batch_order():
    checks = read('graph_value_checks')
    np.testing.assert_allclose(checks.displayed_value, checks.expected_value, equal_nan=True)
    assert checks.figure.nunique() == 9
    metadata = read('graph_metadata')
    assert len(metadata) == 9 and metadata.missing_used_glyphs.eq(0).all()
    assert metadata.titles_axes_legends_present.all()
    for row in metadata.itertuples():
        assert sha(ROOT / row.path) == row.sha256 and sha(row.font_file) == row.font_sha256
    summary = read('historical_summary').set_index('setting')
    for row in checks[checks.source == 'historical_summary'].itertuples():
        assert row.displayed_value == pytest.approx(summary.loc[row.key, 'mean_macro_f1'] * 100)
    sub = checks[checks.figure == 'batch_macro_f1']
    for setting in ['early_mid', 'spread_mid', 'recent_mid']:
        assert [int(key.split('|')[1]) for key in sub[sub.key.str.startswith(setting + '|')].key] == [6, 7, 8]


def test_report_scope_and_all_seed_budget_records():
    text = (ROOT / 'reports' / REPORTS[0]).read_text(encoding='utf-8')
    assert text.count('<h2>') == 10 and text.count('data:image/png;base64,') == 9
    assert '새 독립 Test 없음' in text and 'Model A 유지' in text
    assert '통계적 우월성 미확인' in text
    records = read('fit_records')
    assert records.groupby(['fold', 'setting']).seed.nunique().eq(5).all()
    assert len(records[['fold', 'setting', 'seed']].drop_duplicates()) == 120
