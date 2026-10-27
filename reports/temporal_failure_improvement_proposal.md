# 8단계 개선 실험 제안 — 7단계 관찰에 근거한 설계

이번 단계는 저장 모델 진단만 수행했으며 새 학습·튜닝·전처리 변경 없음.

Batch 9 Toluene 101개를 세 모델 모두 틀림. SVM은 전부 Ethanol. Batch 10 Acetaldehyde 정분류 LR 0/RF 51/SVM 84개, 모두 오답 465개.

## 관찰·해석·미확인

### 1. 가스별 학습 불균형

- 관찰: Train Toluene 546, Acetaldehyde 484; Toluene의 85.53%가 Batch 6. 세 모델 모두 balanced 사용.
- 해석: 시기별 대표성 부족이 남을 수 있음. 클래스 가중치만으로 시기·농도 범위는 복구되지 않음.
- 미확인: 동일 분할의 새 대조 학습 없이 불균형의 독립 효과 추정 불가.

### 2. Train–미래 특징 이동

- 관찰: 동일 가스의 128개 특징 Wasserstein·표준화 꼬리값·Train 근접성 계산표 참조.
- 해석: 관측 특징 공간의 이동이 오류와 함께 존재하는지 검토 가능.
- 미확인: 분포 이동의 원인과 성능 저하의 인과 기여도는 미확인.

### 3. 특정 특징 의존

- 관찰: 고정 LR 표준화 계수 및 RF 중요도·상관관계 CSV 기록. SVM 전역 중요도 미산출.
- 해석: 이동이 큰 특징과 모델 사용 특징의 겹침은 후속 Train 내부 검증 후보.
- 미확인: 특징 제거·대조 재학습 없이 해당 특징이 실패 원인인지 확정 불가.

### 4. 다른 가스 특징 공간 중첩

- 관찰: 같은 가스보다 다른 가스 Train 표본이 가까운 비율과 실제 오분류 방향 기록.
- 해석: 표준화 거리에서 경계 혼동과 양립하는 근거. 화학적 유사성의 증거는 아님.
- 미확인: 128차원 거리와 일부 그림만으로 실제 클래스 분포 중첩의 전체 구조 확정 불가.

### 5. 새로운 시기·조건 일반화 부족

- 관찰: Batch 9 Toluene은 3개 모두 실패. Batch 10 Acetaldehyde Recall은 LR 0%, RF 8.5%, SVM 14%.
- 해석: 일부 가스·Batch의 공통 어려움과 모델별 한계가 함께 존재함.
- 미확인: 농도·환경·측정 세션 및 새 시기 자료 없이 드리프트·환경 효과를 분리할 수 없음.

## 개선 우선순위

### 1. 학습 데이터의 시기·가스 대표성 및 시간순 반복 검증

- purpose: Toluene Train의 Batch 6 집중, 미래의 공통 실패와 작은 Validation 가스 표본
- expected: 어떤 시기에 효과가 유지되는지 확인하고 농도·조건 범위의 공백 파악
- leakage_risk: 평가 Batch를 창 선택·튜닝에 재사용하면 낙관 편향
- validation_scope: 기존 과거 창으로 탐색 가능. 대표성 확보 효과의 독립 확인은 새 자료 필요

### 2. Train 내부의 특징 안정성 평가·선택

- purpose: 조건부 특징 이동과 상관 특징 중복, LR/RF 의존 지표
- expected: 불안정 특징의 영향 감소 여부 검증; 유용한 정보 손실도 점검
- leakage_risk: 이번 평가 기반 상위 이동 특징 목록을 바로 제거하면 평가 정보 유입
- validation_scope: 각 과거 Train 내부에서 선택 Fit, 외부 미래 창에서 6종 성능·최저 Recall 확인

### 3. 제한된 LR/SVM/RF 결합 가능성 검토

- purpose: Batch 10 Acetaldehyde에서 RF·SVM의 정분류 표본은 다르나 공통 실패 465개
- expected: 상보적 오류 일부 감소 가능. 단순 다수결은 공통 실패와 소수 정답을 놓칠 수 있음
- leakage_risk: Batch 9/10 정답으로 가중치·게이트 선택 금지
- validation_scope: Train 내부 시간순 예측으로 결합 설정 결정 후 미래 창 평가; 독립 성능 미확인

### 4. 드리프트 보정 및 Batch 특성 정규화의 운영 가능성 검토

- purpose: 같은 가스에서도 관측 특징 이동이 있고 센서·농도·환경 원인 분리가 어려움
- expected: 참조 측정이 확보되면 시기별 편차 감소 가능; 가스 신호 제거 위험도 있음
- leakage_risk: 평가 정답·미래 전체 Batch 평균으로 정규화하면 누수 또는 전이적 설정이 됨
- validation_scope: 과거 Train 기반 보정 또는 운영 시 확보 가능한 무정답 참조 조건부터 사전 정의

### 5. 다른 모델의 소규모 대조 실험

- purpose: 모델별 오분류 방향이 다르지만 세 모델 공통 실패도 존재
- expected: 결정 경계 가정의 영향을 비교; 데이터 범위 부족을 모델 교체만으로 해결 못할 수 있음
- leakage_risk: 같은 미래 Batch를 반복 보고 모델 종류를 늘리는 선택 편향
- validation_scope: 대표성·반복 검증을 먼저 정한 후 제한된 후보 수로 탐색; 이번 단계 미실행

