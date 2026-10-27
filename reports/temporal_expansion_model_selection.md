# 시간순 확장 실험 후보 선정 근거

기존 자료를 재사용한 탐색적 결과. 최종 확정 모델 아님.

Validation 우선 후보: **B_SVM_balanced**

근접 공동 후보: ['B_SVM_balanced']

사전 선정 규칙은 temporal_expansion_protocol.md 및 experiment_plan.json 참조.
Batch 9–10 평가 전에 selection_frozen.json과 모델 바이트를 고정했음.

## Validation 선정 근거

```text
      trial_id   scaler class_weight  val_equal_batch_macro_f1  val_pooled_macro_f1  val_toluene_recall  val_acetaldehyde_recall  val_min_class_recall  val_other_four_f1  fit_seconds
 B_RF_balanced     none     balanced                  0.651699             0.726083            0.687713                 0.177606              0.177606           0.838165     0.787602
B_SVM_balanced standard     balanced                  0.897000             0.897070            0.890785                 0.629344              0.629344           0.931067     0.459239
B_LR_tune_C0p1 standard     balanced                  0.806230             0.846918            0.970990                 0.387387              0.387387           0.885767     0.499913
```

## 선정 이후 탐색적 평가

```text
      trial_id  partition  equal_batch_macro_f1  batch_sd_macro_f1  min_batch_macro_f1  max_batch_macro_f1  pooled_macro_f1  accuracy  weighted_f1  toluene_recall  toluene_f1  acetaldehyde_recall  acetaldehyde_f1  min_class_recall  other_four_f1
B_LR_tune_C0p1 evaluation              0.577751           0.014457            0.563293            0.592208         0.595821  0.642506     0.596508        0.597718    0.625373             0.017778         0.034934          0.017778       0.728655
B_LR_tune_C0p1 validation              0.806230           0.043832            0.762398            0.850062         0.846918  0.860763     0.844690        0.970990    0.981034             0.387387         0.557407          0.387387       0.885767
 B_RF_balanced evaluation              0.456727           0.059979            0.396748            0.516706         0.408314  0.442998     0.408016        0.176890    0.291765             0.075556         0.122156          0.075556       0.508991
 B_RF_balanced validation              0.651699           0.080190            0.571509            0.731890         0.726083  0.758126     0.713816        0.687713    0.705779             0.177606         0.298056          0.177606       0.838165
B_SVM_balanced evaluation              0.602705           0.068142            0.534563            0.670848         0.558657  0.570270     0.559136        0.462197    0.460227             0.186667         0.304716          0.186667       0.646750
B_SVM_balanced validation              0.897000           0.000058            0.896942            0.897057         0.897070  0.896852     0.892000        0.890785    0.886248             0.629344         0.771902          0.629344       0.931067
```

## 학습 범위 차이

```text
family  partition  equal_batch_macro_f1_A  equal_batch_macro_f1_B  equal_batch_macro_f1_delta_pp  pooled_macro_f1_A  pooled_macro_f1_B  pooled_macro_f1_delta_pp  toluene_recall_A  toluene_recall_B  toluene_recall_delta_pp  acetaldehyde_recall_A  acetaldehyde_recall_B  acetaldehyde_recall_delta_pp  other_four_f1_A  other_four_f1_B  other_four_f1_delta_pp
    LR validation                0.545337                0.795526                      25.018884           0.569078           0.823663                 25.458474               0.0          0.916382                91.638225               0.100386               0.319176                     21.879022         0.816824         0.875780                5.895528
    LR evaluation                0.506693                0.501797                      -0.489579           0.462412           0.502598                  4.018615               0.0          0.493581                49.358060               0.008889               0.000000                     -0.888889         0.689404         0.610447               -7.895671
    RF validation                0.347470                0.636628                      28.915768           0.499315           0.702840                 20.352551               0.0          0.578498                57.849829               0.438867               0.191763                    -24.710425         0.641604         0.799625               15.802026
    RF evaluation                0.387255                0.459440                       7.218505           0.342163           0.414399                  7.223622               0.0          0.169757                16.975749               0.188148               0.088889                     -9.925926         0.455307         0.514585                5.927774
   SVM validation                0.595715                0.862930                      26.721543           0.636887           0.860019                 22.313218               0.0          0.851536                85.153584               0.776062               0.490347                    -28.571429         0.809960         0.901353                9.139286
   SVM evaluation                0.577324                0.577184                      -0.013998           0.468006           0.535063                  6.705688               0.0          0.439372                43.937233               0.253333               0.068148                    -18.518519         0.624352         0.658109                3.375669
```

기본 설정 A/B 비교만 학습 범위의 통제 비교임. 표본 수·가스 구성·시기가 함께 변함.
Batch 8 Toluene 18개, Validation 2개 Batch만으로 장기 안정성을 확정할 수 없음.
0.5pp 근접 규칙은 통계적 동등성 기준이 아님. 개별 클래스와 최저 Recall 검토 필요.
독립 검증에는 새 시기의 미관찰 데이터, 농도·환경 기록 및 사전 고정된 평가가 필요함.
