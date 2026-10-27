# 16단계 HGB 단독 알고리즘 비교

과거 Fold는 반복 사용한 개발 검증 자료이며 독립 Test가 아님. 학습 구간이 겹치는 Fold를 독립 반복 표본으로 취급하지 않음. Batch 9~10 신규 평가 없음. 공식 Model A 유지.

- 연구 결론 C — 개선 근거 부족. 공식 Model A 유지.

- HGB 평균 Macro F1 66.10%, SVM 대비-13.61pp. 모든 보호 조건 통과=False.

- 일부 Fold 또는 가스 평균 F1이 상승하면 전체 보호 미달이라도 사전 규칙상 B로 표시. B는 우수 모델 선정이나 전반적 개선을 뜻하지 않음.

- HGB 학습 3회, SVM 재사용 3개, SVM 재사용 실패 대체 학습0회. 추가 조건·시드 탐색 없음.

- 수치는 관찰 결과이며 새 알고리즘의 원인 효과나 센서 드리프트 단독 원인 확정은 아님.

- 각 Fold의 Train 행·Validation 행·정답·128특징은 동일. HGB는 표준화 없이 사용하므로 알고리즘과 적합한 전처리를 함께 비교한 대조임.

- HGB는 native NaN을 지원하지만 사전 정책대로 Train 중앙값 처리. class_weight=balanced를 지원하며 Train 가스 빈도만 사용. sample_weight 중복 적용 없음.

- HGB early_stopping=False·validation_fraction=None으로 외부·내부 Validation을 학습에 사용하지 않음. class_weight 빈도식은 SVM과 같아도 학습 손실과 적용 효과는 다름.

- Fold A 초기 Toluene 학습79개, Fold C Toluene 평가18개. 한 표본 Recall 변화5.56pp이며 작은 support 및 겹치는 학습 구간 때문에 독립 미래 성능의 신뢰구간이나 유의성 미주장.

- 오류 상호 보완성은 저장된 두 예측을 비교했을 뿐 새 앙상블·Oracle·가중치 조절을 실행하지 않음.

- 실패·혼동 방향·예측 비율을 전부 공개. 새로운 시기·농도·환경·세션 정보의 독립 검증 필요.

- A Toluene HGB: support467, Recall0.00%, Precision0.00%, F10.00%, 예측 수0.

- B Toluene HGB: support568, Recall49.65%, Precision99.30%, F166.20%, 예측 수284.

- C Toluene HGB: support18, Recall77.78%, Precision66.67%, F171.79%, 예측 수21.

```text
fold           A          B          C
model                                 
SVM    61.986979  89.694202  87.443522
HGB    57.995064  67.843738  72.456358
```

```text
       mean_macro_f1   fold_sd  mean_accuracy  mean_weighted_f1  min_recall  zero_pairs  fit_seconds  predict_seconds
model                                                                                                                
SVM         0.797082  0.125645       0.829189          0.829635         0.0           1     0.000000         0.809237
HGB         0.660984  0.060314       0.737441          0.719283         0.0           1    56.122952         0.245941
```

```text
              precision    recall        f1           gas
model gas_id                                             
HGB   1        0.892560  0.881401  0.880750       Ethanol
      2        0.929182  0.612888  0.614419      Ethylene
      3        0.598408  0.826178  0.684163       Ammonia
      4        0.579446  0.715705  0.429873  Acetaldehyde
      5        0.844875  0.961277  0.896725       Acetone
      6        0.553208  0.424752  0.459974       Toluene
SVM   1        0.876624  0.974708  0.922257       Ethanol
      2        0.930622  0.925939  0.921975      Ethylene
      3        0.984067  0.833838  0.899306       Ammonia
      4        0.644928  0.851662  0.589125  Acetaldehyde
      5        0.914344  0.906015  0.903534       Acetone
      6        0.521765  0.575900  0.546296       Toluene
```

보호 기준:
```json
{
  "checks": {
    "complete": true,
    "macro_guard": false,
    "gas_recall_guard": false,
    "other_four_guard": false,
    "zero_count_guard": true,
    "no_new_zero_guard": true
  },
  "all_passed": false,
  "conclusion": "C",
  "mean_macro_delta": -0.13609847499460345,
  "fold_deltas": {
    "A": -0.03991915243792077,
    "B": -0.21850463770505557,
    "C": -0.149871634840834
  },
  "mean_gas_recall_delta": {
    "1": -0.09330727308700008,
    "2": -0.31305082148793,
    "3": -0.007659932659932663,
    "4": -0.1359563375692408,
    "5": 0.055262009717455284,
    "6": -0.1511476264997392
  },
  "mean_gas_f1_delta": {
    "1": -0.041507021084455774,
    "2": -0.3075566554716472,
    "3": -0.21514257089090583,
    "4": -0.15925204103930324,
    "5": -0.006809781496556903,
    "6": -0.0863227799847518
  },
  "other_four_f1_delta": -0.1427540072358914,
  "new_zero_pairs": 0,
  "official_model": "Model A unchanged",
  "future_batches_evaluated": [],
  "frozen_at": "2026-10-27T16:07:46.473866+09:00",
  "new_HGB_fits": 3,
  "reused_SVM": 3,
  "fallback_SVM_fits": 0
}
```

