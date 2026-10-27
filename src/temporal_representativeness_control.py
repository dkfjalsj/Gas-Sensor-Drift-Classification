# 시기별 표본 구성·표본 수·전처리의 통제 비교 실험
# 사전 고정한 부분표본과 SVM으로 회고적 시간순 평가 수행

import argparse
import copy
import importlib.metadata
import json
import logging
from pathlib import Path
import time
import xml.etree.ElementTree as ET

import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from threadpoolctl import threadpool_limits

from .data import ROOT, FEATURES, GASES, load_dataset, read_config
from .temporal_expansion import measured_scores, now, sha, write_json

OUT = ROOT / 'outputs/temporal_representativeness_control'
MODEL_DIR = ROOT / 'models/temporal_representativeness_control'
FOLDS = {'A': (3, 6), 'B': (6, 7), 'C': (7, 8)}
SEEDS = [11, 23, 42, 67, 101]
REPORTS = ['temporal_representativeness_control_report.html',
           'temporal_representativeness_control_summary.md',
           'temporal_representativeness_control_limitations.md']
SETTINGS = [
    ('early_mid', 'early', 'mid', 'native', 'balanced', 'A'),
    ('spread_mid', 'spread', 'mid', 'native', 'balanced', 'A'),
    ('recent_mid', 'recent', 'mid', 'native', 'balanced', 'A'),
    ('spread_small', 'spread', 'small', 'native', 'balanced', 'B'),
    ('spread_max', 'spread', 'max', 'native', 'balanced', 'B'),
    ('spread_mid_unit', 'spread', 'mid', 'native', 'unit', 'C'),
    ('spread_mid_anchor', 'spread', 'mid', 'anchor', 'balanced', 'C'),
    ('spread_mid_anchor_unit', 'spread', 'mid', 'anchor', 'unit', 'C'),
]
FUTURE_SETTINGS = ['early_mid', 'spread_mid', 'recent_mid', 'spread_max']


# 실험 표 저장
def save(name, rows):
    table = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    table.to_csv(OUT / f'{name}.csv', index=False, encoding='utf-8')
    return table


# 기존 원본 외 프로젝트 파일 지문 수집
def snapshot():
    files = [p for directory in ['src', 'tests', 'reports', 'models', 'outputs']
             for p in (ROOT / directory).rglob('*') if p.is_file()
             and '__pycache__' not in p.parts and OUT not in p.parents
             and MODEL_DIR not in p.parents]
    files += [ROOT / n for n in ['config.json', 'training_config.json', 'README.md',
                                 'requirements.txt', 'requirements-lock.txt', '.gitignore']]
    return {str(p.relative_to(ROOT)): sha(p) for p in files}


# 가스별 실제 초기 표본 수에서 공통 예산 계산
def budgets(frame):
    anchor = frame[frame.batch <= 2].groupby('gas').size().reindex(GASES)
    return {name: {int(g): int(np.floor(n * fraction)) for g, n in anchor.items()}
            for name, fraction in [('small', .25), ('mid', .5), ('max', 1)]}


# 시기 구성에 따른 가스별 Batch 배분량 계산
def allocate(available, total, scheme):
    available = {int(b): int(n) for b, n in sorted(available.items()) if n > 0}
    assert sum(available.values()) >= total
    result = {b: 0 for b in available}
    if scheme in ['early', 'recent']:
        for batch in sorted(available, reverse=scheme == 'recent'):
            take = min(available[batch], total)
            result[batch] = take
            total -= take
    else:
        assert scheme == 'spread'
        while total:
            for batch in available:
                if result[batch] < available[batch] and total:
                    result[batch] += 1
                    total -= 1
    assert total == 0
    return result


