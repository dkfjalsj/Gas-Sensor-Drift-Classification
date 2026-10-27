# 15단계 검사 결과·기술 오류 이력 및 계산된 핵심 관찰 정리
# 재학습·재평가 없이 저장된 CSV로 보고서 마무리

import html
import json

import pandas as pd

from .data import ROOT
from .temporal_expansion import now, write_json
from .temporal_svm_ensemble import OUT, REPORTS, verify
from .temporal_svm_ensemble_report import render, test_summary


# 계산된 사실과 연구 해석을 구분하여 공개
def main():
    render()
    tests = test_summary()
    samples = pd.read_csv(OUT/'sample_complementarity.csv')
    classes = pd.read_csv(OUT/'class_metrics.csv')
    prediction_counts = classes.groupby('model').predicted_n.sum()
    tol_predictions = classes[classes.gas_id == 6].groupby('model').predicted_n.sum()
    tol_precision = classes[classes.gas_id == 6].groupby('model').precision.mean()
    repair_records = [json.loads(p.read_text(encoding='utf-8')) for p in sorted(OUT.glob('technical_repair*.json'))]
    only = {k:int(v) for k, v in samples[[c for c in samples if c.endswith('_only_correct')]].sum().items()}
    details = dict(expert_configurations=9, ensemble_configurations=2,
                   conditional_ensemble_fold_evaluations=6, oracle_diagnostic_folds=3,
                   aborted_repeated_full_expert_validation=1,
                   total_expert_fold_evaluations_including_aborted_run=10,
                   reused_unique_models=9, new_expert_models_fitted_and_used=0,
                   technical_aborted_svc_fits=1, new_saved_models=0,
                   study_budget_note='One repeated full-expert diagnostic preceded the technical abort. '
                                     'No new expert/configuration or rule added; disclosed separately from9 unique evaluations.',
                   some_correct=int(samples.some_correct.sum()), all_wrong=int(samples.all_wrong.sum()),
                   disagreement=int(samples.disagreement.sum()), full_wrong_oracle_rescue=int(samples.oracle_rescue.sum()),
                   exclusive_correct=only, technical_repairs=repair_records)
    write_json(OUT/'execution_accounting.json', details)
    note = ('\n## 핵심 관찰 및 기술 실행 이력\n\n'
            f'- 동일 Validation 표본 총 {len(samples)}개 중 일부 전문가만 정답 {int(samples.some_correct.sum())}개, '
            f'공동 오답 {int(samples.all_wrong.sum())}개, 예측 불일치 {int(samples.disagreement.sum())}개. '
            '이 합산은 크기가 다른 개발 Batch를 합한 표본 수이며 주 선정 지표의 동일 Fold 평균과 구분함.\n'
            f'- 기준 full의 오답을 다른 전문가가 구제할 수 있는 표본은 {int(samples.oracle_rescue.sum())}개에 불과함. '
            f'반대로 full만 정답인 표본은 {only["full_only_correct"]}개. '
            '일부만 정답인 표본이 많아도 약한 전문가가 강한 전문가를 돕는 방향이라고 해석할 수 없음.\n'
            '- Fold A Toluene 467개는 세 전문가 모두 정답0개, 416개를 Acetaldehyde로 오분류. '
            '나머지51개의 예측은 전문가별로 다르지만 모두 오답. 단순 결합으로 해당 공동 실패를 구제하지 못함.\n'
            '- Fold B Toluene은 적어도 한 전문가가568개 전부를 맞혀 Oracle 여지가 있었으나, '
            '이는 정답을 아는 선택이며 실제 결합의 성능 보장이 아님.\n'
            '- 다수결·순위 결합 모두 전체형 기준보다 평균 Macro F1과 Toluene·Acetaldehyde 평균 Recall이 낮음. '
            '각 후보는 Macro F1·가스 Recall·나머지4종F1 보호 기준에 미달. 신규 Recall0 조합은 없으나 기존0도 해결 못함.\n'
            '- 사전 규칙상 일부 가스의 지표 향상이 있어 B(부분 개선)로 분류하지만, '
            '실질적인 평균·균형 개선 실패이며 새로운 우수 후보를 선정한 결과가 아님.\n'
            '- 학습량·클래스 구성 차이가 있는 843개 부분표본 전문가가 전체형보다 약했음. '
            '해당 고정 전문가·규칙의 결과이며 시기별 SVM 앙상블 전체의 무효를 입증한 것은 아님.\n'
            '- 기술 이력: sklearn1.9의 probability 기본값 deprecated를 False와 다르게 처리한 검사 오류로 '
            '불필요한 SVC 학습1회가 완료된 뒤 검사에서 중단됨. 해당 모델은 평가·저장·결합하지 않았음. '
            '중단 전에 full/Fold A의 재현 평가1회가 있어9개 고정 전문가 평가와 별도로 기록함.\n'
            '- 검사 호환성만 수정한 뒤9개 저장 전문가를 전부 재사용. 추가 학습0회. '
            '메타데이터 NumPy bool 저장 오류는 완료된 CSV에서 JSON·보고서만 재생성하여 처리함. '
            '계획·게이트·결합 규칙·계산 결과·과거 기록은 변경하지 않았음. '
            '이번 신규 코드 변경 전후 해시는 technical_repair.json과technical_repair_2.json에 보존함.\n'
            f'- 전체 테스트 {tests.get("passed")}개 통과 / {tests.get("failed")}개 실패. '
            f'신규 검사 {tests.get("new_passed")}/{tests.get("new_tests")} 통과, 신규 실패{tests.get("new_failures")}개.\n'
            '- 다음 연구는 강한 단독 모델을 약한 전문가가 압도하지 않는 구조가 필요한지 먼저 검토할 수 있으나, '
            '이번 Validation을 보고 가중치나 전문가를 사후 변경하지 않음. 독립 새 시기 자료 필요성은 여전함.\n')
    ratios = pd.DataFrame(dict(toluene_predicted_n=tol_predictions,
                               pooled_prediction_fraction=tol_predictions/prediction_counts,
                               equal_fold_toluene_precision=tol_precision))
    ratios.to_csv(OUT/'toluene_prediction_bias.csv', encoding='utf-8')
    note += '\n```text\n'+ratios.to_string()+'\n```\n'
    (OUT/'closeout_observations.md').write_text(note, encoding='utf-8')
    summary_path = ROOT/'reports'/REPORTS[1]
    summary_path.write_text(summary_path.read_text(encoding='utf-8')+note, encoding='utf-8')
    report_path = ROOT/'reports'/REPORTS[0]
    section = '<h2>12. 핵심 관찰·기술 실행 이력</h2><pre>'+html.escape(note)+'</pre>'
    report_path.write_text(report_path.read_text(encoding='utf-8').replace('</body>', section+'</body>'), encoding='utf-8')
    preservation = verify()
    preservation.update(completed_at=now(), tests=tests, execution_accounting=details,
                        source_ast='All pre-Stage15 Python source bytes preserved; original AST unchanged',
                        visual_review='Oracle and focus-complementarity graphs visually checked; Korean labels readable',
                        previous_failure_count=5, official_model='Model A unchanged',
                        future_batches_evaluated=[], commits=0, pushes=0)
    write_json(OUT/'final_verification.json', preservation)
    print(json.dumps(tests, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
