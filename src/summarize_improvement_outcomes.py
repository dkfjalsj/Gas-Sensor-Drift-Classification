# 고정된 후보의 실제 성과와 실패 한계를 보고서에 명시
# 모델·선정·예측을 변경하지 않고 설명만 추가

import hashlib
import json
from pathlib import Path

import pandas as pd

from .data import ROOT


# Test 결과의 기술적 해석 추가 및 선정 파일 보존 확인
def main():
    out = ROOT / 'outputs' / 'model_improvement'
    decision_path = out / 'validation_decisions.json'
    decision_before = hashlib.sha256(decision_path.read_bytes()).hexdigest()
    decision = json.loads(decision_path.read_text(encoding='utf-8'))
    selected = decision['joint_candidates']
    delta = pd.read_csv(out / 'improvement_deltas.csv').set_index('trial_id')
    classes = pd.read_csv(out / 'per_class_metrics.csv')
    remarks = [
        '관찰: 이번 실험은 안정적인 미래 6종 분류라는 목표를 달성하지 못했다. '
        'Validation으로 고정한 후보는 유지하지만 운영 적합성을 확인한 모델은 아니다.',
        '세 공동 후보 모두 Validation Acetaldehyde 87개와 Test Acetaldehyde 1,797개에서 '
        'Recall 0%였다. Train/Validation에 클래스가 존재하는 것과 잘 분류하는 것은 다르다.',
    ]
    for trial in selected:
        row = delta.loc[trial]
        remarks.append(
            f'{trial}: Test Toluene Recall {row.test_toluene_recall:.2%}, '
            f'Toluene F1 {row.test_toluene_f1:.2%}. 동일 strict 기본 모델 대비 '
            f'macro-F1 {100 * row.macro_f1_delta_vs_strict_base:+.2f}pp, '
            f'Toluene Recall {100 * row.toluene_recall_delta_vs_strict_base:+.2f}pp, '
            f'다른 5종 평균 F1 {100 * row.other_five_delta_vs_strict_base:+.2f}pp.'
        )
    remarks.extend([
        'LR의 RobustScaler는 전체 Test macro-F1을 높였지만 같은 Train의 기본 LR보다 '
        'Toluene Recall은 낮았다. SVM C=10은 Toluene Recall이 늘었지만 다른 5종 평균 F1이 '
        '약 5.33pp 낮아졌다. RF의 Validation 선택 설정도 미래 Test에서 일관된 개선을 보이지 못했다.',
        '이 관찰은 사후 설명이며 Test에 맞춰 설정을 조정하거나 후보를 재선정하지 않았다. '
        'Toluene Validation 4개, 단일 Validation Batch, 초기 시기에 제한된 Train으로는 '
        '미래 안정성을 충분히 검증할 수 없다.',
    ])
    # 명시한 클래스별 실패를 실제 표에서 대조
    failed = classes[
        classes.trial_id.isin(selected)
        & (classes.scope == 'pooled')
        & (classes.gas == 'Acetaldehyde')
    ]
    if len(failed) != 6 or not failed.recall.eq(0).all():
        raise ValueError('Outcome note does not match saved class metrics')
    report = ROOT / 'reports' / 'model_improvement_report.html'
    text = report.read_text(encoding='utf-8')
    marker = '<!-- outcome-review -->'
    if marker in text:
        raise FileExistsError('Outcome interpretation already added')
    needle = '<h2>9. 공동 후보 선정 근거와 검증 한계</h2>'
    if needle not in text:
        raise ValueError('Expected report section missing')
    addition = marker + ''.join('<p><b>' + note + '</b></p>' for note in remarks)
    text = text.replace(needle, needle + addition, 1)
    if text.count('<section>') != 10:
        raise ValueError('Report section count changed')
    report.write_text(text, encoding='utf-8')
    rationale = ROOT / 'reports' / 'model_selection_rationale.md'
    rationale.write_text(
        rationale.read_text(encoding='utf-8') + '\n## 실제 성과 및 후보 유지의 의미\n\n'
        + '\n\n'.join(remarks) + '\n', encoding='utf-8'
    )
    if hashlib.sha256(decision_path.read_bytes()).hexdigest() != decision_before:
        raise RuntimeError('Validation decision changed')
    audit = dict(
        interpretation_only=True, decision_unchanged=True, decision_sha256=decision_before,
        code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        metrics_sha256=hashlib.sha256((out / 'improvement_deltas.csv').read_bytes()).hexdigest(),
        report_sha256=hashlib.sha256(report.read_bytes()).hexdigest(),
        rationale_sha256=hashlib.sha256(rationale.read_bytes()).hexdigest(),
    )
    (out / 'outcome_interpretation_audit.json').write_text(
        json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    print('Outcome notes verified; frozen candidates and all predictions unchanged')


if __name__ == '__main__':
    main()
