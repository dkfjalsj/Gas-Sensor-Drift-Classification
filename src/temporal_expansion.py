# 시간순 학습 범위 비교와 소규모 개선 실험 실행
# Validation 후보 고정 후 기존 자료의 탐색적 평가 수행

import copy
import hashlib
import importlib.metadata
import json
import logging
import shutil
import time
import warnings
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import joblib
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from .data import ROOT, FEATURES, GASES, load_dataset, read_config
from .train_models import evaluate
from .improve_models import make_pipeline

OUT = ROOT / 'outputs' / 'temporal_expansion'
MODEL_DIR = ROOT / 'models' / 'temporal_expansion'
FAMILIES = ['LogisticRegression', 'RandomForest', 'SVM_RBF']
ABBR = dict(zip(FAMILIES, ['LR', 'RF', 'SVM']))
FOCUS = [4, 6]


# 파일 지문과 서울 시각 기록
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def now():
    return datetime.now(ZoneInfo('Asia/Seoul')).isoformat()


def write_json(path, value):
    Path(path).write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8'
    )


# 고정한 시간순 표본과 중복·클래스 구성 확인
def prepare_split(frame):
    parts = {
        'A': frame.index[frame.batch <= 3].to_numpy(),
        'B': frame.index[frame.batch <= 6].to_numpy(),
        'validation': frame.index[frame.batch.isin([7, 8])].to_numpy(),
        'evaluation': frame.index[frame.batch.isin([9, 10])].to_numpy(),
    }
    groups = pd.util.hash_pandas_object(frame[FEATURES], index=False)
    audits = []
    for condition in ['A', 'B']:
        for other in ['validation', 'evaluation']:
            if set(parts[condition]) & set(parts[other]):
                raise ValueError('Row overlap')
            if set(groups.iloc[parts[condition]]) & set(groups.iloc[parts[other]]):
                raise ValueError('Exact-feature overlap')
        if not (frame.batch.iloc[parts[condition]].max() < 7 < 9):
            raise ValueError('Chronological order violation')
    if set(groups.iloc[parts['validation']]) & set(groups.iloc[parts['evaluation']]):
        raise ValueError('Validation/evaluation feature overlap')
    for part, indices in parts.items():
        sub = frame.iloc[indices]
        if set(sub.gas) != set(GASES):
            raise ValueError('Missing gas class')
        audits.append(dict(
            partition=part, n=len(sub), batches=sorted(map(int, sub.batch.unique())),
            class_counts={str(g): int((sub.gas == g).sum()) for g in GASES},
            toluene_n=int((sub.gas == 6).sum()), acetaldehyde_n=int((sub.gas == 4).sum()),
            row_overlap=0, exact_feature_overlap=0,
        ))
    for batch in [7, 8, 9, 10]:
        if set(frame.loc[frame.batch == batch, 'gas']) != set(GASES):
            raise ValueError('A future batch lacks a class')
    manifest = frame[['row_id', 'batch', 'gas']].copy()
    manifest['main_partition'] = np.select(
        [frame.batch <= 6, frame.batch.isin([7, 8])], ['train', 'validation'],
        default='evaluation',
    )
    manifest['train_A'] = frame.batch <= 3
    manifest['train_B'] = frame.batch <= 6
    return parts, manifest, audits


