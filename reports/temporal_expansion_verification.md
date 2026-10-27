# 6단계 실험 해석 및 최종 보존 검증

전체 테스트: 49개 통과, 2개 실패. 신규 8개 모두 통과.

기존 실패: 과거 소스의 주석·공백 변경에 따른 SHA 불일치, 과거 보존 기록에 포함된 zNex~$haremetrics.csv 부재. 기존 검사와 해시 기록은 수정하지 않았음.

```text
tests.test_diagnostics::test_existing_results_and_models_unchanged
tests.test_models::test_eda_and_sources_preserved_report_complete
```

실험 시작 시 존재한 코드·테스트·보고서·모델·산출물 241개와 원본 10개 해시 보존 확인. 기존 소스가 이번에 변경되지 않았으므로 이번 작업에서 AST 변경도 없음.

## 학습 범위 확장 효과

- LR / validation: Batch 동일 가중 Macro F1 변화 +25.02pp, pooled 변화 +25.46pp. Toluene Recall 0.00%→91.64%, Acetaldehyde Recall 10.04%→31.92%.
- LR / evaluation: Batch 동일 가중 Macro F1 변화 -0.49pp, pooled 변화 +4.02pp. Toluene Recall 0.00%→49.36%, Acetaldehyde Recall 0.89%→0.00%.
- RF / validation: Batch 동일 가중 Macro F1 변화 +28.92pp, pooled 변화 +20.35pp. Toluene Recall 0.00%→57.85%, Acetaldehyde Recall 43.89%→19.18%.
- RF / evaluation: Batch 동일 가중 Macro F1 변화 +7.22pp, pooled 변화 +7.22pp. Toluene Recall 0.00%→16.98%, Acetaldehyde Recall 18.81%→8.89%.
- SVM / validation: Batch 동일 가중 Macro F1 변화 +26.72pp, pooled 변화 +22.31pp. Toluene Recall 0.00%→85.15%, Acetaldehyde Recall 77.61%→49.03%.
- SVM / evaluation: Batch 동일 가중 Macro F1 변화 -0.01pp, pooled 변화 +6.71pp. Toluene Recall 0.00%→43.94%, Acetaldehyde Recall 25.33%→6.81%.

Validation에서는 세 모델 모두 확장 효과가 컸으나, 탐색적 평가의 동일 가중 지표는 RF만 개선되고 LR은 소폭 하락, SVM은 거의 동일함. pooled 지표는 세 모델 모두 개선됨. 평균 방식에 따라 결론이 달라지므로 시간순 확장이 모든 미래 Batch에 효과적이라고 일반화할 수 없음. 기본 모델의 평가 Acetaldehyde Recall은 세 모델 모두 하락함.

## 선정 후보와 남은 실패

Validation 우선 후보: **B_SVM_balanced**.

```text
      trial_id  partition  equal_batch_macro_f1  batch_sd_macro_f1  min_batch_macro_f1  max_batch_macro_f1  pooled_macro_f1  accuracy  weighted_f1  toluene_recall  toluene_f1  acetaldehyde_recall  acetaldehyde_f1  min_class_recall  other_four_f1
B_LR_tune_C0p1 evaluation              0.577751           0.014457            0.563293            0.592208         0.595821  0.642506     0.596508        0.597718    0.625373             0.017778         0.034934          0.017778       0.728655
B_LR_tune_C0p1 validation              0.806230           0.043832            0.762398            0.850062         0.846918  0.860763     0.844690        0.970990    0.981034             0.387387         0.557407          0.387387       0.885767
 B_RF_balanced evaluation              0.456727           0.059979            0.396748            0.516706         0.408314  0.442998     0.408016        0.176890    0.291765             0.075556         0.122156          0.075556       0.508991
 B_RF_balanced validation              0.651699           0.080190            0.571509            0.731890         0.726083  0.758126     0.713816        0.687713    0.705779             0.177606         0.298056          0.177606       0.838165
B_SVM_balanced evaluation              0.602705           0.068142            0.534563            0.670848         0.558657  0.570270     0.559136        0.462197    0.460227             0.186667         0.304716          0.186667       0.646750
B_SVM_balanced validation              0.897000           0.000058            0.896942            0.897057         0.897070  0.896852     0.892000        0.890785    0.886248             0.629344         0.771902          0.629344       0.931067
```

우선 후보의 탐색적 평가 Toluene Recall 0% Batch: [9]. 합산 Recall 개선만으로 미래 Batch 전체의 실패가 해결됐다고 해석할 수 없음.

탐색적 평가의 동일 가중 점수는 SVM 대표가 높지만 pooled Macro F1은 LR 대표가 높음. 이는 평균 기준과 클래스 균형의 차이임. 평가를 보고 후보를 바꾸지 않았음.

## 재현과 실행

- 학습·선정·평가: `.venv\Scripts\python.exe -B -X utf8 -m src.temporal_expansion`
- 검증 문서: `.venv\Scripts\python.exe -B -X utf8 -m src.temporal_expansion_review`
- 전체 테스트: `.venv\Scripts\python.exe -B -X utf8 -m pytest -q -p no:cacheprovider`

학습 코드는 기존 신규 실험 경로가 있으면 중단함. 재현은 1–5단계 파일을 보존한 별도 복제본에서 6단계 출력 경로가 없는 상태로 실행해야 함. 기존 산출물 삭제·덮어쓰기 금지.

모델·전처리·후보는 평가 전에 고정됐으며 재학습이나 평가 기반 변경 없음. 새 측정 시기의 미관찰 자료로 독립 검증 필요. 최종 모델 확정 아님. Commit·Push 없음.
