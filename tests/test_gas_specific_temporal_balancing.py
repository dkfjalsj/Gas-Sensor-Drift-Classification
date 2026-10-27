# 가스별 시기 균형 실험의 표본·재사용·보호·누수·보존 검사

from datetime import datetime
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support

from src.data import ROOT, FEATURES, GASES, load_dataset, read_config
from src.temporal_expansion import sha
from src.gas_specific_temporal_balancing import (
    OUT, MODEL_DIR, OLD, FOLDS, SEEDS, MID_SETTINGS, MAX_CANDIDATES, REPORTS,
    sample_rows, coverage_allocate, signature,
)


# 실제 자료와 실행 기록 공유
@pytest.fixture(scope='module')
def state():
    frame, _ = load_dataset(read_config())
    return frame, read_json('experiment_plan.json'), read('model_registry')


# 검사 대상 CSV와JSON 불러오기
def read(name):
    return pd.read_csv(OUT / f'{name}.csv')


def read_json(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))


def test_plan_budget_and_all_seeds_frozen(state):
    _, plan, _ = state
    assert plan['seeds'] == SEEDS
    assert plan['mid_settings'] == MID_SETTINGS and plan['max_candidates'] == MAX_CANDIDATES
    assert list(plan['budgets']['mid'].values()) == [127, 216, 91, 69, 301, 39]
    assert sum(plan['budgets']['mid'].values()) == 843
    assert sum(plan['budgets']['max'].values()) == 1689
    assert sha(OUT / 'planned_sample_assignments.csv') == plan['samples_sha256']
    assert not plan['independent_test']


def test_sampling_reproducibility_and_exact_gas_budgets(state):
    frame, plan, _ = state
    planned = read('planned_sample_assignments')
    for (fold, setting, seed), sub in planned.groupby(['fold', 'setting', 'seed']):
        scheme, level = setting.rsplit('_', 1)
        budget = {int(g): n for g, n in plan['budgets'][level].items()}
        ids, _ = sample_rows(frame, FOLDS[fold][0], scheme, budget, int(seed))
        assert sub.row_id.tolist() == frame.loc[ids].row_id.tolist()
        assert sub.row_id.is_unique and sub.groupby('gas_id').size().to_dict() == budget


def test_mixed_rule_uses_only_past_training_counts(state):
    frame, plan, _ = state
    rules = read('train_only_strategy_rules')
    for fold, (end, _) in FOLDS.items():
        for gas in GASES:
            counts = frame[(frame.batch <= end) & (frame.gas == gas)].groupby('batch').size()
            expected_share = counts.max() / counts.sum()
            sub = rules[(rules.fold == fold) & (rules.setting == 'mixed_mid') & (rules.gas_id == gas)]
            assert sub.chosen.eq('spread' if expected_share >= .5 else 'recent').all()
            np.testing.assert_allclose(sub.largest_batch_share, expected_share)
        budget = {int(g): n for g, n in plan['budgets']['mid'].items()}
        full, _ = sample_rows(frame, end, 'mixed', budget, 42)
        past, _ = sample_rows(frame[frame.batch <= end], end, 'mixed', budget, 42)
        np.testing.assert_array_equal(full, past)


def test_minimum_representation_and_capacity_constraints(state):
    _, _, _ = state
    cells = read('planned_sample_composition')
    assert (cells.n <= cells.available).all()
    assert cells[cells.available == 0].n.eq(0).all()
    cover = cells[cells.setting.str.startswith('coverage')]
    assert (cover[cover.available > 0].n >= 1).all()
    assert coverage_allocate({1: 74, 2: 5}, 39) == {1: 34, 2: 5}
    assert cells[(cells.gas_id == 6) & cells.batch.isin([3, 4, 5])].available.eq(0).all()


def test_identical_fold_is_neutral_and_not_refitted():
    aliases = read('identical_subset_checks')
    assert aliases[(aliases.fold == 'A') & (aliases.setting == 'mixed_mid')].same_as_spread.all()
    registry = read('model_registry')
    sub = registry[(registry.fold == 'A') & (registry.setting == 'mixed_mid')]
    assert not sub.new_fit.any() and sub.source_stage.eq(12).all()
    delta = read('mid_paired_deltas')
    assert delta[(delta.fold == 'A') & (delta.setting == 'mixed_mid')].macro_delta.eq(0).all()


