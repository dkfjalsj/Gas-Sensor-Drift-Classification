# 18.5단계 가스 구성·창 구성 민감도 진단

- 고정 감지기의 사후 민감도 진단이며 실제 센서 드리프트 탐지 정확도 검증 아님. 라벨 기반 구성 통제는 운영용 무라벨 평가가 아님. 반복 개발 자료이며 독립 Test 없음. Batch9~10 원본 읽기·평가 없음. 모델·임계값 변경 없음.

- 최종 판정: A — 감지기 민감도와 교란 요인 정량 설명. 실제 드리프트 감지 정확도나 원인의 독립 분리 성공을 뜻하지 않음.

- A 분석은 기존38개 창의 저장 점수·경고·오류율을 그대로 재사용함. 가스 비율 차이는 TV=0.5Σ|p_window−p_reference|로 계산함.

- B2 전체 재배열은 원본 잔여 행 일부가 평가에 들어가고 다른 행이 제외될 수 있음. 따라서 순서만의 효과라고 해석하지 않음. 보조 조건은 기존 평가3,600/200행과 제외13/94행을 고정해 창 구성 변화만 비교함.

- 구성 통제는 정답 라벨로 창을 만드는 사후 진단이며 감지기에 라벨을 전달하지 않음. Reference 비율의100행 할당량은 Ethanol:21, Ethylene:26, Ammonia:9, Acetaldehyde:8, Acetone:27, Toluene:9임.

- 같은 출처·시드·비교 안에서는 복제 없이 추출함. 시드 간 및 서로 다른 비교에서는 같은 원본 행이 재사용될 수 있으므로 독립 반복이나 신뢰구간으로 취급하지 않음.

- 구성 통제의 내부 비교 자료는 기존 INTERNAL 평가 풀임. Reference와 임계값 산정 풀의 행은 통제 평가 창에 포함하지 않았음. 내부 풀은 여러 과거 Batch 혼합이며 대상 창은 각 Batch 내부에서만 구성함.

- 전체 평균 RFF 차이와 창 간 변동의 합은 창 평균 MMD²와 같음. 동일 행 조건의 재배열은 전체 평균 차이를 유지하면서 창 간 변동을 바꿀 수 있음. 전체 평균 차이에100행 임계값을 직접 적용하지 않았음.

- 경고 점수·구성·오류의 상관은 기술 통계이며 시기·농도·환경의 독립 효과를 구분하지 못함. 상관이 약해도 가스 구성 영향이 없다는 증거가 아님. 높은 점수도 분류 실패의 보장은 아님.

- 웹앱에서는 '설정된 참조와 다른 센서 측정 분포'로 표시해야 함. 드리프트 발생 확률·장비 고장·예상 정확도로 표시하지 말 것. 입력100행의 가스 구성과 배열에 민감할 수 있고, 경고가 없어도 분류 정확도를 보장하지 않음을 안내할 필요가 있음.

- 19단계 통합이나 기존 경고 문구·감지기 수정은 이번에 수행하지 않음. 실제 운영 전 입력 창 수집 규칙과 기준 가스 구성의 적합성을 정하고 별도 신규 자료로 검증 필요함. 현재 결과로 임계값·창 크기·최적 시드를 재선정하지 않았음.

- 시험 제한: 과거 전체 데이터 테스트의 Batch9~10 원본 읽기와 기존 산출물 쓰기를 감사 훅으로 차단함. 제한으로 건너뛴 검사는 통과가 아니며 상세 기록은 test_summary.json과 test_access_blocks.json 참조. 이번 보존 검사는 원본1~8만 재검증하며9~10은 열지 않았음.

- 구성 통제 B7: 대상 최대23창, 내부 최대14창, 출처마다14창 (1400행) 사용. 대상 미선택2213행, 내부 미선택84행. 특히1창 조건은 평가 불확실성이 큼.

