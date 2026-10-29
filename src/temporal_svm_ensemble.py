# 시기별 SVM 오류 상호 보완성 진단 및 조건부 결합
# 사전 계획 고정·동일 표본 평가·기존 파일 보존 검사


import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from .data import ROOT, FEATURES, GASES
from .temporal_expansion import now
from .temporal_representativeness_control import budgets, sample_rows
from .nonlinear_feature_transformation import row_digest, digest

OUT = ROOT / 'outputs/temporal_svm_ensemble'
MODEL_DIR = ROOT / 'models/temporal_svm_ensemble'
FOLDS = {'A': (3, 6), 'B': (6, 7), 'C': (7, 8)}
EXPERTS = ['full', 'recent', 'spread']
CAUTION = ('새 독립 Test 없음. 과거 Fold는 반복 사용된 개발 검증 자료이며 학습 구간이 겹침. '
           'Batch 9~10 신규 평가 없음. 공식 Model A 유지.')
ORACLE_NOTE = ('정답을 알고 전문가를 선택한 가상 상한이며 실제 배포 가능한 모델이 아님. '
               'Accuracy·가스 Recall은 선택형 상한. Macro F1은 공동 오답에서 full 예측을 '
               '유지한 고정 Oracle의 점수이며 모든 오답 배치를 최적화한 수학적 상한은 아님.')


def save(name, rows):
    table = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    table.to_csv(OUT/f'{name}.csv', index=False, encoding='utf-8')
    return table


# 기존 정식 산출물·모델·코드의 지문 수집


# 예측 결과와 무관하게 고정 시기별 학습 행 선정
def expert_rows(frame, end, expert):
    if expert == 'full':
        return frame.index[frame.batch <= end].to_numpy()
    return sample_rows(frame, end, expert, budgets(frame)['mid'], 42)


# 이전 단계의 정확한 모델·행 기록 조회
def source_record(fold, expert):
    if expert == 'full':
        records = pd.read_csv(ROOT/'outputs/nonlinear_feature_transformation/model_registry.csv')
        row = records[(records.fold == fold) & (records.method == 'baseline')].iloc[0]
    else:
        records = pd.read_csv(ROOT/'outputs/temporal_representativeness_control/fit_records.csv')
        row = records[(records.fold == fold) & (records.setting == f'{expert}_mid') &
                      (records.seed == 42)].iloc[0]
    return dict(path=row.path, sha256=row.sha256)


# 저장 파이프라인의 Train 통계·설정·지원 벡터 검증
def audit_model(model, train, end):
    assert train.batch.max() <= end and len(train) == len(set(train.row_id))
    assert list(model.named_steps) == ['imputer', 'scaler', 'classifier']
    imputer, scaler, classifier = (model[n] for n in ['imputer', 'scaler', 'classifier'])
    assert imputer.strategy == 'median' and isinstance(scaler, StandardScaler)
    np.testing.assert_array_equal(imputer.feature_names_in_, FEATURES)
    np.testing.assert_allclose(imputer.statistics_, train[FEATURES].median())
    filled = imputer.transform(train[FEATURES])
    assert filled.shape == (len(train), 128)
    assert scaler.n_samples_seen_ == len(train)
    np.testing.assert_allclose(scaler.mean_, filled.mean(axis=0), atol=1e-10)
    np.testing.assert_allclose(scaler.var_, filled.var(axis=0), rtol=1e-9)
    assert isinstance(classifier, SVC)
    for key, value in dict(kernel='rbf', C=1., gamma='scale', class_weight='balanced',
                           random_state=42, decision_function_shape='ovr',
                           break_ties=False).items():
        assert classifier.get_params()[key] == value
    # 1.9의 기본 문자열도 확률 계산 비활성 상태임
    assert classifier.probability in [False, 'deprecated']
    assert not hasattr(classifier, 'predict_proba')
    np.testing.assert_array_equal(classifier.classes_, list(GASES))
    np.testing.assert_allclose(classifier.class_weight_,
                               len(train)/(6*train.gas.value_counts().sort_index()))
    transformed = scaler.transform(filled)
    np.testing.assert_allclose(classifier.support_vectors_, transformed[classifier.support_],
                               rtol=1e-8, atol=1e-9)
    return dict(train_n=len(train), train_max_batch=int(train.batch.max()),
                row_sha256=row_digest(train.row_id), input_sha256=digest(train[FEATURES]),
                scaler_n=int(scaler.n_samples_seen_), actual_gamma=float(classifier._gamma),
                train_only=True, feature_count=128, class_order='1,2,3,4,5,6')


# 사전 계획·전문가 구성·실행 게이트 고정


# 동일 표본의 정답·오답 일치와 가상 Oracle 계산
def complement(y, predictions):
    y, predictions = np.asarray(y), np.asarray(predictions)
    if predictions.ndim != 2 or predictions.shape[0] != len(y):
        raise ValueError('n rows by experts required')
    if not np.isin(predictions, list(GASES)).all():
        raise ValueError('Invalid gas mapping')
    correct = predictions == y[:, None]
    count = correct.sum(axis=1)
    disagreement = np.any(predictions != predictions[:, [0]], axis=1)
    oracle = np.where(count > 0, y, predictions[:, 0])
    return pd.DataFrame(dict(y_true=y, correct_experts=count,
                             all_correct=count == predictions.shape[1],
                             some_correct=(count > 0) & (count < predictions.shape[1]),
                             all_wrong=count == 0, disagreement=disagreement,
                             identical_wrong=(~disagreement) & (count == 0),
                             oracle_pred=oracle, full_pred=predictions[:, 0],
                             oracle_rescue=(count > 0) & ~correct[:, 0])), correct