# 가스·Batch별 고정 순열의 앞부분에서 중복 없이 추출
def sample_rows(frame, end, scheme, gas_budget, seed):
    eligible = frame[frame.batch <= (2 if scheme == 'early' else end)]
    selected = []
    for gas, count in gas_budget.items():
        sub = eligible[eligible.gas == gas]
        allocation = allocate(sub.groupby('batch').size().to_dict(), count, scheme)
        for batch, n in allocation.items():
            ids = sub.index[sub.batch == batch].to_numpy()
            rng = np.random.default_rng(np.random.SeedSequence([seed, gas, batch]))
            selected.extend(rng.permutation(ids)[:n].tolist())
    return np.array(sorted(selected), dtype=int)


# 결과 확인 전에 실험 수·표본·해석 규칙 고정
def freeze(frame):
    if OUT.exists() or MODEL_DIR.exists() or any((ROOT / 'reports' / n).exists() for n in REPORTS):
        raise FileExistsError('Stage12 output already exists')
    OUT.mkdir(parents=True)
    MODEL_DIR.mkdir(parents=True)
    budget = budgets(frame)
    assert [sum(budget[b].values()) for b in ['small', 'mid', 'max']] == [419, 843, 1689]
    plan = dict(
        frozen_at=now(), folds=FOLDS, seeds=SEEDS, budgets=budget,
        settings=[dict(setting=s, scheme=a, budget=b, preprocessing=p, weight=w, experiment=e)
                  for s, a, b, p, w, e in SETTINGS],
        classifier_fits=120, native_preprocessing_fits=90, common_anchor_preprocessing_fits=1,
        per_seed_models=24, candidate_selection=False, official_main_candidate='Model A',
        svm=dict(kernel='rbf', C=1., gamma='scale', feature_count=128),
        early='Strict initial pool Batch1-2. Greedy ascending Batch allocation per gas.',
        spread='Round-robin equal counts across existing gas-Batch cells, capacity capped; ascending tie.',
        recent='Greedy descending Batch allocation per gas. No future samples.',
        budget_definition='25%,50%,100% (floor per gas) of Batch1-2 gas counts. '
        'Max means largest under strict early pool, NOT dataset maximum. '
        'Identical six gas counts across schemes and folds at each budget.',
        sampling='Fixed per-cell SeedSequence(seed,gas,Batch) permutation prefixes. '
        'No replacement. Spread budgets nested. Same row subsets across C contrasts.',
        primary='Five-seed average of equal-weight Fold6/7/8 Macro F1; also report each Fold.',
        consistent_effect='Descriptive only: paired delta mean >=0.005, each of three Fold '
        'mean deltas >0 and at least4/5 seed-level equal-Fold deltas >0. '
        'Not a significance test or future generalization claim. Report all negative effects.',
        protection='Separately flag any gas mean Recall drop >0.05, other-four mean F1 '
        'drop >0.02, or increased gas-Fold zero Recall pairs vs spread_mid. '
        'No best setting or seed selection; ties yield no superiority conclusion.',
        anchor='Counterfactual common median imputer and StandardScaler fitted once on '
        'all Batch1-2 (1689 rows), strictly past all Validation. '
        'Additional unsupervised training reference beyond selected classifier rows; '
        'C contrasts are NOT matched total information-budget experiments.',
        weight='balanced from selected Train labels; fixed unit dict {1..6:1.0} '
        'as equal-penalty control. No sample_weight. Same gas budgets imply identical '
        'balanced weights within A. Rounding may alter weights slightly across B budgets.',
        gamma='gamma=scale always. Native standardization gives1/128; common anchor '
        'may change actual gamma via Train transformed variance. C preprocessing effect '
        'includes automatic bandwidth change, not isolated scaler-only causal effect.',
        future_settings=FUTURE_SETTINGS, future_fold='C', future_seeds=SEEDS,
        future='After historical findings frozen, reuse20 Fold C models; evaluate9/10 '
        'and pooled. No new future-fit, winner, seed choice or tuning. '
        'Stored A/B only unmatched-size reference table. No new independent Test.',
        uncertainty='Seed SD(ddof=1) describes subset randomness only. Folds overlap, '
        'seeds share data and cell permutations; no IID repeated-trial claim or p-value.',
        missing='Unsupported gas-Batch cells stay0 support, never synthetic rows. '
        'Unavailable comparisons are NA, not performance0.',
        compute_budget='120 SVC fits of419-1689 rows,128 features. No search/early stopping. '
        'All five seeds retained. Historical full-data SVC runs suggest manageable CPU cost.',
    )
    write_json(OUT / 'experiment_plan.json', plan)
    allocation, samples = [], []
    for fold, (end, target) in FOLDS.items():
        for setting, scheme, level, prep, weight, experiment in SETTINGS:
            for seed in SEEDS:
                ids = sample_rows(frame, end, scheme, budget[level], seed)
                sub = frame.loc[ids]
                assert len(sub) == len(set(ids)) and sub.batch.max() < target
                assert sub.groupby('gas').size().to_dict() == budget[level]
                for row in sub.itertuples():
                    samples.append(dict(fold=fold, setting=setting, seed=seed, row_id=row.row_id,
                                        batch=row.batch, gas_id=row.gas))
                for gas in GASES:
                    for batch in range(1, end + 1):
                        available = int(((frame.batch == batch) & (frame.gas == gas)).sum())
                        allocation.append(dict(fold=fold, setting=setting, seed=seed, gas_id=gas,
                                               batch=batch, n=int(((sub.batch == batch) & (sub.gas == gas)).sum()),
                                               available=available, eligible=not (scheme == 'early' and batch > 2),
                                               budget=level, total_n=len(sub)))
    save('sample_assignments', samples)
    save('sample_composition', allocation)
    save('batch_class_support', frame.groupby(['batch', 'gas']).size().rename('n').reset_index())
    plan['sample_assignments_sha256'] = sha(OUT / 'sample_assignments.csv')
    plan['sample_composition_sha256'] = sha(OUT / 'sample_composition.csv')
    write_json(OUT / 'experiment_plan.json', plan)
    protocol = '''# 12단계 통제 실험 사전 계획

목적은 구성 효과 구분이며 최고 점수/후보/시드 선정 아님. 공식 Model A 유지.
Fold A Train1–3→6, B1–6→7, C1–7→8. 새 독립 Test 없음.
시드11,23,42,67,101 모두 사용. 8조건×3Fold×5시드=120 SVC Fit.

초기 집중=Batch1–2 안에서 오래된 Batch부터 가스별 채움.
분산=가스가 실제 존재하는 과거 Batch를 용량 제한 균등 순환 배분.
최근=가장 최근 Batch부터 가스별 채움. 3조건 모두 같은 가스별 예산.
Batch1–2 가스 수[254,432,183,139,602,79]의25/50/100% 내림.
총419/843/1689개. 최대는 이 초기 풀 제약 내 최대 공통 예산이며 데이터 전체 최대가 아님.
A는843개에서3구성, B는분산419/843/1689개. 작은 예산의 가스 비율 반올림 차이 명시.

C는분산843개 고정 부분표본에서 native/공통anchor × balanced/고정unit 2×2대조.
anchor는Batch1–2 전체1689개로imputer/scaler 한 번 Fit, 전Fold보다 과거임.
선택Train 밖의 추가 과거 무정답 통계 정보가 있어 총정보예산 통제와 구분.
gamma=scale 유지, 실제gamma 변경이 전처리 대조에 포함되므로 순수scaler효과 아님.
고정unit은가스1–6 모두1.0. sample_weight 중복 적용 없음.

주 요약은Fold별Macro F1 동일 가중 평균을시드5개 평균/표준편차로 표시.
일관된 방향 기준: paired 평균+0.5pp 이상,3Fold 평균차 모두양수,5시드중4개이상양수.
통계적 유의성 기준이 아님. 가스Recall5pp/나머지4종F1 2pp 초과 손실 또는0Recall조합 증가 별도표시.
최적모델/시드 선택 없음. 차이 작으면 우월성 미확인. 모든 조건·실패·시드 보고.

과거 요약·해석 JSON을 먼저 고정한 뒤C Fold의 early_mid/spread_mid/recent_mid/spread_max
각5시드20모델만Batch9–10 평가. A/B 저장모델은 별도크기 참조.
9–10 결과로조건/시드/선정규칙 변경 금지. 독립 최종Test 아님.
'''
    (OUT / 'protocol.md').write_text(protocol, encoding='utf-8')
    return plan