- 구성 통제 B8: 대상 최대1창, 내부 최대14창, 출처마다1창 (100행) 사용. 대상 미선택194행, 내부 미선택1384행. 특히1창 조건은 평가 불확실성이 큼.

- 계산값 B7 shuffle_all: 평균 점수0.0406849, 원본 대비-59.38%, 시드 평균 경고율100.00%.

- 계산값 B7 shuffle_fixed_rows: 평균 점수0.0403979, 원본 대비-59.66%, 시드 평균 경고율100.00%.

- 계산값 B7 composition_controlled: 평균 점수0.0281814, 원본 대비-71.86%, 시드 평균 경고율100.00%.

- 계산값 B8 shuffle_all: 평균 점수0.204938, 원본 대비-10.18%, 시드 평균 경고율100.00%.

- 계산값 B8 shuffle_fixed_rows: 평균 점수0.20909, 원본 대비-8.36%, 시드 평균 경고율100.00%.

- 계산값 B8 composition_controlled: 평균 점수0.222819, 원본 대비-2.34%, 시드 평균 경고율100.00%.

- 기존38창 사후 Spearman: score vs mixture_tv=-0.003. 인과·예측력 주장 없음.

- 기존38창 사후 Spearman: score vs gas_classes=-0.001. 인과·예측력 주장 없음.

- 기존38창 사후 Spearman: score vs error_rate=-0.292. 인과·예측력 주장 없음.

## 조건별 결과

