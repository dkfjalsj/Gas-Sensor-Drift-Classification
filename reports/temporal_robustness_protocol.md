# 8단계 사전 실험 계획

## 고정 분할 및 목적
Fold A: Train 1–3 → Validation 6. Fold B: Train 1–6 → Validation 7.
Fold C: Train 1–7 → Validation 8. Train/Validation 6종 및 support·중복 점검.
Train 범위가 겹치고 이전 Validation이 다음 Train에 포함되는 확장 창이므로 독립 반복 표본이 아님.
후보 확정 후 Batch 9–10은 기존 Test를 재사용한 회고적·탐색적 평가로만 사용.
최종 평가 모델은 Fold B(Train1–6) 바이트를 유지해 기존 6단계와 학습 범위를 통제함.
Train1–8 재학습은 이번 실험에 포함하지 않음.

## 설정 수와 전처리
3모델×6특징 조건=18개 설정, 3 Fold에서 분류기54회 Fit. 추가 결합4개=총22개 설정.
전체128 / min-max 범위 정규화 Train 분산 상위115 / abs Pearson>.98 중복 제거 /
Train 동일 가스 Batch 평균 이동이 작은64 / ANOVA SelectKBest32 / SelectKBest64.
분산법은 특징 단위 차이를 줄인 후 하위13개를 제거하는 제한적 대조임.
안정성은 같은 가스 Train 평균과 각 Train Batch 평균의 절대차를 전체 Train SD로 나눈 뒤
가스·Batch 그룹 동일 가중 평균. 2개 이상 Train Batch가 있는 가스만 사용.
작은 그룹의 평균 불확실성, 낮은 이동이 높은 구별 능력을 보장하지 않는 한계 보고.
상관 제거는 원래 특징 순서의 탐욕적 결정이며 최적 특징 집합을 의미하지 않음.
7단계 미래 특징 목록은 사용하지 않음. 미래 Batch·정답·통계로 특징 선택 Fit 금지.
median 결측값 처리 → 특징 선택 → LR/SVM StandardScaler → 분류기. RF 무스케일.
LR balanced C=.1 / RF balanced100 trees / SVM balanced C1,gamma=scale. 기존 나머지 설정 유지.
seed42, BLAS2, RF n_jobs=-1. 이번에는 특징 효과 분리를 위해 추가 파라미터 탐색 없음.

## 결합
full3 hard voting, 각 계열 대표3 hard voting, 대표3 순위점수 동일 가중,
대표3 순위점수 SVM2배(LR/RF/SVM=1/1/2). 순위점수5..0, 모델 내부 순위만 결합.
hard 동점은 SVM 예측 우선, 순위 동점은 SVM 순위 우선, 이후 작은 클래스 번호.
SVM probability=False이고 시간순 확률 보정 품질을 검증하지 않았으므로 Soft Voting 미실행.
순위 결합은 확률 결합이 아니며 신뢰도 크기 정보는 버림.
계열 대표 선정 후 같은 Fold로 결합을 비교하므로 중첩 검증이 아니며 선택 낙관 편향이 남음.

## 선정 규칙
주 지표는 세 Fold Macro F1 동일 가중 평균. 전체 Fold 합산 Macro F1 별도 기록.
계열 대표는 동일 계열 all을, 전체 후보는 SVM_all을 보호 기준의 참조로 사용.
나머지4종 평균 F1이 참조보다3pp 초과 하락하거나 그4종 각각의 Fold 평균 F1이
10pp 초과 하락하면 제외. 기준 모델은 항상 포함 가능.
유효 설정 최고 주 지표의0.5pp 이내에서 Recall0 Fold/가스 조합 수가 적은 것,
높은 최소Recall, 높은 min(Toluene 평균F1,Acetaldehyde 평균F1), 높은 합산Macro F1,
낮은 Fold SD, 고정 설정 순서로 선택. 이 수치는 사전 탐색 규칙이며 통계적 동등성·운영 기준 아님.
최고 평균 설정과 보호·동점 규칙을 적용한 후보를 구분해서 보고.
0% Recall은 숨기지 않으며 후보라도 최종 확정 모델이라고 주장하지 않음.
후보 및 모델 SHA를 고정한 뒤에만9–10 평가. 결과가 나빠도 후보·가중치·특징 변경 금지.

## 보존과 테스트
1–7단계 코드·원본·모델·보고서·과거 해시 수정 금지. 모델은 신규 경로에 저장.
기존2건 실패와 별도로7단계 전체 모델 목록 고정 검사는 승인된 신규 모델 추가로 실패 예상.
기존 테스트 수정 없이 과거 모델 각각의 해시 보존과 신규 재현성·누수 검사를 추가.
Commit·Push 금지.
