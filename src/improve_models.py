# 과거 Test를 제외한 시간순 자료로 소규모 개선 실험 수행
# Validation으로만 후보 선택 후 탐색적 Test 평가

import copy
import hashlib
import json
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

from .data import ROOT, FEATURES, GASES
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


# 후보 고정 후에만 Test 성능 계산


# 저장된 시간순 기준 모델의 지표 재현 및 고정 확장 비교


# 모든 기존 파일을 보존하며 단계별 실험 실행


