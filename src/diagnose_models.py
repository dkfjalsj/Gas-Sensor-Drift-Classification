# 저장된 모델·예측으로 성능 저하와 특징 변화 분석
# 새 분류기 학습 및 기존 분석 결과 덮어쓰기 금지
import hashlib
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import joblib
import numpy as np
import pandas as pd
from scipy.stats import wasserstein_distance, spearmanr
from sklearn.decomposition import PCA
from sklearn.metrics import confusion_matrix, pairwise_distances_argmin_min
from threadpoolctl import threadpool_limits
from .data import ROOT, FEATURES, GASES, feature_label, load_dataset, read_config
from .train_models import evaluate

OUT = ROOT / 'outputs' / 'model_diagnostics'
OLD = ROOT / 'outputs' / 'model_comparison'
COMMON = [6, 7, 8, 9, 10]
SELECTED = [1, 2, 3, 6, 9, 17, 65, 121]


# 파일 변경 확인용 해시 계산
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(name, value):
    (OUT / name).write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8'
    )


# 값이 일정하거나 표본이 부족하면 관련성 계산 생략
def rho(x, y):
    x, y = np.asarray(x), np.asarray(y)
    valid = np.isfinite(x) & np.isfinite(y)
    if valid.sum() < 3 or len(np.unique(x[valid])) < 2 or len(np.unique(y[valid])) < 2:
        return np.nan
    return float(spearmanr(x[valid], y[valid]).statistic)


# 동일 가스의 훈련·평가 특징 분포 차이 계산
def distribution_changes(frame, assignments):
    records = []
    for exp in ['B_early', 'B_history']:
        ids = assignments[
            (assignments.experiment == exp) & (assignments.partition == 'train')
        ].row_id
        reference = frame[frame.row_id.isin(ids)]
        pooled_sd = reference[FEATURES].std(ddof=0)
        for gas in GASES:
            ref = reference[reference.gas == gas]
            for batch in range(1, 11):
                target = frame[(frame.gas == gas) & (frame.batch == batch)]
                if target.empty:
                    continue
                for feature in FEATURES:
                    distance = wasserstein_distance(ref[feature], target[feature])
                    scale = pooled_sd[feature]
                    records.append(
                        dict(
                            experiment=exp,
                            batch=batch,
                            gas=GASES[gas],
                            gas_id=gas,
                            feature=feature,
                            reference_n=len(ref),
                            target_n=len(target),
                            wasserstein_raw=distance,
                            wasserstein_scaled=distance / scale if scale > 0 else np.nan,
                            reference_scale=float(scale),
                        )
                    )
    return pd.DataFrame(records)