```text
                method  seed  target   source  input_rows  used_rows  windows  excluded_tail_rows  mean_score  median_score  min_score  max_score  alert_windows  alert_rate  mean_tv  mean_gas_classes  global_mean_distance_squared  between_window_variation
              original     0       7   target        3613       3600       36                  13    0.100152      0.084069   0.057273   0.256697             36    1.000000 0.641606          2.277778                      0.038027                  0.062126
           shuffle_all    42       7   target        3613       3600       36                  13    0.040614      0.039336   0.027611   0.058682             36    1.000000 0.207161          6.000000                      0.038235                  0.002379
    shuffle_fixed_rows    42       7   target        3613       3600       36                  13    0.040406      0.040636   0.028704   0.056581             36    1.000000 0.210597          6.000000                      0.038027                  0.002379
           shuffle_all    43       7   target        3613       3600       36                  13    0.040922      0.039090   0.026063   0.065703             36    1.000000 0.215714          6.000000                      0.038111                  0.002811
    shuffle_fixed_rows    43       7   target        3613       3600       36                  13    0.040845      0.040824   0.025545   0.055910             36    1.000000 0.216384          6.000000                      0.038027                  0.002818
           shuffle_all    44       7   target        3613       3600       36                  13    0.040627      0.040793   0.025073   0.055439             36    1.000000 0.211147          6.000000                      0.038153                  0.002474
    shuffle_fixed_rows    44       7   target        3613       3600       36                  13    0.040005      0.039950   0.029310   0.058112             36    1.000000 0.211683          6.000000                      0.038027                  0.001978
           shuffle_all    45       7   target        3613       3600       36                  13    0.040583      0.040122   0.027554   0.053285             36    1.000000 0.208613          6.000000                      0.038176                  0.002407
    shuffle_fixed_rows    45       7   target        3613       3600       36                  13    0.040477      0.039222   0.028016   0.054748             36    1.000000 0.208646          6.000000                      0.038027                  0.002451
           shuffle_all    46       7   target        3613       3600       36                  13    0.040678      0.040292   0.029436   0.053659             36    1.000000 0.216056          6.000000                      0.038228                  0.002451
    shuffle_fixed_rows    46       7   target        3613       3600       36                  13    0.040257      0.041422   0.029655   0.052531             36    1.000000 0.213873          6.000000                      0.038027                  0.002230
composition_controlled    42       7 internal        1400       1400       14                   0    0.003210      0.002432   0.001745   0.010373              1    0.071429 0.006662          6.000000                      0.000123                  0.003087
composition_controlled    42       7   target        1400       1400       14                   0    0.027518      0.027574   0.024877   0.029685             14    1.000000 0.006662          6.000000                      0.026265                  0.001253
composition_controlled    43       7 internal        1400       1400       14                   0    0.002989      0.002290   0.001301   0.006800              0    0.000000 0.006662          6.000000                      0.000117                  0.002872
composition_controlled    43       7   target        1400       1400       14                   0    0.027954      0.027828   0.024544   0.030354             14    1.000000 0.006662          6.000000                      0.026873                  0.001081
composition_controlled    44       7 internal        1400       1400       14                   0    0.003097      0.003115   0.000832   0.005649              0    0.000000 0.006662          6.000000                      0.000118                  0.002979
composition_controlled    44       7   target        1400       1400       14                   0    0.029151      0.028643   0.024881   0.034407             14    1.000000 0.006662          6.000000                      0.027945                  0.001206
composition_controlled    45       7 internal        1400       1400       14                   0    0.004205      0.002737   0.000969   0.012226              3    0.214286 0.006662          6.000000                      0.000145                  0.004060
composition_controlled    45       7   target        1400       1400       14                   0    0.028129      0.028120   0.025011   0.031452             14    1.000000 0.006662          6.000000                      0.026430                  0.001699
composition_controlled    46       7 internal        1400       1400       14                   0    0.002276      0.002227   0.001106   0.003400              0    0.000000 0.006662          6.000000                      0.000143                  0.002133
composition_controlled    46       7   target        1400       1400       14                   0    0.028155      0.027202   0.024545   0.035677             14    1.000000 0.006662          6.000000                      0.026415                  0.001739
              original     0       8   target         294        200        2                  94    0.228156      0.228156   0.150838   0.305474              2    1.000000 0.635708          2.500000                      0.208775                  0.019381
           shuffle_all    42       8   target         294        200        2                  94    0.201160      0.201160   0.196125   0.206195              2    1.000000 0.326419          6.000000                      0.201037                  0.000123
    shuffle_fixed_rows    42       8   target         294        200        2                  94    0.208896      0.208896   0.202857   0.214934              2    1.000000 0.566419          3.000000                      0.208775                  0.000121
           shuffle_all    43       8   target         294        200        2                  94    0.204908      0.204908   0.201325   0.208491              2    1.000000 0.291419          6.000000                      0.204742                  0.000166
    shuffle_fixed_rows    43       8   target         294        200        2                  94    0.209338      0.209338   0.192354   0.226323              2    1.000000 0.566419          3.000000                      0.208775                  0.000563
           shuffle_all    44       8   target         294        200        2                  94    0.205887      0.205887   0.193497   0.218277              2    1.000000 0.321419          6.000000                      0.205454                  0.000433
    shuffle_fixed_rows    44       8   target         294        200        2                  94    0.209116      0.209116   0.200501   0.217732              2    1.000000 0.566419          3.000000                      0.208775                  0.000341
           shuffle_all    45       8   target         294        200        2                  94    0.203820      0.203820   0.200242   0.207398              2    1.000000 0.306419          6.000000                      0.203647                  0.000173
    shuffle_fixed_rows    45       8   target         294        200        2                  94    0.209055      0.209055   0.199685   0.218426              2    1.000000 0.566419          3.000000                      0.208775                  0.000280
           shuffle_all    46       8   target         294        200        2                  94    0.208915      0.208915   0.197367   0.220463              2    1.000000 0.296419          6.000000                      0.208611                  0.000304
    shuffle_fixed_rows    46       8   target         294        200        2                  94    0.209042      0.209042   0.204442   0.213642              2    1.000000 0.566419          3.000000                      0.208775                  0.000267
composition_controlled    42       8 internal         100        100        1                   0    0.001890      0.001890   0.001890   0.001890              0    0.000000 0.006662          6.000000                      0.001890                  0.000000
composition_controlled    42       8   target         100        100        1                   0    0.220619      0.220619   0.220619   0.220619              1    1.000000 0.006662          6.000000                      0.220619                  0.000000
composition_controlled    43       8 internal         100        100        1                   0    0.002125      0.002125   0.002125   0.002125              0    0.000000 0.006662          6.000000                      0.002125                  0.000000
composition_controlled    43       8   target         100        100        1                   0    0.216280      0.216280   0.216280   0.216280              1    1.000000 0.006662          6.000000                      0.216280                  0.000000
composition_controlled    44       8 internal         100        100        1                   0    0.001507      0.001507   0.001507   0.001507              0    0.000000 0.006662          6.000000                      0.001507                  0.000000
composition_controlled    44       8   target         100        100        1                   0    0.228462      0.228462   0.228462   0.228462              1    1.000000 0.006662          6.000000                      0.228462                  0.000000
composition_controlled    45       8 internal         100        100        1                   0    0.003747      0.003747   0.003747   0.003747              0    0.000000 0.006662          6.000000                      0.003747                  0.000000
composition_controlled    45       8   target         100        100        1                   0    0.226591      0.226591   0.226591   0.226591              1    1.000000 0.006662          6.000000                      0.226591                  0.000000
composition_controlled    46       8 internal         100        100        1                   0    0.002530      0.002530   0.002530   0.002530              0    0.000000 0.006662          6.000000                      0.002530                  0.000000
composition_controlled    46       8   target         100        100        1                   0    0.222143      0.222143   0.222143   0.222143              1    1.000000 0.006662          6.000000                      0.222143                  0.000000
```

