# 14단계 실행 전 고정 계획

새 독립 Test 없음. 과거 Fold는 반복 사용된 개발 자료이며 서로 독립적인 반복 표본이 아님. Batch 9~10 신규 평가 없음. 공식 Model A 유지.

정확한 공식·보호 기준·결측 클래스·경계값·재사용·중단 규칙은 아래 JSON과 동일함.

```json
{
  "stage": 14,
  "frozen_at": "2026-10-27T15:14:13.376853+09:00",
  "folds": {
    "A": [
      3,
      6
    ],
    "B": [
      6,
      7
    ],
    "C": [
      7,
      8
    ]
  },
  "methods": [
    "baseline",
    "signed_log",
    "yeo_johnson"
  ],
  "maximum_pipeline_evaluations": 9,
  "maximum_new_classifier_fits": 9,
  "train_policy": "All rows; same ordered 128 features and rows for every condition",
  "signed_log": "sign(x)*log1p(abs(x)/s); s=max(median(abs(imputed Train)), 1e-12, 1e-12*max(abs(imputed Train))) per feature",
  "yeo_johnson": "PowerTransformer(yeo-johnson, standardize=False) per column; constant column identity; numerical Train failure identity with reason; any Validation transform failure invalidates candidate; no refit/replacement",
  "fit_boundary": "Only each Fold Train; metadata contains input and ordered-row hashes",
  "svm": {
    "C": 1.0,
    "gamma": "scale",
    "kernel": "rbf",
    "class_weight": "balanced",
    "probability": false,
    "random_state": 42
  },
  "metrics": "Accuracy, equal-present-class macro F1, weighted F1; six-class P/R/F1/support; confusion, prediction fractions, directional errors, min recall, zero count",
  "aggregation": "Equal Fold mean macro F1; per-gas means over positive-support Folds only; other-four F1 = equal gas means for ids1,2,3,5; missing truth metrics NaN (not zero); zero precision for supported but never-predicted class",
  "guards": {
    "macro_gain_min": 0.005,
    "per_gas_mean_recall_loss_max": 0.05,
    "other_four_mean_f1_loss_max": 0.02,
    "zero_pair_increase_max": 0,
    "no_new_zero_when_baseline_positive": true,
    "inclusive": true,
    "tolerance": 1e-12
  },
  "conclusion": "A iff all guards and 3 complete Folds; B iff any positive macro or gas P/R/F1 change but not all guards; C otherwise; no auto ModelA replacement",
  "tie": "Among all-guard candidates: higher mean macro F1; within1e-12 use fewer zeros, higher minimum recall, then signed_log before yeo_johnson",
  "uncertainty": "새 독립 Test 없음. 과거 Fold는 반복 사용된 개발 자료이며 서로 독립적인 반복 표본이 아님. Batch 9~10 신규 평가 없음. 공식 Model A 유지.",
  "future_evaluation": false,
  "stop": "No additional candidates, tuning, feature selection or ensembles. Technical failure invalidates condition, no replacement. Leakage/preservation failure aborts run.",
  "reuse": "Stage8 SVM_all only after file hash, ordered rows, all-feature identity selector, imputer, scaler, SVM params and feature shape checks; unwrap identity only; reference predictions must match stored Stage8 validation predictions",
  "distribution_features": "Train1-3 only: top3 absolute standardized third moments, stable original feature order for ties; no validation ranking",
  "split_sha256": "c5a44aa0023127f5fdcdd6deb3cb3a7c36cdfee1f437adcef1e7676686067942",
  "versions": {
    "numpy": "2.5.4",
    "pandas": "2.3.3",
    "scikit-learn": "1.9.1",
    "scipy": "1.18.1",
    "joblib": "1.6.0",
    "matplotlib": "3.11.2"
  }
}
```
