# 저장 모델의 Batch별 실패와 동일 가스의 특징 분포 변화 분석
# 모델·전처리 재학습 없이 기존 예측 재현 및 원본 보존 확인

import json
import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.stats import wasserstein_distance
from sklearn.metrics.pairwise import euclidean_distances
from threadpoolctl import threadpool_limits

from .data import ROOT, FEATURES, GASES, load_dataset, read_config
from .train_models import evaluate
from .temporal_expansion import sha, now, write_json

OUT = ROOT / 'outputs/temporal_failure_diagnostics'
PREVIOUS = ROOT / 'outputs/temporal_expansion'
TRIALS = dict(LR='B_LR_tune_C0p1', RF='B_RF_balanced', SVM='B_SVM_balanced')


# 재현 결과와 파생 표 저장
def save(name, rows):
    data = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    data.to_csv(OUT / f'{name}.csv', index=False, encoding='utf-8')
    return data


# 저장한 분할·전처리·모델과 예측 결과 확인
def replay_models(frame):
    decision = json.loads((PREVIOUS / 'selection_frozen.json').read_text(encoding='utf-8'))
    stored = pd.read_csv(PREVIOUS / 'predictions.csv.gz')
    split = pd.read_csv(PREVIOUS / 'split_assignments.csv')
    expected = np.select([frame.batch <= 6, frame.batch <= 8],
                         ['train', 'validation'], default='evaluation')
    if not np.array_equal(split.row_id, frame.row_id) or not np.array_equal(
            split.main_partition, expected):
        raise ValueError('Existing split changed')
    features_hash = pd.util.hash_pandas_object(frame[FEATURES], index=False)
    for left, right in [('train', 'validation'), ('train', 'evaluation'),
                        ('validation', 'evaluation')]:
        if set(features_hash[expected == left]) & set(features_hash[expected == right]):
            raise ValueError('Cross-partition exact feature duplicate')
    train = frame[frame.batch <= 6]
    future = frame[frame.batch >= 7]
    wide = future[['row_id', 'batch', 'gas']].copy()
    models, checks = {}, []
    for name, trial in TRIALS.items():
        meta = decision['selected_models'][trial]
        path = ROOT / meta['path']
        if sha(path) != meta['sha256']:
            raise ValueError('Selected model bytes changed')
        model = joblib.load(path)
        if not np.array_equal(model.classes_, list(GASES)):
            raise ValueError('Unexpected class mapping')
        if list(model.feature_names_in_) != FEATURES:
            raise ValueError('Unexpected model inputs')
        np.testing.assert_allclose(model.named_steps['imputer'].statistics_,
                                   train[FEATURES].median().to_numpy())
        if name in ['LR', 'SVM']:
            scaler = model.named_steps['scaler']
            assert scaler.n_samples_seen_ == len(train)
            np.testing.assert_allclose(scaler.mean_, train[FEATURES].mean().to_numpy())
            np.testing.assert_allclose(scaler.var_, train[FEATURES].var(ddof=0).to_numpy())
        with threadpool_limits(limits=2):
            predicted = model.predict(future[FEATURES])
        previous = stored[stored.trial_id == trial].set_index('row_id').loc[future.row_id]
        np.testing.assert_array_equal(previous.y_true, future.gas)
        np.testing.assert_array_equal(previous.batch, future.batch)
        np.testing.assert_array_equal(previous.y_pred, predicted)
        wide[name] = predicted
        models[name] = model
        checks.append(dict(model=name, trial_id=trial, n=len(future), exact_replay=True,
                           class_mapping_ok=True, train_preprocessing_ok=True,
                           model_sha256=sha(path)))
    save('replay_checks', checks)
    save('row_predictions', wide)
    return models, wide


# Batch별 클래스 지표와 정답·예측 조합 집계
def performance_tables(wide):
    scores, classes, confusion = [], [], []
    for model in TRIALS:
        for batch, subset in wide.groupby('batch'):
            result, per_class, cm = evaluate(subset.gas, subset[model])
            scores.append(dict(model=model, batch=int(batch), **result,
                               min_class_recall=min(x['recall'] for x in per_class)))
            classes.extend(dict(model=model, batch=int(batch), **row) for row in per_class)
            for i, gas in enumerate(GASES):
                for j, predicted in enumerate(GASES):
                    confusion.append(dict(
                        model=model, batch=int(batch), actual_id=gas,
                        actual_gas=GASES[gas], predicted_id=predicted,
                        predicted_gas=GASES[predicted], count=int(cm[i, j]),
                        actual_n=int(cm[i].sum()), row_fraction=float(cm[i, j] / cm[i].sum()),
                    ))
    scores = save('batch_metrics', scores)
    classes = save('class_metrics', classes)
    confusion = save('confusion_counts', confusion)
    wrong = confusion[confusion.actual_id != confusion.predicted_id].sort_values(
        ['model', 'batch', 'actual_id', 'count'], ascending=[True, True, True, False])
    save('top_misclassifications', wrong.groupby(['model', 'batch', 'actual_id']).head(2))
    bias = []
    for model in TRIALS:
        for batch, group in wide.groupby('batch'):
            for gas in GASES:
                bias.append(dict(model=model, batch=int(batch), gas=GASES[gas],
                                 actual_n=int((group.gas == gas).sum()),
                                 predicted_n=int((group[model] == gas).sum()),
                                 actual_fraction=float((group.gas == gas).mean()),
                                 predicted_fraction=float((group[model] == gas).mean())))
    save('prediction_bias', bias)
    return scores, classes, confusion