def test_model_reuse_is_exact_and_new_files_are_separate(state):
    _, plan, registry = state
    samples = read('planned_sample_assignments')
    count = int(registry.new_fit.sum())
    assert count <= plan['maximum_new_fits']
    assert len(list(MODEL_DIR.glob('*.joblib'))) == count
    for row in registry.itertuples():
        sub = samples[(samples.fold == row.fold) & (samples.setting == row.setting) & (samples.seed == row.seed)]
        assert signature(sub.row_id.tolist(), row.seed) == row.signature
        assert sha(ROOT / row.path) == row.sha256
        if row.new_fit:
            assert row.source_stage == 13 and (ROOT / row.path).parent == MODEL_DIR
            assert datetime.fromisoformat(row.fit_started_at) >= datetime.fromisoformat(plan['frozen_at'])
        else:
            assert row.fit_seconds == 0


def test_preprocessing_and_class_weight_train_only(state):
    frame, _, registry = state
    samples = read('executed_sample_assignments')
    indexed = frame.set_index('row_id')
    for row in registry.itertuples():
        ids = samples[(samples.fold == row.fold) & (samples.setting == row.setting) & (samples.seed == row.seed)].row_id
        train = indexed.loc[ids]
        model = joblib.load(ROOT / row.path)
        assert model.named_steps['scaler'].n_samples_seen_ == len(train) == row.train_n
        np.testing.assert_allclose(model.named_steps['scaler'].mean_, train[FEATURES].mean(), atol=1e-10)
        np.testing.assert_allclose(model.named_steps['scaler'].var_, train[FEATURES].var(ddof=0), rtol=1e-9)
        np.testing.assert_allclose(model.named_steps['imputer'].statistics_, train[FEATURES].median())
        classifier = model.named_steps['classifier']
        assert classifier.C == 1 and classifier.gamma == 'scale' and classifier.class_weight == 'balanced'
        np.testing.assert_allclose(classifier.class_weight_, len(train) / (6 * train.gas.value_counts().sort_index()))
        assert train.batch.max() < int(row.scope)
        validation = frame[frame.batch == int(row.scope)]
        assert set(train.index).isdisjoint(validation.row_id)


def test_saved_prediction_reproducibility(state):
    frame, _, registry = state
    predictions = read('historical_predictions')
    indexed = frame.set_index('row_id')
    for row in registry.itertuples():
        sub = predictions[(predictions.fold == row.fold) & (predictions.setting == row.setting) & (predictions.seed == row.seed)].iloc[:20]
        model = joblib.load(ROOT / row.path)
        np.testing.assert_array_equal(model.predict(indexed.loc[sub.row_id, FEATURES]), sub.y_pred)


def test_historical_metrics_against_predictions():
    predictions = read('historical_predictions')
    metrics = read('historical_metrics').set_index(['fold', 'setting', 'seed'])
    classes = read('historical_class_metrics')
    for key, sub in predictions.groupby(['fold', 'setting', 'seed']):
        row = metrics.loc[key]
        assert f1_score(sub.y_true, sub.y_pred, labels=list(GASES), average='macro') == pytest.approx(row.macro_f1)
        assert accuracy_score(sub.y_true, sub.y_pred) == pytest.approx(row.accuracy)
        p, r, f, n = precision_recall_fscore_support(sub.y_true, sub.y_pred, labels=list(GASES), zero_division=0)
        actual = classes[(classes.fold == key[0]) & (classes.setting == key[1]) & (classes.seed == key[2])].sort_values('gas_id')
        for field, expected in [('precision', p), ('recall', r), ('f1', f), ('support', n)]:
            np.testing.assert_allclose(actual[field], expected)


def test_guards_and_expansion_follow_preregistered_rules():
    guards = read('mid_guards')
    for row in guards.itertuples():
        assert row.balanced_success == (row.macro_guard and row.focus_guard and row.other_guard and row.fold_guard and row.seed_guard)
        expected = row.macro_guard and row.focus_guard and row.other_guard and row.positive_fold_n >= 2 and row.positive_seed_n >= 4
        assert row.expansion_eligible == expected
    gate = read_json('expansion_decision.json')
    registry = read('model_registry')
    for decision in gate['decisions']:
        eligible = bool(guards[guards.setting == decision['mid_parent']].expansion_eligible.iloc[0])
        assert decision['execute'] == eligible
        assert (decision['setting'] in set(registry.setting)) == eligible
    assert read('max_matched_guards').baseline.eq('spread_max').all()
    missing = read('size_comparisons')
    assert missing[~missing.executed].macro_delta.isna().all()


