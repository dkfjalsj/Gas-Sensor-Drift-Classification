# 시기별 SVM 진단·조건부 결합 결과의 표와 그림 작성
# 기존 결과와 독립 Test의 차이 및 보호 기준 공개

import base64
import html
import json
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .data import ROOT, GASES
from .temporal_expansion import sha, write_json
from .temporal_svm_ensemble import OUT, REPORTS, FOLDS, CAUTION, ORACLE_NOTE


# 과거 실패 이름과 현재 전체 테스트 비교
def test_summary():
    path = OUT/'test_results.xml'
    if not path.exists():
        return {'status':'전체 테스트 실행 전'}
    old = ET.parse(ROOT/'outputs/nonlinear_feature_transformation/test_results.xml')
    old_failures = {(c.get('classname'), c.get('name')) for c in old.iter('testcase')
                    if c.find('failure') is not None or c.find('error') is not None}
    cases = list(ET.parse(path).iter('testcase'))
    failures = []
    for case in cases:
        failure = case.find('failure')
        if failure is None:
            failure = case.find('error')
        if failure is not None:
            key = (case.get('classname'), case.get('name'))
            failures.append(dict(classname=key[0], name=key[1], historical=key in old_failures,
                                 reason=failure.get('message', '')[:1500]))
    new = [c for c in cases if 'test_temporal_svm_ensemble' in c.get('classname', '')]
    result = dict(total=len(cases), passed=sum(c.find('failure') is None and c.find('error') is None
                                             and c.find('skipped') is None for c in cases),
                  failed=len(failures), historical_failures=sum(f['historical'] for f in failures),
                  new_failures=sum(not f['historical'] for f in failures),
                  new_tests=len(new), new_passed=sum(c.find('failure') is None and c.find('error') is None for c in new),
                  failures=failures)
    write_json(OUT/'test_summary.json', result)
    return result


