# 시기·가스 가중치 실험과 학습 범위 효과의 계산값·한계 보고

import base64
import html
import io
import json

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .data import ROOT, GASES

OUT = ROOT / 'outputs/temporal_weighting'


# 표와 자체 포함 그래프 생성
def table(data):
    return data.to_html(index=False, escape=True, float_format=lambda x: f'{x:.4f}')


def figure(name, fig):
    fig.tight_layout()
    fig.savefig(OUT / f'{name}.png', dpi=150)
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=110)
    plt.close(fig)
    encoded = base64.b64encode(buffer.getvalue()).decode('ascii')
    return f'<img alt="{html.escape(name)}" src="data:image/png;base64,{encoded}">'


# 합산 지표와 Batch 동일 가중 지표 구분
def summarize_evaluation(metrics):
    rows = []
    for config_id, group in metrics.groupby('config_id', sort=False):
        pooled = group[group.fold == 'pooled'].iloc[0]
        batches = group[group.fold != 'pooled']
        rows.append(dict(
            model_id=config_id, train_end=int(pooled.train_end), scheme=pooled.scheme,
            equal_batch_macro_f1=float(batches.macro_f1.mean()),
            sd_batch_macro_f1=float(batches.macro_f1.std(ddof=0)),
            pooled_macro_f1=pooled.macro_f1, accuracy=pooled.accuracy,
            weighted_f1=pooled.weighted_f1,
            pooled_toluene_recall=pooled.toluene_recall, pooled_toluene_f1=pooled.toluene_f1,
            pooled_acetaldehyde_recall=pooled.acetaldehyde_recall,
            pooled_acetaldehyde_f1=pooled.acetaldehyde_f1,
            pooled_min_recall=pooled.min_class_recall,
            worst_batch_class_recall=float(batches.min_class_recall.min()),
            zero_batch_class_pairs=int(sum(len(str(x).split(',')) for x in
                                          batches.zero_recall_classes.dropna())),
            other_four_f1=pooled.other_four_f1,
        ))
    return pd.DataFrame(rows)