# 기존 파이프라인 예측과 저장된 예측 대조
def inspect_models(frame, assignments, saved, records):
    lookup = frame.set_index('row_id', drop=False)
    train_rows = []
    costs = []
    coef = []
    importance = []
    sensitivity = []
    replay = []
    benchmark = frame[frame.batch.isin(COMMON)][FEATURES]
    all_predictions = [saved.assign(origin='existing_saved_predictions')]
    for record in records:
        exp, model = record['experiment'], record['model']
        path = ROOT / record['model_file']
        if sha(path) != record['sha256']:
            raise ValueError(f'Saved model hash mismatch: {path.name}')
        pipeline = joblib.load(path)
        classifier = pipeline.named_steps['classifier']
        selected = saved[(saved.experiment == exp) & (saved.model == model)]
        if selected.empty:
            parts = assignments[
                (assignments.experiment == exp) & (assignments.partition != 'train')
            ]
            selected = parts.rename(columns={'gas': 'y_true'}).copy()
            selected['model'] = model
            selected['y_pred'] = pipeline.predict(lookup.loc[selected.row_id, FEATURES])
            all_predictions.append(selected.assign(origin='recreated_from_saved_model'))
        with threadpool_limits(limits=2):
            predicted = pipeline.predict(lookup.loc[selected.row_id, FEATURES])
        if not np.array_equal(predicted, selected.y_pred):
            raise ValueError(f'Prediction replay mismatch: {exp}/{model}')
        replay.append(dict(experiment=exp, model=model, rows=len(selected), exact_match=True))
        train_ids = assignments[
            (assignments.experiment == exp) & (assignments.partition == 'train')
        ].row_id
        train = lookup.loc[train_ids]
        with threadpool_limits(limits=2):
            train_pred = pipeline.predict(train[FEATURES])
        train_metric, _, _ = evaluate(train.gas, train_pred)
        train_rows.append(dict(experiment=exp, model=model, **train_metric))
        # 새 학습 없이 훈련 자료의 참고 점수 계산
        train_predictions = (
            train[['row_id', 'batch', 'gas']].rename(columns={'gas': 'y_true'}).copy()
        )
        train_predictions['y_pred'] = train_pred
        train_predictions['experiment'] = exp
        train_predictions['model'] = model
        train_predictions['partition'] = 'train'
        train_predictions['origin'] = 'resubstitution_prediction'
        all_predictions.append(train_predictions)
        with threadpool_limits(limits=2):
            pipeline.predict(benchmark.iloc[:128])
            durations = []
            for _ in range(3):
                start = time.perf_counter()
                pipeline.predict(benchmark)
                durations.append(time.perf_counter() - start)
        costs.append(
            dict(
                experiment=exp,
                model=model,
                train_n=len(train),
                fit_seconds_recorded=record['fit_seconds'],
                predict_n=len(benchmark),
                prediction_seconds_median=float(np.median(durations)),
                prediction_ms_per_1000=float(np.median(durations) * 1e6 / len(benchmark)),
                model_bytes=path.stat().st_size,
                n_support=(
                    int(classifier.n_support_.sum()) if hasattr(classifier, 'n_support_') else None
                ),
            )
        )
        if model == 'LogisticRegression':
            for row, gas in enumerate(classifier.classes_):
                for j, feature in enumerate(FEATURES):
                    coef.append(
                        dict(
                            experiment=exp,
                            gas=GASES[int(gas)],
                            feature=feature,
                            coefficient=float(classifier.coef_[row, j]),
                            abs_coefficient=float(abs(classifier.coef_[row, j])),
                        )
                    )
        if model == 'RandomForest':
            for j, feature in enumerate(FEATURES):
                importance.append(
                    dict(
                        experiment=exp,
                        feature=feature,
                        importance=float(classifier.feature_importances_[j]),
                    )
                )
        if model == 'SVM_RBF':
            targets = pd.concat([train_predictions, selected], ignore_index=True)
            values = pipeline[:-1].transform(lookup.loc[targets.row_id, FEATURES])
            with threadpool_limits(limits=2):
                _, dist = pairwise_distances_argmin_min(values, classifier.support_vectors_)
            targets = targets.copy()
            targets['max_support_rbf_similarity'] = np.exp(-classifier._gamma * dist**2)
            targets['correct'] = targets.y_true == targets.y_pred
            for (part, batch), group in targets.groupby(['partition', 'batch']):
                sensitivity.append(
                    dict(
                        experiment=exp,
                        partition=part,
                        batch=int(batch),
                        n=len(group),
                        gamma=float(classifier._gamma),
                        accuracy=float(group.correct.mean()),
                        similarity_median=float(group.max_support_rbf_similarity.median()),
                        similarity_correct_median=(
                            float(group.loc[group.correct, 'max_support_rbf_similarity'].median())
                            if group.correct.any()
                            else np.nan
                        ),
                        similarity_wrong_median=(
                            float(group.loc[~group.correct, 'max_support_rbf_similarity'].median())
                            if (~group.correct).any()
                            else np.nan
                        ),
                    )
                )
        print('Inspected', exp, model, flush=True)
    return (
        pd.concat(all_predictions, ignore_index=True),
        pd.DataFrame(train_rows),
        pd.DataFrame(costs),
        pd.DataFrame(coef),
        pd.DataFrame(importance),
        pd.DataFrame(sensitivity),
        pd.DataFrame(replay),
    )


