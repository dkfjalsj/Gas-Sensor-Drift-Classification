# 옛 보고서·캐시를 지문 확인 후 일시 복원해 전체 테스트 실행
# 결과와 의도된 소스 확장 호환성을 따로 집계

from datetime import datetime, timezone
import json
import os
import subprocess
import xml.etree.ElementTree as ET

from ..data import ROOT
from ..research_maintenance.publication_archive import legacy_test_documents, records
from ..research_maintenance.publication import checked_path, sha
from .candidates import json_bytes

OUT = ROOT / 'outputs/retraining_candidates'


# 강제 중단으로 남은 테스트용 복원본만 지문 확인 후 정리
def recover_interrupted_restore():
    state_path = OUT / 'test_execution.json'
    if not state_path.exists():
        return
    state = json.loads(state_path.read_text(encoding='utf-8'))
    if state.get('finished'):
        return
    restored_path = OUT / 'legacy_restored.json'
    names = json.loads(restored_path.read_text(encoding='utf-8'))['paths']
    archive = {row['path']: row for row in records()}
    removed = []
    for name in names:
        path = checked_path(name)
        if name not in archive:
            raise ValueError('복원 목록에 없는 파일은 정리하지 않음')
        if path.exists():
            if path.is_symlink() or sha(path.read_bytes()) != archive[name]['sha256']:
                raise ValueError('중단 이후 달라진 복원 파일은 정리하지 않음: ' + name)
            path.unlink()
            removed.append(name)
    (OUT / 'interruption_recovery.json').write_bytes(json_bytes(dict(
        previous_execution=state, restored_files_removed=removed)))
    log = OUT / 'full_tests.txt'
    if log.exists():
        (OUT / 'interrupted_full_tests.txt').write_bytes(log.read_bytes())


def main():
    recover_interrupted_restore()
    env = os.environ.copy()
    env.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
               MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
    state = dict(started_at_utc=datetime.now(timezone.utc).isoformat(), finished=False)
    (OUT / 'test_execution.json').write_bytes(json_bytes(state))
    with legacy_test_documents() as restored:
        (OUT / 'legacy_restored.json').write_bytes(json_bytes(dict(paths=restored)))
        with (OUT / 'full_tests.txt').open('w', encoding='utf-8') as stream:
            result = subprocess.run([
                str(ROOT / '.venv/Scripts/python.exe'), '-B', '-X', 'utf8', '-m',
                'pytest', 'tests', '-q', '--tb=line', '-p', 'src.retraining.testing_guard',
                '-p', 'no:cacheprovider', '--junitxml=outputs/retraining_candidates/full_tests.xml',
            ], cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
    cases = list(ET.parse(OUT / 'full_tests.xml').iter('testcase'))
    known = {'tests.test_diagnostics::test_existing_results_and_models_unchanged',
             'tests.test_temporal_failure_diagnostics::test_no_new_fit_calls_or_new_model_files'}
    failures = [dict(name=case.attrib['classname'] + '::' + case.attrib['name'],
                     message=case.find('failure').attrib.get('message', ''))
                for case in cases if case.find('failure') is not None]
    expected = [case for case in cases if case.find('skipped') is not None
                and case.find('skipped').attrib.get('type') == 'pytest.xfail']
    summary = dict(total=len(cases), passed=sum(not any(case.find(tag) is not None
        for tag in ['failure', 'skipped', 'error']) for case in cases), failed=len(failures),
        errors=sum(case.find('error') is not None for case in cases),
        restricted_skips=sum(case.find('skipped') is not None for case in cases) - len(expected),
        source_compatibility_xfails=len(expected),
        historical_failures=[row for row in failures if row['name'] in known],
        new_failures=[row for row in failures if row['name'] not in known])
    (OUT / 'test_summary.json').write_bytes(json_bytes(summary))
    state.update(finished=True, finished_at_utc=datetime.now(timezone.utc).isoformat(),
                 returncode=result.returncode, restored_documents_removed=True)
    (OUT / 'test_execution.json').write_bytes(json_bytes(state))
    print(summary)


if __name__ == '__main__':
    main()