## 사전 설계와 평가 제한

현재 모델과 6단계 선정은 유지. 다음 단계 실행 시 먼저 후보 수·동점 규칙·클래스 보호 기준을 고정할 것.
과거 구간 예시: Train 1–3→Validation 6, Train 1–6→Validation 7, Train 1–7→Validation 8. 첫 창 Train의 Toluene 79개, Validation 6의 Acetaldehyde 29개, Validation 8의 Toluene 18개로 시기·표본 제한을 함께 보고할 것. 각 창의 전처리·특징 선택·가중치·앙상블 설정은 그 창의 Train 안에서만 결정하거나 내부 시간순 검증을 사용할 것. Batch 9–10은 현재 진단에 이미 노출됐으므로 나중에 고정 평가하더라도 탐색적 평가로만 표현할 것.

Batch 9/10의 정답이나 전체 배치 통계로 보정·특징 선택·결합 가중치를 맞추지 말 것. 새 시기 자료를 확보하면 후보를 고정한 뒤 독립적으로 평가할 것. 드리프트 보정은 기준 가스·농도·환경 또는 운영 시 확보 가능한 참조 자료의 조건을 명확히 할 것.

특징 그림은 동일 가스 Train 대비 Wasserstein/동일 가스 Train SD 상위 3개씩을 진단 목적으로 선정했음. 이 목록을 바로 모델 입력 선택으로 사용하면 평가 기반 선택 편향이 생김.

## 최종 관찰과 반례

- Batch 9 Toluene 101개 모두 다른 가스의 Train 표본이 더 가까웠다. 같은 가스 최근접 거리 중앙값 2.305, 다른 가스 2.065(저장 SVM Train 표준화 128차원 거리).

- 그중 최근접 Train 가스는 Acetaldehyde 97·Ethanol 3·Acetone 1개였다. 하지만 SVM은 전부 Ethanol로 예측했다. 따라서 단순한 최근접 가스만으로 SVM의 오분류 방향을 설명할 수 없다.

- Batch 9 Toluene의 128개 평균 정규화 Wasserstein은 1.192로, Recall 77.78%였던 Batch 8의 1.248보다 작았다. 평균 분포 거리 증가만으로 Recall 변화를 단조롭게 설명할 수 없다.

- Batch 10 Acetaldehyde는 80.83%에서 다른 가스의 Train 표본이 더 가까웠다. 평균 정규화 Wasserstein은 Batch 7 0.920→Batch 10 1.302였다. 이때 SVM Recall은 61.56%→14%로 낮아졌다. 동반 변화이며 인과 증거가 아니다.

- Batch 9 Toluene과 Batch 10 Acetaldehyde 모두 모든 특징이 전체 Train 기준 |z|≤3이었다. 두 실패를 미래의 극단값 발생만으로 설명할 근거가 없다. 기준은 전체 Train SD이므로 동일 가스의 상대적 이동이나 다변량 변화를 배제하지 않는다.

- Batch 9 Toluene의 지지벡터 최대 RBF 유사도 중앙값은 0.967였다. 유사도가 확률이나 정답 보장은 아니며 단순히 모든 학습 표본에서 멀어졌다는 설명도 충분하지 않다.

- Batch 10에서 SVM만 맞히고 LR이 틀린 Acetaldehyde 84개를 LR은 Ethanol 71개, Ammonia 11개, Acetone 2개로 예측했다. 세부 표본 ID와 예측은 row_predictions.csv, 교차표와 특징 요약은 lr_svm_prediction_crosstab.csv 및 lr_svm_error_group_features.csv에 기록했다.

- 상위 이동 특징 사이 Train 상관관계가 높았다. f036–f044 r=0.987, f107–f099 r=0.994. 일부 특징의 중복 표현 가능성과 중요도 해석의 한계가 있다. 이동 특징을 평가 결과에 맞춰 제거하지 않았다.

## 보존·테스트 결과

전체 테스트 57개 통과, 2개 실패. 신규 테스트 8개 모두 통과. 기존 실패는 과거 소스 SHA 불일치와 과거 기록의 zNex~$haremetrics.csv 부재이며 테스트·과거 기준은 수정하지 않았다. 기존 파일 293개와 원본 10개 해시 보존 확인. 연구 모델 재학습·튜닝·전처리 Fit 없음. 전체 기존 테스트에는 과거의 소규모 예제 Fit 검사가 포함되며 저장 연구 모델을 갱신하지 않는다.

## 실행 방법

```text
.venv\Scripts\python.exe -B -X utf8 -m src.temporal_failure_diagnostics
.venv\Scripts\python.exe -B -X utf8 -m pytest -q -p no:cacheprovider --junitxml=outputs/temporal_failure_diagnostics/test_results.xml
.venv\Scripts\python.exe -B -X utf8 -m src.temporal_failure_review
```

기존 경로가 있으면 진단 코드는 중단함. 재실행은 1–6단계를 보존한 복제본에서 7단계 출력이 없는 상태로 수행해야 함. 기존 산출물 삭제·덮어쓰기 금지.
