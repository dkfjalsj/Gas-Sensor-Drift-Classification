# Toluene 심층 진단의 점수·거리·투영·보존 검사

import ast
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest
from scipy.spatial.distance import cdist

from src.data import ROOT, FEATURES, GASES, KINDS, load_dataset, read_config
from src.temporal_expansion import sha
from src.toluene_deep_diagnostic import OUT, PAIRS, REPORTS, reconstruct_scores


# 실제 원본과 고정 모델 한 번 불러오기
@pytest.fixture(scope='module')
def state():
    frame, _ = load_dataset(read_config())
    config = json.loads((OUT / 'experiment_config.json').read_text(encoding='utf-8'))
    models = {name: joblib.load(ROOT / meta['path']) for name, meta in config['models'].items()}
    return frame, config, models


# 출력 CSV 불러오기
def read(name):
    return pd.read_csv(OUT / f'{name}.csv')


def test_model_hashes_and_original_preprocessing(state):
    frame, config, models = state
    for name, model in models.items():
        meta = config['models'][name]
        assert sha(ROOT / meta['path']) == meta['sha256']
        train = frame[frame.batch <= meta['train_end']]
        scaler = model.named_steps['scaler']
        assert scaler.n_samples_seen_ == len(train)
        np.testing.assert_allclose(scaler.mean_, train[FEATURES].mean(), atol=1e-10)
        assert model.named_steps['classifier'].C == 1
        np.testing.assert_array_equal(model.classes_, list(GASES))
        assert list(model.feature_names_in_) == FEATURES


def test_prediction_replay_and_batch9_support(state):
    frame, _, models = state
    scores = read('decision_scores')
    past = pd.read_csv(ROOT / 'outputs/temporal_generalization_validation/predictions_comparison.csv').set_index('row_id')
    for name, model in models.items():
        sub = scores[scores.model == name]
        raw = frame.set_index('row_id').loc[sub.row_id]
        np.testing.assert_array_equal(model.predict(raw[FEATURES]), sub.prediction)
        np.testing.assert_array_equal(past.loc[sub.row_id, 'pred_' + name], sub.prediction)
    nine = scores[(scores.batch == 9) & (scores.gas_id == 6)]
    assert nine.groupby('model').size().to_dict() == {'A': 101, 'B': 101}
    assert nine[nine.model == 'B'].prediction.value_counts().to_dict() == {4: 96, 1: 4, 6: 1}


def test_ovo_ovr_reconstruction_and_native_votes(state):
    frame, _, models = state
    query = frame[(frame.batch == 9) & (frame.gas == 6)]
    for model in models.values():
        classifier = model.named_steps['classifier']
        ovo = classifier._decision_function(model[:-1].transform(query[FEATURES]))
        rebuilt, _, native = reconstruct_scores(ovo)
        np.testing.assert_allclose(rebuilt, model.decision_function(query[FEATURES]), atol=1e-12)
        np.testing.assert_array_equal(classifier.classes_[native.argmax(axis=1)], model.predict(query[FEATURES]))
    scores = read('ovo_scores')
    assert set(scores.pair_index) == set(range(15))
    assert all((PAIRS[int(r.pair_index)][0] + 1, PAIRS[int(r.pair_index)][1] + 1) ==
               (r.class_i, r.class_j) for r in scores.iloc[:30].itertuples())


def test_rkhs_geometry_and_empirical_boundary_summary():
    geometry = read('pair_geometry')
    assert geometry.reconstruction_max_error.dropna().max() < 1e-9
    assert (geometry.rkhs_weight_norm > 0).all()
    pair = read('ovo_scores')
    summary = read('decision_summary')
    for row in summary.itertuples():
        sub = pair[(pair.model == row.model) & (pair.batch == row.batch) &
                   (pair.gas_id == row.gas_id) & (pair.class_i == 4) & (pair.class_j == 6)]
        assert len(sub) == row.n
        assert sub.margin.median() == pytest.approx(row.margin_Ac_T_median)
        assert int((sub.margin > 0).sum()) == row.pair_Ac_favored_n
        assert int((sub.rkhs_distance.abs() <= sub.train_abs_distance_q25).sum()) == row.within_train_abs_q25_n


