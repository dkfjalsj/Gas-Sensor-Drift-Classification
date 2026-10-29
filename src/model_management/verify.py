# 검증된 과거 원문을 일시 복원해 제한된 전체 테스트 실행
# 결과·접근 제한·기존 실패·신규 실패를 별도 저장

import os
import subprocess
import xml.etree.ElementTree as ET

from ..data import ROOT
from ..research_maintenance.publication_archive import legacy_test_documents
from ..retraining.candidates import json_bytes
from .audit import OUT, verify


def main():
    env = os.environ.copy()
    env.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
               PYTHONDONTWRITEBYTECODE='1')
    with legacy_test_documents() as names:
        (OUT / 'legacy_restored.json').write_bytes(json_bytes(names))
        with (OUT / 'full_tests.txt').open('w', encoding='utf-8') as stream:
            completed = subprocess.run([
                str(ROOT / '.venv/Scripts/python.exe'), '-B', '-X', 'utf8', '-m',
                'pytest', 'tests', '-q', '--tb=line', '-p', 'src.model_management.testing_guard',
                '-p', 'no:cacheprovider', '--junitxml=outputs/model_approval/full_tests.xml',
            ], cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
    cases = list(ET.parse(OUT / 'full_tests.xml').iter('testcase'))
    known = {'tests.test_diagnostics::test_existing_results_and_models_unchanged',
             'tests.test_temporal_failure_diagnostics::test_no_new_fit_calls_or_new_model_files'}
    failures = [dict(name=c.attrib['classname'] + '::' + c.attrib['name'],
                     message=c.find('failure').attrib.get('message', ''))
                for c in cases if c.find('failure') is not None]
    xfail = sum(c.find('skipped') is not None and c.find('skipped').attrib.get('type') == 'pytest.xfail'
                for c in cases)
    summary = dict(total=len(cases), passed=sum(not any(c.find(t) is not None
        for t in ['failure', 'error', 'skipped']) for c in cases), failed=len(failures),
        errors=sum(c.find('error') is not None for c in cases),
        restricted_skips=sum(c.find('skipped') is not None for c in cases) - xfail,
        source_compatibility_xfails=xfail,
        historical_failures=[f for f in failures if f['name'] in known],
        new_failures=[f for f in failures if f['name'] not in known],
        process_returncode=completed.returncode, restored_documents_removed=True)
    (OUT / 'test_summary.json').write_bytes(json_bytes(summary))
    (OUT / 'preservation_after.json').write_bytes(json_bytes(verify()))
    print(summary)


if __name__ == '__main__':
    main()