# 평가 자료별 점수와 가스별 오류 개수 계산
def error_tables(predictions):
    batch_rows = []
    gas_rows = []
    pairs = []
    matrices = []
    for (exp, model, part), group in predictions.groupby(
        ['experiment', 'model', 'partition'], sort=False
    ):
        slices = [('pooled', 0, group)] + [('batch', int(b), s) for b, s in group.groupby('batch')]
        if part == 'test':
            slices.append(('common_6_10', 0, group[group.batch.isin(COMMON)]))
        for scope, batch, sub in slices:
            metrics, classes, cm = evaluate(sub.y_true, sub.y_pred)
            meta = dict(experiment=exp, model=model, partition=part, scope=scope, batch=batch)
            batch_rows.append(dict(**meta, **metrics, n_classes=sub.y_true.nunique()))
            for row in classes:
                error_n = int(((sub.y_true == row['gas_id']) & (sub.y_pred != sub.y_true)).sum())
                gas_rows.append(
                    dict(
                        **meta,
                        **row,
                        errors=error_n,
                        error_rate=error_n / row['support'] if row['support'] else np.nan,
                    )
                )
            for i, gas in enumerate(GASES):
                support = cm[i].sum()
                for j, predicted in enumerate(GASES):
                    entry = dict(
                        **meta,
                        true_gas=GASES[gas],
                        predicted_gas=GASES[predicted],
                        count=int(cm[i, j]),
                        true_support=int(support),
                        true_class_fraction=float(cm[i, j] / support) if support else np.nan,
                    )
                    matrices.append(entry)
                    if i != j and cm[i, j] > 0:
                        pairs.append(entry)
    return (
        pd.DataFrame(batch_rows),
        pd.DataFrame(gas_rows),
        pd.DataFrame(pairs),
        pd.DataFrame(matrices),
    )


# 동일 미래 Batch의 평균·변동·최저 가스 재현율 비교
def selection_table(metrics, gas, costs):
    rows = []
    for (exp, model), sub in metrics[
        (metrics.partition == 'test') & (metrics.scope == 'batch')
    ].groupby(['experiment', 'model']):
        same = sub[sub.batch.isin(COMMON)]
        pooled = metrics[
            (metrics.experiment == exp)
            & (metrics.model == model)
            & (metrics.partition == 'test')
            & (metrics.scope == 'common_6_10')
        ].iloc[0]
        classes = gas[
            (gas.experiment == exp)
            & (gas.model == model)
            & (gas.partition == 'test')
            & (gas.scope == 'common_6_10')
        ]
        worst = classes.loc[classes.recall.idxmin()]
        batch_classes = gas[
            (gas.experiment == exp)
            & (gas.model == model)
            & (gas.partition == 'test')
            & (gas.scope == 'batch')
            & gas.batch.isin(COMMON)
        ]
        cost = costs[(costs.experiment == exp) & (costs.model == model)].iloc[0]
        rows.append(
            dict(
                experiment=exp,
                model=model,
                common_n=int(pooled.n),
                common_batches=5,
                pooled_accuracy=pooled.accuracy,
                pooled_macro_f1=pooled.macro_f1,
                equal_batch_mean_f1=same.macro_f1.mean(),
                batch_sd_f1=same.macro_f1.std(ddof=0),
                min_batch_f1=same.macro_f1.min(),
                worst_batch=int(same.loc[same.macro_f1.idxmin(), 'batch']),
                best_batch=int(same.loc[same.macro_f1.idxmax(), 'batch']),
                max_batch_f1=same.macro_f1.max(),
                min_class_recall=worst.recall,
                worst_gas=worst.gas,
                class_recall_sd=classes.recall.std(ddof=0),
                zero_recall_gas_batch_cells=int((batch_classes.recall == 0).sum()),
                fit_seconds_recorded=cost.fit_seconds_recorded,
                prediction_ms_per_1000=cost.prediction_ms_per_1000,
                model_bytes=int(cost.model_bytes),
            )
        )
    return pd.DataFrame(rows)


