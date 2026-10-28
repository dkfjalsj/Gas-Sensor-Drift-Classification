# 저장 감지기로 창 재배열·가스 구성 통제의 민감도 계산
# 라벨 기반 진단과 무라벨 점수 입력 분리 및 기존 파일 보존

import argparse
import json
import logging
from pathlib import Path
import xml.etree.ElementTree as ET

import joblib
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from ..data import ROOT, FEATURES, GASES, parse_line, read_config
from ..temporal_expansion import sha, now
from ..drift_detection.detector import load_detector

OUT = ROOT / "outputs/drift_detection_sensitivity"
OLD = ROOT / "outputs/drift_detection"
DETECTOR = ROOT / "models/drift_detection/rff_mmd_v1.joblib"
OFFICIAL = ROOT / "models/temporal_expansion/B_SVM_balanced.joblib"
SEEDS = [42, 43, 44, 45, 46]
THRESHOLD = 0.00825701197565701
REPORTS = [f"drift_detection_sensitivity_report.{ext}" for ext in ["html", "md"]]
CAUTION = ("고정 감지기의 사후 민감도 진단이며 실제 센서 드리프트 탐지 정확도 검증 아님. "
           "라벨 기반 구성 통제는 운영용 무라벨 평가가 아님. 반복 개발 자료이며 독립 Test 없음. "
           "Batch9~10 원본 읽기·평가 없음. 모델·임계값 변경 없음.")


# 새 결과만 UTF-8로 저장
def write(name, value):
    def convert(item):
        if isinstance(item, np.generic):
            return item.item()
        if isinstance(item, np.ndarray):
            return item.tolist()
        raise TypeError(type(item).__name__)
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False,
                                      default=convert), encoding="utf-8")


def save(name, rows):
    table = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    table.to_csv(OUT / f"{name}.csv", index=False, encoding="utf-8")
    return table


# 신규 분석 결과를 제외한 파일 지문 수집
def snapshot():
    result = {}
    for folder in ["src", "tests", "outputs", "reports", "models"]:
        for path in (ROOT / folder).rglob("*"):
            if not path.is_file() or "__pycache__" in path.parts or OUT in path.parents:
                continue
            if path.parent == ROOT / "reports" and path.name in REPORTS:
                continue
            result[str(path.relative_to(ROOT))] = sha(path)
    for name in ["README.md", "config.json", "training_config.json", ".gitignore",
                 "requirements.txt", "requirements-lock.txt"]:
        result[name] = sha(ROOT / name)
    return result