# 동일 지표와 클래스별 결과·혼동행렬 기록
def evaluate(model, sub, meta, metrics, classes, predictions, matrices):
    started = time.perf_counter()
    predicted = model.predict(sub[FEATURES])
    seconds = time.perf_counter() - started
    score, per_class, cm = measured_scores(sub.gas, predicted)
    metrics.append(dict(**meta, **score, predict_seconds=seconds,
                        zero_recall_classes=int(sum(r['recall'] == 0 for r in per_class if r['support'] > 0))))
    classes.extend(dict(**meta, **row) for row in per_class)
    predictions.extend(dict(**meta, row_id=row.row_id, batch=row.batch,
                            y_true=row.gas, y_pred=int(pred))
                       for row, pred in zip(sub.itertuples(), predicted))
    for i, actual in enumerate(GASES):
        for j, predicted_gas in enumerate(GASES):
            matrices.append(dict(**meta, actual_id=actual, predicted_id=predicted_gas,
                                 count=int(cm[i, j]), support=int(cm[i].sum())))


# 고정한 학습 표본만으로120개 SVM 학습 및 과거 평가
def fit_history(frame, plan):
    assignments = pd.read_csv(OUT / 'sample_assignments.csv')
    indexed = frame.set_index('row_id', drop=False)
    anchor = frame[frame.batch <= 2]
    anchor_imputer = SimpleImputer(strategy='median').fit(anchor[FEATURES])
    anchor_scaler = StandardScaler().fit(anchor_imputer.transform(anchor[FEATURES]))
    write_json(OUT / 'anchor_preprocessing.json', dict(
        n=len(anchor), rows=anchor.row_id.tolist(), batches=[1, 2],
        imputer=anchor_imputer.statistics_.tolist(), mean=anchor_scaler.mean_.tolist(),
        scale=anchor_scaler.scale_.tolist(), var=anchor_scaler.var_.tolist()))
    metrics, classes, predictions, matrices, records, prep_stats, weights = [], [], [], [], [], [], []
    for fold, (end, target) in FOLDS.items():
        for setting, scheme, level, prep, weight, experiment in SETTINGS:
            for seed in SEEDS:
                key = (assignments.fold == fold) & (assignments.setting == setting) & (assignments.seed == seed)
                train = indexed.loc[assignments.loc[key, 'row_id']].copy()
                validation = frame[frame.batch == target]
                assert set(train.row_id).isdisjoint(validation.row_id)
                assert train.batch.max() < target
                assert set(pd.util.hash_pandas_object(train[FEATURES], index=False)).isdisjoint(
                    pd.util.hash_pandas_object(validation[FEATURES], index=False))
                started = time.perf_counter()
                if prep == 'anchor':
                    imputer, scaler = copy.deepcopy(anchor_imputer), copy.deepcopy(anchor_scaler)
                    reference = anchor
                else:
                    imputer = SimpleImputer(strategy='median').fit(train[FEATURES])
                    scaler = StandardScaler().fit(imputer.transform(train[FEATURES]))
                    reference = train
                transformed = scaler.transform(imputer.transform(train[FEATURES]))
                class_weight = 'balanced' if weight == 'balanced' else {g: 1. for g in GASES}
                classifier = SVC(kernel='rbf', C=1., gamma='scale', class_weight=class_weight,
                                 random_state=seed, cache_size=256)
                classifier.fit(transformed, train.gas.to_numpy())
                model = Pipeline([('imputer', imputer), ('scaler', scaler), ('classifier', classifier)])
                fit_seconds = time.perf_counter() - started
                path = MODEL_DIR / f'{fold}_{setting}_seed{seed}.joblib'
                joblib.dump(model, path)
                meta = dict(fold=fold, setting=setting, seed=seed, scope=str(target),
                            train_n=len(train), budget=level, scheme=scheme,
                            preprocessing=prep, weight=weight, experiment=experiment)
                evaluate(model, validation, meta, metrics, classes, predictions, matrices)
                records.append(dict(**meta, path=str(path.relative_to(ROOT)), sha256=sha(path),
                                    fit_seconds=fit_seconds, train_max_batch=int(train.batch.max()),
                                    validation_batch=target, preprocessing_n=len(reference),
                                    preprocessing_reference='Batch1-2_anchor' if prep == 'anchor' else 'selected_Train',
                                    gamma_numeric=float(classifier._gamma),
                                    support_vectors=int(classifier.n_support_.sum()),
                                    row_overlap=0, exact_feature_overlap=0))
                for j, feature in enumerate(FEATURES):
                    prep_stats.append(dict(fold=fold, setting=setting, seed=seed, feature=feature,
                                           reference_n=len(reference), imputer=float(imputer.statistics_[j]),
                                           mean=float(scaler.mean_[j]), scale=float(scaler.scale_[j]),
                                           var=float(scaler.var_[j])))
                for gas in GASES:
                    n = int((train.gas == gas).sum())
                    weights.append(dict(fold=fold, setting=setting, seed=seed, gas_id=gas, n=n,
                                        class_weight=float(classifier.class_weight_[gas - 1]),
                                        expected_weight=len(train) / (6 * n) if weight == 'balanced' else 1.))
            print('Completed', fold, setting, '5 seeds', flush=True)
    save('historical_metrics', metrics)
    save('historical_class_metrics', classes)
    save('historical_predictions', predictions)
    save('historical_confusion', matrices)
    save('fit_records', records)
    save('preprocessing_statistics', prep_stats)
    save('class_weights', weights)
    return records


