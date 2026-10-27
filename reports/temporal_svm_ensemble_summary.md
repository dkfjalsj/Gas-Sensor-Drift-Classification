# 15단계 시기별 SVM 진단·결합 요약

새 독립 Test 없음. 과거 Fold는 반복 사용된 개발 검증 자료이며 학습 구간이 겹침. Batch 9~10 신규 평가 없음. 공식 Model A 유지.

- 연구 결론 B — 부분 개선. 공식 Model A 유지.

- 전문가 평가 9건, 기존 모델 재사용 9개, 신규 SVC 학습 1회, 조건부 결합 평가 6건.

- 게이트 통과=True. Oracle 평균 Macro F1과 최고 단독 평균의 차이 +1.56%p. Oracle은 실현 가능한 성능이 아님.

- 동일 표본에서 일부 전문가만 정답인 경우만 오류 상호 보완성으로 계산함. 예측 불일치만으로 개선 가능성을 선언하지 않음.

- 단독 최고 대비 결합의 추가 가치는 above_best_single 열로 별도 공개. 기준 대비 개선이 곧 앙상블 필요성의 증거는 아님.

- 전체형과 부분표본형은 학습량·클래스 구성·balanced 벌점·전처리도 달라짐. 최근형과 분산형은 같은 843개·가스별 수로 대조하되 순수 시기 인과 효과는 아님.

- 시드42는 기본값으로 사전 고정했고 성능으로 고르지 않음. 한 시드의 재사용 진단이므로 부분표본 선택 불확실성을 평가하지 못함.

- 각 전문가가 6종을 학습해도 Fold A의 Toluene 초기 자료 부족은 남음. Fold C Toluene 18개는 Recall 한 표본이5.56pp이며 결과 과대 해석 금지.

- SVM OVR 점수는 모델 내부 클래스 순위만 이용. predict는 OVO 투표에 기반하므로 OVR argmax와 다른 표본 수를 audit에 기록. 확률 해석·raw 점수 평균 없음.

- 8단계 이종 모델 결합과 다른 연구 질문. 과거 Hard Voting의 실패만으로 시기별 결합을 미리 기각하지 않고 사전 게이트로 검토함.

- Fold A Toluene support=467, 정답 수 full/recent/spread=0/0/0, 공동 오답=467. 이 결과만으로 다른 시기 앙상블의 보편적 효용을 단정하지 않음.

- hard_equal: 평균 Macro F1 74.05%, 기준 대비-5.66pp, 최고 단독 대비-5.66pp, 보호 조건 전부 통과=False, 최악 Fold 변화-12.67pp, Recall0 조합1, 신규0 조합0.

- rank_equal: 평균 Macro F1 70.32%, 기준 대비-9.39pp, 최고 단독 대비-9.39pp, 보호 조건 전부 통과=False, 최악 Fold 변화-21.81pp, Recall0 조합1, 신규0 조합0.

- 다음 연구는 새 실험 전에 별도 계획 고정 필요. Oracle과 실제 결합의 격차가 크면 현재 결합 규칙의 한계를 뜻하나, 사후 가스별 가중치나 미래 결과로 규칙을 수정하지 않음.

```text
fold           A     B     C
model                       
full       61.99 89.69 87.44
hard_equal 61.47 85.91 74.78
oracle     62.42 91.46 89.92
rank_equal 61.64 83.68 65.64
recent     56.61 72.96 57.67
spread     51.08 79.06 48.77
```

