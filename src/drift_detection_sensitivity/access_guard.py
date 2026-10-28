# 금지된 원본 읽기와 기존 파일 쓰기를 실행 전에 차단
# 기존 테스트는 수정하지 않고 제한으로 인한 건너뜀 별도 기록

import json
import os
from pathlib import Path
import sys

from ..data import ROOT, read_config

EVENTS = []
CURRENT_TEST = ""
INSTALLED = False


# 실제 원본 Batch9~10과 기존 산출물 접근 제한
def install(test_mode=False):
    global INSTALLED
    if INSTALLED:
        return
    raw = Path(read_config()["data_dir"])
    denied = {os.path.normcase(str(raw / f"batch{b}.dat")) for b in [9, 10]}
    allowed_output = os.path.normcase(str(ROOT / "outputs/drift_detection_sensitivity")) + os.sep
    allowed_reports = {os.path.normcase(str(ROOT / "reports" / f"drift_detection_sensitivity_report.{ext}"))
                       for ext in ["html", "md"]}
    protected = [os.path.normcase(str(ROOT / name)) + os.sep for name in
                 ["src", "tests", "outputs", "reports", "models"]]

    def hook(event, args):
        if event != "open" or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        path = os.path.normcase(os.path.abspath(os.fsdecode(args[0])))
        mode = args[1] or ""
        flags = args[2] or 0
        writing = any(c in str(mode) for c in "wax+") or bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
        reason = None
        if path in denied:
            reason = "Batch9~10 원본 열기 금지"
        elif writing and any(path.startswith(folder) for folder in protected):
            if not path.startswith(allowed_output) and path not in allowed_reports:
                reason = "기존 파일 쓰기 금지"
        if reason:
            EVENTS.append(dict(nodeid=CURRENT_TEST, action="write" if writing else "read", path=path, reason=reason))
            if test_mode:
                import pytest
                pytest.skip("18.5단계 접근 제한: " + reason)
            raise PermissionError(reason + ": " + path)
    sys.addaudithook(hook)
    INSTALLED = True


def pytest_sessionstart(session):
    install(test_mode=True)


def pytest_runtest_setup(item):
    global CURRENT_TEST
    CURRENT_TEST = item.nodeid


def pytest_sessionfinish(session, exitstatus):
    path = ROOT / "outputs/drift_detection_sensitivity/test_access_blocks.json"
    path.write_text(json.dumps(EVENTS, ensure_ascii=False, indent=2), encoding="utf-8")