# 시드와Fold를 분리한 기술 통계 및 대응 차이 계산
def summarize_history():
    metrics = pd.read_csv(OUT / 'historical_metrics.csv')
    classes = pd.read_csv(OUT / 'historical_class_metrics.csv')
    predictions = pd.read_csv(OUT / 'historical_predictions.csv')
    pooled, pooled_classes = [], []
    for (setting, seed), sub in predictions.groupby(['setting', 'seed']):
        score, per_class, _ = measured_scores(sub.y_true, sub.y_pred)
        pooled.append(dict(setting=setting, seed=int(seed), **score))
        pooled_classes.extend(dict(setting=setting, seed=int(seed), **row) for row in per_class)
    save('historical_pooled_metrics', pooled)
    save('historical_pooled_class_metrics', pooled_classes)
    seed_summary = metrics.groupby(['setting', 'seed']).agg(
        equal_fold_macro_f1=('macro_f1', 'mean'), mean_accuracy=('accuracy', 'mean'),
        mean_weighted_f1=('weighted_f1', 'mean'), fold_sd=('macro_f1', lambda x: x.std(ddof=0)),
        toluene_recall=('toluene_recall', 'mean'), acetaldehyde_recall=('acetaldehyde_recall', 'mean'),
        min_recall=('min_class_recall', 'min'), zero_pairs=('zero_recall_classes', 'sum'),
        other_four_f1=('other_four_f1', 'mean')).reset_index()
    save('seed_summary', seed_summary)
    summary = seed_summary.groupby('setting').agg(
        mean_macro_f1=('equal_fold_macro_f1', 'mean'), seed_sd_macro_f1=('equal_fold_macro_f1', 'std'),
        mean_accuracy=('mean_accuracy', 'mean'), mean_toluene_recall=('toluene_recall', 'mean'),
        mean_acetaldehyde_recall=('acetaldehyde_recall', 'mean'), mean_other_four_f1=('other_four_f1', 'mean'),
        worst_recall=('min_recall', 'min'), zero_pairs_mean=('zero_pairs', 'mean')).reset_index()
    save('historical_summary', summary)
    save('fold_summary', metrics.groupby(['setting', 'fold', 'scope']).agg(
        train_n=('train_n', 'first'), validation_n=('n', 'first'), macro_f1_mean=('macro_f1', 'mean'),
        macro_f1_seed_sd=('macro_f1', 'std'), accuracy_mean=('accuracy', 'mean')).reset_index())
    save('class_summary', classes.groupby(['setting', 'fold', 'gas_id']).agg(
        support=('support', 'first'), precision_mean=('precision', 'mean'),
        recall_mean=('recall', 'mean'), recall_sd=('recall', 'std'), f1_mean=('f1', 'mean')).reset_index())
    comparisons = [('spread_vs_early', 'early_mid', 'spread_mid'),
                   ('recent_vs_early', 'early_mid', 'recent_mid'),
                   ('recent_vs_spread', 'spread_mid', 'recent_mid'),
                   ('size_mid_vs_small', 'spread_small', 'spread_mid'),
                   ('size_max_vs_mid', 'spread_mid', 'spread_max'),
                   ('unit_vs_balanced', 'spread_mid', 'spread_mid_unit'),
                   ('anchor_vs_native', 'spread_mid', 'spread_mid_anchor'),
                   ('anchor_unit_vs_native_unit', 'spread_mid_unit', 'spread_mid_anchor_unit')]
    paired, paired_classes, effects = [], [], []
    for name, base, treatment in comparisons:
        a = metrics[metrics.setting == base].set_index(['fold', 'seed'])
        b = metrics[metrics.setting == treatment].set_index(['fold', 'seed'])
        delta = b.macro_f1 - a.macro_f1
        seed_delta = delta.groupby('seed').mean()
        fold_delta = delta.groupby('fold').mean()
        ca = classes[classes.setting == base].set_index(['fold', 'seed', 'gas_id'])
        cb = classes[classes.setting == treatment].set_index(['fold', 'seed', 'gas_id'])
        recall_delta = (cb.recall - ca.recall).groupby('gas_id').mean()
        consistent = bool(seed_delta.mean() >= .005 and (fold_delta > 0).all() and (seed_delta > 0).sum() >= 4)
        harms = bool((recall_delta < -.05).any() or
                     (b.other_four_f1 - a.other_four_f1).mean() < -.02 or
                     (b.zero_recall_classes - a.zero_recall_classes).mean() > 0)
        for (fold, seed), value in delta.items():
            paired.append(dict(comparison=name, base=base, treatment=treatment, fold=fold, seed=seed,
                               macro_delta=float(value), n_validation=int(a.loc[(fold, seed), 'n'])))
        for gas, value in recall_delta.items():
            paired_classes.append(dict(comparison=name, gas_id=int(gas), mean_recall_delta=float(value)))
        effects.append(dict(comparison=name, base=base, treatment=treatment, mean_delta=float(seed_delta.mean()),
                            seed_sd_delta=float(seed_delta.std()), positive_seed_n=int((seed_delta > 0).sum()),
                            positive_fold_n=int((fold_delta > 0).sum()),
                            consistent_descriptive=consistent, protection_flag=harms,
                            statistical_significance_established=False))
    save('paired_effects', paired)
    save('paired_class_effects', paired_classes)
    effects = save('effect_summary', effects)
    frozen = dict(frozen_at=now(), selection='No model/seed selection; Model A remains official.',
                  historical_summary_sha256=sha(OUT / 'historical_summary.csv'),
                  historical_metrics_sha256=sha(OUT / 'historical_metrics.csv'),
                  effect_summary=effects.to_dict('records'), future_settings=FUTURE_SETTINGS,
                  future_seeds=SEEDS, future_model_fold='C')
    write_json(OUT / 'historical_findings_frozen.json', frozen)


