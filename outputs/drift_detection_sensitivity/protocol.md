# 18.5단계 사전 고정 계획

고정 감지기의 사후 민감도 진단이며 실제 센서 드리프트 탐지 정확도 검증 아님. 라벨 기반 구성 통제는 운영용 무라벨 평가가 아님. 반복 개발 자료이며 독립 Test 없음. Batch9~10 원본 읽기·평가 없음. 모델·임계값 변경 없음.

```json
{
  "stage": "18.5",
  "frozen_at": "2026-10-27T17:32:15.521434+09:00",
  "seeds": [
    42,
    43,
    44,
    45,
    46
  ],
  "window_size": 100,
  "detector_sha256": "de47661f66c69cdc7553f73acf1df9b721f65771d0301fe69a7a326f814fa4c5",
  "official_sha256": "1d6b20c94d1580d799e05ab5a9ce746bdb272d74f70ec2ff964011fffecfde32",
  "threshold": 0.00825701197565701,
  "data": "Read raw Batch1..8 only. Reference/Calibration/internal IDs reused from stage18. Reference used only to describe proportions; Calibration never rescored or refitted. No raw9/10 read including hash checks and full tests.",
  "experiment_A": "Reuse all38 saved stage18 target windows, gas support and classifier error. TV=0.5*sum(abs(window gas proportion - saved Reference proportion)). Spearman pooled and per Batch for score vs TV/classes/error; >=3 nonconstant observations only; descriptive, no p-values or causal claims.",
  "experiment_B1": "Original per-Batch source-line order. Replay against old scores before comparisons.",
  "experiment_B2": "For each Batch7/8 independently, default_rng(SeedSequence([seed,batch])).permutation(N). All rows shuffled, full100 windows used, remainder excluded. Same5 seeds, no selection.",
  "paired_row_check": "Additional diagnostic: permute only original first floor(N/100)*100 evaluated rows with same SeedSequence, append unchanged original tail. Isolates grouping changes from excluded-row membership. Not a fourth detector configuration.",
  "experiment_B3": "Label-based diagnostic only. Hamilton integer quota100 from saved Reference gas proportions, tie lower gas ID, all6 quotas>=1 else unavailable. For each target7/8 and saved INTERNAL evaluation pool, capacity K_s=min_g floor(n_sg/quota_g). Use common K=min(K_internal,K_target); if K<1 unavailable. Per gas default_rng(SeedSequence([seed,target,source_code,gas])) with source0=internal, source_code=target Batch otherwise. Pick K*quota without replacement, consecutive quota slices per window; no duplicate rows within source/seed/comparison. No Reference/Calibration rows in controlled null, no cross-target-Batch mixture.",
  "controlled_limits": "Unequal source capacities disclosed; equal selected K within target/internal pair. Rows can recur across seeds and controlled comparisons. Batch8 likely1 matched window; no independent repeats, no mechanistic causal isolation.",
  "mean_decomposition": "For each equal100-row window set: mean(score)=||overall RFF mean-ref||² + mean(||window mean-overall mean||²). Global term diagnostic only, no threshold applied to global mean. Fixed-row shuffle must keep global term unchanged.",
  "label_boundary": "True labels used only for A interpretation and B3 row selection. Frozen detector evaluate/score receives exactly f001..f128; no fit/calibrate/threshold changes.",
  "metrics": "All window scores/alerts/proportions/IDs, mean median min max MMD, alert count/rate, excluded rows, paired membership checks, descriptive seed SD/ddof1 and range; no favorable seed.",
  "inference": "Window partition, mixture proportions and retained sample content may change together. All-row shuffle not pure ordering contrast; fixed-row check separates tail membership. Controlled sampling changes content too; residual shift not proof of physical drift.",
  "tests": "Full existing+new tests with audit-hook block on raw9/10 and writes to past project files. Restricted tests skipped and logged; no old test/hash edits. Do not call skipped checks passed.",
  "preservation": "Hash all existing project artifacts and raw1..8 only; no9/10 hash reread. Verify existing model inventory unchanged (no new joblib).",
  "conclusion": "C on replay/partition/preservation/threshold violation. A if A/B1/B2/paired/B3 quantified for both targets with >=1 unique controlled window, all seeds recorded, new tests pass and limits disclosed. B if one diagnostic unavailable or insufficient. A quantifies sensitivity, not drift detection accuracy or causal separation.",
  "stop": "No parameter/seed/quota/window/threshold retry based on outcomes; stop on integrity failure. No classifier fits, detector fits, new artifacts under models, Streamlit integration or Git mutations.",
  "limitations": "고정 감지기의 사후 민감도 진단이며 실제 센서 드리프트 탐지 정확도 검증 아님. 라벨 기반 구성 통제는 운영용 무라벨 평가가 아님. 반복 개발 자료이며 독립 Test 없음. Batch9~10 원본 읽기·평가 없음. 모델·임계값 변경 없음."
}
```
