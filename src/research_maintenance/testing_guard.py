# 과거 산출물 쓰기와 원본 Batch 9~10 분석 차단
# 제한된 테스트는 통과로 처리하지 않고 별도 기록

import json
import os
from pathlib import Path
import sys

from src.data import ROOT, read_config

EVENTS = []
CURRENT = ''


# 정리 결과 폴더 외 기존 연구 파일 쓰기 제한
def pytest_sessionstart(session):
    raw = Path(read_config()['data_dir'])
    denied = {os.path.normcase(str(raw / f'batch{b}.dat')) for b in [9, 10]}
    allowed = os.path.normcase(str(ROOT / 'outputs/project_cleanup')) + os.sep
    protected = [os.path.normcase(str(ROOT / name)) + os.sep for name in ['src', 'tests', 'outputs', 'models', 'reports', 'data']]

    def hook(event, args):
        if event != 'open' or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        path = os.path.normcase(os.path.abspath(os.fsdecode(args[0])))
        flags = args[2] or 0
        writing = any(char in str(args[1] or '') for char in 'wax+') or bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
        reason = '원본9~10 접근 제한' if path in denied else None
        if writing and any(path.startswith(prefix) for prefix in protected) and not path.startswith(allowed):
            reason = '과거 파일 쓰기 제한'
        if reason:
            EVENTS.append(dict(nodeid=CURRENT, path=path, reason=reason))
            import pytest
            pytest.skip('정리 단계 보존 검사: ' + reason)
    sys.addaudithook(hook)


def pytest_runtest_setup(item):
    global CURRENT
    CURRENT = item.nodeid


# 기존 실패·접근 제한과 신규 실패를 구분할 근거 저장
def pytest_sessionfinish(session, exitstatus):
    (ROOT / 'outputs/project_cleanup/test_access_blocks.json').write_text(
        json.dumps(EVENTS, ensure_ascii=False, indent=2), encoding='utf-8')
