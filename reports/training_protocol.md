# 고정 기준선 학습 프로토콜

실행 전 EDA 보고서와 evaluation_design.md를 검토했으며, 이번 사용자 요청이 이전 설계보다 우선한다.

- A: seed 42로 계층 Test 20%를 먼저 떼고, 나머지 80%에서 25%를 Validation으로 분리한다. 최종 60/20/20.
- 기존 EDA의 20% Test 행을 그대로 유지한다. 세 모델은 같은 분할을 공유한다.
- B_early: Train=1, Validation=2, Test=3–10. 과거 Batch 1 고정 학습 목표를 유지하며 Validation을 별도로 유보한다.
- B_history: Train=1–3, Validation=4, Test=5–10. 기존 보조 고정 학습 조건에 Validation을 추가한다.
- B_history Validation 4 및 Test 5에는 Toluene 없음. B_early Test 3–5에도 없음.
- 확장 창은 이번 고정 기준선 비교에서 실행하지 않는다. 미래 자료로 Train/전처리를 보충하지 않는다.
- 각 실험의 세 파티션을 한 번 결정한 뒤 모델별로 같은 행을 사용한다.
- 전처리는 imputer(median), LR/SVM의 scaler를 각 Train에만 Fit한다. RF는 scaler 없이 학습한다.
- 실제 결측·Inf는 없고, 특징 128개 전체를 사용한다. 이상치 삭제·PCA·선택·재표본화 없음.
- 모델 설정은 training_config.json으로 고정한다. LR 반복 한도 10,000은 사전 수렴 여유이며 탐색 없음.
- Validation 성능은 별도 보고만 한다. 설정 변경, 최종 모델 선정, Train+Validation 재학습, early stopping 없음.
- Test 결과는 성능 보고에만 사용한다. 총 9개 파이프라인을 저장한다.
- 정확 중복의 파티션 간 누수 또는 상충 레이블이 발견되면 학습 중단 후 분할 정책을 재설계한다.
- 주 macro 지표는 평가 집합에 실제 존재하는 클래스 평균, 없는 클래스의 개별 지표는 NA/support=0.
- 고정 6종 zero-fill macro 지표도 별도 보고한다. 예측이 없는 실제 클래스의 precision/F1은 0.
- 안정성은 동일 클래스가 존재하는 공통 미래 Batch 6–10의 동일 가중 mean/min/SD로 보조 평가한다.
- 신뢰구간, 반복 시드, 학습량 통제는 이번에 미실행이다. 수치적 순위를 최종 모델 선정으로 해석하지 않는다.
- 랜덤 분할은 모든 Batch에서 학습하며 더 많은 표본을 쓰므로 A−B 차이는 드리프트만의 효과가 아니다.
- 기존 EDA 파일과 원본 데이터의 실행 전후 해시를 비교한다. 새 출력은 outputs/model_comparison/에 둔다.

실행: `.venv\Scripts\python.exe -m src.train_models`

검증: `.venv\Scripts\python.exe -m pytest -q`

현재 환경의 정확한 패키지 버전은 requirements-lock.txt와 새 run_manifest.json에 기록한다.
재실행은 모델과 새 비교 산출물을 덮어쓰며 기존 EDA 산출물은 보존한다.
