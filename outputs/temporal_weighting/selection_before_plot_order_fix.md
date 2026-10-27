# 9단계 모델 선정 근거

고정 가중치 후보: **class_balanced**. 기존 모델 유지: True.

## 사전 계획과 보호 기준

temporal_weighting_protocol.md와 experiment_plan.json에 학습 전8설정·24회Fit·수식·보호·동점 규칙 고정.
과거3Fold 동일 가중Macro F1이 주 지표. 보호 미통과 시 기존6단계 SVM 유지.
주 후보 Train1–6, 동일 가중치의Train1–7은 별도 범위 비교이며 평가 후 후보를 바꾸지 않음.

```text
        config_id  order  mean_macro_f1  sd_macro_f1  pooled_macro_f1  mean_accuracy  mean_weighted_f1  mean_toluene_recall  mean_toluene_f1  mean_acetaldehyde_recall  mean_acetaldehyde_f1  min_recall  zero_recall_pairs  mean_other_four_f1  fit_seconds_sum  predict_seconds_sum  mean_n_features  focus_min_f1  mean_class1_f1  mean_class2_f1  mean_class3_f1  mean_class5_f1
   class_balanced      0       0.797082     0.125645         0.808872       0.829189          0.829635             0.575900         0.546296                  0.851662              0.589125         0.0                  1            0.911768         1.696093             0.768064            128.0      0.546296        0.922257        0.921975        0.899306        0.903534
      time_linear      1       0.798124     0.128990         0.805752       0.829547          0.831237             0.560316         0.555031                  0.852110              0.583902         0.0                  1            0.912453         1.607011             0.918985            128.0      0.555031        0.914693        0.923955        0.894416        0.916747
         time_exp      2       0.799268     0.130049         0.805853       0.829441          0.831277             0.559729         0.560863                  0.853454              0.584834         0.0                  1            0.912477         1.630494             0.771949            128.0      0.560863        0.914215        0.925357        0.894416        0.915920
      time_recent      3       0.800705     0.127866         0.808421       0.832590          0.832819             0.558555         0.562890                  0.853454              0.586039         0.0                  1            0.913825         1.613920             0.752944            128.0      0.562890        0.924011        0.923557        0.894868        0.912864
     class_sample      4       0.797082     0.125645         0.808872       0.829189          0.829635             0.575900         0.546296                  0.851662              0.589125         0.0                  1            0.911768         1.589618             0.751911            128.0      0.546296        0.922257        0.921975        0.899306        0.903534
        gas_batch      5       0.760870     0.109374         0.793345       0.775982          0.787126             0.555947         0.416453                  0.845389              0.583865         0.0                  1            0.891225         1.595628             0.742564            128.0      0.416453        0.915293        0.922764        0.898850        0.827994
time_class_shrink      6       0.796471     0.123417         0.801961       0.829782          0.828650             0.557381         0.565461                  0.835085              0.571767         0.0                  1            0.910400         1.581764             0.714181            128.0      0.565461        0.913459        0.917661        0.898065        0.912415
   time_gas_batch      7       0.775515     0.112922         0.798950       0.803297          0.808376             0.557707         0.460839                  0.848526              0.586658         0.0                  1            0.901399         1.616721             0.754697            128.0      0.460839        0.918844        0.921975        0.897490        0.867286
```

## 보호 통과 여부

```text
        config_id  macro_guard  toluene_guard  acetaldehyde_guard  other_four_guard  individual_other_guard  min_recall_guard  fold_min_guard  zero_pair_guard  improvement_evidence  eligible                                                            failed_guards
   class_balanced         True           True                True              True                    True              True            True             True                  True      True                                                                      NaN
      time_linear         True           True                True              True                    True              True            True             True                 False     False                                                     improvement_evidence
         time_exp         True           True                True              True                    True              True            True             True                  True      True                                                                      NaN
      time_recent         True           True                True              True                    True              True            True             True                  True      True                                                                      NaN
     class_sample         True           True                True              True                    True              True            True             True                 False     False                                                     improvement_evidence
        gas_batch        False           True                True             False                   False              True            True             True                 False     False macro_guard,other_four_guard,individual_other_guard,improvement_evidence
time_class_shrink         True           True                True              True                    True              True            True             True                 False     False                                                     improvement_evidence
   time_gas_batch        False           True                True              True                    True              True            True             True                 False     False                                         macro_guard,improvement_evidence
```

## 공통 Batch8의 범위 효과

```text
  n  accuracy  macro_precision  macro_recall  macro_f1  weighted_f1  macro_precision_fixed6  macro_recall_fixed6  macro_f1_fixed6  missing_classes  toluene_recall  toluene_f1  toluene_support  acetaldehyde_recall  acetaldehyde_f1  acetaldehyde_support  min_class_recall  other_four_f1      config_id fold  fit_seconds  predict_seconds  n_features  zero_recall_classes
294  0.921769         0.913551      0.891256  0.897057     0.920407                0.913551             0.891256         0.897057              NaN        0.777778        0.80               18             0.939394         0.953846                    33             0.725       0.907124 class_balanced    6            0                0         128                  NaN
294  0.897959         0.886702      0.876408  0.874435     0.896466                0.886702             0.876408         0.874435              NaN        0.833333        0.75               18             0.939394         0.911765                    33             0.675       0.896212 class_balanced    7            0                0         128                  NaN
```