def test_historical_conclusion_frozen_before_future():
    research = read_json('research_conclusion_frozen.json')
    findings = read_json('historical_findings_frozen.json')
    gate = read_json('exploratory_gate.json')
    assert gate['historical_frozen_before_evaluation']
    assert findings['research_conclusion_sha256'] == sha(OUT / 'research_conclusion_frozen.json')
    assert research['mid_guards_sha256'] == sha(OUT / 'mid_guards.csv')
    assert research['max_guards_sha256'] == sha(OUT / 'max_matched_guards.csv')
    assert datetime.fromisoformat(research['frozen_at']) <= datetime.fromisoformat(gate['started_at'])
    assert not research['official_model_changed'] and not research['independent_generalization_proven']


def test_predefined_future_models_and_confusion_consistency():
    prediction = pd.read_csv(OUT / 'exploratory_predictions.csv', dtype={'scope': str})
    cm = pd.read_csv(OUT / 'exploratory_confusion.csv', dtype={'scope': str})
    assert set(prediction.setting) == set(MID_SETTINGS) and set(prediction.seed) == set(SEEDS)
    assert set(prediction.fold) == {'C'} and set(prediction.batch) == {9, 10}
    for key, sub in prediction.groupby(['setting', 'seed', 'scope']):
        actual = cm[(cm.setting == key[0]) & (cm.seed == key[1]) & (cm.scope == key[2])]
        assert actual['count'].sum() == len(sub)
        assert actual.groupby('actual_id')['count'].sum().to_dict() == sub.y_true.value_counts().sort_index().to_dict()


def test_stage12_and_model_a_b_predictions_unchanged():
    replay = read('replay_checks')
    assert len(replay) == 47 and replay.exact_match.all()
    old = pd.read_csv(OLD / 'historical_metrics.csv')
    current = read('historical_metrics')
    for setting in ['spread_mid', 'recent_mid', 'spread_max']:
        a = old[old.setting == setting].set_index(['fold', 'seed']).macro_f1
        b = current[current.setting == setting].set_index(['fold', 'seed']).macro_f1
        np.testing.assert_allclose(a.sort_index(), b.sort_index(), atol=1e-12)


def test_existing_files_models_raw_and_plan_preserved():
    manifest = read_json('run_manifest.json')
    for name, expected in manifest['before'].items():
        assert sha(ROOT / name) == expected
    for name, expected in manifest['raw_hashes'].items():
        assert sha(Path(read_config()['data_dir']) / name) == expected
    assert len([n for n in manifest['before'] if n.endswith('.joblib')]) == 260
    assert sha(OUT / 'experiment_plan.json') == manifest['plan_sha256']
    assert not manifest['official_model_changed']


def test_graph_values_fonts_csv_and_numeric_batch_order():
    checks = read('graph_value_checks')
    np.testing.assert_allclose(checks.displayed_value, checks.expected_value, equal_nan=True)
    metadata = read('graph_metadata')
    assert len(metadata) == 10 and checks.figure.nunique() == 10
    assert metadata.missing_used_glyphs.eq(0).all() and metadata.titles_axes_legends_present.all()
    for row in metadata.itertuples():
        assert sha(ROOT / row.path) == row.sha256 and sha(row.font_file) == row.font_sha256
    classes = read('historical_class_metrics')
    for row in checks[checks.source == 'historical_class_metrics'].itertuples():
        setting, gas = row.key.split('|')
        expected = classes[(classes.setting == setting) & (classes.gas_id == int(gas))].recall.mean() * 100
        assert row.displayed_value == pytest.approx(expected)
    sub = checks[checks.figure == 'fold_macro_f1']
    for setting in MID_SETTINGS:
        assert [int(k.split('|')[1]) for k in sub[sub.key.str.startswith(setting + '|')].key] == [6, 7, 8]


def test_reports_conclusion_and_missing_expansion_not_zero():
    document = (ROOT / 'reports' / REPORTS[0]).read_text(encoding='utf-8')
    assert document.count('<h2>') == 10 and document.count('data:image/png;base64,') == 10
    assert '새 독립 Test 없음' in document and '공식 Model A 유지' in document
    conclusion = read_json('research_conclusion_frozen.json')['conclusion']
    assert conclusion in document and conclusion[0] in ['A', 'B', 'C']
    registry = read('model_registry')
    assert registry.groupby(['fold', 'setting']).seed.nunique().eq(5).all()
