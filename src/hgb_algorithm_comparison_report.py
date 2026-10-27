# HGB와 SVM의 동일 시간순 Fold 비교 결과 보고서 작성
# 가스별 손익·오류 상호 보완성·기존 실패 및 연구 한계 공개

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
from .temporal_expansion import sha
from .hgb_algorithm_comparison import OUT, REPORTS, FOLDS, CAUTION, HGB_PARAMS, write


# 기존 실패와 신규 실패 구분
def test_summary():
    if not (OUT/'test_results.xml').exists():
        return dict(status='전체 테스트 실행 전')
    old = ET.parse(ROOT/'outputs/temporal_svm_ensemble/test_results.xml')
    old_failures = {(c.get('classname'), c.get('name')) for c in old.iter('testcase')
                    if c.find('failure') is not None or c.find('error') is not None}
    cases = list(ET.parse(OUT/'test_results.xml').iter('testcase'))
    failures = []
    for c in cases:
        problem = c.find('failure')
        if problem is None:
            problem = c.find('error')
        if problem is not None:
            key = (c.get('classname'), c.get('name'))
            failures.append(dict(classname=key[0], name=key[1], historical=key in old_failures,
                                 reason=problem.get('message', '')[:1300]))
    new = [c for c in cases if 'test_hgb_algorithm_comparison' in c.get('classname', '')]
    results = dict(total=len(cases), passed=sum(c.find('failure') is None and c.find('error') is None
                                               and c.find('skipped') is None for c in cases),
                   failed=len(failures), historical_failures=sum(f['historical'] for f in failures),
                   new_failures=sum(not f['historical'] for f in failures), new_tests=len(new),
                   new_passed=sum(c.find('failure') is None and c.find('error') is None for c in new), failures=failures)
    write('test_summary.json', results)
    return results