# 분포 변화와 오류의 관련성 계산 및 인과 해석 제한
def associations(distances, metrics, gas):
    per_gas = distances.groupby(['experiment', 'batch', 'gas'], as_index=False).agg(
        shift=('wasserstein_scaled', 'mean'), n=('target_n', 'first')
    )
    per_batch = per_gas.groupby(['experiment', 'batch'], as_index=False).agg(
        shift=('shift', 'mean'), n_classes=('gas', 'nunique')
    )
    agg = []
    feature_rows = []
    class_rows = []
    for exp in ['B_early', 'B_history']:
        d = distances[(distances.experiment == exp) & distances.batch.isin(COMMON)]
        feature_shift = (
            d.groupby(['batch', 'feature'])
            .wasserstein_scaled.mean()
            .unstack('feature')
            .reindex(COMMON)
        )
        for model in ['LogisticRegression', 'RandomForest', 'SVM_RBF']:
            m = (
                metrics[
                    (metrics.experiment == exp)
                    & (metrics.model == model)
                    & (metrics.partition == 'test')
                    & (metrics.scope == 'batch')
                    & metrics.batch.isin(COMMON)
                ]
                .set_index('batch')
                .reindex(COMMON)
            )
            shift = (
                per_batch[(per_batch.experiment == exp) & per_batch.batch.isin(COMMON)]
                .set_index('batch')
                .reindex(COMMON)
            )
            agg.append(
                dict(
                    experiment=exp,
                    model=model,
                    n_batches=5,
                    spearman_shift_vs_f1_loss=rho(shift['shift'], 1 - m.macro_f1),
                )
            )
            for f in FEATURES:
                feature_rows.append(
                    dict(
                        experiment=exp,
                        model=model,
                        feature=f,
                        n_batches=5,
                        spearman_shift_vs_f1_loss=rho(feature_shift[f], 1 - m.macro_f1),
                    )
                )
            for name in GASES.values():
                c = (
                    gas[
                        (gas.experiment == exp)
                        & (gas.model == model)
                        & (gas.partition == 'test')
                        & (gas.scope == 'batch')
                        & (gas.gas == name)
                        & gas.batch.isin(COMMON)
                    ]
                    .set_index('batch')
                    .reindex(COMMON)
                )
                s = (
                    per_gas[
                        (per_gas.experiment == exp)
                        & (per_gas.gas == name)
                        & per_gas.batch.isin(COMMON)
                    ]
                    .set_index('batch')
                    .reindex(COMMON)
                )
                class_rows.append(
                    dict(
                        experiment=exp,
                        model=model,
                        gas=name,
                        n_batches=5,
                        spearman_shift_vs_recall_loss=rho(s['shift'], 1 - c.recall),
                    )
                )
    return (
        per_gas,
        per_batch,
        pd.DataFrame(agg),
        pd.DataFrame(feature_rows),
        pd.DataFrame(class_rows),
    )


# 기존 훈련 자료 기준으로 PCA 시각화 값 계산
def diagnostic_pca(frame, assignments):
    coordinates = []
    variance = []
    for exp in ['B_early', 'B_history']:
        pipe = joblib.load(ROOT / 'models' / f'{exp}__LogisticRegression.joblib')
        ids = assignments[
            (assignments.experiment == exp) & (assignments.partition == 'train')
        ].row_id
        train = frame.row_id.isin(ids).to_numpy()
        values = pipe[:-1].transform(frame[FEATURES])
        with threadpool_limits(limits=2):
            pca = PCA(n_components=2, svd_solver='full').fit(values[train])
            pcs = pca.transform(values)
        for i, v in enumerate(pca.explained_variance_ratio_, 1):
            variance.append(
                dict(experiment=exp, component=i, train_explained_variance_ratio=float(v))
            )
        part_map = assignments[assignments.experiment == exp].set_index('row_id').partition
        temp = frame[['row_id', 'batch', 'gas']].copy()
        temp['partition'] = temp.row_id.map(part_map)
        temp['pc1'] = pcs[:, 0]
        temp['pc2'] = pcs[:, 1]
        temp['experiment'] = exp
        coordinates.append(temp)
    return pd.concat(coordinates, ignore_index=True), pd.DataFrame(variance)


