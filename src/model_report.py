"""Self-contained UTF-8 report, built solely from measured predictions."""
import base64
import html
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix
from .data import ROOT, GASES

NAMES = {'A_random':'A · Random 60/20/20', 'B_early':'B · Early (train 1 / val 2 / test 3–10)',
         'B_history':'B · History (train 1–3 / val 4 / test 5–10)'}
MODELS = ['LogisticRegression','RandomForest','SVM_RBF']
METRICS = ['accuracy','macro_precision','macro_recall','macro_f1','weighted_f1']

def table(frame,index=False):
    return '<div class="table">'+frame.to_html(index=index,border=0,escape=True,na_rep='NA',float_format=lambda v:f'{v:.4f}')+'</div>'

def make_report(metrics,per_class,predictions,stability,audits,fit_records,manifest):
    out = ROOT/'outputs'/'model_comparison'
    fig_dir = out/'figures'
    fig_dir.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.grid':True,'grid.alpha':.2})
    figures = {}
    def save(fig,name,caption):
        fig.tight_layout()
        path = fig_dir/f'{name}.png'
        fig.savefig(path,dpi=120,bbox_inches='tight')
        plt.close(fig)
        figures[name] = f'<figure><img alt="{html.escape(caption)}" src="data:image/png;base64,{base64.b64encode(path.read_bytes()).decode()}"><figcaption>{html.escape(caption)}</figcaption></figure>'
    labels, gasnames = list(GASES), list(GASES.values())
    for experiment in NAMES:
        for partition in ('validation','test'):
            fig,axes = plt.subplots(3,2,figsize=(14,17))
            for row,model in enumerate(MODELS):
                selected = predictions[(predictions.experiment==experiment) & (predictions.model==model) & (predictions.partition==partition)]
                cm = confusion_matrix(selected.y_true,selected.y_pred,labels=labels)
                support = cm.sum(axis=1)
                normalized = np.divide(cm,support[:,None],out=np.zeros_like(cm,dtype=float),where=support[:,None]!=0)
                for col,data in enumerate((cm,normalized)):
                    ax = axes[row,col]
                    mask = np.broadcast_to(support[:,None]==0,cm.shape) if col else np.zeros_like(cm,dtype=bool)
                    shown = np.ma.masked_array(data,mask=mask)
                    cmap = plt.colormaps['Blues'].copy(); cmap.set_bad('#dddddd')
                    image = ax.imshow(shown,cmap=cmap,vmin=0,vmax=1 if col else max(1,cm.max()))
                    for i in range(6):
                        for j in range(6):
                            text = 'NA' if mask[i,j] else (f'{data[i,j]:.2f}' if col else str(data[i,j]))
                            ax.text(j,i,text,ha='center',va='center',fontsize=9,
                                    color='white' if not mask[i,j] and data[i,j] > (.5 if col else cm.max()/2) else '#222222')
                    ax.set(title=f'{model} — {partition} / '+('row-normalized' if col else 'counts'),
                           xlabel='Predicted gas class',ylabel='True gas class',xticks=range(6),xticklabels=gasnames,
                           yticks=range(6),yticklabels=gasnames)
                    ax.tick_params(axis='x',rotation=35)
                    ax.grid(False)
                    fig.colorbar(image,ax=ax,fraction=.046,pad=.04,label='Within-true-class fraction' if col else 'Number of samples')
            fig.suptitle(NAMES[experiment]+f' — {partition} confusion matrices',fontsize=14,y=1.005)
            save(fig,f'cm_{experiment}_{partition}',f'{NAMES[experiment]} / {partition}: 왼쪽은 실제 개수, 오른쪽은 실제 클래스 기준 정규화. 행=True, 열=Predicted. 실제 표본이 없는 클래스의 정규화 행은 NA다.')
        selected = metrics[(metrics.experiment==experiment) & (metrics.partition=='test') & (metrics.scope=='batch')]
        fig,axes = plt.subplots(1,2,figsize=(14,5))
        for ax,metric,title in zip(axes,['accuracy','macro_f1'],['Accuracy','Present-class macro F1']):
            for model in MODELS:
                sub = selected[selected.model==model].sort_values('batch')
                ax.plot(sub.batch,sub[metric],marker='o',label=model)
            ax.set(title=f'{NAMES[experiment]}\n{title} by test batch',xlabel='Batch (ordered category)',ylabel=title,ylim=(0,1.02),xticks=sorted(selected.batch.unique()))
            ax.legend(fontsize=8)
        save(fig,f'batch_{experiment}','각 Batch의 Test 부분만 평가했다. A는 같은 Batch의 다른 표본을 학습에서 보았으며 B는 미래 Batch 전체를 평가한다. 누락 클래스가 있는 Batch의 macro 지표는 존재 클래스 평균이다.')
    pooled = metrics[(metrics.partition=='test') & (metrics.scope=='pooled')]
    validation = metrics[(metrics.partition=='validation') & (metrics.scope=='pooled')]
    fig,axes = plt.subplots(1,2,figsize=(14,5))
    for ax,metric in zip(axes,['accuracy','macro_f1']):
        positions = np.arange(3)
        for i,experiment in enumerate(NAMES):
            values = pooled[pooled.experiment==experiment].set_index('model').loc[MODELS,metric]
            bars = ax.bar(positions+(i-1)*.25,values,width=.25,label=experiment)
            ax.bar_label(bars,fmt='%.3f',fontsize=8,padding=2)
        ax.set(title=f'Pooled test {metric}',xlabel='Classifier',ylabel=metric,xticks=positions,xticklabels=MODELS,ylim=(0,1.08))
        ax.legend(fontsize=8)
    save(fig,'pooled_comparison','Test 성능을 실험별로 분리해 표시했다. 세 실험의 학습량·수집 시기·평가 표본이 다르므로 차이는 드리프트만의 효과가 아니다.')
    common = stability[stability.scope=='common_full6_batches_6_to_10']
    fig,axes = plt.subplots(1,2,figsize=(14,5))
    for ax,experiment in zip(axes,['B_early','B_history']):
        sub = common[common.experiment==experiment].set_index('model').loc[MODELS]
        bars = ax.bar(np.arange(3),sub.mean_macro_f1,yerr=sub.std_macro_f1,capsize=5,color=['#357ca5','#e89d3c','#41967f'])
        ax.bar_label(bars,fmt='%.3f',padding=4,fontsize=9)
        ax.set(title=experiment+': common full-class test batches 6–10',xlabel='Classifier',ylabel='Equal-batch mean macro F1 +/- descriptive SD',xticks=np.arange(3),xticklabels=MODELS,ylim=(0,1.1))
    save(fig,'stability','동일한 6종 클래스가 존재하는 공통 미래 Batch 6–10의 평균과 기술적 표준편차(ddof=0). 오차막대는 신뢰구간이 아니다. 작은 표준편차만으로 좋은 모델이라고 판단하지 않는다.')
    audit_frame = pd.DataFrame(audits)
    audit_frame['batches'] = audit_frame.batches.apply(lambda v:','.join(map(str,v)))
    audit_frame['missing_classes'] = audit_frame.missing_classes.apply(lambda v:','.join(v) or '없음')
    counts_rows = []
    for row in audits:
        counts_rows.append({'experiment':row['experiment'],'partition':row['partition'],
                            **{GASES[int(g)]:n for g,n in row['class_counts'].items()}})
    fit_table = pd.DataFrame([dict(experiment=r['experiment'],model=r['model'],train_n=r['train_n'],
                                   fit_seconds=r['fit_seconds'],n_iter=str(r['n_iter']),
                                   warnings='; '.join(w['category']+': '+w['message'] for w in r['warnings']) or '없음') for r in fit_records])
    config_text = (ROOT/'training_config.json').read_text(encoding='utf-8')
    full_common = common[common.experiment.str.startswith('B_')].copy()
    observations = []
    for experiment in NAMES:
        sub = pooled[pooled.experiment==experiment]
        highest = sub.loc[sub.macro_f1.idxmax()]
        observations.append(f"{experiment}: 관측 pooled Test macro-F1 최댓값은 {highest['model']} {highest['macro_f1']:.4f}였다. 이는 이 분할에서의 관측 비교이며 최종 모델 선정이 아니다.")
    for experiment in ['B_early','B_history']:
        sub = full_common[full_common.experiment==experiment]
        high = sub.loc[sub.mean_macro_f1.idxmax()]
        low = sub.loc[sub.std_macro_f1.idxmin()]
        observations.append(f"{experiment}, 공통 미래 Batch 6–10: 평균 macro-F1 최댓값 {high['model']}={high['mean_macro_f1']:.4f}, 최소 Batch 간 SD {low['model']}={low['std_macro_f1']:.4f}. 평균·최솟값·산포를 함께 해석한다.")
    gaps = []
    for model in MODELS:
        values = pooled[pooled.model==model].set_index('experiment')
        for experiment in ['B_early','B_history']:
            gaps.append(dict(model=model,comparison=f'A_random minus {experiment}',
                             accuracy_gap_pp=100*(values.loc['A_random','accuracy']-values.loc[experiment,'accuracy']),
                             macro_f1_gap_pp=100*(values.loc['A_random','macro_f1']-values.loc[experiment,'macro_f1'])))
    sections=[]
    def section(title,body):
        sections.append(f'<section><h2>{title}</h2>{body}</section>')
    section('1. 연구 목표 및 실험 설계','''<p>센서에서 추출한 128개 특징으로 6종 가스를 분류하고, 동일 수집 집합의 랜덤 분할과 과거→미래 Batch 평가를 비교한다.
향후 Batch에서 모델이 상대적으로 얼마나 안정적인지 관찰한다. 최종 모델 선정과 하이퍼파라미터 탐색은 수행하지 않았다.</p>
<p>기존 eda_report.html 및 evaluation_design.md를 읽고 실험을 정했다. 이번 요청에 따라 A는 기존 80/20에서 60/20/20으로 변경했다.
기존 seed=42의 20% Test를 그대로 유지하고 나머지 80%를 다시 75/25로 계층 분할했다.
B의 초기 고정 학습 및 1–3 학습 실험을 유지하면서 각각 다음 Batch를 Validation으로 유보했다.
확장 창 실험은 이번 고정 기준선 비교 범위에서 수행하지 않았다.</p>
<p><b>사전 고정:</b> training_config.json에 모델·분할·파라미터를 기록한 뒤 실행했다.
Validation은 진단으로만 보고했으며 설정 변경, 모델 선정, Train+Validation 재학습, 조기 종료에 사용하지 않았다.
Test도 결과 보고에만 사용했다. 이번 실험은 분할당 3모델, 총 9회 Fit이다.</p>''')
    section('2. 데이터 분할 방법과 표본 수',table(audit_frame[['experiment','partition','n','batches','missing_classes','row_overlap','cross_partition_exact_duplicate_groups']])+
            table(pd.DataFrame(counts_rows))+'''<p>A: Train 8,346 / Validation 2,782 / Test 2,782.
B_early: Train Batch 1(445) / Validation Batch 2(1,244) / Test Batch 3–10(12,221).
B_history: Train Batch 1–3(3,275) / Validation Batch 4(161) / Test Batch 5–10(10,474).</p>
<p>검사: 모든 Train에 6종 존재, 행 중복·정확 특징 중복의 파티션 간 누수 없음, B는 Train &lt; Validation &lt; Test의 Batch 순서 충족.
B_history Validation Batch 4에는 Toluene이 없고, B_early Test Batch 3–5 및 B_history Test Batch 5에도 없다.
Batch 2의 Toluene은 5개뿐이다. split_assignments.csv에 전체 행별 분할을 저장했다.
정확 중복이 발견되면 이 코드는 학습을 중단하므로 그룹 분할/중복 정책을 먼저 재설계해야 한다.</p>''')
    section('3. 모델별 전처리 및 학습 조건','''<p>입력은 f001–f128만 사용했다. batch, source_line, row_id, gas 레이블은 입력에서 제외했다.
모든 모델에 Train에서만 Fit하는 median SimpleImputer를 사용했다. 현재 실제 자료의 결측·Inf는 0개이며 이상치 제거·특징 선택·재표본화는 하지 않았다.</p>
<p>Logistic Regression 및 RBF SVM은 그 뒤 StandardScaler를 사용했고 Random Forest는 스케일링하지 않았다.
이는 이번 요청을 반영한 기존 설계의 변경이다. 세 모델이 공유하는 것은 같은 표본과 분할이며 모델에 필요한 전처리는 다르게 적용한다.
EDA PCA와 스케일러는 사용하지 않았다.</p>
<p>LR의 max_iter=10,000은 사전에 정한 수렴 여유이며 탐색 결과가 아니다. RF=100 trees, RBF SVM C=1, gamma=scale을 고정했다.
SVM gamma=scale은 Train 변환값에서 계산되며 미래 Batch 통계를 사용하지 않는다.
각 클래스의 가중치는 기본 동일 가중, RF seed=42, 선형 대수 thread 한도=2다.
fit 시간은 실행 환경 의존적이며 효율성 순위를 확정하지 않는다.</p>'''+table(fit_table)+
            '<details><summary>실행 전 고정한 설정</summary><pre>'+html.escape(config_text)+'</pre></details>'+
            table(pd.DataFrame([{'package':p,'version':v} for p,v in manifest['package_versions'].items()]))+
            '<p>모든 실제 estimator 파라미터와 경고는 fit_records.json, 실행 환경·소스 지문은 run_manifest.json에 저장했다. 수렴 경고가 있으면 원문을 위 표에 남긴다.</p>')
    section('4. 모델 성능 비교표','''<p><b>지표 정의:</b> 값은 0–1 범위다. macro_precision/recall/F1은 평가 집합에 실제 존재하는 클래스의 동일 가중 평균이다.
표본이 있는 클래스에서 예측이 전혀 없으면 precision/F1을 0으로 처리했다.
실제 표본이 없는 클래스의 개별 지표는 NA, support는 0으로 표시한다.
고정 6종 평균은 없는 클래스를 0으로 채운 macro_*_fixed6 열에 별도 제공한다.
현재 모든 pooled Test에는 6종이 있어 두 macro 정의가 일치한다. weighted-F1은 실제 support 가중 평균이다.</p>
<h3>Test — 실험별 전체 평가 표본을 합쳐 계산</h3>'''+table(pooled[['experiment','model','n',*METRICS,'macro_f1_fixed6','missing_classes']])+figures['pooled_comparison']+
            '<h3>Validation — 설정 변경에 사용하지 않은 별도 진단</h3>'+table(validation[['experiment','model','n',*METRICS,'macro_f1_fixed6','missing_classes']])+
            '<details><summary>Validation 및 Test의 클래스별 지표 전체 보기</summary>'+table(per_class[per_class.scope=='pooled'][['experiment','model','partition','gas','support','predicted_count','precision','recall','f1']])+'</details>')
    cm_body='<p>클래스 순서는 UCI 224 설명의 1 Ethanol, 2 Ethylene, 3 Ammonia, 4 Acetaldehyde, 5 Acetone, 6 Toluene이다. 예측을 수정하거나 성능을 보정하지 않았다.</p>'
    for experiment in NAMES:
        cm_body+=f'<h3>{html.escape(NAMES[experiment])} — Test</h3>'+figures[f'cm_{experiment}_test']
        cm_body+='<details><summary>Validation Confusion Matrix</summary>'+figures[f'cm_{experiment}_validation']+'</details>'
    section('5. Confusion Matrix',cm_body)
    body='''<p>모든 Batch 그래프의 가로축은 순서 범주이며 시간 간격이나 정확한 측정 날짜가 아니다.
A는 Test에 배정된 일부 표본만, B는 해당 미래 Batch 전체를 평가하므로 두 곡선의 표본 조건이 다르다.</p>'''
    for experiment in NAMES:
        body+=figures[f'batch_{experiment}']
        body+='<details><summary>'+html.escape(experiment)+' Batch별 Test 지표</summary>'+table(metrics[(metrics.experiment==experiment)&(metrics.partition=='test')&(metrics.scope=='batch')][['model','batch','n',*METRICS,'macro_f1_fixed6','missing_classes']])+'</details>'
    body+=figures['stability']+table(stability[['experiment','model','scope','n_batches','mean_accuracy','mean_macro_f1','std_macro_f1','min_macro_f1','max_macro_f1']])
    body+='''<p>pooled는 표본을 합쳐 새로 계산한 지표이며 Batch 지표의 단순 평균이 아니다.
stability 표는 각 Batch에 동일 가중치를 준 평균이다. 전체 Test 구간에서는 클래스 집합이 달라지는 Batch가 섞여 있으므로
공통 6종이 존재하는 Batch 6–10의 안정성을 별도로 제시했다. B의 두 학습 조건은 이 구간에서 같은 Test 표본을 사용하지만 A는 부분 표본이다.</p>'''
    section('6. Batch별 성능 변화',body)
    section('7. Random Split과 Batch Split 결과 비교',table(pd.DataFrame(gaps))+'''<p>차이는 percentage point(pp), A−B 기준이다.
두 평가는 Test 집합이 서로 다르고 독립적인 대조실험이 아니다. A는 모든 Batch에서 학습하며 Train 표본도 더 많다.
B_early는 445개, B_history는 3,275개, A는 8,346개로 학습량·클래스 구성·시기 범위가 함께 바뀐다.
따라서 이 차이를 드리프트의 순수 효과, 인과 효과, 통계적으로 유의한 차이라고 해석하지 않는다.</p>
<p>B_early와 B_history의 전체 pooled Test 구간도 다르다. 두 B 조건을 직접 비교하려면 위의 공통 Batch 6–10 결과를 우선 참조한다.</p>''')
    section('8. 모델 성능 차이에 대한 해석','<ul>'+''.join('<li>'+html.escape(item)+'</li>' for item in observations)+'''</ul>
<p>이 수치는 고정한 기본 조건에서의 관찰이다. 선형 경계, 비선형 커널, 트리 앙상블의 표현 방식과 전처리의 차이가 결과에 영향을 줄 수 있지만,
개별 요인의 효과를 분리하는 ablation 실험을 수행하지 않았으므로 차이의 원인을 특정하지 않는다.
새 Batch에서의 낮은 점수나 큰 산포는 배포 안정성 검토의 근거이며 성능이 낮다는 이유로 결과를 바꾸지 않았다.</p>''')
    section('9. 데이터 및 평가 방법의 한계','''<p>Batch는 불규칙한 수집 구간이며 측정별 timestamp·농도·환경·센서 관리 기록이 없다.
같은 가스 안의 농도 구성, 실험 조건, 클래스 구성, 학습량, 센서 변화 모두 성능 차이에 관여할 수 있다.
정확 중복이 없더라도 근접 반복 측정이나 수집 의존성은 배제되지 않는다.
랜덤 분할은 독립 표본 가정이 약해질 수 있으며, 이미 EDA로 전체 분포를 관찰했다는 한계가 있다.</p>
<p>학습 크기를 맞추는 대조실험, 반복 랜덤 시드, 신뢰구간/유의성 검정은 이번에 수행하지 않았다.
시간순 평가는 한 고정 초기창과 한 보조창이며 모든 가능한 시간 분할을 포괄하지 않는다.
Batch 3–5의 Toluene 누락 및 일부 소수 클래스의 작은 support 때문에 macro 지표의 비교 조건을 확인해야 한다.
같은 Test를 반복 검토한 뒤 다음 실험을 정하면 선택 편향이 생길 수 있어 새 독립 자료가 필요하다.</p>''')
    section('10. 다음 단계 개선 방향','''<p>다음에는 Train 데이터만 사용해 학습량을 맞춘 대조실험, 과거→미래 확장 창 검증, 클래스별 오류 분석을 사전에 설계할 수 있다.
이후 튜닝이 필요하면 내부 시간순 Validation 범위 안에서 동일 예산으로 수행하고 외부 Test를 고정한다.
농도·환경 메타데이터 확보, class_weight/재표본화, 강건 스케일링, 드리프트 적응은 별도 실험으로 다루며 누수 방지 원칙을 유지한다.</p>
<p>재현: 프로젝트 루트에서 <code>.venv\\Scripts\\python.exe -m src.train_models</code>,
검증은 <code>.venv\\Scripts\\python.exe -m pytest -q</code>.
models/에 파이프라인 9개를 .joblib으로 저장했다. 전처리와 모델을 함께 저장하며 Validation/Test로 재학습하지 않았다.
개별 예측·혼동행렬·지표·분할·환경은 outputs/model_comparison/에 보존한다.
원본 데이터 및 기존 EDA 파일의 실행 전후 SHA-256 일치를 확인했다.
최종 모델 선정·Commit·Push는 하지 않았다.</p>
<p>출처: <a href="https://archive.ics.uci.edu/dataset/224/gas+sensor+array+drift+dataset">UCI Dataset 224</a>.
본 보고서의 모든 성능 수치는 저장된 실제 예측에서 계산했다.</p>''')
    document='''<!doctype html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gas Sensor Drift — 모델 성능 비교</title><style>
body{font-family:"Malgun Gothic",Arial,sans-serif;max-width:1260px;margin:32px auto;padding:0 24px;background:#f6f8fc;color:#20344a;line-height:1.75}
h1,h2{color:#164a72}section{background:#fff;border:1px solid #dce5ef;border-radius:10px;padding:24px;margin:24px 0;overflow:hidden}
.table{overflow-x:auto;margin:16px 0}table{border-collapse:collapse;font-size:13px;white-space:nowrap}th,td{padding:7px 9px;border:1px solid #dce5ef;text-align:right}
th{background:#edf4fa}img{max-width:100%;height:auto}figure{margin:24px 0}figcaption{font-size:13px;color:#536a7e}
pre{white-space:pre-wrap;font-size:13px}details{padding:12px 0}summary{cursor:pointer;color:#165d87}code{background:#edf4fa;padding:3px}a{color:#165d87}
</style></head><body><h1>Gas Sensor Drift Classification</h1><p>모델 학습 및 성능 비교 · 고정 기준선 실험 · 최종 모델 선정 없음</p>'''
    document+='<p>실행 시각(서울): '+html.escape(manifest['generated_at_seoul'])+'</p>'+''.join(sections)+'</body></html>'
    (ROOT/'reports'/'model_comparison_report.html').write_text(document,encoding='utf-8')
