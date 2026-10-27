# 라벨 없는 감지 입력·고정 임계값·자료 분리·기존 파일 보존 검사
# 작은 가상 자료 검사와 실제 저장 결과 검증 분리

import io
import json

import joblib
import numpy as np
import pandas as pd
import pytest

from src.data import ROOT, FEATURES
from src.drift_detection.detector import DriftDetector, MESSAGES, evaluate_csv, validate_features
from src.drift_detection.experiment import OUT, load_features, split_reference, verify


@pytest.fixture(scope="module")
def synthetic():
    rng = np.random.default_rng(71)
    ref = pd.DataFrame(rng.normal(size=(300, 128)), columns=FEATURES)
    cal = pd.DataFrame(rng.normal(size=(1000, 128)), columns=FEATURES)
    detector = DriftDetector().fit_reference(ref)
    detector.calibrate(cal)
    return detector, ref, cal


# 순서만 다른 입력은 명시적 정렬
def test_exact_schema_and_reorder(synthetic):
    detector, _, cal = synthetic
    normal = detector.evaluate(cal)
    shuffled = detector.evaluate(cal[FEATURES[::-1]])
    assert normal["windows"] == shuffled["windows"]
    assert shuffled["schema_reordered"] is True
    assert detector.evaluate(cal.drop(columns=["f001"]))["status"] == "평가 불가"
    assert detector.evaluate(cal.assign(gas=1))["status"] == "평가 불가"


def test_duplicate_columns_and_bad_values(synthetic):
    detector, _, cal = synthetic
    duplicate = cal.copy()
    duplicate.columns = ["f002", *FEATURES[1:]]
    assert detector.evaluate(duplicate)["status"] == "평가 불가"
    for bad in [np.inf, -np.inf, "text"]:
        frame = cal.astype(object).copy()
        frame.iloc[0, 0] = bad
        assert detector.evaluate(frame)["status"] == "평가 불가"
    assert detector.evaluate(None)["status"] == "평가 불가"


def test_partial_missing_uses_reference_median(synthetic):
    detector, _, cal = synthetic
    missing = cal.iloc[:100].copy()
    missing.iloc[0, 0] = np.nan
    filled = missing.fillna({FEATURES[i]: detector.imputer.statistics_[i] for i in range(128)})
    assert detector.score_window(missing) == detector.score_window(filled)
    assert detector.evaluate(missing)["windows"][0]["missing_cells"] == 1


def test_all_missing_rejected(synthetic):
    detector, _, cal = synthetic
    for axis in [0, 1]:
        missing = cal.copy()
        if axis == 0:
            missing.iloc[:, 0] = np.nan
        else:
            missing.iloc[0, :] = np.nan
        assert detector.evaluate(missing)["status"] == "평가 불가"


def test_small_input_and_tail(synthetic):
    detector, _, cal = synthetic
    assert detector.evaluate(cal.iloc[:99])["status"] == "평가 불가"
    result = detector.evaluate(cal.iloc[:250])
    assert result["valid_windows"] == 2
    assert result["excluded_tail_rows"] == 50
    assert [(w["start_position"], w["end_position"]) for w in result["windows"]] == [(1, 100), (101, 200)]


def test_rff_determinism(synthetic):
    detector, ref, cal = synthetic
    replay = DriftDetector().fit_reference(ref)
    replay.calibrate(cal)
    np.testing.assert_array_equal(detector.rff.random_weights_, replay.rff.random_weights_)
    assert detector.threshold_ == replay.threshold_
    assert detector.evaluate(cal) == replay.evaluate(cal)


def test_mmd_formula_and_shift(synthetic):
    detector, _, cal = synthetic
    piece = cal.iloc[:100]
    values = detector.scaler.transform(detector.imputer.transform(piece))
    delta = detector.rff.transform(values).mean(axis=0) - detector.reference_mean_
    assert detector.score_window(piece) == float(delta @ delta)
    assert detector.score_window(piece + 100) > detector.score_window(piece)


def test_threshold_boundary_and_no_reset(synthetic):
    detector, _, cal = synthetic
    assert detector.status(detector.threshold_)[0] == "기준 범위"
    assert detector.status(np.nextafter(detector.threshold_, np.inf))[0] == "분포 변화 감지"
    with pytest.raises(ValueError):
        detector.calibrate(cal)
    with pytest.raises(ValueError):
        detector.fit_reference(cal)
    with pytest.raises(ValueError):
        detector.status(np.nan)


def test_degenerate_bandwidth_and_small_null():
    constant = pd.DataFrame(np.zeros((100, 128)), columns=FEATURES)
    with pytest.raises(ValueError, match="양의 거리"):
        DriftDetector().fit_reference(constant)
    rng = np.random.default_rng(6)
    frame = pd.DataFrame(rng.normal(size=(100, 128)), columns=FEATURES)
    with pytest.raises(ValueError, match="최소10"):
        DriftDetector().fit_reference(frame).calibrate(frame)


def test_csv_api_round_trip_and_error(synthetic):
    detector, _, cal = synthetic
    result = evaluate_csv(detector, io.StringIO(cal.iloc[:250].to_csv(index=False)))
    expected = detector.evaluate(cal.iloc[:250])
    np.testing.assert_allclose([w["score"] for w in result["windows"]],
                               [w["score"] for w in expected["windows"]], rtol=1e-12)
    assert result["status"] == expected["status"]
    assert evaluate_csv(detector, io.StringIO("bad\n1"))["status"] == "평가 불가"


