# Train 시기·가스·Batch 가중치의 시간순 검증과 학습 범위 비교
# 사전 보호 기준으로 후보 고정 후 Batch 9–10 탐색적 평가 수행

import time
import warnings

import joblib
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from .data import ROOT, FEATURES, GASES
from .improve_models import make_pipeline
from .temporal_expansion import sha, write_json
from .temporal_robustness import FOLDS, score_predictions, summarize, sha_rows

OUT = ROOT / 'outputs/temporal_weighting'
MODELS = ROOT / 'models/temporal_weighting'
SCHEMES = ['class_balanced', 'time_linear', 'time_exp', 'time_recent',
           'class_sample', 'gas_batch', 'time_class_shrink', 'time_gas_batch']


# 표를 UTF-8 CSV로 저장
def save(name, rows):
    data = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    data.to_csv(OUT / f'{name}.csv', index=False, encoding='utf-8')
    return data


# 해당 Train의 실제 표본 수만으로 제한된 가중치 계산
def calculate_weights(train, scheme):
    if scheme not in SCHEMES:
        raise ValueError('Unknown weighting scheme')
    if set(train.gas) != set(GASES):
        raise ValueError('Training classes missing')
    n = len(train)
    gas_counts = train.groupby('gas').size()
    cell_counts = train.groupby(['gas', 'batch']).size()
    gas_batches = train.groupby('gas').batch.nunique()
    class_factor = train.gas.map(n / (6 * gas_counts)).to_numpy(dtype=float)
    batches = sorted(train.batch.unique())
    position = train.batch.map({b: i for i, b in enumerate(batches)}).to_numpy(dtype=float)
    u = position / max(len(batches) - 1, 1)
    temporal = np.ones(n)
    cell = np.ones(n)
    gas_factor = class_factor.copy()
    class_weight = 'balanced' if scheme in SCHEMES[:4] else None
    if scheme in ['time_linear', 'time_class_shrink']:
        temporal = 1 + u
    elif scheme == 'time_exp':
        temporal = np.power(2.0, u)
    elif scheme == 'time_recent':
        temporal = np.where(position >= max(len(batches) - 2, 0), 1.75, 1.0)
    if scheme in ['gas_batch', 'time_gas_batch']:
        cell = np.array([
            np.clip(np.sqrt(gas_counts[g] / (gas_batches[g] * cell_counts.loc[(g, b)])), .75, 1.5)
            for g, b in zip(train.gas, train.batch)
        ])
    if scheme == 'time_class_shrink':
        gas_factor = np.sqrt(class_factor)
    if scheme == 'time_gas_batch':
        temporal = np.sqrt(1 + u)
    raw_effective = gas_factor * temporal * cell
    normalization = float(raw_effective.mean())
    effective = raw_effective / normalization
    applied_class = class_factor if class_weight == 'balanced' else np.ones(n)
    sample = effective / applied_class
    if not np.isfinite(effective).all() or effective.min() <= 0:
        raise ValueError('Invalid effective weights')
    if not np.isclose(effective.mean(), 1):
        raise ValueError('Effective weights are not mean-normalized')
    weights = train[['row_id', 'batch', 'gas']].copy()
    weights['scheme'] = scheme
    weights['balanced_class_reference'] = class_factor
    weights['gas_factor'] = gas_factor
    weights['temporal_factor'] = temporal
    weights['cell_factor'] = cell
    weights['normalization'] = normalization
    weights['applied_class_factor'] = applied_class
    weights['sample_weight'] = sample
    weights['effective_weight'] = effective
    weights['effective_C'] = effective
    return class_weight, weights


# 실행 전에 수식·예산·보호 기준 기록


