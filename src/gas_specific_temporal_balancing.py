# 가스별 시기 구성의 균형 성능과 보호 기준 검증
# 기존 모델 재사용 및 조건부 확대 후 사전 지정 회고적 평가

import hashlib
import json
import time

import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from .data import ROOT, FEATURES, GASES
from .temporal_expansion import now, sha, write_json
from .temporal_representativeness_control import FOLDS, SEEDS, allocate, evaluate

OUT = ROOT / 'outputs/gas_specific_temporal_balancing'
MODEL_DIR = ROOT / 'models/gas_specific_temporal_balancing'
OLD = ROOT / 'outputs/temporal_representativeness_control'
MID_SETTINGS = ['spread_mid', 'recent_mid', 'mixed_mid', 'coverage_mid']
MAX_CANDIDATES = ['mixed_max', 'coverage_max']


# 실험 표 저장
def save(name, rows):
    table = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    table.to_csv(OUT / f'{name}.csv', index=False, encoding='utf-8')
    return table


# 기존 코드·모델·보고서·결과 지문 수집


# 실제 존재하는 Batch에 최소 대표 수 배정 후 최근순으로 채움
def coverage_allocate(available, total):
    available = {int(b): int(n) for b, n in sorted(available.items()) if n > 0}
    minimum = max(1, total // (2 * len(available)))
    result = {b: min(n, minimum) for b, n in available.items()}
    assert sum(result.values()) <= total <= sum(available.values())
    remaining = total - sum(result.values())
    for batch in sorted(available, reverse=True):
        n = min(available[batch] - result[batch], remaining)
        result[batch] += n
        remaining -= n
    assert remaining == 0
    return result


# Train의 가스별 시기 집중도로 전략 선택
def gas_rule(frame, end, gas, scheme):
    counts = frame[(frame.batch <= end) & (frame.gas == gas)].groupby('batch').size()
    largest_share = float(counts.max() / counts.sum())
    chosen = ('spread' if largest_share >= .5 else 'recent') if scheme == 'mixed' else scheme
    return chosen, largest_share, counts.to_dict()


# 가스별 배분과 고정 셀 순열로 부분표본 선택
def sample_rows(frame, end, scheme, gas_budget, seed):
    selected, rules = [], []
    for gas, count in gas_budget.items():
        chosen, concentration, available = gas_rule(frame, end, gas, scheme)
        allocation = coverage_allocate(available, count) if chosen == 'coverage' else allocate(available, count, chosen)
        for batch, n in allocation.items():
            ids = frame.index[(frame.batch == batch) & (frame.gas == gas)].to_numpy()
            rng = np.random.default_rng(np.random.SeedSequence([seed, gas, batch]))
            selected.extend(rng.permutation(ids)[:n].tolist())
        rules.append(dict(gas_id=gas, chosen=chosen, largest_batch_share=concentration,
                          observed_batches=len(available), allocated_batches=sum(n > 0 for n in allocation.values())))
    return np.array(sorted(selected), dtype=int), rules


# 학습 행 순서·설정·시드가 같은 모델만 재사용
def signature(row_ids, seed):
    payload = json.dumps(dict(rows=list(row_ids), seed=int(seed), C=1., gamma='scale',
                              kernel='rbf', weight='balanced', preprocessing='median_standard',
                              features=FEATURES), sort_keys=True).encode('utf-8')
    return hashlib.sha256(payload).hexdigest()


# 평가 전에 모든 가능한 표본·확대 규칙·판정 기준 고정


# 기존 모델의 정확한 학습 표본 서명 목록 구성
def old_cache():
    records = pd.read_csv(OLD / 'fit_records.csv')
    assignments = pd.read_csv(OLD / 'sample_assignments.csv')
    cache = {}
    for row in records[records.setting.isin(['spread_mid', 'recent_mid', 'spread_max'])].itertuples():
        sub = assignments[(assignments.fold == row.fold) & (assignments.setting == row.setting) &
                          (assignments.seed == row.seed)]
        assert sha(ROOT / row.path) == row.sha256
        cache[signature(sub.row_id.tolist(), row.seed)] = dict(path=row.path, sha256=row.sha256,
            source_stage=12, source_setting=row.setting, source_fold=row.fold)
    return cache


# 중복 학습 없이 실행 구성 평가
def execute(frame, settings, cache, records, metrics, classes, predictions, matrices):
    samples = pd.read_csv(OUT / 'planned_sample_assignments.csv')
    indexed = frame.set_index('row_id', drop=False)
    for fold, (end, target) in FOLDS.items():
        validation = frame[frame.batch == target]
        for setting in settings:
            for seed in SEEDS:
                sub = samples[(samples.fold == fold) & (samples.setting == setting) & (samples.seed == seed)]
                train = indexed.loc[sub.row_id]
                assert train.batch.max() < target and set(train.row_id).isdisjoint(validation.row_id)
                assert set(pd.util.hash_pandas_object(train[FEATURES], index=False)).isdisjoint(
                    pd.util.hash_pandas_object(validation[FEATURES], index=False))
                key = signature(train.row_id.tolist(), seed)
                new_fit = key not in cache
                started = time.perf_counter()
                if new_fit:
                    model = Pipeline([
                        ('imputer', SimpleImputer(strategy='median')),
                        ('scaler', StandardScaler()),
                        ('classifier', SVC(C=1., gamma='scale', kernel='rbf', class_weight='balanced',
                                           random_state=seed, cache_size=256)),
                    ])
                    fit_started = now()
                    model.fit(train[FEATURES], train.gas.to_numpy())
                    fit_seconds = time.perf_counter() - started
                    path = MODEL_DIR / f'{fold}_{setting}_seed{seed}.joblib'
                    joblib.dump(model, path)
                    cache[key] = dict(path=str(path.relative_to(ROOT)), sha256=sha(path),
                                      source_stage=13, source_setting=setting, source_fold=fold)
                else:
                    fit_started, fit_seconds = None, 0.
                    assert sha(ROOT / cache[key]['path']) == cache[key]['sha256']
                    model = joblib.load(ROOT / cache[key]['path'])
                classifier = model.named_steps['classifier']
                scaler = model.named_steps['scaler']
                assert classifier.C == 1 and classifier.gamma == 'scale' and classifier.class_weight == 'balanced'
                assert list(model.feature_names_in_) == FEATURES
                np.testing.assert_array_equal(model.classes_, list(GASES))
                np.testing.assert_allclose(scaler.mean_, train[FEATURES].mean(), atol=1e-10)
                np.testing.assert_allclose(scaler.var_, train[FEATURES].var(ddof=0), rtol=1e-9)
                np.testing.assert_allclose(model.named_steps['imputer'].statistics_, train[FEATURES].median())
                expected_weights = len(train) / (6 * train.gas.value_counts().sort_index().to_numpy())
                np.testing.assert_allclose(classifier.class_weight_, expected_weights)
                meta = dict(fold=fold, setting=setting, seed=seed, scope=str(target), train_n=len(train))
                evaluate(model, validation, meta, metrics, classes, predictions, matrices)
                records.append(dict(**meta, **cache[key], signature=key, new_fit=new_fit,
                    fit_started_at=fit_started, fit_seconds=fit_seconds, train_max_batch=int(train.batch.max()),
                    preprocessing_n=int(scaler.n_samples_seen_), gamma_numeric=float(classifier._gamma),
                    row_overlap=0, exact_feature_overlap=0))
            print('Evaluated', fold, setting, 'five seeds', flush=True)


# Fold와시드 평균 및 가스별 보호 기준 판정
def summarize(metrics, classes, phase, baseline='spread_mid'):
    metric = pd.DataFrame(metrics)
    per_class = pd.DataFrame(classes)
    seeds = metric.groupby(['setting', 'seed']).agg(
        equal_fold_macro_f1=('macro_f1', 'mean'), mean_accuracy=('accuracy', 'mean'),
        mean_weighted_f1=('weighted_f1', 'mean'), mean_toluene_recall=('toluene_recall', 'mean'),
        mean_acetaldehyde_recall=('acetaldehyde_recall', 'mean'), other_four_f1=('other_four_f1', 'mean'),
        worst_recall=('min_class_recall', 'min')).reset_index()
    zero = per_class.groupby(['setting', 'seed']).recall.agg(lambda x: int((x == 0).sum())).reset_index(name='zero_pairs')
    seeds = seeds.merge(zero, on=['setting', 'seed'])
    summary = seeds.groupby('setting').agg(
        mean_macro_f1=('equal_fold_macro_f1', 'mean'), seed_sd_macro_f1=('equal_fold_macro_f1', 'std'),
        mean_accuracy=('mean_accuracy', 'mean'), mean_weighted_f1=('mean_weighted_f1', 'mean'),
        toluene_recall=('mean_toluene_recall', 'mean'), acetaldehyde_recall=('mean_acetaldehyde_recall', 'mean'),
        other_four_f1=('other_four_f1', 'mean'), worst_recall=('worst_recall', 'min'),
        zero_pairs_mean=('zero_pairs', 'mean')).reset_index()
    guards, changes, pairs = [], [], []
    base = metric[metric.setting == baseline].set_index(['fold', 'seed'])
    base_class = per_class[per_class.setting == baseline].set_index(['fold', 'seed', 'gas_id'])
    for setting in summary.setting:
        target = metric[metric.setting == setting].set_index(['fold', 'seed'])
        delta = target.macro_f1 - base.macro_f1
        fold_delta, seed_delta = delta.groupby('fold').mean(), delta.groupby('seed').mean()
        target_class = per_class[per_class.setting == setting].set_index(['fold', 'seed', 'gas_id'])
        recall_delta = (target_class.recall - base_class.recall).groupby('gas_id').mean()
        for gas, value in recall_delta.items():
            changes.append(dict(setting=setting, gas_id=int(gas), mean_recall_delta=float(value)))
        for (fold, seed), value in delta.items():
            pairs.append(dict(setting=setting, fold=fold, seed=int(seed), macro_delta=float(value)))
        focus_guard = bool((recall_delta.loc[[4, 6]] > -.05).all())
        other_guard = bool((recall_delta.loc[[1, 2, 3, 5]] > -.10).all())
        macro_guard = bool(seed_delta.mean() >= .005)
        fold_guard = bool((fold_delta >= -1e-12).all() and (fold_delta > 1e-12).sum() >= 2)
        seed_guard = bool((seed_delta > 1e-12).all())
        success = macro_guard and focus_guard and other_guard and fold_guard and seed_guard
        expand = macro_guard and focus_guard and other_guard and (fold_delta > 1e-12).sum() >= 2 and (seed_delta > 1e-12).sum() >= 4
        any_gain = bool(seed_delta.mean() >= .005 or (recall_delta >= .02).any())
        conclusion = 'A' if success else ('B' if any_gain else 'C')
        guards.append(dict(setting=setting, baseline=baseline, mean_macro_delta=float(seed_delta.mean()),
            paired_seed_sd=float(seed_delta.std()), positive_fold_n=int((fold_delta > 1e-12).sum()),
            neutral_fold_n=int((fold_delta.abs() <= 1e-12).sum()), positive_seed_n=int((seed_delta > 1e-12).sum()),
            toluene_delta=float(recall_delta.loc[6]), acetaldehyde_delta=float(recall_delta.loc[4]),
            macro_guard=macro_guard, focus_guard=focus_guard, other_guard=other_guard,
            fold_guard=fold_guard, seed_guard=seed_guard, balanced_success=bool(success),
            expansion_eligible=bool(expand), conclusion=conclusion))
    save(f'{phase}_seed_summary', seeds)
    save(f'{phase}_summary', summary)
    guards = save(f'{phase}_guards', guards)
    save(f'{phase}_class_deltas', changes)
    save(f'{phase}_paired_deltas', pairs)
    return guards


# 843개 결과로 사전 지정한 두 확대 대상만 판정
def expansion_gate(guards):
    rows = []
    for setting in MAX_CANDIDATES:
        mid = setting.replace('_max', '_mid')
        row = guards[guards.setting == mid].iloc[0]
        rows.append(dict(setting=setting, mid_parent=mid, execute=bool(row.expansion_eligible),
                         reason='Predeclared plausibility guards passed' if row.expansion_eligible else
                         'Predeclared plausibility guards not all satisfied; no replacement'))
    gate = dict(frozen_at=now(), decisions=rows, mid_guards_sha256=sha(OUT / 'mid_guards.csv'),
                candidate_selection=False, independent_validation=False)
    write_json(OUT / 'expansion_decision.json', gate)
    return [row['setting'] for row in rows if row['execute']]


# 실행 여부를 유지한 예산 확대 대응 비교
def size_comparisons(metrics, classes):
    metric = pd.DataFrame(metrics)
    per_class = pd.DataFrame(classes)
    rows, changes = [], []
    for scheme in ['spread', 'mixed', 'coverage']:
        mid, large = scheme + '_mid', scheme + '_max'
        executed = large in set(metric.setting)
        row = dict(scheme=scheme, mid_n=843, max_n=1689, executed=executed,
                   macro_delta=np.nan, positive_fold_n=np.nan, positive_seed_n=np.nan,
                   toluene_recall_delta=np.nan, acetaldehyde_recall_delta=np.nan)
        if executed:
            a = metric[metric.setting == mid].set_index(['fold', 'seed'])
            b = metric[metric.setting == large].set_index(['fold', 'seed'])
            delta = b.macro_f1 - a.macro_f1
            row.update(macro_delta=float(delta.mean()),
                       positive_fold_n=int((delta.groupby('fold').mean() > 0).sum()),
                       positive_seed_n=int((delta.groupby('seed').mean() > 0).sum()),
                       toluene_recall_delta=float((b.toluene_recall - a.toluene_recall).mean()),
                       acetaldehyde_recall_delta=float((b.acetaldehyde_recall - a.acetaldehyde_recall).mean()))
            ca = per_class[per_class.setting == mid].groupby('gas_id').recall.mean()
            cb = per_class[per_class.setting == large].groupby('gas_id').recall.mean()
            changes.extend(dict(scheme=scheme, gas_id=int(gas), recall_delta=float(value))
                           for gas, value in (cb - ca).items())
        rows.append(row)
    save('size_comparisons', rows)
    save('size_class_deltas', changes)


# 회고적 평가 전에 연구 결론 고정


# 선지정한843개4구성만 과거 분석 동결 후 회고적 평가


# 기존 기준 예측·Model A/B 불변 대조
def replay_checks(frame, predictions):
    pred = pd.DataFrame(predictions)
    prior = pd.read_csv(OLD / 'historical_predictions.csv')
    rows = []
    for setting in ['spread_mid', 'recent_mid', 'spread_max']:
        for fold in FOLDS:
            for seed in SEEDS:
                a = pred[(pred.setting == setting) & (pred.fold == fold) & (pred.seed == seed)].set_index('row_id').y_pred
                b = prior[(prior.setting == setting) & (prior.fold == fold) & (prior.seed == seed)].set_index('row_id').y_pred
                np.testing.assert_array_equal(a.loc[b.index], b)
                rows.append(dict(model=setting, fold=fold, seed=seed, n=len(a), exact_match=True))
    config = json.loads((ROOT / 'outputs/temporal_generalization_validation/experiment_config.json').read_text(encoding='utf-8'))
    old = pd.read_csv(ROOT / 'outputs/temporal_generalization_validation/predictions_comparison.csv').set_index('row_id')
    for name, meta in config['models'].items():
        assert sha(ROOT / meta['path']) == meta['sha256']
        model = joblib.load(ROOT / meta['path'])
        sub = frame[frame.batch >= 8]
        np.testing.assert_array_equal(model.predict(sub[FEATURES]), old.loc[sub.row_id, 'pred_' + name])
        rows.append(dict(model='Model_' + name, fold='reference', seed=42, n=len(sub), exact_match=True))
    save('replay_checks', rows)


# 고정 계획·재사용·조건부 확대·회고적 평가 순서 실행


# 전체 테스트와 기존 실패 범주를 분리하여 최종 확정


