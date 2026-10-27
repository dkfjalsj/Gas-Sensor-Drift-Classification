# 고정 계획에 따른 비지도 감지 실행 및 사후 분류 오류 비교
# 기존 자료 보존과 라벨 없는 적합 경계 검사

import argparse
import importlib.metadata
import json
import logging
from pathlib import Path
import xml.etree.ElementTree as ET

import joblib
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from ..data import ROOT, FEATURES, GASES, parse_line, read_config
from ..nonlinear_feature_transformation import score_predictions
from ..temporal_expansion import now, sha
from .detector import DriftDetector

OUT = ROOT / "outputs/drift_detection"
MODEL_DIR = ROOT / "models/drift_detection"
REPORT_NAMES = [f"drift_detection_{name}" for name in
                ["report.html", "summary.md", "limitations.md"]]
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
def snapshot():
    result = {}
    for folder in ["src", "tests", "outputs", "reports", "models"]:
        for path in (ROOT / folder).rglob("*"):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            if OUT in path.parents or MODEL_DIR in path.parents:
                continue
            if path.parent == ROOT / "reports" and path.name in REPORT_NAMES:
                continue
            result[str(path.relative_to(ROOT))] = sha(path)
    for name in ["README.md", "config.json", "training_config.json", ".gitignore",
                 "requirements.txt", "requirements-lock.txt"]:
        result[name] = sha(ROOT / name)
    return result