## 동결 이후 탐색적 평가

```text
             model_id  train_end                 scheme  equal_batch_macro_f1  sd_batch_macro_f1  pooled_macro_f1  accuracy  weighted_f1  pooled_toluene_recall  pooled_toluene_f1  pooled_acetaldehyde_recall  pooled_acetaldehyde_f1  pooled_min_recall  worst_batch_class_recall  zero_batch_class_pairs  other_four_f1  equal_macro_delta_vs_stage6_pp  pooled_macro_delta_vs_stage6_pp
train6_class_balanced          6         class_balanced              0.602705           0.068142         0.558657  0.570270     0.559136               0.462197           0.460227                    0.186667                0.304716           0.186667                  0.000000                       1       0.646750                        0.000000                         0.000000
train7_class_balanced          7         class_balanced              0.700451           0.037361         0.677537  0.674939     0.677859               0.677603           0.622951                    0.605926                0.558362           0.392330                  0.009901                       0       0.720978                        9.774514                        11.888041
           stage6_SVM          6         class_balanced              0.602705           0.068142         0.558657  0.570270     0.559136               0.462197           0.460227                    0.186667                0.304716           0.186667                  0.000000                       1       0.646750                        0.000000                         0.000000
    stage8_HardVoting          6 historical_hard_voting              0.601822           0.039746         0.575858  0.600246     0.576445               0.410842           0.468293                    0.084444                0.150396           0.084444                  0.000000                       1       0.709116                       -0.088335                         1.720151
```

기존 Test 재사용의 회고적·탐색적 결과이며 독립 최종 Test가 아님. Batch8 Toluene18개, Fold A Train Toluene79개. Fold는 독립 반복이 아님.

가중치는 실제Train 클래스·Batch만 사용. c×sample 중복 보정 금지, 유효가중치 평균1. 전처리 무가중TrainFit으로 가중치 효과와 분리. 공식 정의: [scikit-learn SVC](https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html).

실행: `.venv\Scripts\python.exe -B -X utf8 -m src.temporal_weighting`

테스트: `.venv\Scripts\python.exe -B -X utf8 -m pytest -q -p no:cacheprovider --junitxml=outputs/temporal_weighting/test_results.xml`

## 최종 해석

- 8개 SVM 가중치 설정을3Fold에서 비교해24회 학습. 평균점수 최고는 time_recent 80.07%, 기준 79.71% 대비 +0.36pp였다.

- 주 후보는 class_balanced. time_exp와 time_recent는 보호 기준을 통과했지만 기준도 최고 평균의0.5pp 이내에 포함됐다.0% 조합 수와 최소Recall이 같아 집중 가스 최소 평균Recall이 높은 기준 모델을 유지했다. “모든 개선 설정이 보호 검사에 실패했다”는 뜻은 아니다.

- 최근2Batch 가중치의 평균 Toluene Recall은 57.59%→55.86%. 모든 설정은 Fold A Toluene Recall0%를 해소하지 못했다.

- 가스·Batch 보정의 평균 Macro F1은 76.09%, 시간·셀 결합은 77.55%로 기준보다 낮았다. 클래스 sample 가중치 대조는3Fold의6207개 예측이 기존 balanced와 모두 같았다.

- 기본 가중치 Train1–6→1–7의 공통Batch8 Macro F1은 89.71%→87.44%. Batch8은 이미 개발 자료이고 Toluene18개이므로 이 구간만으로 안정적 개선을 결론 내릴 수 없다.

- 동일 기본 가중치의 별도 확장 비교에서9–10 동일 가중 Macro F1은 60.27%→70.05% (+9.77pp), 합산은 55.87%→67.75%. 이는 가중치 최적화의 개선 효과가 아니라 학습 범위 비교 결과다.

- 확장 모델의 합산 Toluene Recall은 46.22%→67.76%, Acetaldehyde는 18.67%→60.59%. 하지만 Batch9 Toluene은1/101(0.99%)만 맞혀 실질적인 실패가 여전히 크다.

- 확장 모델의 Batch10 Acetaldehyde Recall은14%→55.83%, Toluene은54%→79%였다. 반면 합산 Ethanol Recall은80.79%→72.77%로 낮아졌고 Batch10 Acetone Recall도32.83%에 머물렀다. 모든 가스의 안정적 개선으로 보지 않는다.

- Train1–7에서 Toluene 표본은546→1114개, Acetaldehyde는484→1228개로 늘었다. Batch6 Toluene 집중도도85.53%→41.92%로 낮아졌다. 표본 수·시기·가스 구성·기본 클래스 가중치가 함께 바뀌므로 원인을 데이터 양 하나로 분리할 수 없다.

