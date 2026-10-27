# 과거 Test를 제외한 시간순 자료로 소규모 개선 실험 수행
# Validation으로만 후보 선택 후 탐색적 Test 평가

import argparse
import copy
import hashlib
import importlib.metadata
import json
import logging
import time
import warnings
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.svm import SVC
from threadpoolctl import threadpool_limits

from .data import ROOT, FEATURES, GASES, load_dataset, read_config
from .train_models import evaluate

OUT = ROOT / 'outputs' / 'model_improvement'
MODELS = ROOT / 'models' / 'improvement_strict'
FAMILIES = ['LogisticRegression', 'RandomForest', 'SVM_RBF']
ABBR = dict(zip(FAMILIES, ['LR', 'RF', 'SVM']))
SEED = 42


# 파일 해시 및 서울 시각 기록
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def now():
    return datetime.now(ZoneInfo('Asia/Seoul')).isoformat()


def write_json(path, content):
    Path(path).write_text(
        json.dumps(content, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8'
    )


# 모든 과거 Test 표본을 새 Train·Validation에서 제외
def strict_split(frame, historical):
    excluded = set(historical.loc[historical.partition == 'test', 'row_id'])
    train = frame.index[(frame.batch == 1) & ~frame.row_id.isin(excluded)].to_numpy()
    validation = frame.index[(frame.batch == 2) & ~frame.row_id.isin(excluded)].to_numpy()
    test = frame.index[frame.batch >= 3].to_numpy()
    parts = {'train': train, 'validation': validation, 'test': test}
    hashes = pd.util.hash_pandas_object(frame[FEATURES], index=False)
    for name in ['train', 'validation']:
        if set(frame.iloc[parts[name]].row_id) & excluded:
            raise ValueError('Historical Test entered development data')
        if set(frame.iloc[parts[name]].gas) != set(GASES):
            raise ValueError('Missing development gas class')
    for a, b in [('train', 'validation'), ('train', 'test'), ('validation', 'test')]:
        if set(parts[a]) & set(parts[b]) or set(hashes.iloc[parts[a]]) & set(hashes.iloc[parts[b]]):
            raise ValueError('Row or exact-feature overlap')
    if not (frame.batch.iloc[train].max() < frame.batch.iloc[validation].min()
            < frame.batch.iloc[test].min()):
        raise ValueError('Invalid chronological order')
    manifest = frame[['row_id', 'batch', 'gas']].copy()
    manifest['partition'] = 'excluded_historical_test'
    for name, indices in parts.items():
        manifest.loc[indices, 'partition'] = name
    manifest['historical_test'] = manifest.row_id.isin(excluded)
    return parts, manifest


# 결과 확인 전에 실험 규칙과 표본 목록 저장
def freeze_plan(frame, historical):
    if OUT.exists() or MODELS.exists():
        raise FileExistsError('Improvement paths already exist; refusing overwrite')
    OUT.mkdir(parents=True)
    MODELS.mkdir(parents=True)
    parts, assignments = strict_split(frame, historical)
    assignments.to_csv(OUT / 'split_assignments.csv', index=False, encoding='utf-8')
    counts = assignments.groupby(['partition', 'batch', 'gas']).size().rename('n').reset_index()
    counts.to_csv(OUT / 'split_class_counts.csv', index=False, encoding='utf-8')
    plan = dict(
        frozen_at_seoul=now(), policy='strict historical Test exclusion; user explicitly confirmed',
        train_batch=1, validation_batch=2, exploratory_test_batches=list(range(3, 11)),
        train_n=len(parts['train']), validation_n=len(parts['validation']), test_n=len(parts['test']),
        train_toluene_n=int((frame.iloc[parts['train']].gas == 6).sum()),
        validation_toluene_n=int((frame.iloc[parts['validation']].gas == 6).sum()),
        historical_test_union_n=int(historical.loc[historical.partition == 'test', 'row_id'].nunique()),
        split_sha256=sha(OUT / 'split_assignments.csv'), random_state=SEED,
        max_new_fits=14, initial_trials=8, additional_trials=6,
        initial_variants='LR/SVM: standard-none, standard-balanced, robust-none; RF: none, balanced',
        tuning='Per-family initial Validation winner fixes scaler/weight; LR C=.1/10; '
               'RF trees=200 or depth=12,leaf=3; SVM C=10 or gamma=.001',
        ranking='Exclude non-Toluene mean F1 drop > .03 vs strict family baseline. '
                'Within .01 macro-F1 of eligible best, prefer Toluene F1, recall, '
                'other-five F1, macro-F1, then fixed trial order.',
        finalists='One Validation-selected representative per family retained jointly: only 4 Validation Toluene.',
        priority='Highest representative Validation macro-F1, then Toluene F1; exploratory priority only.',
        stability='Validation is one Batch: stability unavailable for selection. Test SD descriptive only.',
        refit_on_validation=False, pca_or_feature_selection=False,
        expansion='No new expanded-Batch fitting: impossible under strict historical Test exclusion. '
                  'Frozen original B_early vs B_history comparison only.',
        evaluation='Exploratory; all existing Test periods already observed in prior stages.',
    )
    write_json(OUT / 'experiment_plan.json', plan)
    text = '''# 5단계 사전 고정 실험 계획

사용자는 과거 Test 일부를 개발 자료로 바꾸지 않고 엄격 분리를 유지하도록 명시했다.
과거 모든 Test 행 ID의 합집합 12,518개를 새 Train/Validation에서 제외한다.
Train=Batch 1의 남은 370개(Toluene 59), Validation=Batch 2의 남은 1,022개(Toluene 4),
최종 탐색적 Test=Batch 3–10 전체 12,221개(Toluene 1,754)로 고정한다.
Train/Validation 모두 6종이 존재하고, 행·정확 특징 중복 및 시간 순서를 확인한다.
Batch 1–2의 과거 랜덤 Test 297개는 이번 새 학습·검증·평가에서 제외한다.

## 실험과 비용
- A: 기존 시간순 모델 6개를 재학습 없이 재예측하고 기존 지표와 대조한다. Test 대조는 후보를 고정한 후 수행한다.
- B: 저장된 Batch 1 / Batch 1–3 모델을 공통 미래 Batch 6–10에서 비교한다.
  새 Batch 확장 학습은 과거 Test를 학습·튜닝에 넣게 되므로 실행하지 않는다.
- C: 엄격 Train/Validation에서 세 모델의 class_weight=None/balanced 비교.
- D: LR/SVM에 StandardScaler/RobustScaler 비교. RF는 무스케일 유지.
  PCA·특징 선택은 Train 370개, Toluene 검증 4개의 제한과 탐색 예산 때문에 이번에는 실행하지 않는다.
- E: 초기 비교의 모델별 Validation 승자가 전처리/가중치를 고정하고 2개 파라미터 후보만 추가.
  LR C=0.1/10, RF (200 trees) 또는 (100 trees, depth=12, leaf=3),
  SVM (C=10,gamma=scale) 또는 (C=1,gamma=0.001).
  RF 두 번째 조건은 depth와 leaf를 함께 바꾸므로 개별 인과효과로 해석하지 않는다.
총 8개 초기 + 6개 후속 = 최대 14회 Fit. 모든 조합의 전체 격자 탐색은 하지 않는다.

## 선정 규칙
동일 계열 기본 모델보다 Validation의 다른 5종 평균 F1이 3pp 넘게 낮아진 설정은 제외한다.
이는 사전 탐색 보호 규칙이며 운영 허용오류나 통계적 유의성 기준은 아니다.
남은 후보 중 최고 Validation macro-F1의 1pp 이내를 근접 후보로 보고
Toluene F1 → Toluene Recall → 다른 5종 F1 → macro-F1 → 고정 실행 순서로 계열 대표를 정한다.
후속 튜닝의 초기 부모와 최종 대표 모두 같은 규칙을 사용한다.
Toluene 검증 표본이 4개뿐이므로 세 계열 대표를 공동 검증 후보로 유지한다.
대표 중 Validation macro-F1이 가장 높은 모델을 우선 검증 순서로만 제시한다.
Validation이 단일 Batch여서 Batch 간 안정성을 선정 기준으로 추정할 수 없다.
선정 이후 Test 변동은 설명용이며 후보 변경이나 재튜닝에 사용하지 않는다.

## 누수·보존
각 파이프라인의 imputer와 scaler는 해당 Train 370개에서만 Fit한다.
기존 EDA의 PCA/스케일러를 재사용하지 않는다. Validation을 합쳐 재학습하지 않는다.
Validation 결정과 모델 해시를 먼저 동결한 뒤 Test 예측을 실행한다.
기존 모델·보고서·원본·테스트·과거 해시는 덮어쓰지 않는다.
새 모델은 models/improvement_strict/, 새 결과는 outputs/model_improvement/에 저장한다.
모든 Test는 이전에 관찰한 자료이므로 독립 성능이 아닌 탐색적 성능이다.
새 시기의 미관찰 자료 없이는 최종 확정 모델을 선언하지 않는다.
'''
    (ROOT / 'reports/model_improvement_protocol.md').write_text(text, encoding='utf-8')
    return parts, assignments, plan


# Train에만 적용할 파이프라인 구성
def make_pipeline(family, scaler, weight, overrides):
    config = json.loads((ROOT / 'training_config.json').read_text(encoding='utf-8'))
    params = copy.deepcopy(config['models'][family])
    params['class_weight'] = weight
    params.update(overrides)
    constructors = dict(LogisticRegression=LogisticRegression,
                        RandomForest=RandomForestClassifier, SVM_RBF=SVC)
    steps = [('imputer', SimpleImputer(strategy='median', keep_empty_features=True))]
    if scaler == 'standard':
        steps.append(('scaler', StandardScaler()))
    elif scaler == 'robust':
        steps.append(('scaler', RobustScaler()))
    steps.append(('classifier', constructors[family](**params)))
    return Pipeline(steps)


# 다른 5종의 성능과 Toluene 성능을 따로 계산
def score(y_true, predicted):
    metric, classes, cm = evaluate(y_true, predicted)
    tol = next(row for row in classes if row['gas_id'] == 6)
    other = [row['f1'] for row in classes if row['gas_id'] != 6 and row['support'] > 0]
    metric.update(toluene_recall=tol['recall'], toluene_f1=tol['f1'],
                  toluene_support=tol['support'], other_five_macro_f1=float(np.mean(other)),
                  min_class_recall=float(min(row['recall'] for row in classes if row['support'])))
    return metric, classes, cm


# 사전 규칙으로 Validation 후보만 선택
def choose_family(rows, baseline_id):
    data = pd.DataFrame(rows)
    base = data[data.trial_id == baseline_id].iloc[0]
    eligible = data[data.other_five_macro_f1 >= base.other_five_macro_f1 - .03 - 1e-12]
    near = eligible[eligible.macro_f1 >= eligible.macro_f1.max() - .01 - 1e-12]
    return near.sort_values(
        ['toluene_f1', 'toluene_recall', 'other_five_macro_f1', 'macro_f1', 'order'],
        ascending=[False, False, False, False, True],
    ).iloc[0].trial_id


# Train 학습 후 Validation만 예측하고 모델 저장
def fit_trial(spec, train, validation, order):
    pipeline = make_pipeline(spec['family'], spec['scaler'], spec['class_weight'], spec['overrides'])
    start = time.perf_counter()
    with warnings.catch_warnings(record=True) as captured, threadpool_limits(limits=2):
        warnings.simplefilter('always')
        pipeline.fit(train[FEATURES], train.gas)
    fit_seconds = time.perf_counter() - start
    with threadpool_limits(limits=2):
        start = time.perf_counter()
        predicted = pipeline.predict(validation[FEATURES])
        predict_seconds = time.perf_counter() - start
    metric, classes, cm = score(validation.gas, predicted)
    path = MODELS / f'{spec["trial_id"]}.joblib'
    joblib.dump(pipeline, path, compress=3)
    record = dict(**spec, order=order, fit_seconds=fit_seconds,
                  validation_predict_seconds=predict_seconds, train_n=len(train),
                  model_file=str(path.relative_to(ROOT)), model_sha256=sha(path),
                  params=pipeline.named_steps['classifier'].get_params(),
                  complexity=dict(
                      model_bytes=path.stat().st_size,
                      support_vectors=int(pipeline.named_steps['classifier'].n_support_.sum())
                      if spec['family'] == 'SVM_RBF' else None,
                      tree_count=len(pipeline.named_steps['classifier'].estimators_)
                      if spec['family'] == 'RandomForest' else None,
                  ),
                  warnings=[dict(category=w.category.__name__, message=str(w.message)) for w in captured])
    row = dict(trial_id=spec['trial_id'], family=spec['family'], group=spec['group'],
               order=order, **metric)
    pred = validation[['row_id', 'batch', 'gas']].rename(columns={'gas': 'y_true'}).copy()
    pred['y_pred'] = predicted
    pred['trial_id'] = spec['trial_id']
    pred['partition'] = 'validation'
    print('Validation', spec['trial_id'], f'F1={metric["macro_f1"]:.5f}', flush=True)
    return row, record, pred


# 소규모 초기 비교와 Validation 기반 후속 후보 학습
def training_phase(train, validation):
    rows, records, predictions = [], [], []
    initial = []
    for family in FAMILIES:
        abbr = ABBR[family]
        scaler = 'none' if family == 'RandomForest' else 'standard'
        initial.extend([
            dict(trial_id=f'{abbr}_base', family=family, group='baseline', scaler=scaler,
                 class_weight=None, overrides={}, parent=None),
            dict(trial_id=f'{abbr}_balanced', family=family, group='C_weight', scaler=scaler,
                 class_weight='balanced', overrides={}, parent=None),
        ])
        if family != 'RandomForest':
            initial.append(dict(trial_id=f'{abbr}_robust', family=family, group='D_scaler',
                                scaler='robust', class_weight=None, overrides={}, parent=None))
    for spec in initial:
        row, record, pred = fit_trial(spec, train, validation, len(rows))
        rows.append(row); records.append(record); predictions.append(pred)
    for family in FAMILIES:
        abbr = ABBR[family]
        parent = choose_family([r for r in rows if r['family'] == family], f'{abbr}_base')
        source = next(record for record in records if record['trial_id'] == parent)
        settings = {
            'LogisticRegression': [('C0p1', {'C': .1}), ('C10', {'C': 10.0})],
            'RandomForest': [('trees200', {'n_estimators': 200}),
                             ('depth12_leaf3', {'max_depth': 12, 'min_samples_leaf': 3})],
            'SVM_RBF': [('C10', {'C': 10.0}), ('gamma0p001', {'gamma': .001})],
        }[family]
        for suffix, overrides in settings:
            spec = dict(trial_id=f'{abbr}_tune_{suffix}', family=family, group='E_tuning',
                        scaler=source['scaler'], class_weight=source['class_weight'],
                        overrides=overrides, parent=parent)
            row, record, pred = fit_trial(spec, train, validation, len(rows))
            rows.append(row); records.append(record); predictions.append(pred)
    data = pd.DataFrame(rows)
    representatives = [choose_family([r for r in rows if r['family'] == family],
                                     f'{ABBR[family]}_base') for family in FAMILIES]
    ranking = data[data.trial_id.isin(representatives)].sort_values(
        ['macro_f1', 'toluene_f1', 'order'], ascending=[False, False, True])
    decision = dict(frozen_at_seoul=now(), joint_candidates=representatives,
                    priority_candidate=ranking.iloc[0].trial_id, selection_data='validation_only',
                    independent_validation=False, final_confirmed=False,
                    rationale='Only 4 Toluene validation samples; retain all three family representatives.',
                    selected_model_hashes={r['trial_id']: r['model_sha256'] for r in records
                                           if r['trial_id'] in representatives})
    data.to_csv(OUT / 'validation_metrics.csv', index=False, encoding='utf-8')
    write_json(OUT / 'fit_records.json', records)
    write_json(OUT / 'validation_decisions.json', decision)
    return data, records, pd.concat(predictions, ignore_index=True), decision


# 후보 고정 후에만 Test 성능 계산
def evaluation_phase(frame, parts, records, validation_predictions, decision):
    frozen_hash = sha(OUT / 'validation_decisions.json')
    started = now()
    predictions = [validation_predictions]
    metrics, classes, matrices, timings = [], [], [], []
    for record in records:
        trial = record['trial_id']
        pipeline = joblib.load(ROOT / record['model_file'])
        test = frame.iloc[parts['test']]
        with threadpool_limits(limits=2):
            start = time.perf_counter()
            pred = pipeline.predict(test[FEATURES])
            elapsed = time.perf_counter() - start
        temp = test[['row_id', 'batch', 'gas']].rename(columns={'gas': 'y_true'}).copy()
        temp['y_pred'] = pred; temp['trial_id'] = trial; temp['partition'] = 'test'
        predictions.append(temp)
        timings.append(dict(trial_id=trial, partition='test', n=len(test),
                            predict_seconds=elapsed, predict_ms_per_1000=elapsed * 1e6 / len(test)))
        combined = pd.concat([validation_predictions[validation_predictions.trial_id == trial], temp])
        for part, subset in combined.groupby('partition', sort=False):
            scopes = [('pooled', 0, subset)] + [('batch', int(b), sub) for b, sub in subset.groupby('batch')]
            if part == 'test':
                scopes.append(('common_6_10', 0, subset[subset.batch.isin([6, 7, 8, 9, 10])]))
            for scope, batch, sub in scopes:
                metric, per_class, cm = score(sub.y_true, sub.y_pred)
                meta = dict(trial_id=trial, family=record['family'], group=record['group'],
                            partition=part, scope=scope, batch=batch)
                metrics.append(dict(**meta, **metric))
                classes.extend(dict(**meta, **row) for row in per_class)
                for i, true in enumerate(GASES):
                    for j, predicted in enumerate(GASES):
                        matrices.append(dict(**meta, true_class=true, predicted_class=predicted,
                                             count=int(cm[i, j])))
    data = pd.DataFrame(metrics)
    stability = data[(data.partition == 'test') & (data.scope == 'batch')]
    stability = stability[stability.batch.isin([6, 7, 8, 9, 10])].groupby('trial_id').macro_f1.agg(
        mean_macro_f1='mean', sd_macro_f1=lambda s: s.std(ddof=0),
        min_macro_f1='min', max_macro_f1='max').reset_index()
    pd.concat(predictions, ignore_index=True).to_csv(
        OUT / 'predictions.csv.gz', index=False, encoding='utf-8', compression='gzip')
    for name, table in [('metrics', data), ('per_class_metrics', pd.DataFrame(classes)),
                        ('confusion_matrices', pd.DataFrame(matrices)), ('prediction_times', pd.DataFrame(timings)),
                        ('test_batch_stability', stability)]:
        table.to_csv(OUT / f'{name}.csv', index=False, encoding='utf-8')
    if sha(OUT / 'validation_decisions.json') != frozen_hash:
        raise RuntimeError('Selection changed after Test access')
    write_json(OUT / 'evaluation_gate.json', dict(
        test_evaluation_started_at_seoul=started, decision_sha256=frozen_hash,
        selection_frozen_before_test=decision['frozen_at_seoul'] <= started,
        selection_unchanged=True, test_used_for_selection=False))
    return data, pd.DataFrame(classes), stability


# 저장된 시간순 기준 모델의 지표 재현 및 고정 확장 비교
def reproduce_baselines(frame):
    old = pd.read_csv(ROOT / 'outputs/model_comparison/predictions.csv')
    existing = pd.read_csv(ROOT / 'outputs/model_comparison/metrics.csv')
    records = json.loads((ROOT / 'outputs/model_comparison/fit_records.json').read_text(encoding='utf-8'))
    lookup = frame.set_index('row_id')
    results, reproduction = [], []
    for record in records:
        exp, model = record['experiment'], record['model']
        path = ROOT / record['model_file']
        if sha(path) != record['sha256']:
            raise RuntimeError('Original model changed')
        if exp not in ['B_early', 'B_history']:
            continue
        pipeline = joblib.load(path)
        selected = old[(old.experiment == exp) & (old.model == model)]
        with threadpool_limits(limits=2):
            pred = pipeline.predict(lookup.loc[selected.row_id, FEATURES])
        if not np.array_equal(pred, selected.y_pred):
            raise RuntimeError('Original predictions not reproduced')
        for row in existing[(existing.experiment == exp) & (existing.model == model)].itertuples():
            sub = selected[selected.partition == row.partition]
            if row.scope == 'batch':
                sub = sub[sub.batch == row.batch]
            measured, _, _ = score(sub.y_true, sub.y_pred)
            for key in ['accuracy', 'macro_f1', 'weighted_f1', 'macro_precision', 'macro_recall']:
                if not np.isclose(measured[key], getattr(row, key), atol=1e-12, rtol=1e-12):
                    raise RuntimeError('Original metric mismatch')
        reproduction.append(dict(experiment=exp, model=model, prediction_rows=len(selected),
                                 exact_replay=True, existing_metrics_match=True))
        for scope, sub in [('all_test', selected[selected.partition == 'test']),
                           ('common_6_10', selected[(selected.partition == 'test') & selected.batch.isin([6, 7, 8, 9, 10])])]:
            measured, _, _ = score(sub.y_true, sub.y_pred)
            results.append(dict(experiment=exp, family=model, scope=scope,
                                train_n=record['train_n'], **measured))
    pd.DataFrame(reproduction).to_csv(OUT / 'baseline_reproduction.csv', index=False, encoding='utf-8')
    baseline = pd.DataFrame(results)
    baseline.to_csv(OUT / 'frozen_baseline_metrics.csv', index=False, encoding='utf-8')
    return baseline


# 모든 기존 파일을 보존하며 단계별 실험 실행
def run():
    targets = ['model_improvement_report.html', 'model_selection_rationale.md', 'model_improvement_protocol.md']
    if any((ROOT / 'reports' / name).exists() for name in targets):
        raise FileExistsError('Improvement report already exists')
    paths = [p for directory in ['src', 'tests', 'models', 'reports', 'outputs']
             for p in (ROOT / directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    before = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    frame, source = load_dataset(read_config())
    previous = json.loads((ROOT / 'outputs/model_comparison/run_manifest.json').read_text(encoding='utf-8'))
    if dict(zip(source.file, source.sha256)) != previous['source_sha256']:
        raise RuntimeError('Raw dataset differs from historical training source')
    historical = pd.read_csv(ROOT / 'outputs/model_comparison/split_assignments.csv')
    parts, assignments, plan = freeze_plan(frame, historical)
    plan_hash = sha(OUT / 'experiment_plan.json')
    train, validation = frame.iloc[parts['train']], frame.iloc[parts['validation']]
    validation_metrics, records, validation_predictions, decision = training_phase(train, validation)
    metrics, classes, stability = evaluation_phase(frame, parts, records, validation_predictions, decision)
    baseline = reproduce_baselines(frame)
    from .improvement_report import build_report
    build_report(plan, assignments, validation_metrics, records, decision, metrics, classes, stability, baseline)
    after = {name: sha(ROOT / name) for name in before}
    raw_hashes = dict(zip(source.file, source.sha256))
    if before != after or any(sha(Path(read_config()['data_dir']) / name) != value for name, value in raw_hashes.items()):
        raise RuntimeError('Existing files or raw data changed')
    if sha(OUT / 'experiment_plan.json') != plan_hash:
        raise RuntimeError('Frozen plan changed')
    write_json(OUT / 'run_manifest.json', dict(
        completed_at_seoul=now(), existing_files_unchanged=True, before=before, after=after,
        raw_hashes=raw_hashes, raw_files_unchanged=True, fits=len(records), seed=SEED,
        plan_sha256=plan_hash, selected_by='validation_only', final_model_confirmed=False,
        code_sha256={name: sha(ROOT / 'src' / name) for name in ['improve_models.py', 'improvement_report.py']},
        package_versions={p: importlib.metadata.version(p) for p in ['numpy', 'pandas', 'scikit-learn', 'joblib', 'scipy', 'matplotlib']},
    ))
    print('JOINT CANDIDATES', decision['joint_candidates'], 'PRIORITY', decision['priority_candidate'], flush=True)
    print(validation_metrics.to_string(index=False), flush=True)


if __name__ == '__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    try:
        run()
    except Exception:
        logging.exception('Improvement experiment failed')
        raise