## 시드 변동

```text
                method  target   source  seeds  mean_score  seed_sd_mean_score  min_seed_mean  max_seed_mean  mean_alert_rate  min_alert_rate  max_alert_rate  seed_sd_alert_rate
composition_controlled       7 internal      5    0.003155            0.000691       0.002276       0.004205         0.057143             0.0        0.214286            0.093131
composition_controlled       7   target      5    0.028181            0.000599       0.027518       0.029151         1.000000             1.0        1.000000            0.000000
composition_controlled       8 internal      5    0.002360            0.000860       0.001507       0.003747         0.000000             0.0        0.000000            0.000000
composition_controlled       8   target      5    0.222819            0.004851       0.216280       0.228462         1.000000             1.0        1.000000            0.000000
           shuffle_all       7   target      5    0.040685            0.000137       0.040583       0.040922         1.000000             1.0        1.000000            0.000000
           shuffle_all       8   target      5    0.204938            0.002839       0.201160       0.208915         1.000000             1.0        1.000000            0.000000
    shuffle_fixed_rows       7   target      5    0.040398            0.000308       0.040005       0.040845         1.000000             1.0        1.000000            0.000000
    shuffle_fixed_rows       8   target      5    0.209090            0.000161       0.208896       0.209338         1.000000             1.0        1.000000            0.000000
```

## 전체 테스트