# 실제 학습 전에 분할·탐색·선정 규칙 동결
def freeze_protocol(frame):
    if OUT.exists() or MODEL_DIR.exists():
        raise FileExistsError('Temporal expansion output already exists')
    targets = ['temporal_expansion_protocol.md', 'temporal_expansion_report.html',
               'temporal_expansion_model_selection.md']
    if any((ROOT / 'reports' / name).exists() for name in targets):
        raise FileExistsError('Temporal expansion report already exists')
    parts, manifest, audit = prepare_split(frame)
    OUT.mkdir(parents=True)
    (MODEL_DIR / 'trials').mkdir(parents=True)
    manifest.to_csv(OUT / 'split_assignments.csv', index=False, encoding='utf-8')
    write_json(OUT / 'split_audit.json', audit)
    frame.groupby(['batch', 'gas']).size().rename('n').reset_index().to_csv(
        OUT / 'batch_class_counts.csv', index=False, encoding='utf-8'
    )
    plan = dict(
        frozen_at_seoul=now(), seed=42, retrospective_reassignment=True,
        train_A_batches=[1, 2, 3], train_B_batches=list(range(1, 7)),
        validation_batches=[7, 8], exploratory_evaluation_batches=[9, 10],
        split_sha256=sha(OUT / 'split_assignments.csv'),
        new_fits=17, initial_fits=11, followup_fits=6,
        base_settings_source='training_config.json; original Standard LR/SVM, unscaled RF',
        base_settings_sha256=sha(ROOT / 'training_config.json'),
        initial_B='base/ balanced for three families; robust-none for LR/SVM',
        tuning_B='LR C=.1 or 10; RF trees=200 or depth=12+leaf=3; '
                 'SVM C=10 or gamma=.001. Initial Validation winner fixes weight/scaler.',
        primary='Validation per-Batch macro-F1 equal-weight mean over batches 7 and 8',
        eligibility='Other four gas pooled Validation mean F1 must not fall more than .03 '
                    'below same-family B baseline; focus gases are IDs 4 and 6.',
        tie='Within .005 of best primary: larger min(Toluene F1,Acetaldehyde F1), '
            'larger minimum-class recall, larger pooled macro-F1, smaller Validation Batch SD, '
            'then fixed trial order. Margins are exploratory rules, not significance tests.',
        selection_pool='Only condition B. One representative per family; global close joint '
                       'candidates are representatives within .005 of highest primary.',
        refit_on_validation=False, feature_selection=False, pca=False,
        evaluation_gate='Freeze selection and selected model bytes before any 9–10 predictions.',
        independent_final_test=False,
    )
    write_json(OUT / 'experiment_plan.json', plan)
    text = '''# 6단계 시간순 확장 학습 사전 계획

기존 Test의 일부를 새 개발 자료로 재지정하는 회고적·탐색적 실험이다.
1–5단계의 실험, 코드, 원본, 모델, 보고서와 과거 해시 기록은 보존한다.

## 고정 분할
- 조건 A Train=Batch 1–3: 3,275개(Toluene 79, Acetaldehyde 379).
- 조건 B Train=Batch 1–6: 5,933개(Toluene 546, Acetaldehyde 484).
- 공통 Validation=Batch 7–8: 3,907개(Toluene 586, Acetaldehyde 777).
- 공통 탐색적 평가=Batch 9–10: 4,070개(Toluene 701, Acetaldehyde 675).
각 Train과 이후 Validation/평가의 행·정확 특징 중복, 시간 순서, 6종 존재를 확인한다.
조건 A와 B의 Train 겹침은 의도한 포함 관계이며 같은 조건 내부 평가 누수와 다르다.

## 실험 수와 설정
기존 training_config.json의 기본 모델 설정을 동일하게 사용해 A/B 각각 3개를 학습한다.
조건 B에 class_weight=balanced 3개, LR/SVM RobustScaler+weight=None 2개를 추가한다.
초기 총 11개를 Validation으로 비교한 뒤 각 계열의 초기 대표를 고정한다.
해당 부모의 가중치·스케일러를 유지하고 다음 2개씩만 추가한다.
- LR C=0.1 / 10
- RF n_estimators=200 / (n_estimators=100,max_depth=12,min_samples_leaf=3)
- SVM C=10,gamma=scale / C=1,gamma=0.001
총 17회 Fit. RF depth와 leaf는 함께 바꾸므로 개별 효과를 분리하지 않는다.
전처리는 median imputer와 LR/SVM StandardScaler 또는 RobustScaler다.
각 Train에서만 Fit한다. RF 무스케일 기준 유지. PCA·특징 선택·재표본화는 미실행.
Validation을 합친 재학습은 하지 않는다. seed=42, BLAS thread=2, RF n_jobs=-1 유지.

## 후보 선정과 동점 처리
주 지표는 Validation Batch 7과 8의 macro-F1 동일 가중 평균이다.
pooled Validation macro-F1, Batch SD, Toluene/Acetaldehyde F1·Recall,
최저 클래스 Recall, 나머지 4종 평균 F1과 비용을 함께 기록한다.
조건 B 설정만 개선 후보 선정에 사용한다. A는 통제 비교다.
동일 계열 B 기본 모델 대비 나머지 4종 pooled 평균 F1이 3pp 초과 낮아지면 제외한다.
남은 설정 중 주 지표 최고점의 0.5pp 이내를 근접 점수로 본다.
min(Toluene F1,Acetaldehyde F1) → 최저 클래스 Recall → pooled macro-F1 →
작은 Validation Batch SD → 고정 실행 순서로 대표를 고른다.
3pp/0.5pp는 사전 탐색 규칙이며 운영 기준·통계적 동등성 기준이 아니다.
계열별 대표 3개를 저장하고, 그 대표들의 최고 주 지표 0.5pp 이내를 근접 공동 후보로 표시한다.
근접 집합에서 같은 동점 규칙으로 우선 후보를 정한다. 최종 확정 모델은 선정하지 않는다.
Validation 두 Batch만으로 안정성의 독립 증거를 확정할 수 없고 Batch 8의 Toluene은 18개다.

## 평가 제한과 보존
모든 후보 결정과 모델 SHA-256을 기록한 후에만 Batch 9–10 예측을 수행한다.
평가 결과가 나빠도 파라미터·전처리·후보를 바꾸지 않는다.
평가 결과는 새 독립 Test가 아닌 기존 자료를 재사용한 탐색적 평가다.
성능 변화는 학습량·클래스 구성·시기가 함께 달라진 결과이며 데이터 양만의 효과가 아니다.
기존 테스트는 수정하지 않고 기존 실패 2건과 신규 실패를 구분한다. Commit·Push 금지.
'''
    (ROOT / 'reports/temporal_expansion_protocol.md').write_text(text, encoding='utf-8')
    return parts, plan


