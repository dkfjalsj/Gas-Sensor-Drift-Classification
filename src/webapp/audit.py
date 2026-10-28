# 웹앱 통합 전후 기존 모델·연구 결과 보존 및 실행 환경 기록
# 원본9~10은 수치 평가 없이 파일 지문 확인에만 사용

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import pandas as pd

from ..data import ROOT, read_config
from ..temporal_expansion import now

OUT = ROOT / "outputs/streamlit_integration"
REPORT = ROOT / "reports/streamlit_integration_report.md"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


# 이번 단계의 신규 파일을 제외한 보존 지문 수집
def snapshot():
    files = {}
    new_code = ROOT / "src/webapp"
    new_test = ROOT / "tests/test_streamlit_integration.py"
    for folder in ["src", "tests", "models", "outputs", "reports"]:
        for path in (ROOT / folder).rglob("*"):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            if OUT in path.parents or new_code in path.parents or path in [REPORT, new_test]:
                continue
            files[str(path.relative_to(ROOT))] = sha(path)
    for name in ["README.md", "requirements.txt", "requirements-lock.txt", "config.json", "training_config.json", ".gitignore"]:
        files[name] = sha(ROOT / name)
    return files


# 추론 앱 개발 범위와 보존 기준 먼저 기록
def prepare():
    if OUT.exists() or REPORT.exists():
        raise FileExistsError("19단계 결과 경로가 이미 존재함")
    OUT.mkdir()
    directory = Path(read_config()["data_dir"])
    write("preservation_before.json", {"files": snapshot(), "raw": {
        f"batch{b}.dat": sha(directory / f"batch{b}.dat") for b in range(1, 11)}})
    write("integration_plan.json", {
        "stage": 19, "prepared_at": now(), "new_model_fits": 0,
        "purpose": "Existing Model A predict + existing RFF-MMD evaluate; no scientific model comparison",
        "models": ["models/temporal_expansion/B_SVM_balanced.joblib", "models/drift_detection/rff_mmd_v1.joblib"],
        "threshold": 0.00825701197565701, "window_size": 100,
        "inputs": "UTF-8 CSV f001..f128, optional gas integer1..6; reject unknown columns; reorder exact features",
        "privacy": "No application persistence of uploaded sensor features; model cache only, results per-session memory",
        "tests": "Service unit tests + Streamlit AppTest real file_uploader + localhost server and browser; "
                 "99/100/101/200 rows, labels/no labels, malformed headers/values, changing input, downloads and replay",
        "data": "Synthetic fixtures are UI tests only, not research performance; Batch7 first200 in-memory "
                "prediction equality against saved stage14 baseline only. No new Batch9/10 evaluation; "
                "raw9/10 bytes read for preservation SHA only outside restricted legacy tests.",
        "old_tests": "Audit hook skips attempts to open raw9/10 or overwrite old artifacts; report skips separately",
        "changes": "Only new app entrypoint, src/webapp, test, requirements-streamlit/constraints/lock, README_streamlit, new outputs/report",
        "limits": "Research prototype, no authentication/production safety certification, no retraining or automatic swap; "
                  "MMD not probability, equipment fault or predicted classification accuracy",
    })
    write("core_environment.json", {n: importlib.metadata.version(n) for n in
        ["numpy", "pandas", "scipy", "scikit-learn", "joblib", "matplotlib", "streamlit", "altair"]})
    print("Stage19 preservation and integration scope recorded", flush=True)


# 기존 기록은 수정하지 않고 지문만 비교
def verify(include_raw=True):
    before = json.loads((OUT / "preservation_before.json").read_text(encoding="utf-8"))
    rows = [dict(kind="existing", path=p, expected=s, actual=sha(ROOT / p)) for p, s in before["files"].items()]
    if include_raw:
        directory = Path(read_config()["data_dir"])
        rows += [dict(kind="raw_hash_only", path=p, expected=s, actual=sha(directory / p)) for p, s in before["raw"].items()]
    table = pd.DataFrame(rows)
    assert table.expected.eq(table.actual).all()
    table.to_csv(OUT / "preservation_audit.csv", index=False, encoding="utf-8")
    old = {p for p in before["files"] if p.endswith(".joblib")}
    assert old == {str(p.relative_to(ROOT)) for p in (ROOT / "models").rglob("*.joblib")}
    return dict(all_preserved=True, existing_files=len(before["files"]), models=len(old),
                raw_files_hashed=10 if include_raw else 0, new_model_fits=0,
                batch9_10_new_evaluation=False)


def test_summary():
    path = OUT / "test_results.xml"
    if not path.exists():
        return {"status": "pending"}
    old = ET.parse(ROOT / "outputs/drift_detection/test_results.xml")
    historical = {(c.get("classname"), c.get("name")) for c in old.iter("testcase")
                  if c.find("failure") is not None or c.find("error") is not None}
    cases = list(ET.parse(path).iter("testcase"))
    failures, skipped = [], []
    for case in cases:
        error = case.find("failure")
        if error is None:
            error = case.find("error")
        if error is not None:
            key = (case.get("classname"), case.get("name"))
            failures.append(dict(classname=key[0], name=key[1], historical=key in historical,
                                 reason=error.get("message", "")[:1000]))
        skip = case.find("skipped")
        if skip is not None:
            skipped.append(dict(classname=case.get("classname"), name=case.get("name"), reason=skip.get("message", "")))
    new = [c for c in cases if "test_streamlit_integration" in c.get("classname", "")]
    result = dict(total=len(cases), passed=len(cases) - len(failures) - len(skipped), failed=len(failures),
        skipped=len(skipped), historical_failures=sum(f["historical"] for f in failures),
        new_failures=sum(not f["historical"] for f in failures), new_tests=len(new),
        new_passed=sum(c.find("failure") is None and c.find("error") is None and c.find("skipped") is None for c in new),
        failures=failures, skipped_tests=skipped)
    write("test_summary.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "verify"])
    if parser.parse_args().action == "prepare":
        prepare()
    else:
        write("final_verification.json", {**verify(), "tests": test_summary(), "checked_at": now()})