```json
{
  "total": 234,
  "passed": 143,
  "failed": 2,
  "skipped": 89,
  "historical_failures": 2,
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
      "classname": "tests.test_temporal_failure_diagnostics",
      "name": "test_no_new_fit_calls_or_new_model_files",
      "historical": true,
      "reason": "AssertionError: assert {'models\\\\A_r....joblib', ...} == {'models\\\\A_r....joblib', ...}\n  \n  Extra items in the right set:\n  'models\\\\temporal_representativeness_control\\\\B_early_mid_seed11.joblib'\n  'models\\\\temporal_representativeness_control\\\\A_spread_mid_anchor_seed67.joblib'\n  'models\\\\temporal_representativeness_control\\\\A_early_mid_seed67.joblib'\n  'models\\\\temporal_representativeness_control\\\\C_spread_mid_unit_seed67.joblib'\n  'models\\\\temporal_weighting\\\\B\\\\class_balanced.joblib'...\n  \n  ...Full output truncated (278 lines hidden), use '-vv' to show"
    }
  ],
  "skipped_tests": [
    {
      "classname": "tests.test_diagnostics",
      "name": "test_wasserstein_same_gas_train_reference",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_drift_detection",
      "name": "test_real_files_and_plan_preserved",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_gas_specific_temporal_balancing",
      "name": "test_plan_budget_and_all_seeds_frozen",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_gas_specific_temporal_balancing",
      "name": "test_sampling_reproducibility_and_exact_gas_budgets",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_gas_specific_temporal_balancing",
      "name": "test_mixed_rule_uses_only_past_training_counts",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_gas_specific_temporal_balancing",
      "name": "test_minimum_representation_and_capacity_constraints",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_gas_specific_temporal_balancing",
      "name": "test_model_reuse_is_exact_and_new_files_are_separate",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_gas_specific_temporal_balancing",
      "name": "test_preprocessing_and_class_weight_train_only",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_gas_specific_temporal_balancing",
      "name": "test_saved_prediction_reproducibility",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_gas_specific_temporal_balancing",
      "name": "test_existing_files_models_raw_and_plan_preserved",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_hgb_algorithm_comparison",
      "name": "test_ordered_rows_feature_hashes_and_temporal_separation",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_hgb_algorithm_comparison",
      "name": "test_train_only_imputation_and_hgb_input_order",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_hgb_algorithm_comparison",
      "name": "test_balanced_class_weights_computed_only_from_train",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_hgb_algorithm_comparison",
      "name": "test_no_internal_or_external_validation_fit",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_hgb_algorithm_comparison",
      "name": "test_model_reload_matches_saved_predictions",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_hgb_algorithm_comparison",
      "name": "test_prior_files_raw_models_preserved_and_graphs_complete",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_improvement",
      "name": "test_historical_test_exclusion_and_class_coverage",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_improvement",
      "name": "test_duplicate_guard",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_improvement",
      "name": "test_train_only_transformer_statistics",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_improvement",
      "name": "test_saved_models_replay_all_predictions",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_improvement",
      "name": "test_preservation_and_frozen_plan",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_models",
      "name": "test_real_split_sizes_disjointness_and_chronology",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_models",
      "name": "test_split_guard_rejects_cross_partition_duplicate",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_models",
      "name": "test_saved_pipelines_train_statistics_and_reload_predictions",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_models",
      "name": "test_eda_and_sources_preserved_report_complete",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_nonlinear_feature_transformation",
      "name": "test_time_order_equal_rows_and_no_exact_overlap",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_nonlinear_feature_transformation",
      "name": "test_preprocessing_train_only_and_feature_order",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_nonlinear_feature_transformation",
      "name": "test_saved_models_prediction_reproduction",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_nonlinear_feature_transformation",
      "name": "test_gamma_records_match_actual_train_variance",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_nonlinear_feature_transformation",
      "name": "test_original_files_raw_data_and_plan_preserved",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_calibration",
      "name": "test_calibration_evaluation_disjoint_nested_and_exact_counts",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_calibration",
      "name": "test_original_row_ids_and_split_reproducibility",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_calibration",
      "name": "test_same_evaluation_for_every_rate_and_exact_past_train",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_calibration",
      "name": "test_train_only_preprocessing_and_classifier_parameters",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_calibration",
      "name": "test_balanced_weights_combined_train_only",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_calibration",
      "name": "test_saved_models_and_reloaded_predictions",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_calibration",
      "name": "test_regression_set_is_existing_heldout_and_no_train_score_proxy",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_calibration",
      "name": "test_no_future_evaluation_and_historical_files_preserved",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_expansion",
      "name": "test_temporal_split_counts_and_classes",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_expansion",
      "name": "test_duplicate_features_rejected",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_expansion",
      "name": "test_preprocessing_fit_train_only",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_expansion",
      "name": "test_saved_model_predictions_reproduced",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_expansion",
      "name": "test_preservation_and_reports",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_failure_diagnostics",
      "name": "test_replay_without_model_fit",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_failure_diagnostics",
      "name": "test_feature_stats_and_wasserstein",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_failure_diagnostics",
      "name": "test_proximity_and_kernel_values",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_failure_diagnostics",
      "name": "test_prior_files_raw_and_report_preserved",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_generalization_validation",
      "name": "test_fixed_models_and_train_only_preprocessing",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_generalization_validation",
      "name": "test_korean_font_and_sensor_plot_statistics",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_generalization_validation",
      "name": "test_existing_files_raw_and_model_inventory_preserved",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_representativeness_control",
      "name": "test_frozen_budget_scope_and_exact_counts",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_representativeness_control",
      "name": "test_sampling_reproduces_all_120_subsets",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_representativeness_control",
      "name": "test_allocation_capacity_and_absent_cells",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_representativeness_control",
      "name": "test_spread_budgets_are_nested_and_controls_share_rows",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_representativeness_control",
      "name": "test_native_and_anchor_preprocessing_are_train_only",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_representativeness_control",
      "name": "test_saved_models_parameters_and_predictions_reproduce",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_representativeness_control",
      "name": "test_existing_model_reference_predictions_unchanged",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_representativeness_control",
      "name": "test_prior_files_and_raw_hashes_preserved",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_robustness",
      "name": "test_fixed_folds_and_support",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_robustness",
      "name": "test_train_only_preprocessing_and_feature_inputs",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_robustness",
      "name": "test_feature_selection_uses_training_statistics",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_robustness",
      "name": "test_serialized_fold_and_ensemble_predictions_reproduce",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_robustness",
      "name": "test_evaluation_gate_and_baseline_reproduction",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_robustness",
      "name": "test_existing_files_and_raw_preserved",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_svm_ensemble",
      "name": "test_expert_rows_reproducible_past_only_and_same_validation",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_svm_ensemble",
      "name": "test_recent_and_spread_have_equal_gas_budgets_and_no_future_dependence",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_svm_ensemble",
      "name": "test_train_only_scaler_imputer_mapping_and_support_vectors",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_svm_ensemble",
      "name": "test_reloaded_expert_predictions_and_rank_mapping",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_svm_ensemble",
      "name": "test_ensemble_gate_execution_and_predictions",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_svm_ensemble",
      "name": "test_raw_models_sources_preserved_and_no_future_predictions",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_weighting",
      "name": "test_fixed_fold_counts_and_support",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_weighting",
      "name": "test_weight_formulas_limits_and_actual_cells",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_weighting",
      "name": "test_train_only_scaling_and_effective_class_weight",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_weighting",
      "name": "test_fold_prediction_reproduction_and_metrics",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_weighting",
      "name": "test_common_range_comparison_on_future_batch8",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_weighting",
      "name": "test_evaluation_reproduction_and_per_class_metrics",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_temporal_weighting",
      "name": "test_existing_files_and_raw_preserved",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_toluene",
      "name": "test_distance_and_overlap_reference",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_toluene",
      "name": "test_historical_and_current_preservation",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_toluene_deep_diagnostic",
      "name": "test_model_hashes_and_original_preprocessing",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_toluene_deep_diagnostic",
      "name": "test_prediction_replay_and_batch9_support",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_toluene_deep_diagnostic",
      "name": "test_ovo_ovr_reconstruction_and_native_votes",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_toluene_deep_diagnostic",
      "name": "test_exact_neighbors_and_training_only_candidates",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_toluene_deep_diagnostic",
      "name": "test_sensor_statistics_correlations_and_class_weights",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_toluene_deep_diagnostic",
      "name": "test_pca_fits_only_train_and_coordinates_reproduce",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_toluene_deep_diagnostic",
      "name": "test_preserved_files_raw_models_and_config",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_validation",
      "name": "test_real_structure_and_expected_totals",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_validation",
      "name": "test_report_numbers_and_source_integrity",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    },
    {
      "classname": "tests.test_validation",
      "name": "test_saved_splits_reproducible_and_temporal",
      "reason": "18.5단계 접근 제한: Batch9~10 원본 열기 금지"
    }
  ]
}
```


