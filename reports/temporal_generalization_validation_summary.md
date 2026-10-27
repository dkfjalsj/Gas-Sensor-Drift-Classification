# 10단계 시간순 일반화 검증 요약

**새 독립 Test 없음. 독립 최종 성능을 측정하지 않았음. 공식 주 후보 Model A 유지.**

신규 모델 학습·전처리 Fit·튜닝·가중치·특징·임계값 변경0회. 저장된 A/B만 비교.

## A/B 관찰 결과

```text
model  train_end  equal_batch9_10_macro_f1  batch9_10_sd  batch8_10_sd  pooled_macro_f1  toluene_recall  acetaldehyde_recall  pooled_min_class_recall  worst_batch_class_recall  other_four_f1
    A          6                  0.602705      0.068142      0.149498         0.558657        0.462197             0.186667                 0.186667                  0.000000       0.646750
    B          7                  0.700451      0.037361      0.087506         0.677537        0.677603             0.605926                 0.392330                  0.009901       0.720978
```

```text
model       scope    n  accuracy  macro_precision  macro_recall  macro_f1  weighted_f1  macro_precision_fixed6  macro_recall_fixed6  macro_f1_fixed6  missing_classes  toluene_recall  toluene_f1  toluene_support  acetaldehyde_recall  acetaldehyde_f1  acetaldehyde_support  min_class_recall  other_four_f1
    A           8  294  0.921769         0.913551      0.891256  0.897057     0.920407                0.913551             0.891256         0.897057              NaN        0.777778    0.800000               18             0.939394         0.953846                    33          0.725000       0.907124
    A           9  470  0.702128         0.668721      0.747179  0.670848     0.640441                0.668721             0.747179         0.670848              NaN        0.000000    0.000000              101             0.560000         0.717949                    75          0.000000       0.826784
    A          10 3600  0.553056         0.667553      0.553056  0.534563     0.534563                0.667553             0.553056         0.534563              NaN        0.540000    0.495792              600             0.140000         0.236620                   600          0.140000       0.618742
    A pooled_9_10 4070  0.570270         0.674268      0.572290  0.558657     0.559136                0.674268             0.572290         0.558657              NaN        0.462197    0.460227              701             0.186667         0.304716                   675          0.186667       0.646750
    B           8  294  0.897959         0.886702      0.876408  0.874435     0.896466                0.886702             0.876408         0.874435              NaN        0.833333    0.750000               18             0.939394         0.911765                    33          0.675000       0.896212
    B           9  470  0.755319         0.766999      0.798677  0.737812     0.695507                0.766999             0.798677         0.737812              NaN        0.009901    0.019231              101             0.986667         0.594378                    75          0.009901       0.953315
    B          10 3600  0.664444         0.717574      0.664444  0.663090     0.663090                0.717574             0.664444         0.663090              NaN        0.790000    0.667136              600             0.558333         0.550987                   600          0.328333       0.690104
    B pooled_9_10 4070  0.674939         0.723423      0.675138  0.677537     0.677859                0.723423             0.675138         0.677537              NaN        0.677603    0.622951              701             0.605926         0.558362                   675          0.392330       0.720978
```

- 확장 학습이 평균 Macro F1을 높였는가? 관찰9–10 동일 가중 평균 +9.77pp. 개발Batch8은 -2.26pp로 하락.
- 개선된 가스는? 합산 Toluene Recall46.22→67.76%, Acetaldehyde18.67→60.59%. 가스별 F1·Recall 표 참고.
- 여전히 실패하는 가스는? B의 Batch9 Toluene1/101(0.99%), Batch10 Acetone197/600(32.83%).
- 안정성 개선이 일관적인가? 아님. 관찰 변동은 줄었지만 Batch8 Macro F1·Ethanol 등 Recall 손실과 특정 가스 실패가 남음.
- 데이터 양 증가만의 효과인가? 아님. 시기·클래스 구성·농도 가능성·기본 클래스 가중치가 함께 달라짐.
- 독립 평가 없이 B를 최종 선정할 수 있는가? 불가. 현재 공식 주 후보 A 유지, B는 확장 비교 모델.
- 현장 적용 성능을 주장할 수 있는가? 불가. 새 시기·환경·농도·세션의 독립 검증과 운영 기준이 없음.

## 불확실성과 검사

Batch×실제 가스 내부의 paired2000회·seed42·백분위95% 조건부 구간. 시간·세션 의존성 미보정이므로 미래 일반화의 신뢰구간이 아님.

전체 89개 통과, 기존 3개 실패. 신규 12개 모두 통과. 신규 실패 0개.

## 주요 그래프

- outputs/temporal_generalization_validation/batch_macro_f1.png
- outputs/temporal_generalization_validation/class_recall_heatmap.png
- outputs/temporal_generalization_validation/confusion_model_A.png
- outputs/temporal_generalization_validation/confusion_model_B.png
- outputs/temporal_generalization_validation/focus_correct_errors.png
- outputs/temporal_generalization_validation/performance_changes.png
- outputs/temporal_generalization_validation/sensor_distribution_6.png
- outputs/temporal_generalization_validation/sensor_distribution_4.png

## 재현

```text
.venv\Scripts\python.exe -B -X utf8 -m src.temporal_generalization_validation
.venv\Scripts\python.exe -B -X utf8 -m pytest -q -p no:cacheprovider --junitxml=outputs/temporal_generalization_validation/test_results.xml
.venv\Scripts\python.exe -B -X utf8 -m src.temporal_generalization_validation --finalize
```

1–9단계 보존 복제본에서10단계 출력이 없는 상태로 실행. 기존 경로가 있으면 중단. 기존 결과 삭제·덮어쓰기 없음. Git Commit·Push 없음.
