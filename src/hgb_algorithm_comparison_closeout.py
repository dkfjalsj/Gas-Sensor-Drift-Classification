# 16단계 계산값·전체 테스트·보존 결과를 최종 보고서에 반영
# 저장된 표만 사용하며 추가 학습·평가·튜닝 없음

import html
import json

import pandas as pd

from .data import ROOT
from .temporal_expansion import now
from .hgb_algorithm_comparison import OUT, REPORTS, verify, write
from .hgb_algorithm_comparison_report import render, test_summary


# 관찰된 손실과 해석의 범위를 구분하여 정리
def main():
    render()
    tests = test_summary()
    summary = pd.read_csv(OUT/'summary.csv').set_index('model')
    metrics = pd.read_csv(OUT/'fold_metrics.csv')
    classes = pd.read_csv(OUT/'class_metrics.csv')
    agreement = pd.read_csv(OUT/'error_agreement.csv')
    directional = pd.read_csv(OUT/'focus_error_directions.csv')
    decision = json.loads((OUT/'conclusion_frozen.json').read_text(encoding='utf-8'))
    delta = pd.read_csv(OUT/'class_deltas.csv')
    for col in ['precision','recall','f1']:
        delta[col+'_delta_pp'] = delta[col]*100
    delta[['gas_id','gas','precision_delta_pp','recall_delta_pp','f1_delta_pp']].to_csv(
        OUT/'class_delta_percentages.csv',index=False,encoding='utf-8')
    only_svm = int(agreement.svm_only.sum())
    only_hgb = int(agreement.hgb_only.sum())
    common_wrong = int(agreement.both_wrong.sum())
    hgb_ac_b = classes[(classes.model == 'HGB')&(classes.fold == 'B')&(classes.gas_id == 4)].iloc[0]
    hgb_et_c = classes[(classes.model == 'HGB')&(classes.fold == 'C')&(classes.gas_id == 2)].iloc[0]
    b_dirs = directional[(directional.fold == 'B')&(directional.true_gas == 4)].set_index('model')
    notes = [
        f'계산 결과: HGB 평균 Macro F1 {summary.loc["HGB","mean_macro_f1"]*100:.2f}% 대 '
        f'SVM {summary.loc["SVM","mean_macro_f1"]*100:.2f}%, '
        f'차이{decision["mean_macro_delta"]*100:+.2f}pp. 세 Fold 모두 HGB가 낮음.',
        '가스별 Fold 평균 F1은6종 모두 하락. 일부 Precision·Recall 향상만으로 B로 판정하지 않는 '
        '사전 규칙에 따라 C(개선 근거 부족). 새 우수 후보 없음. 공식 Model A 유지.',
        'Fold A Toluene467개는 HGB·SVM 모두 정답0개. HGB는448개를 Acetaldehyde로 '
        '오분류해 기준416개보다 증가. 새로운 알고리즘도 이 공동 실패를 해결하지 못함.',
        f'Fold B Acetaldehyde: HGB 정답{int(round(hgb_ac_b.recall*hgb_ac_b.support))}/'
        f'{int(hgb_ac_b.support)}개, Recall{hgb_ac_b.recall*100:.2f}%. '
        f'Toluene 오분류는{int(b_dirs.loc["SVM","target_pair"])}→{int(b_dirs.loc["HGB","target_pair"])}개로 '
        f'줄었지만 기타 가스 오분류는{int(b_dirs.loc["SVM","other_wrong"])}→{int(b_dirs.loc["HGB","other_wrong"])}개로 증가. '
        '오류 방향 감소를 정분류 개선으로 해석하면 안 됨.',
        f'Fold C Ethylene: HGB 정답{int(round(hgb_et_c.recall*hgb_et_c.support))}/'
        f'{int(hgb_et_c.support)}개, Recall{hgb_et_c.recall*100:.2f}%. '
        '새로운0% 조합은 없지만 거의 실패하는 가스가 있어0% 개수만으로 안정성을 판단할 수 없음.',
        f'다른 네 가스 평균 F1 변화{decision["other_four_f1_delta"]*100:+.2f}pp. '
        'Acetone 평균 Recall은 상승했지만 Precision 손실과 함께 평균 F1은 하락. '
        '초점 가스만 보지 않고6종 전체의 손익을 공개함.',
        f'오류 구조: 두 모델 공동 오답{common_wrong}개, SVM만 정답{only_svm}개, '
        f'HGB만 정답{only_hgb}개. 합산 표본 수는 크기가 다른 개발 Batch의 합이며 '
        '동일 Fold 가중 평균과 구분. 상호 보완성이 있어도 앙상블 이득을 보장하지 않으며 이번에는 결합 미실행.',
        f'학습 비용: HGB3회 총{summary.loc["HGB","fit_seconds"]:.2f}초. '
        'SVM 학습0초는 저장 모델 재사용을 뜻하며 SVM 자체 학습 비용이0이라는 뜻이 아님. '
        '단회 추론 시간은 환경·캐시·표본 수에 의존하므로 일반적인 속도 우월성을 주장하지 않음.',
        '해석: 이번 고정 기본 설정 HGB는 현재 시간순 개발 과제에서 기준보다 불리함. '
        'HGB의 최적 성능 상한, 모든 부스팅 알고리즘의 무효, 드리프트 단독 원인 또는 과적합 원인을 입증한 것은 아님.',
        '후속 검토가 필요하면 별도 계획·작은 예산·시간순 검증을 사전에 정해야 함. '
        '현재 결과로 즉석 튜닝이나 SVM·HGB 결합을 추가하지 않음. 새로운 시기의 독립 자료 확보가 여전히 중요함.',
        f'전체 테스트 {tests.get("passed")}개 통과 / {tests.get("failed")}개 실패. '
        f'기존 실패{tests.get("historical_failures")}개, 신규 실패{tests.get("new_failures")}개, '
        f'신규 검사{tests.get("new_passed")}/{tests.get("new_tests")}개 통과.',
    ]
    text = '\n## 계산 결과의 상세 해석\n\n'+'\n\n'.join('- '+s for s in notes)+'\n'
    (OUT/'closeout_observations.md').write_text(text,encoding='utf-8')
    path = ROOT/'reports'/REPORTS[1]
    path.write_text(path.read_text(encoding='utf-8')+text,encoding='utf-8')
    path = ROOT/'reports'/REPORTS[0]
    section = '<h2>12. 계산 결과의 상세 해석</h2><ul>'+''.join('<li>'+html.escape(s)+'</li>' for s in notes)+'</ul>'
    path.write_text(path.read_text(encoding='utf-8').replace('</body>',section+'</body>'),encoding='utf-8')
    result = verify()
    result.update(completed_at=now(), tests=tests, new_HGB_fits=3, reused_SVM=3, fallback_SVM_fits=0,
                  ensemble_executed=False, future_batches_evaluated=[], official_model='Model A unchanged',
                  previous_source_ast='All existing Python bytes unchanged; same AST',
                  visual_review='Recall heatmap and focus-error graphs inspected; Korean labels readable',
                  commit=False,push=False)
    write('final_verification.json',result)
    print(json.dumps(tests,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