# 선지정20개 모델만 회고적 미래 평가
def evaluate_future(frame, records):
    gate = json.loads((OUT / 'historical_findings_frozen.json').read_text(encoding='utf-8'))
    assert sha(OUT / 'historical_metrics.csv') == gate['historical_metrics_sha256']
    started = now()
    metrics, classes, predictions, matrices = [], [], [], []
    for record in records:
        if record['fold'] != 'C' or record['setting'] not in FUTURE_SETTINGS:
            continue
        assert sha(ROOT / record['path']) == record['sha256']
        model = joblib.load(ROOT / record['path'])
        for scope in ['9', '10', 'pooled']:
            sub = frame[frame.batch >= 9] if scope == 'pooled' else frame[frame.batch == int(scope)]
            meta = {key: record[key] for key in ['fold', 'setting', 'seed', 'train_n', 'budget', 'scheme', 'preprocessing', 'weight', 'experiment']}
            evaluate(model, sub, dict(**meta, scope=scope), metrics, classes, predictions, matrices)
    save('exploratory_metrics', metrics)
    save('exploratory_class_metrics', classes)
    save('exploratory_predictions', predictions)
    save('exploratory_confusion', matrices)
    write_json(OUT / 'exploratory_gate.json', dict(started_at=started,
        findings_frozen_before_evaluation=gate['frozen_at'] <= started,
        findings_sha256=sha(OUT / 'historical_findings_frozen.json'),
        evaluated_settings=FUTURE_SETTINGS, seeds=SEEDS, model_count=20,
        independent_test=False, model_selection_changed=False))


