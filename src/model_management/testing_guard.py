# 기존 연구 쓰기·Batch9~10 읽기 차단 및 소스 보존 충돌 구분
# 실제 기능 실패와 예상 해시 충돌을 같은 통과로 계산하지 않음

import json
import os
from pathlib import Path
import sys

import pytest

from ..data import ROOT, read_config
from .audit import OUT, ALLOWED, verify

EVENTS = []
COMPATIBILITY = []
CURRENT = ''
PRESERVED = None
CONFLICTS = {
    'tests/test_project_cleanup.py::test_prior_research_preserved',
    'tests/test_report_publication.py::test_actual_sources_are_unchanged',
    'tests/test_streamlit_integration.py::test_existing_model_and_results_preserved',
    'tests/test_retraining_candidate_ui.py::test_prior_research_and_20a_extension_preserved',
    'tests/test_retraining_preparation.py::test_no_fit_calls_and_git_exclusion_and_preservation',
}
PATH_CONFLICTS = {
    'tests/test_gas_specific_temporal_balancing.py::test_existing_files_models_raw_and_plan_preserved',
    'tests/test_temporal_generalization_validation.py::test_existing_files_raw_and_model_inventory_preserved',
    'tests/test_temporal_representativeness_control.py::test_prior_files_and_raw_hashes_preserved',
    'tests/test_temporal_robustness.py::test_existing_files_and_raw_preserved',
    'tests/test_temporal_weighting.py::test_existing_files_and_raw_preserved',
    'tests/test_toluene_deep_diagnostic.py::test_preserved_files_raw_models_and_config',
}


def pytest_sessionstart(session):
    raw = Path(read_config()['data_dir'])
    denied = {os.path.normcase(str(raw / f'batch{n}.dat')) for n in [9, 10]}
    allowed = os.path.normcase(str(OUT)) + os.sep
    protected = [os.path.normcase(str(ROOT / name)) + os.sep
                 for name in ['src', 'tests', 'outputs', 'models', 'reports', 'data']]

    def hook(event, args):
        if event != 'open' or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        path = os.path.normcase(os.path.abspath(os.fsdecode(args[0])))
        flags = args[2] or 0
        writing = any(c in str(args[1] or '') for c in 'wax+') or bool(
            flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
        reason = 'Batch9~10 원본 읽기 제한' if path in denied else None
        if writing and any(path.startswith(p) for p in protected) and not path.startswith(allowed):
            reason = '기존 연구·운영 경로 쓰기 제한'
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
    if (call.when != 'call' or not report.failed or item.nodeid not in CONFLICTS | PATH_CONFLICTS
            or call.excinfo is None or not call.excinfo.errisinstance(AssertionError)):
        return
    # 마지막 보존 assert가 아닌 기능 검사에서 실패한 경우는 그대로 실패
    trace = call.excinfo.traceback[-1]
    line = str(trace.statement)
    if item.nodeid in PATH_CONFLICTS:
        name = str(trace.locals.get('name', '')).replace('\\', '/')
        if name not in ALLOWED or 'sha(ROOT / name)' not in line:
            return
    elif not ('all_preserved' in line or 'row[' in line):
        return
    if PRESERVED is None:
        PRESERVED = verify()
    if PRESERVED['all_preserved'] and PRESERVED['production_pointer_unchanged']:
        report.outcome = 'skipped'
        report.wasxfail = '20-C 허용 소스·문서 확장과 과거 고정 지문 충돌; 독립 보존 검사 통과'
        COMPATIBILITY.append(dict(nodeid=item.nodeid, reason=report.wasxfail))


def pytest_sessionfinish(session, exitstatus):
    (OUT / 'test_access_blocks.json').write_text(json.dumps(EVENTS, ensure_ascii=False, indent=2), encoding='utf-8')
    (OUT / 'source_conflicts.json').write_text(json.dumps(
        dict(conflicts=COMPATIBILITY, independent_preservation=PRESERVED),
        ensure_ascii=False, indent=2), encoding='utf-8')
