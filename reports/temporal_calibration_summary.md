# 17단계 소량 신규 시기 자료 기반 지도학습 적응

- 정답이 확인된 새 시기 자료를 이용한 지도학습 모델 적응이며 물리적 센서 교정이나 드리프트 감지 실험이 아님. 반복 사용한 개발 Batch 내부의 평가이며 독립 Test가 아님. Batch 9~10 신규 평가 없음. 공식 Model A 유지.

- 교정 비율의 분모는 전체 target Batch. 평가50%를 먼저 고정한 뒤 남은50%에서5/10/20%를 중첩 추출. 실제 수는 내림하며 모든 가스 최소1개 확보. 같은 Fold·시드의 평가 행은 모든 비율에서 동일.

- 0% 기준도 이번50% 평가 행에서 새로 계산한 지표임. 이전 전체 Batch 평가79.71%와 표본이 달라 직접 같은 수치가 아님.

- 평가 정답은 층화 분할·최종 지표 계산에만 사용. 전처리·SVM·balanced 가중치는 과거+선택 Calibration에서만 Fit.

- 새 시기 정답이 있는 적응과 새 시기 정답이 전혀 없는 미래 일반화는 다른 문제. 현재 목표 Batch 안에서의 회복이며 이후 미관찰 시기에 대한 지속성은 검증하지 않았음.

- 과거 시기 회귀 검사는 Fold A의 기존 B_history Validation4·Test5만 재등록. 358개·5종 가스(Toluene 없음), 적응 Train·교정·평가와 중복 없음. B/C는 적절한 과거 held-out 없음.

- 평가 집합은 이전에 반복 관찰한 자료에서 새로 나눈 것으로 독립성이 복구되지 않음. 시드별 분할이 겹치며 한 시드의 평가 행이 다른 시드의 교정 행일 수 있음. 독립 미래 반복이나 p값 미주장.

- 가스별 층화에는 기존 정답 정보가 필요함. 실제 배포에서 같은 클래스 구성을 모으는 라벨 수집 비용이 5%라고 증명한 결과가 아님. 농도·환경·세션의 유사성과 근접 반복 측정 가능성도 남음.

- 동일 Batch 내부의 정확한 시각이 없어 무작위 교정 자료가 평가보다 실제로 먼저 측정됐다고 주장할 수 없음.

- 각 비율을 별도로 판정하며 우수 비율을 사후 선정해 공식 모델을 교체하지 않음. 추가 비율·시드·튜닝·앙상블·물리적 센서 교정·감지 알고리즘 없음.

- 과거 유지 성능은 별도의 진단이며 현재 시기 보호 조건 통과가 과거 전 가스의 유지 성능을 보장하지 않음.

- 5% 판정 A: 평균 Macro F1 변화+12.02pp, 긍정 Fold-시드 8/9, 신규 Recall0 0, 모든 보호·일관성 조건 통과=True.

- 10% 판정 A: 평균 Macro F1 변화+13.70pp, 긍정 Fold-시드 9/9, 신규 Recall0 0, 모든 보호·일관성 조건 통과=True.

- 20% 판정 A: 평균 Macro F1 변화+14.37pp, 긍정 Fold-시드 9/9, 신규 Recall0 0, 모든 보호·일관성 조건 통과=True.

비율 요약:
```text
      mean_macro_f1   seed_sd  mean_accuracy  mean_weighted_f1  mean_macro_delta
rate                                                                            
0          0.802428  0.012064       0.832054          0.831931          0.000000
5          0.922580  0.011152       0.926251          0.925575          0.120152
10         0.939445  0.011110       0.945643          0.944916          0.137017
20         0.946083  0.010531       0.953306          0.952079          0.143655
```

Fold 요약:
```text
           mean_macro_f1   seed_sd  mean_macro_delta  evaluation_n  calibration_n
rate fold                                                                        
0    A          0.617083  0.003020          0.000000          1150              0
     B          0.901435  0.001993          0.000000          1806              0
     C          0.888768  0.036106          0.000000           147              0
5    A          0.916475  0.005390          0.299391          1150            115
     B          0.954225  0.007008          0.052791          1806            180
     C          0.897041  0.033004          0.008274           147             14
10   A          0.937234  0.005871          0.320151          1150            230
     B          0.977125  0.004756          0.075691          1806            361
     C          0.903976  0.037602          0.015209           147             29
20   A          0.941117  0.003488          0.324034          1150            460
     B          0.985528  0.001360          0.084094          1806            722
     C          0.911604  0.030626          0.022837           147             58
```

