# 개선된 모델 후보 선정 근거

이 모델들은 최종 확정 모델이 아닌 탐색적 검증 후보다.
사용자 확인에 따라 모든 과거 Test 행을 새 Train/Validation에서 제외했다.
새 Train=Batch 1의 370개(Toluene 59), Validation=Batch 2의 1,022개(Toluene 4).
새 Batch 확장 학습은 금지 조건과 충돌하므로 저장 모델의 고정 비교로만 수행했다.

## 선정 시점과 기준
Validation 결정 시각: 2026-10-27T09:49:49.367943+09:00
우선 검증 후보: **LR_robust**
공동 검증 후보: LR_robust, RF_tune_depth12_leaf3, SVM_tune_C10

계열별 기본 모델보다 다른 5종 Validation 평균 F1이 3pp 초과 악화된 설정은 제외했다.
가장 높은 Validation macro-F1의 1pp 이내 설정에서 Toluene F1, Recall,
다른 5종 F1, 전체 macro-F1, 고정 순서로 대표를 골랐다.
3pp/1pp는 실행 전에 기록한 탐색 규칙이며 업무 허용오류·유의성 기준은 아니다.
Validation Toluene 4개로는 견고한 단일 우승 모델 판단이 어려워 세 계열 대표를 공동 검증 후보로 유지했다.
공동 후보가 동등한 성능이라는 뜻은 아니다. 우선 검증 순서는 대표들의 Validation macro-F1에 따른다.

## Validation 근거
```text
             trial_id             family    group  accuracy  macro_f1  weighted_f1  toluene_recall  toluene_f1  other_five_macro_f1  min_class_recall
            LR_robust LogisticRegression D_scaler  0.879648  0.743923     0.860160             1.0    0.800000             0.732708               0.0
RF_tune_depth12_leaf3       RandomForest E_tuning  0.752446  0.706658     0.763262             1.0    1.000000             0.647989               0.0
         SVM_tune_C10            SVM_RBF E_tuning  0.684932  0.706510     0.724213             1.0    0.888889             0.670034               0.0
```

## 탐색적 Test 결과 (선정 후 확인)
```text
                       accuracy  macro_f1  weighted_f1  toluene_recall  toluene_f1  other_five_macro_f1
trial_id                                                                                               
LR_robust              0.486458  0.371077     0.382329        0.019954    0.037057             0.437881
RF_tune_depth12_leaf3  0.429916  0.312995     0.330461        0.000000    0.000000             0.375593
SVM_tune_C10           0.363555  0.309348     0.308113        0.014823    0.028729             0.365471
```

Test 평가 전에 validation_decisions.json과 모델 해시를 고정했다.
Test 성능이나 Batch SD를 보고 후보·파라미터를 바꾸지 않았다.
Validation은 단일 Batch이므로 Batch 간 안정성을 선정 근거로 측정할 수 없었다.
Test의 6–10 SD는 설명용이며 안정성은 신규 시기의 자료로 추가 검증해야 한다.
기존 Test를 재사용한 이번 평가는 독립 성능이 아니다.
Toluene 검증 4개와 기존 전체 EDA·Test 관찰에 의한 선택 편향을 명시한다.
Toluene 개선이 다른 가스 악화와 맞바뀌는지는 improvement_deltas.csv와 클래스별 표를 함께 확인한다.
개선이 없거나 여전히 특정 가스에서 실패하면 이를 그대로 보고하며 운영 모델로 확정하지 않는다.

## 실제 성과 및 후보 유지의 의미

관찰: 이번 실험은 안정적인 미래 6종 분류라는 목표를 달성하지 못했다. Validation으로 고정한 후보는 유지하지만 운영 적합성을 확인한 모델은 아니다.

세 공동 후보 모두 Validation Acetaldehyde 87개와 Test Acetaldehyde 1,797개에서 Recall 0%였다. Train/Validation에 클래스가 존재하는 것과 잘 분류하는 것은 다르다.

LR_robust: Test Toluene Recall 2.00%, Toluene F1 3.71%. 동일 strict 기본 모델 대비 macro-F1 +3.46pp, Toluene Recall -0.74pp, 다른 5종 평균 F1 +4.42pp.

RF_tune_depth12_leaf3: Test Toluene Recall 0.00%, Toluene F1 0.00%. 동일 strict 기본 모델 대비 macro-F1 -1.15pp, Toluene Recall -0.11pp, 다른 5종 평균 F1 -1.33pp.

SVM_tune_C10: Test Toluene Recall 1.48%, Toluene F1 2.87%. 동일 strict 기본 모델 대비 macro-F1 -3.96pp, Toluene Recall +1.48pp, 다른 5종 평균 F1 -5.33pp.

LR의 RobustScaler는 전체 Test macro-F1을 높였지만 같은 Train의 기본 LR보다 Toluene Recall은 낮았다. SVM C=10은 Toluene Recall이 늘었지만 다른 5종 평균 F1이 약 5.33pp 낮아졌다. RF의 Validation 선택 설정도 미래 Test에서 일관된 개선을 보이지 못했다.

이 관찰은 사후 설명이며 Test에 맞춰 설정을 조정하거나 후보를 재선정하지 않았다. Toluene Validation 4개, 단일 Validation Batch, 초기 시기에 제한된 Train으로는 미래 안정성을 충분히 검증할 수 없다.
