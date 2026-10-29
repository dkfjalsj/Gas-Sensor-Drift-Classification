# 같은 신규Validation에서6종 지표와 점수 기반OvR ROC 계산
# ROC 점수는 확률이 아니며 임계값 선택에 사용하지 않음

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, confusion_matrix, f1_score,
    precision_recall_fscore_support, roc_auc_score, roc_curve,
)

from ..data import GASES

LABELS = list(GASES)
RECALL_DROP_NOTICE = 0.05
MIN_VALIDATION_SUPPORT = 5


# 모든 모델에 같은 정답·클래스 순서 적용
def evaluate_model(model, features, target):
    predicted = model.predict(features)
    precision, recall, f1, support = precision_recall_fscore_support(
        target, predicted, labels=LABELS, zero_division=0,
    )
    classes = pd.DataFrame(dict(
        gas_id=LABELS, gas=list(GASES.values()), precision=precision,
        recall=recall, f1=f1, support=support,
        predicted_count=[int((predicted == gas).sum()) for gas in LABELS],
    ))
    result = dict(accuracy=float(accuracy_score(target, predicted)),
                  macro_f1=float(f1_score(target, predicted, labels=LABELS,
                                          average='macro', zero_division=0)),
                  weighted_f1=float(f1_score(target, predicted, labels=LABELS,
                                             average='weighted', zero_division=0)),
                  rows=len(target))
    matrix = confusion_matrix(target, predicted, labels=LABELS)
    auc_rows, curve_rows = [], []
    classifier = model.named_steps['classifier']
    reason = None
    if classifier.decision_function_shape != 'ovr':
        reason = 'OVR 클래스 점수 형식이 아님'
    elif list(model.classes_) != LABELS:
        reason = '모델 클래스 열 대응이 다름'
    scores = None if reason else model.decision_function(features)
    if scores is not None and (scores.shape != (len(target), 6)
                               or not np.isfinite(scores).all()):
        reason, scores = '유효한6개 클래스 점수 열이 아님', None
    for column, gas in enumerate(LABELS):
        binary = np.asarray(target) == gas
        positives, negatives = int(binary.sum()), int((~binary).sum())
        unavailable = reason or ('양성·음성 각5개 미만' if min(positives, negatives) < 5 else None)
        auc = None
        if not unavailable:
            auc = float(roc_auc_score(binary, scores[:, column]))
            false_positive, true_positive, thresholds = roc_curve(binary, scores[:, column])
            for fp, tp, threshold in zip(false_positive, true_positive, thresholds):
                curve_rows.append(dict(gas_id=gas, fpr=float(fp), tpr=float(tp),
                                       threshold=None if np.isinf(threshold) else float(threshold),
                                       threshold_is_infinite=bool(np.isinf(threshold))))
        auc_rows.append(dict(gas_id=gas, gas=GASES[gas], positives=positives,
                             negatives=negatives, auc=auc, unavailable_reason=unavailable))
    result['roc_note'] = 'SVC OVR 변환 결정점수의 클래스별 이진 ROC; 확률·자동 임계값·드리프트 판정 아님'
    result['score_argmax_disagrees_with_predict'] = (
        int((np.array(LABELS)[scores.argmax(axis=1)] != predicted).sum())
        if scores is not None else None)
    return result, classes, matrix, predicted, pd.DataFrame(auc_rows), pd.DataFrame(curve_rows)


# 관찰한 점수 변화와 승인 가능 여부를 분리
def compare(baseline, candidate, old_classes, new_classes, manifest):
    delta = candidate['macro_f1'] - baseline['macro_f1']
    change = new_classes[['gas_id', 'gas', 'support']].copy()
    for metric in ['precision', 'recall', 'f1', 'predicted_count']:
        change['official_' + metric] = old_classes[metric]
        change['candidate_' + metric] = new_classes[metric]
        change[metric + '_delta'] = new_classes[metric] - old_classes[metric]
    change['recall_drop_notice'] = change.recall_delta < -RECALL_DROP_NOTICE
    reasons = []
    if change.support.lt(MIN_VALIDATION_SUPPORT).any():
        reasons.append('일부 가스의Validation 표본이5개 미만')
    if manifest.get('physical_independence_verified') is not True:
        reasons.append('세션의 물리적 독립성은 확인되지 않음')
    reasons.append('단일 개발Validation이며 독립 최종Test가 아님')
    result = dict(
        observed_outcome='향상 관찰' if delta > 0 else ('저하 관찰' if delta < 0 else '변화 없음'),
        macro_f1_delta=delta,
        accuracy_delta=candidate['accuracy'] - baseline['accuracy'],
        severe_recall_drop_gases=change.loc[change.recall_drop_notice, 'gas'].tolist(),
        diagnostic_recall_drop_threshold=RECALL_DROP_NOTICE,
        assessment='평가 불충분 · 후보 검토 전용', assessment_reasons=reasons,
        approval_eligible=False, automatic_replacement=False,
    )
    return result, change
