# 16단계 연구 한계

과거 Fold는 반복 사용한 개발 검증 자료이며 독립 Test가 아님. 학습 구간이 겹치는 Fold를 독립 반복 표본으로 취급하지 않음. Batch 9~10 신규 평가 없음. 공식 Model A 유지.

- 수치는 관찰 결과이며 새 알고리즘의 원인 효과나 센서 드리프트 단독 원인 확정은 아님.

- 각 Fold의 Train 행·Validation 행·정답·128특징은 동일. HGB는 표준화 없이 사용하므로 알고리즘과 적합한 전처리를 함께 비교한 대조임.

- HGB는 native NaN을 지원하지만 사전 정책대로 Train 중앙값 처리. class_weight=balanced를 지원하며 Train 가스 빈도만 사용. sample_weight 중복 적용 없음.

- HGB early_stopping=False·validation_fraction=None으로 외부·내부 Validation을 학습에 사용하지 않음. class_weight 빈도식은 SVM과 같아도 학습 손실과 적용 효과는 다름.

- Fold A 초기 Toluene 학습79개, Fold C Toluene 평가18개. 한 표본 Recall 변화5.56pp이며 작은 support 및 겹치는 학습 구간 때문에 독립 미래 성능의 신뢰구간이나 유의성 미주장.

- 오류 상호 보완성은 저장된 두 예측을 비교했을 뿐 새 앙상블·Oracle·가중치 조절을 실행하지 않음.

- 실패·혼동 방향·예측 비율을 전부 공개. 새로운 시기·농도·환경·세션 정보의 독립 검증 필요.

- 기존 5개 실패: 과거 소스 SHA, 임시 파일 후보 부재, 기존 전역 모델 목록 고정 충돌3건. 기존 테스트·과거 해시 기준 미수정.
- 단일 고정 HGB 설정의 결과이며 HGB 전체 성능 상한이 아님. 결과 확인 후 추가 탐색·공식 모델 교체·Commit·Push 없음.