# 가중치별 보호 지표 통과 여부 계산
def select_candidate(summary, metrics, classes):
    baseline = summary[summary.config_id == 'class_balanced'].iloc[0]
    rows = []
    base_class = classes[classes.config_id == 'class_balanced']
    base_zeros = set(map(tuple, base_class[base_class.recall == 0][['fold', 'gas_id']].to_numpy()))
    base_min = metrics[metrics.config_id == 'class_balanced'].set_index('fold').min_class_recall
    for _, row in summary.iterrows():
        tests = {}
        tests['macro_guard'] = row.mean_macro_f1 >= baseline.mean_macro_f1 - .005 - 1e-12
        tests['toluene_guard'] = row.mean_toluene_recall >= baseline.mean_toluene_recall - .03 - 1e-12
        tests['acetaldehyde_guard'] = row.mean_acetaldehyde_recall >= baseline.mean_acetaldehyde_recall - .03 - 1e-12
        tests['other_four_guard'] = row.mean_other_four_f1 >= baseline.mean_other_four_f1 - .02 - 1e-12
        tests['individual_other_guard'] = all(
            row[f'mean_class{gas}_f1'] >= baseline[f'mean_class{gas}_f1'] - .05 - 1e-12 for gas in [1, 2, 3, 5])
        tests['min_recall_guard'] = row.min_recall >= baseline.min_recall - .02 - 1e-12
        subset = metrics[metrics.config_id == row.config_id].set_index('fold').min_class_recall
        tests['fold_min_guard'] = bool((subset >= base_min - .05 - 1e-12).all())
        part = classes[classes.config_id == row.config_id]
        zeros = set(map(tuple, part[part.recall == 0][['fold', 'gas_id']].to_numpy()))
        tests['zero_pair_guard'] = zeros.issubset(base_zeros)
        tests['improvement_evidence'] = bool(
            row.config_id == 'class_balanced' or len(zeros) < len(base_zeros) or
            row.mean_macro_f1 >= baseline.mean_macro_f1 + .002 - 1e-12)
        rows.append(dict(config_id=row.config_id, **tests, eligible=all(tests.values()),
                         failed_guards=','.join(k for k, value in tests.items() if not value)))
    checks = pd.DataFrame(rows)
    valid = summary[summary.config_id.isin(checks[checks.eligible].config_id)].copy()
    near = valid[valid.mean_macro_f1 >= valid.mean_macro_f1.max() - .005 - 1e-12].copy()
    near['focus_min_recall'] = near[['mean_toluene_recall', 'mean_acetaldehyde_recall']].min(axis=1)
    near = near.sort_values(
        ['zero_recall_pairs', 'min_recall', 'focus_min_recall', 'pooled_macro_f1', 'sd_macro_f1', 'order'],
        ascending=[True, False, False, False, True, True])
    return near.iloc[0].config_id, checks


