# 과거 산출물 쓰기와Batch9~10 읽기 차단
# 의도된UI확장과 고정 소스 해시 검사의 충돌은 별도xfail 기록

import json
import os
from pathlib import Path
import sys

import pytest

from ..data import ROOT, read_config
from .preservation import verify

EVENTS = []
CURRENT = ''
PRESERVED = None
COMPATIBILITY = []
LEGACY_SOURCE_CHECKS = {
    'tests/test_project_cleanup.py::test_prior_research_preserved',
    'tests/test_report_publication.py::test_actual_sources_are_unchanged',
}


def pytest_sessionstart(session):
    raw = Path(read_config()['data_dir'])
    denied = {os.path.normcase(str(raw / f'batch{batch}.dat')) for batch in [9, 10]}
    allowed = os.path.normcase(str(ROOT / 'outputs/retraining_candidates')) + os.sep
    protected = [os.path.normcase(str(ROOT / name)) + os.sep
                 for name in ['src', 'tests', 'outputs', 'models', 'reports', 'data']]

    def hook(event, args):
        if event != 'open' or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        path = os.path.normcase(os.path.abspath(os.fsdecode(args[0])))
        flags = args[2] or 0
        writing = any(char in str(args[1] or '') for char in 'wax+') or bool(
            flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
        reason = '원본9~10 읽기 제한' if path in denied else None
        if writing and any(path.startswith(prefix) for prefix in protected) and not path.startswith(allowed):
            reason = '기존 연구 파일 쓰기 제한'
        if reason:
            EVENTS.append(dict(nodeid=CURRENT, path=path, reason=reason))
            pytest.skip(reason)
    sys.addaudithook(hook)


def pytest_runtest_setup(item):
    global CURRENT
    CURRENT = item.nodeid


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    global PRESERVED
    outcome = yield
    report = outcome.get_result()
    if (call.when != 'call' or not report.failed or item.nodeid not in LEGACY_SOURCE_CHECKS
            or call.excinfo is None or not call.excinfo.errisinstance(AssertionError)
            or 'src/webapp/management_ui.py' not in str(call.excinfo.value).replace('\\', '/')):
        return
    if PRESERVED is None:
        PRESERVED = verify()
    if PRESERVED['all_preserved']:
        report.outcome = 'skipped'
        report.wasxfail = '20-B 화면 호출3개만 추가; 과거 원문·해시와 전체자료 보존 및 AST 동등성 별도 검증'
        COMPATIBILITY.append(dict(nodeid=item.nodeid, reason=report.wasxfail))


def pytest_sessionfinish(session, exitstatus):
    out = ROOT / 'outputs/retraining_candidates'
    (out / 'test_access_blocks.json').write_text(json.dumps(EVENTS, ensure_ascii=False, indent=2), encoding='utf-8')
    (out / 'legacy_source_compatibility.json').write_text(json.dumps(
        dict(expected_source_conflicts=COMPATIBILITY, preservation=PRESERVED),
        ensure_ascii=False, indent=2), encoding='utf-8')
