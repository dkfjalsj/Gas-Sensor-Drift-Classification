# 가스별 시기 구성의 균형 성능과 보호 기준 검증
# 기존 모델 재사용 및 조건부 확대 후 사전 지정 회고적 평가

import argparse
import hashlib
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
from .temporal_expansion import now, sha, write_json, measured_scores
from .temporal_representativeness_control import FOLDS, SEEDS, budgets, allocate, evaluate

OUT = ROOT / 'outputs/gas_specific_temporal_balancing'
MODEL_DIR = ROOT / 'models/gas_specific_temporal_balancing'
OLD = ROOT / 'outputs/temporal_representativeness_control'
MID_SETTINGS = ['spread_mid', 'recent_mid', 'mixed_mid', 'coverage_mid']
MAX_CANDIDATES = ['mixed_max', 'coverage_max']
REPORTS = ['gas_specific_temporal_balancing_report.html',
           'gas_specific_temporal_balancing_summary.md',
           'gas_specific_temporal_balancing_limitations.md']


# 실험 표 저장
def save(name, rows):
    table = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    table.to_csv(OUT / f'{name}.csv', index=False, encoding='utf-8')
    return table


# 기존 코드·모델·보고서·결과 지문 수집
def snapshot():
    files = [p for folder in ['src', 'tests', 'models', 'reports', 'outputs']
             for p in (ROOT / folder).rglob('*') if p.is_file()
             and '__pycache__' not in p.parts and OUT not in p.parents
             and MODEL_DIR not in p.parents]
    files += [ROOT / name for name in ['config.json', 'training_config.json',
                                      'README.md', 'requirements.txt',
                                      'requirements-lock.txt', '.gitignore']]
    return {str(p.relative_to(ROOT)): sha(p) for p in files}


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
def freeze(frame):
    if OUT.exists() or MODEL_DIR.exists() or any((ROOT / 'reports' / n).exists() for n in REPORTS):
        raise FileExistsError('Stage13 output already exists')
    OUT.mkdir(parents=True)
    MODEL_DIR.mkdir(parents=True)
    budget = {k: v for k, v in budgets(frame).items() if k in ['mid', 'max']}
    plan = dict(
        frozen_at=now(), folds=FOLDS, seeds=SEEDS, budgets=budget,
        mid_settings=MID_SETTINGS, max_candidates=MAX_CANDIDATES,
        baseline_max='spread_max: reuse stage12',
        mixed='Per gas, largest actual Train Batch share >=0.50 -> spread; otherwise recent. '
        'Threshold fixed before new evaluation, no gas identity or Batch9/10 score rule.',
        coverage='For q gas rows over m observed Train batches, reserve '
        'min(cell_capacity,max(1,floor(q/(2m)))) in every observed cell, '
        'then fill remaining budget greedily from newest batches. No nonexistent cells.',
        sampling='Same SeedSequence(seed,gas,Batch) prefixes as stage12; fixed row order.',
        primary='Mean of3 Fold Macro F1, then mean across5 seeds; SD across seed means(ddof1).',
        balance='Mean Macro F1 delta vs spread_mid >=0.005; Toluene/Acetaldehyde '
        'mean Recall delta >-0.05; each of other4 gas mean Recall delta >-0.10; '
        'all Fold mean deltas >=0 (tolerance1e-12), >=2 strictly positive; '
        'all5 seed equal-Fold mean deltas >0. Identical subsets count as neutral, '
        'never artificially perturbed. Rules descriptive, not safety/significance standards.',
        expansion='Only prespecified mixed/coverage are eligible for1689: '
        '843 mean Macro delta>=0.005, all Recall guards, >=2 positive Fold means '
        'and >=4 positive seed means. At most2 targets, all3Folds/all5seeds. '
        'Always reuse spread_max reference. Expanded strategies are additionally '
        'judged against equal-size spread_max; same Validation reused, not independent. '
        'No after-result substitution.',
        conclusion='A if a new strategy satisfies full balance; B if Macro gain>=0.005 '
        'or any mean gas Recall gain>=0.02 exists but loss/inconsistency remains; otherwise C. '
        'No official model replacement or seed winner.',
        svm=dict(C=1., gamma='scale', kernel='rbf', class_weight='balanced', features=128,
                 imputer='median', scaler='StandardScaler_selected_Train_only'),
        maximum_new_fits=55, expected_mid_new_fits=25,
        reuse='Stage12 stored models for exact matching rows/order,settings,seed. '
        'All new fits only under models/gas_specific_temporal_balancing.',
        future_settings=MID_SETTINGS, future_fold='C', future_seeds=SEEDS,
        future='After all historical and expansion findings are frozen, evaluate '
        'only four843 strategies x5seeds (20 logical models), Batch9/10 and pooled. '
        'No expansion models in future evaluation, no reselection, new independent Test absent.',
        limitations='Historical windows and seeds overlap; five seeds quantify subset '
        'randomness, not independent temporal replication. Research motivated by already '
        'seen9/10; no future-independent or fully causal claim.',
        official_model='Model A unchanged', independent_test=False,
    )
    write_json(OUT / 'experiment_plan.json', plan)
    samples, composition, rule_rows = [], [], []
    for fold, (end, target) in FOLDS.items():
        for setting in [*MID_SETTINGS, 'spread_max', *MAX_CANDIDATES]:
            scheme, level = setting.rsplit('_', 1)
            for seed in SEEDS:
                ids, rules = sample_rows(frame, end, scheme, budget[level], seed)
                sub = frame.loc[ids]
                assert len(sub) == sub.row_id.nunique() == sum(budget[level].values())
                assert sub.groupby('gas').size().to_dict() == budget[level]
                assert sub.batch.max() < target
                for row in sub.itertuples():
                    samples.append(dict(fold=fold, setting=setting, seed=seed,
                                        row_id=row.row_id, batch=row.batch, gas_id=row.gas))
                for rule in rules:
                    rule_rows.append(dict(fold=fold, setting=setting, seed=seed, **rule))
                for gas in GASES:
                    for batch in range(1, end + 1):
                        composition.append(dict(fold=fold, setting=setting, seed=seed, gas_id=gas, batch=batch,
                            n=int(((sub.batch == batch) & (sub.gas == gas)).sum()),
                            available=int(((frame.batch == batch) & (frame.gas == gas)).sum()), total_n=len(sub)))
    save('planned_sample_assignments', samples)
    save('planned_sample_composition', composition)
    save('train_only_strategy_rules', rule_rows)
    plan['samples_sha256'] = sha(OUT / 'planned_sample_assignments.csv')
    plan['composition_sha256'] = sha(OUT / 'planned_sample_composition.csv')
    write_json(OUT / 'experiment_plan.json', plan)
    (OUT / 'protocol.md').write_text('''# 13단계 사전 계획

모든 조건·시드는신규평가전에고정. Model A 유지. 독립Test없음.
Fold1–3→6 /1–6→7 /1–7→8, 시드11·23·42·67·101.
843개 가스별127/216/91/69/301/39개, 확대1689개254/432/183/139/602/79개.

분산/최근은12단계와같음. 혼합형은Train의한Batch집중도50%이상이면분산,아니면최근.
최소대표형은가스q개·관측m개Batch마다min(실제수,max(1,q//(2m)))개보장후최근순채움.
가스ID에따른수동전략·미래점수에따른비율조정없음. 동일구성이되면동일하다고기록.

균형판정: Macro F1 평균+0.5pp이상, 집중2가스Recall손실5pp미만,
다른각가스손실10pp미만,3Fold평균비음수(최소2양수),5시드평균모두양수.
동일Fold표본은중립0으로처리. 연구용기술기준이며통계적유의성/안전기준아님.

확대대상은혼합/최소대표최대2개로사전지정. 843개에서평균+0.5pp·Recall보호충족·
Fold2개이상/시드4개이상양수일때만전체3Fold5시드확대.
분산1689는기존모델재사용대조. 확대평가도같은개발Validation재사용이며독립검증아님.

동일학습행순서·설정·시드면12단계모델참조. 신규학습최대55회,843개신규25회예상.
과거및확대결과를먼저고정한뒤、843개4구성×5시드만9–10회고적진단.
사후최고조건/시드/Model A교체없음. Recall0·전체클래스손실모두공개.
'''.replace('뒤、', '뒤 '), encoding='utf-8')
    return plan


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
def freeze_research_conclusion(mid, maximum):
    new_mid = mid[mid.setting.isin(['mixed_mid', 'coverage_mid'])]
    new_max = maximum[maximum.setting.isin(['mixed_max', 'coverage_max'])]
    if new_mid.balanced_success.any() or (len(new_max) and new_max.balanced_success.any()):
        conclusion = 'A — 균형 개선 근거 관찰'
    elif new_mid.conclusion.eq('B').any() or (len(new_max) and new_max.conclusion.eq('B').any()):
        conclusion = 'B — 부분 개선'
    else:
        conclusion = 'C — 개선 근거 부족'
    write_json(OUT / 'research_conclusion_frozen.json', dict(
        frozen_at=now(), conclusion=conclusion, based_on='Past Fold guards only; max budget matched',
        mid_guards_sha256=sha(OUT / 'mid_guards.csv'),
        max_guards_sha256=sha(OUT / 'max_matched_guards.csv'),
        official_model_changed=False, independent_generalization_proven=False))


