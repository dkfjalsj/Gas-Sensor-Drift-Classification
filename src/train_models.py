# 동일 자료 분할로 세 모델 학습 및 성능 비교

"""Fixed baseline experiments; no tuning, refit on validation, or EDA transformer reuse.

Notebook에서 make_splits/make_pipeline/evaluate 공통 함수를 재사용함.
"""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from .data import ROOT, FEATURES, GASES

OUT = ROOT / 'outputs' / 'model_comparison'
LABELS = list(GASES)


# 파일 변경 확인용 해시 계산
def fingerprint(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# 결과를 JSON 파일로 저장
def write_json(path, value):
    Path(path).write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8'
    )


# 훈련·검증·테스트 자료를 동일 기준으로 분할
def make_splits(frame, settings):
    """A keeps the old seeded 20% Test, then splits remaining 80% 75:25."""
    indices = np.arange(len(frame))
    splits = {}
    for name, spec in settings['experiments'].items():
        if name == 'A_random':
            # 가스 비율을 유지하며 자료 분할
            development, test = train_test_split(
                indices, test_size=0.2, stratify=frame.gas, random_state=settings['random_state']
            )
            # 가스 비율을 유지하며 자료 분할
            train, validation = train_test_split(
                development,
                test_size=0.25,
                stratify=frame.gas.iloc[development],
                random_state=settings['random_state'],
            )
            splits[name] = {'train': train, 'validation': validation, 'test': test}
        else:
            splits[name] = {
                part: indices[frame.batch.isin(spec[f'{part}_batches'])]
                for part in ('train', 'validation', 'test')
            }
    return splits


# 자료 분할의 중복과 시간 순서 검사
def audit_splits(frame, splits):
    groups = pd.util.hash_pandas_object(frame[FEATURES], index=False).astype(str)
    records, assignments = [], []
    for experiment, parts in splits.items():
        if any(len(idx) == 0 for idx in parts.values()):
            raise ValueError(f'Empty partition: {experiment}')
        sets = {part: set(map(int, idx)) for part, idx in parts.items()}
        if any(
            sets[a] & sets[b]
            for a, b in [('train', 'validation'), ('train', 'test'), ('validation', 'test')]
        ):
            raise ValueError(f'Overlapping rows: {experiment}')
        if set.union(*sets.values()) != set(range(len(frame))):
            raise ValueError(f'Partitions do not cover the dataset: {experiment}')
        if set(frame.gas.iloc[parts['train']]) != set(LABELS):
            raise ValueError(f'Train missing a gas class: {experiment}')
        for a, b in [('train', 'validation'), ('train', 'test'), ('validation', 'test')]:
            if set(groups.iloc[parts[a]]) & set(groups.iloc[parts[b]]):
                raise ValueError(
                    f'Exact feature duplicates cross partitions: {experiment}/{a}/{b}; resolve group splitting before training'
                )
        if experiment.startswith('B_'):
            if not (
                frame.batch.iloc[parts['train']].max() < frame.batch.iloc[parts['validation']].min()
                and frame.batch.iloc[parts['validation']].max()
                < frame.batch.iloc[parts['test']].min()
            ):
                raise ValueError(f'Future information in chronological split: {experiment}')
        for part, idx in parts.items():
            subset = frame.iloc[idx]
            records.append(
                dict(
                    experiment=experiment,
                    partition=part,
                    n=len(idx),
                    batches=sorted(map(int, subset.batch.unique())),
                    class_counts={str(g): int((subset.gas == g).sum()) for g in LABELS},
                    missing_classes=[GASES[g] for g in LABELS if not (subset.gas == g).any()],
                    row_overlap=0,
                    cross_partition_exact_duplicate_groups=0,
                )
            )
            for row in subset[['row_id', 'batch', 'gas']].itertuples(index=False):
                assignments.append(
                    dict(
                        experiment=experiment,
                        partition=part,
                        row_id=row.row_id,
                        batch=row.batch,
                        gas=row.gas,
                    )
                )
    return records, pd.DataFrame(assignments)


# 자료 정리 단계와 분류 모델을 파이프라인으로 연결
def make_pipeline(name, settings):
    constructors = {
        'LogisticRegression': LogisticRegression,
        'RandomForest': RandomForestClassifier,
        'SVM_RBF': SVC,
    }
    # 훈련 중앙값으로 결측값 처리 준비
    steps = [('imputer', SimpleImputer(strategy='median', keep_empty_features=True))]
    if name != 'RandomForest':
        steps.append(('scaler', StandardScaler()))
    steps.append(('classifier', constructors[name](**settings['models'][name])))
    return Pipeline(steps)


# 실제 정답과 예측 비교 및 성능 계산
def evaluate(y, pred):
    y, pred = np.asarray(y), np.asarray(pred)
    p, r, f, support = precision_recall_fscore_support(y, pred, labels=LABELS, zero_division=0)
    present = support > 0
    metrics = dict(
        n=len(y),
        accuracy=float(accuracy_score(y, pred)),
        macro_precision=float(p[present].mean()),
        macro_recall=float(r[present].mean()),
        macro_f1=float(f[present].mean()),
        weighted_f1=float(np.average(f, weights=support)),
        macro_precision_fixed6=float(p.mean()),
        macro_recall_fixed6=float(r.mean()),
        macro_f1_fixed6=float(f.mean()),
        missing_classes=','.join(GASES[g] for g, mask in zip(LABELS, present) if not mask),
    )
    per_class = []
    for i, g in enumerate(LABELS):
        per_class.append(
            dict(
                gas_id=g,
                gas=GASES[g],
                support=int(support[i]),
                predicted_count=int((pred == g).sum()),
                precision=float(p[i]) if present[i] else None,
                recall=float(r[i]) if present[i] else None,
                f1=float(f[i]) if present[i] else None,
            )
        )
    # 실제 가스·예측 가스 조합별 개수 계산
    return metrics, per_class, confusion_matrix(y, pred, labels=LABELS)


# 자료 불러오기 및 분석 결과 저장


# 프로그램 실행 및 오류 안내


