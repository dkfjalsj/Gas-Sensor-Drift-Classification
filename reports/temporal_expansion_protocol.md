# 6단계 시간순 확장 학습 사전 계획

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