# 분석 전 계획 저장 및 기존 자료 지문 고정
def freeze():
    if OUT.exists() or MODEL_DIR.exists() or any((ROOT / "reports" / n).exists() for n in REPORT_NAMES):
        raise FileExistsError("18단계 경로가 이미 존재함")
    OUT.mkdir()
    plan = dict(
        stage=18, frozen_at=now(), reference_candidate_batches=[1, 2, 3, 4, 5, 6],
        target_batches=[7, 8], prohibited_scoring_batches=[9, 10], seed=42,
        algorithm="RBF Random Fourier Features MMD squared mean distance",
        n_components=512, window_size=100,
        split="Concatenate original Batch1..6 rows. default_rng(42).permutation(N), "
              "Reference first floor(N/2), Calibration next floor((N-ref)/2), "
              "internal evaluation remainder. No gas labels or gas stratification.",
        null_windows="Calibration/internal evaluation preserve their random permutation order; "
                     "nonoverlapping100-row pooled mixture windows. These are NOT chronological "
                     "or within-Batch normal windows. This null differs from target file-order windows.",
        target_windows="Separately per Batch, original file source-line order, nonoverlapping100; "
                       "discard and log tail<100. No cross-target-Batch windows; no wall-clock claim.",
        preprocessing="Median Imputer then StandardScaler fitted ONLY Reference Pool. "
                      "Same feature order/types as official Model A; distinct subset-fitted objects. "
                      "No all-reference refit after threshold. No target fit.",
        bandwidth="Impute/scale Reference only. default_rng(42).choice(n,min(n,1024),replace=False). "
                  "Upper-triangle squared Euclidean pair distances; omit<=1e-12. "
                  "sigma²=median positive squared distances; gamma=1/(2*sigma²). "
                  "No positive distance => stop; no fallback gamma.",
        threshold="At least10 full Calibration windows, percentile95 via np.quantile(method=linear). "
                  "Warn iff score>threshold; equality baseline. Same frozen Reference embedding at use.",
        missing="Reorder exact named f001..f128 schema; reject extra/duplicate/missing columns, "
                "nonnumeric/boolean/infinity/all-missing row or feature. Partial NaN median-imputed "
                "using Reference only; record counts. Window-local all-missing feature => unavailable.",
        labels="No labels in fit/calibrate/score/API or serialized detector. Read gas labels "
               "only after detector/score hashes are locked, for mixture and saved-SVM error analysis.",
        normal_warning="Separate14 expected pooled internal windows; descriptive reference-internal "
                       "warning rate, not true normal-sensor false positive rate or 5% guarantee.",
        metrics="n, full/invalid windows, dropped rows, mean/median/max MMD, alerts/rate, "
                "consecutive alert runs; posthoc errors/support/mixture total variation; "
                "Spearman(score,window_error) descriptive, no p/inference. No2-point Batch correlation.",
        classifier="Official Model A unchanged; zero new classifier fits/predictions. "
                   "Reuse stage6 B_SVM_balanced saved Batch7/8 predictions, verify stage7 replay and truth IDs.",
        stop="Leakage/duplicate overlap/preservation/plan mismatch, insufficient null windows or "
             "degenerate Reference => abort, no altered seed/window/bandwidth/threshold retry.",
        conclusion="A only if valid target scores, independent-row internal warning estimate, fixed "
                   "threshold, unlabeled API, replay, input handling and preservation tests pass. "
                   "A is technical prototype success, not physical drift detection accuracy. "
                   "B partial with noncritical missing evidence, C substantial leakage/replay failure.",
        ui="CSV service API and optional Streamlit adapter; live Streamlit not installed initially. "
           "Do not infer web deployment validation from backend tests.",
        limits=CAUTION + " Shared Reference induces score dependence; pooled historical data may "
               "already drift; file-order windows may concentrate gases. No event labels, exact "
               "timestamps, concentrations or environment attribution. Only2 Batch8 full windows.",
        official_sha256=sha(OFFICIAL), packages={name: importlib.metadata.version(name)
            for name in ["numpy", "scipy", "pandas", "scikit-learn", "joblib"]},
    )
    write("experiment_plan.json", plan)
    (OUT / "protocol.md").write_text("# 18단계 사전 고정 프로토콜\n\n" + CAUTION +
        "\n\n```json\n" + json.dumps(plan, ensure_ascii=False, indent=2) + "\n```\n", encoding="utf-8")
    write("plan_lock.json", dict(plan_sha256=sha(OUT / "experiment_plan.json"),
                                protocol_sha256=sha(OUT / "protocol.md")))
    raw_dir = Path(read_config()["data_dir"])
    write("preservation_before.json", dict(files=snapshot(), raw={
        f"batch{b}.dat": sha(raw_dir / f"batch{b}.dat") for b in range(1, 11)}))
    print("Stage18 protocol frozen before new feature analysis", flush=True)


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
def verify():
    before = json.loads((OUT / "preservation_before.json").read_text(encoding="utf-8"))
    raw_dir = Path(read_config()["data_dir"])
    checks = [dict(kind="existing", path=p, expected=s, actual=sha(ROOT / p))
              for p, s in before["files"].items()]
    checks += [dict(kind="raw", path=p, expected=s, actual=sha(raw_dir / p))
               for p, s in before["raw"].items()]
    table = save("preservation_audit", checks)
    assert table.expected.eq(table.actual).all()
    lock = json.loads((OUT / "plan_lock.json").read_text(encoding="utf-8"))
    assert lock["plan_sha256"] == sha(OUT / "experiment_plan.json")
    assert lock["protocol_sha256"] == sha(OUT / "protocol.md")
    if (OUT / "detection_lock.json").exists():
        locked = json.loads((OUT / "detection_lock.json").read_text(encoding="utf-8"))
        for path, value in locked["files"].items():
            assert sha(ROOT / path) == value
    return dict(all_preserved=True, raw_files=len(before["raw"]),
                existing_models=sum(p.endswith(".joblib") for p in before["files"]),
                existing_files=len(before["files"]), plan_unchanged=True,
                official_sha256=sha(OFFICIAL), evaluated_target_batches=[7, 8],
                scored_batches_9_10=[], new_classifier_fits=0)


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
def run():
    if (OUT / "started.json").exists():
        raise FileExistsError("이미 실행됨: 결과에 따른 재실행 금지")
    verify()
    write("started.json", dict(started_at=now()))
    logging.basicConfig(filename=OUT / "execution_log.txt", encoding="utf-8", level=logging.INFO)
    frame = load_features()
    parts = split_reference(frame)
    all_parts = {**parts, **{f"batch{b}": frame.index[frame.batch == b].to_numpy() for b in [7, 8]}}
    hashes = pd.util.hash_pandas_object(frame[FEATURES], index=False)
    overlaps = []
    for i, a in enumerate(all_parts):
        for b in list(all_parts)[i + 1:]:
            row_overlap = len(set(all_parts[a]) & set(all_parts[b]))
            feature_overlap = len(set(hashes.loc[all_parts[a]]) & set(hashes.loc[all_parts[b]]))
            overlaps.append(dict(left=a, right=b, row_overlap=row_overlap, exact_feature_overlap=feature_overlap))
            assert row_overlap == feature_overlap == 0
    save("overlap_checks", overlaps)
    detector = DriftDetector().fit_reference(frame.loc[parts["reference"], FEATURES])
    detector.calibrate(frame.loc[parts["calibration"], FEATURES])
    ref = frame.loc[parts["reference"], FEATURES]
    np.testing.assert_allclose(detector.imputer.statistics_, np.nanmedian(ref, axis=0))
    values = detector.imputer.transform(ref)
    np.testing.assert_allclose(detector.scaler.mean_, values.mean(axis=0))
    np.testing.assert_allclose(detector.scaler.var_, values.var(axis=0))
    assert detector.scaler.n_samples_seen_ == len(ref)
    MODEL_DIR.mkdir()
    path = MODEL_DIR / "rff_mmd_v1.joblib"
    joblib.dump(detector, path)
    reloaded = joblib.load(path)
    assignment_rows, scores, summaries, runs = [], [], [], []
    assignment_rows.extend(dict(partition="reference", row_id=r.row_id, batch=int(r.batch),
                                source_line=int(r.source_line), pool_position=i, window=0)
                           for i, r in enumerate(frame.loc[parts["reference"]].itertuples(), 1))
    inputs = {name: frame.loc[parts[name]] for name in ["calibration", "internal"]}
    inputs.update({f"batch{b}": frame[frame.batch == b] for b in [7, 8]})
    replay_checks = []
    for part, sub in inputs.items():
        result = detector.evaluate(sub[FEATURES])
        duplicate = reloaded.evaluate(sub[FEATURES])
        assert result == duplicate
        replay_checks.append(dict(partition=part, identical=True, windows=len(result["windows"])))
        assert result["valid_windows"] >= (10 if part in ["calibration", "internal"] else 1)
        assignment_rows.extend(memberships(part, sub))
        for item in result["windows"]:
            scores.append(dict(partition=part, **item))
        valid = [w["score"] for w in result["windows"] if w["score"] is not None]
        summaries.append(dict(partition=part, input_rows=len(sub), windows=len(result["windows"]),
                               valid_windows=result["valid_windows"], invalid_windows=result["invalid_windows"],
                               excluded_tail_rows=result["excluded_tail_rows"], mean_score=float(np.mean(valid)),
                               median_score=float(np.median(valid)), max_score=float(np.max(valid)),
                               alert_windows=result["alert_windows"], alert_rate=result["alert_rate"],
                               threshold=detector.threshold_))
        runs.extend(dict(partition=part, **r) for r in alert_runs(result["windows"]))
        logging.info("%s rows=%s windows=%s alerts=%s", part, len(sub), result["valid_windows"], result["alert_windows"])
    assignments = save("split_assignments", assignment_rows)
    windows = save("windows", scores)
    save("partition_summary", summaries)
    save("alert_runs", pd.DataFrame(runs, columns=["partition", "start_window", "end_window", "windows"]))
    save("reload_checks", replay_checks)
    write("detector_metadata.json", {**detector.metadata_, "artifact_sha256": sha(path),
                                    "plan_sha256": sha(OUT / "experiment_plan.json"),
                                    "feature_order": FEATURES, "reference_n": len(ref)})
    write("train_only_audit.json", dict(imputer_median_reference_only=True, scaler_reference_only=True,
        scaler_n=int(detector.scaler.n_samples_seen_), rff_reference_only=True, threshold_calibration_only=True,
        gas_labels_used=False, target_fit_rows=0, full_reference_refit=False,
        official_classifier_preprocessing_unchanged=True))
    # 감지기와 점수 저장 이후에만 정답 기반 진단 허용
    locked_paths = [path, OUT / "windows.csv", OUT / "partition_summary.csv", OUT / "split_assignments.csv",
                    OUT / "detector_metadata.json", OUT / "train_only_audit.json"]
    write("detection_lock.json", dict(locked_before_posthoc_at=now(), files={
        str(p.relative_to(ROOT)): sha(p) for p in locked_paths}))
    posthoc(frame, assignments, windows)
    write("final_verification.json", {**verify(), "completed_at": now(), "technical_conclusion": "pending tests"})
    from .report import render
    render()
    print(pd.DataFrame(summaries).to_string(index=False), flush=True)


