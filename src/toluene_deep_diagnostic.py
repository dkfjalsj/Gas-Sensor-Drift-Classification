# 저장된 두 SVM의 Toluene 실패 점수·거리·센서 구조 진단
# 분류기 변경 없이 Train 전용 PCA와 사후 군집 분석 수행

import itertools

import joblib
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import cdist, pdist, squareform
from scipy.stats import wasserstein_distance
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

from .data import ROOT, FEATURES, GASES, KINDS
from .temporal_expansion import sha, write_json

OUT = ROOT / 'outputs/toluene_failure_deep_diagnostic'
PAIRS = list(itertools.combinations(range(6), 2))
SOURCES = {
    'uci': 'https://archive.ics.uci.edu/dataset/224/gas+sensor+array+drift+dataset',
    'svm': 'https://scikit-learn.org/stable/modules/svm.html#multi-class-classification',
}


# 분석 표를 UTF-8 CSV로 저장
def save(name, rows):
    table = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    table.to_csv(OUT / f'{name}.csv', index=False, encoding='utf-8')
    return table


# 기존 파일의 해시 목록 수집


# 분석 전 모델·방법·사후 선택 기준 고정


# OvO 점수에서 OvR 점수와 투표 재구성
def reconstruct_scores(ovo):
    votes = np.zeros((len(ovo), 6), dtype=int)
    native_votes = np.zeros_like(votes)
    sums = np.zeros_like(votes, dtype=float)
    for k, (i, j) in enumerate(PAIRS):
        votes[:, i] += ovo[:, k] >= 0
        votes[:, j] += ovo[:, k] < 0
        native_votes[:, i] += ovo[:, k] > 0
        native_votes[:, j] += ovo[:, k] <= 0
        sums[:, i] += ovo[:, k]
        sums[:, j] -= ovo[:, k]
    ovr = votes + sums / (3 * (np.abs(sums) + 1))
    return ovr, votes, native_votes


# 관심 이진 경계의 RBF 가중치 길이 및 점수 재검산
def pair_geometry(classifier, z):
    starts = np.r_[0, np.cumsum(classifier.n_support_)]
    rows, parameters = [], {}
    for i, j in [(0, 5), (3, 5), (0, 3)]:
        k = PAIRS.index((i, j))
        ids = np.r_[np.arange(starts[i], starts[i + 1]),
                    np.arange(starts[j], starts[j + 1])]
        alpha = np.r_[classifier.dual_coef_[j - 1, starts[i]:starts[i + 1]],
                      classifier.dual_coef_[i, starts[j]:starts[j + 1]]]
        sv = classifier.support_vectors_[ids]
        kernel = np.exp(-classifier._gamma * cdist(sv, sv, metric='sqeuclidean'))
        norm = float(np.sqrt(max(0, alpha @ kernel @ alpha)))
        assert norm > 0
        reconstructed = (np.exp(-classifier._gamma * cdist(z[:64], sv, metric='sqeuclidean'))
                         @ alpha + classifier.intercept_[k])
        expected = classifier._decision_function(z[:64])[:, k]
        np.testing.assert_allclose(reconstructed, expected, atol=1e-9)
        parameters[k] = norm
        rows.append(dict(pair_index=k, class_i=i + 1, class_j=j + 1,
                         support_vectors=len(ids), rkhs_weight_norm=norm,
                         reconstruction_max_error=float(np.max(np.abs(reconstructed - expected)))))
    return rows, parameters


