# 자료 분할·클래스 구성·중복 검사 공통 함수





import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedGroupKFold

from .data import GASES

SELECTED = [1, 2, 3, 6, 9, 17, 65, 121]
EXPECTED_COUNTS = [445, 1244, 1586, 161, 197, 2300, 3613, 294, 470, 3600]


# 계산 결과를 HTML 표로 변환


# 훈련·평가 자료 중복 확인
def audit_split(frame, train, test, name, groups):
    left, right = frame.iloc[train], frame.iloc[test]
    overlap = set(groups.iloc[train]) & set(groups.iloc[test])
    return dict(
        name=name,
        train_n=len(left),
        test_n=len(right),
        train_batches=sorted(map(int, left.batch.unique())),
        test_batches=sorted(map(int, right.batch.unique())),
        missing_train=sorted(set(GASES) - set(map(int, left.gas.unique()))),
        missing_test=sorted(set(GASES) - set(map(int, right.gas.unique()))),
        row_overlap=len(set(train) & set(test)),
        duplicate_feature_groups=len(overlap),
        test_rows_matching_train=int(groups.iloc[test].isin(overlap).sum()),
        train_class_counts={str(g): int((left.gas == g).sum()) for g in GASES},
        test_class_counts={str(g): int((right.gas == g).sum()) for g in GASES},
    )


# 분할별 표본 수와 누락 가스 확인
def build_split_audits(frame, groups, seed):
    indices = np.arange(len(frame))
    # 가스 비율을 유지하며 자료 분할
    train, test = train_test_split(indices, test_size=0.2, stratify=frame.gas, random_state=seed)
    audits = [audit_split(frame, train, test, 'A_stratified_random_80_20', groups)]
    assignments = pd.DataFrame(
        {
            'row_id': frame.row_id,
            'feature_group': groups,
            'random_split': np.where(np.isin(indices, test), 'test', 'train'),
        }
    )
    if audits[0]['duplicate_feature_groups']:
        splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)
        train, test = next(splitter.split(indices, frame.gas, groups))
        audits.append(audit_split(frame, train, test, 'A_group_safe_approx_80_20', groups))
        assignments['group_safe_split'] = np.where(np.isin(indices, test), 'test', 'train')
    for end in (1, 3):
        for target in range(end + 1, 11):
            train = indices[frame.batch <= end]
            test = indices[frame.batch == target]
            audits.append(audit_split(frame, train, test, f'B_fixed_1-{end}_to_{target}', groups))
    for end in range(2, 10):
        train = indices[frame.batch <= end]
        test = indices[frame.batch == end + 1]
        audits.append(audit_split(frame, train, test, f'B_expanding_1-{end}_to_{end+1}', groups))
    return audits, assignments


# 자료 불러오기 및 분석 결과 저장


