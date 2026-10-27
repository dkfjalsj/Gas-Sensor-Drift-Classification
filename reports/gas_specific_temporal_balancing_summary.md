# 13단계 가스별 시기 균형 실험 요약

**B — 부분 개선**

공식 Model A 유지. 새 독립 Test 없음.9–10은회고적진단이며조건/시드선정에미사용.

신규학습25회, 논리평가75건, 재사용50건.

## 843개 과거 결과

```text
     setting  mean_macro_f1  seed_sd_macro_f1  mean_accuracy  mean_weighted_f1  toluene_recall  acetaldehyde_recall  other_four_f1  worst_recall  zero_pairs_mean
coverage_mid       0.644733          0.029395       0.668878          0.683666        0.504556             0.786942       0.781477           0.0              0.8
   mixed_mid       0.643400          0.039113       0.667777          0.677154        0.446088             0.727118       0.775463           0.0              1.0
  recent_mid       0.653622          0.020815       0.691407          0.700549        0.508790             0.788645       0.788687           0.0              1.0
  spread_mid       0.608991          0.009673       0.583914          0.592401        0.600378             0.687366       0.734658           0.0              1.0
```

## 보호 기준

```text
     setting   baseline  mean_macro_delta  paired_seed_sd  positive_fold_n  neutral_fold_n  positive_seed_n  toluene_delta  acetaldehyde_delta  macro_guard  focus_guard  other_guard  fold_guard  seed_guard  balanced_success  expansion_eligible conclusion
coverage_mid spread_mid          0.035743        0.022604                2               0                5      -0.095822            0.099576         True        False         True       False        True             False               False          B
   mixed_mid spread_mid          0.034409        0.036805                1               1                4      -0.154291            0.039752         True        False         True       False       False             False               False          B
  recent_mid spread_mid          0.044632        0.016159                2               0                5      -0.091588            0.101279         True        False         True       False        True             False               False          B
  spread_mid spread_mid          0.000000        0.000000                0               3                0       0.000000            0.000000        False         True         True       False       False             False               False          C
```

## 조건부 확대

```text
     setting   mid_parent  execute                                                            reason
   mixed_max    mixed_mid    False Predeclared plausibility guards not all satisfied; no replacement
coverage_max coverage_mid    False Predeclared plausibility guards not all satisfied; no replacement
```

## 1689개 결과

```text
   setting  mean_macro_f1  seed_sd_macro_f1  mean_accuracy  mean_weighted_f1  toluene_recall  acetaldehyde_recall  other_four_f1  worst_recall  zero_pairs_mean
spread_max        0.69921          0.012882       0.683322          0.710167         0.55296             0.763384       0.840629           0.0              1.0
```

## 동일1689개 기준 보호

```text
   setting   baseline  mean_macro_delta  paired_seed_sd  positive_fold_n  neutral_fold_n  positive_seed_n  toluene_delta  acetaldehyde_delta  macro_guard  focus_guard  other_guard  fold_guard  seed_guard  balanced_success  expansion_eligible conclusion
spread_max spread_max               0.0             0.0                0               3                0            0.0                 0.0        False         True         True       False       False             False               False          C
```

## 9–10 회고적 결과

```text
     setting  scope    n  macro_f1_mean  macro_f1_sd  accuracy_mean  toluene_recall_mean  acetaldehyde_recall_mean  other_four_f1_mean  min_recall
coverage_mid     10 3600       0.560702     0.018746       0.562611             0.902667                  0.251667            0.623611    0.170000
coverage_mid      9  470       0.554092     0.062116       0.624255             0.184158                  0.805333            0.673627    0.000000
coverage_mid pooled 4070       0.574113     0.017764       0.569730             0.799144                  0.313185            0.641046    0.216296
   mixed_mid     10 3600       0.423880     0.019267       0.408167             0.790333                  0.207000            0.469325    0.121667
   mixed_mid      9  470       0.542420     0.058111       0.626383             0.415842                  0.405333            0.594063    0.000000
   mixed_mid pooled 4070       0.450472     0.021628       0.433366             0.736377                  0.229037            0.505789    0.145185
  recent_mid     10 3600       0.558240     0.043771       0.569000             0.787333                  0.313000            0.592183    0.240000
  recent_mid      9  470       0.521459     0.003100       0.619149             0.000000                  0.968000            0.630271    0.000000
  recent_mid pooled 4070       0.572180     0.038589       0.574791             0.673894                  0.385778            0.612129    0.321481
  spread_mid     10 3600       0.518186     0.015070       0.526667             0.961667                  0.085667            0.618208    0.043333
  spread_mid      9  470       0.624886     0.005251       0.691915             0.936634                  0.328000            0.675654    0.000000
  spread_mid pooled 4070       0.538268     0.013742       0.545749             0.958060                  0.112593            0.636242    0.074074
```

전체 129개 통과, 5개 실패. 기존 실패3건과 과거 모델 목록 고정 충돌2건. 신규 16개 모두 통과, 신규 실패0건.

기존260개모델·원본10개·과거결과보존. Commit·Push없음.

## 추가 복잡성 평가

단순 최근형의 과거 평균 Macro F1은 65.36%로, 가스혼합 64.34%와 최소대표 64.47%보다 높았다. 이번 결과에서 새 구성의 추가 복잡성을 정당화할 안정적인 우월성은 확인하지 못했다. 이는 과거 개발 구간의 기술적 평가이며 회고적 미래 점수로 후보를 재선정한 것이 아니다.
