# 동일한 과거 학습 행에서 SVM과 HGB 단독 모델 비교
# 사전 계획·Train 전처리·가스별 보호 기준 및 기존 파일 보존 검사

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier

from .data import ROOT, FEATURES, GASES
from .temporal_expansion import sha
from .temporal_svm_ensemble import audit_model
from .nonlinear_feature_transformation import row_digest

OUT = ROOT/'outputs/hgb_algorithm_comparison'
MODEL_DIR = ROOT/'models/hgb_algorithm_comparison'
FOLDS = {'A': (3, 6), 'B': (6, 7), 'C': (7, 8)}
CAUTION = ('과거 Fold는 반복 사용한 개발 검증 자료이며 독립 Test가 아님. '
           '학습 구간이 겹치는 Fold를 독립 반복 표본으로 취급하지 않음. '
           'Batch 9~10 신규 평가 없음. 공식 Model A 유지.')
HGB_PARAMS = dict(loss='log_loss', learning_rate=.1, max_iter=100, max_leaf_nodes=31,
                  max_depth=None, min_samples_leaf=20, l2_regularization=0., max_features=1.,
                  max_bins=255, categorical_features=None, monotonic_cst=None,
                  interaction_cst=None, warm_start=False, early_stopping=False,
                  scoring='loss', validation_fraction=None, n_iter_no_change=10, tol=1e-7,
                  verbose=0, random_state=42, class_weight='balanced')


# NumPy 자료형도 손실 없이 JSON 기록
def write(name, value):
    def convert(item):
        if isinstance(item, np.generic):
            return item.item()
        if isinstance(item, np.ndarray):
            return item.tolist()
        if isinstance(item, Path):
            return str(item)
        raise TypeError(type(item).__name__)
    (OUT/name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False,
                                     default=convert), encoding='utf-8')


def save(name, rows):
    table = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    table.to_csv(OUT/f'{name}.csv', index=False, encoding='utf-8')
    return table


# 기존 파일 전체의 바이트 지문 수집


# 동일한 학습·검증 행과 시간순·정확 중복 검사
def splits(frame):
    assert frame.batch.max() <= 8
    fingerprints = pd.util.hash_pandas_object(frame[FEATURES], index=False)
    assignments, supports = [], []
    for fold, (end, batch) in FOLDS.items():
        train, validation = frame[frame.batch <= end], frame[frame.batch == batch]
        assert train.batch.max() < batch
        assert set(train.row_id).isdisjoint(validation.row_id)
        assert set(fingerprints.loc[train.index]).isdisjoint(fingerprints.loc[validation.index])
        assert set(train.gas) == set(GASES)
        for part, sub in [('train', train), ('validation', validation)]:
            assignments.extend(dict(fold=fold, partition=part, row_id=r.row_id,
                                    batch=int(r.batch), gas_id=int(r.gas)) for r in sub.itertuples())
            supports.extend(dict(fold=fold, partition=part, gas_id=g, gas=GASES[g],
                                 n=int((sub.gas == g).sum())) for g in GASES)
    return pd.DataFrame(assignments), pd.DataFrame(supports)


# 지원 기능·기존 SVM 호환성을 학습 전에 검사
def preflight(frame):
    classifier = HistGradientBoostingClassifier(**HGB_PARAMS)
    classifier._validate_params()
    assert classifier.__sklearn_tags__().input_tags.allow_nan
    old = pd.read_csv(ROOT/'outputs/nonlinear_feature_transformation/model_registry.csv')
    results = []
    for fold, (end, _) in FOLDS.items():
        row = old[(old.fold == fold) & (old.method == 'baseline')].iloc[0]
        train = frame[frame.batch <= end]
        try:
            assert sha(ROOT/row.path) == row.sha256
            model = joblib.load(ROOT/row.path)
            check = audit_model(model, train, end)
            results.append(dict(fold=fold, can_reuse=True, path=row.path,
                                sha256=row.sha256, reason='', **check))
        except (ValueError, AssertionError, FileNotFoundError) as exc:
            results.append(dict(fold=fold, can_reuse=False, path=row.path,
                                sha256=row.sha256, reason=repr(exc), train_n=len(train),
                                row_sha256=row_digest(train.row_id)))
    return results


# 결과 확인 전에 두 조건과 보호 기준 고정


# 표본별 두 단독 모델의 오류 비교
def error_agreement(y, svm, hgb):
    y, svm, hgb = np.asarray(y), np.asarray(svm), np.asarray(hgb)
    if y.shape != svm.shape or y.shape != hgb.shape:
        raise ValueError('Same ordered validation rows required')
    a, b = svm == y, hgb == y
    return pd.DataFrame(dict(y_true=y, svm_pred=svm, hgb_pred=hgb,
                             both_correct=a & b, svm_only=a & ~b, hgb_only=~a & b,
                             both_wrong=~a & ~b, disagreement=svm != hgb))


# 평균·가스·Recall0 보호 기준 판정
def judge(metrics, classes):
    baseline = classes[classes.model == 'SVM'].set_index(['fold', 'gas_id'])
    treatment = classes[classes.model == 'HGB'].set_index(['fold', 'gas_id'])
    paired = treatment[['precision', 'recall', 'f1']].join(
        baseline[['precision', 'recall', 'f1']], rsuffix='_svm')
    gas_delta = (paired.recall-paired.recall_svm).groupby('gas_id').mean()
    f1_delta = (paired.f1-paired.f1_svm).groupby('gas_id').mean()
    other = paired[paired.index.get_level_values('gas_id').isin([1, 2, 3, 5])]
    fold_delta = (metrics[metrics.model == 'HGB'].set_index('fold').macro_f1-
                  metrics[metrics.model == 'SVM'].set_index('fold').macro_f1)
    gain = float(fold_delta.mean())
    checks = dict(complete=len(metrics) == 6 and len(paired) == 18,
                  macro_guard=gain >= .005-1e-12,
                  gas_recall_guard=bool((gas_delta >= -.05-1e-12).all()),
                  other_four_guard=float((other.f1-other.f1_svm).mean()) >= -.02-1e-12,
                  zero_count_guard=int(treatment.recall.eq(0).sum()) <= int(baseline.recall.eq(0).sum()),
                  no_new_zero_guard=not bool((paired.recall.eq(0) & (paired.recall_svm > 0)).any()))
    positive = gain > 1e-12 or bool((fold_delta > 1e-12).any()) or bool((f1_delta > 1e-12).any())
    category = 'A' if all(checks.values()) else ('B' if positive else 'C')
    return dict(checks=checks, all_passed=all(checks.values()), conclusion=category,
                mean_macro_delta=gain, fold_deltas={k:float(v) for k, v in fold_delta.items()},
                mean_gas_recall_delta={int(k):float(v) for k, v in gas_delta.items()},
                mean_gas_f1_delta={int(k):float(v) for k, v in f1_delta.items()},
                other_four_f1_delta=float((other.f1-other.f1_svm).mean()),
                new_zero_pairs=int((paired.recall.eq(0) & (paired.recall_svm > 0)).sum()),
                official_model='Model A unchanged', future_batches_evaluated=[])


# 기존 파일·원본·고정 계획 검사


# 학습을 한 번씩 수행하고 저장 예측의 재현성 확인


# 새 조건 추가 없이 계획·실행·최종 보고서 갱신 분리