# 선지정한843개4구성만 과거 분석 동결 후 회고적 평가
def future_evaluation(frame, records):
    frozen = dict(frozen_at=now(), settings=MID_SETTINGS, seeds=SEEDS,
        historical_metrics_sha256=sha(OUT / 'historical_metrics.csv'),
        guards_sha256=sha(OUT / 'all_guards.csv'),
        max_matched_guards_sha256=sha(OUT / 'max_matched_guards.csv'),
        research_conclusion_sha256=sha(OUT / 'research_conclusion_frozen.json'),
        expansion_decision_sha256=sha(OUT / 'expansion_decision.json'),
        official_model='Model A unchanged', no_reselection=True)
    write_json(OUT / 'historical_findings_frozen.json', frozen)
    started = now()
    metrics, classes, predictions, matrices = [], [], [], []
    for record in records:
        if record['fold'] != 'C' or record['setting'] not in MID_SETTINGS:
            continue
        model = joblib.load(ROOT / record['path'])
        for scope in ['9', '10', 'pooled']:
            sub = frame[frame.batch >= 9] if scope == 'pooled' else frame[frame.batch == int(scope)]
            meta = {key: record[key] for key in ['fold', 'setting', 'seed', 'train_n']}
            evaluate(model, sub, dict(**meta, scope=scope), metrics, classes, predictions, matrices)
    save('exploratory_metrics', metrics)
    save('exploratory_class_metrics', classes)
    save('exploratory_predictions', predictions)
    save('exploratory_confusion', matrices)
    write_json(OUT / 'exploratory_gate.json', dict(started_at=started,
        historical_frozen_before_evaluation=frozen['frozen_at'] <= started,
        frozen_sha256=sha(OUT / 'historical_findings_frozen.json'),
        settings=MID_SETTINGS, seeds=SEEDS, logical_model_count=20,
        independent_test=False, official_model_changed=False))


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
def run():
    before = snapshot()
    frame, source = load_dataset(read_config())
    raw = dict(zip(source.file, source.sha256))
    prior = json.loads((OLD / 'run_manifest.json').read_text(encoding='utf-8'))
    assert raw == prior['raw_hashes']
    plan = freeze(frame)
    plan_sha = sha(OUT / 'experiment_plan.json')
    cache = old_cache()
    records, metrics, classes, predictions, matrices = [], [], [], [], []
    with threadpool_limits(limits=2):
        execute(frame, MID_SETTINGS, cache, records, metrics, classes, predictions, matrices)
        guards = summarize(metrics, classes, 'mid')
        expanded = expansion_gate(guards)
        execute(frame, ['spread_max', *expanded], cache, records, metrics, classes, predictions, matrices)
        save('historical_metrics', metrics)
        save('historical_class_metrics', classes)
        save('historical_predictions', predictions)
        save('historical_confusion', matrices)
        save('model_registry', records)
        summarize(metrics, classes, 'all')
        max_guards = summarize([r for r in metrics if r['setting'].endswith('_max')],
                               [r for r in classes if r['setting'].endswith('_max')],
                               'max_matched', baseline='spread_max')
        freeze_research_conclusion(guards, max_guards)
        size_comparisons(metrics, classes)
        replay_checks(frame, predictions)
        future_evaluation(frame, records)
    samples = pd.read_csv(OUT / 'planned_sample_assignments.csv')
    composition = pd.read_csv(OUT / 'planned_sample_composition.csv')
    executed = set(pd.DataFrame(records).setting)
    save('executed_sample_assignments', samples[samples.setting.isin(executed)])
    save('executed_sample_composition', composition[composition.setting.isin(executed)])
    aliases = []
    for (fold, seed), sub in samples.groupby(['fold', 'seed']):
        baseline = set(sub[sub.setting == 'spread_mid'].row_id)
        recent = set(sub[sub.setting == 'recent_mid'].row_id)
        for setting in MID_SETTINGS:
            ids = set(sub[sub.setting == setting].row_id)
            aliases.append(dict(fold=fold, seed=seed, setting=setting,
                                same_as_spread=ids == baseline, same_as_recent=ids == recent))
    save('identical_subset_checks', aliases)
    from .gas_balancing_visuals import create_visuals
    create_visuals()
    from .gas_balancing_report import build_report
    build_report(None)
    assert all(sha(ROOT / n) == value for n, value in before.items())
    assert all(sha(Path(read_config()['data_dir']) / n) == value for n, value in raw.items())
    assert sha(OUT / 'experiment_plan.json') == plan_sha
    count = sum(row['new_fit'] for row in records)
    assert count <= 55 and count == len(list(MODEL_DIR.glob('*.joblib')))
    write_json(OUT / 'run_manifest.json', dict(completed_at=now(), before=before, raw_hashes=raw,
        plan_sha256=plan_sha, logical_model_evaluations=len(records), new_classifier_fits=count,
        reused_evaluations=len(records) - count, old_model_files=260, new_model_files=count,
        expanded_settings=expanded, official_model_changed=False,
        code_sha256={name: sha(ROOT / 'src' / name) for name in [
            'gas_specific_temporal_balancing.py', 'gas_balancing_visuals.py', 'gas_balancing_report.py']},
        package_versions={name: importlib.metadata.version(name) for name in ['numpy', 'pandas', 'scikit-learn', 'matplotlib', 'joblib']}))
    print(pd.read_csv(OUT / 'mid_summary.csv').to_string(index=False), flush=True)
    print('Expansion', expanded, 'new fits', count, flush=True)