```text
     model     role  mean_macro_f1  mean_accuracy  mean_weighted_f1  fold_sd  macro_delta  above_best_single  mean_toluene_recall  mean_acetaldehyde_recall  min_recall  zero_pairs  new_zero_pairs  other_four_f1  worst_fold_delta  macro_guard  gas_recall_guard  other_guard  zero_guard  new_zero_guard  balanced_success conclusion
      full   expert       0.797082       0.829189          0.829635 0.125645     0.000000      -1.110223e-16             0.575900                  0.851662         0.0           1               0       0.911768          0.000000        False              True         True        True            True             False     expert
    recent   expert       0.624153       0.669884          0.677178 0.074706    -0.172929      -1.729293e-01             0.418362                  0.819648         0.0           1               0       0.750999         -0.297689        False             False        False        True            True             False     expert
    spread   expert       0.596367       0.556138          0.562581 0.137655    -0.200715      -2.007153e-01             0.621153                  0.713791         0.0           1               0       0.711895         -0.386763        False             False        False        True            True             False     expert
    oracle   oracle       0.812672       0.842277          0.842047 0.133399     0.015590       1.559001e-02             0.648148                  0.874552         0.0           1               0       0.920071          0.004358         True              True         True        True            True             False     oracle
hard_equal ensemble       0.740510       0.736962          0.753038 0.099907    -0.056572      -5.657200e-02             0.567423                  0.825228         0.0           1               0       0.881421         -0.126669        False             False        False        True            True             False          B
rank_equal ensemble       0.703184       0.715303          0.727737 0.095858    -0.093898      -9.389806e-02             0.567423                  0.818304         0.0           1               0       0.837723         -0.218065        False             False        False        True            True             False          B
```

```text
             support  full_correct  recent_correct  spread_correct  some_correct  all_wrong  oracle_rescue
fold y_true                                                                                               
A    4            29            29              29              29             0          0              0
     6           467             0               0               0             0        467              0
B    4           744           458             364             263           215        280              6
     6           568           508             208             522           360          0             60
C    4            33            31              32              26             8          0              2
     6            18            15              16              17             2          1              2
```

정답을 알고 전문가를 선택한 가상 상한이며 실제 배포 가능한 모델이 아님. Accuracy·가스 Recall은 선택형 상한. Macro F1은 공동 오답에서 full 예측을 유지한 고정 Oracle의 점수이며 모든 오답 배치를 최적화한 수학적 상한은 아님.

테스트:
```json
{
  "total": 168,
  "passed": 163,
  "failed": 5,
  "historical_failures": 5,
  "new_failures": 0,
  "new_tests": 17,
  "new_passed": 17,
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
      "reason": "AssertionError: assert {'models\\\\A_r....joblib', ...} == {'models\\\\A_r....joblib', ...}\n  \n  Extra items in the right set:\n  'models\\\\temporal_robustness\\\\A\\\\RF_variance.joblib'\n  'models\\\\temporal_robustness\\\\B\\\\LR_correlation.joblib'\n  'models\\\\temporal_robustness\\\\B\\\\rank_svm2.joblib'\n  'models\\\\temporal_representativeness_control\\\\A_early_mid_seed101.joblib'\n  'models\\\\temporal_representativeness_control\\\\B_spread_mid_unit_seed101.joblib'...\n  \n  ...Full output truncated (247 lines hidden), use '-vv' to show"
    },
    {
      "classname": "tests.test_temporal_generalization_validation",
      "name": "test_existing_files_raw_and_model_inventory_preserved",
      "historical": true,
      "reason": "AssertionError: assert {'models\\\\A_r....joblib', ...} == {'models\\\\A_r....joblib', ...}\n  \n  Extra items in the left set:\n  'models\\\\temporal_representativeness_control\\\\C_early_mid_seed67.joblib'\n  'models\\\\temporal_representativeness_control\\\\C_spread_mid_anchor_seed42.joblib'\n  'models\\\\temporal_representativeness_control\\\\B_spread_max_seed67.joblib'\n  'models\\\\nonlinear_feature_transformation\\\\C_signed_log.joblib'\n  'models\\\\temporal_representativeness_control\\\\B_spread_max_seed23.joblib'...\n  \n  ...Full output truncated (150 lines hidden), use '-vv' to show"
    },
    {
      "classname": "tests.test_toluene_deep_diagnostic",
      "name": "test_preserved_files_raw_models_and_config",
      "historical": true,
      "reason": "AssertionError: assert ({'models\\\\A_r....joblib', ...} == {'models\\\\A_r....joblib', ...}\n  \n  Extra items in the right set:\n  'models\\\\temporal_representativeness_control\\\\C_early_mid_seed67.joblib'\n  'models\\\\temporal_representativeness_control\\\\C_spread_mid_anchor_seed42.joblib'\n  'models\\\\temporal_representativeness_control\\\\B_spread_max_seed67.joblib'\n  'models\\\\nonlinear_feature_transformation\\\\C_signed_log.joblib'\n  'models\\\\temporal_representativeness_control\\\\B_spread_max_seed23.joblib'...\n  \n  ...Full output truncated (150 lines hidden), use '-vv' to show)"
    }
  ]
}
```

