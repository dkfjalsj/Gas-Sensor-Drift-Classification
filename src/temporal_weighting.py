# Train 시기·가스·Batch 가중치의 시간순 검증과 학습 범위 비교
# 사전 보호 기준으로 후보 고정 후 Batch 9–10 탐색적 평가 수행

import importlib.metadata
import json
import logging
import shutil
import time
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from .data import ROOT, FEATURES, GASES, load_dataset, read_config
from .improve_models import make_pipeline
from .temporal_expansion import measured_scores, sha, now, write_json
from .temporal_robustness import FOLDS, score_predictions, summarize, sha_rows, split_folds

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
def freeze_protocol(frame):
    targets = ['temporal_weighting_report.html', 'temporal_weighting_model_selection.md',
               'temporal_weighting_protocol.md']
    if OUT.exists() or MODELS.exists() or any((ROOT / 'reports' / f).exists() for f in targets):
        raise FileExistsError('Temporal weighting output already exists')
    support = split_folds(frame)
    OUT.mkdir(parents=True)
    MODELS.mkdir(parents=True)
    save('fold_support', support)
    plan = dict(
        frozen_at_seoul=now(), seed=42, schemes=SCHEMES, setting_count=8, classifier_fits=24,
        folds=FOLDS, final_comparison_train_ends=[6, 7], primary_candidate_train_end=6,
        model='SVM RBF, StandardScaler, C=1, gamma=scale, 128 features; original other settings',
        preprocessing='Unweighted median imputer and StandardScaler fitted only on each Train. '
        'Weights passed only to classifier. No feature selection or PCA.',
        formulas=dict(
            class_balanced='c=N/(6*n_g), class_weight=balanced, sample_weight=None',
            time_linear='raw=c*(1+u), class_weight=balanced, sample=(1+u)/mean(raw)',
            time_exp='raw=c*2**u, class_weight=balanced, sample=2**u/mean(raw)',
            time_recent='raw=c*t, t=1.75 for last two observed Train batches, else1',
            class_sample='raw=c, class_weight=None, sample=c/mean(c); equivalence control',
            gas_batch='raw=c*r; r=clip(sqrt(n_g/(m_g*n_gb)), .75,1.5); class_weight=None',
            time_class_shrink='raw=sqrt(c)*(1+u); class_weight=None',
            time_gas_batch='raw=c*r*sqrt(1+u); class_weight=None',
        ),
        normalization='effective=raw/mean(raw); class multiplier*sample multiplier=effective; '
        'C_i=C*effective. u=ordinal rank among observed Train batches/(B-1), not elapsed time.',
        primary='Equal-weight mean of Fold macro F1',
        guards=dict(
            mean_macro_max_drop=.005, mean_focus_recall_max_drop=.03,
            mean_other_four_f1_max_drop=.02, each_other_mean_f1_max_drop=.05,
            minimum_recall_max_drop=.02, each_fold_min_recall_max_drop=.05,
            no_new_zero_recall_pairs=True,
            evidence='Nonbaseline must reduce zero pairs OR improve mean macro F1 by at least .002',
        ),
        tie='Among guard-passing candidates and baseline, within .005 of best mean macro: '
        'fewer zero pairs, higher min recall, higher min(mean Toluene recall, mean Acetaldehyde recall), '
        'higher pooled macro, smaller Fold SD, fixed scheme order. Baseline retained if none pass.',
        range_comparison='Baseline Train1-6 vs1-7 on common Batch8; not a range selection. '
        'Candidate weighting also paired at both ranges. No evaluation of Train1-7 on Batch7.',
        evaluation_gate='Freeze candidate, selected model hashes and rules before any Batch9-10 predictions.',
        candidate_fallback='Keep original stage6 saved SVM bytes if no nonbaseline candidate passes guards.',
        independent_test=False, test_reused=True,
        training_config_sha256=sha(ROOT / 'training_config.json'),
        official_weight_reference='https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html',
    )
    write_json(OUT / 'experiment_plan.json', plan)
    text = '''# 9단계 사전 실험 계획

## 고정 분할과 예산
SVM8개 가중치 설정 × Fold A/B/C =24회 분류기 Fit. LR 추가 실험 없음.
A Train1–3→Validation6, B Train1–6→Validation7, C Train1–7→Validation8.
실제 존재하는 가스·Batch만 사용. 합성·재표본화 없음. Train/Validation 클래스·중복 확인.
Fold A Train Toluene79개, Fold C Validation Toluene18개. Fold는 독립 반복 아님.
원본128특징, Train median imputer와 StandardScaler. 전처리는 무가중 Train Fit 유지.
SVM RBF C1,gamma=scale,seed42, 기존 나머지 설정 유지. 가중치만 분류기에 적용.

## 가중치 수식
N=Train크기, n_g=가스 수, n_gb=실재 가스·Batch 셀 수, m_g=가스가 존재하는 Train Batch 수.
c=N/(6*n_g), u=Train의 관찰 Batch 순서0..B-1을0..1로 변환. 실제 경과 시간이 아님.
r=clip(sqrt(n_g/(m_g*n_gb)),0.75,1.5). 모든 raw를 평균1로 정규화해 effective로 사용.
1. class_balanced: raw=c, class_weight=balanced, sample=None.
2. time_linear: raw=c*(1+u), class_weight=balanced, sample=(1+u)/mean(raw).
3. time_exp: raw=c*2**u, class_weight=balanced, sample=2**u/mean(raw).
4. time_recent: raw=c*t, 최근2개 Train Batch t=1.75, 나머지1, class_weight=balanced.
5. class_sample: raw=c, class_weight=None, sample=effective. 동일 유효 가중치의 대조.
6. gas_batch: raw=c*r, class_weight=None. 작은 셀의 완전 역빈도 보정 대신 제한된 제곱근 보정.
7. time_class_shrink: raw=sqrt(c)*(1+u), class_weight=None. 완화된 가스 균형과 시간 결합.
8. time_gas_batch: raw=c*r*sqrt(1+u), class_weight=None. 제한된 셀 보정·완만한 시간 결합.
class_weight의 실제 승수×sample_weight가 effective이며 C_i=C*effective로 기록.
class_sample은 baseline과의 동등성 대조이며 독립적인 새 개선 방법으로 부풀리지 않음.
시간 승수1..2, 셀 승수0.75..1.5. 특정 가스 우대 계수 없음. 모든 가중치 양수.
가스·Batch 보정은 정확히 셀 질량을 같게 만드는 방법이 아니며 작은 셀 과대 영향 방지가 목적.
행별 가중치·셀별 질량·최소최대·가중치 집중도(합w)^2/합w² 기록. 집중도는 독립 표본 수 추정 아님.

## 사전 선정과 보호 기준
기준 class_balanced에 비해 다음을 모두 만족해야 함.
- Fold 평균 Macro F1 하락 최대0.5pp, Toluene/Acetaldehyde 평균 Recall 각각 하락 최대3pp.
- 나머지4종 평균F1 하락 최대2pp, 각 가스 Fold평균F1 하락 최대5pp.
- 전체 최소Recall 하락 최대2pp, 각 Fold 최소Recall 하락 최대5pp.
- 기존에 없던 Recall0 Fold/가스 조합 추가 금지.
- 비기준 후보는0% 조합을 줄이거나 평균Macro F1을0.2pp 이상 높여야 함.
통과 후보가 없으면 원래6단계 SVM 유지. 기준은 항상 비교 집합에 유지.
유효 설정 최고평균의0.5pp 이내에서 적은0% 조합→높은최소Recall→높은
min(Toluene평균Recall,Acetaldehyde평균Recall)→높은합산Macro F1→낮은Fold SD→설정순서.
보호 수치는 사전 탐색 기준이며 통계적 유의성·운영 안전 기준이 아님. 평균만으로 우수 판정 금지.

## 학습 범위 비교와 평가
가중치 후보 선정은3Fold만 사용. 후보의 주 모델은Train1–6으로 기존SVM과 가중치 효과 비교.
같은 설정의Train1–7 모델은 별도 확장 비교이며 주 후보로 사후 교체하지 않음.
기본 설정Train1–6(B모델) vs1–7(C모델)을 공통미래Batch8에서 비교.
Batch8을 보고 학습 범위를 재선정하지 않음. Validation으로 이미 사용한18개 Toluene의 한계 명시.
후보와 모델SHA 고정 후에만9–10 평가. 모든8설정의Train6/7과 기존SVM·8단계Hard Voting 기록.
학습 범위가 다른 모델은 별도 표. 학습량·시기·클래스 구성 효과를 데이터 양 하나로 해석 금지.
과거 Test 재사용의 회고적·탐색적 평가이며 독립 최종Test 아님. 평가 기반 재선정·튜닝 금지.
기존1–8단계 파일·모델·원본·해시·테스트 보존. 기존실패3건은 별도 기록. Commit·Push 금지.
'''
    (ROOT / 'reports/temporal_weighting_protocol.md').write_text(text, encoding='utf-8')
    return plan


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
def freeze_selection(selected, checks):
    prior = json.loads((ROOT / 'outputs/temporal_expansion/selection_frozen.json').read_text(encoding='utf-8'))
    baseline = prior['selected_models']['B_SVM_balanced']
    assert sha(ROOT / baseline['path']) == baseline['sha256']
    saved = {}
    for end, fold in [(6, 'B'), (7, 'C')]:
        source = ROOT / baseline['path'] if selected == 'class_balanced' and end == 6 else MODELS / fold / f'{selected}.joblib'
        target = MODELS / f'selected_train1_{end}_{selected}.joblib'
        shutil.copy2(source, target)
        saved[str(end)] = dict(path=str(target.relative_to(ROOT)), sha256=sha(target))
    decision = dict(
        frozen_at_seoul=now(), selected_scheme=selected,
        eligible_schemes=checks[checks.eligible].config_id.tolist(),
        baseline_retained=selected == 'class_balanced', main_candidate_train_end=6,
        expansion_comparison_train_end=7, selected_models=saved,
        selection_used='Folds A/B/C only; range Batch8 not used to select deployment range',
        evaluation_used=False, independent_test=False, final_confirmed_model=False,
    )
    write_json(OUT / 'selection_frozen.json', decision)
    return decision