# 전체 테스트와 기존 실패 범주를 분리하여 최종 확정
def finalize():
    if (OUT / 'final_verification.json').exists():
        raise FileExistsError('Stage13 finalized already')
    manifest = json.loads((OUT / 'run_manifest.json').read_text(encoding='utf-8'))
    assert all(sha(ROOT / n) == value for n, value in manifest['before'].items())
    cases = ET.parse(OUT / 'test_results.xml').getroot().findall('.//testcase')
    failures = [f"{c.get('classname')}::{c.get('name')}" for c in cases
                if c.find('failure') is not None or c.find('error') is not None]
    prior = json.loads((OLD / 'final_verification.json').read_text(encoding='utf-8'))['test_status']
    assert set(failures) == set(prior['failed_tests']), failures
    new = [c for c in cases if c.get('classname', '').endswith('test_gas_specific_temporal_balancing')]
    status = dict(passed=len(cases) - len(failures), failed=len(failures),
        prior_legacy_failures=3, prior_inventory_conflicts=2, new_failures=0,
        new_tests=len(new), failed_tests=failures)
    from .gas_balancing_report import build_report
    build_report(status)
    write_json(OUT / 'final_verification.json', dict(completed_at=now(), test_status=status,
        prior_files_unchanged=len(manifest['before']), old_models_unchanged=260,
        raw_files_unchanged=10, new_classifier_fits=manifest['new_classifier_fits'],
        official_model='Model A unchanged', report_sha256={name: sha(ROOT / 'reports' / name) for name in REPORTS}))
    print('FINAL', status, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--finalize', action='store_true')
    args = parser.parse_args()
    try:
        finalize() if args.finalize else run()
    except Exception:
        logging.exception('Stage13 balancing failed')
        raise