# 기존 A/B 설정·통계·예측 불변 확인
def historical_references(frame):
    config = json.loads((ROOT / 'outputs/temporal_generalization_validation/experiment_config.json').read_text(encoding='utf-8'))
    old = pd.read_csv(ROOT / 'outputs/temporal_generalization_validation/predictions_comparison.csv').set_index('row_id')
    rows, stats, weights, audits = [], [], [], []
    for name, meta in config['models'].items():
        model = joblib.load(ROOT / meta['path'])
        assert sha(ROOT / meta['path']) == meta['sha256']
        train = frame[frame.batch <= meta['train_end']]
        classifier = model.named_steps['classifier']
        scaler = model.named_steps['scaler']
        future = frame[frame.batch >= 8]
        pred = model.predict(future[FEATURES])
        np.testing.assert_array_equal(pred, old.loc[future.row_id, 'pred_' + name])
        for gas in GASES:
            weights.append(dict(model=name, gas_id=gas, train_n=int((train.gas == gas).sum()),
                                class_weight=float(classifier.class_weight_[gas - 1])))
        for j, feature in enumerate(FEATURES):
            stats.append(dict(model=name, feature=feature, mean=float(scaler.mean_[j]),
                              scale=float(scaler.scale_[j]), imputer=float(model.named_steps['imputer'].statistics_[j])))
        for scope in ['8', '9', '10', 'pooled']:
            sub = frame[frame.batch >= 9] if scope == 'pooled' else frame[frame.batch == int(scope)]
            score, _, _ = measured_scores(sub.gas, model.predict(sub[FEATURES]))
            rows.append(dict(model=name, train_n=len(train), scope=scope, **score))
        audits.append(dict(model=name, sha256=meta['sha256'], replay_n=len(future),
                           exact_prediction_match=True, gamma_numeric=float(classifier._gamma)))
    save('reference_model_metrics', rows)
    save('reference_preprocessing', stats)
    save('reference_class_weights', weights)
    save('reference_model_audit', audits)