# 후보 고정 이후 기존 모델과 두 학습 범위의 탐색적 평가
def evaluate_frozen(frame, decision):
    selection_hash = sha(OUT / 'selection_frozen.json')
    started = now()
    evaluation = frame[frame.batch >= 9]
    tasks = []
    for end, fold in [(6, 'B'), (7, 'C')]:
        for scheme in SCHEMES:
            tasks.append((f'train{end}_{scheme}', end, scheme, MODELS / fold / f'{scheme}.joblib'))
    stage6 = json.loads((ROOT / 'outputs/temporal_expansion/selection_frozen.json').read_text(encoding='utf-8'))
    stage8 = json.loads((ROOT / 'outputs/temporal_robustness/selection_frozen.json').read_text(encoding='utf-8'))
    tasks += [
        ('stage6_SVM', 6, 'class_balanced', ROOT / stage6['selected_models']['B_SVM_balanced']['path']),
        ('stage8_HardVoting', 6, 'historical_hard_voting',
         ROOT / stage8['selected_models']['hard_representatives']['path']),
    ]
    rows, classes, matrices, predictions, times, model_files = [], [], [], [], [], []
    for model_id, end, scheme, path in tasks:
        model = joblib.load(path)
        with threadpool_limits(limits=2):
            start = time.perf_counter()
            predicted = model.predict(evaluation[FEATURES])
            seconds = time.perf_counter() - start
        times.append(dict(model_id=model_id, train_end=end, n=len(evaluation),
                          predict_seconds=seconds, ms_per_1000=seconds * 1e6 / len(evaluation)))
        model_files.append(dict(model_id=model_id, train_end=end, scheme=scheme,
                                path=str(path.relative_to(ROOT)), sha256=sha(path)))
        for batch in ['pooled', 9, 10]:
            mask = np.ones(len(evaluation), dtype=bool) if batch == 'pooled' else evaluation.batch.to_numpy() == batch
            metric, per_class, cm, pred = score_predictions(model_id, str(batch), evaluation[mask], predicted[mask])
            metric.update(train_end=end, scheme=scheme)
            rows.append(metric)
            classes.extend(dict(**row, train_end=end, scheme=scheme) for row in per_class)
            matrices.extend(cm)
            if batch == 'pooled':
                predictions.append(pred)
    predictions = pd.concat(predictions, ignore_index=True)
    baseline = predictions[predictions.config_id == 'stage6_SVM'].sort_values('row_id')
    fresh = predictions[predictions.config_id == 'train6_class_balanced'].sort_values('row_id')
    np.testing.assert_array_equal(fresh.y_pred, baseline.y_pred)
    old_predictions = pd.read_csv(ROOT / 'outputs/temporal_expansion/predictions.csv.gz')
    old_predictions = old_predictions[(old_predictions.trial_id == 'B_SVM_balanced') &
                                      (old_predictions.partition == 'evaluation')].sort_values('row_id')
    np.testing.assert_array_equal(baseline.y_pred, old_predictions.y_pred)
    old_hard = pd.read_csv(ROOT / 'outputs/temporal_robustness/evaluation_predictions.csv.gz')
    old_hard = old_hard[old_hard.config_id == 'hard_representatives'].sort_values('row_id')
    current_hard = predictions[predictions.config_id == 'stage8_HardVoting'].sort_values('row_id')
    np.testing.assert_array_equal(current_hard.y_pred, old_hard.y_pred)
    for name, data in [('evaluation_metrics', rows), ('evaluation_classes', classes),
                       ('evaluation_confusion', matrices), ('evaluation_times', times),
                       ('evaluation_models', model_files)]:
        save(name, data)
    predictions.to_csv(OUT / 'evaluation_predictions.csv.gz', index=False, encoding='utf-8', compression='gzip')
    assert sha(OUT / 'selection_frozen.json') == selection_hash
    write_json(OUT / 'evaluation_gate.json', dict(
        evaluation_started_at_seoul=started, selection_sha256=selection_hash,
        selection_before_evaluation=decision['frozen_at_seoul'] <= started,
        evaluation_used_for_selection=False, original_SVM_reproduced=True,
        stage8_HardVoting_reproduced=True,
    ))