# 전체 지표와 두 집중 가스의 지표를 함께 계산
def measured_scores(y, predicted):
    metrics, classes, cm = evaluate(y, predicted)
    by_id = {row['gas_id']: row for row in classes}
    for gas, prefix in [(6, 'toluene'), (4, 'acetaldehyde')]:
        metrics[prefix + '_recall'] = by_id[gas]['recall']
        metrics[prefix + '_f1'] = by_id[gas]['f1']
        metrics[prefix + '_support'] = by_id[gas]['support']
    metrics['min_class_recall'] = min(row['recall'] for row in classes if row['support'])
    metrics['other_four_f1'] = float(np.mean([by_id[g]['f1'] for g in [1, 2, 3, 5]]))
    return metrics, classes, cm


# Validation 전체와 Batch 동일 가중 성능 계산
def validation_summary(validation, predicted):
    pooled, _, _ = measured_scores(validation.gas, predicted)
    batch_scores = []
    for batch in [7, 8]:
        mask = validation.batch.to_numpy() == batch
        result, _, _ = measured_scores(validation.gas.to_numpy()[mask], predicted[mask])
        batch_scores.append(result['macro_f1'])
    return dict(
        val_equal_batch_macro_f1=float(np.mean(batch_scores)),
        val_batch_sd=float(np.std(batch_scores)),
        val_pooled_macro_f1=pooled['macro_f1'], val_accuracy=pooled['accuracy'],
        val_weighted_f1=pooled['weighted_f1'],
        val_toluene_recall=pooled['toluene_recall'], val_toluene_f1=pooled['toluene_f1'],
        val_acetaldehyde_recall=pooled['acetaldehyde_recall'],
        val_acetaldehyde_f1=pooled['acetaldehyde_f1'],
        val_min_class_recall=pooled['min_class_recall'],
        val_other_four_f1=pooled['other_four_f1'],
        val_focus_min_f1=min(pooled['toluene_f1'], pooled['acetaldehyde_f1']),
        val_batch7_macro_f1=batch_scores[0], val_batch8_macro_f1=batch_scores[1],
    )


# 사전 규칙으로 Validation 근접 점수와 보호 기준 적용
def choose(rows, baseline_id):
    data = pd.DataFrame(rows)
    baseline = data[data.trial_id == baseline_id].iloc[0]
    eligible = data[
        data.val_other_four_f1 >= baseline.val_other_four_f1 - .03 - 1e-12
    ]
    near = eligible[
        eligible.val_equal_batch_macro_f1 >= eligible.val_equal_batch_macro_f1.max() - .005 - 1e-12
    ]
    return rank_near(near).iloc[0].trial_id


# 근접 점수 내의 고정 동점 순서 적용
def rank_near(data):
    return data.sort_values(
        ['val_focus_min_f1', 'val_min_class_recall', 'val_pooled_macro_f1',
         'val_batch_sd', 'order'], ascending=[False, False, False, True, True],
    )


