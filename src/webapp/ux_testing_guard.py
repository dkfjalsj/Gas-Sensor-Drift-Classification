# 기존 테스트의 원본9~10 접근·과거 산출물 쓰기를 차단
# 제한된 검사는 통과가 아닌 건너뜀으로 기록

import json
import os
from pathlib import Path
import sys

from ..data import ROOT, read_config

EVENTS = []
CURRENT = ""


def pytest_sessionstart(session):
    raw = Path(read_config()["data_dir"])
    denied = {os.path.normcase(str(raw / f"batch{b}.dat")) for b in [9, 10]}
    allowed = os.path.normcase(str(ROOT / "outputs/streamlit_ux")) + os.sep
    protected = [os.path.normcase(str(ROOT / n)) + os.sep for n in ["src", "tests", "outputs", "models", "reports"]]

    def hook(event, args):
        if event != "open" or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        path = os.path.normcase(os.path.abspath(os.fsdecode(args[0])))
        flags = args[2] or 0
        writing = any(c in str(args[1] or "") for c in "wax+") or bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
        reason = "원본9~10 접근 제한" if path in denied else None
        if writing and any(path.startswith(p) for p in protected) and not path.startswith(allowed):
            reason = "과거 파일 쓰기 제한"
        if reason:
            EVENTS.append(dict(nodeid=CURRENT, path=path, reason=reason))
            import pytest
            pytest.skip("19.5단계 보존 검사: " + reason)
    sys.addaudithook(hook)


def pytest_runtest_setup(item):
    global CURRENT
    CURRENT = item.nodeid


def pytest_sessionfinish(session, exitstatus):
    (ROOT / "outputs/streamlit_ux/test_access_blocks.json").write_text(
        json.dumps(EVENTS, ensure_ascii=False, indent=2), encoding="utf-8")