가스별 평균:
```text
             precision    recall        f1           gas
rate gas_id                                             
0    1        0.882218  0.972763  0.923871       Ethanol
     2        0.931479  0.922261  0.920156      Ethylene
     3        0.985406  0.815825  0.887116       Ammonia
     4        0.664394  0.861779  0.605681  Acetaldehyde
     5        0.911051  0.912955  0.905429       Acetone
     6        0.550152  0.599113  0.572317       Toluene
5    1        0.945776  0.991353  0.966922       Ethanol
     2        0.939892  0.922261  0.925280      Ethylene
     3        0.990741  0.820146  0.891910       Ammonia
     4        0.915453  0.934658  0.919072  Acetaldehyde
     5        0.955310  0.928651  0.938943       Acetone
     6        0.852963  0.944795  0.893357       Toluene
10   1        0.967085  0.991353  0.977926       Ethanol
     2        0.968475  0.929668  0.945885      Ethylene
     3        0.990741  0.820763  0.892245       Ammonia
     4        0.928865  0.975578  0.948435  Acetaldehyde
     5        0.955517  0.964334  0.958928       Acetone
     6        0.888038  0.947142  0.913253       Toluene
20   1        0.954887  0.993515  0.972911       Ethanol
     2        0.980119  0.929668  0.952203      Ethylene
     3        1.000000  0.823232  0.896036       Ammonia
     4        0.940995  0.971815  0.952862  Acetaldehyde
     5        0.957337  0.977082  0.966198       Acetone
     6        0.926985  0.950272  0.936290       Toluene
```

과거 회귀 검사:
```text
fold  seed  rate      scope  target_batch  calibration_n  train_n   n  accuracy  macro_f1  weighted_f1  min_recall  zero_recall  toluene_to_acetaldehyde  acetaldehyde_to_toluene  fit_seconds  predict_seconds  macro_delta
   A    11     0 regression             6              0     3275 358  0.935754  0.942497     0.936342    0.855263            0                        0                        0     0.000000         0.030351     0.000000
   A    11     5 regression             6            115     3390 358  0.941341  0.947892     0.942029    0.855263            0                        0                        0     0.234323         0.032157     0.005395
   A    11    10 regression             6            230     3505 358  0.941341  0.947892     0.942029    0.855263            0                        0                        0     0.221803         0.033065     0.005395
   A    11    20 regression             6            460     3735 358  0.941341  0.947892     0.942029    0.855263            0                        0                        0     0.203006         0.036381     0.005395
   A    23     0 regression             6              0     3275 358  0.935754  0.942497     0.936342    0.855263            0                        0                        0     0.000000         0.030544     0.000000
   A    23     5 regression             6            115     3390 358  0.941341  0.947892     0.942029    0.855263            0                        0                        0     0.170844         0.031342     0.005395
   A    23    10 regression             6            230     3505 358  0.941341  0.947892     0.942029    0.855263            0                        0                        0     0.193650         0.033245     0.005395
   A    23    20 regression             6            460     3735 358  0.938547  0.945528     0.939278    0.855263            0                        0                        0     0.228717         0.035644     0.003031
   A    42     0 regression             6              0     3275 358  0.935754  0.942497     0.936342    0.855263            0                        0                        0     0.000000         0.029531     0.000000
   A    42     5 regression             6            115     3390 358  0.941341  0.947892     0.942029    0.855263            0                        0                        0     0.169750         0.032352     0.005395
   A    42    10 regression             6            230     3505 358  0.941341  0.947892     0.942029    0.855263            0                        0                        0     0.179675         0.032618     0.005395
   A    42    20 regression             6            460     3735 358  0.941341  0.947892     0.942029    0.855263            0                        0                        0     0.233518         0.036936     0.005395
```

테스트:
```json
{
  "total": 199,
  "passed": 194,
  "failed": 5,
  "historical_failures": 5,
  "new_failures": 0,
  "new_tests": 16,
  "new_passed": 16,
  "failures": [
    {
      "classname": "tests.test_diagnostics",
      "name": "test_existing_results_and_models_unchanged",
      "historical": true,
      "reason": "FileNotFoundError: [Errno 2] No such file or directory: 'D:\\\\Gas-Sensor-Drift-Classification\\\\outputs\\\\model_comparison\\\\zNex~$haremetrics.csv'"
    },
    {
      "classname": "tests.test_models",
      "name": "test_eda_and_sources_preserved_report_complete",
      "historical": true,
      "reason": "AssertionError: assert '32974e022d81...49a573513c6bc' == '2adcd085c767...491a3306d723b'\n  \n  - 2adcd085c767f9fc675e60220392b7e7ea89808a0f1ade2d2ca491a3306d723b\n  + 32974e022d81b0f382d1f8a4c35f75a6f5d3c0b3009fd28659a49a573513c6bc"
    },
    {
      "classname": "tests.test_temporal_failure_diagnostics",
      "name": "test_no_new_fit_calls_or_new_model_files",
      "historical": true,
      "reason": "AssertionError: assert {'models\\\\A_r....joblib', ...} == {'models\\\\A_r....joblib', ...}\n  \n  Extra items in the right set:\n  'models\\\\temporal_robustness\\\\A\\\\RF_kbest64.joblib'\n  'models\\\\temporal_representativeness_control\\\\B_spread_mid_unit_seed23.joblib'\n  'models\\\\temporal_calibration\\\\B_seed11_cal20.joblib'\n  'models\\\\temporal_robustness\\\\C\\\\rank_equal.joblib'\n  'models\\\\temporal_robustness\\\\C\\\\LR_all.joblib'...\n  \n  ...Full output truncated (277 lines hidden), use '-vv' to show"
    },
    {
      "classname": "tests.test_temporal_generalization_validation",
      "name": "test_existing_files_raw_and_model_inventory_preserved",
      "historical": true,
      "reason": "AssertionError: assert {'models\\\\A_r....joblib', ...} == {'models\\\\A_r....joblib', ...}\n  \n  Extra items in the left set:\n  'models\\\\temporal_representativeness_control\\\\A_spread_mid_anchor_seed11.joblib'\n  'models\\\\temporal_representativeness_control\\\\C_early_mid_seed11.joblib'\n  'models\\\\temporal_representativeness_control\\\\B_early_mid_seed42.joblib'\n  'models\\\\temporal_representativeness_control\\\\A_early_mid_seed42.joblib'\n  'models\\\\temporal_representativeness_control\\\\B_spread_mid_anchor_unit_seed42.joblib'...\n  \n  ...Full output truncated (180 lines hidden), use '-vv' to show"
    },
    {
      "classname": "tests.test_toluene_deep_diagnostic",
      "name": "test_preserved_files_raw_models_and_config",
      "historical": true,
      "reason": "AssertionError: assert ({'models\\\\A_r....joblib', ...} == {'models\\\\A_r....joblib', ...}\n  \n  Extra items in the right set:\n  'models\\\\temporal_representativeness_control\\\\A_spread_mid_anchor_seed11.joblib'\n  'models\\\\temporal_representativeness_control\\\\C_early_mid_seed11.joblib'\n  'models\\\\temporal_representativeness_control\\\\B_early_mid_seed42.joblib'\n  'models\\\\temporal_representativeness_control\\\\A_early_mid_seed42.joblib'\n  'models\\\\temporal_representativeness_control\\\\B_spread_mid_anchor_unit_seed42.joblib'...\n  \n  ...Full output truncated (180 lines hidden), use '-vv' to show)"
    }
  ]
}
```


