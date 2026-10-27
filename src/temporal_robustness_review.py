# 고정된 실험 결과와 테스트 실패 사유를 최종 문서에 반영
# 탐색적 평가 이후 모델·후보·가중치 변경 없음

import html
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

from .data import ROOT, load_dataset, read_config
from .temporal_expansion import sha, write_json

OUT = ROOT / 'outputs/temporal_robustness'


# 계산값의 개선 여부와 과거 검사 충돌을 구분해 기록
def run():
    if (OUT / 'final_verification.json').exists():
        raise FileExistsError('Review already exists')
    manifest = json.loads((OUT / 'run_manifest.json').read_text(encoding='utf-8'))
    for name, expected in manifest['before'].items():
        if sha(ROOT / name) != expected:
            raise RuntimeError('Existing file changed')
    _, source = load_dataset(read_config())
    assert dict(zip(source.file, source.sha256)) == manifest['raw_hashes']
    decision_path = OUT / 'selection_frozen.json'
    selection_hash = sha(decision_path)
    decision = json.loads(decision_path.read_text(encoding='utf-8'))
    chosen = decision['selected_candidate']
    cv = pd.read_csv(OUT / 'cv_summary.csv').set_index('config_id')
    summary = pd.read_csv(OUT / 'evaluation_summary.csv').set_index('config_id')
    classes = pd.read_csv(OUT / 'evaluation_class_metrics.csv', dtype={'fold': str})
    choice = cv.loc[chosen]
    baseline = cv.loc['SVM_all']
    choice_eval = summary.loc[chosen]
    base_eval = summary.loc['stage6_saved_SVM']
    facts = [
        '18개 단일 설정과4개 결합 설정, 총22개 설정 비교. 3Fold에서 분류기54회 Fit. '
        '앙상블은 저장 구성 모델을 사용하며 추가 분류기 Fit 없음.',
        f'과거 Fold 후보는 {chosen}: 동일 가중 Macro F1 '
        f'{100 * choice.mean_macro_f1:.2f}%, 기준 SVM '
        f'{100 * baseline.mean_macro_f1:.2f}% 대비 '
        f'{100 * (choice.mean_macro_f1 - baseline.mean_macro_f1):+.2f}pp. '
        'LR_variance(115), RF_all(128), SVM_variance(115)의 Hard Voting이다.',
        f'SVM 저분산13개 제거의 Fold 평균 변화는 '
        f'{100 * (cv.loc["SVM_variance"].mean_macro_f1 - baseline.mean_macro_f1):+.2f}pp. '
        '상관 제거·안정성64·KBest32/64는 SVM 평균을 낮췄다. 특징 선택의 보편적 개선은 확인되지 않았다.',
        f'후보의 탐색적 동일 가중 Macro F1 '
        f'{100 * choice_eval.equal_batch_macro_f1:.2f}% vs 기존 '
        f'{100 * base_eval.equal_batch_macro_f1:.2f}% '
        f'({choice_eval.equal_macro_delta_pp:+.2f}pp). 합산 Macro F1은 '
        f'{100 * choice_eval.pooled_macro_f1:.2f}% vs '
        f'{100 * base_eval.pooled_macro_f1:.2f}% '
        f'({choice_eval.pooled_macro_delta_pp:+.2f}pp). 평균 기준에 따라 평가가 달라진다.',
        '후보는 Fold A Toluene Recall0%를 해결하지 못했다. '
        '탐색적 Batch 9 Toluene도0%이며, Batch 10 Acetaldehyde Recall은14%→4.5%로 악화됐다. '
        'Batch 10 Acetone Recall은31.67%→71.17%로 개선됐지만 일부 가스의 손실을 동반했다.',
        f'합산 Toluene Recall은 {100 * base_eval.pooled_toluene_recall:.2f}%→'
        f'{100 * choice_eval.pooled_toluene_recall:.2f}%, Acetaldehyde는 '
        f'{100 * base_eval.pooled_acetaldehyde_recall:.2f}%→'
        f'{100 * choice_eval.pooled_acetaldehyde_recall:.2f}%. '
        '이번 후보를 균형 잡힌 미래 성능 개선 모델로 확정하거나 기존 SVM의 대체 모델로 권고할 근거는 부족하다.',
        'SVM_variance의 탐색적 동일 가중 Macro F1은61.13%였지만, '
        '평가 결과로 후보를 이 설정으로 바꾸지 않았다. 후보·특징·가중치는 동결 상태를 유지했다.',
        'LR_correlation은 과거 Fold에서 Recall0 조합이 없었지만 평균76.78%로 '
        '81.39% 후보보다 낮았다. 0% 회피와 평균 성능 간 절충은 다음 실험에서 '
        '평가 전에 운영 기준으로 정할 문제이며 이번 결과를 보고 재선정하지 않았다.',
    ]
    cases = ET.parse(OUT / 'test_results.xml').getroot().findall('.//testcase')
    failed = [f"{c.get('classname')}::{c.get('name')}" for c in cases
              if c.find('failure') is not None or c.find('error') is not None]
    passed = sum(c.find('failure') is None and c.find('error') is None and
                 c.find('skipped') is None for c in cases)
    new_cases = [c for c in cases if c.get('classname', '').endswith('test_temporal_robustness')]
    if any(c.find('failure') is not None or c.find('error') is not None for c in new_cases):
        raise RuntimeError('New tests failed')
    expected_failures = {
        'tests.test_diagnostics::test_existing_results_and_models_unchanged',
        'tests.test_models::test_eda_and_sources_preserved_report_complete',
        'tests.test_temporal_failure_diagnostics::test_no_new_fit_calls_or_new_model_files',
    }
    if set(failed) != expected_failures:
        raise RuntimeError('Unexpected test failure')
    old_models = {name for name in manifest['before'] if name.endswith('.joblib')}
    actual_models = {str(p.relative_to(ROOT)) for p in (ROOT / 'models').rglob('*.joblib')}
    new_models = actual_models - old_models
    assert all((ROOT / name).is_relative_to(ROOT / 'models/temporal_robustness') for name in new_models)
    test_note = (
        f'전체 테스트 {passed}개 통과·{len(failed)}개 실패. 신규 {len(new_cases)}개 모두 통과. '
        '기존 실패2건은 과거 소스 SHA 불일치와 과거 보존 기록의 임시 파일 후보 부재. '
        '추가1건은7단계의 프로젝트 전체 모델 목록 고정 검사로, 이번에 승인된 신규 모델 추가에 따른 '
        '검사 범위 충돌이다. 기존 연구 모델·파일의 변경이나 신규 코드 테스트 실패가 아니다. '
        '과거 테스트·해시 기록은 수정하지 않았다.'
    )
    preservation = (f'기존 파일 {len(manifest["before"])}개와 원본10개 해시 보존, '
                    f'기존 모델 {len(old_models)}개 보존 및 신규 모델 파일 {len(new_models)}개 별도 저장 확인. '
                    '66개 Fold 설정 예측(단일54+결합12)과 평가23개 설정 예측의 재현 검사 통과. '
                    '기존 저장 SVM과 새 SVM_all의 평가 예측 일치. '
                    'Train 외 전처리·특징 선택 Fit 없음. 모델 파일은 Git 제외 상태이며 Commit·Push 없음.')
    report_path = ROOT / 'reports/temporal_robustness_improvement_report.html'
    report_before = sha(report_path)
    doc = report_path.read_text(encoding='utf-8')
    aside = '<aside style="background:#eef5fa;padding:18px"><h3>실험 결론과 검증 결과</h3><ul>'
    aside += ''.join('<li>' + html.escape(fact) + '</li>' for fact in facts)
    aside += '</ul><p>' + html.escape(test_note) + '</p><p>' + html.escape(preservation) + '</p></aside>'
    report_path.write_text(doc.replace('</h1>', '</h1>' + aside, 1), encoding='utf-8')
    selection_path = ROOT / 'reports/temporal_robustness_model_selection.md'
    with selection_path.open('a', encoding='utf-8') as stream:
        stream.write('\n## 최종 관찰과 판단\n\n' + '\n\n'.join('- ' + fact for fact in facts))
        stream.write('\n\n## 후보·기존 SVM의 Batch별6종 Recall\n\n```text\n')
        stream.write(classes[classes.config_id.isin([chosen, 'stage6_saved_SVM'])][
            ['config_id', 'fold', 'gas', 'support', 'recall', 'f1']].to_string(index=False))
        stream.write('\n```\n\n## 테스트·보존 검증\n\n' + test_note + '\n\n' + preservation + '\n\n')
        stream.write('```text\n' + '\n'.join(failed) + '\n```\n\n')
        stream.write('다음 우선순위는 새로운 시기·농도·환경 자료 확보와 시간순 중첩 검증임. '
                     '공통0% 실패를 다수결만으로 해결할 수 없으며, 평가에서 좋아 보인 특징·모델을 '
                     '사후 채택하지 않을 것. 무정답 Batch 평균 보정도 운영 시점과 참조 자료 조건을 '
                     '사전에 정의해야 함.\n\n')
        stream.write('테스트 후 문서 보완 재현: '
                     '`.venv\\Scripts\\python.exe -B -X utf8 -m src.temporal_robustness_review`\n')
    assert sha(decision_path) == selection_hash
    for name, expected in manifest['before'].items():
        assert sha(ROOT / name) == expected
    write_json(OUT / 'final_verification.json', dict(
        full_suite_passed=passed, full_suite_failed=len(failed), new_tests=len(new_cases),
        failed_tests=failed, preexisting_failures=2, historical_inventory_conflict=1,
        new_code_test_failures=0, prior_files_unchanged=len(manifest['before']),
        old_models_preserved=len(old_models), new_model_files=len(new_models),
        selection_sha256=selection_hash, candidate_unchanged_after_evaluation=True,
        report_before_review_sha256=report_before, report_final_sha256=sha(report_path),
        selection_document_sha256=sha(selection_path), review_code_sha256=sha(Path(__file__)),
    ))
    print('\n'.join(facts) + '\n' + test_note + '\n' + preservation)


if __name__ == '__main__':
    run()