# 기존 파일 해시 기록 및 새 폴더에 진단 결과 저장
def run():
    if OUT.exists() or (ROOT / 'reports' / 'model_diagnostic_report.html').exists():
        raise FileExistsError(
            'Diagnostic output already exists; archive it explicitly before rerunning'
        )
    baseline = [
        p
        for folder in ['outputs', 'reports', 'models']
        for p in (ROOT / folder).rglob('*')
        if p.is_file()
    ]
    before = {str(p.relative_to(ROOT)): sha(p) for p in baseline}
    OUT.mkdir(parents=True)
    frame, source = load_dataset(read_config())
    records = json.loads((OLD / 'fit_records.json').read_text(encoding='utf-8'))
    assignments = pd.read_csv(OLD / 'split_assignments.csv')
    pred_path = OLD / 'predictions.csv'
    saved = (
        pd.read_csv(pred_path)
        if pred_path.exists()
        else pd.DataFrame(
            columns=['row_id', 'batch', 'y_true', 'y_pred', 'experiment', 'model', 'partition']
        )
    )
    predictions, train, costs, coef, importance, sensitivity, replay = inspect_models(
        frame, assignments, saved, records
    )
    metrics, gas, pairs, matrices = error_tables(predictions)
    old = pd.read_csv(OLD / 'metrics.csv')
    # 기존 평가 표본과 점수 재확인
    for row in old.itertuples(index=False):
        current = metrics[
            (metrics.experiment == row.experiment)
            & (metrics.model == row.model)
            & (metrics.partition == row.partition)
            & (metrics.scope == row.scope)
            & (metrics.batch == row.batch)
        ]
        if len(current) != 1 or any(
            not np.isclose(current.iloc[0][key], getattr(row, key))
            for key in ['accuracy', 'macro_f1', 'macro_precision', 'macro_recall', 'weighted_f1']
        ):
            raise ValueError('Existing metric reproduction failed')
    stats = (
        frame.groupby(['batch', 'gas'])[FEATURES]
        .agg(['mean', 'median', 'std'])
        .stack(level=0, future_stack=True)
        .reset_index()
        .rename(columns={'level_2': 'feature'})
    )
    distances = distribution_changes(frame, assignments)
    pergas, perbatch, assoc, feature_assoc, gas_assoc = associations(distances, metrics, gas)
    selection = selection_table(metrics, gas, costs)
    pcs, variance = diagnostic_pca(frame, assignments)
    correlation_rows = []
    for exp in ['B_early', 'B_history']:
        ids = assignments[
            (assignments.experiment == exp) & (assignments.partition == 'train')
        ].row_id
        corr = frame.loc[frame.row_id.isin(ids), FEATURES].corr(method='spearman').abs()
        for i in range(128):
            for j in range(i + 1, 128):
                if corr.iloc[i, j] >= 0.9:
                    correlation_rows.append(
                        dict(
                            experiment=exp,
                            feature1=FEATURES[i],
                            feature2=FEATURES[j],
                            abs_train_spearman=float(corr.iloc[i, j]),
                        )
                    )
    tables = {
        'predictions': predictions,
        'metrics': metrics,
        'gas_errors': gas,
        'error_pairs': pairs,
        'confusion_matrices': matrices,
        'train_scores': train,
        'costs': costs,
        'lr_coefficients': coef,
        'rf_importance': importance,
        'svm_sensitivity': sensitivity,
        'prediction_replay': replay,
        'feature_stats': stats,
        'wasserstein': distances,
        'gas_shift': pergas,
        'batch_shift': perbatch,
        'batch_associations': assoc,
        'feature_associations': feature_assoc,
        'gas_associations': gas_assoc,
        'selection_evidence': selection,
        'pca_coordinates': pcs,
        'pca_variance': variance,
        'correlated_feature_pairs': pd.DataFrame(correlation_rows),
    }
    for name, table in tables.items():
        table.to_csv(OUT / f'{name}.csv', index=False, encoding='utf-8')
    after = {name: sha(ROOT / name) for name in before}
    if before != after:
        raise RuntimeError('Existing artifact changed')
    source_unchanged = all(
        sha(Path(read_config()['data_dir']) / row['file']) == row['sha256']
        for row in source.to_dict('records')
    )
    if not source_unchanged:
        raise RuntimeError('Raw dataset changed')
    write_json(
        'preservation.json',
        dict(
            existing_artifacts_unchanged=True,
            raw_files_unchanged=True,
            before=before,
            after=after,
            raw_hashes=dict(zip(source.file, source.sha256)),
        ),
    )
    manifest = dict(
        generated_at_seoul=datetime.now(ZoneInfo('Asia/Seoul')).isoformat(),
        new_classifier_fits=0,
        diagnostic_pca_fit='2 exploratory PCA fits, Train only; no classifier changes',
        prediction_source='existing predictions verified by replay; Train predictions added as resubstitution diagnostics',
        prediction_replay_rows=int(replay.rows.sum()),
        benchmark_repetitions=3,
        common_batches=COMMON,
        code_sha256=sha(Path(__file__)),
        post_test_exploratory=True,
        final_model_selected=False,
    )
    write_json('run_manifest.json', manifest)
    from .diagnostic_report import build_report

    build_report(tables, manifest)
    print(selection.to_string(index=False), flush=True)


if __name__ == '__main__':
    try:
        run()
    except Exception:
        logging.exception('Diagnostic analysis failed')
        raise