def test_messages_do_not_claim_accuracy_or_cause():
    assert "정확도를 보장하지" in MESSAGES["기준 범위"]
    assert "재검증" in MESSAGES["분포 변화 감지"]
    assert all("%" not in message for message in MESSAGES.values())
    assert all("고장입니다" not in message and "교정 완료" not in message for message in MESSAGES.values())


@pytest.fixture(scope="module")
def actual():
    detector = joblib.load(ROOT / "models/drift_detection/rff_mmd_v1.joblib")
    frame = load_features()
    return detector, frame, pd.read_csv(OUT / "split_assignments.csv")


def test_real_reference_splits_and_no_overlap(actual):
    _, frame, assignments = actual
    assert assignments.row_id.is_unique
    assert set(assignments.row_id) == set(frame.row_id)
    parts = split_reference(frame)
    for part, ids in parts.items():
        rows = assignments[assignments.partition == part]
        assert rows.row_id.tolist() == frame.loc[ids, "row_id"].tolist()
        assert rows.batch.max() <= 6
    overlap = pd.read_csv(OUT / "overlap_checks.csv")
    assert len(overlap) == 10
    assert overlap.row_overlap.eq(0).all() and overlap.exact_feature_overlap.eq(0).all()
    assert assignments.groupby("partition").size().to_dict() == {
        "reference": 2966, "calibration": 1483, "internal": 1484, "batch7": 3613, "batch8": 294}


def test_real_reference_only_preprocessing(actual):
    detector, frame, assignments = actual
    ids = assignments[assignments.partition == "reference"].row_id
    ref = frame.set_index("row_id").loc[ids, FEATURES]
    np.testing.assert_allclose(detector.imputer.statistics_, ref.median())
    np.testing.assert_allclose(detector.scaler.mean_, ref.mean())
    np.testing.assert_allclose(detector.scaler.var_, ref.var(ddof=0))
    assert detector.scaler.n_samples_seen_ == 2966
    assert list(detector.imputer.feature_names_in_) == FEATURES
    assert detector.rff.random_state == 42 and detector.rff.n_components == 512


def test_real_threshold_only_calibration(actual):
    detector, _, _ = actual
    windows = pd.read_csv(OUT / "windows.csv")
    scores = windows[windows.partition == "calibration"].score
    assert len(scores) == 14
    np.testing.assert_allclose(detector.threshold_, np.quantile(scores, .95, method="linear"), rtol=1e-14)
    for row in windows.itertuples():
        assert row.alert == (row.score > detector.threshold_)


def test_real_original_target_order_and_tail(actual):
    _, _, assignments = actual
    summary = pd.read_csv(OUT / "partition_summary.csv").set_index("partition")
    for batch, win, tail in [(7, 36, 13), (8, 2, 94)]:
        rows = assignments[assignments.partition == f"batch{batch}"]
        np.testing.assert_array_equal(rows.source_line, np.arange(1, len(rows) + 1))
        assert summary.loc[f"batch{batch}", "valid_windows"] == win
        assert summary.loc[f"batch{batch}", "excluded_tail_rows"] == tail


def test_real_saved_model_and_scores_replay(actual):
    detector, frame, assignments = actual
    windows = pd.read_csv(OUT / "windows.csv")
    indexed = frame.set_index("row_id")
    for part in ["calibration", "internal", "batch7", "batch8"]:
        ids = assignments[assignments.partition == part].row_id
        result = detector.evaluate(indexed.loc[ids, FEATURES])
        old = windows[windows.partition == part]
        np.testing.assert_allclose([w["score"] for w in result["windows"]], old.score, rtol=1e-13)
        assert result["alert_windows"] == int(old.alert.sum())


def test_real_artifact_contains_no_labels_or_future_info(actual):
    detector, frame, _ = actual
    assert "gas" not in detector.metadata_ and "batch" not in detector.metadata_
    assert not hasattr(detector, "classifier") and not hasattr(detector, "classes_")
    assert frame.batch.max() == 8 and "gas" not in frame.columns
    plan = json.loads((OUT / "experiment_plan.json").read_text(encoding="utf-8"))
    assert plan["target_batches"] == [7, 8]
    assert plan["prohibited_scoring_batches"] == [9, 10]


def test_real_posthoc_metrics_and_support(actual):
    _, _, _ = actual
    wm = pd.read_csv(OUT / "window_error_analysis.csv")
    support = pd.read_csv(OUT / "window_gas_support.csv")
    assert len(wm) == 38 and wm.n.sum() == 3800
    assert support.groupby(["partition", "window"]).n.sum().eq(100).all()
    comparison = pd.read_csv(OUT / "warning_error_comparison.csv")
    for row in comparison[comparison.scope == "pooled_7_8"].itertuples():
        sub = wm[wm.alert == row.alert]
        assert sub.error_n.sum() == row.errors
        assert np.isclose(row.error_rate, row.errors / row.rows)
    replay = pd.read_csv(OUT / "prediction_reuse.csv")
    assert replay.exact_stage7_replay.all() and replay.fresh_predictions.eq(0).all()


def test_real_files_and_plan_preserved():
    check = verify()
    assert check["all_preserved"] and check["existing_models"] == 324
    assert check["scored_batches_9_10"] == [] and check["new_classifier_fits"] == 0


def test_graphs_reports_and_unavailable_disclosure():
    manifest = pd.read_csv(OUT / "graph_manifest.csv")
    assert len(manifest) >= 8
    assert all((ROOT / path).is_file() for path in manifest.path)
    report = (ROOT / "reports/drift_detection_report.html").read_text(encoding="utf-8")
    assert "독립 Test가 아님" in report and "Batch8" in report
    assert "실제 Streamlit은 설치·실행하지 않았고" in report
    assert "data:image/png;base64," in report