def test_exact_neighbors_and_training_only_candidates(state):
    frame, _, models = state
    neighbors = read('nearest_neighbors')
    for space, model, end in [('A_native', models['A'], 6), ('B_native', models['B'], 7),
                              ('A_space_train7', models['A'], 7)]:
        sub = neighbors[(neighbors.space == space) & (neighbors.batch == 9) & (neighbors.gas_id == 6)].iloc[[0, 50, 100]]
        train = frame[frame.batch <= end]
        query = frame.set_index('row_id').loc[sub.row_id]
        distance = cdist(model[:-1].transform(query[FEATURES]), model[:-1].transform(train[FEATURES]))
        indices = distance.argmin(axis=1)
        np.testing.assert_allclose(distance.min(axis=1), sub.nearest_distance)
        np.testing.assert_array_equal(train.row_id.iloc[indices], sub.nearest_row_id)
        assert sub.nearest_batch.max() <= end
    top = read('top5_neighbors')
    assert top.groupby(['space', 'row_id']).size().eq(5).all()
    for space, end in [('A_native', 6), ('B_native', 7), ('A_space_train7', 7)]:
        assert top[top.space == space].neighbor_batch.max() <= end
    replay = read('stage7_distance_replay')
    np.testing.assert_allclose(replay.nearest_distance, replay.nearest_train_distance, atol=1e-8)


def test_sensor_mapping_and_objective_selection():
    mapping = read('sensor_feature_mapping')
    assert mapping.feature.tolist() == FEATURES
    assert mapping.sensor.tolist() == np.repeat(np.arange(1, 17), 8).tolist()
    assert mapping.kind.tolist() == KINDS * 16
    selected = read('sensor_plot_selection')
    assert selected.plot_selected.sum() == 2
    assert selected.mean_normalized_wasserstein.is_monotonic_decreasing
    shifts = read('feature_distribution_shift')
    for row in selected.itertuples():
        sub = shifts[(shifts.reference == 'B') & (shifts.batch == 9) &
                     (shifts.gas_id == 6) & (shifts.sensor == row.sensor)]
        assert len(sub) == 8
        assert sub.normalized_wasserstein.mean() == pytest.approx(row.mean_normalized_wasserstein)


def test_sensor_statistics_correlations_and_class_weights(state):
    frame, _, models = state
    raw = frame[(frame.batch == 9) & (frame.gas == 6)]
    z = models['A'][:-1].transform(raw[FEATURES])
    stats = read('feature_statistics')
    sub = stats[(stats.partition == 'Batch9') & (stats.gas_id == 6)].set_index('feature').loc[FEATURES]
    np.testing.assert_allclose(sub.mean_z, z.mean(axis=0))
    np.testing.assert_allclose(sub.sd_z, z.std(axis=0))
    corr = read('sensor_correlations')
    matrix = corr[(corr.partition == 'Batch9') & (corr.gas_id == 6) & (corr.sensor == 1)].pivot(
        index='feature_i', columns='feature_j', values='correlation').to_numpy()
    np.testing.assert_allclose(matrix, np.corrcoef(z[:, :8], rowvar=False))
    weights = read('class_weights')
    np.testing.assert_allclose(weights.class_weight, weights.expected_weight)


def test_pca_fits_only_train_and_coordinates_reproduce(state):
    frame, _, models = state
    audits = json.loads((OUT / 'pca_fit_audit.json').read_text(encoding='utf-8'))
    coordinates = read('pca_coordinates')
    components = read('pca_components')
    for audit in audits:
        name, end = audit['model'], audit['train_end']
        train = frame[frame.batch <= end]
        assert set(audit['fit_row_ids']) == set(train.row_id)
        assert max(audit['fit_batches']) == end
        query = frame[(frame.batch == 9) & (frame.gas == 6)].iloc[:3]
        matrix = components[components.model == name].pivot(index='component', columns='feature', values='loading').reindex(columns=FEATURES).to_numpy()
        center = models[name][:-1].transform(train[FEATURES]).mean(axis=0)
        expected = (models[name][:-1].transform(query[FEATURES]) - center) @ matrix.T
        actual = coordinates[coordinates.model == name].set_index('row_id').loc[query.row_id, ['pc1', 'pc2']]
        np.testing.assert_allclose(actual, expected, atol=1e-10)