# 조건에 맞는 Train만 학습하고 Validation 예측 저장
def fit_trial(spec, frame, parts, order):
    train = frame.iloc[parts[spec['condition']]]
    validation = frame.iloc[parts['validation']]
    pipeline = make_pipeline(
        spec['family'], spec['scaler'], spec['class_weight'], spec['overrides']
    )
    start = time.perf_counter()
    with warnings.catch_warnings(record=True) as caught, threadpool_limits(limits=2):
        warnings.simplefilter('always')
        pipeline.fit(train[FEATURES], train.gas)
    seconds = time.perf_counter() - start
    with threadpool_limits(limits=2):
        start = time.perf_counter()
        predicted = pipeline.predict(validation[FEATURES])
        predict_seconds = time.perf_counter() - start
    path = MODEL_DIR / 'trials' / (spec['trial_id'] + '.joblib')
    joblib.dump(pipeline, path, compress=3)
    estimator = pipeline.named_steps['classifier']
    record = dict(
        **spec, order=order, train_n=len(train), fit_seconds=seconds,
        validation_predict_seconds=predict_seconds,
        model_file=str(path.relative_to(ROOT)), model_sha256=sha(path),
        model_bytes=path.stat().st_size, params=estimator.get_params(),
        warnings=[dict(category=w.category.__name__, message=str(w.message)) for w in caught],
        support_vectors=int(estimator.n_support_.sum()) if hasattr(estimator, 'n_support_') else None,
        tree_count=len(estimator.estimators_) if hasattr(estimator, 'estimators_') else None,
        train_row_ids_sha256=hashlib.sha256('\n'.join(train.row_id).encode()).hexdigest(),
    )
    row = dict(
        trial_id=spec['trial_id'], family=spec['family'], condition=spec['condition'],
        group=spec['group'], order=order, **validation_summary(validation, predicted),
    )
    pred = validation[['row_id', 'batch', 'gas']].rename(columns={'gas': 'y_true'}).copy()
    pred['y_pred'] = predicted
    pred['trial_id'] = spec['trial_id']
    pred['partition'] = 'validation'
    print('Validation', spec['trial_id'],
          f'equal-batch F1={row["val_equal_batch_macro_f1"]:.6f}', flush=True)
    return row, record, pred


# 기본 범위 비교 후 조건 B의 제한적 개선 설정만 학습
def train_and_select(frame, parts):
    initial = []
    for condition in ['A', 'B']:
        for family in FAMILIES:
            initial.append(dict(
                trial_id=f'{condition}_{ABBR[family]}_base', family=family,
                condition=condition, group='range_baseline',
                scaler='none' if family == 'RandomForest' else 'standard',
                class_weight=None, overrides={}, parent=None,
            ))
    for family in FAMILIES:
        initial.append(dict(
            trial_id=f'B_{ABBR[family]}_balanced', family=family, condition='B',
            group='weight', scaler='none' if family == 'RandomForest' else 'standard',
            class_weight='balanced', overrides={}, parent=None,
        ))
        if family != 'RandomForest':
            initial.append(dict(
                trial_id=f'B_{ABBR[family]}_robust', family=family, condition='B',
                group='scaler', scaler='robust', class_weight=None, overrides={}, parent=None,
            ))
    rows, records, predictions = [], [], []
    for spec in initial:
        row, record, pred = fit_trial(spec, frame, parts, len(rows))
        rows.append(row)
        records.append(record)
        predictions.append(pred)
    for family in FAMILIES:
        family_rows = [r for r in rows if r['family'] == family and r['condition'] == 'B']
        parent = choose(family_rows, f'B_{ABBR[family]}_base')
        settings = next(record for record in records if record['trial_id'] == parent)
        tuning = {
            'LogisticRegression': [('C0p1', {'C': .1}), ('C10', {'C': 10.0})],
            'RandomForest': [('trees200', {'n_estimators': 200}),
                             ('depth12_leaf3', {'max_depth': 12, 'min_samples_leaf': 3})],
            'SVM_RBF': [('C10', {'C': 10.0}), ('gamma0p001', {'gamma': .001})],
        }[family]
        for suffix, overrides in tuning:
            spec = dict(
                trial_id=f'B_{ABBR[family]}_tune_{suffix}', family=family, condition='B',
                group='tuning', scaler=settings['scaler'],
                class_weight=settings['class_weight'], overrides=overrides, parent=parent,
            )
            row, record, pred = fit_trial(spec, frame, parts, len(rows))
            rows.append(row)
            records.append(record)
            predictions.append(pred)
    validation = pd.DataFrame(rows)
    representatives = [
        choose([r for r in rows if r['family'] == family and r['condition'] == 'B'],
               f'B_{ABBR[family]}_base') for family in FAMILIES
    ]
    selected = validation[validation.trial_id.isin(representatives)]
    near = selected[
        selected.val_equal_batch_macro_f1 >= selected.val_equal_batch_macro_f1.max() - .005 - 1e-12
    ]
    priority = rank_near(near).iloc[0].trial_id
    saved_models = {}
    for trial in representatives:
        record = next(r for r in records if r['trial_id'] == trial)
        target = MODEL_DIR / (trial + '.joblib')
        shutil.copy2(ROOT / record['model_file'], target)
        saved_models[trial] = dict(path=str(target.relative_to(ROOT)), sha256=sha(target))
    decision = dict(
        frozen_at_seoul=now(), selection_data='validation_batches_7_8_only',
        primary_metric='val_equal_batch_macro_f1', family_representatives=representatives,
        close_joint_candidates=near.trial_id.tolist(), priority_candidate=priority,
        selected_models=saved_models, refit_on_validation=False, final_model_confirmed=False,
    )
    validation.to_csv(OUT / 'validation_metrics.csv', index=False, encoding='utf-8')
    write_json(OUT / 'fit_records.json', records)
    write_json(OUT / 'selection_frozen.json', decision)
    return validation, records, pd.concat(predictions, ignore_index=True), decision