# 단독 정분류·공통 실패와 모델 간 불일치 집계
def agreement_tables(wide):
    rows, pairs = [], []
    for batch, group in wide.groupby('batch'):
        for gas in [0, *GASES]:
            part = group if gas == 0 else group[group.gas == gas]
            correct = part[list(TRIALS)].eq(part.gas, axis=0)
            n_correct = correct.sum(axis=1)
            rows.append(dict(
                batch=int(batch), gas_id=gas, gas='ALL' if not gas else GASES[gas], n=len(part),
                **{name + '_only_correct': int((correct[name] & (n_correct == 1)).sum())
                   for name in TRIALS},
                all_wrong=int((n_correct == 0).sum()), all_correct=int((n_correct == 3).sum()),
                disagree_n=int((part[list(TRIALS)].nunique(axis=1) > 1).sum()),
                disagree_rate=float((part[list(TRIALS)].nunique(axis=1) > 1).mean()),
            ))
            for a, b in [('LR', 'SVM'), ('RF', 'SVM'), ('LR', 'RF')]:
                pairs.append(dict(batch=int(batch), gas_id=gas, model_a=a, model_b=b, n=len(part),
                                  same_prediction_n=int((part[a] == part[b]).sum()),
                                  same_prediction_rate=float((part[a] == part[b]).mean()),
                                  a_correct_b_wrong=int((correct[a] & ~correct[b]).sum()),
                                  b_correct_a_wrong=int((correct[b] & ~correct[a]).sum())))
    save('pairwise_agreement', pairs)
    return save('model_agreement', rows)


# 원본 및 Train 표준화 기준의 128개 특징 요약
def feature_tables(frame, svm):
    train = frame[frame.batch <= 6]
    scaler = svm.named_steps['scaler']
    center, scale = scaler.mean_, scaler.scale_
    parts = {f'batch{batch}': frame[frame.batch == batch] for batch in range(1, 11)}
    parts.update(train=train, validation=frame[frame.batch.isin([7, 8])],
                 evaluation=frame[frame.batch.isin([9, 10])])
    summaries = []
    for part, subset in parts.items():
        for gas in [0, *GASES]:
            sub = subset if gas == 0 else subset[subset.gas == gas]
            if sub.empty:
                continue
            raw = sub[FEATURES].to_numpy()
            z = (raw - center) / scale
            for j, feature in enumerate(FEATURES):
                x = raw[:, j]
                summaries.append(dict(
                    partition=part, gas_id=gas, n=len(x), feature=feature,
                    mean=float(x.mean()), std=float(x.std(ddof=0)), median=float(np.median(x)),
                    minimum=float(x.min()), maximum=float(x.max()),
                    q01=float(np.quantile(x, .01)), q99=float(np.quantile(x, .99)),
                    train_z_mean=float(z[:, j].mean()), train_z_std=float(z[:, j].std(ddof=0)),
                    abs_z_gt3_n=int((np.abs(z[:, j]) > 3).sum()),
                    abs_z_gt5_n=int((np.abs(z[:, j]) > 5).sum()),
                ))
    save('feature_summary', summaries)
    shifts = []
    for gas in [0, *GASES]:
        reference = train if gas == 0 else train[train.gas == gas]
        ref = reference[FEATURES].to_numpy()
        ref_sd = ref.std(axis=0, ddof=0)
        if np.any(ref_sd == 0):
            raise ValueError('Zero conditional training scale needs explicit policy')
        for batch in range(7, 11):
            target = frame[(frame.batch == batch) & ((frame.gas == gas) if gas else True)]
            values = target[FEATURES].to_numpy()
            for j, feature in enumerate(FEATURES):
                distance = wasserstein_distance(ref[:, j], values[:, j])
                shifts.append(dict(
                    batch=batch, gas_id=gas, feature=feature, train_n=len(reference), n=len(target),
                    wasserstein_raw=float(distance),
                    wasserstein_train_global_sd=float(distance / scale[j]),
                    wasserstein_same_gas_train_sd=float(distance / ref_sd[j]),
                    mean_shift_train_global_sd=float((values[:, j].mean() - ref[:, j].mean()) / scale[j]),
                    outside_same_gas_train_range=float(
                        ((values[:, j] < ref[:, j].min()) | (values[:, j] > ref[:, j].max())).mean()),
                ))
    shifts = save('feature_shifts', shifts)
    chosen = []
    for gas, batch in [(6, 9), (4, 10)]:
        top = shifts[(shifts.gas_id == gas) & (shifts.batch == batch)].sort_values(
            ['wasserstein_same_gas_train_sd', 'feature'], ascending=[False, True]).head(3).copy()
        top['selection_target'] = f'{GASES[gas]} batch{batch}'
        top['rank'] = range(1, 4)
        chosen.append(top)
    chosen = save('selected_plot_features', pd.concat(chosen, ignore_index=True))
    tail_rows = []
    for name, sub in parts.items():
        z = (sub[FEATURES].to_numpy() - center) / scale
        for gas in [0, 4, 6]:
            mask = np.ones(len(sub), dtype=bool) if gas == 0 else sub.gas.to_numpy() == gas
            if mask.any():
                tail_rows.append(dict(partition=name, gas_id=gas, n=int(mask.sum()),
                                      any_abs_z_gt3_rate=float((np.abs(z[mask]) > 3).any(axis=1).mean()),
                                      any_abs_z_gt5_rate=float((np.abs(z[mask]) > 5).any(axis=1).mean()),
                                      max_abs_z=float(np.abs(z[mask]).max())))
    save('extreme_response_summary', tail_rows)
    return shifts, chosen