# 그림에 평균 방식·평가 Batch·표본 수 표시
def render():
    def read(name):
        return pd.read_csv(OUT/f'{name}.csv')

    metrics, classes, summary = read('fold_metrics'), read('class_metrics'), read('summary')
    samples, audit = read('sample_complementarity'), read('expert_audit')
    gate = json.loads((OUT/'diagnostic_gate.json').read_text(encoding='utf-8'))
    conclusion = json.loads((OUT/'conclusion_frozen.json').read_text(encoding='utf-8'))
    statuses = read('ensemble_execution')
    models = [m for m in ['full', 'recent', 'spread', 'hard_equal', 'rank_equal'] if m in summary.model.tolist()]
    plt.rcParams.update({'font.family':'Malgun Gothic', 'axes.unicode_minus':False})
    figures = []
    label = '개발 Fold A: Batch6 n=2300 / B: Batch7 n=3613 / C: Batch8 n=294'

    def finish(name, title, fig, oracle=False):
        subtitle = '가상 Oracle: 정답을 알고 선택함. 배포 불가.' if oracle else label
        fig.suptitle(title+'\n'+subtitle, fontsize=11)
        fig.tight_layout(rect=(0, 0, 1, .94))
        path = OUT/f'{name}.png'
        fig.savefig(path, dpi=150)
        plt.close(fig)
        figures.append(dict(name=name, title=title, path=str(path.relative_to(ROOT)),
                            sha256=sha(path), oracle=oracle, axes_and_support_labelled=True))

    expert_summary = summary[summary.role == 'expert']
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(expert_summary.model, expert_summary.mean_macro_f1*100)
    ax.set(xlabel='시기별 전문가', ylabel='Fold 동일 가중 평균 Macro F1 (%)', ylim=(0, 100))
    for i, value in enumerate(expert_summary.mean_macro_f1):
        ax.text(i, value*100+1, f'{value*100:.2f}', ha='center')
    finish('expert_mean_macro', '전문가 단독 평균 성능', fig)
    fig, ax = plt.subplots(figsize=(10, 5))
    for name in models:
        sub = metrics[metrics.model == name]
        ax.plot(sub.fold, sub.macro_f1*100, marker='o', label=name)
    ax.set(xlabel='시간순 Fold (A→6, B→7, C→8)', ylabel='Macro F1 (%)', ylim=(0, 100))
    ax.legend()
    finish('fold_performance', 'Fold별 단독·실행된 결합 성능', fig)
    aggregate = samples.groupby('fold')[['all_correct', 'some_correct', 'all_wrong',
                                         'disagreement', 'identical_wrong']].mean()*100
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    aggregate[['all_correct', 'some_correct', 'all_wrong']].plot.bar(stacked=True, ax=axes[0])
    aggregate[['disagreement', 'identical_wrong']].plot.bar(ax=axes[1])
    for ax in axes:
        ax.set(xlabel='Validation Fold', ylabel='동일 표본 기준 비율 (%)', ylim=(0, 100))
        ax.tick_params(axis='x', rotation=0)
    finish('agreement_disagreement', '정답·오답 분해 및 예측 불일치 (오른쪽 비율은 상호 배타적 아님)', fig)
    by_gas = samples.groupby(['fold', 'y_true']).some_correct.mean().unstack()*100
    fig, ax = plt.subplots(figsize=(10, 4))
    by_gas.rename(columns=GASES).plot.bar(ax=ax)
    ax.set(xlabel='Validation Fold', ylabel='일부 전문가만 정답인 표본 비율 (%)')
    ax.tick_params(axis='x', rotation=0)
    finish('partial_correct', '가스별 실제 오류 상호 보완성', fig)
    fig, ax = plt.subplots(figsize=(10, 5))
    oracle_plot = summary[summary.model.isin(['full', 'recent', 'spread', 'oracle'])]
    ax.bar(oracle_plot.model, oracle_plot.mean_macro_f1*100)
    ax.set(xlabel='단독 전문가 / 정답 이용 고정 Oracle', ylabel='Fold 동일 가중 Macro F1 (%)', ylim=(0, 100))
    for i, value in enumerate(oracle_plot.mean_macro_f1):
        ax.text(i, value*100+1, f'{value*100:.2f}', ha='center')
    finish('oracle_macro', '단독 성능과 고정 Oracle의 가능성 진단', fig, True)
    mean_class = classes.groupby(['model', 'gas_id'])[['precision', 'recall', 'f1']].mean()
    fig, ax = plt.subplots(figsize=(12, 5))
    mean_class.recall.unstack(0).loc[:, ['full', 'recent', 'spread', 'oracle']].rename(index=GASES).mul(100).plot.bar(ax=ax)
    ax.set(xlabel='실제 가스', ylabel='Fold 동일 가중 Recall (%)', ylim=(0, 100))
    ax.tick_params(axis='x', rotation=20)
    finish('oracle_recall', '6종 가스 Oracle Recall과 단독 전문가', fig, True)
    focus_rows = []
    for (fold, gas), sub in samples[samples.y_true.isin([4, 6])].groupby(['fold', 'y_true']):
        focus_rows.append(dict(label=f'{fold}/{GASES[gas]} n={len(sub)}',
                               all_correct=sub.all_correct.sum(), some_correct=sub.some_correct.sum(),
                               all_wrong=sub.all_wrong.sum()))
    focus = pd.DataFrame(focus_rows).set_index('label')
    fig, ax = plt.subplots(figsize=(12, 5))
    focus.plot.bar(stacked=True, ax=ax)
    ax.set(xlabel='Validation Fold / 실제 가스 / support', ylabel='표본 수')
    ax.tick_params(axis='x', rotation=25)
    finish('focus_complementarity', 'Toluene·Acetaldehyde 공동 정답·일부 정답·공동 오답', fig)
    for delta in [False, True]:
        pivot = classes[classes.model.isin(models)].pivot(index=['model', 'fold'], columns='gas_id', values='recall')
        pivot = pivot.reindex(pd.MultiIndex.from_product([models, list(FOLDS)]))
        if delta:
            pivot = pivot-pd.concat([pivot.loc['full']]*len(models), keys=models)
        fig, ax = plt.subplots(figsize=(11, max(6, len(pivot)*.35)))
        image = ax.imshow(pivot.to_numpy()*100, aspect='auto', cmap='RdBu_r' if delta else 'viridis',
                          vmin=-100 if delta else 0, vmax=100)
        ax.set_xticks(range(6), list(GASES.values()), rotation=20, ha='right')
        ax.set_yticks(range(len(pivot)), [f'{m}/{f}' for m, f in pivot.index])
        ax.set(xlabel='실제 가스', ylabel='전문가·결합 / Validation Fold')
        for i in range(len(pivot)):
            for j in range(6):
                ax.text(j, i, f'{pivot.iloc[i,j]*100:.1f}', ha='center', va='center', fontsize=7)
        fig.colorbar(image, ax=ax, label='Recall 증감 (%p)' if delta else 'Recall (%)')
        finish('recall_delta' if delta else 'recall_heatmap',
               '전체형 기준 Recall 증감' if delta else '6종 가스 Recall', fig)
    if statuses.executed.any():
        matrices = read('confusion')
        fig, axes = plt.subplots(len(models), 3, figsize=(16, len(models)*4), squeeze=False)
        for i, model in enumerate(models):
            for j, fold in enumerate(FOLDS):
                ax = axes[i, j]
                sub = matrices[(matrices.model == model) & (matrices.fold == fold)]
                matrix = sub.pivot(index='true_gas', columns='predicted_gas', values='n').to_numpy()
                ax.imshow(matrix, cmap='Blues')
                ax.set(title=f'{model}/{fold} Batch{FOLDS[fold][1]} n={matrix.sum()}',
                       xlabel='예측 가스 번호', ylabel='실제 가스 번호')
                ax.set_xticks(range(6), list(GASES))
                ax.set_yticks(range(6), list(GASES))
                for a in range(6):
                    for b in range(6):
                        ax.text(b, a, str(matrix[a, b]), ha='center', va='center', fontsize=7,
                                color='white' if matrix[a, b] > matrix.max()/2 else 'black')
        finish('confusion_matrices', '단독·결합 Confusion Matrix (동일 Validation 표본)', fig)
        fig, ax = plt.subplots(figsize=(11, 5))
        metrics[metrics.model.isin(models)].groupby('model')[['toluene_to_acetaldehyde', 'acetaldehyde_to_toluene']].sum().reindex(models).plot.bar(ax=ax)
        ax.set(xlabel='전문가·실행된 결합', ylabel='Fold 6·7·8 오분류 수 합계')
        ax.tick_params(axis='x', rotation=10)
        finish('directional_errors', 'Toluene ↔ Acetaldehyde 오분류 방향', fig)
    pd.DataFrame(figures).to_csv(OUT/'graph_manifest.csv', index=False, encoding='utf-8')
    mean_class.reset_index().to_csv(OUT/'mean_class_metrics.csv', index=False, encoding='utf-8')
    support_summary = samples.groupby('fold').agg(
        n=('row_id','size'), all_correct=('all_correct','sum'), some_correct=('some_correct','sum'),
        all_wrong=('all_wrong','sum'), disagreement=('disagreement','sum'), identical_wrong=('identical_wrong','sum'))
    support_summary.to_csv(OUT/'complementarity_summary.csv', encoding='utf-8')
    focus_summary = samples[samples.y_true.isin([4, 6])].groupby(['fold', 'y_true']).agg(
        support=('row_id','size'), full_correct=('full_correct','sum'), recent_correct=('recent_correct','sum'),
        spread_correct=('spread_correct','sum'), some_correct=('some_correct','sum'),
        all_wrong=('all_wrong','sum'), oracle_rescue=('oracle_rescue','sum'))
    focus_summary.to_csv(OUT/'focus_complementarity.csv', encoding='utf-8')
    tests = test_summary()
    code = conclusion['conclusion']
    verdict = {'A':'균형 개선 근거 관찰', 'B':'부분 개선', 'C':'개선 근거 부족'}[code]
    fold_table = metrics.pivot(index='model', columns='fold', values='macro_f1').mul(100)
    observations = [
        f'연구 결론 {code} — {verdict}. 공식 Model A 유지.',
        f'전문가 평가 {conclusion["expert_evaluations"]}건, 기존 모델 재사용 {conclusion["reused_models"]}개, '
        f'신규 SVC 학습 {conclusion["new_svc_fits"]}회, 조건부 결합 평가 {conclusion["ensemble_evaluations"]}건.',
        f'게이트 통과={gate["passed"]}. Oracle 평균 Macro F1과 최고 단독 평균의 차이 '
        f'{gate["oracle_macro_gain"]*100:+.2f}%p. Oracle은 실현 가능한 성능이 아님.',
        '동일 표본에서 일부 전문가만 정답인 경우만 오류 상호 보완성으로 계산함. '
        '예측 불일치만으로 개선 가능성을 선언하지 않음.',
        '단독 최고 대비 결합의 추가 가치는 above_best_single 열로 별도 공개. '
        '기준 대비 개선이 곧 앙상블 필요성의 증거는 아님.',
        '전체형과 부분표본형은 학습량·클래스 구성·balanced 벌점·전처리도 달라짐. '
        '최근형과 분산형은 같은 843개·가스별 수로 대조하되 순수 시기 인과 효과는 아님.',
        '시드42는 기본값으로 사전 고정했고 성능으로 고르지 않음. '
        '한 시드의 재사용 진단이므로 부분표본 선택 불확실성을 평가하지 못함.',
        '각 전문가가 6종을 학습해도 Fold A의 Toluene 초기 자료 부족은 남음. '
        'Fold C Toluene 18개는 Recall 한 표본이5.56pp이며 결과 과대 해석 금지.',
        'SVM OVR 점수는 모델 내부 클래스 순위만 이용. predict는 OVO 투표에 기반하므로 '
        'OVR argmax와 다른 표본 수를 audit에 기록. 확률 해석·raw 점수 평균 없음.',
        '8단계 이종 모델 결합과 다른 연구 질문. 과거 Hard Voting의 실패만으로 '
        '시기별 결합을 미리 기각하지 않고 사전 게이트로 검토함.',
    ]
    if 'A' in focus_summary.index.get_level_values(0):
        tol = focus_summary.loc[('A', 6)]
        observations.append(f'Fold A Toluene support={int(tol.support)}, 정답 수 full/recent/spread='
                            f'{int(tol.full_correct)}/{int(tol.recent_correct)}/{int(tol.spread_correct)}, '
                            f'공동 오답={int(tol.all_wrong)}. 이 결과만으로 다른 시기 앙상블의 보편적 효용을 단정하지 않음.')
    for row in summary[summary.role == 'ensemble'].itertuples():
        observations.append(f'{row.model}: 평균 Macro F1 {row.mean_macro_f1*100:.2f}%, '
                            f'기준 대비{row.macro_delta*100:+.2f}pp, 최고 단독 대비{row.above_best_single*100:+.2f}pp, '
                            f'보호 조건 전부 통과={row.balanced_success}, 최악 Fold 변화{row.worst_fold_delta*100:+.2f}pp, '
                            f'Recall0 조합{row.zero_pairs}, 신규0 조합{row.new_zero_pairs}.')
    observations.append('다음 연구는 새 실험 전에 별도 계획 고정 필요. Oracle과 실제 결합의 격차가 크면 '
                        '현재 결합 규칙의 한계를 뜻하나, 사후 가스별 가중치나 미래 결과로 규칙을 수정하지 않음.')
    limitation_text = ('# 15단계 한계\n\n'+CAUTION+'\n\n'+ORACLE_NOTE+'\n\n'+'\n\n'.join('- '+x for x in observations[5:10])+
        '\n\n- 새 시기의 농도·환경·세션·정확한 측정 시각 정보 부족. 드리프트 단독 원인이나 개선의 인과 효과 미확정.\n'+
        '- 진단과 결합 평가에 같은 과거 Validation을 사용한 조건부 탐색. 사전 계획이 역사적 선택 편향을 제거하지 못함.\n'+
        '- 기존 5개 테스트 실패는 과거 소스 SHA, 누락 임시 파일 후보, 전역 모델 목록 고정 충돌3건. 기준 미수정.\n'+
        '- 모든 실패·미실행을 기록하고 독립 미래 일반화·산업 안전성·통계적 유의성 미주장. Commit·Push 없음.\n')
    summary_text = ('# 15단계 시기별 SVM 진단·결합 요약\n\n'+CAUTION+'\n\n'+'\n\n'.join('- '+x for x in observations)+
        '\n\n```text\n'+fold_table.to_string(float_format=lambda x:f'{x:.2f}')+'\n```\n\n```text\n'+summary.to_string(index=False)+
        '\n```\n\n```text\n'+focus_summary.to_string()+'\n```\n\n'+ORACLE_NOTE+'\n\n테스트:\n```json\n'+json.dumps(tests, ensure_ascii=False, indent=2)+'\n```\n')
    (ROOT/'reports'/REPORTS[1]).write_text(summary_text, encoding='utf-8')
    (ROOT/'reports'/REPORTS[2]).write_text(limitation_text, encoding='utf-8')
    sections = []
    def section(title, content):
        sections.append('<h2>'+html.escape(title)+'</h2>'+content)
    section('1. 연구 목적·공식 기준 유지', '<p>'+CAUTION+'</p><p>시기별 SVM의 실제 오류 상호 보완성 진단 후 조건부 결합.</p>')
    section('2. 사전 계획·전문가 구성', '<pre>'+html.escape((OUT/'experiment_plan.json').read_text(encoding='utf-8'))+'</pre>'+
            read('expert_plan').to_html(index=False)+read('class_batch_support').to_html(index=False))
    section('3. 단독·조건부 결합 성능', '<p>숫자는 계산 결과이며 독립 Test 점수가 아님.</p>'+fold_table.to_html()+summary.to_html(index=False))
    section('4. 동일 표본의 정답·오답 상호 보완성', support_summary.to_html()+read('pairwise_complementarity').to_html(index=False))
    section('5. Oracle와 사전 게이트', '<p>'+ORACLE_NOTE+'</p><pre>'+html.escape(json.dumps(gate, ensure_ascii=False, indent=2))+'</pre>')
    section('6. Toluene·Acetaldehyde 상세', focus_summary.to_html()+mean_class.reset_index().to_html(index=False))
    section('7. 결합 실행 여부·보호 기준', statuses.to_html(index=False)+summary[summary.role == 'ensemble'].to_html(index=False))
    section('8. 계산 결과 시각화', '<p>가스 번호 '+html.escape(str(GASES))+'</p>'+''.join(
        '<figure><img alt="'+html.escape(f['title'])+'" src="data:image/png;base64,'+
        base64.b64encode((ROOT/f['path']).read_bytes()).decode('ascii')+'"><figcaption>'+html.escape(f['title'])+
        (' — '+ORACLE_NOTE if f['oracle'] else '')+'</figcaption></figure>' for f in figures))
    section('9. 모델·전처리·예측 재현 감사', audit.to_html(index=False)+read('pooled_metrics').to_html(index=False))
    section('10. 관찰과 해석·다음 연구', '<ul>'+''.join('<li>'+html.escape(x)+'</li>' for x in observations)+'</ul><pre>'+html.escape(limitation_text)+'</pre>')
    section('11. 보존·테스트·재현 방법', '<pre>'+html.escape(json.dumps(tests, ensure_ascii=False, indent=2))+'</pre>'+
            '<p>preservation_audit.csv에 기존 파일과 원본의 해시 검사 기록. 과거 기록·기준 미수정.</p>'+
            '<p>프로젝트 루트에서 python -m src.temporal_svm_ensemble freeze → run → 전체 pytest → report. '
            '출력 경로가 이미 존재하면 재실행 학습·진단 명령은 덮어쓰기를 거부함.</p>')
    document = ('<!doctype html><html lang="ko"><meta charset="utf-8"><title>15단계 시기별 SVM 앙상블</title>'+
        '<style>body{font-family:Malgun Gothic,sans-serif;margin:32px;color:#172536}table{border-collapse:collapse;display:block;overflow:auto;font-size:13px}'
        'td,th{border:1px solid #bbc;padding:6px}img{max-width:100%;height:auto}pre{white-space:pre-wrap;overflow-wrap:anywhere}h2{margin-top:36px}</style>'+
        '<body><h1>시기별 SVM 오류 상호 보완성 및 조건부 결합</h1>'+''.join(sections)+'</body></html>')
    (ROOT/'reports'/REPORTS[0]).write_text(document, encoding='utf-8')