# 고정 계획·과거 분석·미래 진단·보존 검사 순서 실행
def run():
    before = snapshot()
    frame, source = load_dataset(read_config())
    raw = dict(zip(source.file, source.sha256))
    prior = json.loads((ROOT / 'outputs/toluene_failure_deep_diagnostic/run_manifest.json').read_text(encoding='utf-8'))
    assert raw == prior['raw_hashes']
    plan = freeze(frame)
    plan_sha = sha(OUT / 'experiment_plan.json')
    with threadpool_limits(limits=2):
        records = fit_history(frame, plan)
        summarize_history()
        evaluate_future(frame, records)
        historical_references(frame)
    from .representativeness_visuals import create_visuals
    create_visuals()
    from .representativeness_report import build_report
    build_report(None)
    assert all(sha(ROOT / name) == value for name, value in before.items())
    assert all(sha(Path(read_config()['data_dir']) / name) == value for name, value in raw.items())
    assert sha(OUT / 'experiment_plan.json') == plan_sha
    write_json(OUT / 'run_manifest.json', dict(
        completed_at=now(), before=before, raw_hashes=raw, plan_sha256=plan_sha,
        classifier_fits=len(records), new_model_files=len(list(MODEL_DIR.glob('*.joblib'))),
        old_model_files=140, preprocessing_policy='90 native fits +1 shared past anchor',
        model_selection_changed=False, prior_files_unchanged=True,
        code_sha256={n: sha(ROOT / 'src' / n) for n in ['temporal_representativeness_control.py',
                     'representativeness_visuals.py', 'representativeness_report.py']},
        package_versions={n: importlib.metadata.version(n) for n in ['numpy', 'pandas', 'scikit-learn', 'joblib', 'matplotlib']},
    ))
    print(pd.read_csv(OUT / 'historical_summary.csv').to_string(index=False), flush=True)