- 확장 모델은 후속 독립 검증 대상이다. 평가에서 더 좋아 보였다는 이유로 주 후보나 학습 범위·가중치를 사후 변경하지 않았다. 모든9–10 결과는 기존 Test 재사용의 회고적·탐색적 성능이며 최종 대체 모델의 확정 근거가 아니다.

## 가중치 효과와 확장 효과의 분리

동일 Train 범위에서의 가중치 차이는 weight_effects_within_range.csv, 고정 기본 설정의 범위 차이는 baseline_range_effects.csv 참조.

```text
 scope    n  macro_train6  macro_train7  macro_delta_pp  other_four_f1_train6  other_four_f1_train7  class1_recall_train6  class1_recall_train7  class2_recall_train6  class2_recall_train7  class3_recall_train6  class3_recall_train7  class4_recall_train6  class4_recall_train7  class5_recall_train6  class5_recall_train7  class6_recall_train6  class6_recall_train7
     8  294      0.897057      0.874435       -2.262187              0.907124              0.896212              1.000000              1.000000              0.933333              0.866667              0.725000              0.675000              0.939394              0.939394              0.972028              0.944056              0.777778              0.833333
     9  470      0.670848      0.737812        6.696380              0.826784              0.953315              1.000000              0.983607              1.000000              0.927273              1.000000              1.000000              0.560000              0.986667              0.923077              0.884615              0.000000              0.009901
    10 3600      0.534563      0.663090       12.852647              0.618742              0.690104              0.788333              0.701667              0.840000              0.815000              0.693333              0.793333              0.140000              0.558333              0.316667              0.328333              0.540000              0.790000
pooled 4070      0.558657      0.677537       11.888041              0.646750              0.720978              0.807867              0.727685              0.853435              0.824427              0.737143              0.822857              0.186667              0.605926              0.386431              0.392330              0.462197              0.677603
```

```text
 train_end  gas_id          gas    n  train_n  observed_gas_batches  batch6_n  batch6_fraction
         6       1      Ethanol 1225     5933    [1, 2, 3, 4, 5, 6]       514         0.419592
         6       2     Ethylene 1579     5933    [1, 2, 3, 4, 5, 6]       574         0.363521
         6       3      Ammonia  541     5933    [1, 2, 3, 4, 5, 6]       110         0.203327
         6       4 Acetaldehyde  484     5933    [1, 2, 3, 4, 5, 6]        29         0.059917
         6       5      Acetone 1558     5933    [1, 2, 3, 4, 5, 6]       606         0.388960
         6       6      Toluene  546     5933             [1, 2, 6]       467         0.855311
         7       1      Ethanol 1874     9546 [1, 2, 3, 4, 5, 6, 7]       514         0.274280
         7       2     Ethylene 2241     9546 [1, 2, 3, 4, 5, 6, 7]       574         0.256136
         7       3      Ammonia  901     9546 [1, 2, 3, 4, 5, 6, 7]       110         0.122087
         7       4 Acetaldehyde 1228     9546 [1, 2, 3, 4, 5, 6, 7]        29         0.023616
         7       5      Acetone 2188     9546 [1, 2, 3, 4, 5, 6, 7]       606         0.276965
         7       6      Toluene 1114     9546          [1, 2, 6, 7]       467         0.419210
```

## 다음 단계

단순 시간·셀 가중치의 강도를 Test에 맞춰 더 탐색하지 않을 것. Batch9 Toluene의 낮은 Recall과 다른 가스 손실을 운영 기준과 연결하고, 새 시기·농도·환경별 측정 자료 및 참조 측정을 확보해 고정 후보를 독립 검증할 것. Train1–7 확장은 유망한 비교 결과이지만 이번 평가로 사후 채택하지 않음.

## 테스트와 보존

전체 테스트 76개 통과·3개 실패. 신규10개 모두 통과. 기존3건은 과거 소스 SHA 불일치, 과거 보존 기록의 임시 파일 후보 부재, 7단계 전체 모델 목록 고정 검사와 승인된 신규 모델 추가의 충돌이다. 기존 검사·해시를 수정하거나 누락 파일을 생성하지 않았다. 신규 코드 테스트 실패 없음.

기존 파일 445개·원본10개·기존 모델114개 해시 보존 확인. 새 모델 파일26개를 별도 경로에 저장했다. 전처리는 무가중Train만 Fit, 가중치는 Train 클래스·Batch만으로 산정했다. 기존SVM·8단계Hard Voting 예측 재현, 유효가중치 평균1·class×sample 중복 방지·분할 중복 검사 통과. Commit·Push 없음.

```text
tests.test_diagnostics::test_existing_results_and_models_unchanged
tests.test_models::test_eda_and_sources_preserved_report_complete
tests.test_temporal_failure_diagnostics::test_no_new_fit_calls_or_new_model_files
```

테스트 후 문서 보완: `.venv\Scripts\python.exe -B -X utf8 -m src.temporal_weighting_review`
