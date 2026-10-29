# 시간순 학습 범위 비교와 소규모 개선 실험 실행
# Validation 후보 고정 후 기존 자료의 탐색적 평가 수행

import hashlib
import json
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

from .data import ROOT, FEATURES, GASES
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


# 기존 산출물·모델·원본의 변경 없이 전체 실험 실행