# 다수결 또는 모델 내부 클래스 순위만 결합
def combine(predictions, scores=None, mode='hard_equal'):
    predictions = np.asarray(predictions)
    if predictions.ndim != 2 or predictions.shape[1] < 1 or not np.isin(predictions, list(GASES)).all():
        raise ValueError('Invalid expert predictions')
    if mode == 'hard_equal':
        totals = np.column_stack([(predictions == g).sum(axis=1) for g in GASES])
        primary = totals == totals.max(axis=1, keepdims=True)
        secondary = np.zeros_like(totals)
        secondary[np.arange(len(predictions)), predictions[:, 0]-1] = 1
    elif mode == 'rank_equal':
        scores = np.asarray(scores)
        if scores.shape != (predictions.shape[1], len(predictions), 6) or not np.isfinite(scores).all():
            raise ValueError('Finite experts×rows×6 OVR scores required')
        order = np.argsort(-scores, axis=2, kind='stable')
        points = np.empty_like(scores, dtype=int)
        np.put_along_axis(points, order, np.broadcast_to(np.arange(5, -1, -1), scores.shape), axis=2)
        totals = points.sum(axis=0)
        primary = totals == totals.max(axis=1, keepdims=True)
        secondary = points[0]
    else:
        raise ValueError('Unplanned ensemble mode')
    return np.argmax(np.where(primary, secondary, -1), axis=1) + 1


# 전체 Fold 기준 진단 게이트 재현
def gate_decision(metrics, classes, samples, provenance=True):
    experts = metrics[metrics.role == 'expert']
    best = experts.groupby('model').macro_f1.mean().max()
    oracle = metrics[metrics.model == 'oracle'].macro_f1.mean()
    means = classes.groupby(['model', 'gas_id']).recall.mean()
    focus = []
    for gas in [6, 4]:
        best_recall = max(means.loc[(expert, gas)] for expert in experts.model.unique())
        gain = means.loc[('oracle', gas)]-best_recall
        rescued = int(samples[samples.y_true == gas].oracle_rescue.sum())
        focus.append(dict(gas_id=gas, recall_gain=float(gain), rescued=rescued,
                          passes=bool(gain >= .02-1e-12 and rescued >= 10)))
    checks = dict(nonidentical=bool(samples.disagreement.any()),
                  partial_correct=bool(samples.some_correct.any()),
                  macro_gain=bool(oracle-best >= .01-1e-12),
                  focus_room=any(r['passes'] for r in focus), provenance=bool(provenance))
    return dict(checks=checks, passed=all(checks.values()), oracle_mean_macro_f1=float(oracle),
                best_expert_mean_macro_f1=float(best), oracle_macro_gain=float(oracle-best),
                focus=focus, decided_at=now(), oracle_warning=ORACLE_NOTE)


# 기준 대비 보호 조건 및 단독 최고 대비 추가 가치 계산
def summarize(metrics, classes):
    baseline = classes[classes.model == 'full'].set_index(['fold', 'gas_id'])
    best_single = metrics[metrics.role == 'expert'].groupby('model').macro_f1.mean().max()
    rows = []
    for name, sub in metrics.groupby('model', sort=False):
        gas = classes[classes.model == name].set_index(['fold', 'gas_id'])
        paired = gas[['precision', 'recall', 'f1']].join(
            baseline[['precision', 'recall', 'f1']], rsuffix='_base')
        mean_delta = (paired.recall-paired.recall_base).groupby('gas_id').mean()
        other = paired[paired.index.get_level_values('gas_id').isin([1, 2, 3, 5])]
        delta = sub.macro_f1.mean()-metrics[metrics.model == 'full'].macro_f1.mean()
        zero = int(gas.recall.eq(0).sum())
        new_zero = int((paired.recall.eq(0) & (paired.recall_base > 0)).sum())
        guards = dict(macro_guard=bool(delta >= .005-1e-12),
                      gas_recall_guard=bool((mean_delta >= -.05-1e-12).all()),
                      other_guard=bool((other.f1-other.f1_base).mean() >= -.02-1e-12),
                      zero_guard=zero <= int(baseline.recall.eq(0).sum()), new_zero_guard=new_zero == 0)
        positive = delta > 1e-12 or bool(((paired[['precision', 'recall', 'f1']].to_numpy()-
                    paired[['precision_base', 'recall_base', 'f1_base']].to_numpy()) > 1e-12).any())
        role = sub.role.iloc[0]
        status = ('A' if all(guards.values()) else ('B' if positive else 'C')) if role == 'ensemble' else role
        rows.append(dict(model=name, role=role, mean_macro_f1=sub.macro_f1.mean(),
                         mean_accuracy=sub.accuracy.mean(), mean_weighted_f1=sub.weighted_f1.mean(),
                         fold_sd=sub.macro_f1.std(ddof=0), macro_delta=delta,
                         above_best_single=sub.macro_f1.mean()-best_single,
                         mean_toluene_recall=gas.xs(6, level='gas_id').recall.mean(),
                         mean_acetaldehyde_recall=gas.xs(4, level='gas_id').recall.mean(),
                         min_recall=gas.recall.min(), zero_pairs=zero, new_zero_pairs=new_zero,
                         other_four_f1=other.f1.mean(), worst_fold_delta=float((sub.set_index('fold').macro_f1-
                         metrics[metrics.model == 'full'].set_index('fold').macro_f1).min()),
                         **guards, balanced_success=role == 'ensemble' and all(guards.values()), conclusion=status))
    return pd.DataFrame(rows)


# 원본·기존 파일·사전 규칙 보존 검사


# 저장 전문가 진단 후 게이트 통과 시에만 결합 평가


# 계산 완료 표에서 JSON·보고서만 재생성


# 실행 전 고정과 진단·결합 실행 분리