# 저장된 점수·예측과 Train 전처리 통계 확인
def score_models(frame, config):
    import copy

    focus = frame[(frame.batch >= 8) & frame.gas.isin([4, 6])].copy()
    old = pd.read_csv(ROOT / 'outputs/temporal_generalization_validation/predictions_comparison.csv')
    models, decisions, pairs, summaries, audits, geometry = {}, [], [], [], [], []
    weights, train_perf = [], []
    for name, meta in config['models'].items():
        print('Frozen model scores', name, flush=True)
        model = joblib.load(ROOT / meta['path'])
        models[name] = model
        train = frame[frame.batch <= meta['train_end']]
        classifier = model.named_steps['classifier']
        scaler = model.named_steps['scaler']
        np.testing.assert_array_equal(model.classes_, list(GASES))
        assert list(model.feature_names_in_) == FEATURES
        assert classifier.C == 1 and classifier.gamma == 'scale'
        assert classifier.class_weight == 'balanced' and classifier.kernel == 'rbf'
        assert not classifier.break_ties and classifier.decision_function_shape == 'ovr'
        np.testing.assert_allclose(scaler.mean_, train[FEATURES].mean(), atol=1e-10)
        np.testing.assert_allclose(scaler.var_, train[FEATURES].var(ddof=0), rtol=1e-9)
        np.testing.assert_allclose(model.named_steps['imputer'].statistics_, train[FEATURES].median())
        z = model[:-1].transform(focus[FEATURES])
        train_z = model[:-1].transform(train[FEATURES])
        ovo = classifier._decision_function(z)
        public_copy = copy.deepcopy(classifier)
        public_copy.decision_function_shape = 'ovo'
        np.testing.assert_allclose(public_copy.decision_function(z), ovo)
        ovr = model.decision_function(focus[FEATURES])
        rebuilt, votes, native_votes = reconstruct_scores(ovo)
        np.testing.assert_allclose(rebuilt, ovr, atol=1e-12)
        pred = model.predict(focus[FEATURES])
        np.testing.assert_array_equal(classifier.classes_[native_votes.argmax(axis=1)], pred)
        expected = old.set_index('row_id').loc[focus.row_id, 'pred_' + name].to_numpy()
        np.testing.assert_array_equal(pred, expected)
        geo, norms = pair_geometry(classifier, z)
        geometry.extend(dict(model=name, **item) for item in geo)
        train_ovo = classifier._decision_function(train_z)
        train_pred = classifier.predict(train_z)
        train_ovr = classifier.decision_function(train_z)
        for gas in GASES:
            mask = train.gas.to_numpy() == gas
            weights.append(dict(model=name, gas_id=gas, n=int(mask.sum()),
                                class_weight=float(classifier.class_weight_[gas - 1]),
                                expected_weight=float(len(train) / (6 * mask.sum())),
                                effective_C=float(classifier.C * classifier.class_weight_[gas - 1])))
            train_perf.append(dict(model=name, gas_id=gas, n=int(mask.sum()),
                                   correct_n=int((train_pred[mask] == gas).sum()),
                                   recall=float((train_pred[mask] == gas).mean()),
                                   role='resubstitution_only_not_generalization'))
        for k, norm in norms.items():
            i, j = PAIRS[k]
            mask = train.gas.isin([i + 1, j + 1]).to_numpy()
            abs_ref = np.abs(train_ovo[mask, k] / norm)
            q25 = float(np.quantile(abs_ref, .25))
            pair_pred = np.where(train_ovo[mask, k] > 0, i + 1, j + 1)
            geometry.append(dict(model=name, pair_index=k, class_i=i + 1, class_j=j + 1,
                                 support_vectors=np.nan, rkhs_weight_norm=norm,
                                 train_pair_n=int(mask.sum()), train_abs_distance_q25=q25,
                                 train_pair_accuracy=float((pair_pred == train.gas.to_numpy()[mask]).mean())))
        train_reference = {k: float(np.quantile(np.abs(train_ovo[
            train.gas.isin([PAIRS[k][0] + 1, PAIRS[k][1] + 1]).to_numpy(), k] / norm), .25))
            for k, norm in norms.items()}
        for row_index, row in enumerate(focus.itertuples()):
            item = dict(model=name, row_id=row.row_id, batch=row.batch, gas_id=row.gas,
                        source_line=row.source_line, prediction=int(pred[row_index]),
                        ovr_toluene_minus_acetaldehyde=float(ovr[row_index, 5] - ovr[row_index, 3]),
                        ovr_argmax=int(classifier.classes_[ovr[row_index].argmax()]),
                        vote_tied=bool((native_votes[row_index] == native_votes[row_index].max()).sum() > 1),
                        correct=bool(pred[row_index] == row.gas))
            for gas in GASES:
                item['ovr_' + str(gas)] = float(ovr[row_index, gas - 1])
                item['votes_' + str(gas)] = int(native_votes[row_index, gas - 1])
            decisions.append(item)
            for k, (i, j) in enumerate(PAIRS):
                raw = float(ovo[row_index, k])
                pairs.append(dict(model=name, row_id=row.row_id, batch=row.batch, gas_id=row.gas,
                                  prediction=int(pred[row_index]), pair_index=k, class_i=i + 1,
                                  class_j=j + 1, margin=raw, favors=i + 1 if raw > 0 else j + 1,
                                  rkhs_distance=raw / norms[k] if k in norms else np.nan,
                                  train_abs_distance_q25=train_reference.get(k, np.nan)))
        train_focus = train[train.gas.isin([4, 6])]
        train_indices = np.flatnonzero(train.gas.isin([4, 6]))
        save('train_scores_' + name, [dict(row_id=row.row_id, batch=row.batch, gas_id=row.gas,
             prediction=int(train_pred[index]), margin_Ac_T=float(train_ovo[index, PAIRS.index((3, 5))]),
             ovr_Ac=float(train_ovr[index, 3]), ovr_T=float(train_ovr[index, 5]))
             for row, index in zip(train_focus.itertuples(), train_indices)])
        audits.append(dict(model=name, train_end=meta['train_end'], train_n=len(train),
                           class_mapping_ok=True, feature_mapping_ok=True,
                           prediction_replay_n=len(focus), prediction_replay_exact=True,
                           decision_ovr_reconstruction_max_error=float(np.max(np.abs(rebuilt - ovr))),
                           native_votes_match=True, preprocessing_train_only=True,
                           gamma_numeric=float(classifier._gamma), model_sha256=sha(ROOT / meta['path'])))
    scores = save('decision_scores', decisions)
    pair_table = save('ovo_scores', pairs)
    save('pair_geometry', geometry)
    save('class_weights', weights)
    save('train_class_recall', train_perf)
    save('model_audit', audits)
    for (model, batch, gas), sub in scores.groupby(['model', 'batch', 'gas_id']):
        pair = pair_table[(pair_table.model == model) & (pair_table.batch == batch) &
                          (pair_table.gas_id == gas) & (pair_table.class_i == 4) & (pair_table.class_j == 6)]
        summaries.append(dict(model=model, batch=batch, gas_id=gas, n=len(sub),
                              correct_n=int(sub.correct.sum()), recall=float(sub.correct.mean()),
                              ovr_T_minus_Ac_median=float(sub.ovr_toluene_minus_acetaldehyde.median()),
                              pair_Ac_favored_n=int((pair.margin > 0).sum()),
                              pair_T_favored_n=int((pair.margin <= 0).sum()),
                              margin_Ac_T_median=float(pair.margin.median()),
                              rkhs_Ac_T_median=float(pair.rkhs_distance.median()),
                              abs_rkhs_Ac_T_median=float(pair.rkhs_distance.abs().median()),
                              within_train_abs_q25_n=int((pair.rkhs_distance.abs() <= pair.train_abs_distance_q25).sum()),
                              vote_ties_n=int(sub.vote_tied.sum()),
                              ovr_argmax_differs_n=int((sub.ovr_argmax != sub.prediction).sum())))
    save('decision_summary', summaries)
    counts = scores.groupby(['model', 'batch', 'gas_id', 'prediction']).size().rename('n').reset_index()
    counts['support'] = counts.groupby(['model', 'batch', 'gas_id']).n.transform('sum')
    counts['fraction'] = counts.n / counts.support
    save('prediction_distribution', counts)
    return models, focus, scores