## 계산 결과와 해석 구분

- 계산값: 0% 교정의 평균 Macro F1은 80.24%, 같은 평가 행의 기준 대비 +0.00%p임.

- 계산값: 5% 교정의 평균 Macro F1은 92.26%, 같은 평가 행의 기준 대비 +12.02%p임.

- 계산값: 10% 교정의 평균 Macro F1은 93.94%, 같은 평가 행의 기준 대비 +13.70%p임.

- 계산값: 20% 교정의 평균 Macro F1은 94.61%, 같은 평가 행의 기준 대비 +14.37%p임.

- 계산값: Acetaldehyde의 Fold·시드 평균 Recall은 0% 교정: 86.18% → 5% 교정: 93.47% → 10% 교정: 97.56% → 20% 교정: 97.18%임.

- 계산값: Toluene의 Fold·시드 평균 Recall은 0% 교정: 59.91% → 5% 교정: 94.48% → 10% 교정: 94.71% → 20% 교정: 95.03%임.

- 계산값: Fold A의 Toluene 평가 표본은 시드마다 233개임. 기준 정분류는 모두 0개, 각 교정 비율에서 시드11은 233개, 시드23·42는 각각 232개임. Toluene→Acetaldehyde 오분류는 기준 209·208·202개에서 각 교정 비율 모두 0개로 감소함.

- 계산값: 나머지 네 가스의 평균 F1은 기준 대비 5%에서 +2.16%p, 10%에서 +3.46%p, 20%에서 +3.77%p임. 신규 Recall 0 조합은 없음.

- 해석: 가장 큰 회복은 0→5%에서 나타남. 평균 Macro F1의 추가 증가는 5→10%에서 약1.69%p, 10→20%에서 약0.66%p로 작아짐. Acetaldehyde Recall과 Ethanol F1 등 일부 지표는 20%가 10%보다 낮아 모든 클래스 지표의 단조 개선을 뜻하지 않음.

- 계산값·한계: 과거 유지 진단은 Fold A의 Batch4–5, 358개·5종만 가능함. 평균 Macro F1은 기준94.25%, 5%·10% 교정94.79%, 20% 교정94.71%임. 해당 자료에 Toluene이 없어 그 가스의 과거 유지 성능은 검증 불가함. Fold B/C에는 적합한 과거 미학습 평가 집합이 없어 유지 성능 결론을 내리지 않음.

- 연구 결론: 5%·10%·20%는 각각 사전 보호·일관성 기준을 충족하여 A로 판정함. 세 비율 중 공식 채택 비율을 선정한 결과가 아님. 공식 Model A 유지함.

- 연구 한계: 같은 Batch에서 확보한 정답 일부가 도움이 된다는 근거임. 미관찰 다음 Batch에서도 효과가 유지되거나 센서 드리프트의 독립 효과가 확인됐다는 증거는 아님. 물리적 센서 교정으로 해석하지 않음.

- 검증 조건: 전체 Batch 정답을 이용한 층화 표본 구성이며 실제 배포에서 같은 6종 구성의 라벨을 같은 비용으로 확보할 수 있다는 보장은 없음. Batch 내 시각 정보가 없어 교정이 평가보다 실제로 선행했다는 주장도 불가함.