# 새 점수 산출 전 분석 조건과 판정 규칙 고정
def freeze():
    if OUT.exists() or any((ROOT / "reports" / n).exists() for n in REPORTS):
        raise FileExistsError("18.5단계 경로가 이미 존재함")
    OUT.mkdir()
    plan = dict(
        stage="18.5", frozen_at=now(), seeds=SEEDS, window_size=100,
        detector_sha256=sha(DETECTOR), official_sha256=sha(OFFICIAL), threshold=THRESHOLD,
        data="Read raw Batch1..8 only. Reference/Calibration/internal IDs reused from stage18. "
             "Reference used only to describe proportions; Calibration never rescored or refitted. "
             "No raw9/10 read including hash checks and full tests.",
        experiment_A="Reuse all38 saved stage18 target windows, gas support and classifier error. "
                     "TV=0.5*sum(abs(window gas proportion - saved Reference proportion)). "
                     "Spearman pooled and per Batch for score vs TV/classes/error; >=3 nonconstant "
                     "observations only; descriptive, no p-values or causal claims.",
        experiment_B1="Original per-Batch source-line order. Replay against old scores before comparisons.",
        experiment_B2="For each Batch7/8 independently, default_rng(SeedSequence([seed,batch])).permutation(N). "
                      "All rows shuffled, full100 windows used, remainder excluded. Same5 seeds, no selection.",
        paired_row_check="Additional diagnostic: permute only original first floor(N/100)*100 evaluated "
                         "rows with same SeedSequence, append unchanged original tail. Isolates grouping "
                         "changes from excluded-row membership. Not a fourth detector configuration.",
        experiment_B3="Label-based diagnostic only. Hamilton integer quota100 from saved Reference gas "
                      "proportions, tie lower gas ID, all6 quotas>=1 else unavailable. For each target7/8 "
                      "and saved INTERNAL evaluation pool, capacity K_s=min_g floor(n_sg/quota_g). "
                      "Use common K=min(K_internal,K_target); if K<1 unavailable. "
                      "Per gas default_rng(SeedSequence([seed,target,source_code,gas])) with source0=internal, "
                      "source_code=target Batch otherwise. Pick K*quota without replacement, consecutive "
                      "quota slices per window; no duplicate rows within source/seed/comparison. "
                      "No Reference/Calibration rows in controlled null, no cross-target-Batch mixture.",
        controlled_limits="Unequal source capacities disclosed; equal selected K within target/internal pair. "
                          "Rows can recur across seeds and controlled comparisons. Batch8 likely1 matched "
                          "window; no independent repeats, no mechanistic causal isolation.",
        mean_decomposition="For each equal100-row window set: mean(score)=||overall RFF mean-ref||² "
                           "+ mean(||window mean-overall mean||²). Global term diagnostic only, no threshold "
                           "applied to global mean. Fixed-row shuffle must keep global term unchanged.",
        label_boundary="True labels used only for A interpretation and B3 row selection. Frozen detector "
                       "evaluate/score receives exactly f001..f128; no fit/calibrate/threshold changes.",
        metrics="All window scores/alerts/proportions/IDs, mean median min max MMD, alert count/rate, "
                "excluded rows, paired membership checks, descriptive seed SD/ddof1 and range; no favorable seed.",
        inference="Window partition, mixture proportions and retained sample content may change together. "
                  "All-row shuffle not pure ordering contrast; fixed-row check separates tail membership. "
                  "Controlled sampling changes content too; residual shift not proof of physical drift.",
        tests="Full existing+new tests with audit-hook block on raw9/10 and writes to past project files. "
              "Restricted tests skipped and logged; no old test/hash edits. Do not call skipped checks passed.",
        preservation="Hash all existing project artifacts and raw1..8 only; no9/10 hash reread. "
                     "Verify existing model inventory unchanged (no new joblib).",
        conclusion="C on replay/partition/preservation/threshold violation. A if A/B1/B2/paired/B3 "
                   "quantified for both targets with >=1 unique controlled window, all seeds recorded, "
                   "new tests pass and limits disclosed. B if one diagnostic unavailable or insufficient. "
                   "A quantifies sensitivity, not drift detection accuracy or causal separation.",
        stop="No parameter/seed/quota/window/threshold retry based on outcomes; stop on integrity failure. "
             "No classifier fits, detector fits, new artifacts under models, Streamlit integration or Git mutations.",
        limitations=CAUTION,
    )
    write("experiment_plan.json", plan)
    (OUT / "protocol.md").write_text("# 18.5단계 사전 고정 계획\n\n" + CAUTION + "\n\n```json\n" +
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n```\n", encoding="utf-8")
    write("plan_lock.json", dict(plan=sha(OUT / "experiment_plan.json"), protocol=sha(OUT / "protocol.md")))
    raw_dir = Path(read_config()["data_dir"])
    write("preservation_before.json", dict(files=snapshot(), raw={
        f"batch{b}.dat": sha(raw_dir / f"batch{b}.dat") for b in range(1, 9)}))
    print("Stage18.5 protocol frozen; no new scores computed", flush=True)


# 기존 형식 파서로 허용된8개 Batch만 불러오기
def load_allowed():
    rows = []
    raw = Path(read_config()["data_dir"])
    for batch in range(1, 9):
        for source_line, line in enumerate((raw / f"batch{batch}.dat").read_text(encoding="utf-8").splitlines(), 1):
            gas, values = parse_line(line)
            rows.append([f"b{batch:02d}_r{source_line:05d}", batch, source_line, gas, *values])
    return pd.DataFrame(rows, columns=["row_id", "batch", "source_line", "gas", *FEATURES])


# 기준 가스 비율을100개 정수 할당량으로 변환
def quotas_from_reference(proportions):
    if len(proportions) != 6 or not np.isfinite(proportions).all() or not np.isclose(np.sum(proportions), 1):
        raise ValueError("유효한6종 비율 필요")
    ideal = np.asarray(proportions, dtype=float) * 100
    counts = np.floor(ideal).astype(int)
    remaining = 100 - counts.sum()
    order = sorted(range(6), key=lambda i: (-(ideal[i] - counts[i]), i))
    for i in order[:remaining]:
        counts[i] += 1
    if counts.sum() != 100 or (counts < 1).any():
        raise ValueError("6종을 포함한100행 할당 불가")
    return counts


# 동일 행 집합 재배열과 전체 Batch 재배열 구분
def shuffle_rows(sub, seed, fixed_rows=False):
    used = len(sub) // 100 * 100 if fixed_rows else len(sub)
    order = np.random.default_rng(np.random.SeedSequence([seed, int(sub.batch.iloc[0])])).permutation(used)
    return pd.concat([sub.iloc[order], sub.iloc[used:]])


# 가스별 표본을 복제 없이 뽑아 같은 구성의 창 생성
def controlled_rows(sub, quota, n_windows, seed, target, source_code):
    selected = []
    for i, gas in enumerate(GASES):
        ids = sub.index[sub.gas == gas].to_numpy()
        order = np.random.default_rng(np.random.SeedSequence([seed, target, source_code, gas])).permutation(ids)
        if len(order) < n_windows * quota[i]:
            raise ValueError("구성 통제 표본 부족")
        selected.append(order[:n_windows * quota[i]].reshape(n_windows, quota[i]))
    ids = np.concatenate([np.concatenate([g[w] for g in selected]) for w in range(n_windows)])
    if len(ids) != len(set(ids)):
        raise AssertionError("구성 통제 표본 중복")
    return sub.loc[ids]


# 기존 파일·모델·계획 보존 확인 (원본9~10 열지 않음)
def verify():
    before = json.loads((OUT / "preservation_before.json").read_text(encoding="utf-8"))
    raw = Path(read_config()["data_dir"])
    rows = [dict(kind="existing", path=p, expected=s, actual=sha(ROOT / p)) for p, s in before["files"].items()]
    rows += [dict(kind="raw_1_8", path=p, expected=s, actual=sha(raw / p)) for p, s in before["raw"].items()]
    table = save("preservation_audit", rows)
    assert table.expected.eq(table.actual).all()
    lock = json.loads((OUT / "plan_lock.json").read_text(encoding="utf-8"))
    assert sha(OUT / "experiment_plan.json") == lock["plan"]
    assert sha(OUT / "protocol.md") == lock["protocol"]
    if (OUT / "result_lock.json").exists():
        for path, digest in json.loads((OUT / "result_lock.json").read_text(encoding="utf-8")).items():
            assert sha(ROOT / path) == digest
    old_models = {p for p in before["files"] if p.endswith(".joblib")}
    current_models = {str(p.relative_to(ROOT)) for p in (ROOT / "models").rglob("*.joblib")}
    assert old_models == current_models
    return dict(all_preserved=True, existing_models=len(old_models), existing_files=len(before["files"]),
                raw_files_verified=8, raw9_10_opened=False, raw9_10_reverified=False,
                detector_unchanged=True, threshold=THRESHOLD, new_fits=0, plan_unchanged=True)


# 조건별 창 요약과 가스 구성 기록
def evaluate_condition(detector, sub, method, seed, target, source, reference_proportions):
    result = detector.evaluate(sub[FEATURES])
    assert result["valid_windows"] == len(sub) // 100 and result["invalid_windows"] == 0
    windows, members, gas_rows, means = [], [], [], []
    for pos, row in enumerate(sub.itertuples(), 1):
        members.append(dict(method=method, seed=seed, target=target, source=source,
                            row_id=row.row_id, batch=int(row.batch), source_line=int(row.source_line),
                            gas_id=int(row.gas), position=pos,
                            window=(pos - 1) // 100 + 1 if pos <= result["valid_windows"] * 100 else 0))
    for item in result["windows"]:
        piece = sub.iloc[item["start_position"] - 1:item["end_position"]]
        proportions = piece.gas.value_counts(normalize=True).reindex(GASES, fill_value=0)
        tv = float(np.abs(proportions.to_numpy() - reference_proportions).sum() / 2)
        meta = dict(method=method, seed=seed, target=target, source=source, window=item["window"])
        windows.append(dict(**meta, score=item["score"], alert=item["alert"], n=100,
                            gas_classes=int(piece.gas.nunique()), mixture_tv=tv))
        gas_rows.extend(dict(**meta, gas_id=g, n=int((piece.gas == g).sum()), proportion=float(proportions[g])) for g in GASES)
        values = detector.scaler.transform(detector.imputer.transform(piece[FEATURES]))
        means.append(detector.rff.transform(values).mean(axis=0))
    embedding_means = np.asarray(means)
    global_mean = embedding_means.mean(axis=0)
    global_score = float(np.square(global_mean - detector.reference_mean_).sum())
    between = float(np.square(embedding_means - global_mean).sum(axis=1).mean())
    scores = np.asarray([w["score"] for w in windows])
    np.testing.assert_allclose(scores.mean(), global_score + between, rtol=1e-10, atol=1e-14)
    summary = dict(method=method, seed=seed, target=target, source=source,
        input_rows=len(sub), used_rows=len(windows) * 100, windows=len(windows),
        excluded_tail_rows=result["excluded_tail_rows"], mean_score=float(scores.mean()),
        median_score=float(np.median(scores)), min_score=float(scores.min()), max_score=float(scores.max()),
        alert_windows=result["alert_windows"], alert_rate=result["alert_rate"],
        mean_tv=float(np.mean([w["mixture_tv"] for w in windows])),
        mean_gas_classes=float(np.mean([w["gas_classes"] for w in windows])),
        global_mean_distance_squared=global_score, between_window_variation=between)
    return summary, windows, members, gas_rows


# 저장된 원본 창 점수에만 정답 구성·오류 정보를 결합
def analyze_existing(reference_proportions):
    old = pd.read_csv(OLD / "window_error_analysis.csv")
    supports = pd.read_csv(OLD / "window_gas_support.csv")
    supports = supports[supports.partition.isin(["batch7", "batch8"])].copy()
    supports["proportion"] = supports.n / 100
    rows = []
    for row in old.itertuples():
        sub = supports[(supports.partition == row.partition) & (supports.window == row.window)].set_index("gas_id").loc[list(GASES)]
        tv = float(np.abs(sub.proportion.to_numpy() - reference_proportions).sum() / 2)
        assert np.isclose(tv, row.mixture_total_variation)
        rows.append(dict(partition=row.partition, window=row.window, score=row.score, alert=row.alert,
                         gas_classes=int((sub.n > 0).sum()), mixture_tv=tv, error_n=row.error_n,
                         error_rate=row.error_rate, **{f"gas{g}_proportion": float(sub.loc[g, "proportion"]) for g in GASES}))
    table = save("existing_window_analysis", rows)
    associations = []
    for scope, sub in [("pooled_7_8", table), ("batch7", table[table.partition == "batch7"]),
                       ("batch8", table[table.partition == "batch8"])]:
        for variable in ["mixture_tv", "gas_classes", "error_rate"]:
            enough = len(sub) >= 3 and sub.score.nunique() > 1 and sub[variable].nunique() > 1
            associations.append(dict(scope=scope, variable=variable, windows=len(sub),
                spearman=float(spearmanr(sub.score, sub[variable]).statistic) if enough else None,
                inferential=False, note="descriptive" if enough else "insufficient/constant"))
    save("existing_associations", associations)


# 정해진 조건과 모든 시드 한 번 실행
def run():
    if (OUT / "started.json").exists():
        raise FileExistsError("실행 흔적 있음: 조건 변경 재실행 금지")
    verify()
    write("started.json", dict(started_at=now()))
    logging.basicConfig(filename=OUT / "execution_log.txt", encoding="utf-8", level=logging.INFO)
    frame = load_allowed()
    detector = load_detector(DETECTOR)
    assert detector.threshold_ == THRESHOLD
    state_hash = joblib.hash(detector)
    split = pd.read_csv(OLD / "split_assignments.csv")
    reference = pd.read_csv(OLD / "gas_composition.csv")
    reference = reference[reference.partition == "reference"].set_index("gas_id").loc[list(GASES)]
    proportions = reference.proportion.to_numpy()
    quota = quotas_from_reference(proportions)
    save("controlled_quota", [dict(gas_id=g, gas=GASES[g], reference_n=int(reference.loc[g, "n"]),
                                   reference_proportion=float(proportions[i]), quota=int(quota[i])) for i, g in enumerate(GASES)])
    indexed = frame.set_index("row_id", drop=False)
    internal = indexed.loc[split[split.partition == "internal"].row_id].copy()
    # 행 ID를 인덱스로 사용해 통제 추출의 중복 확인
    frame = frame.set_index("row_id", drop=False)
    all_summary, all_windows, all_members, all_gas = [], [], [], []

    def evaluate(sub, method, seed, target, source):
        summary, windows, members, gas_rows = evaluate_condition(
            detector, sub, method, seed, target, source, proportions)
        all_summary.append(summary)
        all_windows.extend(windows)
        all_members.extend(members)
        all_gas.extend(gas_rows)
        logging.info("%s target%s source%s seed%s: windows=%s alerts=%s mean=%s",
                     method, target, source, seed, summary["windows"], summary["alert_windows"], summary["mean_score"])
        return summary, windows

    support_rows, paired_checks, availability = [], [], []
    old_windows = pd.read_csv(OLD / "windows.csv")
    for batch in [7, 8]:
        sub = frame[frame.batch == batch]
        base, original = evaluate(sub, "original", 0, batch, "target")
        old = old_windows[old_windows.partition == f"batch{batch}"]
        np.testing.assert_allclose([w["score"] for w in original], old.score, rtol=1e-13)
        np.testing.assert_array_equal([w["alert"] for w in original], old.alert)
        for seed in SEEDS:
            evaluate(shuffle_rows(sub, seed), "shuffle_all", seed, batch, "target")
            fixed = shuffle_rows(sub, seed, fixed_rows=True)
            paired, _ = evaluate(fixed, "shuffle_fixed_rows", seed, batch, "target")
            n = len(sub) // 100 * 100
            assert set(sub.iloc[:n].row_id) == set(fixed.iloc[:n].row_id)
            assert sub.iloc[n:].row_id.tolist() == fixed.iloc[n:].row_id.tolist()
            np.testing.assert_allclose(base["global_mean_distance_squared"], paired["global_mean_distance_squared"], rtol=1e-12)
            paired_checks.append(dict(target=batch, seed=seed, used_row_ids_same=True, excluded_row_ids_same=True,
                global_distance_delta=paired["global_mean_distance_squared"] - base["global_mean_distance_squared"]))
        caps = {}
        for source, part in [("internal", internal), ("target", sub)]:
            counts = part.gas.value_counts().reindex(GASES, fill_value=0).to_numpy()
            caps[source] = int(np.min(counts // quota))
            support_rows.extend(dict(target=batch, source=source, gas_id=g, n=int(counts[i]),
                                      quota=int(quota[i]), capacity_windows=int(counts[i] // quota[i])) for i, g in enumerate(GASES))
        common = min(caps.values())
        availability.append(dict(target=batch, internal_capacity=caps["internal"],
                                  target_capacity=caps["target"], selected_windows_per_source=common,
                                  internal_n=len(internal), target_n=len(sub), selected_rows=common * 100,
                                  internal_unselected=len(internal) - common * 100,
                                  target_unselected=len(sub) - common * 100,
                                  available=common >= 1))
        if common < 1:
            continue
        for seed in SEEDS:
            for source, part, source_code in [("internal", internal, 0), ("target", sub, batch)]:
                selected = controlled_rows(part, quota, common, seed, batch, source_code)
                assert set(selected.row_id).isdisjoint(set(split[split.partition.isin(["reference", "calibration"])].row_id))
                evaluate(selected, "composition_controlled", seed, batch, source)
    analyze_existing(proportions)
    summary = save("condition_summary", all_summary)
    save("window_scores", all_windows)
    save("window_membership", all_members)
    save("window_gas_composition", all_gas)
    save("controlled_support", support_rows)
    save("controlled_availability", availability)
    save("paired_row_checks", paired_checks)
    grouped = summary[summary.seed.isin(SEEDS)].groupby(["method", "target", "source"])
    variability = grouped.agg(seeds=("seed", "nunique"), mean_score=("mean_score", "mean"),
        seed_sd_mean_score=("mean_score", "std"), min_seed_mean=("mean_score", "min"),
        max_seed_mean=("mean_score", "max"), mean_alert_rate=("alert_rate", "mean"),
        min_alert_rate=("alert_rate", "min"), max_alert_rate=("alert_rate", "max"),
        seed_sd_alert_rate=("alert_rate", "std")).reset_index()
    save("seed_variability", variability)
    assert joblib.hash(detector) == state_hash
    write("execution_audit.json", dict(loaded_detector_state_unchanged=True, threshold_unchanged=True,
        original_replay_exact=True, model_A_predictions=0, new_fits=0, labels_passed_to_detector=False,
        scored_target_batches=[7, 8], raw_batches_loaded=list(range(1, 9)), raw9_10_opened=False,
        reference_refitted=False, calibration_rescored=False, all_seeds=SEEDS))
    locked = [OUT / f"{n}.csv" for n in ["condition_summary", "window_scores", "window_membership",
              "window_gas_composition", "controlled_quota", "existing_window_analysis"]]
    write("result_lock.json", {str(p.relative_to(ROOT)): sha(p) for p in locked})
    write("final_verification.json", {**verify(), "completed_at": now(), "tests_pending": True})
    from .report import render
    render()
    print(summary.to_string(index=False), flush=True)


# 이번 제한으로 건너뛴 검사와 역사적 실패 구분
def test_summary():
    path = OUT / "test_results.xml"
    if not path.exists():
        return dict(status="전체 테스트 실행 전")
    previous = ET.parse(OLD / "test_results.xml")
    old = {(c.get("classname"), c.get("name")) for c in previous.iter("testcase")
           if c.find("failure") is not None or c.find("error") is not None}
    cases = list(ET.parse(path).iter("testcase"))
    failures, skipped = [], []
    for c in cases:
        error = c.find("failure")
        if error is None:
            error = c.find("error")
        if error is not None:
            key = (c.get("classname"), c.get("name"))
            failures.append(dict(classname=key[0], name=key[1], historical=key in old,
                                 reason=error.get("message", "")[:900]))
        skip = c.find("skipped")
        if skip is not None:
            skipped.append(dict(classname=c.get("classname"), name=c.get("name"), reason=skip.get("message", "")))
    new = [c for c in cases if "test_drift_detection_sensitivity" in c.get("classname", "")]
    result = dict(total=len(cases), passed=len(cases) - len(failures) - len(skipped), failed=len(failures),
        skipped=len(skipped), historical_failures=sum(f["historical"] for f in failures),
        new_failures=sum(not f["historical"] for f in failures), new_tests=len(new),
        new_passed=sum(c.find("failure") is None and c.find("error") is None and c.find("skipped") is None for c in new),
        failures=failures, skipped_tests=skipped)
    write("test_summary.json", result)
    return result


def main():
    from .access_guard import install
    install()
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["freeze", "run", "report"])
    action = parser.parse_args().action
    if action == "freeze":
        freeze()
    elif action == "run":
        try:
            run()
        except Exception:
            logging.exception("고정 진단 중단: 설정 변경 재시도 없음")
            raise
    else:
        from .report import render
        render()
        write("final_verification.json", {**verify(), "tests": test_summary(), "checked_at": now()})


if __name__ == "__main__":
    main()
