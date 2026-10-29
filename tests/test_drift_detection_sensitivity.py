# 고정 감지기·복제 없는 구성 통제·재배열 재현성과 보존 검사
# 원본9~10 접근이나 기존 결과 쓰기 없이 신규 진단 검증

import ast
import json

import joblib
import numpy as np
import pandas as pd
import pytest

from src.data import ROOT, FEATURES
from src.drift_detection.detector import load_detector
from src.drift_detection_sensitivity.experiment import OUT, OLD, DETECTOR, SEEDS, THRESHOLD, quotas_from_reference, shuffle_rows, controlled_rows, load_allowed


# 가상 표본으로 추출 규칙만 확인
def toy_frame():
    return pd.DataFrame({"gas": np.repeat(np.arange(1, 7), 120), "batch": 7,
                         "row_id": [f"toy_{i}" for i in range(720)]})


def test_quota_rule_and_invalid_proportions():
    np.testing.assert_array_equal(quotas_from_reference(np.ones(6) / 6), [17, 17, 17, 17, 16, 16])
    with pytest.raises(ValueError):
        quotas_from_reference([1, 0, 0, 0, 0, 0])
    with pytest.raises(ValueError):
        quotas_from_reference([.1] * 6)


def test_shuffle_reproducible_and_fixed_tail():
    frame = toy_frame()
    a = shuffle_rows(frame, 42)
    b = shuffle_rows(frame, 42)
    assert a.row_id.tolist() == b.row_id.tolist()
    assert a.row_id.tolist() != shuffle_rows(frame, 43).row_id.tolist()
    assert set(a.row_id) == set(frame.row_id)
    fixed = shuffle_rows(frame, 42, True)
    assert set(fixed.iloc[:700].row_id) == set(frame.iloc[:700].row_id)
    assert fixed.iloc[700:].row_id.tolist() == frame.iloc[700:].row_id.tolist()


def test_controlled_sampling_unique_and_reproducible():
    frame = toy_frame()
    quota = np.array([21, 26, 9, 8, 27, 9])
    a = controlled_rows(frame, quota, 4, 42, 7, 7)
    b = controlled_rows(frame, quota, 4, 42, 7, 7)
    assert a.row_id.tolist() == b.row_id.tolist() and a.row_id.is_unique
    for start in range(0, 400, 100):
        np.testing.assert_array_equal(a.iloc[start:start + 100].gas.value_counts().sort_index(), quota)
    with pytest.raises(ValueError):
        controlled_rows(frame, quota, 10, 42, 7, 7)


@pytest.fixture(scope="module")
def actual():
    return load_detector(DETECTOR), load_allowed().set_index("row_id", drop=False)


def test_detector_config_and_no_fit_calls(actual):
    detector, _ = actual
    assert detector.threshold_ == THRESHOLD
    path = ROOT / "src/drift_detection_sensitivity/experiment.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    forbidden = {"fit", "fit_transform", "fit_reference", "calibrate", "predict"}
    assert not [n for n in ast.walk(tree) if isinstance(n, ast.Call) and
                isinstance(n.func, ast.Attribute) and n.func.attr in forbidden]
    audit = json.loads((OUT / "execution_audit.json").read_text(encoding="utf-8"))
    assert not audit["labels_passed_to_detector"] and audit["new_fits"] == 0
    assert audit["loaded_detector_state_unchanged"] and audit["calibration_rescored"] is False


def test_original_scores_and_existing_error_reused():
    new = pd.read_csv(OUT / "existing_window_analysis.csv")
    old = pd.read_csv(OLD / "window_error_analysis.csv")
    assert len(new) == 38
    np.testing.assert_allclose(new.score, old.score, rtol=1e-14)
    np.testing.assert_array_equal(new.alert, old.alert)
    np.testing.assert_array_equal(new.error_n, old.error_n)
    np.testing.assert_allclose(new.mixture_tv, old.mixture_total_variation, rtol=1e-13)
    np.testing.assert_allclose(new[[f"gas{g}_proportion" for g in range(1, 7)]].sum(axis=1), 1)