# 모델 비교에 사용할 평가 원칙 정리
def evaluation_plan(audits):
    return '''# 모델 비교 실험 설계 (미실행)

## 공통 데이터와 모델
입력은 f001–f128만 사용한다. gas는 타깃, batch/source_line/row_id는 메타데이터다.
Logistic Regression, Random Forest, SVM(RBF)을 같은 표본·레이블·분할·평가지표로 비교한다.
세 모델 모두 Pipeline(StandardScaler, estimator)을 기본 조건으로 정한다. Random Forest에도
동일한 스케일링 조건을 적용할 수 있다. 특징 선택·PCA·대체·이상치 처리·재표본화는 기본 실험에서 사용하지 않는다.
추후 필요하면 Train 내부의 각 Fold에서만 Fit하는 파이프라인 단계로 추가하고 공통 ablation으로 비교한다.
EDA 결과를 보고 유리한 특징·클래스를 사후 선택하지 않는다. 모델의 기본값과 버전, LR 반복 한도,
SVM 커널, RF seed를 실행 전 명시하며, 이번에는 분류기 생성·Fit·튜닝을 수행하지 않았다.

## A. Stratified Random Split
전체 자료에서 seed=42, Train 80%, Test 20% 계층 분할을 미리 기록했다.
모든 모델은 split_manifest.csv의 같은 행 목록을 사용한다. 정확 중복 특징이 양쪽에 걸치면
일반 분할은 누수 진단용으로만 남기고 StratifiedGroupKFold(5개 Fold)의 첫 Fold를 약 20% holdout으로 사용한다.
그룹 분할의 클래스별 수와 크기는 재확인한다. 같은 특징에 상충하는 레이블이 있으면 출처 확인 전 학습을 중단한다.
내부 검증은 Train 내부 5-fold StratifiedKFold(shuffle=True, random_state=42),
중복이 있으면 StratifiedGroupKFold로 대체한다. 가장 작은 클래스의 고유 그룹 수보다 Fold 수를 크게 잡지 않는다.
클래스당 그룹이 부족하면 Fold 수를 줄이고 사유를 보고한다. Test를 내부 검증이나 설정 결정에 사용하지 않는다.
표본의 독립성과 동일 분포 가정은 보장되지 않으므로 이 평가는 동일 수집 집합 내 기준 성능으로 해석한다.

## B. Batch 기반 시간순 분할
주 실험은 Batch 1만 Train으로 고정하고 Batch 2–10 각각을 Test로 평가한다.
보조 실험은 Batch 1–3으로 Train을 고정하고 Batch 4–10을 각각 평가한다.
적응에 따른 학습 자료 증가와 시간 변화의 혼동을 구분하기 위해,
확장 창 Train=Batch 1..k, Test=Batch k+1 (k=2..9)은 별도 보조 표로 보고한다.
Batch 번호의 순서만 사용하며 숫자 간격을 월 간격으로 사용하지 않는다.
학습 Batch가 하나인 주 실험은 Batch 간 시간순 내부 검증이 불가능하다.
이때 Train 안의 계층/그룹 검증은 보조 안정성 진단으로만 사용하며 시간 일반화 검증이라고 부르지 않는다.
여러 학습 Batch가 있는 경우 forward validation: Train=1..j, Validation=j+1을 사용하고
외부 Test보다 앞선 Batch만 포함한다. 클래스 누락 Fold를 명시하고 임의로 미래 표본을 보충하지 않는다.
Train에 없는 클래스가 Test에 있으면 알려진 6종 분류를 온전히 검증할 수 없으므로
해당 분할을 부적격으로 표시하고, 새 클래스 문제를 별도로 논의한다.
Test에 특정 클래스가 없으면 해당 클래스 recall/F1은 NA와 support=0으로 보고한다.
미래 Batch가 Train과 같은 특징 벡터를 포함하면 미래 Test에서 해당 중복을 제외한 결과를 주 결과로 삼고
원래 평가 수, 제외 수, 클래스 구성, 원본 중복 포함 결과를 민감도 분석으로 함께 보고한다.
배치 내부 행 순서로 시계열 Fold를 만들지 않는다. 동일 측정의 변형·근접 중복은 정확 중복 검사로 보장되지 않는다.

## 지표와 공정성
Accuracy, macro-F1, balanced accuracy(평가 Batch에 실제 존재하는 클래스의 평균 recall),
클래스별 precision/recall/F1/support와 고정 6×6 confusion matrix를 제공한다.
6종 모두 있는 Test는 6-class macro-F1을 주 지표로 사용한다.
누락 클래스가 있는 Test는 present-class macro-F1을 보고하고 그 클래스 집합을 명시한다.
고정 6-class zero-fill macro-F1을 보조 지표로 함께 표시하여 클래스 구성이 다른 Batch끼리의 단순 비교를 피한다.
분할별·모델별 paired 비교, 전체 표본 가중 집계와 Batch 동일 가중 집계를 구분한다.
소수 클래스 support와 클래스별 결과를 함께 해석하며 accuracy만으로 선정하지 않는다.
불확실성은 동일 Test 표본의 paired bootstrap을 고려하되 독립 표본 가정을 밝히고,
Batch 수가 적다는 한계와 연속 수집 의존성 때문에 신뢰구간을 과신하지 않는다.
class_weight/resampling, 특징 선택, 튜닝은 이번 범위 밖이며 추후 모든 모델에 동일한 검증 예산·원칙을 적용한다.
모든 scaler/selector/PCA는 매 Train/Fold에서 새로 Fit한다. EDA scaler/PCA는 저장하거나 재사용하지 않는다.
하이퍼파라미터 결정 전 Test 결과를 확인하지 않으며, 이번 EDA로 이미 전체 분포를 관찰했음을 기록한다.
완전히 독립적인 최종 확인에는 새 자료가 필요하다.

## 드리프트 해석
시간에 따른 성능 감소는 아직 확인하지 않았다. 향후 감소하더라도 센서 드리프트 외에
클래스 구성, 가스 농도, 실험 환경, 표본 수, 수집·전처리 변화가 원인일 수 있다.
같은 가스 내 특징 분포 변화와 Batch별 성능을 병렬로 비교하되 상관과 인과를 구분한다.
'''


# EDA 결과로 한글 보고서 생성


# 프로그램 실행 및 오류 안내


