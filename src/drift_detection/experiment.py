# 고정 계획에 따른 비지도 감지 실행 및 사후 분류 오류 비교
# 기존 자료 보존과 라벨 없는 적합 경계 검사

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from ..data import ROOT, FEATURES, GASES, parse_line, read_config
from ..nonlinear_feature_transformation import score_predictions
from ..temporal_expansion import sha

OUT = ROOT / "outputs/drift_detection"
MODEL_DIR = ROOT / "models/drift_detection"
OFFICIAL = ROOT / "models/temporal_expansion/B_SVM_balanced.joblib"
CAUTION = ("분포 변화 ≠ 센서 고장 ≠ 모델 성능 저하. 반복 사용한 개발 자료의 사후 진단이며 "
           "독립 Test가 아님. 실제 센서 드리프트 탐지 정확도를 측정하지 않음. "
           "Batch9~10 신규 점수·평가 없음. 공식 Model A 유지.")


# UTF-8 결과 저장
def write(name, value):
    def convert(item):
        if isinstance(item, np.generic):
            return item.item()
        if isinstance(item, np.ndarray):
            return item.tolist()
        raise TypeError(type(item).__name__)
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2,
                                      allow_nan=False, default=convert), encoding="utf-8")


def save(name, rows):
    table = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    table.to_csv(OUT / f"{name}.csv", index=False, encoding="utf-8")
    return table


# 기존 파일 지문 수집


# 분석 전 계획 저장 및 기존 자료 지문 고정


# Batch1~8만 읽고 감지 경로에서 정답 열 제외
def load_features():
    directory = Path(read_config()["data_dir"])
    rows = []
    for batch in range(1, 9):
        for line_n, line in enumerate((directory / f"batch{batch}.dat").read_text(encoding="utf-8").splitlines(), 1):
            _, values = parse_line(line)
            rows.append([f"b{batch:02d}_r{line_n:05d}", batch, line_n, *values])
    return pd.DataFrame(rows, columns=["row_id", "batch", "source_line", *FEATURES])


# 고정 난수로 라벨 없이 세 기준 집합 분리
def split_reference(frame):
    base = frame[frame.batch <= 6]
    ids = np.random.default_rng(42).permutation(base.index)
    n_ref = len(ids) // 2
    n_cal = (len(ids) - n_ref) // 2
    return {"reference": ids[:n_ref], "calibration": ids[n_ref:n_ref + n_cal],
            "internal": ids[n_ref + n_cal:]}


# 기존 지문·계획·분할 고정 상태 확인