테스트:
```json
{
  "total": 183,
  "passed": 178,
  "failed": 5,
  "historical_failures": 5,
  "new_failures": 0,
  "new_tests": 15,
  "new_passed": 15,
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
      "reason": "AssertionError: assert {'models\\\\A_r....joblib', ...} == {'models\\\\A_r....joblib', ...}\n  \n  Extra items in the right set:\n  'models\\\\temporal_weighting\\\\C\\\\class_sample.joblib'\n  'models\\\\temporal_representativeness_control\\\\C_spread_mid_seed42.joblib'\n  'models\\\\temporal_weighting\\\\C\\\\time_exp.joblib'\n  'models\\\\temporal_representativeness_control\\\\A_spread_max_seed42.joblib'\n  'models\\\\temporal_robustness\\\\C\\\\RF_correlation.joblib'...\n  \n  ...Full output truncated (250 lines hidden), use '-vv' to show"
    },
    {
      "classname": "tests.test_temporal_generalization_validation",
      "name": "test_existing_files_raw_and_model_inventory_preserved",
      "historical": true,
      "reason": "AssertionError: assert {'models\\\\A_r....joblib', ...} == {'models\\\\A_r....joblib', ...}\n  \n  Extra items in the left set:\n  'models\\\\temporal_representativeness_control\\\\C_recent_mid_seed23.joblib'\n  'models\\\\temporal_representativeness_control\\\\C_spread_mid_seed42.joblib'\n  'models\\\\temporal_representativeness_control\\\\A_spread_max_seed42.joblib'\n  'models\\\\temporal_representativeness_control\\\\A_spread_mid_anchor_unit_seed101.joblib'\n  'models\\\\temporal_representativeness_control\\\\C_spread_max_seed101.joblib'...\n  \n  ...Full output truncated (153 lines hidden), use '-vv' to show"
    },
    {
      "classname": "tests.test_toluene_deep_diagnostic",
      "name": "test_preserved_files_raw_models_and_config",
      "historical": true,
      "reason": "AssertionError: assert ({'models\\\\A_r....joblib', ...} == {'models\\\\A_r....joblib', ...}\n  \n  Extra items in the right set:\n  'models\\\\temporal_representativeness_control\\\\C_recent_mid_seed23.joblib'\n  'models\\\\temporal_representativeness_control\\\\C_spread_mid_seed42.joblib'\n  'models\\\\temporal_representativeness_control\\\\A_spread_max_seed42.joblib'\n  'models\\\\temporal_representativeness_control\\\\A_spread_mid_anchor_unit_seed101.joblib'\n  'models\\\\temporal_representativeness_control\\\\C_spread_max_seed101.joblib'...\n  \n  ...Full output truncated (153 lines hidden), use '-vv' to show)"
    }
  ]
}
```

## 계산 결과의 상세 해석

- 계산 결과: HGB 평균 Macro F1 66.10% 대 SVM 79.71%, 차이-13.61pp. 세 Fold 모두 HGB가 낮음.

- 가스별 Fold 평균 F1은6종 모두 하락. 일부 Precision·Recall 향상만으로 B로 판정하지 않는 사전 규칙에 따라 C(개선 근거 부족). 새 우수 후보 없음. 공식 Model A 유지.

- Fold A Toluene467개는 HGB·SVM 모두 정답0개. HGB는448개를 Acetaldehyde로 오분류해 기준416개보다 증가. 새로운 알고리즘도 이 공동 실패를 해결하지 못함.

- Fold B Acetaldehyde: HGB 정답132/744개, Recall17.74%. Toluene 오분류는67→2개로 줄었지만 기타 가스 오분류는219→610개로 증가. 오류 방향 감소를 정분류 개선으로 해석하면 안 됨.

- Fold C Ethylene: HGB 정답1/30개, Recall3.33%. 새로운0% 조합은 없지만 거의 실패하는 가스가 있어0% 개수만으로 안정성을 판단할 수 없음.

- 다른 네 가스 평균 F1 변화-14.28pp. Acetone 평균 Recall은 상승했지만 Precision 손실과 함께 평균 F1은 하락. 초점 가스만 보지 않고6종 전체의 손익을 공개함.

- 오류 구조: 두 모델 공동 오답968개, SVM만 정답880개, HGB만 정답144개. 합산 표본 수는 크기가 다른 개발 Batch의 합이며 동일 Fold 가중 평균과 구분. 상호 보완성이 있어도 앙상블 이득을 보장하지 않으며 이번에는 결합 미실행.

- 학습 비용: HGB3회 총56.12초. SVM 학습0초는 저장 모델 재사용을 뜻하며 SVM 자체 학습 비용이0이라는 뜻이 아님. 단회 추론 시간은 환경·캐시·표본 수에 의존하므로 일반적인 속도 우월성을 주장하지 않음.

- 해석: 이번 고정 기본 설정 HGB는 현재 시간순 개발 과제에서 기준보다 불리함. HGB의 최적 성능 상한, 모든 부스팅 알고리즘의 무효, 드리프트 단독 원인 또는 과적합 원인을 입증한 것은 아님.

- 후속 검토가 필요하면 별도 계획·작은 예산·시간순 검증을 사전에 정해야 함. 현재 결과로 즉석 튜닝이나 SVM·HGB 결합을 추가하지 않음. 새로운 시기의 독립 자료 확보가 여전히 중요함.

- 전체 테스트 178개 통과 / 5개 실패. 기존 실패5개, 신규 실패0개, 신규 검사15/15개 통과.