# 고정 변환 공간에서 실제 학습 표본의 최근접 구조 계산
def neighbor_analysis(frame, models, focus):
    rows, top = [], []
    setups = [('A_native', models['A'], 6), ('B_native', models['B'], 7),
              ('A_space_train7', models['A'], 7)]
    for space, model, end in setups:
        print('Exact neighbors', space, flush=True)
        train = frame[frame.batch <= end].reset_index(drop=True)
        z_train = model[:-1].transform(train[FEATURES])
        z_query = model[:-1].transform(focus[FEATURES])
        for start in range(0, len(focus), 128):
            query = focus.iloc[start:start + 128]
            distance = cdist(z_query[start:start + 128], z_train)
            nearest5 = np.argsort(distance, axis=1, kind='stable')[:, :5]
            for i, row in enumerate(query.itertuples()):
                selected = train.iloc[nearest5[i]]
                first = selected.iloc[0]
                item = dict(space=space, row_id=row.row_id, batch=row.batch, gas_id=row.gas,
                            nearest_gas=int(first.gas), nearest_batch=int(first.batch),
                            nearest_row_id=first.row_id, nearest_distance=float(distance[i, nearest5[i, 0]]))
                for gas in GASES:
                    ids = np.flatnonzero(train.gas.to_numpy() == gas)
                    index = ids[distance[i, ids].argmin()]
                    item[f'distance_gas_{gas}'] = float(distance[i, index])
                    item[f'nearest_gas_{gas}_row'] = train.row_id.iloc[index]
                    item[f'nearest_gas_{gas}_batch'] = int(train.batch.iloc[index])
                item['other_closer'] = min(item[f'distance_gas_{gas}'] for gas in GASES if gas != row.gas) < item[f'distance_gas_{row.gas}']
                rows.append(item)
                for rank, index in enumerate(nearest5[i], 1):
                    target = train.iloc[index]
                    top.append(dict(space=space, row_id=row.row_id, batch=row.batch, gas_id=row.gas,
                                    rank=rank, neighbor_row_id=target.row_id, neighbor_gas=int(target.gas),
                                    neighbor_batch=int(target.batch), distance=float(distance[i, index])))
    table = save('nearest_neighbors', rows)
    save('top5_neighbors', top)
    counts = table.groupby(['space', 'batch', 'gas_id', 'nearest_gas']).size().rename('n').reset_index()
    counts['support'] = counts.groupby(['space', 'batch', 'gas_id']).n.transform('sum')
    counts['fraction'] = counts.n / counts.support
    save('nearest_gas_counts', counts)
    save('nearest_batch_counts', table.groupby(['space', 'batch', 'gas_id', 'nearest_batch']).size().rename('n').reset_index())
    save('top5_gas_counts', pd.DataFrame(top).groupby(
        ['space', 'batch', 'gas_id', 'neighbor_gas']).size().rename('neighbor_slots').reset_index())
    summaries = []
    for (space, batch, gas), sub in table.groupby(['space', 'batch', 'gas_id']):
        summaries.append(dict(space=space, batch=batch, gas_id=gas, n=len(sub),
                              other_closer_n=int(sub.other_closer.sum()),
                              median_own_distance=float(sub[f'distance_gas_{gas}'].median()),
                              median_Ac_distance=float(sub.distance_gas_4.median()),
                              median_Ethanol_distance=float(sub.distance_gas_1.median()),
                              median_Toluene_distance=float(sub.distance_gas_6.median())))
    save('neighbor_summary', summaries)
    historical = pd.read_csv(ROOT / 'outputs/temporal_failure_diagnostics/sample_proximity.csv')
    sub = table[(table.space == 'A_native') & (table.batch == 9) & (table.gas_id == 6)]
    comparison = sub.merge(historical, on='row_id', suffixes=('_now', '_stage7'), validate='one_to_one')
    np.testing.assert_array_equal(comparison.nearest_gas, comparison.nearest_train_gas)
    np.testing.assert_allclose(comparison.nearest_distance, comparison.nearest_train_distance, atol=1e-8)
    save('stage7_distance_replay', comparison[['row_id', 'nearest_gas', 'nearest_train_gas',
                                              'nearest_distance', 'nearest_train_distance']])
    return table


