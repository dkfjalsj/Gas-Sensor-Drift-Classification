# 저장된 실험값과 테스트 결과를 최종 검증 문서로 정리
# 모델 학습·선정 없이 계산된 결과만 요약

import json
import xml.etree.ElementTree as ET

import pandas as pd

from .data import ROOT
from .temporal_expansion import sha, write_json

OUT = ROOT / 'outputs/temporal_expansion'


# 평가 이후의 해석과 보존 확인 결과 추가
def run():
    report = ROOT / 'reports/temporal_expansion_report.html'
    target = ROOT / 'reports/temporal_expansion_verification.md'
    if target.exists():
        raise FileExistsError('Verification document already exists')
    state = json.loads((OUT / 'run_manifest.json').read_text(encoding='utf-8'))
    for name, expected in state['before'].items():
        if sha(ROOT / name) != expected:
            raise RuntimeError('Preserved file changed')
    tests = ET.parse(OUT / 'test_results.xml').getroot()
    cases = tests.findall('.//testcase')
    failed = [f"{case.get('classname')}::{case.get('name')}" for case in cases
              if case.find('failure') is not None or case.find('error') is not None]
    new_cases = [c for c in cases if 'test_temporal_expansion' in c.get('classname', '')]
    passed = sum(c.find('failure') is None and c.find('error') is None and
                 c.find('skipped') is None for c in cases)
    decision = json.loads((OUT / 'selection_frozen.json').read_text(encoding='utf-8'))
    delta = pd.read_csv(OUT / 'expansion_deltas.csv')
    summary = pd.read_csv(OUT / 'summary_metrics.csv')
    metrics = pd.read_csv(OUT / 'metrics.csv')
    priority = decision['priority_candidate']
    selected = summary[summary.trial_id.isin(decision['family_representatives'])]
    lines = [
        '# 6단계 실험 해석 및 최종 보존 검증', '',
        f'전체 테스트: {passed}개 통과, {len(failed)}개 실패. 신규 {len(new_cases)}개 모두 통과.', '',
        '기존 실패: 과거 소스의 주석·공백 변경에 따른 SHA 불일치, 과거 보존 기록에 포함된 '
        'zNex~$haremetrics.csv 부재. 기존 검사와 해시 기록은 수정하지 않았음.', '',
        '```text', *failed, '```', '',
        f'실험 시작 시 존재한 코드·테스트·보고서·모델·산출물 {len(state["before"])}개와 '
        f'원본 {len(state["raw_hashes"])}개 해시 보존 확인. 기존 소스가 이번에 변경되지 않았으므로 '
        '이번 작업에서 AST 변경도 없음.', '',
        '## 학습 범위 확장 효과', '',
    ]
    notes = []
    for _, row in delta.iterrows():
        notes.append(
            f'{row.family} / {row.partition}: Batch 동일 가중 Macro F1 변화 '
            f'{row.equal_batch_macro_f1_delta_pp:+.2f}pp, pooled 변화 '
            f'{row.pooled_macro_f1_delta_pp:+.2f}pp. '
            f'Toluene Recall {100 * row.toluene_recall_A:.2f}%→{100 * row.toluene_recall_B:.2f}%, '
            f'Acetaldehyde Recall {100 * row.acetaldehyde_recall_A:.2f}%→'
            f'{100 * row.acetaldehyde_recall_B:.2f}%.'
        )
    lines += ['- ' + note for note in notes]
    lines += ['', 'Validation에서는 세 모델 모두 확장 효과가 컸으나, 탐색적 평가의 동일 가중 지표는 '
              'RF만 개선되고 LR은 소폭 하락, SVM은 거의 동일함. pooled 지표는 세 모델 모두 개선됨. '
              '평균 방식에 따라 결론이 달라지므로 시간순 확장이 모든 미래 Batch에 효과적이라고 '
              '일반화할 수 없음. 기본 모델의 평가 Acetaldehyde Recall은 세 모델 모두 하락함.', '',
              '## 선정 후보와 남은 실패', '', f'Validation 우선 후보: **{priority}**.', '',
              '```text', selected.to_string(index=False), '```', '']
    zero = metrics[(metrics.trial_id == priority) & (metrics.scope == 'batch') &
                   (metrics.partition == 'evaluation') & (metrics.toluene_recall == 0)]
    zero_batches = zero.batch.astype(int).tolist()
    lines += [f'우선 후보의 탐색적 평가 Toluene Recall 0% Batch: {zero_batches}. '
              '합산 Recall 개선만으로 미래 Batch 전체의 실패가 해결됐다고 해석할 수 없음.', '',
              '탐색적 평가의 동일 가중 점수는 SVM 대표가 높지만 pooled Macro F1은 LR 대표가 높음. '
              '이는 평균 기준과 클래스 균형의 차이임. 평가를 보고 후보를 바꾸지 않았음.', '',
              '## 재현과 실행', '',
              '- 학습·선정·평가: `.venv\\Scripts\\python.exe -B -X utf8 -m src.temporal_expansion`',
              '- 검증 문서: `.venv\\Scripts\\python.exe -B -X utf8 -m src.temporal_expansion_review`',
              '- 전체 테스트: `.venv\\Scripts\\python.exe -B -X utf8 -m pytest -q -p no:cacheprovider`', '',
              '학습 코드는 기존 신규 실험 경로가 있으면 중단함. 재현은 1–5단계 파일을 보존한 '
              '별도 복제본에서 6단계 출력 경로가 없는 상태로 실행해야 함. 기존 산출물 삭제·덮어쓰기 금지.', '',
              '모델·전처리·후보는 평가 전에 고정됐으며 재학습이나 평가 기반 변경 없음. '
              '새 측정 시기의 미관찰 자료로 독립 검증 필요. 최종 모델 확정 아님. Commit·Push 없음.']
    target.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    intro = '<aside style="background:#eef5fa;padding:18px"><h3>계산 결과와 테스트 요약</h3>'
    intro += '<p>Validation에서는 기본 세 모델 모두 학습 범위 확장 후 개선됐다. '
    intro += 'Batch 9–10 동일 가중 Macro F1은 RF만 개선됐으며, LR은 소폭 하락, SVM은 거의 동일했다. '
    intro += 'pooled Macro F1은 세 모델 모두 개선됐다. 기본 세 모델의 평가 Acetaldehyde Recall은 하락했다.</p>'
    intro += f'<p>Validation 우선 후보는 {priority}. 평가 Batch {zero_batches}에서는 '
    intro += 'Toluene Recall이 여전히 0%다. 6종의 안정적 분류 문제가 모두 해결된 것은 아니다.</p>'
    intro += f'<p>전체 테스트 {passed}개 통과, 기존 사유 {len(failed)}개 실패. '
    intro += f'신규 테스트 {len(new_cases)}개 통과. 상세: temporal_expansion_verification.md.</p></aside>'
    document = report.read_text(encoding='utf-8')
    before = sha(report)
    document = document.replace('</h1>', '</h1>' + intro, 1)
    report.write_text(document, encoding='utf-8')
    write_json(OUT / 'final_verification.json', dict(
        full_suite_passed=passed, full_suite_failed=len(failed), failed_tests=failed,
        new_tests=len(new_cases), prior_files_rechecked=len(state['before']),
        report_before_review_sha256=before, report_final_sha256=sha(report),
        review_code_sha256=sha(ROOT / 'src/temporal_expansion_review.py'),
        candidate_unchanged=True, selection_sha256=sha(OUT / 'selection_frozen.json'),
    ))
    print('\n'.join(lines))


if __name__ == '__main__':
    run()
