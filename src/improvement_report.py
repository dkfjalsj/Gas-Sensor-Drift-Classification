# 개선 실험의 Validation 선정 근거와 탐색적 Test 결과 보고서 생성
# 후보 순위는 고정한 Validation 결정만 사용

import base64
import html
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .data import ROOT, GASES
from .improve_models import OUT, FAMILIES


# 긴 표를 가로 스크롤로 표시
def table(frame):
    return '<div class="table">' + frame.to_html(
        index=False, border=0, na_rep='NA', float_format=lambda value: f'{value:.4f}'
    ) + '</div>'


# 실제 저장된 결과로만 그래프·HTML·선정 근거 작성
def build_report(plan, assignments, validation, records, decision, metrics, classes, stability, baseline):
    figures = {}
    folder = OUT / 'figures'
    folder.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'axes.grid': True, 'grid.alpha': .2})

    # 외부 파일 없이 볼 수 있는 보고서 이미지 생성
    def save(fig, name, caption):
        fig.tight_layout()
        path = folder / f'{name}.png'
        fig.savefig(path, dpi=130, bbox_inches='tight')
        plt.close(fig)
        figures[name] = '<figure><img alt="' + html.escape(caption) + '" src="data:image/png;base64,' + base64.b64encode(path.read_bytes()).decode() + '"><figcaption>' + html.escape(caption) + '</figcaption></figure>'

    selected = decision['joint_candidates']
    priority = decision['priority_candidate']
    test = metrics[(metrics.partition == 'test') & (metrics.scope == 'pooled')]
    val_columns = ['trial_id', 'family', 'group', 'accuracy', 'macro_f1', 'weighted_f1',
                   'toluene_recall', 'toluene_f1', 'other_five_macro_f1', 'min_class_recall']
    labels = [record['trial_id'] for record in records]
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    ordered = validation.set_index('trial_id').loc[labels]
    colors = ['#c37b36' if name in selected else '#438bad' for name in labels]
    for ax, metric, title in zip(axes, ['macro_f1', 'toluene_f1'],
                               ['Validation macro F1', 'Validation Toluene F1 (support=4)']):
        ax.barh(labels, ordered[metric], color=colors)
        ax.set(title=title, xlabel=metric + ' (0–1)', ylabel='Predefined trial', xlim=(0, 1))
        ax.invert_yaxis()
    save(fig, 'validation_trials', '주황색은 Validation으로 고정한 계열별 공동 후보. Toluene 검증 4개의 Recall은 25pp 단위로 변한다. 주황색이 통계적 우월성을 뜻하지 않는다.')

    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    compare = baseline[baseline.scope == 'common_6_10']
    for ax, metric in zip(axes, ['macro_f1', 'toluene_recall']):
        for offset, exp in [(-.18, 'B_early'), (.18, 'B_history')]:
            values = compare[compare.experiment == exp].set_index('family').loc[FAMILIES, metric]
            bars = ax.bar(np.arange(3) + offset, values, width=.36, label=exp)
            ax.bar_label(bars, fmt='%.3f', fontsize=8)
        ax.set(title='Frozen original models: ' + metric, xlabel='Classifier', ylabel=metric,
               xticks=range(3), xticklabels=['LR', 'RF', 'SVM'], ylim=(0, 1.06))
        ax.legend(fontsize=8)
    save(fig, 'frozen_expansion', '실험 B: 저장 모델의 기존 Train Batch 1→1–3 고정 비교. 공통 미래 Batch 6–10의 동일 표본만 비교했다. 과거 Test를 새 학습·튜닝에 넣지 않았으며 이 모델들은 새 후보 선정에 사용하지 않았다.')

    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    candidate_test = test[test.trial_id.isin(selected)].set_index('trial_id').loc[selected]
    candidate_val = validation[validation.trial_id.isin(selected)].set_index('trial_id').loc[selected]
    for ax, metric in zip(axes, ['macro_f1', 'toluene_recall']):
        positions = np.arange(3)
        ax.bar(positions - .18, candidate_val[metric], width=.36, label='Validation (selection)')
        ax.bar(positions + .18, candidate_test[metric], width=.36, label='Seen Test (exploratory)')
        ax.set(title='Frozen candidates: ' + metric, xlabel='Validation-selected joint candidate',
               ylabel=metric, xticks=positions, xticklabels=selected, ylim=(0, 1.05))
        ax.tick_params(axis='x', rotation=20)
        ax.legend(fontsize=8)
    save(fig, 'candidate_generalization', '후보 결정 이후 계산한 Test. Test 성능을 보고 후보나 파라미터를 변경하지 않았다. Validation은 Batch 2, Test는 Batch 3–10이며 관측 시기·구성이 다르다.')

    fig, axes = plt.subplots(1, 2, figsize=(16, 5))
    for ax, metric in zip(axes, ['macro_f1', 'toluene_recall']):
        for trial in selected:
            sub = metrics[(metrics.trial_id == trial) & (metrics.partition == 'test') &
                          (metrics.scope == 'batch')].sort_values('batch')
            ax.plot(sub.batch, sub[metric], marker='o', label=trial)
        ax.set(title='Exploratory Test by batch: ' + metric, xlabel='Batch (ordered category)',
               ylabel=metric, xticks=range(3, 11), ylim=(-.01, 1.02))
        ax.axvspan(5.5, 10.5, color='#edf4fa', alpha=.5)
        ax.legend(fontsize=8)
    save(fig, 'candidate_batches', 'Toluene이 없는 Batch 3–5의 Recall은 NA로 끊었다. 6종이 공통 존재하는 Batch 6–10의 동일 가중 변동을 별도 표에 제공한다. 이 변동은 선정 후 설명용이다.')

    matrices = pd.read_csv(OUT / 'confusion_matrices.csv')
    fig, axes = plt.subplots(3, 2, figsize=(14, 17))
    for row, trial in enumerate(selected):
        for col, part in enumerate(['validation', 'test']):
            sub = matrices[(matrices.trial_id == trial) & (matrices.partition == part) &
                           (matrices.scope == 'pooled')]
            values = sub['count'].to_numpy().reshape(6, 6)
            fractions = values / values.sum(axis=1, keepdims=True)
            ax = axes[row, col]
            im = ax.imshow(fractions, vmin=0, vmax=1, cmap='Blues')
            for i in range(6):
                for j in range(6):
                    ax.text(j, i, f'{values[i,j]}\n{fractions[i,j]:.2f}', ha='center', va='center',
                            fontsize=7, color='white' if fractions[i,j] > .5 else 'black')
            ax.set(title=f'{trial}: {part}', xlabel='Predicted gas class', ylabel='True gas class',
                   xticks=range(6), xticklabels=GASES.values(),
                   yticks=range(6), yticklabels=GASES.values())
            ax.tick_params(axis='x', rotation=40)
            ax.grid(False)
            fig.colorbar(im, ax=ax, label='Within-true-class fraction', fraction=.046)
    save(fig, 'candidate_confusion', '행=True, 열=Predicted. 각 칸은 개수와 실제 클래스 내 비율이다. 전체 14회 실험의 혼동행렬·클래스별 지표도 CSV에 저장했다.')

    cost_rows = []
    times = pd.read_csv(OUT / 'prediction_times.csv').set_index('trial_id')
    for record in records:
        cost_rows.append(dict(
            trial_id=record['trial_id'], fit_seconds=record['fit_seconds'],
            validation_predict_seconds=record['validation_predict_seconds'],
            test_predict_seconds=times.loc[record['trial_id'], 'predict_seconds'],
            test_predict_ms_per_1000=times.loc[record['trial_id'], 'predict_ms_per_1000'],
            **record['complexity'],
        ))
    costs = pd.DataFrame(cost_rows)
    costs.to_csv(OUT / 'cost_summary.csv', index=False, encoding='utf-8')
    improvements = []
    for record in records:
        current = test[test.trial_id == record['trial_id']].iloc[0]
        strict_base_id = {'LogisticRegression': 'LR_base', 'RandomForest': 'RF_base', 'SVM_RBF': 'SVM_base'}[record['family']]
        strict_base = test[test.trial_id == strict_base_id].iloc[0]
        original = baseline[(baseline.family == record['family']) &
                            (baseline.experiment == 'B_early') & (baseline.scope == 'all_test')].iloc[0]
        improvements.append(dict(
            trial_id=record['trial_id'], group=record['group'],
            test_macro_f1=current.macro_f1, test_toluene_recall=current.toluene_recall,
            test_toluene_f1=current.toluene_f1, test_other_five_f1=current.other_five_macro_f1,
            macro_f1_delta_vs_strict_base=current.macro_f1 - strict_base.macro_f1,
            toluene_recall_delta_vs_strict_base=current.toluene_recall - strict_base.toluene_recall,
            other_five_delta_vs_strict_base=current.other_five_macro_f1 - strict_base.other_five_macro_f1,
            macro_f1_delta_vs_old_early=current.macro_f1 - original.macro_f1,
            toluene_recall_delta_vs_old_early=current.toluene_recall - original.toluene_recall,
        ))
    delta = pd.DataFrame(improvements)
    delta.to_csv(OUT / 'improvement_deltas.csv', index=False, encoding='utf-8')

    rationale = '''# 개선된 모델 후보 선정 근거

이 모델들은 최종 확정 모델이 아닌 탐색적 검증 후보다.
사용자 확인에 따라 모든 과거 Test 행을 새 Train/Validation에서 제외했다.
새 Train=Batch 1의 370개(Toluene 59), Validation=Batch 2의 1,022개(Toluene 4).
새 Batch 확장 학습은 금지 조건과 충돌하므로 저장 모델의 고정 비교로만 수행했다.

## 선정 시점과 기준
Validation 결정 시각: {time}
우선 검증 후보: **{priority}**
공동 검증 후보: {candidates}

계열별 기본 모델보다 다른 5종 Validation 평균 F1이 3pp 초과 악화된 설정은 제외했다.
가장 높은 Validation macro-F1의 1pp 이내 설정에서 Toluene F1, Recall,
다른 5종 F1, 전체 macro-F1, 고정 순서로 대표를 골랐다.
3pp/1pp는 실행 전에 기록한 탐색 규칙이며 업무 허용오류·유의성 기준은 아니다.
Validation Toluene 4개로는 견고한 단일 우승 모델 판단이 어려워 세 계열 대표를 공동 검증 후보로 유지했다.
공동 후보가 동등한 성능이라는 뜻은 아니다. 우선 검증 순서는 대표들의 Validation macro-F1에 따른다.

## Validation 근거
```text
{validation}
```

## 탐색적 Test 결과 (선정 후 확인)
```text
{test}
```

Test 평가 전에 validation_decisions.json과 모델 해시를 고정했다.
Test 성능이나 Batch SD를 보고 후보·파라미터를 바꾸지 않았다.
Validation은 단일 Batch이므로 Batch 간 안정성을 선정 근거로 측정할 수 없었다.
Test의 6–10 SD는 설명용이며 안정성은 신규 시기의 자료로 추가 검증해야 한다.
기존 Test를 재사용한 이번 평가는 독립 성능이 아니다.
Toluene 검증 4개와 기존 전체 EDA·Test 관찰에 의한 선택 편향을 명시한다.
Toluene 개선이 다른 가스 악화와 맞바뀌는지는 improvement_deltas.csv와 클래스별 표를 함께 확인한다.
개선이 없거나 여전히 특정 가스에서 실패하면 이를 그대로 보고하며 운영 모델로 확정하지 않는다.
'''.format(
        time=decision['frozen_at_seoul'], priority=priority, candidates=', '.join(selected),
        validation=validation[validation.trial_id.isin(selected)][val_columns].to_string(index=False),
        test=candidate_test[['accuracy', 'macro_f1', 'weighted_f1', 'toluene_recall', 'toluene_f1', 'other_five_macro_f1']].to_string(),
    )
    (ROOT / 'reports/model_selection_rationale.md').write_text(rationale, encoding='utf-8')

    sections = []
    def section(title, body):
        sections.append('<section><h2>' + title + '</h2>' + body + '</section>')

    section('1. 실험 목적과 데이터 사용 원칙', '''<p>미래 Batch의 6종 분류 및 Toluene 실패 개선을 검토한다.
기존 EDA·모델 비교·진단·Toluene 보고서와 보존 검사 제안, 학습 코드와 저장 모델을 확인했다.
분석 시작 전에 과거 Test 전체가 Batch 3–10을 포함한다는 충돌을 확인했고,
사용자는 과거 Test 일부를 개발 자료로 재지정하지 않고 <b>엄격 분리 유지</b>를 선택했다.</p>
<p>따라서 이번 새 학습의 범위가 제한된다. 성능을 높이기 위해 이 원칙을 완화하거나 결과에 맞춰 분할을 바꾸지 않았다.
사전 계획은 model_improvement_protocol.md와 experiment_plan.json에 저장했다.</p>''')
    counts = pd.read_csv(OUT / 'split_class_counts.csv')
    section('2. 사전 고정 분할과 누수 점검', table(counts) + '''<p>새 Train=Batch 1의 370개, Validation=Batch 2의 1,022개,
Test=Batch 3–10의 12,221개. Toluene은 각각 59·4·1,754개다.
Train/Validation 모두 6종 존재, 시간 순서 1&lt;2&lt;3–10, 행·정확 특징 중복 없음.
이전 랜덤 Test이기도 한 Batch 1–2의 297개는 새 실험에서 제외했다.</p>
<p>모든 과거 Test 행 ID의 합집합 12,518개가 Train/Validation에 들어오지 않았음을 검사했다.
새 파이프라인의 결측값 처리·스케일링은 Train에만 Fit한다.
Validation을 합친 재학습, 기존 EDA 스케일러·PCA 재사용, 특징 선택, 재표본화는 하지 않았다.</p>
<p>Validation이 시간상 미래인 Batch 2인 것은 정상적인 시간순 검증이다.
문제는 그보다 뒤의 과거 Test를 개발 자료로 사용하는 것이며 이번에는 이를 금지했다.</p>''')
    section('3. 실험 A·B: 기준 재현과 저장 모델의 고정 확장 비교',
            table(pd.read_csv(OUT / 'baseline_reproduction.csv')) + table(baseline) + figures['frozen_expansion'] + '''
<p>기존 시간순 모델 6개의 Validation/Test 예측을 그대로 재현하고 기존 Accuracy·macro-F1·weighted-F1·macro precision/recall과 대조했다.
Train Batch 1→1–3으로 확장한 저장 모델은 공통 미래 6–10에서만 우선 비교한다.
기존 Train Toluene 74→79개, 전체 445→3,275개로 변화했다.</p>
<p><b>실험 B 제한:</b> 과거 Test를 제외하면 새로운 학습 범위 확장은 불가능하다.
따라서 B는 사용자 확인대로 저장 모델의 고정 비교만 실행했다. 이 모델들을 새 후보 선정에 사용하지 않았다.
새 실험과 과거 모델은 Train 표본과 수가 달라 차이를 순수한 전처리·튜닝 효과로 해석하지 않는다.</p>''')
    settings = pd.DataFrame([dict(
        trial_id=r['trial_id'], family=r['family'], group=r['group'], parent=r['parent'],
        scaler=r['scaler'], class_weight=r['class_weight'], parameters=json.dumps(r['overrides']),
        warnings='; '.join(w['category'] + ': ' + w['message'] for w in r['warnings']) or '없음',
    ) for r in records])
    section('4. 실험 C·D·E: 개선 조건과 소규모 탐색', table(settings) + '''
<p>총 14회 Fit: 초기 비교 8개와 후속 6개. class_weight=None/ balanced, LR/SVM Standard/Robust를 별도 비교했다.
RF는 스케일링이 필수적이지 않아 원래 무스케일 기준을 유지했다.
초기 Validation의 계열별 대표를 부모로 정한 후 스케일러·가중치를 고정하고 2개 파라미터 후보만 추가했다.</p>
<p>LR C=0.1/10, RF trees=200 또는 depth=12·leaf=3, SVM C=10 또는 gamma=0.001을 비교했다.
전체 조합을 탐색하지 않았다. RF의 depth·leaf 동시 변경은 개별 효과를 분리하지 못한다.
PCA/특징 선택은 근거와 계산 예산을 고려해 이번에는 실행하지 않았다. 낮은 결과 때문에 탐색 범위를 늘리지 않았다.</p>''')
    section('5. Validation 성능과 후보 결정', figures['validation_trials'] + table(validation[val_columns]) + '''
<p>후보 결정은 Validation만 사용했다. 다른 5종 평균 F1의 3pp 보호 규칙과 근접 macro-F1 1pp 규칙을 사전에 고정했다.
Toluene은 4개뿐이라 Recall 1개 차이가 25pp다. 한 가스의 소수 표본과 단일 Batch만으로 최종 우승을 확정하지 않는다.</p>
<p>Validation은 단일 Batch여서 Batch 간 변동을 측정할 수 없다.
따라서 계열별 대표 3개를 공동 검증 후보로 유지하며 Test 안정성을 보고 순위를 바꾸지 않았다.</p>''')
    section('6. 선정 후 탐색적 Test 및 Toluene 개선', figures['candidate_generalization'] +
            table(test[['trial_id', 'family', 'accuracy', 'macro_f1', 'weighted_f1', 'toluene_recall', 'toluene_f1', 'other_five_macro_f1', 'min_class_recall']]) +
            table(delta) + '''<p>delta 열은 0–1 단위의 차이다. ×100 하면 pp다.
동일 strict Train을 쓰는 기본 모델 대비 차이가 C/D/E의 비교 기준이며,
과거 B_early와의 차이는 Train 구성도 바뀌었다는 혼동이 있다.</p>
<p>모든 Test는 이미 이전 단계에서 관찰한 자료다. 수치는 탐색적 성능이며 독립 최종 평가가 아니다.
Test를 보기 전에 선정 JSON과 모델 해시를 고정했고, 이후 후보·전처리·파라미터를 바꾸지 않았다.
Toluene 개선이 없거나 다른 가스가 악화되면 그 결과를 그대로 제시했다.</p>''')
    section('7. 가스별 성능·Confusion Matrix', figures['candidate_confusion'] +
            table(classes[(classes.trial_id.isin(selected)) & (classes.scope == 'pooled')][[
                'trial_id', 'partition', 'gas', 'support', 'precision', 'recall', 'f1', 'predicted_count']]) + '''
<p>pooled Test/Validation에는 6종이 존재한다. Batch별로는 3–5에 Toluene이 없으므로 그 클래스의 지표는 NA다.
실제 존재 클래스 평균인 macro-F1과 누락 클래스를 0으로 둔 fixed6 macro-F1을 별도 CSV에 제공한다.
오분류를 화학적 유사성이나 센서 드리프트 하나의 증거로 해석하지 않는다.</p>''')
    section('8. Batch별 성능·계산 비용', figures['candidate_batches'] + table(stability) + table(costs) + '''
<p>Batch 안정성 표는 6종이 공통 존재하는 Test Batch 6–10의 동일 가중 mean/SD(ddof=0)/min/max다.
pooled Test 지표와 Batch 평균은 다른 집계다. Batch 3–5의 macro-F1을 클래스 구성이 같은 것처럼 직접 비교하지 않는다.</p>
<p>학습 및 예측 시간은 해당 실행의 파이프라인 전체 시간이며 환경과 부하에 의존한다.
BLAS thread 한도 2, RF의 n_jobs=-1을 유지했다. 압축 모델 크기·트리 수·지지 벡터 수로 복잡도도 기록했다.
비용과 Test 변동은 선정 이후 설명 자료이며 Test에 맞춘 재선정에 사용하지 않았다.</p>''')
    section('9. 공동 후보 선정 근거와 검증 한계', f'''<p><b>우선 검증 후보: {html.escape(priority)}</b>.
공동 후보: {html.escape(', '.join(selected))}. 모두 최종 확정 모델이 아닌 개선 실험 후보다.</p>
<p>이 순서는 Validation으로 정했으며 Test 최고점 순위가 아니다. Toluene 표본 4개의 불확실성과
단일 Validation Batch 때문에 세 계열의 대표를 공동 유지했다. 공동 후보는 동등한 성능이나 배포 적합성을 뜻하지 않는다.</p>
<p>엄격 분리로 인해 최근 Toluene 반응을 새 Train에 포함하지 못했다. 초기 표본만의 튜닝으로 분포 변화가 해결된다고 보장할 수 없다.
이미 전체 EDA와 Test 결과를 관찰했다는 선택 편향도 남는다. 독립적인 신규 시기 자료와 가스별 허용오류 기준이 필요하다.</p>''')
    section('10. 보존·테스트·다음 단계', '''<p>원본과 기존 모델·EDA·보고서·코드·테스트의 실행 전후 해시를 비교한다.
과거 소스 해시 불일치와 현재 없는 임시 파일 후보 참조는 기록을 유지하며 새 결과에 맞춰 갱신하지 않는다.
기존 테스트와 신규 테스트를 모두 실행하고 실제 결과를 outputs/model_improvement/test_results.txt 및 XML에 기록한다.</p>
<p>신규 검사는 저장 모델 재예측, Train 통계 기반 전처리, 과거 Test 제외, 행·특징 중복, Validation 결정 재계산,
Test 이전 선정 고정, 기존 파일 보존을 포함한다. 모델 파일은 models/improvement_strict/에 저장하며 Git 제외 대상이다.</p>
<p>이번 제약 아래 성능 개선이 충분하지 않으면 신규 자료 확보가 다음 우선 과제다.
과거 Test를 개발 자료로 재지정하려면 별도 명시적 허용과 새 평가 설계를 먼저 확정해야 한다.
Commit·Push·최종 확정 모델 선정은 하지 않았다.</p>
<p>재현: <code>.venv\\Scripts\\python.exe -B -m src.improve_models</code>.
같은 산출물이 있으면 덮어쓰기를 거부한다. 같은 분석을 다시 실행하려면 사용자가 별도 보관 경로를 먼저 준비해야 한다.</p>''')
    document = '''<!doctype html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>모델 개선 실험 및 후보 선정</title><style>
body{font-family:"Malgun Gothic",Arial,sans-serif;max-width:1280px;margin:32px auto;padding:0 24px;background:#f6f8fc;color:#20364c;line-height:1.8}section{background:#fff;padding:24px;border:1px solid #dce5ee;margin:24px 0;border-radius:10px}h1,h2{color:#174e75}.table{overflow-x:auto;margin:16px 0}table{font-size:12px;border-collapse:collapse;white-space:nowrap}td,th{border:1px solid #dce5ee;padding:7px;text-align:right}th{background:#edf4fa}img{max-width:100%;height:auto}figure{margin:24px 0}figcaption{font-size:13px;color:#536b80}code{background:#edf4fa;padding:3px}</style></head><body><h1>Gas Sensor 분류 모델 개선 실험 및 공동 후보</h1><p>엄격한 과거 Test 제외 · Validation 선정 · 최종 평가는 탐색적 성능</p>'''
    document += ''.join(sections) + '</body></html>'
    (ROOT / 'reports/model_improvement_report.html').write_text(document, encoding='utf-8')