# 후보 확정 뒤에만 Batch 9–10의 탐색적 예측 수행
def evaluate_frozen(frame, parts, records, validation_predictions, decision):
    selection_hash = sha(OUT / 'selection_frozen.json')
    started = now()
    metrics, classes, matrices, predictions, timings = [], [], [], [validation_predictions], []
    for record in records:
        pipeline = joblib.load(ROOT / record['model_file'])
        trial = record['trial_id']
        subset = frame.iloc[parts['evaluation']]
        with threadpool_limits(limits=2):
            start = time.perf_counter()
            predicted = pipeline.predict(subset[FEATURES])
            seconds = time.perf_counter() - start
        pred = subset[['row_id', 'batch', 'gas']].rename(columns={'gas': 'y_true'}).copy()
        pred['y_pred'] = predicted
        pred['trial_id'] = trial
        pred['partition'] = 'evaluation'
        predictions.append(pred)
        timings.append(dict(trial_id=trial, evaluation_n=len(subset),
                            predict_seconds=seconds, ms_per_1000=seconds * 1e6 / len(subset)))
        combined = pd.concat([validation_predictions[validation_predictions.trial_id == trial], pred])
        for partition, group in combined.groupby('partition', sort=False):
            scopes = [('pooled', 0, group)]
            scopes.extend(('batch', int(batch), sub) for batch, sub in group.groupby('batch'))
            for scope, batch, sub in scopes:
                result, per_class, cm = measured_scores(sub.y_true, sub.y_pred)
                meta = dict(trial_id=trial, family=record['family'], condition=record['condition'],
                            group=record['group'], partition=partition, scope=scope, batch=batch)
                metrics.append(dict(**meta, **result))
                classes.extend(dict(**meta, **row) for row in per_class)
                for i, true in enumerate(GASES):
                    for j, predicted_class in enumerate(GASES):
                        matrices.append(dict(**meta, true_class=true, predicted_class=predicted_class,
                                             count=int(cm[i, j])))
    data = pd.DataFrame(metrics)
    summaries = []
    for (trial, partition), group in data[data.scope == 'batch'].groupby(['trial_id', 'partition']):
        pooled = data[(data.trial_id == trial) & (data.partition == partition) & (data.scope == 'pooled')].iloc[0]
        summaries.append(dict(
            trial_id=trial, partition=partition, equal_batch_macro_f1=group.macro_f1.mean(),
            batch_sd_macro_f1=group.macro_f1.std(ddof=0),
            min_batch_macro_f1=group.macro_f1.min(), max_batch_macro_f1=group.macro_f1.max(),
            pooled_macro_f1=pooled.macro_f1, accuracy=pooled.accuracy,
            weighted_f1=pooled.weighted_f1, toluene_recall=pooled.toluene_recall,
            toluene_f1=pooled.toluene_f1, acetaldehyde_recall=pooled.acetaldehyde_recall,
            acetaldehyde_f1=pooled.acetaldehyde_f1,
            min_class_recall=pooled.min_class_recall, other_four_f1=pooled.other_four_f1,
        ))
    pd.concat(predictions, ignore_index=True).to_csv(
        OUT / 'predictions.csv.gz', index=False, encoding='utf-8', compression='gzip'
    )
    for name, table in [('metrics', data), ('per_class_metrics', pd.DataFrame(classes)),
                        ('confusion_matrices', pd.DataFrame(matrices)),
                        ('prediction_times', pd.DataFrame(timings)),
                        ('summary_metrics', pd.DataFrame(summaries))]:
        table.to_csv(OUT / f'{name}.csv', index=False, encoding='utf-8')
    if sha(OUT / 'selection_frozen.json') != selection_hash:
        raise RuntimeError('Selection changed after evaluation')
    write_json(OUT / 'evaluation_gate.json', dict(
        evaluation_started_at_seoul=started, selection_sha256=selection_hash,
        frozen_before_evaluation=decision['frozen_at_seoul'] <= started,
        selection_unchanged=True, evaluation_used_for_selection=False,
    ))
    return data, pd.DataFrame(classes), pd.DataFrame(summaries)