# 기존 실패와 신규 실패 구분
def test_summary():
    path = OUT / "test_results.xml"
    if not path.exists():
        return dict(status="전체 테스트 실행 전")
    previous = ET.parse(ROOT / "outputs/temporal_calibration/test_results.xml")
    old = {(c.get("classname"), c.get("name")) for c in previous.iter("testcase")
           if c.find("failure") is not None or c.find("error") is not None}
    cases = list(ET.parse(path).iter("testcase"))
    failures = []
    for case in cases:
        error = case.find("failure")
        if error is None:
            error = case.find("error")
        if error is not None:
            key = (case.get("classname"), case.get("name"))
            failures.append(dict(classname=key[0], name=key[1], historical=key in old,
                                 reason=error.get("message", "")[:900]))
    new = [c for c in cases if "test_drift_detection" in c.get("classname", "")]
    result = dict(total=len(cases), passed=len(cases) - len(failures), failed=len(failures),
                  historical_failures=sum(f["historical"] for f in failures),
                  new_failures=sum(not f["historical"] for f in failures),
                  new_tests=len(new), new_passed=sum(c.find("failure") is None and c.find("error") is None for c in new),
                  failures=failures)
    write("test_summary.json", result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["freeze", "run", "report"])
    action = parser.parse_args().action
    if action == "freeze":
        freeze()
    elif action == "run":
        try:
            run()
        except Exception:
            logging.exception("고정 실행 중단: 설정 변경 재시도 없음")
            raise
    else:
        from .report import render
        render()
        tests = test_summary()
        write("final_verification.json", {**verify(), "tests": tests,
              "technical_conclusion": "A" if tests.get("new_failures") == 0 else "pending/B/C",
              "checked_at": now()})


if __name__ == "__main__":
    main()
