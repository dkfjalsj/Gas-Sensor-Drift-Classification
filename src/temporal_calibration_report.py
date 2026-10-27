# 고정 평가 집합의 교정 비율·시드별 적응 효과와 부작용 보고
# 과거 회귀 검사·소수 클래스·재사용 개발 자료의 한계 공개

import base64
import html
import json
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .data import ROOT,GASES
from .temporal_expansion import sha
from .temporal_calibration import OUT,REPORTS,FOLDS,SEEDS,RATES,CAUTION,write


def test_summary():
    if not (OUT/'test_results.xml').exists():
        return dict(status='전체 테스트 실행 전')
    old=ET.parse(ROOT/'outputs/hgb_algorithm_comparison/test_results.xml')
    old_fail={(c.get('classname'),c.get('name')) for c in old.iter('testcase')
              if c.find('failure') is not None or c.find('error') is not None}
    cases=list(ET.parse(OUT/'test_results.xml').iter('testcase'))
    failures=[]
    for c in cases:
        f=c.find('failure')
        if f is None:
            f=c.find('error')
        if f is not None:
            key=(c.get('classname'),c.get('name'))
            failures.append(dict(classname=key[0],name=key[1],historical=key in old_fail,reason=f.get('message','')[:1200]))
    new=[c for c in cases if 'test_temporal_calibration' in c.get('classname','')]
    result=dict(total=len(cases),passed=sum(c.find('failure') is None and c.find('error') is None
                and c.find('skipped') is None for c in cases),failed=len(failures),
                historical_failures=sum(f['historical'] for f in failures),new_failures=sum(not f['historical'] for f in failures),
                new_tests=len(new),new_passed=sum(c.find('failure') is None and c.find('error') is None for c in new),failures=failures)
    write('test_summary.json',result)
    return result