# Train 기준 거리로 같은 가스와 다른 가스의 근접성 확인
def proximity_tables(frame, svm, wide):
    train = frame[frame.batch <= 6]
    future = frame[frame.batch >= 7]
    transformed_train = svm[:-1].transform(train[FEATURES])
    transformed_future = svm[:-1].transform(future[FEATURES])
    classifier = svm.named_steps['classifier']
    train_labels = train.gas.to_numpy()
    support = classifier.support_
    rows = []
    with threadpool_limits(limits=2):
        for start in range(0, len(future), 256):
            stop = min(start + 256, len(future))
            squared = euclidean_distances(transformed_future[start:stop],
                                          transformed_train, squared=True)
            nearest = squared.argmin(axis=1)
            own = np.array([squared[i, train_labels == gas].min()
                            for i, gas in enumerate(future.gas.iloc[start:stop])])
            other = np.array([squared[i, train_labels != gas].min()
                              for i, gas in enumerate(future.gas.iloc[start:stop])])
            support_min = squared[:, support].min(axis=1)
            for i, (_, item) in enumerate(future.iloc[start:stop].iterrows()):
                rows.append(dict(
                    row_id=item.row_id, batch=int(item.batch), gas_id=int(item.gas),
                    nearest_train_gas=int(train_labels[nearest[i]]),
                    nearest_train_distance=float(np.sqrt(squared[i, nearest[i]])),
                    nearest_own_gas_distance=float(np.sqrt(own[i])),
                    nearest_other_gas_distance=float(np.sqrt(other[i])),
                    other_gas_closer=bool(other[i] < own[i]),
                    max_rbf_similarity_to_train=float(np.exp(-classifier._gamma * squared[i].min())),
                    max_rbf_similarity_to_support=float(np.exp(-classifier._gamma * support_min[i])),
                ))
    proximity = save('sample_proximity', rows)
    joined = proximity.merge(wide[['row_id', *TRIALS]], on='row_id', validate='one_to_one')
    aggregate = joined.groupby(['batch', 'gas_id']).agg(
        n=('row_id', 'size'), other_gas_closer_rate=('other_gas_closer', 'mean'),
        median_own_distance=('nearest_own_gas_distance', 'median'),
        median_other_distance=('nearest_other_gas_distance', 'median'),
        median_max_support_kernel=('max_rbf_similarity_to_support', 'median'),
    ).reset_index()
    save('proximity_summary', aggregate)
    save('nearest_train_gas_counts', proximity.groupby(
        ['batch', 'gas_id', 'nearest_train_gas']).size().rename('n').reset_index())
    return aggregate