# 고정된 표와 실제 예측으로만 그래프·보고서 생성
def render():
    def read(name):
        return pd.read_csv(OUT/f'{name}.csv')
    metrics, classes = read('fold_metrics'), read('class_metrics')
    confusion, agreement = read('confusion'), read('error_agreement')
    decision = json.loads((OUT/'conclusion_frozen.json').read_text(encoding='utf-8'))
    summary = metrics.groupby('model').agg(mean_macro_f1=('macro_f1','mean'),
                fold_sd=('macro_f1',lambda x:x.std(ddof=0)), mean_accuracy=('accuracy','mean'),
                mean_weighted_f1=('weighted_f1','mean'), min_recall=('min_recall','min'),
                zero_pairs=('zero_recall','sum'), fit_seconds=('fit_seconds','sum'),
                predict_seconds=('predict_seconds','sum')).reindex(['SVM', 'HGB'])
    mean_class = classes.groupby(['model','gas_id'])[['precision','recall','f1']].mean()
    mean_class['gas'] = [GASES[g] for _, g in mean_class.index]
    gas_delta = mean_class.loc['HGB'][['precision','recall','f1']]-mean_class.loc['SVM'][['precision','recall','f1']]
    gas_delta['gas'] = [GASES[g] for g in gas_delta.index]
    summary.to_csv(OUT/'summary.csv', encoding='utf-8')
    mean_class.to_csv(OUT/'mean_class_metrics.csv', encoding='utf-8')
    gas_delta.to_csv(OUT/'class_deltas.csv', encoding='utf-8')
    totals = agreement.groupby('fold')[['both_correct','svm_only','hgb_only','both_wrong','disagreement']].sum()
    totals['n'] = agreement.groupby('fold').size()
    totals.to_csv(OUT/'error_agreement_summary.csv', encoding='utf-8')
    focus_agreement = agreement[agreement.y_true.isin([4,6])].groupby(['fold','y_true'])[
        ['both_correct','svm_only','hgb_only','both_wrong','disagreement']].sum()
    focus_agreement.to_csv(OUT/'focus_error_agreement.csv', encoding='utf-8')
    plt.rcParams.update({'font.family':'Malgun Gothic','axes.unicode_minus':False})
    figures = []
    context = '과거 개발 Fold A: Batch6 n=2300 / B: Batch7 n=3613 / C: Batch8 n=294'
    def finish(name, title, fig):
        fig.suptitle(title+'\n'+context, fontsize=11)
        fig.tight_layout(rect=(0,0,1,.93))
        path = OUT/f'{name}.png'
        fig.savefig(path, dpi=150)
        plt.close(fig)
        figures.append(dict(name=name, title=title, path=str(path.relative_to(ROOT)), sha256=sha(path),
                            batch_support_and_axes_labelled=True))
    fig, ax = plt.subplots(figsize=(9,5))
    ax.bar(summary.index, summary.mean_macro_f1*100)
    ax.set(xlabel='단독 분류 모델', ylabel='Fold 동일 가중 평균 Macro F1 (%)', ylim=(0,100))
    for i, value in enumerate(summary.mean_macro_f1):
        ax.text(i, value*100+1, f'{value*100:.2f}%', ha='center')
    finish('mean_macro_f1','SVM과 HGB 평균 Macro F1',fig)
    fig, ax = plt.subplots(figsize=(9,5))
    for name in ['SVM','HGB']:
        sub = metrics[metrics.model == name]
        ax.plot(sub.fold, sub.macro_f1*100, marker='o', label=name)
    ax.set(xlabel='Validation Fold (A→6, B→7, C→8)', ylabel='Macro F1 (%)', ylim=(0,100))
    ax.legend()
    finish('fold_macro_f1','Fold별 단독 성능',fig)
    for delta in [False,True]:
        pivot = classes.pivot(index=['model','fold'], columns='gas_id', values='recall')
        pivot = pivot.reindex(pd.MultiIndex.from_product([['SVM','HGB'],list(FOLDS)]))
        if delta:
            pivot = pivot-pd.concat([pivot.loc['SVM']]*2,keys=['SVM','HGB'])
        fig, ax = plt.subplots(figsize=(11,5))
        image = ax.imshow(pivot.to_numpy()*100, aspect='auto', cmap='RdBu_r' if delta else 'viridis',
                          vmin=-100 if delta else 0,vmax=100)
        ax.set_xticks(range(6),list(GASES.values()),rotation=20,ha='right')
        ax.set_yticks(range(6),[f'{m}/{f}' for m,f in pivot.index])
        ax.set(xlabel='실제 가스',ylabel='모델 / Validation Fold')
        for i in range(6):
            for j in range(6):
                ax.text(j,i,f'{pivot.iloc[i,j]*100:.1f}',ha='center',va='center',fontsize=9)
        fig.colorbar(image,ax=ax,label='Recall 증감 (%p)' if delta else 'Recall (%)')
        finish('recall_delta' if delta else 'recall_heatmap',
               '기준 SVM 대비 가스 Recall 증감' if delta else '6종 가스 Recall',fig)
    fig, axes = plt.subplots(1,2,figsize=(12,5))
    for ax, gas in zip(axes,[6,4]):
        mean_class.xs(gas,level='gas_id')[['precision','recall','f1']].reindex(['SVM','HGB']).mul(100).plot.bar(ax=ax)
        ax.set(title=GASES[gas],xlabel='단독 분류 모델',ylabel='Fold 동일 가중 평균 (%)',ylim=(0,100))
        ax.tick_params(axis='x',rotation=0)
    finish('focus_precision_recall_f1','Toluene·Acetaldehyde P/R/F1',fig)
    fig, axes = plt.subplots(2,3,figsize=(16,10))
    for i, name in enumerate(['SVM','HGB']):
        for j, fold in enumerate(FOLDS):
            ax = axes[i,j]
            sub = confusion[(confusion.model == name)&(confusion.fold == fold)]
            matrix = sub.pivot(index='true_gas',columns='predicted_gas',values='n').to_numpy()
            ax.imshow(matrix,cmap='Blues')
            ax.set(title=f'{name}/{fold}: Batch{FOLDS[fold][1]} n={matrix.sum()}',
                   xlabel='예측 가스 번호 (1~6)',ylabel='실제 가스 번호 (1~6)')
            ax.set_xticks(range(6),list(GASES))
            ax.set_yticks(range(6),list(GASES))
            for a in range(6):
                for b in range(6):
                    ax.text(b,a,str(matrix[a,b]),ha='center',va='center',fontsize=8,
                            color='white' if matrix[a,b]>matrix.max()/2 else 'black')
    finish('confusion_matrices','Fold별 Confusion Matrix — 표본 수',fig)
    directional = []
    for (name,fold,gas), sub in confusion[confusion.true_gas.isin([4,6])].groupby(['model','fold','true_gas']):
        opposite = 4 if gas == 6 else 6
        directional.append(dict(model=name,fold=fold,true_gas=gas,
            target_pair=int(sub.loc[sub.predicted_gas == opposite,'n'].sum()),
            other_wrong=int(sub.loc[~sub.predicted_gas.isin([gas,opposite]),'n'].sum())))
    directional = pd.DataFrame(directional)
    directional.to_csv(OUT/'focus_error_directions.csv',index=False,encoding='utf-8')
    fig, axes = plt.subplots(1,2,figsize=(12,5))
    for ax, gas in zip(axes,[6,4]):
        directional[directional.true_gas == gas].set_index(['model','fold'])[['target_pair','other_wrong']].plot.bar(stacked=True,ax=ax)
        ax.set(title=GASES[gas],xlabel='모델 / Validation Fold',ylabel='오분류 표본 수')
        ax.tick_params(axis='x',rotation=25)
    finish('focus_error_directions','집중 가스의 상대 가스·기타 가스 오분류',fig)
    fig, axes = plt.subplots(1,2,figsize=(12,5))
    totals[['both_correct','svm_only','hgb_only','both_wrong']].div(totals.n,axis=0).mul(100).plot.bar(stacked=True,ax=axes[0])
    totals[['disagreement']].div(totals.n,axis=0).mul(100).plot.bar(ax=axes[1],legend=False)
    for ax in axes:
        ax.set(xlabel='Validation Fold',ylabel='동일 표본 기준 비율 (%)',ylim=(0,100))
        ax.tick_params(axis='x',rotation=0)
    finish('error_agreement','두 단독 모델의 정답·오답 및 예측 불일치',fig)
    pd.DataFrame(figures).to_csv(OUT/'graph_manifest.csv',index=False,encoding='utf-8')
    tests = test_summary()
    code = decision['conclusion']
    verdict = {'A':'균형 개선 근거 관찰','B':'부분 개선','C':'개선 근거 부족'}[code]
    observations = [f'연구 결론 {code} — {verdict}. 공식 Model A 유지.',
        f'HGB 평균 Macro F1 {summary.loc["HGB","mean_macro_f1"]*100:.2f}%, '
        f'SVM 대비{decision["mean_macro_delta"]*100:+.2f}pp. 모든 보호 조건 통과={decision["all_passed"]}.',
        '일부 Fold 또는 가스 평균 F1이 상승하면 전체 보호 미달이라도 사전 규칙상 B로 표시. '
        'B는 우수 모델 선정이나 전반적 개선을 뜻하지 않음.',
        f'HGB 학습 {decision["new_HGB_fits"]}회, SVM 재사용 {decision["reused_SVM"]}개, '
        f'SVM 재사용 실패 대체 학습{decision["fallback_SVM_fits"]}회. 추가 조건·시드 탐색 없음.',
        '수치는 관찰 결과이며 새 알고리즘의 원인 효과나 센서 드리프트 단독 원인 확정은 아님.',
        '각 Fold의 Train 행·Validation 행·정답·128특징은 동일. HGB는 표준화 없이 사용하므로 '
        '알고리즘과 적합한 전처리를 함께 비교한 대조임.',
        'HGB는 native NaN을 지원하지만 사전 정책대로 Train 중앙값 처리. class_weight=balanced를 '
        '지원하며 Train 가스 빈도만 사용. sample_weight 중복 적용 없음.',
        'HGB early_stopping=False·validation_fraction=None으로 외부·내부 Validation을 학습에 사용하지 않음. '
        'class_weight 빈도식은 SVM과 같아도 학습 손실과 적용 효과는 다름.',
        'Fold A 초기 Toluene 학습79개, Fold C Toluene 평가18개. 한 표본 Recall 변화5.56pp이며 '
        '작은 support 및 겹치는 학습 구간 때문에 독립 미래 성능의 신뢰구간이나 유의성 미주장.',
        '오류 상호 보완성은 저장된 두 예측을 비교했을 뿐 새 앙상블·Oracle·가중치 조절을 실행하지 않음.',
        '실패·혼동 방향·예측 비율을 전부 공개. 새로운 시기·농도·환경·세션 정보의 독립 검증 필요.']
    for fold in FOLDS:
        sub = classes[(classes.model == 'HGB')&(classes.fold == fold)&(classes.gas_id == 6)].iloc[0]
        observations.append(f'{fold} Toluene HGB: support{int(sub.support)}, Recall{sub.recall*100:.2f}%, '
                            f'Precision{sub.precision*100:.2f}%, F1{sub.f1*100:.2f}%, 예측 수{int(sub.predicted_n)}.')
    fold_table = metrics.pivot(index='model',columns='fold',values='macro_f1').reindex(['SVM','HGB']).mul(100)
    summary_text = ('# 16단계 HGB 단독 알고리즘 비교\n\n'+CAUTION+'\n\n'+
        '\n\n'.join('- '+x for x in observations)+'\n\n```text\n'+fold_table.to_string()+
        '\n```\n\n```text\n'+summary.to_string()+'\n```\n\n```text\n'+mean_class.to_string()+
        '\n```\n\n보호 기준:\n```json\n'+json.dumps(decision,ensure_ascii=False,indent=2)+
        '\n```\n\n테스트:\n```json\n'+json.dumps(tests,ensure_ascii=False,indent=2)+'\n```\n')
    limitations = ('# 16단계 연구 한계\n\n'+CAUTION+'\n\n'+'\n\n'.join('- '+x for x in observations[4:11])+
        '\n\n- 기존 5개 실패: 과거 소스 SHA, 임시 파일 후보 부재, 기존 전역 모델 목록 고정 충돌3건. '
        '기존 테스트·과거 해시 기준 미수정.\n- 단일 고정 HGB 설정의 결과이며 HGB 전체 성능 상한이 아님. '
        '결과 확인 후 추가 탐색·공식 모델 교체·Commit·Push 없음.\n')
    (ROOT/'reports'/REPORTS[1]).write_text(summary_text,encoding='utf-8')
    (ROOT/'reports'/REPORTS[2]).write_text(limitations,encoding='utf-8')
    sections = []
    def section(title,content):
        sections.append('<h2>'+html.escape(title)+'</h2>'+content)
    section('1. 연구 목적·기존 결과·독립성 한계','<p>'+CAUTION+'</p><p>8단계 단독·12~13단계 구성·14단계 변환·15단계 결합 이후 다른 분류 경계의 단독 대조.</p>')
    section('2. 사전 고정 계획·환경','<pre>'+html.escape((OUT/'experiment_plan.json').read_text(encoding='utf-8'))+'</pre>')
    section('3. 동일 분할과 가스 support',read('fold_support').to_html(index=False))
    section('4. 평균 및 Fold별 성능',summary.to_html()+fold_table.to_html()+metrics.to_html(index=False))
    section('5. 6종 가스별 지표·예측 비율',mean_class.to_html()+gas_delta.to_html()+classes.to_html(index=False))
    section('6. 사전 보호 기준과 연구 결론','<p>'+code+' — '+verdict+'</p><pre>'+html.escape(json.dumps(decision,ensure_ascii=False,indent=2))+'</pre>')
    section('7. 오류 상호 보완성·집중 가스 오분류',totals.to_html()+focus_agreement.to_html()+directional.to_html(index=False))
    section('8. 실제 계산값 시각화','<p>가스 번호: '+html.escape(str(GASES))+'</p>'+''.join(
        '<figure><img alt="'+html.escape(f['title'])+'" src="data:image/png;base64,'+
        base64.b64encode((ROOT/f['path']).read_bytes()).decode('ascii')+'"><figcaption>'+html.escape(f['title'])+'</figcaption></figure>' for f in figures))
    section('9. Train-only·가중치·모델 재현 검사',read('train_only_audit').to_html(index=False)+read('class_weights').to_html(index=False))
    section('10. 관찰·해석·한계·다음 단계','<ul>'+''.join('<li>'+html.escape(x)+'</li>' for x in observations)+'</ul><pre>'+html.escape(limitations)+'</pre>')
    section('11. 보존·전체 테스트·재실행','<pre>'+html.escape(json.dumps(tests,ensure_ascii=False,indent=2))+'</pre>'+
        '<p>preservation_audit.csv에서 기존 원본·모델·코드·보고서 바이트 해시 검사. '
        '프로젝트 루트에서 python -m src.hgb_algorithm_comparison freeze → run → 전체 pytest → report. '
        '기존 출력이 있으면 학습 재실행은 덮어쓰기를 거부함.</p>')
    document = ('<!doctype html><html lang="ko"><meta charset="utf-8"><title>16단계 HGB 단독 비교</title>'+
        '<style>body{font-family:Malgun Gothic,sans-serif;margin:32px;color:#172536}table{border-collapse:collapse;display:block;overflow:auto;font-size:13px}'
        'td,th{border:1px solid #bbc;padding:6px}img{max-width:100%;height:auto}pre{white-space:pre-wrap;overflow-wrap:anywhere}h2{margin-top:36px}</style>'+
        '<body><h1>HistGradientBoosting과 RBF SVM 시간순 단독 비교</h1>'+''.join(sections)+'</body></html>')
    (ROOT/'reports'/REPORTS[0]).write_text(document,encoding='utf-8')
