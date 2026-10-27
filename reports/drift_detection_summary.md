# 18단계 비지도 분포 변화 감지

- 분포 변화 ≠ 센서 고장 ≠ 모델 성능 저하. 반복 사용한 개발 자료의 사후 진단이며 독립 Test가 아님. 실제 센서 드리프트 탐지 정확도를 측정하지 않음. Batch9~10 신규 점수·평가 없음. 공식 Model A 유지.

- 결론: A — 운영 가능한 감지 프로토타입. 기술적인 구축·검증 판정이며 실제 드리프트 탐지 정확도의 판정이 아님.

- 관찰: 기준 후보 Batch1–6의5,933행을 라벨 없이 무작위 분리함. Reference2,966행, Calibration1,483행, 내부 평가1,484행. Reference에만 중앙값·평균·표준편차·커널 폭 적합.

- 계산값: sigma²=161.54357, gamma=0.0030951403, 고정 임계값=0.008257012. Calibration14창의95백분위수이며 미래 경고율5% 보장 아님.

- 한계: Calibration과 내부 평가는 여러 과거 Batch를 무작위로 섞은 pooled 분포의 창임. Batch7–8은 파일 순서의 창이므로 가스 비율·행 순서·측정 조건 차이가 함께 반영될 수 있음. 기준 자체에도 시간 변화가 있고 무노화 정상 상태 정답은 없음.

- 한계: 같은 Reference를 공유해 창별 점수가 통계적으로 의존함. Calibration14창과 내부14창은 적고, Batch8은 전체294행 중200행·2창만 평가하며94행을 제외함. Batch8 경고율 한 창의 변화는50%p임. 이 자료로 정밀한 오경고율이나 재현율을 추정하지 않음.

- 관찰과 해석 구분: 가스 구성 비율과 분류 오류는 감지기·점수를 저장하고 해시로 잠근 뒤 정답과 기존 예측을 결합해 계산함. 정답으로 감지기·임계값을 수정하지 않았음. Window의 실제 클래스 수를 공개하고 창 Macro F1을6종 전체 성능처럼 해석하지 않음.

- 연관성 한계: 경고·비경고 오류율은 가스 구성·Batch·측정 조건의 교란이 있음. Spearman은 설명용이며 독립 관측의 유의성이나 향후 오류 예측력을 주장하지 않음. Batch가2개뿐이므로 Batch 평균2점의 상관계수는 산출하지 않음.

- 운영 해석: 경고는 기준 가스 측정·모델 재검증의 검토 신호임. 경고가 없어도 분류 정확도를 보장하지 않으며, 경고가 있어도 센서 고장·노후화·분류 실패를 확정하지 않음.

- 메타데이터 한계: 현재 .dat에는 정답과128개 특징만 있음. Batch와 source_line은 파일에서 파생한 정보이며 정확한 측정 시각·농도·환경·개별 측정 센서 식별 정보가 없음. 고정 특징 묶음의 센서 번호는 행별 장치 식별자나 물리적 원인 증거가 아님.

- 구현 범위: CSV 서비스는128개 특징 이름을 확인하고 순서만 다르면 재정렬함. 추가 열·중복 열·비수치·무한대·전체 결측은 평가 불가. 일부 결측만 Reference 중앙값으로 처리. 실제 Streamlit은 설치·실행하지 않았고, 선택형 화면 어댑터와 백엔드 CSV 경계를 제공함.

- 웹앱 실행: Streamlit을 별도 설치한 환경에서 프로젝트 루트의 python -m streamlit run src/drift_detection/streamlit_app.py 사용. 실제 배포 검증·경고의 업무 적합성 검증은 다음 단계임.

- 재실행: python -B -m src.drift_detection.experiment freeze → run → 전체pytest → report. freeze/run은 기존 경로 또는 실행 흔적이 있으면 거부하며 추가 실험 없이 report만 갱신 가능.

- 다음 검증: 새 시기의 라벨 없는 입력으로 고정 감지기를 적용하고 별도 기준 가스·환경·정답 자료를 독립 수집해 경고 해석과 운영 비용 검토. 가스 구성 통제 조건과 무통제 조건을 구분하고, 향후 임계값 버전 변경 시 새 독립 자료로 검증 필요.

- 계산값: calibration: 14창, 평균0.00447738, 중앙값0.00406737, 최대0.00831366, 경고1창(7.14%), 잔여83행 제외.

- 계산값: internal: 14창, 평균0.00314313, 중앙값0.00259291, 최대0.00834615, 경고1창(7.14%), 잔여84행 제외.

- 계산값: batch7: 36창, 평균0.100152, 중앙값0.0840692, 최대0.256697, 경고36창(100.00%), 잔여13행 제외.

- 계산값: batch8: 2창, 평균0.228156, 중앙값0.228156, 최대0.305474, 경고2창(100.00%), 잔여94행 제외.

- 사후 계산값: 경고 38창 3800행 중 오류391개(10.29%). 경고가 오류를 일으켰거나 오류를 예측한다고 해석하지 않음.

## 상세 요약

```text
             input_rows  windows  valid_windows  invalid_windows  excluded_tail_rows  mean_score  median_score  max_score  alert_windows  alert_rate  threshold
partition                                                                                                                                                      
calibration        1483       14             14                0                  83    0.004477      0.004067   0.008314              1    0.071429   0.008257
internal           1484       14             14                0                  84    0.003143      0.002593   0.008346              1    0.071429   0.008257
batch7             3613       36             36                0                  13    0.100152      0.084069   0.256697             36    1.000000   0.008257
batch8              294        2              2                0                  94    0.228156      0.228156   0.305474              2    1.000000   0.008257
```