## 핵심 관찰 및 기술 실행 이력

- 동일 Validation 표본 총 6207개 중 일부 전문가만 정답 1481개, 공동 오답 1025개, 예측 불일치 1897개. 이 합산은 크기가 다른 개발 Batch를 합한 표본 수이며 주 선정 지표의 동일 Fold 평균과 구분함.
- 기준 full의 오답을 다른 전문가가 구제할 수 있는 표본은 87개에 불과함. 반대로 full만 정답인 표본은 337개. 일부만 정답인 표본이 많아도 약한 전문가가 강한 전문가를 돕는 방향이라고 해석할 수 없음.
- Fold A Toluene 467개는 세 전문가 모두 정답0개, 416개를 Acetaldehyde로 오분류. 나머지51개의 예측은 전문가별로 다르지만 모두 오답. 단순 결합으로 해당 공동 실패를 구제하지 못함.
- Fold B Toluene은 적어도 한 전문가가568개 전부를 맞혀 Oracle 여지가 있었으나, 이는 정답을 아는 선택이며 실제 결합의 성능 보장이 아님.
- 다수결·순위 결합 모두 전체형 기준보다 평균 Macro F1과 Toluene·Acetaldehyde 평균 Recall이 낮음. 각 후보는 Macro F1·가스 Recall·나머지4종F1 보호 기준에 미달. 신규 Recall0 조합은 없으나 기존0도 해결 못함.
- 사전 규칙상 일부 가스의 지표 향상이 있어 B(부분 개선)로 분류하지만, 실질적인 평균·균형 개선 실패이며 새로운 우수 후보를 선정한 결과가 아님.
- 학습량·클래스 구성 차이가 있는 843개 부분표본 전문가가 전체형보다 약했음. 해당 고정 전문가·규칙의 결과이며 시기별 SVM 앙상블 전체의 무효를 입증한 것은 아님.
- 기술 이력: sklearn1.9의 probability 기본값 deprecated를 False와 다르게 처리한 검사 오류로 불필요한 SVC 학습1회가 완료된 뒤 검사에서 중단됨. 해당 모델은 평가·저장·결합하지 않았음. 중단 전에 full/Fold A의 재현 평가1회가 있어9개 고정 전문가 평가와 별도로 기록함.
- 검사 호환성만 수정한 뒤9개 저장 전문가를 전부 재사용. 추가 학습0회. 메타데이터 NumPy bool 저장 오류는 완료된 CSV에서 JSON·보고서만 재생성하여 처리함. 계획·게이트·결합 규칙·계산 결과·과거 기록은 변경하지 않았음. 이번 신규 코드 변경 전후 해시는 technical_repair.json과technical_repair_2.json에 보존함.
- 전체 테스트 163개 통과 / 5개 실패. 신규 검사 17/17 통과, 신규 실패0개.
- 다음 연구는 강한 단독 모델을 약한 전문가가 압도하지 않는 구조가 필요한지 먼저 검토할 수 있으나, 이번 Validation을 보고 가중치나 전문가를 사후 변경하지 않음. 독립 새 시기 자료 필요성은 여전함.

```text
            toluene_predicted_n  pooled_prediction_fraction  equal_fold_toluene_precision
model                                                                                    
full                        597                    0.096182                      0.521765
hard_equal                  714                    0.115031                      0.305335
oracle                      659                    0.106170                      0.534274
rank_equal                  763                    0.122926                      0.287198
recent                      394                    0.063477                      0.287691
spread                     1377                    0.221846                      0.176167
```