# 센서 매핑과 동일 가스 분포·상관 구조 정리
def sensor_analysis(frame, models):
    mapping = save('sensor_feature_mapping', [dict(feature=feature, feature_index=i + 1,
                    sensor=i // 8 + 1, within_sensor=i % 8 + 1, kind=KINDS[i % 8],
                    source=SOURCES['uci']) for i, feature in enumerate(FEATURES)])
    transformed = models['A'][:-1].transform(frame[FEATURES])
    populations = {'Train1_6': frame.batch <= 6, 'Train1_7': frame.batch <= 7,
                   'Batch7': frame.batch == 7, **{f'Batch{b}': frame.batch == b for b in [8, 9, 10]}}
    stats, shifts, correlations = [], [], []
    for partition, mask in populations.items():
        for gas in [1, 4, 6]:
            z = transformed[mask & (frame.gas == gas)]
            for j, feature in enumerate(FEATURES):
                stats.append(dict(partition=partition, gas_id=gas, feature=feature, sensor=j // 8 + 1,
                                  n=len(z), mean_z=float(z[:, j].mean()), median_z=float(np.median(z[:, j])),
                                  sd_z=float(z[:, j].std()), q25_z=float(np.quantile(z[:, j], .25)),
                                  q75_z=float(np.quantile(z[:, j], .75))))
            for sensor in range(1, 17):
                columns = list(range((sensor - 1) * 8, sensor * 8))
                corr = pd.DataFrame(z[:, columns]).corr().to_numpy()
                for i in range(8):
                    for j in range(8):
                        correlations.append(dict(partition=partition, gas_id=gas, sensor=sensor,
                                                 feature_i=FEATURES[columns[i]], feature_j=FEATURES[columns[j]],
                                                 n=len(z), correlation=float(corr[i, j])))
    for name, end in [('A', 6), ('B', 7)]:
        for gas in [1, 4, 6]:
            reference = frame[(frame.batch <= end) & (frame.gas == gas)][FEATURES].to_numpy()
            sd = reference.std(axis=0)
            for batch in [8, 9, 10]:
                target = frame[(frame.batch == batch) & (frame.gas == gas)][FEATURES].to_numpy()
                for j, feature in enumerate(FEATURES):
                    distance = wasserstein_distance(reference[:, j], target[:, j])
                    shifts.append(dict(reference=name, batch=batch, gas_id=gas, feature=feature,
                                       sensor=j // 8 + 1, train_n=len(reference), n=len(target),
                                       train_gas_sd=float(sd[j]), wasserstein_raw=float(distance),
                                       normalized_wasserstein=float(distance / sd[j]) if sd[j] > 0 else np.nan))
    save('feature_statistics', stats)
    shift = save('feature_distribution_shift', shifts)
    sensor_shift = shift.groupby(['reference', 'batch', 'gas_id', 'sensor']).agg(
        mean_normalized_wasserstein=('normalized_wasserstein', 'mean'),
        valid_feature_n=('normalized_wasserstein', 'count'), n=('n', 'first')).reset_index()
    save('sensor_distribution_shift', sensor_shift)
    correlation = save('sensor_correlations', correlations)
    changes = []
    for reference in ['Train1_6', 'Train1_7']:
        for gas in [4, 6]:
            for sensor in range(1, 17):
                ref = correlation[(correlation.partition == reference) & (correlation.gas_id == gas) &
                                  (correlation.sensor == sensor)]
                ref = ref[ref.feature_i < ref.feature_j].set_index(['feature_i', 'feature_j']).correlation
                for batch in [8, 9, 10]:
                    target = correlation[(correlation.partition == f'Batch{batch}') &
                                         (correlation.gas_id == gas) & (correlation.sensor == sensor)]
                    target = target[target.feature_i < target.feature_j].set_index(['feature_i', 'feature_j']).correlation
                    differences = (target - ref).abs()
                    changes.append(dict(reference=reference, batch=batch, gas_id=gas, sensor=sensor,
                                        valid_pair_n=int(differences.notna().sum()),
                                        mean_abs_correlation_change=float(differences.mean()),
                                        max_abs_correlation_change=float(differences.max())))
    save('sensor_correlation_changes', changes)
    ranking = sensor_shift[(sensor_shift.reference == 'B') & (sensor_shift.batch == 9) &
                           (sensor_shift.gas_id == 6)].sort_values(
                               ['mean_normalized_wasserstein', 'sensor'], ascending=[False, True]).copy()
    ranking['rank'] = np.arange(1, len(ranking) + 1)
    ranking['plot_selected'] = ranking['rank'] <= 2
    ranking['selection_role'] = 'posthoc_diagnostic_only_not_feature_selection'
    save('sensor_plot_selection', ranking)
    contrast = []
    for partition, mask in populations.items():
        tol = transformed[mask & (frame.gas == 6)]
        ac = transformed[mask & (frame.gas == 4)]
        for sensor in range(1, 17):
            cols = slice((sensor - 1) * 8, sensor * 8)
            contrast.append(dict(partition=partition, sensor=sensor, toluene_n=len(tol), acetaldehyde_n=len(ac),
                                 centroid_distance_A_z=float(np.linalg.norm(tol[:, cols].mean(axis=0) - ac[:, cols].mean(axis=0)))))
    save('sensor_gas_contrasts', contrast)
    return mapping