# 이미 고정한 후보로만 보고서와 선정 근거 작성
def build_report(plan, decision):
    cv = pd.read_csv(OUT / 'cv_summary.csv')
    fold_metrics = pd.read_csv(OUT / 'fold_metrics.csv')
    fold_classes = pd.read_csv(OUT / 'fold_class_metrics.csv')
    groups = pd.read_csv(OUT / 'weight_group_summary.csv')
    guards = pd.read_csv(OUT / 'guard_checks.csv')
    range8 = pd.read_csv(OUT / 'range_batch8_metrics.csv', dtype={'fold': str})
    range8_classes = pd.read_csv(OUT / 'range_batch8_classes.csv', dtype={'fold': str})
    evaluation = pd.read_csv(OUT / 'evaluation_metrics.csv', dtype={'fold': str})
    eval_classes = pd.read_csv(OUT / 'evaluation_classes.csv', dtype={'fold': str})
    records = pd.DataFrame(json.loads((OUT / 'fit_records.json').read_text(encoding='utf-8')))
    selected = decision['selected_scheme']
    compare = list(dict.fromkeys(['stage6_SVM', 'stage8_HardVoting',
                                  f'train6_{selected}', f'train7_{selected}',
                                  'train6_class_balanced', 'train7_class_balanced']))
    sections = []

    def section(title, body):
        sections.append(f'<section><h2>{title}</h2>{body}</section>')

    section('1. 기존 실험 및 문제 요약',
            '<p>6단계 B_SVM_balanced를 기준으로 학습 정보의 시기·가스 대표성을 검토한다. '
            'Train1–6의 Toluene546개 중467개(85.53%)가 Batch6에 집중된다. '
            '초기1–3 모델의 Toluene 일반화 실패, 7단계의 동일 가스 특징 이동과 공통 실패, '
            '8단계 특징 선택·Hard Voting의 불일관한 미래 개선을 반영했다.</p>'
            '<p>SVM8설정×3Fold=24회 Fit. LR·새 모델·추가 C/gamma 탐색 없음. '
            '모든 설정은128특징, Train 무가중 median imputer·StandardScaler, C1, gamma=scale을 사용한다. '
            '가중치는 분류기에만 적용해 전처리 가중화 효과를 섞지 않았다.</p>')
    formulas = pd.DataFrame([dict(scheme=key, formula=value) for key, value in plan['formulas'].items()])
    section('2. 시기별 가중치 설계와 결과',
            '<p>u는 관찰 Train Batch의 순서0..1이며 실제 경과 시간이 아니다. '
            '선형1+u, 완만한 지수2^u, 최근2Batch만1.75배를 비교한다. '
            '시간 승수는1..2 범위로 제한해 과거 자료를 제외하지 않는다.</p>' +
            table(formulas) + table(cv[cv.config_id.isin(
                ['class_balanced', 'time_linear', 'time_exp', 'time_recent'])]) +
            '<p><a href="https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html">'
            'scikit-learn SVC 공식 문서</a>의 클래스·표본별 C 조정에 따라 '
            'class 승수×sample 승수를 유효 가중치로 기록했다. raw 평균으로 정규화해 '
            '유효 가중치 평균1을 유지한다. 동일 C 설정에서 전체 손실 규모 차이를 줄이려는 통제다.</p>')
    fig, axes = plt.subplots(1, 2, figsize=(13, 4))
    for ax, gas in zip(axes, [6, 4]):
        for scheme in ['class_balanced', 'time_linear', 'gas_batch', 'time_gas_batch']:
            data = groups[(groups.fold == 'B') & (groups.gas == gas) & (groups.scheme == scheme)]
            ax.plot(data.batch, data.mean_effective, marker='o', label=scheme)
        ax.set(title=f'Train 1-6: {GASES[gas]}', xlabel='Training batch number',
               ylabel='Mean effective sample weight')
        ax.legend(fontsize=8)
    section('3. 가스별·Batch별 균형 실험',
            figure('effective_weights_by_batch', fig) +
            table(cv[cv.config_id.isin(['class_balanced', 'class_sample', 'gas_batch',
                                      'time_class_shrink', 'time_gas_batch'])]) +
            table(records[['scheme', 'fold', 'class_weight', 'effective_weight_min',
                           'effective_weight_max', 'effective_weight_mean', 'weight_concentration_n']]) +
            '<p>가스·Batch 제곱근 보정 r은0.75..1.5로 제한한다. 셀을 완전히 같은 질량으로 '
            '만들지 않으며 작은 셀의 과대 영향도 제한한다. 존재하지 않는 가스·Batch 표본은 '
            '만들지 않았다. time_class_shrink는 sqrt(c)를 사용해 클래스 보정을 완화한다. '
            'time_gas_batch는 시간 제곱근을 사용해 결합 강도를 제한한다.</p>' +
            table(pd.read_csv(OUT / 'class_sample_equivalence_control.csv')) +
            '<p>class_sample은 balanced 승수를 sample_weight로 옮긴 동등성 대조이며 독립적인 '
            '새 개선 방법으로 세지 않는다. (합w)^2/합w²는 가중치 집중도 요약일 뿐 '
            '시간 의존 자료의 독립 유효 표본 수나 신뢰구간이 아니다. '
            '행별 승수·정규화·effective C는 sample_weights.csv.gz에 기록했다.</p>')
    fig, ax = plt.subplots(figsize=(11, 5))
    x = np.arange(len(cv))
    ax.bar(x, cv.mean_macro_f1, color=['#dd7733' if name == selected else '#397cab' for name in cv.config_id])
    ax.set(xticks=x, xticklabels=cv.config_id, title='Temporal weighting: mean Fold Macro F1',
           xlabel='Weighting scheme', ylabel='Equal-weight mean Macro F1', ylim=(0, 1))
    ax.tick_params(axis='x', rotation=35)
    section('4. 시간순 반복 검증 결과',
            table(pd.read_csv(OUT / 'fold_support.csv')) + figure('cv_weighting_comparison', fig) +
            table(cv) + table(fold_metrics) +
            '<details><summary>Fold별6종 Precision·Recall·F1</summary>' + table(fold_classes) + '</details>'
            '<p>Fold A Train1–3→Validation6, B Train1–6→Validation7, C Train1–7→Validation8. '
            'Train이 겹치므로 독립 반복으로 해석하지 않는다. Fold A Toluene Train79개, '
            'A Validation Acetaldehyde29개, C Validation Toluene18개로 작은 클래스의 불확실성이 크다.</p>')
    baseline_range = range8[range8.config_id == 'class_balanced']
    focused_range = range8[range8.config_id.isin(['class_balanced', selected])]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(baseline_range.fold, baseline_range.macro_f1)
    ax.set(title='Fixed baseline: training expansion on common Batch 8', xlabel='Last training batch',
           ylabel='Batch 8 Macro F1', ylim=(0, 1))
    section('5. 학습 범위 확장 효과',
            figure('range_expansion_batch8', fig) + table(focused_range) +
            table(range8_classes[range8_classes.config_id.isin(['class_balanced', selected])]) +
            '<p>동일한 기본 SVM 설정으로 Train1–6과1–7을 공통미래Batch8에서 비교한다. '
            'Train1–7을 Batch7에서 평가하지 않는다. 가중치 효과는 같은 학습 범위 내부에서 '
            '비교하며 기본 가중치의 확장 효과와 구분한다. Batch8은 이미 개발용 Validation으로 '
            '사용한 자료이며 Toluene18개다. 이 결과로 주 후보의 학습 범위를 선택하지 않았다. '
            'Train5933→9546개와 함께 시기·가스 구성·클래스 균형 승수도 달라진다. '
            '효과를 데이터 양 하나로 해석할 수 없다.</p>')
    selected_class = fold_classes[fold_classes.config_id == selected]
    section('6. 사전 보호 기준과 후보 선정 근거',
            '<p>평균 Macro F1 하락≤0.5pp, Toluene·Acetaldehyde 평균Recall 각각 하락≤3pp, '
            '나머지4종 평균F1 하락≤2pp, 개별4종 평균F1 하락≤5pp, 전체최소Recall 하락≤2pp, '
            '각Fold 최소Recall 하락≤5pp, 새 Recall0 조합 추가 금지를 모두 적용했다. '
            '비기준 설정은0% 조합을 줄이거나 평균Macro F1을0.2pp 이상 높여야 한다.</p>' +
            table(guards) +
            f'<p><b>고정 후보: {html.escape(selected)}</b>. '
            f'기준 유지 여부: {decision["baseline_retained"]}. '
            '보호 통과 설정과 기준 중 최고 평균0.5pp 이내에서 적은0% 조합→높은최소Recall→'
            '높은집중가스최소평균Recall→높은합산Macro F1→낮은Fold SD→고정순서로 결정했다. '
            '모두 실패하면 원래6단계 저장 모델을 유지한다. 보호 수치는 통계적 유의성·운영 기준이 아니다.</p>' +
            '<h3>후보의 Recall0 Fold·가스</h3>' + table(selected_class[selected_class.recall == 0]) +
            '<p>주 후보 Train1–6과 동일 설정의 Train1–7 확장 비교 모델은 평가 전에 함께 고정했다. '
            '이후 평가 결과로 가중치·후보·범위·보호 기준을 변경하지 않았다.</p>')
    summary = summarize_evaluation(evaluation)
    reference = summary[summary.model_id == 'stage6_SVM'].iloc[0]
    summary['equal_macro_delta_vs_stage6_pp'] = 100 * (summary.equal_batch_macro_f1 - reference.equal_batch_macro_f1)
    summary['pooled_macro_delta_vs_stage6_pp'] = 100 * (summary.pooled_macro_f1 - reference.pooled_macro_f1)
    summary.to_csv(OUT / 'evaluation_summary.csv', index=False, encoding='utf-8')
    section('7. Batch 9–10 탐색적 평가',
            '<p><strong>이미 관찰한 기존 Test를 재사용한 회고적·탐색적 평가이며 '
            '독립적인 최종 Test 성능이 아니다.</strong> 후보 동결 시각과 평가 시작·선정 SHA를 '
            'evaluation_gate.json에 기록했다.</p>' +
            '<h3>동일 Train1–6 모델 비교</h3>' + table(summary[(summary.train_end == 6) & summary.model_id.isin(compare)]) +
            '<h3>Train1–7 확장 모델 — 별도 비교</h3>' + table(summary[(summary.train_end == 7) & summary.model_id.isin(compare)]) +
            table(evaluation[evaluation.config_id.isin(compare)]) +
            table(eval_classes[eval_classes.config_id.isin(compare)]) +
            '<details><summary>전체8가중치×2범위 및 기존 모델의 탐색적 결과</summary>' + table(summary) + '</details>' +
            table(pd.read_csv(OUT / 'evaluation_times.csv').query('model_id in @compare')))
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for ax, end in zip(axes, [6, 7]):
        candidates = ['stage6_SVM', f'train{end}_class_balanced', f'train{end}_{selected}']
        for name in dict.fromkeys(candidates):
            sub = evaluation[(evaluation.config_id == name) & (evaluation.fold != 'pooled')].sort_values('fold')
            ax.plot([9, 10], sub.macro_f1, marker='o', label=name)
        ax.set(title=f'Exploratory comparison: Train1-{end}', xlabel='Evaluation batch',
               ylabel='Macro F1', xticks=[9, 10], ylim=(0, 1))
        ax.legend(fontsize=7)
    section('8. 기존 SVM 대비 개선 여부',
            figure('evaluation_range_comparison', fig) +
            '<p>동일 범위의 가중치 차이와 동일 가중치의 범위 차이를 구분한다. '
            '합산 Macro F1은 큰 Batch10의 영향을 많이 받고 동일 가중 평균은 작은 Batch9에도 '
            '같은 비중을 준다. 두 값을 함께 보고하며 낮은 가스별Recall이나0% 실패를 숨기지 않는다. '
            '과거 Fold 선정과 미래 성능이 다르면 그대로 보고한다.</p>')
    matrices = pd.read_csv(OUT / 'evaluation_confusion.csv', dtype={'fold': str})
    labels = list(dict.fromkeys(['stage6_SVM', f'train6_{selected}', f'train7_{selected}']))
    fig, axes = plt.subplots(2, len(labels), figsize=(6 * len(labels), 12), squeeze=False)
    for i, batch in enumerate(['9', '10']):
        for j, name in enumerate(labels):
            cm = matrices[(matrices.config_id == name) & (matrices.fold == batch)].pivot(
                index='actual_id', columns='predicted_id', values='count').to_numpy()
            ax = axes[i, j]
            image = ax.imshow(cm, cmap='Blues')
            for a in range(6):
                for b in range(6):
                    ax.text(b, a, str(cm[a, b]), ha='center', va='center', fontsize=8)
            ax.set(title=f'{name}: Batch {batch}', xlabel='Predicted gas', ylabel='Actual gas',
                   xticks=range(6), yticks=range(6), xticklabels=list(GASES.values()), yticklabels=list(GASES.values()))
            ax.tick_params(axis='x', rotation=65)
            fig.colorbar(image, ax=ax, shrink=.6, label='Sample count')
    section('9. 추가 해석과 검증 한계',
            figure('weighting_confusion_matrices', fig) +
            '<p>가중치는 이미 존재하는 표본의 손실 중요도를 바꿀 뿐, 관찰하지 못한 농도·측정조건이나 '
            '새로운 특징 공간을 생성하지 못한다. 시간 가중치가 과거 Toluene 범위를 약화시킬 수도 있고 '
            '셀 보정은 작은5개 표본의 불확실성을 그대로 가진다. 고정 상한은 과대를 줄일 뿐 이를 해결하지 않는다.</p>'
            '<p>Fold 중첩, 작은 클래스, 과거 여러 단계의 Test 관찰, Batch8의 반복 개발 사용에 따른 '
            '선택 편향이 남는다. 센서 드리프트·농도·환경 변화의 인과 효과는 분리할 수 없다. '
            '전처리·가중치는 Train 정보만 Fit하며 과거 모델과 예측 재현·파일 해시는 별도 검사했다.</p>')
    section('10. 다음 단계와 재현·보존',
            '<p>개선 주장은 평균 점수 외에 집중 가스·최소Recall·새0% 실패·나머지4종 손실을 '
            '함께 충족해야 한다. 이번 범위에서 부족하면 추가 Test 기반 가중치 탐색 대신 '
            '새 시기·농도·환경 대표성 확보와 시간순 중첩 검증을 우선한다. '
            '참조 가스 측정이 있다면 Train 기반 보정의 대조 실험을 별도로 사전 설계할 수 있다.</p>'
            '<p>실행: python -B -X utf8 -m src.temporal_weighting. 기존8단계까지 보존한 복제본에서 '
            '신규 출력 경로가 없는 상태로 재실행한다. 출력이 있으면 덮어쓰지 않고 중단한다. '
            '사전설정 experiment_plan.json, 선정 selection_frozen.json, 보존 run_manifest.json, '
            '전체 테스트 tests.txt·test_results.xml 및 최종 final_verification.json을 제공한다. '
            '기존3건 실패는 그대로 보고하고 신규 실패와 구분한다. Commit·Push 없음.</p>')
    document = '<!doctype html><html lang="ko"><meta charset="utf-8"><title>시간순 학습 가중치 실험</title>'
    document += '<style>body{font:16px/1.6 sans-serif;max-width:1500px;margin:25px auto;padding:20px}'
    document += 'section{overflow-x:auto;margin:35px 0}table{border-collapse:collapse;font-size:12px}'
    document += 'th,td{border:1px solid #bbb;padding:6px}img{max-width:100%}h1,h2{color:#173a58}</style>'
    document += '<h1>9단계: 시간순 학습 데이터 구성 및 가중치 최적화</h1>' + ''.join(sections) + '</html>'
    (ROOT / 'reports/temporal_weighting_report.html').write_text(document, encoding='utf-8')
    text = '# 9단계 모델 선정 근거\n\n'
    text += f'고정 가중치 후보: **{selected}**. 기존 모델 유지: {decision["baseline_retained"]}.\n\n'
    text += '## 사전 계획과 보호 기준\n\n'
    text += 'temporal_weighting_protocol.md와 experiment_plan.json에 학습 전8설정·24회Fit·수식·보호·동점 규칙 고정.\n'
    text += '과거3Fold 동일 가중Macro F1이 주 지표. 보호 미통과 시 기존6단계 SVM 유지.\n'
    text += '주 후보 Train1–6, 동일 가중치의Train1–7은 별도 범위 비교이며 평가 후 후보를 바꾸지 않음.\n\n'
    text += '```text\n' + cv.to_string(index=False) + '\n```\n\n'
    text += '## 보호 통과 여부\n\n```text\n' + guards.to_string(index=False) + '\n```\n\n'
    text += '## 공통 Batch8의 범위 효과\n\n```text\n' + focused_range.to_string(index=False) + '\n```\n\n'
    text += '## 동결 이후 탐색적 평가\n\n```text\n' + summary[
        summary.model_id.isin(compare)].to_string(index=False) + '\n```\n\n'
    text += '기존 Test 재사용의 회고적·탐색적 결과이며 독립 최종 Test가 아님. '
    text += 'Batch8 Toluene18개, Fold A Train Toluene79개. Fold는 독립 반복이 아님.\n\n'
    text += '가중치는 실제Train 클래스·Batch만 사용. c×sample 중복 보정 금지, 유효가중치 평균1. '
    text += '전처리 무가중TrainFit으로 가중치 효과와 분리. 공식 정의: '
    text += '[scikit-learn SVC](https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html).\n\n'
    text += '실행: `.venv\\Scripts\\python.exe -B -X utf8 -m src.temporal_weighting`\n\n'
    text += '테스트: `.venv\\Scripts\\python.exe -B -X utf8 -m pytest -q -p no:cacheprovider '
    text += '--junitxml=outputs/temporal_weighting/test_results.xml`\n'
    (ROOT / 'reports/temporal_weighting_model_selection.md').write_text(text, encoding='utf-8')