## 최종 관찰과 해석

- 핵심 관찰: 원본·전체 재배열·평가 행 고정 재배열·가스 구성 통제의 대상 창 모두 경고율100%를 유지함. 이번 범위에서 경고 여부는 안정적이지만 점수 크기는 창 구성에 민감함.

- 계산값: Batch7 원본 평균0.100152가 전체 재배열0.040685(-59.38%), 동일 평가 행 재배열0.040398(-59.66%)로 감소함. Batch8은0.228156에서 각각0.204938(-10.18%), 0.209090(-8.36%)로 감소함. 전체 재배열은 제외 행도 달라질 수 있어 두 조건을 구분함.

- 계산값: 전체 재배열5개 시드의 평균 점수 범위는 Batch7 0.040583~0.040922, Batch8 0.201160~0.208915임. 유리한 시드를 선택하지 않았으며 시드 SD는 독립 미래 환경의 불확실성 추정치가 아님.

- 계산값: 동일 가스 할당량 창의 대상/내부 평균은 Batch7 0.028181/0.003155, Batch8 0.222819/0.002360임. 내부 출처의 시드 평균 경고율은 각각5.71%/0%, 대상은 모두100%임. Batch7은 출처마다14창, Batch8은1창을 사용했으며 반복 시드의 표본이 겹칠 수 있어70개 또는5개의 독립 새 표본이라고 해석하지 않음.