# 창과 원본 행의 연결 기록
def memberships(part, subset, window_size=100):
    rows = []
    for pos, row in enumerate(subset.itertuples(), 1):
        rows.append(dict(partition=part, row_id=row.row_id, batch=int(row.batch),
                         source_line=int(row.source_line), pool_position=pos,
                         window=(pos - 1) // window_size + 1 if pos <= len(subset) // 100 * 100 else 0))
    return rows


# 연속 경고 창 구간 수집
def alert_runs(windows):
    runs, start, end = [], None, None
    for row in windows:
        if row["alert"] is True:
            start = row["window"] if start is None else start
            end = row["window"]
        elif start is not None:
            runs.append(dict(start_window=start, end_window=end, windows=end - start + 1))
            start = None
    if start is not None:
        runs.append(dict(start_window=start, end_window=end, windows=end - start + 1))
    return runs


# 감지 결과를 고정한 후에만 정답과 기존 예측 결합
def posthoc(frame, assignments, windows):
    assert (OUT / "detection_lock.json").exists()
    directory = Path(read_config()["data_dir"])
    labels = {}
    for batch in range(1, 9):
        for line_n, line in enumerate((directory / f"batch{batch}.dat").read_text(encoding="utf-8").splitlines(), 1):
            label, _ = parse_line(line)
            labels[f"b{batch:02d}_r{line_n:05d}"] = label
    data = frame.assign(gas=frame.row_id.map(labels))
    counts = pd.crosstab(data.batch, data.gas).reindex(columns=list(GASES), fill_value=0)
    save("batch_class_counts", counts.rename_axis(columns="gas_id").stack().rename("n").reset_index())
    raw_audit = []
    for batch, sub in data.groupby("batch"):
        raw_audit.append(dict(batch=batch, n=len(sub), missing=int(sub[FEATURES].isna().sum().sum()),
                              infinite=int(np.isinf(sub[FEATURES]).sum().sum()),
                              constant_features=int((sub[FEATURES].nunique() <= 1).sum()),
                              gas_label_runs=int(1 + np.count_nonzero(np.diff(sub.gas))),
                              exact_measurement_times=False, concentration=False,
                              environment_metadata=False, sensor_identity_per_row=False))
    save("input_audit", raw_audit)
    reference_ids = assignments[assignments.partition == "reference"].row_id
    reference_gases = data.set_index("row_id").loc[reference_ids, "gas"]
    ref_proportions = reference_gases.value_counts(normalize=True).reindex(GASES, fill_value=0)
    stored = pd.read_csv(ROOT / "outputs/temporal_expansion/predictions.csv.gz")
    pred = stored[(stored.trial_id == "B_SVM_balanced") & stored.batch.isin([7, 8])].copy()
    assert pred.row_id.is_unique
    indexed = data.set_index("row_id")
    np.testing.assert_array_equal(pred.y_true, indexed.loc[pred.row_id, "gas"])
    replay = pd.read_csv(ROOT / "outputs/temporal_failure_diagnostics/row_predictions.csv").set_index("row_id")
    np.testing.assert_array_equal(pred.y_pred, replay.loc[pred.row_id, "SVM"])
    assert set(pred.row_id) == set(data[data.batch.isin([7, 8])].row_id)
    save("prediction_reuse", [dict(model="B_SVM_balanced", rows=len(pred), exact_stage7_replay=True,
                                   fresh_predictions=0, model_sha256=sha(OFFICIAL))])
    pred = pred.set_index("row_id")
    composition, window_metrics, gas_support, gas_metrics, batch_metrics = [], [], [], [], []
    for part in ["reference", "calibration", "internal", "batch7", "batch8"]:
        ids = assignments[assignments.partition == part].row_id
        sub = indexed.loc[ids]
        for gas in GASES:
            composition.append(dict(partition=part, gas_id=gas, gas=GASES[gas],
                                    n=int((sub.gas == gas).sum()), proportion=float((sub.gas == gas).mean())))
    for row in windows.itertuples():
        ids = assignments[(assignments.partition == row.partition) & (assignments.window == row.window)].row_id
        sub = indexed.loc[ids]
        proportions = sub.gas.value_counts(normalize=True).reindex(GASES, fill_value=0)
        tv = float(np.abs(proportions - ref_proportions).sum() / 2)
        for gas in GASES:
            gas_support.append(dict(partition=row.partition, window=row.window, gas_id=gas,
                                    n=int((sub.gas == gas).sum())))
        if row.partition not in ["batch7", "batch8"]:
            continue
        yp = pred.loc[ids, "y_pred"]
        errors = np.asarray(yp) != sub.gas.to_numpy()
        window_metrics.append(dict(partition=row.partition, window=row.window, score=row.score,
                                   alert=bool(row.alert), n=len(sub), error_n=int(errors.sum()),
                                   error_rate=float(errors.mean()), gas_classes=int(sub.gas.nunique()),
                                   dominant_gas_fraction=float(proportions.max()),
                                   mixture_total_variation=tv))
    for batch in [7, 8]:
        sub = data[data.batch == batch]
        score, per_gas, _ = score_predictions(sub.gas, pred.loc[sub.row_id, "y_pred"])
        batch_metrics.append(dict(batch=batch, **score, includes_tail=True))
        gas_metrics.extend(per_gas.assign(batch=batch).to_dict("records"))
    wm = save("window_error_analysis", window_metrics)
    save("batch_classifier_metrics", batch_metrics)
    save("class_classifier_metrics", gas_metrics)
    save("gas_composition", composition)
    save("window_gas_support", gas_support)
    comparison = []
    for scope, sub in [("pooled_7_8", wm), ("batch7", wm[wm.partition == "batch7"]),
                       ("batch8", wm[wm.partition == "batch8"])]:
        for alert, group in sub.groupby("alert"):
            comparison.append(dict(scope=scope, alert=bool(alert), windows=len(group),
                                   rows=int(group.n.sum()), errors=int(group.error_n.sum()),
                                   error_rate=float(group.error_n.sum() / group.n.sum())))
    save("warning_error_comparison", comparison)
    associations = []
    for name, sub in [("pooled_7_8", wm), ("batch7", wm[wm.partition == "batch7"]),
                      ("batch8", wm[wm.partition == "batch8"])]:
        for other in ["error_rate", "mixture_total_variation"]:
            available = len(sub) >= 3 and sub.score.nunique() > 1 and sub[other].nunique() > 1
            coefficient = float(spearmanr(sub.score, sub[other]).statistic) if available else None
            associations.append(dict(scope=name, variables=f"score vs {other}", windows=len(sub),
                                     spearman=coefficient, inference=False,
                                     note="descriptive only" if available else "too few/constant windows"))
    save("associations", associations)


# 고정 감지기 한 번 적합·평가 및 저장


# 기존 실패와 신규 실패 구분