## 사후 분류 오류 비교

```text
     scope  alert  windows  rows  errors  error_rate
pooled_7_8   True       38  3800     391    0.102895
    batch7   True       36  3600     378    0.105000
    batch8   True        2   200      13    0.065000
```

## 전체 테스트

```json
{
  "total": 219,
  "passed": 214,
  "failed": 5,
  "historical_failures": 5,
  "new_failures": 0,
  "new_tests": 20,
  "new_passed": 20,
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
      "reason": "AssertionError: assert {'models\\\\A_r....joblib', ...} == {'models\\\\A_r....joblib', ...}\n  \n  Extra items in the right set:\n  'models\\\\temporal_representativeness_control\\\\C_early_mid_seed11.joblib'\n  'models\\\\temporal_calibration\\\\B_seed23_cal05.joblib'\n  'models\\\\temporal_robustness\\\\candidate_SVM_variance.joblib'\n  'models\\\\temporal_calibration\\\\C_seed23_cal10.joblib'\n  'models\\\\temporal_robustness\\\\A\\\\rank_svm2.joblib'...\n  \n  ...Full output truncated (278 lines hidden), use '-vv' to show"
    },
    {
      "classname": "tests.test_temporal_generalization_validation",
      "name": "test_existing_files_raw_and_model_inventory_preserved",
      "historical": true,
      "reason": "AssertionError: assert {'models\\\\A_r....joblib', ...} == {'models\\\\A_r....joblib', ...}\n  \n  Extra items in the left set:\n  'models\\\\temporal_representativeness_control\\\\C_early_mid_seed11.joblib'\n  'models\\\\temporal_calibration\\\\B_seed23_cal05.joblib'\n  'models\\\\gas_specific_temporal_balancing\\\\C_mixed_mid_seed101.joblib'\n  'models\\\\temporal_representativeness_control\\\\A_spread_mid_seed11.joblib'\n  'models\\\\temporal_calibration\\\\C_seed23_cal10.joblib'...\n  \n  ...Full output truncated (181 lines hidden), use '-vv' to show"
    },
    {
      "classname": "tests.test_toluene_deep_diagnostic",
      "name": "test_preserved_files_raw_models_and_config",
      "historical": true,
      "reason": "AssertionError: assert ({'models\\\\A_r....joblib', ...} == {'models\\\\A_r....joblib', ...}\n  \n  Extra items in the right set:\n  'models\\\\temporal_representativeness_control\\\\C_early_mid_seed11.joblib'\n  'models\\\\temporal_calibration\\\\B_seed23_cal05.joblib'\n  'models\\\\gas_specific_temporal_balancing\\\\C_mixed_mid_seed101.joblib'\n  'models\\\\temporal_representativeness_control\\\\A_spread_mid_seed11.joblib'\n  'models\\\\temporal_calibration\\\\C_seed23_cal10.joblib'...\n  \n  ...Full output truncated (181 lines hidden), use '-vv' to show)"
    }
  ]
}
```


## 경고 해석에서 특히 주의할 결과

- 관찰: Batch7·8의38개 평가 창이 모두 경고됨. 따라서 대상 자료 안에서 경고와 비경고의 오류율을 비교할 비경고 집합은 없음. 비경고 오류율을0으로 채우거나 감지 민감도·특이도·정확도·ROC-AUC를 계산하지 않음.

- 관찰: 참조 분포 내부 평가 경고율은1/14=7.14%임. 이는 무작위 pooled 기준 분포 내부의 관찰값이며 실제 정상 센서 오경고율이나5% 보장이 아님.

- 관찰: Calibration·내부 평가의 모든100행 창에는6종이 존재함. 반면 Batch7은 36개 창 중30개가2종,2개가3종,4개가4종임. Batch8은2개 창에 각각2종·3종이 존재함. 전체 Batch의6종 비율만으로 창별 구성 차이를 설명하기 어려움.

- 해석: pooled 참조와 파일 순서 창의 가스 구성 차이는 경고에 영향을 줄 수 있음. 각 창의 total variation과 점수 사이 단순 상관이 작더라도 구성 영향이 없다고 결론 내릴 수 없음. 가스별 거리·농도·반응 변화와 비선형 상호작용을 분리하지 못함.

- 반례: Batch8 창1은 점수0.305474로 임계값을 크게 초과하지만100개 모두 정분류됨. Batch7 창8은 더 낮은 점수0.057273에서도29개가 오분류됨. 이 경우도 임계값은 초과했으므로 비경고 실패 사례로 잘못 표현하지 않음.

- 관찰·해석 구분:38개 창의 점수와 오류율의 Spearman은 약-0.292이며 설명용임. 점수가 클수록 오류가 증가한다는 근거를 보이지 않았고, 음의 인과 효과나 미래 오류 예측력을 뜻하지 않음. 창의 가스 구성·Batch 영향이 남음.

- 기술 결론 A의 범위: 라벨 없는 점수·고정 경고·저장 재현·입력 처리·분리 검사를 갖춘 백엔드 프로토타입 구축임. 모든 대상 창 경고로 인해 선택적인 운영 경보의 효용은 확인되지 않음. 물리적 드리프트 탐지 정확도나 실제 배포 신뢰성 인증 아님.

- 다음 단계 제안: 감지 규칙을 현재 결과에 맞춰 바꾸지 말고, 가스 구성과 측정 조건을 통제한 별도 기준 자료 및 새 시기 자료를 수집해 검증. Streamlit 어댑터의 실제 실행·배포와 사용자 경고 이해도 검증도 별도 필요함.