# 기존 파일을 보존하면서 고정된 실험 전체 실행
def run():
    before = {str(p.relative_to(ROOT)): sha(p)
              for directory in ['src', 'tests', 'reports', 'models', 'outputs']
              for p in (ROOT / directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    before.update({name: sha(ROOT / name) for name in
                   ['config.json', 'training_config.json', 'README.md', 'requirements.txt', '.gitignore']})
    frame, source = load_dataset(read_config())
    raw = dict(zip(source.file, source.sha256))
    old = json.loads((ROOT / 'outputs/temporal_robustness/run_manifest.json').read_text(encoding='utf-8'))
    assert raw == old['raw_hashes']
    plan = freeze_protocol(frame)
    plan_hash = sha(OUT / 'experiment_plan.json')
    protocol_hash = sha(ROOT / 'reports/temporal_weighting_protocol.md')
    selected, checks = train_folds(frame)
    compare_ranges_before_evaluation(frame)
    decision = freeze_selection(selected, checks)
    print('FROZEN', selected, 'baseline retained:', decision['baseline_retained'], flush=True)
    evaluate_frozen(frame, decision)
    from .temporal_weighting_report import build_report
    build_report(plan, decision)
    after = {name: sha(ROOT / name) for name in before}
    assert before == after
    assert sha(OUT / 'experiment_plan.json') == plan_hash
    assert all(sha(Path(read_config()['data_dir']) / name) == value for name, value in raw.items())
    write_json(OUT / 'run_manifest.json', dict(
        completed_at_seoul=now(), before=before, after=after, raw_hashes=raw,
        settings=8, classifier_fits=24, model_ranges=[6, 7], independent_test=False,
        plan_sha256=plan_hash, protocol_sha256=protocol_hash,
        code_sha256={name: sha(ROOT / 'src' / name) for name in
                     ['temporal_weighting.py', 'temporal_weighting_report.py']},
        package_versions={name: importlib.metadata.version(name) for name in
                          ['numpy', 'pandas', 'scikit-learn', 'scipy', 'joblib', 'matplotlib']},
    ))
    print(pd.read_csv(OUT / 'cv_summary.csv').to_string(index=False), flush=True)


if __name__ == '__main__':
    try:
        run()
    except Exception:
        logging.exception('Temporal weighting experiment failed')
        raise