# 기존 실패와 새 모델 목록 충돌을 구분한 최종 기록
def finalize():
    if (OUT / 'final_verification.json').exists():
        raise FileExistsError('Stage12 finalized already')
    manifest = json.loads((OUT / 'run_manifest.json').read_text(encoding='utf-8'))
    assert all(sha(ROOT / n) == value for n, value in manifest['before'].items())
    cases = ET.parse(OUT / 'test_results.xml').getroot().findall('.//testcase')
    failures = [f"{c.get('classname')}::{c.get('name')}" for c in cases
                if c.find('failure') is not None or c.find('error') is not None]
    expected = {
        'tests.test_diagnostics::test_existing_results_and_models_unchanged',
        'tests.test_models::test_eda_and_sources_preserved_report_complete',
        'tests.test_temporal_failure_diagnostics::test_no_new_fit_calls_or_new_model_files',
        'tests.test_temporal_generalization_validation::test_existing_files_raw_and_model_inventory_preserved',
        'tests.test_toluene_deep_diagnostic::test_preserved_files_raw_models_and_config',
    }
    assert set(failures) == expected, failures
    new = [c for c in cases if c.get('classname', '').endswith('test_temporal_representativeness_control')]
    status = dict(passed=len(cases) - len(failures), failed=len(failures),
                  prior_failures=3, additional_inventory_conflicts=2,
                  failed_tests=failures, new_tests=len(new), new_failures=0)
    from .representativeness_report import build_report
    build_report(status)
    write_json(OUT / 'final_verification.json', dict(
        completed_at=now(), test_status=status, prior_files_unchanged=len(manifest['before']),
        raw_files_unchanged=10, old_models_unchanged=140, new_model_files=120,
        official_main_candidate='Model A', model_selection_changed=False,
        report_sha256={name: sha(ROOT / 'reports' / name) for name in REPORTS}))
    print('FINAL', status, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--finalize', action='store_true')
    args = parser.parse_args()
    try:
        finalize() if args.finalize else run()
    except Exception:
        logging.exception('Stage12 control failed')
        raise