# 기존 산출물·모델·원본의 변경 없이 전체 실험 실행
def run():
    existing = [p for name in ['src', 'tests', 'models', 'reports', 'outputs']
                for p in (ROOT / name).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    before = {str(p.relative_to(ROOT)): sha(p) for p in existing}
    config = read_config()
    frame, source = load_dataset(config)
    legacy = json.loads((ROOT / 'outputs/model_comparison/run_manifest.json').read_text(encoding='utf-8'))
    if dict(zip(source.file, source.sha256)) != legacy['source_sha256']:
        raise RuntimeError('Original raw dataset changed')
    for registry in ['model_comparison', 'model_improvement']:
        previous = json.loads((ROOT / 'outputs' / registry / 'fit_records.json').read_text(encoding='utf-8'))
        for record in previous:
            expected = record.get('model_sha256', record.get('sha256'))
            if sha(ROOT / record['model_file']) != expected:
                raise RuntimeError('Existing model hash mismatch')
    parts, plan = freeze_protocol(frame)
    plan_hash = sha(OUT / 'experiment_plan.json')
    protocol_hash = sha(ROOT / 'reports/temporal_expansion_protocol.md')
    validation, records, predictions, decision = train_and_select(frame, parts)
    metrics, classes, summary = evaluate_frozen(frame, parts, records, predictions, decision)
    from .temporal_expansion_report import build_report
    build_report(plan, validation, records, decision, metrics, classes, summary)
    after = {name: sha(ROOT / name) for name in before}
    raw = dict(zip(source.file, source.sha256))
    if before != after or any(sha(Path(config['data_dir']) / name) != value for name, value in raw.items()):
        raise RuntimeError('Existing files or raw data changed')
    if sha(OUT / 'experiment_plan.json') != plan_hash:
        raise RuntimeError('Frozen plan changed')
    write_json(OUT / 'run_manifest.json', dict(
        completed_at_seoul=now(), fits=len(records), existing_files_unchanged=True,
        before=before, after=after, raw_files_unchanged=True, raw_hashes=raw,
        plan_sha256=plan_hash, protocol_sha256=protocol_hash,
        seed=42, independent_final_test=False, final_model_confirmed=False,
        code_sha256={name: sha(ROOT / 'src' / name)
                     for name in ['temporal_expansion.py', 'temporal_expansion_report.py']},
        package_versions={name: importlib.metadata.version(name)
                          for name in ['numpy', 'pandas', 'scikit-learn', 'scipy', 'joblib', 'matplotlib']},
    ))
    print('SELECTED', decision, flush=True)
    print(summary[summary.partition == 'evaluation'].to_string(index=False), flush=True)


if __name__ == '__main__':
    try:
        run()
    except Exception:
        logging.exception('Temporal expansion failed')
        raise