# 같은 Fold Train으로 전처리·가중치·모델 학습
def train_folds(frame):
    metrics, classes, matrices, predictions, records, weights_all = [], [], [], [], [], []
    for fold, (end, validation_batch) in FOLDS.items():
        train = frame[frame.batch <= end]
        validation = frame[frame.batch == validation_batch]
        (MODELS / fold).mkdir()
        for scheme in SCHEMES:
            class_weight, weights = calculate_weights(train, scheme)
            weights['fold'] = fold
            weights_all.append(weights)
            model = make_pipeline('SVM_RBF', 'standard', class_weight, {})
            supplied = None if scheme == 'class_balanced' else weights.sample_weight.to_numpy()
            start = time.perf_counter()
            with warnings.catch_warnings(record=True) as caught, threadpool_limits(limits=2):
                warnings.simplefilter('always')
                model.fit(train[FEATURES], train.gas, classifier__sample_weight=supplied)
            fit_seconds = time.perf_counter() - start
            classifier = model.named_steps['classifier']
            actual_class = pd.Series(classifier.class_weight_, index=classifier.classes_)
            actual_effective = train.gas.map(actual_class).to_numpy() * weights.sample_weight.to_numpy()
            np.testing.assert_allclose(actual_effective, weights.effective_weight)
            with threadpool_limits(limits=2):
                start = time.perf_counter()
                predicted = model.predict(validation[FEATURES])
                seconds = time.perf_counter() - start
            metric, per_class, cm, pred = score_predictions(
                scheme, fold, validation, predicted, fit_seconds, seconds, 128)
            metrics.append(metric)
            classes.extend(per_class)
            matrices.extend(cm)
            predictions.append(pred)
            path = MODELS / fold / f'{scheme}.joblib'
            joblib.dump(model, path, compress=3)
            records.append(dict(
                scheme=scheme, fold=fold, train_end=end, train_n=len(train), validation_batch=validation_batch,
                validation_n=len(validation), train_row_ids_sha256=sha_rows(train.row_id),
                model_file=str(path.relative_to(ROOT)), sha256=sha(path),
                class_weight=class_weight, actual_class_factors=actual_class.to_dict(),
                params=classifier.get_params(), gamma_effective=float(classifier._gamma),
                fit_seconds=fit_seconds, predict_seconds=seconds,
                sample_weight_supplied=scheme != 'class_balanced',
                effective_weight_min=float(weights.effective_weight.min()),
                effective_weight_max=float(weights.effective_weight.max()),
                effective_weight_mean=float(weights.effective_weight.mean()),
                weight_concentration_n=float(weights.effective_weight.sum() ** 2 /
                                             np.square(weights.effective_weight).sum()),
                warnings=[dict(category=w.category.__name__, message=str(w.message)) for w in caught],
            ))
            print(f'{fold} {scheme}: Macro F1={metric["macro_f1"]:.6f}', flush=True)
    predictions = pd.concat(predictions, ignore_index=True)
    control = []
    for fold in FOLDS:
        a = predictions[(predictions.config_id == 'class_balanced') &
                        (predictions.fold == fold)].sort_values('row_id')
        b = predictions[(predictions.config_id == 'class_sample') &
                        (predictions.fold == fold)].sort_values('row_id')
        control.append(dict(fold=fold, n=len(a), different_predictions=int((a.y_pred.to_numpy() != b.y_pred.to_numpy()).sum())))
    save('class_sample_equivalence_control', control)
    all_weights = pd.concat(weights_all, ignore_index=True)
    all_weights.to_csv(OUT / 'sample_weights.csv.gz', index=False, encoding='utf-8', compression='gzip')
    groups = all_weights.groupby(['fold', 'scheme', 'gas', 'batch']).agg(
        n=('row_id', 'size'), sum_effective=('effective_weight', 'sum'),
        mean_effective=('effective_weight', 'mean'), min_effective=('effective_weight', 'min'),
        max_effective=('effective_weight', 'max'), temporal_factor=('temporal_factor', 'first'),
        cell_factor=('cell_factor', 'first')).reset_index()
    save('weight_group_summary', groups)
    summary = summarize(metrics, classes, predictions, {name: i for i, name in enumerate(SCHEMES)})
    selected, checks = select_candidate(summary, pd.DataFrame(metrics), pd.DataFrame(classes))
    for name, data in [('fold_metrics', metrics), ('fold_class_metrics', classes),
                       ('fold_confusion', matrices), ('cv_summary', summary), ('guard_checks', checks)]:
        save(name, data)
    write_json(OUT / 'fit_records.json', records)
    predictions.to_csv(OUT / 'fold_predictions.csv.gz', index=False, encoding='utf-8', compression='gzip')
    return selected, checks


# 동일 설정의 학습 범위를 공통 미래 Batch8에서 비교
def compare_ranges_before_evaluation(frame):
    validation = frame[frame.batch == 8]
    rows, classes, predictions = [], [], []
    for end, fold in [(6, 'B'), (7, 'C')]:
        for scheme in SCHEMES:
            model = joblib.load(MODELS / fold / f'{scheme}.joblib')
            with threadpool_limits(limits=2):
                predicted = model.predict(validation[FEATURES])
            metric, per_class, _, pred = score_predictions(scheme, str(end), validation, predicted)
            rows.append(metric)
            classes.extend(per_class)
            predictions.append(pred)
    save('range_batch8_metrics', rows)
    save('range_batch8_classes', classes)
    pd.concat(predictions, ignore_index=True).to_csv(
        OUT / 'range_batch8_predictions.csv.gz', index=False, encoding='utf-8', compression='gzip')


# 평가 전에 후보·범위·모델 지문 동결


# 후보 고정 이후 기존 모델과 두 학습 범위의 탐색적 평가


# 기존 파일을 보존하면서 고정된 실험 전체 실행


