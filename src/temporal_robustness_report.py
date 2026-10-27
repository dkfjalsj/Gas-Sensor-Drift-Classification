# 반복 검증·특징 선택·결합 실험의 계산값과 한계 정리

import base64
import html
import io
import json

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .data import ROOT, FEATURES, GASES

OUT = ROOT / 'outputs/temporal_robustness'


# 표와 그래프를 자체 포함 HTML로 변환
def table(data):
    return data.to_html(index=False, escape=True, float_format=lambda x: f'{x:.4f}')


def figure(name, fig):
    fig.tight_layout()
    fig.savefig(OUT / f'{name}.png', dpi=150)
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=110)
    plt.close(fig)
    return '<img alt="' + html.escape(name) + '" src="data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode() + '">'


# 결과 이후 후보를 바꾸지 않고 관찰값 보고
def build_report(plan, decision):
    cv = pd.read_csv(OUT / 'cv_summary.csv')
    folds = pd.read_csv(OUT / 'fold_metrics.csv')
    fold_classes = pd.read_csv(OUT / 'fold_class_metrics.csv')
    evaluation = pd.read_csv(OUT / 'evaluation_metrics.csv')
    eval_classes = pd.read_csv(OUT / 'evaluation_class_metrics.csv')
    records = json.loads((OUT / 'fit_records.json').read_text(encoding='utf-8'))
    candidate = decision['selected_candidate']
    interesting = list(dict.fromkeys([
        candidate, 'SVM_all', *decision['family_representatives'].values(),
    ]))
    compare = ['stage6_saved_SVM', *interesting]
    sections = []

    def section(title, body):
        sections.append(f'<section><h2>{title}</h2>{body}</section>')

    headline = cv[cv.config_id == candidate].iloc[0]
    section('1. 시간순 반복 검증 설계와 결과',
            '<p>기준은 6단계 B_SVM_balanced. Fold A Train1–3→Validation6, '
            'B Train1–6→Validation7, C Train1–7→Validation8을 고정했다. '
            '각 Train과 Validation에 6종이 모두 있다. A의 Toluene Train79개, '
            'A Validation Acetaldehyde29개, C Validation Toluene18개로 클래스별 표본 제한이 있다.</p>' +
            table(pd.read_csv(OUT / 'fold_support.csv')) +
            '<p>Train 범위가 겹치므로 세 Fold는 독립적인 반복 표본이 아니다. '
            '평균·표준편차는 탐색 요약이며 유의성이나 장기 안정성의 증명으로 해석하지 않는다. '
            '18개 단일 설정×3Fold=54회 분류기 Fit, 결합4개를 포함해 총22개 설정이다.</p>' +
            table(cv) + '<details><summary>Fold별 전체 지표</summary>' + table(folds) + '</details>')
    feature_rows, feature_detail = [], []
    for record in records:
        selected = set(record['selected_features'])
        for feature, score in zip(FEATURES, record['selector_scores']):
            feature_detail.append(dict(config_id=record['config_id'], fold=record['fold'],
                                       feature=feature, selected=feature in selected, selection_score=score))
    pd.DataFrame(feature_detail).to_csv(OUT / 'feature_selection_details.csv', index=False, encoding='utf-8')
    for family in ['LR', 'RF', 'SVM']:
        baseline = cv[cv.config_id == family + '_all'].iloc[0]
        for _, row in cv[cv.config_id.str.startswith(family + '_')].iterrows():
            counts = [len(record['selected_features']) for record in records if record['config_id'] == row.config_id]
            feature_rows.append(dict(
                family=family, config_id=row.config_id, feature_counts_A_B_C=str(counts),
                mean_macro_f1=row.mean_macro_f1,
                delta_macro_pp=100 * (row.mean_macro_f1 - baseline.mean_macro_f1),
                delta_toluene_recall_pp=100 * (row.mean_toluene_recall - baseline.mean_toluene_recall),
                delta_acetaldehyde_recall_pp=100 * (row.mean_acetaldehyde_recall - baseline.mean_acetaldehyde_recall),
                delta_other_four_f1_pp=100 * (row.mean_other_four_f1 - baseline.mean_other_four_f1),
                zero_recall_pairs=row.zero_recall_pairs,
            ))
    feature_effect = pd.DataFrame(feature_rows)
    feature_effect.to_csv(OUT / 'feature_effects.csv', index=False, encoding='utf-8')
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    for ax, family in zip(axes, ['LR', 'RF', 'SVM']):
        data = feature_effect[feature_effect.family == family]
        ax.barh(data.config_id, data.delta_macro_pp)
        ax.axvline(0, color='black', linewidth=.8)
        ax.set(title=f'{family}: feature selection vs all', xlabel='Mean Fold Macro F1 change (pp)',
               ylabel='Feature condition')
    section('2. 특징 선택 전후 비교',
            '<p>분산법은 Train min-max 범위로 단위를 맞춘 분산 상위115개(하위13개 제거). '
            '상관법은 Train |Pearson r|&gt;0.98인 중복 특징을 원래 순서대로 제거한다. '
            '안정성법은 동일 가스의 Train 내부 Batch 평균 이동/전체 Train SD를 그룹 동일 가중으로 '
            '평균해 작은64개를 선택한다. ANOVA SelectKBest는32·64개를 비교한다. '
            '결측값 처리·특징 선택·스케일링은 각 Fold Train만 Fit한다.</p>' +
            figure('feature_selection_effect', fig) + table(feature_effect) +
            '<p>분산이 작거나 시간별 평균 변화가 작아도 가스를 구별하는 능력이 좋다는 보장은 없다. '
            'Train 내부 안정성은 Batch별 가스 표본 수·농도 구성 차이의 영향을 받는다. '
            '과거 Test에서 확인한7단계 특징 목록은 제거 기준으로 사용하지 않았다. '
            '전체6912개 특징 선택·점수 기록은 feature_selection_details.csv에 있다.</p>')
    fig, ax = plt.subplots(figsize=(12, 8))
    ordered = cv.sort_values('mean_macro_f1')
    ax.barh(ordered.config_id, ordered.mean_macro_f1,
            color=['#d96c32' if x == candidate else '#397cab' for x in ordered.config_id])
    ax.set(title='Temporal validation: all 22 settings', xlabel='Mean Fold Macro F1', ylabel='Configuration', xlim=(0, 1))
    section('3. 모델별 개선 결과와 선정 규칙',
            figure('cv_configuration_comparison', fig) +
            '<p>LR balanced C=.1, RF balanced100 trees, SVM balanced C1·gamma=scale을 유지했다. '
            'LR/SVM StandardScaler, RF 무스케일. 이번에는 특징 선택 효과를 분리하기 위해 '
            '추가 하이퍼파라미터 탐색을 하지 않았다.</p>' +
            f'<p><b>평균 점수 최고 설정:</b> {html.escape(decision["raw_mean_leader"])}. '
            f'<b>사전 보호·동점 규칙 적용 후보:</b> {html.escape(candidate)} '
            f'(동일 가중 Macro F1 {headline.mean_macro_f1:.4f}).</p>' +
            '<p>나머지4종 평균F1이 참조보다3pp 초과 하락하거나 개별4종 평균F1이10pp 초과 하락하면 제외한다. '
            '계열 대표의 참조는 해당 all, 전체 후보의 참조는 SVM_all이다. 유효 설정 최고점0.5pp 이내에서 '
            'Recall0 조합 수→최소Recall→집중 가스 최소 평균F1→합산Macro F1→작은SD→고정순서로 선정했다. '
            '0.5pp는 통계적 동등성 기준이 아니다.</p>' +
            table(cv[cv.config_id.isin(interesting)]) +
            '<p>최고 평균 설정과 규칙 적용 후보가 다르면 점수를 숨기거나 평가 결과로 재선정한 것이 아니라 '
            '사전 보호·동점 규칙에 따른 차이다.</p>')
    ensembles = cv[cv.config_id.isin([row['config_id'] for row in decision['ensembles']])]
    section('4. 앙상블 효과', table(ensembles) +
            table(pd.DataFrame(decision['ensembles'])) +
            '<p>Hard Voting 동점은 SVM 예측을 우선한다. 순위 결합은 각 모델 클래스 순위에5..0점을 주고 '
            '동일 가중 또는 SVM2배로 합산한다. 순위 동점은 SVM 순위를 우선한다. '
            '순위 결합은 확률 평균이 아니며 모델 간 점수 크기 정보를 버린다.</p>'
            '<p>SVM probability=False이고 시간순 보정 확률의 품질을 검증하지 않았으므로 '
            'Soft Voting은 실행하지 않았다. 계열 대표 선정과 앙상블 비교에 같은 Fold를 사용한 '
            '비중첩 탐색이므로 앙상블 검증 점수에도 선택 낙관 편향이 남는다. '
            '순위 가중치는 사전 후보1/1/1 및1/1/2만 비교했고9–10으로 결정하지 않았다.</p>')
    focus_classes = fold_classes[fold_classes.config_id.isin(interesting)]
    failures = focus_classes[focus_classes.recall == 0]
    all_failures = fold_classes[fold_classes.recall == 0]
    all_failures.to_csv(OUT / 'zero_recall_fold_classes.csv', index=False, encoding='utf-8')
    section('5. Toluene·Acetaldehyde와 다른 가스의 균형',
            table(focus_classes) + '<h3>대표·후보 설정의 Recall0 Fold·가스</h3>' +
            (table(failures) if len(failures) else '<p>해당 없음.</p>') +
            '<p>평균이 높아도 특정 Fold의0% Recall을 해결하지 못한 설정은 별도로 표시한다. '
            '보호 기준은 Fold 평균 기준이므로 특정 Fold의 개별 가스 악화를 완전히 막지 못한다. '
            '전체 설정의0% 목록도 별도 CSV로 제공한다.</p>')
    eval_summary = []
    for config_id, group in evaluation.groupby('config_id', sort=False):
        batches = group[group.fold != 'pooled']
        pooled = group[group.fold == 'pooled'].iloc[0]
        eval_summary.append(dict(
            config_id=config_id, equal_batch_macro_f1=float(batches.macro_f1.mean()),
            sd_batch_macro_f1=float(batches.macro_f1.std(ddof=0)), pooled_macro_f1=pooled.macro_f1,
            accuracy=pooled.accuracy, weighted_f1=pooled.weighted_f1,
            pooled_toluene_recall=pooled.toluene_recall, pooled_toluene_f1=pooled.toluene_f1,
            pooled_acetaldehyde_recall=pooled.acetaldehyde_recall,
            pooled_acetaldehyde_f1=pooled.acetaldehyde_f1, min_class_recall=pooled.min_class_recall,
            other_four_f1=pooled.other_four_f1,
        ))
    eval_summary = pd.DataFrame(eval_summary)
    base = eval_summary[eval_summary.config_id == 'stage6_saved_SVM'].iloc[0]
    eval_summary['equal_macro_delta_pp'] = 100 * (eval_summary.equal_batch_macro_f1 - base.equal_batch_macro_f1)
    eval_summary['pooled_macro_delta_pp'] = 100 * (eval_summary.pooled_macro_f1 - base.pooled_macro_f1)
    eval_summary.to_csv(OUT / 'evaluation_summary.csv', index=False, encoding='utf-8')
    chosen_eval = evaluation[evaluation.config_id.isin(compare)]
    fig, ax = plt.subplots(figsize=(10, 5))
    for config_id in compare:
        sub = chosen_eval[(chosen_eval.config_id == config_id) & (chosen_eval.fold != 'pooled')].sort_values('fold')
        ax.plot([9, 10], sub.macro_f1, marker='o', label=config_id)
    ax.set(title='Frozen models: exploratory batches 9 and 10', xlabel='Batch number',
           ylabel='Macro F1', xticks=[9, 10], ylim=(0, 1))
    ax.legend(fontsize=8)
    section('6. Batch 9·10 탐색적 평가',
            '<p><strong>기존 Test를 재사용한 회고적·탐색적 평가다. 독립적인 최종 Test가 아니다.</strong> '
            '모든 후보·가중치·선정 모델 해시를 고정한 뒤에만9–10을 예측했다. '
            '최종 평가 모델은 모든 설정에서 Train1–6의 Fold B 모델이며 '
            'Fold C Train1–7이나 Train1–8로 평가용 재학습하지 않았다.</p>' +
            figure('exploratory_batch_scores', fig) + table(chosen_eval) +
            table(eval_classes[eval_classes.config_id.isin(compare)]) +
            '<details><summary>전체 설정의 합산·동일 가중 탐색 지표</summary>' + table(eval_summary) + '</details>')
    matrices = pd.read_csv(OUT / 'evaluation_confusion.csv', dtype={'fold': str})
    fig, axes = plt.subplots(2, 2, figsize=(13, 12))
    for i, batch in enumerate(['9', '10']):
        for j, config_id in enumerate(['stage6_saved_SVM', candidate]):
            cm = matrices[(matrices.config_id == config_id) & (matrices.fold == batch)].pivot(
                index='actual_id', columns='predicted_id', values='count').to_numpy()
            ax = axes[i, j]
            image = ax.imshow(cm, cmap='Blues')
            for a in range(6):
                for b in range(6):
                    ax.text(b, a, str(cm[a, b]), ha='center', va='center', fontsize=8)
            ax.set(title=f'{config_id}: Batch {batch}', xlabel='Predicted gas', ylabel='Actual gas',
                   xticks=range(6), yticks=range(6),
                   xticklabels=list(GASES.values()), yticklabels=list(GASES.values()))
            ax.tick_params(axis='x', rotation=65)
            fig.colorbar(image, ax=ax, shrink=.6, label='Sample count')
    candidate_eval = eval_summary[eval_summary.config_id == candidate].iloc[0]
    section('7. 기존 6단계 SVM 대비 변화',
            table(eval_summary[eval_summary.config_id.isin(compare)]) +
            figure('candidate_baseline_confusion', fig) +
            f'<p><b>계산값:</b> 선정 후보의 동일 가중 평가 Macro F1 변화 '
            f'{candidate_eval.equal_macro_delta_pp:+.2f}pp, 합산 변화 '
            f'{candidate_eval.pooled_macro_delta_pp:+.2f}pp. '
            '좋지 않은 평가 결과가 나오더라도 설정·후보를 바꾸지 않았다. '
            '새 SVM_all의 평가 예측은 기존 저장 SVM과 완전히 일치하는지 검사했다.</p>')
    section('8. 가장 유력한 후보와 검증 한계',
            f'<p><b>과거 Fold 기준 후보: {html.escape(candidate)}</b>. '
            '최종 확정 모델이 아니며9–10 점수로 다시 고르지 않았다. '
            '동일 자료의 여러 단계 결과를 이미 관찰했으므로 분할 내부 누수 차단과 별개로 '
            '연구 전체의 선택 편향이 존재한다. Fold SD는 독립 반복의 불확실성 구간이 아니다.</p>'
            '<p>원본·기존 파일·모델 해시는 보존하며 각 Fold의 Train 행 SHA, 선택 특징, '
            '전처리 통계, Fit 경고, 모델 SHA, 예측을 기록했다. '
            '전체 테스트 결과는 tests.txt·test_results.xml 및 final_verification.json을 참조한다. '
            '기존2건 실패 외에7단계 전체 모델 목록 고정 검사는 승인된 신규 모델 추가로 '
            '실패할 수 있다. 해당 과거 검사와 해시 기록은 변경하지 않는다.</p>')
    section('9. 다음 개선 실험',
            '<p>각 Fold·가스의0% Recall과 다른 가스 손실을 먼저 확인해야 한다. '
            '특징 수를 줄여도 시간순 구별 정보가 사라질 수 있고, 단순 결합은 공통 실패를 '
            '고치지 못할 수 있다. 다음 단계에서는 현재 Test에 맞춘 추가 탐색을 늘리기보다 '
            '가스·농도·시기·측정 환경 대표성 및 새 시기 자료 확보를 우선 검토한다.</p>'
            '<p>확률 결합이 필요하면 Train 내부의 시간순 확률 보정을 별도로 설계하고 '
            '보정 성능을 검증해야 한다. 특징 안정성·스케일링·드리프트 보정의 효과는 '
            '새 참조 측정과 사전 고정된 제한적 대조 실험으로 확인한다. '
            '센서 드리프트를 성능 변화의 유일한 원인으로 단정하지 않는다.</p>')
    document = '<!doctype html><html lang="ko"><meta charset="utf-8"><title>시간순 반복 검증과 특징 개선</title>'
    document += '<style>body{font:16px/1.6 sans-serif;max-width:1500px;margin:25px auto;padding:20px}'
    document += 'section{overflow-x:auto;margin:35px 0}table{border-collapse:collapse;font-size:12px}'
    document += 'th,td{border:1px solid #bbb;padding:6px}img{max-width:100%}h1,h2{color:#173a58}</style>'
    document += '<h1>8단계: 시간순 반복 검증 및 센서 특징 기반 모델 개선</h1>'
    document += ''.join(sections) + '</html>'
    (ROOT / 'reports/temporal_robustness_improvement_report.html').write_text(document, encoding='utf-8')
    text = '# 8단계 후보 선정 근거\n\n'
    text += f'평균 점수 최고 설정: **{decision["raw_mean_leader"]}**\n\n'
    text += f'사전 보호·동점 규칙 적용 후보: **{candidate}**\n\n'
    text += '기준 B_SVM_balanced, 18개 단일 설정×3Fold=54회 Fit, 결합4개 포함22개 설정.\n\n'
    text += '## 과거 Fold 결과\n\n```text\n' + cv.to_string(index=False) + '\n```\n\n'
    text += '## 후보·기준의 평가 결과\n\n```text\n' + eval_summary[
        eval_summary.config_id.isin(compare)].to_string(index=False) + '\n```\n\n'
    text += '## 설정과 한계\n\n'
    text += 'temporal_robustness_protocol.md에 학습 전 분할·예산·보호·동점·최종Train 범위를 고정했음.\n'
    text += '평가 전 selection_frozen.json과 후보 모델 SHA를 저장했으며9–10 결과로 변경하지 않았음.\n'
    text += '각 Fold 특징 선택은 Train 내부만 Fit. 안정성은 Train 동일 가스·Batch 정보만 사용.\n'
    text += '최종 모델은 Fold B Train1–6으로 기존 SVM과 학습 범위를 통제. '
    text += '더 많은 Train으로의 재학습 효과는 이번 실험에 포함되지 않음.\n'
    text += 'Soft Voting은 시간순 확률 품질 미검증으로 미실행. 순위 결합은 확률 평균이 아님.\n'
    text += 'Fold는 학습 자료가 겹치고 계열 대표·결합의 비중첩 탐색이므로 낙관 편향이 남음.\n'
    text += '기존 Test 재사용의 회고적·탐색적 결과이며 독립 최종 성능·확정 모델이 아님.\n\n'
    text += '## 재현 실행\n\n```text\n.venv\\Scripts\\python.exe -B -X utf8 -m src.temporal_robustness\n'
    text += '.venv\\Scripts\\python.exe -B -X utf8 -m pytest -q -p no:cacheprovider '
    text += '--junitxml=outputs/temporal_robustness/test_results.xml\n```\n\n'
    text += '재실행 시1–7단계를 보존한 복제본에서8단계 출력 경로가 없는 상태로 실행해야 함. '
    text += '기존 출력이 있으면 중단하며 삭제·덮어쓰기하지 않음.\n'
    (ROOT / 'reports/temporal_robustness_model_selection.md').write_text(text, encoding='utf-8')