def render():
    metrics=pd.read_csv(OUT/'metrics.csv')
    classes=pd.read_csv(OUT/'class_metrics.csv')
    main=metrics[metrics.scope=='evaluation'].copy()
    gas=classes[classes.scope=='evaluation'].copy()
    baseline=main[main.rate==0].set_index(['fold','seed']).macro_f1
    main['macro_delta']=[r.macro_f1-baseline.loc[(r.fold,r.seed)] for r in main.itertuples()]
    main.to_csv(OUT/'evaluation_metrics.csv',index=False,encoding='utf-8')
    seed_summary=main.groupby(['rate','seed']).agg(macro_f1=('macro_f1','mean'),accuracy=('accuracy','mean'),
        weighted_f1=('weighted_f1','mean'),macro_delta=('macro_delta','mean'),zero_pairs=('zero_recall','sum')).reset_index()
    seed_summary.to_csv(OUT/'seed_summary.csv',index=False,encoding='utf-8')
    summary=seed_summary.groupby('rate').agg(mean_macro_f1=('macro_f1','mean'),seed_sd=('macro_f1','std'),
        mean_accuracy=('accuracy','mean'),mean_weighted_f1=('weighted_f1','mean'),mean_macro_delta=('macro_delta','mean'))
    summary.to_csv(OUT/'ratio_summary.csv',encoding='utf-8')
    fold_summary=main.groupby(['rate','fold']).agg(mean_macro_f1=('macro_f1','mean'),seed_sd=('macro_f1','std'),
        mean_macro_delta=('macro_delta','mean'),evaluation_n=('n','first'),calibration_n=('calibration_n','first'))
    fold_summary.to_csv(OUT/'fold_summary.csv',encoding='utf-8')
    mean_gas=gas.groupby(['rate','seed','gas_id'])[['precision','recall','f1']].mean().groupby(['rate','gas_id']).mean()
    mean_gas['gas']=[GASES[g] for _,g in mean_gas.index]
    mean_gas.to_csv(OUT/'mean_class_metrics.csv',encoding='utf-8')
    regression=metrics[metrics.scope=='regression'].copy()
    reference=regression[regression.rate==0].set_index('seed').macro_f1
    regression['macro_delta']=[r.macro_f1-reference.loc[r.seed] for r in regression.itertuples()]
    regression.to_csv(OUT/'regression_metrics.csv',index=False,encoding='utf-8')
    predictions=pd.read_csv(OUT/'predictions.csv')
    focus=[]
    for key,sub in predictions[(predictions.scope=='evaluation')&predictions.y_true.isin([4,6])].groupby(['fold','seed','rate','y_true']):
        fold,seed,rate,g=key
        other=4 if g==6 else 6
        focus.append(dict(fold=fold,seed=seed,rate=rate,gas_id=g,support=len(sub),correct=int((sub.y_true==sub.y_pred).sum()),
                          pair_errors=int((sub.y_pred==other).sum()),other_errors=int((~sub.y_pred.isin([g,other])).sum())))
    focus=pd.DataFrame(focus)
    focus.to_csv(OUT/'focus_counts.csv',index=False,encoding='utf-8')
    decisions=json.loads((OUT/'rate_decisions.json').read_text(encoding='utf-8'))
    plt.rcParams.update({'font.family':'Malgun Gothic','axes.unicode_minus':False})
    figures=[]
    context='동일 평가 행(시드 내 고정): A/Batch6 n=1150, B/Batch7 n=1806, C/Batch8 n=147'
    def finish(name,title,fig):
        fig.suptitle(title+'\n'+context,fontsize=11)
        fig.tight_layout(rect=(0,0,1,.93))
        path=OUT/f'{name}.png'
        fig.savefig(path,dpi=150)
        plt.close(fig)
        figures.append(dict(name=name,title=title,path=str(path.relative_to(ROOT)),sha256=sha(path),fixed_evaluation=True))
    fig,ax=plt.subplots(figsize=(10,5))
    ax.errorbar(summary.index,summary.mean_macro_f1*100,yerr=summary.seed_sd*100,marker='o',capsize=4)
    ax.set(xlabel='전체 target Batch 기준 교정 비율 (%)',ylabel='시드별 동일 Fold 평균 → 시드 평균 Macro F1 (%)',ylim=(0,100))
    ax.set_xticks(RATES)
    finish('mean_macro_by_rate','교정 비율별 Macro F1 (오차 막대: 3시드 SD, 미래 신뢰구간 아님)',fig)
    fig,ax=plt.subplots(figsize=(10,5))
    for fold in FOLDS:
        sub=fold_summary.xs(fold,level='fold')
        ax.plot(sub.index,sub.mean_macro_f1*100,marker='o',label=f'{fold} / Batch{FOLDS[fold][1]}')
    ax.set(xlabel='교정 비율 (%)',ylabel='3시드 평균 Macro F1 (%)',ylim=(0,100))
    ax.set_xticks(RATES)
    ax.legend()
    finish('fold_macro_by_rate','Fold별 교정 전후 성능',fig)
    pivot=gas.groupby(['rate','fold','gas_id']).recall.mean().unstack('gas_id')
    rows=[]
    labels=[]
    for rate in RATES:
        for fold in FOLDS:
            rows.append((pivot.loc[(rate,fold)]-pivot.loc[(0,fold)]).to_numpy()*100)
            labels.append(f'{fold} / {rate}%')
    fig,ax=plt.subplots(figsize=(11,7))
    image=ax.imshow(rows,aspect='auto',cmap='RdBu_r',vmin=-100,vmax=100)
    ax.set_xticks(range(6),list(GASES.values()),rotation=20,ha='right')
    ax.set_yticks(range(12),labels)
    ax.set(xlabel='실제 가스',ylabel='Fold / 교정 비율')
    for i in range(12):
        for j in range(6):
            ax.text(j,i,f'{rows[i][j]:+.1f}',ha='center',va='center',fontsize=8)
    fig.colorbar(image,ax=ax,label='0% 대비 Recall 증감 (%p), 3시드 평균')
    finish('recall_delta','가스별 Recall 변화 (가스 support는 split_support.csv)',fig)
    for field,name,title in [('correct','toluene_correct','Toluene 정분류 수'),('pair_errors','toluene_to_acetaldehyde','Toluene → Acetaldehyde 오류')]:
        fig,ax=plt.subplots(figsize=(10,5))
        for fold in FOLDS:
            sub=focus[(focus.fold==fold)&(focus.gas_id==6)]
            values=sub.groupby('rate')[field].mean()
            support=int(sub.support.iloc[0])
            ax.plot(values.index,values,marker='o',label=f'{fold} Tol support={support} / seed')
        ax.set(xlabel='교정 비율 (%)',ylabel='시드별 평가 표본 수의 3시드 평균')
        ax.set_xticks(RATES)
        ax.legend()
        finish(name,title+' (반복 시드 표본을 합산하지 않음)',fig)
    fig,ax=plt.subplots(figsize=(10,5))
    ac=mean_gas.xs(4,level='gas_id')
    for name in ['precision','recall','f1']:
        ax.plot(ac.index,ac[name]*100,marker='o',label=name)
    ax.set(xlabel='교정 비율 (%)',ylabel='Fold 평균 후 시드 평균 (%)',ylim=(0,100))
    ax.set_xticks(RATES)
    ax.legend()
    finish('acetaldehyde_metrics','Acetaldehyde Precision·Recall·F1',fig)
    fig,ax=plt.subplots(figsize=(11,5))
    for g in GASES:
        sub=mean_gas.xs(g,level='gas_id')
        ax.plot(sub.index,sub.f1*100,marker='o',label=GASES[g])
    ax.set(xlabel='교정 비율 (%)',ylabel='Fold 평균 후 시드 평균 F1 (%)',ylim=(0,100))
    ax.set_xticks(RATES)
    ax.legend(ncol=2)
    finish('six_gas_f1','6종 가스 F1 및 성능 균형',fig)
    fig,ax=plt.subplots(figsize=(10,5))
    for seed in SEEDS:
        sub=seed_summary[seed_summary.seed==seed]
        ax.plot(sub.rate,sub.macro_f1*100,marker='o',label=f'seed {seed}')
    ax.set(xlabel='교정 비율 (%)',ylabel='동일3Fold 평균 Macro F1 (%)',ylim=(0,100))
    ax.set_xticks(RATES)
    ax.legend()
    finish('seed_variability','시드별 표본 선택 변동성 (독립 환경 반복 아님)',fig)
    fig,ax=plt.subplots(figsize=(11,5))
    for (fold,seed),sub in main.groupby(['fold','seed']):
        ax.plot(sub.calibration_n,sub.macro_delta*100,marker='o',label=f'{fold} seed{seed}')
    ax.set(xlabel='실제 추가 교정 표본 수',ylabel='같은 평가 행의 0% 대비 Macro F1 증감 (%p)')
    ax.legend(ncol=3,fontsize=8)
    finish('sample_count_effect','교정 표본 수와 대응 성능 변화',fig)
    pd.DataFrame(figures).to_csv(OUT/'graph_manifest.csv',index=False,encoding='utf-8')
    tests=test_summary()
    notes=[
        CAUTION,
        '교정 비율의 분모는 전체 target Batch. 평가50%를 먼저 고정한 뒤 남은50%에서5/10/20%를 중첩 추출. '
        '실제 수는 내림하며 모든 가스 최소1개 확보. 같은 Fold·시드의 평가 행은 모든 비율에서 동일.',
        '0% 기준도 이번50% 평가 행에서 새로 계산한 지표임. 이전 전체 Batch 평가79.71%와 표본이 달라 직접 같은 수치가 아님.',
        '평가 정답은 층화 분할·최종 지표 계산에만 사용. 전처리·SVM·balanced 가중치는 과거+선택 Calibration에서만 Fit.',
        '새 시기 정답이 있는 적응과 새 시기 정답이 전혀 없는 미래 일반화는 다른 문제. '
        '현재 목표 Batch 안에서의 회복이며 이후 미관찰 시기에 대한 지속성은 검증하지 않았음.',
        '과거 시기 회귀 검사는 Fold A의 기존 B_history Validation4·Test5만 재등록. '
        '358개·5종 가스(Toluene 없음), 적응 Train·교정·평가와 중복 없음. B/C는 적절한 과거 held-out 없음.',
        '평가 집합은 이전에 반복 관찰한 자료에서 새로 나눈 것으로 독립성이 복구되지 않음. '
        '시드별 분할이 겹치며 한 시드의 평가 행이 다른 시드의 교정 행일 수 있음. 독립 미래 반복이나 p값 미주장.',
        '가스별 층화에는 기존 정답 정보가 필요함. 실제 배포에서 같은 클래스 구성을 모으는 라벨 수집 비용이 '
        '5%라고 증명한 결과가 아님. 농도·환경·세션의 유사성과 근접 반복 측정 가능성도 남음.',
        '동일 Batch 내부의 정확한 시각이 없어 무작위 교정 자료가 평가보다 실제로 먼저 측정됐다고 주장할 수 없음.',
        '각 비율을 별도로 판정하며 우수 비율을 사후 선정해 공식 모델을 교체하지 않음. '
        '추가 비율·시드·튜닝·앙상블·물리적 센서 교정·감지 알고리즘 없음.',
        '과거 유지 성능은 별도의 진단이며 현재 시기 보호 조건 통과가 과거 전 가스의 유지 성능을 보장하지 않음.'
    ]
    for d in decisions['rates']:
        notes.append(f'{d["rate"]}% 판정 {d["conclusion"]}: 평균 Macro F1 변화{d["mean_macro_delta"]*100:+.2f}pp, '
                     f'긍정 Fold-시드 {d["positive_cells"]}/9, 신규 Recall0 {d["new_zero_pairs"]}, '
                     f'모든 보호·일관성 조건 통과={d["all_passed"]}.')
    summary_text=('# 17단계 소량 신규 시기 자료 기반 지도학습 적응\n\n'+'\n\n'.join('- '+s for s in notes)+
        '\n\n비율 요약:\n```text\n'+summary.to_string()+'\n```\n\nFold 요약:\n```text\n'+fold_summary.to_string()+
        '\n```\n\n가스별 평균:\n```text\n'+mean_gas.to_string()+'\n```\n\n과거 회귀 검사:\n```text\n'+regression.to_string(index=False)+
        '\n```\n\n테스트:\n```json\n'+json.dumps(tests,ensure_ascii=False,indent=2)+'\n```\n')
    limits=('# 17단계 연구 한계\n\n'+CAUTION+'\n\n'+'\n\n'.join('- '+s for s in notes[3:11])+
        '\n\n- Fold C Toluene 평가9개로 한 표본 Recall11.11pp. 작은 차이 과대 해석 금지.\n'+
        '- 수량 증가 시 클래스별 추가 수·시기 정보·전처리·balanced 벌점도 바뀜. 순수 수량 또는 물리적 드리프트 효과 분리 불가.\n'+
        '- 이전부터 있던5개 테스트 실패와 신규 실패를 구분. 과거 해시·테스트 기준 미수정. Commit·Push 없음.\n')
    (ROOT/'reports'/REPORTS[1]).write_text(summary_text,encoding='utf-8')
    (ROOT/'reports'/REPORTS[2]).write_text(limits,encoding='utf-8')
    sections=[]
    def section(title,body):
        sections.append('<h2>'+html.escape(title)+'</h2>'+body)
    section('1. 목적·이전 실험과 달라진 정보 조건','<p>'+CAUTION+'</p><p>고정 SVM에 정답이 있는 target 일부를 추가하는 실험. '
            '12~13단계 과거 표본 재구성·14단계 변환·15단계 결합·16단계 알고리즘 변경과 구분.</p>')
    section('2. 실행 전 계획과 고정 분할','<pre>'+html.escape((OUT/'experiment_plan.json').read_text(encoding='utf-8'))+'</pre>')
    section('3. 실제 표본 수·가스 support·중복 검사',pd.read_csv(OUT/'overlap_checks.csv').to_html(index=False)+pd.read_csv(OUT/'split_support.csv').to_html(index=False))
    section('4. 비율별·시드별·Fold별 성능',summary.to_html()+seed_summary.to_html(index=False)+fold_summary.to_html()+main.to_html(index=False))
    section('5. 6종 가스와 Toluene·Acetaldehyde',mean_gas.to_html()+focus.to_html(index=False))
    section('6. 사전 보호 기준과 비율별 결론','<pre>'+html.escape(json.dumps(decisions,ensure_ascii=False,indent=2))+'</pre>')
    section('7. 과거 시기 유지·회귀 진단','<p>Fold A만 가능. 실제 존재하는5개 정답 가스의 Macro F1. '
            '독립 미래 일반화·Toluene 유지 성능 아님. B/C 평가 불가.</p>'+regression.to_html(index=False))
    section('8. 동일 평가 행의 교정 전후 그래프',''.join('<figure><img alt="'+html.escape(f['title'])+
        '" src="data:image/png;base64,'+base64.b64encode((ROOT/f['path']).read_bytes()).decode('ascii')+
        '"><figcaption>'+html.escape(f['title'])+'</figcaption></figure>' for f in figures))
    section('9. Train-only·가중치·모델 감사',pd.read_csv(OUT/'train_only_audit.csv').to_html(index=False)+pd.read_csv(OUT/'class_weights.csv').to_html(index=False))
    section('10. 계산 결과 해석·한계·다음 연구','<ul>'+''.join('<li>'+html.escape(s)+'</li>' for s in notes)+'</ul><pre>'+html.escape(limits)+'</pre>')
    section('11. 전체 테스트·보존·재실행','<pre>'+html.escape(json.dumps(tests,ensure_ascii=False,indent=2))+'</pre>'+
        '<p>기존 원본·모델·코드·보고서 SHA는 preservation_audit.csv 참조. '
        '프로젝트 루트에서 python -m src.temporal_calibration freeze → run → 전체 pytest → report. '
        '출력이 있으면 학습 재실행을 거부함. 과거 기록·기준 미수정.</p>')
    document=('<!doctype html><html lang="ko"><meta charset="utf-8"><title>17단계 지도학습 시기 적응</title>'+
        '<style>body{font-family:Malgun Gothic,sans-serif;margin:32px;color:#172536}table{border-collapse:collapse;display:block;overflow:auto;font-size:13px}'
        'td,th{border:1px solid #bbc;padding:6px}img{max-width:100%;height:auto}pre{white-space:pre-wrap;overflow-wrap:anywhere}h2{margin-top:36px}</style>'+
        '<body><h1>소량 신규 시기 정답 데이터 기반 SVM 적응</h1>'+''.join(sections)+'</body></html>')
    (ROOT/'reports'/REPORTS[0]).write_text(document,encoding='utf-8')