def test_every_condition_seed_and_exact_sizes():
    summary = pd.read_csv(OUT / "condition_summary.csv")
    assert len(summary) == 42
    for batch, n, count, tail in [(7, 3613, 36, 13), (8, 294, 2, 94)]:
        for method in ["shuffle_all", "shuffle_fixed_rows"]:
            sub = summary[(summary.target == batch) & (summary.method == method)]
            assert set(sub.seed) == set(SEEDS) and len(sub) == 5
            assert sub.input_rows.eq(n).all() and sub.windows.eq(count).all()
            assert sub.excluded_tail_rows.eq(tail).all()


def test_no_cross_target_batch_or_duplicate_rows():
    members = pd.read_csv(OUT / "window_membership.csv")
    for keys, group in members.groupby(["method", "seed", "target", "source"]):
        assert group.row_id.is_unique
        if keys[3] == "target":
            assert group.batch.eq(keys[2]).all()
        else:
            assert group.batch.max() <= 6


def test_fixed_rows_and_global_mean_invariance():
    checks = pd.read_csv(OUT / "paired_row_checks.csv")
    assert len(checks) == 10 and checks.used_row_ids_same.all() and checks.excluded_row_ids_same.all()
    np.testing.assert_allclose(checks.global_distance_delta, 0, atol=1e-13)
    summary = pd.read_csv(OUT / "condition_summary.csv")
    np.testing.assert_allclose(summary.mean_score,
        summary.global_mean_distance_squared + summary.between_window_variation, atol=1e-13)


def test_controlled_equal_quotas_and_heldout_internal():
    quota = pd.read_csv(OUT / "controlled_quota.csv")
    np.testing.assert_array_equal(quota.quota, [21, 26, 9, 8, 27, 9])
    composition = pd.read_csv(OUT / "window_gas_composition.csv")
    sub = composition[composition.method == "composition_controlled"]
    for _, rows in sub.groupby(["seed", "target", "source", "window"]):
        np.testing.assert_array_equal(rows.sort_values("gas_id").n, quota.quota)
    split = pd.read_csv(OLD / "split_assignments.csv")
    members = pd.read_csv(OUT / "window_membership.csv")
    ids = members[(members.method == "composition_controlled") & (members.source == "internal")].row_id
    assert set(ids) <= set(split[split.partition == "internal"].row_id)
    assert set(ids).isdisjoint(split[split.partition.isin(["reference", "calibration"])].row_id)


def test_controlled_capacity_matches_available_support():
    table = pd.read_csv(OUT / "controlled_support.csv")
    availability = pd.read_csv(OUT / "controlled_availability.csv")
    for row in availability.itertuples():
        for source in ["internal", "target"]:
            sub = table[(table.target == row.target) & (table.source == source)]
            assert row.selected_windows_per_source <= (sub.n // sub.quota).min()
        assert row.selected_rows == row.selected_windows_per_source * 100
    assert availability.selected_windows_per_source.tolist() == [14, 1]


def test_all_stored_scores_and_memberships_reproduce(actual):
    detector, frame = actual
    before = joblib.hash(detector)
    members = pd.read_csv(OUT / "window_membership.csv")
    windows = pd.read_csv(OUT / "window_scores.csv")
    for keys, group in members.groupby(["method", "seed", "target", "source"], sort=False):
        group = group.sort_values("position")
        result = detector.evaluate(frame.loc[group.row_id, FEATURES])
        method, seed, target, source = keys
        stored = windows[(windows.method == method) & (windows.seed == seed) &
                         (windows.target == target) & (windows.source == source)].sort_values("window")
        np.testing.assert_allclose([w["score"] for w in result["windows"]], stored.score, rtol=1e-12)
        np.testing.assert_array_equal([w["alert"] for w in result["windows"]], stored.alert)
    assert joblib.hash(detector) == before


def test_mean_median_min_max_and_warning_rate():
    summary = pd.read_csv(OUT / "condition_summary.csv")
    windows = pd.read_csv(OUT / "window_scores.csv")
    for row in summary.itertuples():
        sub = windows[(windows.method == row.method) & (windows.seed == row.seed) &
                      (windows.target == row.target) & (windows.source == row.source)]
        np.testing.assert_allclose([row.mean_score, row.median_score, row.min_score, row.max_score],
                                   [sub.score.mean(), sub.score.median(), sub.score.min(), sub.score.max()], rtol=1e-12)
        assert row.alert_windows == sub.alert.sum()
        assert np.isclose(row.alert_rate, sub.alert.mean())
        assert (sub.alert == (sub.score > THRESHOLD)).all()






