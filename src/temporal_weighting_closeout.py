# 그래프 교정 후 최종 테스트·보존 결과와 재현 순서 기록
# 초기 검증 기록을 덮어쓰지 않고 새 최종 감사 파일 생성

import json
import xml.etree.ElementTree as ET

from .data import ROOT, load_dataset, read_config
from .temporal_expansion import sha, write_json, now

OUT = ROOT / 'outputs/temporal_weighting'


# 변경 없는 모델과 교정된 표시의 최종 상태 확인
def run():
    if (OUT / 'final_audit.json').exists():
        raise FileExistsError('Final audit already exists')
    state = json.loads((OUT / 'run_manifest.json').read_text(encoding='utf-8'))
    correction = json.loads((OUT / 'plot_order_correction.json').read_text(encoding='utf-8'))
    for name, expected in state['before'].items():
        assert sha(ROOT / name) == expected
    _, source = load_dataset(read_config())
    assert dict(zip(source.file, source.sha256)) == state['raw_hashes']
    assert sha(OUT / 'selection_frozen.json') == correction['frozen_selection_sha256']
    assert sha(ROOT / 'reports/temporal_weighting_report.html') == correction['report_current_sha256']
    cases = ET.parse(OUT / 'test_results_final.xml').getroot().findall('.//testcase')
    failed = [f"{case.get('classname')}::{case.get('name')}" for case in cases
              if case.find('failure') is not None or case.find('error') is not None]
    expected = {
        'tests.test_diagnostics::test_existing_results_and_models_unchanged',
        'tests.test_models::test_eda_and_sources_preserved_report_complete',
        'tests.test_temporal_failure_diagnostics::test_no_new_fit_calls_or_new_model_files',
    }
    assert set(failed) == expected
    passed = sum(case.find('failure') is None and case.find('error') is None and
                 case.find('skipped') is None for case in cases)
    new_cases = [case for case in cases if 'test_temporal_weighting' in case.get('classname', '')]
    assert all(case.find('failure') is None and case.find('error') is None for case in new_cases)
    text = f'''# 9단계 최종 테스트·보존 검증

최종 전체 테스트: **{passed}개 통과, {len(failed)}개 실패**. 신규 테스트 **{len(new_cases)}개 모두 통과**.
최신 결과: outputs/temporal_weighting/tests_final.txt 및 test_results_final.xml.
보고서 본문의76개 통과·신규10개 통과는 그래프 검증을 추가하기 전의 초기 전체 검사 기록이다.
초기 기록은 tests.txt·test_results.xml·final_verification.json에 그대로 보존한다.

## 실패의 구분
- 과거 소스 주석·공백 변경에 따른 SHA-256 불일치.
- 과거 보존 목록의 zNex~$haremetrics.csv 부재.
- 7단계 프로젝트 전체 모델 목록 고정 검사와 승인된 신규 모델 추가의 충돌.
기존 테스트·과거 해시 기준을 수정하거나 누락 파일을 생성하지 않았다. 신규 코드 실패는 없다.

## 보존과 그래프 교정
기존 파일{len(state['before'])}개와 원본10개 해시를 최종 재확인했다.
모델·가중치·후보·지표·예측은 그래프 교정 전후 동일하다.
새9단계 선그래프의 Batch 문자열 정렬을 숫자 정렬로 바로잡았다.
교정 전 HTML·선정 문서·PNG는 snapshot으로 남기고, 초기 해시 기록은 덮어쓰지 않았다.
현재 보고서·PNG의 기준은 plot_order_correction.json, 마지막 감사는 final_audit.json이다.
추가 테스트는 plot_coordinates.csv의 숫자9·10과 지표 CSV의 대응을 검사한다.

기존8단계 exploratory_batch_scores.png에서도 동일한 표시 순서 문제를 확인했다.
8단계 원본 파일은 보존 조건에 따라 수정하지 않았다. 당시 CSV·표의 수치와 모델은 변하지 않았으며,
현재9단계 비교는 해당 수치 CSV를 올바른 Batch에 대응시켜 사용했다.

## 전체 재현 순서
1–8단계 산출물을 보존한 별도 복제본에서9단계 출력 경로가 없는 상태로 실행한다.
초기 전체 검사는 아직 생성되지 않은 교정 기록을 요구하는 그래프 검사만 제외한다.
문서 보완·교정 이후의 마지막 전체 검사에는 그래프 검사까지 모두 포함한다.

```text
.venv\\Scripts\\python.exe -B -X utf8 -m src.temporal_weighting
.venv\\Scripts\\python.exe -B -X utf8 -m pytest -q -p no:cacheprovider --ignore=tests/test_temporal_weighting_plot.py --junitxml=outputs/temporal_weighting/test_results.xml
.venv\\Scripts\\python.exe -B -X utf8 -m src.temporal_weighting_review
.venv\\Scripts\\python.exe -B -X utf8 -m src.temporal_weighting_plot_review
.venv\\Scripts\\python.exe -B -X utf8 -m pytest -q -p no:cacheprovider --junitxml=outputs/temporal_weighting/test_results_final.xml
.venv\\Scripts\\python.exe -B -X utf8 -m src.temporal_weighting_closeout
```

기존3건 실패는 예상된 과거 검사 충돌로 남는다. 출력 경로가 있으면 코드가 중단하므로
기존 산출물을 삭제·덮어쓰기하지 말고 복제본에서 재현해야 한다.
최초 실행에서는 위의 초기 그래프 검사 제외가 필요하며, 최종 전체 검사에서 제외되는 검사는 없다.
Commit·Push 없음. 주 후보는 기존6단계 SVM 유지, Train1–7은 별도 확장 비교이며 사후 재선정하지 않았다.
'''
    document = ROOT / 'reports/temporal_weighting_final_verification.md'
    document.write_text(text, encoding='utf-8')
    write_json(OUT / 'final_audit.json', dict(
        completed_at_seoul=now(), full_suite_passed=passed, full_suite_failed=len(failed),
        failed_tests=failed, new_tests=len(new_cases), new_failures=0,
        prior_files_unchanged=len(state['before']), raw_files_unchanged=10,
        frozen_selection_sha256=sha(OUT / 'selection_frozen.json'),
        current_report_sha256=sha(ROOT / 'reports/temporal_weighting_report.html'),
        current_selection_doc_sha256=sha(ROOT / 'reports/temporal_weighting_model_selection.md'),
        initial_verification_sha256=sha(OUT / 'final_verification.json'),
        plot_correction_sha256=sha(OUT / 'plot_order_correction.json'),
        closeout_document_sha256=sha(document), closeout_source_sha256=sha(ROOT / 'src/temporal_weighting_closeout.py'),
        initial_test_records_preserved=True, model_or_prediction_changes=False,
    ))
    print(text)


if __name__ == '__main__':
    run()
