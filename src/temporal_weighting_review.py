# 가중치 효과와 학습 범위 효과를 분리한 최종 해석·검증 기록
# 후보 동결 이후 모델·가중치·선정 기준 변경 없음

import html
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

from .data import ROOT, GASES, load_dataset, read_config
from .temporal_expansion import sha, write_json

OUT = ROOT / 'outputs/temporal_weighting'


# 저장 지표만으로 범위별 가중치 차이와 최종 검증 정리
def run():
    if (OUT / 'final_verification.json').exists():
        raise FileExistsError('Final review already exists')
    state = json.loads((OUT / 'run_manifest.json').read_text(encoding='utf-8'))
    for name, expected in state['before'].items():
        if sha(ROOT / name) != expected:
            raise RuntimeError('Preserved file changed')
    frame, source = load_dataset(read_config())
    assert dict(zip(source.file, source.sha256)) == state['raw_hashes']
    decision_path = OUT / 'selection_frozen.json'
    selection_hash = sha(decision_path)
    decision = json.loads(decision_path.read_text(encoding='utf-8'))
    cv = pd.read_csv(OUT / 'cv_summary.csv').set_index('config_id')
    evaluation = pd.read_csv(OUT / 'evaluation_metrics.csv', dtype={'fold': str})
    eval_classes = pd.read_csv(OUT / 'evaluation_classes.csv', dtype={'fold': str})
    summary = pd.read_csv(OUT / 'evaluation_summary.csv').set_index('model_id')
    range8 = pd.read_csv(OUT / 'range_batch8_metrics.csv', dtype={'fold': str})
    range8_classes = pd.read_csv(OUT / 'range_batch8_classes.csv', dtype={'fold': str})
    within_range = []
    for end in [6, 7]:
        base = summary.loc[f'train{end}_class_balanced']
        for model_id, row in summary[summary.train_end == end].iterrows():
            within_range.append(dict(
                model_id=model_id, train_end=end,
                equal_macro_delta_pp=100 * (row.equal_batch_macro_f1 - base.equal_batch_macro_f1),
                pooled_macro_delta_pp=100 * (row.pooled_macro_f1 - base.pooled_macro_f1),
                toluene_recall_delta_pp=100 * (row.pooled_toluene_recall - base.pooled_toluene_recall),
                acetaldehyde_recall_delta_pp=100 * (row.pooled_acetaldehyde_recall - base.pooled_acetaldehyde_recall),
                other_four_f1_delta_pp=100 * (row.other_four_f1 - base.other_four_f1),
            ))
    pd.DataFrame(within_range).to_csv(OUT / 'weight_effects_within_range.csv', index=False, encoding='utf-8')
    range_rows = []
    for scope in ['8', '9', '10', 'pooled']:
        if scope == '8':
            a = range8[(range8.config_id == 'class_balanced') & (range8.fold == '6')].iloc[0]
            b = range8[(range8.config_id == 'class_balanced') & (range8.fold == '7')].iloc[0]
            class_a = range8_classes[(range8_classes.config_id == 'class_balanced') & (range8_classes.fold == '6')]
            class_b = range8_classes[(range8_classes.config_id == 'class_balanced') & (range8_classes.fold == '7')]
        else:
            a = evaluation[(evaluation.config_id == 'train6_class_balanced') & (evaluation.fold == scope)].iloc[0]
            b = evaluation[(evaluation.config_id == 'train7_class_balanced') & (evaluation.fold == scope)].iloc[0]
            class_a = eval_classes[(eval_classes.config_id == 'train6_class_balanced') & (eval_classes.fold == scope)]
            class_b = eval_classes[(eval_classes.config_id == 'train7_class_balanced') & (eval_classes.fold == scope)]
        row = dict(scope=scope, n=int(a.n), macro_train6=a.macro_f1, macro_train7=b.macro_f1,
                   macro_delta_pp=100 * (b.macro_f1 - a.macro_f1),
                   other_four_f1_train6=a.other_four_f1, other_four_f1_train7=b.other_four_f1)
        for gas in GASES:
            row[f'class{gas}_recall_train6'] = float(class_a[class_a.gas_id == gas].recall.iloc[0])
            row[f'class{gas}_recall_train7'] = float(class_b[class_b.gas_id == gas].recall.iloc[0])
        range_rows.append(row)
    ranges = pd.DataFrame(range_rows)
    ranges.to_csv(OUT / 'baseline_range_effects.csv', index=False, encoding='utf-8')
    support_rows = []
    for end in [6, 7]:
        train = frame[frame.batch <= end]
        for gas in GASES:
            sub = train[train.gas == gas]
            support_rows.append(dict(train_end=end, gas_id=gas, gas=GASES[gas], n=len(sub),
                                     train_n=len(train), observed_gas_batches=str(sorted(sub.batch.unique().tolist())),
                                     batch6_n=int((sub.batch == 6).sum()),
                                     batch6_fraction=float((sub.batch == 6).mean())))
    supports = pd.DataFrame(support_rows)
    supports.to_csv(OUT / 'training_range_class_support.csv', index=False, encoding='utf-8')
    predictions = pd.read_csv(OUT / 'evaluation_predictions.csv.gz')
    controls = []
    for end in [6, 7]:
        a = predictions[predictions.config_id == f'train{end}_class_balanced'].sort_values('row_id')
        b = predictions[predictions.config_id == f'train{end}_class_sample'].sort_values('row_id')
        controls.append(dict(train_end=end, n=len(a), different_predictions=int((a.y_pred.to_numpy() != b.y_pred.to_numpy()).sum())))
    pd.DataFrame(controls).to_csv(OUT / 'equivalence_evaluation.csv', index=False, encoding='utf-8')
    baseline = cv.loc['class_balanced']
    best_id = cv.mean_macro_f1.idxmax()
    best = cv.loc[best_id]
    train6 = summary.loc['train6_class_balanced']
    train7 = summary.loc['train7_class_balanced']
    facts = [
        f'8개 SVM 가중치 설정을3Fold에서 비교해24회 학습. 평균점수 최고는 '
        f'{best_id} {100 * best.mean_macro_f1:.2f}%, 기준 '
        f'{100 * baseline.mean_macro_f1:.2f}% 대비 '
        f'{100 * (best.mean_macro_f1 - baseline.mean_macro_f1):+.2f}pp였다.',
        f'주 후보는 {decision["selected_scheme"]}. time_exp와 time_recent는 보호 기준을 통과했지만 '
        '기준도 최고 평균의0.5pp 이내에 포함됐다.0% 조합 수와 최소Recall이 같아 '
        '집중 가스 최소 평균Recall이 높은 기준 모델을 유지했다. '
        '“모든 개선 설정이 보호 검사에 실패했다”는 뜻은 아니다.',
        f'최근2Batch 가중치의 평균 Toluene Recall은 '
        f'{100 * baseline.mean_toluene_recall:.2f}%→{100 * cv.loc["time_recent"].mean_toluene_recall:.2f}%. '
        '모든 설정은 Fold A Toluene Recall0%를 해소하지 못했다.',
        f'가스·Batch 보정의 평균 Macro F1은 '
        f'{100 * cv.loc["gas_batch"].mean_macro_f1:.2f}%, 시간·셀 결합은 '
        f'{100 * cv.loc["time_gas_batch"].mean_macro_f1:.2f}%로 기준보다 낮았다. '
        '클래스 sample 가중치 대조는3Fold의6207개 예측이 기존 balanced와 모두 같았다.',
        f'기본 가중치 Train1–6→1–7의 공통Batch8 Macro F1은 '
        f'{100 * ranges.iloc[0].macro_train6:.2f}%→{100 * ranges.iloc[0].macro_train7:.2f}%. '
        'Batch8은 이미 개발 자료이고 Toluene18개이므로 이 구간만으로 안정적 개선을 결론 내릴 수 없다.',
        f'동일 기본 가중치의 별도 확장 비교에서9–10 동일 가중 Macro F1은 '
        f'{100 * train6.equal_batch_macro_f1:.2f}%→{100 * train7.equal_batch_macro_f1:.2f}% '
        f'({100 * (train7.equal_batch_macro_f1 - train6.equal_batch_macro_f1):+.2f}pp), '
        f'합산은 {100 * train6.pooled_macro_f1:.2f}%→{100 * train7.pooled_macro_f1:.2f}%. '
        '이는 가중치 최적화의 개선 효과가 아니라 학습 범위 비교 결과다.',
        f'확장 모델의 합산 Toluene Recall은 '
        f'{100 * train6.pooled_toluene_recall:.2f}%→{100 * train7.pooled_toluene_recall:.2f}%, '
        f'Acetaldehyde는 {100 * train6.pooled_acetaldehyde_recall:.2f}%→'
        f'{100 * train7.pooled_acetaldehyde_recall:.2f}%. '
        '하지만 Batch9 Toluene은1/101(0.99%)만 맞혀 실질적인 실패가 여전히 크다.',
        '확장 모델의 Batch10 Acetaldehyde Recall은14%→55.83%, Toluene은54%→79%였다. '
        '반면 합산 Ethanol Recall은80.79%→72.77%로 낮아졌고 '
        'Batch10 Acetone Recall도32.83%에 머물렀다. 모든 가스의 안정적 개선으로 보지 않는다.',
        'Train1–7에서 Toluene 표본은546→1114개, Acetaldehyde는484→1228개로 늘었다. '
        'Batch6 Toluene 집중도도85.53%→41.92%로 낮아졌다. '
        '표본 수·시기·가스 구성·기본 클래스 가중치가 함께 바뀌므로 원인을 데이터 양 하나로 분리할 수 없다.',
        '확장 모델은 후속 독립 검증 대상이다. 평가에서 더 좋아 보였다는 이유로 주 후보나 '
        '학습 범위·가중치를 사후 변경하지 않았다. 모든9–10 결과는 기존 Test 재사용의 '
        '회고적·탐색적 성능이며 최종 대체 모델의 확정 근거가 아니다.',
    ]
    cases = ET.parse(OUT / 'test_results.xml').getroot().findall('.//testcase')
    failed = [f"{case.get('classname')}::{case.get('name')}" for case in cases
              if case.find('failure') is not None or case.find('error') is not None]
    passed = sum(case.find('failure') is None and case.find('error') is None and
                 case.find('skipped') is None for case in cases)
    expected_failed = {
        'tests.test_diagnostics::test_existing_results_and_models_unchanged',
        'tests.test_models::test_eda_and_sources_preserved_report_complete',
        'tests.test_temporal_failure_diagnostics::test_no_new_fit_calls_or_new_model_files',
    }
    assert set(failed) == expected_failed
    new_cases = [c for c in cases if c.get('classname', '').endswith('test_temporal_weighting')]
    assert all(c.find('failure') is None and c.find('error') is None for c in new_cases)
    old_models = {name for name in state['before'] if name.endswith('.joblib')}
    actual_models = {str(p.relative_to(ROOT)) for p in (ROOT / 'models').rglob('*.joblib')}
    new_models = actual_models - old_models
    assert all((ROOT / name).is_relative_to(ROOT / 'models/temporal_weighting') for name in new_models)
    test_note = (
        f'전체 테스트 {passed}개 통과·{len(failed)}개 실패. 신규10개 모두 통과. 기존3건은 '
        '과거 소스 SHA 불일치, 과거 보존 기록의 임시 파일 후보 부재, '
        '7단계 전체 모델 목록 고정 검사와 승인된 신규 모델 추가의 충돌이다. '
        '기존 검사·해시를 수정하거나 누락 파일을 생성하지 않았다. 신규 코드 테스트 실패 없음.'
    )
    preserve_note = (
        f'기존 파일 {len(state["before"])}개·원본10개·기존 모델{len(old_models)}개 해시 보존 확인. '
        f'새 모델 파일{len(new_models)}개를 별도 경로에 저장했다. 전처리는 무가중Train만 Fit, '
        '가중치는 Train 클래스·Batch만으로 산정했다. 기존SVM·8단계Hard Voting 예측 재현, '
        '유효가중치 평균1·class×sample 중복 방지·분할 중복 검사 통과. Commit·Push 없음.'
    )
    report_path = ROOT / 'reports/temporal_weighting_report.html'
    before_report = sha(report_path)
    doc = report_path.read_text(encoding='utf-8')
    aside = '<aside style="background:#eef5fa;padding:18px"><h3>계산 결과와 최종 판단</h3><ul>'
    aside += ''.join('<li>' + html.escape(fact) + '</li>' for fact in facts)
    aside += '</ul><p>' + html.escape(test_note) + '</p><p>' + html.escape(preserve_note) + '</p>'
    aside += '<p>가중치 그래프의 점은 실제 존재한 가스·Batch만 표시한다. 점을 잇는 선은 '
    aside += '없는 가스 표본의 생성이나 시간 보간을 의미하지 않는다.</p></aside>'
    report_path.write_text(doc.replace('</h1>', '</h1>' + aside, 1), encoding='utf-8')
    selection_doc = ROOT / 'reports/temporal_weighting_model_selection.md'
    with selection_doc.open('a', encoding='utf-8') as stream:
        stream.write('\n## 최종 해석\n\n' + '\n\n'.join('- ' + fact for fact in facts))
        stream.write('\n\n## 가중치 효과와 확장 효과의 분리\n\n')
        stream.write('동일 Train 범위에서의 가중치 차이는 weight_effects_within_range.csv, '
                     '고정 기본 설정의 범위 차이는 baseline_range_effects.csv 참조.\n\n')
        stream.write('```text\n' + ranges.to_string(index=False) + '\n```\n\n')
        stream.write('```text\n' + supports.to_string(index=False) + '\n```\n\n')
        stream.write('## 다음 단계\n\n')
        stream.write('단순 시간·셀 가중치의 강도를 Test에 맞춰 더 탐색하지 않을 것. '
                     'Batch9 Toluene의 낮은 Recall과 다른 가스 손실을 운영 기준과 연결하고, '
                     '새 시기·농도·환경별 측정 자료 및 참조 측정을 확보해 고정 후보를 독립 검증할 것. '
                     'Train1–7 확장은 유망한 비교 결과이지만 이번 평가로 사후 채택하지 않음.\n\n')
        stream.write('## 테스트와 보존\n\n' + test_note + '\n\n' + preserve_note + '\n\n')
        stream.write('```text\n' + '\n'.join(failed) + '\n```\n\n')
        stream.write('테스트 후 문서 보완: '
                     '`.venv\\Scripts\\python.exe -B -X utf8 -m src.temporal_weighting_review`\n')
    assert sha(decision_path) == selection_hash
    for name, expected in state['before'].items():
        assert sha(ROOT / name) == expected
    write_json(OUT / 'final_verification.json', dict(
        full_suite_passed=passed, full_suite_failed=len(failed), failed_tests=failed,
        new_tests=len(new_cases), new_code_test_failures=0, existing_failure_count=3,
        old_files_preserved=len(state['before']), old_models_preserved=len(old_models), new_model_files=len(new_models),
        selection_sha256=selection_hash, candidate_unchanged_after_evaluation=True,
        report_before_review_sha256=before_report, report_final_sha256=sha(report_path),
        selection_document_sha256=sha(selection_doc), review_code_sha256=sha(Path(__file__)),
        independent_test=False,
    ))
    print('\n'.join(facts) + '\n' + test_note + '\n' + preserve_note)


if __name__ == '__main__':
    run()