- 해석: 가스 구성·창 구성을 통제해도 대상과 내부 기준의 차이가 남음. 따라서 기존 100% 경고를 가스 구성만의 결과라고 설명할 수 없지만, 남은 차이가 물리적 센서 드리프트라고 확정할 수도 없음. 조건 통제는 선택 표본도 바꾸며 농도·환경·시기별 가스 내 반응 차이를 분리하지 못함.

- 해석: 동일 평가 행 재배열에서 전체 평균 RFF 차이는 유지됐고 창 간 변동 항이 줄었음. 이 수학적 분해는 창 묶음에 대한 점수 민감도를 설명하며 드리프트의 인과 효과를 추정한 결과가 아님.

- 사후 관계: 기존38창에서 점수와 가스 비율 TV·가스 종류 수의 Spearman은 모두 약0이며, 점수와 분류 오류율은 약-0.292임. 관찰 상관이 작다는 사실로 구성 영향을 배제하지 않음. 점수 크기를 분류 오류의 일관된 순위나 정확도 예측값으로 쓰는 근거도 확보하지 못함.

- 웹앱 전 검토: '설정된 참조와 다른 측정 분포'라는 의미와 가스 구성·창 구성의 영향을 화면에 명시할 필요가 있음. 실제 고장 경보나 분류 성능 경보로 사용하려면 입력 창 수집 규칙과 운영 목적에 맞춘 별도 검증이 필요함. 이번에는 기존 코드·문구·임계값 수정 및19단계 통합을 하지 않았음.

- 테스트 해석:143개 통과·2개 역사적 실패·89개 접근 제한 건너뜀. 신규15개 모두 통과. 기존 실패5개 중2개는 그대로 재현됐고3개는 Batch9~10 접근이 필요한 검사여서 건너뜀. 건너뜀은 해결이나 통과가 아님. 실패2개는 과거 누락 임시 파일과 고정 모델 목록 검사임. 기존 기준이나 과거 해시 기록은 수정하지 않았음.

- 보존 범위: 기존325개 모델과 기존 코드·산출물의 SHA-256이 유지됨. 원본1~8을 재검증했고9~10은 읽기 금지에 따라 해시 재검증도 하지 않았음. 테스트에서32번의 금지 원본 접근 시도를 파일 열기 전에 차단했고 이 제한이89개 건너뜀에 반영됨.