def test_subgroups_pairwise_and_prediction_changes():
    groups = read('batch9_subgroups')
    assert len(groups) == 101 and groups.row_id.is_unique
    assert groups.prediction_A.eq(1).all()
    assert read('batch9_pairwise_distances').shape[0] == 5050
    for k in [2, 3, 4]:
        assert groups[f'ward_k{k}'].nunique() == k
    changes = read('prediction_changes').set_index('prediction_B')
    assert changes.n.to_dict() == {1: 4, 4: 96, 6: 1}
    assert read('prediction_group_features').groupby('prediction_B').size().eq(128).all()


def test_graph_values_fonts_and_numeric_batch_order():
    checks = read('graph_value_checks')
    np.testing.assert_allclose(checks.displayed_value, checks.expected_value, equal_nan=True)
    metadata = read('graph_metadata')
    assert len(metadata) == 10 and metadata.titles_axes_legends_present.all()
    assert metadata.missing_used_glyphs.eq(0).all()
    for row in metadata.itertuples():
        assert sha(ROOT / row.path) == row.sha256
        assert sha(row.font_file) == row.font_sha256
    counts = read('prediction_distribution')
    for row in checks[checks.figure == 'toluene_prediction_distribution'].itertuples():
        model, batch, gas, predicted = row.key.split('|')
        sub = counts[(counts.model == model) & (counts.batch == int(batch)) &
                     (counts.gas_id == int(gas)) & (counts.prediction == int(predicted))]
        assert row.displayed_value == pytest.approx(sub.n.sum())
    sub = checks[(checks.figure == 'toluene_prediction_distribution') & checks.key.str.startswith('A|')]
    assert list(dict.fromkeys(int(key.split('|')[1]) for key in sub.key)) == [8, 9, 10]


def test_preserved_files_raw_models_and_config():
    manifest = json.loads((OUT / 'run_manifest.json').read_text(encoding='utf-8'))
    for name, expected in manifest['before'].items():
        assert sha(ROOT / name) == expected
    for name, expected in manifest['raw_hashes'].items():
        assert sha(Path(read_config()['data_dir']) / name) == expected
    old_models = {name for name in manifest['before'] if name.endswith('.joblib')}
    actual_models = {str(p.relative_to(ROOT)) for p in (ROOT / 'models').rglob('*.joblib')}
    assert old_models == actual_models and len(actual_models) == 140
    assert sha(OUT / 'experiment_config.json') == manifest['experiment_sha256']


def test_no_classifier_fit_and_report_hypothesis_scope():
    for name in ['toluene_deep_diagnostic.py', 'toluene_deep_visuals.py', 'toluene_deep_report.py']:
        tree = ast.parse((ROOT / 'src' / name).read_text(encoding='utf-8'))
        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and
                 isinstance(node.func, ast.Attribute) and node.func.attr in ['fit', 'fit_transform', 'partial_fit']]
        assert all(isinstance(node.func.value, ast.Name) and node.func.value.id == 'pca' and
                   node.func.attr == 'fit' for node in calls)
    manifest = json.loads((OUT / 'run_manifest.json').read_text(encoding='utf-8'))
    assert manifest['classifier_fits'] == manifest['preprocessing_fits'] == 0
    assert manifest['diagnostic_pca_fits'] == 2
    report = (ROOT / 'reports' / REPORTS[0]).read_text(encoding='utf-8')
    assert report.count('<h2>') == 11 and report.count('data:image/png;base64,') == 10
    assert '새 독립 Test 없음' in report and '주 후보 A 유지' in report
    assert set(read('hypothesis_evidence').assessment) <= {'관찰 결과와 부합', '일부 부합', '현재 근거 부족', '관찰 결과와 충돌'}