# 저장 모델의 특징 의존 지표와 상관관계 기록
def dependence_tables(frame, models, chosen):
    coefficient = models['LR'].named_steps['classifier'].coef_
    importance = models['RF'].named_steps['classifier'].feature_importances_
    rows = []
    for j, feature in enumerate(FEATURES):
        row = dict(feature=feature, lr_mean_abs_coefficient=float(np.abs(coefficient[:, j]).mean()),
                   rf_impurity_importance=float(importance[j]))
        row.update({f'lr_coefficient_class{gas}': float(coefficient[i, j])
                    for i, gas in enumerate(GASES)})
        rows.append(row)
    dependency = save('model_feature_dependence', rows)
    selected = list(dict.fromkeys(chosen.feature))
    corr = frame[frame.batch <= 6][FEATURES].corr()
    correlations = []
    for feature in selected:
        best = corr[feature].drop(feature).abs().sort_values(ascending=False).head(3)
        for other in best.index:
            correlations.append(dict(feature=feature, correlated_feature=other,
                                     train_pearson_r=float(corr.loc[feature, other])))
    save('selected_feature_correlations', correlations)
    return dependency


# 새 경로에서 진단 실행 및 기존 파일 지문 보존
def run():
    targets = ['temporal_failure_diagnostic_report.html', 'temporal_failure_improvement_proposal.md']
    if OUT.exists() or any((ROOT / 'reports' / name).exists() for name in targets):
        raise FileExistsError('Diagnostic outputs already exist')
    before = {str(p.relative_to(ROOT)): sha(p)
              for name in ['src', 'tests', 'reports', 'models', 'outputs']
              for p in (ROOT / name).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    frame, source = load_dataset(read_config())
    raw = dict(zip(source.file, source.sha256))
    previous = json.loads((PREVIOUS / 'run_manifest.json').read_text(encoding='utf-8'))
    if raw != previous['raw_hashes']:
        raise ValueError('Raw dataset mismatch')
    OUT.mkdir(parents=True)
    write_json(OUT / 'analysis_protocol.json', dict(
        recorded_at_seoul=now(), train_batches=list(range(1, 7)),
        validation_batches=[7, 8], exploratory_evaluation_batches=[9, 10],
        models=TRIALS, new_model_fits=0, preprocessing_fits=0,
        pca_umap_used=False, model_or_threshold_changes=False,
        feature_plot_selection='Top three of 128 features for each focus target: '
        'Toluene batch9 and Acetaldehyde batch10, ranked by univariate Wasserstein '
        'distance from same-gas Train divided by same-gas Train population SD; '
        'feature name breaks ties; diagnostic plots only, no model feature selection.',
        extreme_rule='abs(z)>3 and >5 using frozen SVM Train scaler; descriptive, not removal.',
        proximity='Euclidean distance in frozen SVM Train standardized 128-D space; '
        'class labels describe neighbors, not a newly trained classifier. '
        'No use of diagnostic results for model tuning.',
        independent_test=False,
    ))
    print('Checking existing models and reproducing predictions', flush=True)
    models, wide = replay_models(frame)
    scores, classes, confusion = performance_tables(wide)
    agreement = agreement_tables(wide)
    print('Summarizing 128 features and conditional Wasserstein shifts', flush=True)
    shifts, chosen = feature_tables(frame, models['SVM'])
    proximity = proximity_tables(frame, models['SVM'], wide)
    dependence = dependence_tables(frame, models, chosen)
    shift_average = shifts[shifts.gas_id > 0].groupby(['batch', 'gas_id']).agg(
        mean_conditional_wasserstein=('wasserstein_same_gas_train_sd', 'mean'),
        mean_global_sd_wasserstein=('wasserstein_train_global_sd', 'mean'),
    ).reset_index()
    joined = classes.merge(shift_average, on=['batch', 'gas_id'], validate='many_to_one')
    save('shift_and_performance', joined)
    save('batch_class_counts', frame.groupby(['batch', 'gas']).size().rename('n').reset_index())
    print('Creating diagnostic report', flush=True)
    from .temporal_failure_report import build_report
    build_report(frame, wide, scores, classes, confusion, agreement, shifts,
                 chosen, proximity, dependence)
    after = {name: sha(ROOT / name) for name in before}
    if before != after:
        raise RuntimeError('Preserved file changed')
    directory = Path(read_config()['data_dir'])
    if any(sha(directory / name) != value for name, value in raw.items()):
        raise RuntimeError('Raw file changed')
    write_json(OUT / 'run_manifest.json', dict(
        completed_at_seoul=now(), before=before, after=after, raw_hashes=raw,
        existing_files_unchanged=True, raw_files_unchanged=True,
        new_model_fits=0, preprocessing_fits=0, independent_test=False,
        code_sha256={name: sha(ROOT / 'src' / name) for name in
                     ['temporal_failure_diagnostics.py', 'temporal_failure_report.py']},
    ))
    print(scores.to_string(index=False), flush=True)
    print(agreement[((agreement.batch == 9) & (agreement.gas_id == 6)) |
                    ((agreement.batch == 10) & (agreement.gas_id == 4))].to_string(index=False))


if __name__ == '__main__':
    try:
        run()
    except Exception:
        logging.exception('Temporal failure diagnostics failed')
        raise
