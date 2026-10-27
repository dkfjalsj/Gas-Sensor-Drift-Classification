# 5단계 사전 고정 실험 계획

사용자는 과거 Test 일부를 개발 자료로 바꾸지 않고 엄격 분리를 유지하도록 명시했다.
과거 모든 Test 행 ID의 합집합 12,518개를 새 Train/Validation에서 제외한다.
Train=Batch 1의 남은 370개(Toluene 59), Validation=Batch 2의 남은 1,022개(Toluene 4),
최종 탐색적 Test=Batch 3–10 전체 12,221개(Toluene 1,754)로 고정한다.
Train/Validation 모두 6종이 존재하고, 행·정확 특징 중복 및 시간 순서를 확인한다.
Batch 1–2의 과거 랜덤 Test 297개는 이번 새 학습·검증·평가에서 제외한다.

## 실험과 비용
- A: 기존 시간순 모델 6개를 재학습 없이 재예측하고 기존 지표와 대조한다. Test 대조는 후보를 고정한 후 수행한다.
- B: 저장된 Batch 1 / Batch 1–3 모델을 공통 미래 Batch 6–10에서 비교한다.
  새 Batch 확장 학습은 과거 Test를 학습·튜닝에 넣게 되므로 실행하지 않는다.
- C: 엄격 Train/Validation에서 세 모델의 class_weight=None/balanced 비교.
- D: LR/SVM에 StandardScaler/RobustScaler 비교. RF는 무스케일 유지.
  PCA·특징 선택은 Train 370개, Toluene 검증 4개의 제한과 탐색 예산 때문에 이번에는 실행하지 않는다.
- E: 초기 비교의 모델별 Validation 승자가 전처리/가중치를 고정하고 2개 파라미터 후보만 추가.
  LR C=0.1/10, RF (200 trees) 또는 (100 trees, depth=12, leaf=3),
  SVM (C=10,gamma=scale) 또는 (C=1,gamma=0.001).
  RF 두 번째 조건은 depth와 leaf를 함께 바꾸므로 개별 인과효과로 해석하지 않는다.
총 8개 초기 + 6개 후속 = 최대 14회 Fit. 모든 조합의 전체 격자 탐색은 하지 않는다.

## 선정 규칙
동일 계열 기본 모델보다 Validation의 다른 5종 평균 F1이 3pp 넘게 낮아진 설정은 제외한다.
이는 사전 탐색 보호 규칙이며 운영 허용오류나 통계적 유의성 기준은 아니다.
남은 후보 중 최고 Validation macro-F1의 1pp 이내를 근접 후보로 보고
Toluene F1 → Toluene Recall → 다른 5종 F1 → macro-F1 → 고정 실행 순서로 계열 대표를 정한다.
후속 튜닝의 초기 부모와 최종 대표 모두 같은 규칙을 사용한다.
Toluene 검증 표본이 4개뿐이므로 세 계열 대표를 공동 검증 후보로 유지한다.
대표 중 Validation macro-F1이 가장 높은 모델을 우선 검증 순서로만 제시한다.
Validation이 단일 Batch여서 Batch 간 안정성을 선정 기준으로 추정할 수 없다.
선정 이후 Test 변동은 설명용이며 후보 변경이나 재튜닝에 사용하지 않는다.

## 누수·보존
각 파이프라인의 imputer와 scaler는 해당 Train 370개에서만 Fit한다.
기존 EDA의 PCA/스케일러를 재사용하지 않는다. Validation을 합쳐 재학습하지 않는다.
Validation 결정과 모델 해시를 먼저 동결한 뒤 Test 예측을 실행한다.
기존 모델·보고서·원본·테스트·과거 해시는 덮어쓰지 않는다.
새 모델은 models/improvement_strict/, 새 결과는 outputs/model_improvement/에 저장한다.
모든 Test는 이전에 관찰한 자료이므로 독립 성능이 아닌 탐색적 성능이다.
새 시기의 미관찰 자료 없이는 최종 확정 모델을 선언하지 않는다.
