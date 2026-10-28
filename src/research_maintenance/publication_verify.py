# 보관 문서를 일시 복원해 기존 전체 테스트 실행
# 종료 후 열람용 HTML 하나만 남기고 신규 결과 별도 기록

from datetime import datetime, timezone
import json
import os
import subprocess
import xml.etree.ElementTree as ET

from ..data import ROOT
from .publication import OUT, save_json
from .publication_archive import legacy_test_documents


def main():
    env = os.environ.copy()
    env.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
               MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
    state = dict(started_at=datetime.now(timezone.utc).isoformat(),
                 finished=False, legacy_documents_temporarily_restored=True)
    save_json(OUT / 'test_execution.json', state)
    with legacy_test_documents() as restored:
        save_json(OUT / 'test_restoration.json', dict(paths=restored,
                                                    restored_count=len(restored)))
        with (OUT / 'tests.txt').open('w', encoding='utf-8') as stream:
            result = subprocess.run([
                str(ROOT / '.venv/Scripts/python.exe'), '-B', '-X', 'utf8',
                '-m', 'pytest', 'tests', '-q', '--tb=line',
                '-p', 'src.research_maintenance.publication_testing_guard',
                '-p', 'no:cacheprovider',
                '--junitxml=outputs/report_publication/tests.xml',
            ], cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
    cases = list(ET.parse(OUT / 'tests.xml').iter('testcase'))
    failures = [dict(name=case.attrib['classname'] + '::' + case.attrib['name'],
                     message=case.find('failure').attrib.get('message', ''))
                for case in cases if case.find('failure') is not None]
    baseline = {'tests.test_diagnostics::test_existing_results_and_models_unchanged',
                'tests.test_temporal_failure_diagnostics::test_no_new_fit_calls_or_new_model_files'}
    summary = dict(total=len(cases),
                   passed=sum(not any(case.find(tag) is not None for tag in ['failure', 'error', 'skipped']) for case in cases),
                   failed=len(failures),
                   skipped=sum(case.find('skipped') is not None for case in cases),
                   errors=sum(case.find('error') is not None for case in cases),
                   historical_failures=[row for row in failures if row['name'] in baseline],
                   new_failures=[row for row in failures if row['name'] not in baseline])
    save_json(OUT / 'test_summary.json', summary)
    state.update(finished=True, finished_at=datetime.now(timezone.utc).isoformat(),
                 returncode=result.returncode, temporary_documents_removed=True)
    save_json(OUT / 'test_execution.json', state)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