# Train에만 맞춘 PCA와 Batch9 내부 계층 군집
def projection_and_groups(frame, models, scores):
    points, fit_audits, components = [], [], []
    for name, model in models.items():
        end = 6 if name == 'A' else 7
        train = frame[frame.batch <= end]
        pca = PCA(n_components=2, svd_solver='full', random_state=42)
        z_train = model[:-1].transform(train[FEATURES])
        pca.fit(z_train)
        view = frame[((frame.batch <= end) & frame.gas.isin([1, 4, 6])) |
                     ((frame.batch >= 8) & frame.gas.isin([4, 6]))]
        projected = pca.transform(model[:-1].transform(view[FEATURES]))
        pred_map = scores[scores.model == name].set_index('row_id').prediction
        for row, point in zip(view.itertuples(), projected):
            points.append(dict(model=name, row_id=row.row_id, batch=row.batch, gas_id=row.gas,
                               role='Train' if row.batch <= end else f'Batch{row.batch}',
                               pc1=float(point[0]), pc2=float(point[1]),
                               prediction=pred_map.get(row.row_id, np.nan)))
        fit_audits.append(dict(model=name, train_end=end, fit_n=len(train),
                               fit_batches=sorted(train.batch.unique().tolist()),
                               pca1_variance=float(pca.explained_variance_ratio_[0]),
                               pca2_variance=float(pca.explained_variance_ratio_[1]),
                               fit_row_ids=train.row_id.tolist()))
        for i in range(2):
            for feature, value in zip(FEATURES, pca.components_[i]):
                components.append(dict(model=name, component=i + 1, feature=feature, loading=float(value)))
    save('pca_coordinates', points)
    save('pca_components', components)
    write_json(OUT / 'pca_fit_audit.json', fit_audits)
    focus = frame[(frame.batch == 9) & (frame.gas == 6)].copy()
    z = models['A'][:-1].transform(focus[FEATURES])
    condensed = pdist(z)
    distances = squareform(condensed)
    tree = linkage(condensed, method='ward')
    save('batch9_pairwise_distances', [dict(row_i=focus.row_id.iloc[i], row_j=focus.row_id.iloc[j],
           distance=float(distances[i, j])) for i, j in itertools.combinations(range(len(focus)), 2)])
    save('batch9_linkage', pd.DataFrame(tree, columns=['left', 'right', 'ward_height', 'cluster_n']))
    write_json(OUT / 'batch9_distance_summary.json', dict(
        n=len(focus), pairs=len(condensed), min=float(condensed.min()), median=float(np.median(condensed)),
        max=float(condensed.max()), order_interpretation='file line order, not measurement timestamps'))
    groups = focus[['row_id', 'source_line', 'batch', 'gas']].copy()
    for name in ['A', 'B']:
        sub = scores[scores.model == name].set_index('row_id')
        groups['prediction_' + name] = groups.row_id.map(sub.prediction)
        groups['ovr_T_minus_Ac_' + name] = groups.row_id.map(sub.ovr_toluene_minus_acetaldehyde)
    cluster_summary = []
    for k in [2, 3, 4]:
        labels = fcluster(tree, t=k, criterion='maxclust')
        groups['ward_k' + str(k)] = labels
        silhouette = float(silhouette_score(distances, labels, metric='precomputed'))
        for cluster in sorted(set(labels)):
            sub = groups[labels == cluster]
            cluster_summary.append(dict(k=k, cluster=int(cluster), n=len(sub), silhouette=silhouette,
                                        source_line_min=int(sub.source_line.min()), source_line_max=int(sub.source_line.max()),
                                        B_Ac_n=int((sub.prediction_B == 4).sum()), B_Ethanol_n=int((sub.prediction_B == 1).sum()),
                                        B_Toluene_n=int((sub.prediction_B == 6).sum())))
    save('batch9_subgroups', groups)
    save('batch9_cluster_summary', cluster_summary)
    transitions = groups.groupby(['prediction_A', 'prediction_B']).size().rename('n').reset_index()
    transitions['support'] = len(groups)
    save('prediction_changes', transitions)
    feature_groups = []
    pair = pd.read_csv(OUT / 'ovo_scores.csv')
    margin = pair[(pair.class_i == 4) & (pair.class_j == 6)].pivot(index='row_id', columns='model', values='margin')
    summaries = []
    for predicted, sub in groups.groupby('prediction_B'):
        ids = focus.row_id.isin(sub.row_id).to_numpy()
        for j, feature in enumerate(FEATURES):
            feature_groups.append(dict(prediction_B=int(predicted), feature=feature, sensor=j // 8 + 1,
                                       n=len(sub), mean_A_z=float(z[ids, j].mean()),
                                       median_A_z=float(np.median(z[ids, j])), sd_A_z=float(z[ids, j].std())))
        summaries.append(dict(prediction_B=int(predicted), n=len(sub),
                              source_line_min=int(sub.source_line.min()), source_line_max=int(sub.source_line.max()),
                              ovr_T_minus_Ac_A_median=float(sub.ovr_T_minus_Ac_A.median()),
                              ovr_T_minus_Ac_B_median=float(sub.ovr_T_minus_Ac_B.median()),
                              ovo_Ac_T_A_median=float(margin.loc[sub.row_id, 'A'].median()),
                              ovo_Ac_T_B_median=float(margin.loc[sub.row_id, 'B'].median())))
    save('prediction_group_features', feature_groups)
    save('prediction_group_summary', summaries)


# 분석 순서 및 기존 파일 보존 검증


# 전체 테스트 후 보고서의 검사 결과 확정


