# 시간순 확장 실험의 계산값과 해석을 HTML 보고서로 정리

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

OUT = ROOT / 'outputs/temporal_expansion'


# 표의 소수와 HTML 특수문자 정리
def table(data):
    return data.to_html(index=False, escape=True, float_format=lambda x: f'{x:.4f}')


# 그래프 파일과 보고서 내 이미지 함께 저장
def figure(name, fig):
    fig.tight_layout()
    fig.savefig(OUT / f'{name}.png', dpi=150)
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=120)
    plt.close(fig)
    encoded = base64.b64encode(buffer.getvalue()).decode('ascii')
    return f'<img alt="{html.escape(name)}" src="data:image/png;base64,{encoded}">'


# 기존 평가와 구분한 신규 실험 보고서 작성
def build_report(plan, validation, records, decision, metrics, classes, summary):
    validation = validation.merge(
        pd.DataFrame(records)[['trial_id', 'scaler', 'class_weight', 'fit_seconds']],
        on='trial_id', validate='one_to_one',
    )
    sections = []

    def section(title, body):
        sections.append(f'<section><h2>{title}</h2>{body}</section>')

    section('1. 실험 배경 및 목적', '<p>학습 범위를 Batch 1–3에서 1–6으로 확장했을 때 '
            '동일 미래 Batch에서 성능이 달라지는지 확인한다. 기존 설정의 통제 비교와 '
            '조건 B의 소규모 개선 실험을 구분한다. 실제 계산값은 표·그래프로, 해석은 본문으로 표시한다.</p>')
    section('2. 기존 평가 자료 재지정과 한계', '<p><strong>기존 자료를 재사용한 회고적·탐색적 평가다. '
            '독립적인 최종 Test 성능이 아니다.</strong> 과거 평가 결과를 이미 관찰했으므로 '
            '현재 분할 내부의 정보 차단만으로 연구 전체의 선택 편향을 제거할 수 없다. '
            '이전 1–5단계 결과와 모델은 보존한다.</p>')
    counts = pd.read_csv(OUT / 'batch_class_counts.csv').pivot(
        index='batch', columns='gas', values='n').fillna(0).astype(int)
    counts.columns = [GASES[int(x)] for x in counts.columns]
    counts['total'] = counts.sum(axis=1)
    audit = json.loads((OUT / 'split_audit.json').read_text(encoding='utf-8'))
    split = pd.DataFrame([{k: v for k, v in row.items() if k != 'class_counts'} for row in audit])
    section('3. 데이터 분할 및 클래스 분포', table(split) + table(counts.reset_index()) +
            '<p>조건 A/B는 같은 Validation 7–8과 평가 9–10을 사용한다. '
            '각 분할 및 미래 Batch에 6종이 모두 존재한다. Batch 8은 294개, Toluene 18개로 작다. '
            '학습 표본 수·가스 구성·수집 시기가 함께 변하므로 차이를 데이터 양 하나의 효과로 해석하지 않는다.</p>')
    deltas = []
    for family in ['LR', 'RF', 'SVM']:
        for partition in ['validation', 'evaluation']:
            a = summary[(summary.trial_id == f'A_{family}_base') &
                        (summary.partition == partition)].iloc[0]
            b = summary[(summary.trial_id == f'B_{family}_base') &
                        (summary.partition == partition)].iloc[0]
            row = dict(family=family, partition=partition)
            for key in ['equal_batch_macro_f1', 'pooled_macro_f1', 'toluene_recall',
                        'acetaldehyde_recall', 'other_four_f1']:
                row[key + '_A'] = a[key]
                row[key + '_B'] = b[key]
                row[key + '_delta_pp'] = 100 * (b[key] - a[key])
            deltas.append(row)
    delta = pd.DataFrame(deltas)
    delta.to_csv(OUT / 'expansion_deltas.csv', index=False, encoding='utf-8')
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for ax, part in zip(axes, ['validation', 'evaluation']):
        sub = delta[delta.partition == part]
        x = np.arange(3)
        for offset, condition in [(-.18, 'A'), (.18, 'B')]:
            ax.bar(x + offset, sub[f'equal_batch_macro_f1_{condition}'], .36, label=condition)
        ax.set(xticks=x, xticklabels=sub.family, ylim=(0, 1), xlabel='Model family',
               ylabel='Equal-batch Macro F1', title=f'Training range: {part}')
        ax.legend(title='Train condition')
    section('4. 학습 범위 확장 전후 비교', figure('training_range_comparison', fig) + table(delta) +
            '<p>위 차이는 동일한 기본 설정과 미래 Batch를 사용한 계산값이다. '
            'Toluene 학습 표본은 79→546개, Acetaldehyde는 379→484개다. '
            'Batch 6의 새로운 시기·조건에 대한 노출 효과와 표본 증가 효과를 분리할 수 없다.</p>')
    columns = ['trial_id', 'scaler', 'class_weight', 'val_equal_batch_macro_f1',
               'val_pooled_macro_f1', 'val_toluene_recall', 'val_acetaldehyde_recall',
               'val_min_class_recall', 'val_other_four_f1', 'fit_seconds']
    section('5. 세 모델 및 개선 설정 비교', table(validation[columns]) +
            '<p>총 17회 Fit: A/B 기본 6개, B 가중치·스케일러 5개, '
            '초기 Validation 대표에 제한적 파라미터 6개를 추가했다. '
            '조합을 전부 탐색하지 않았으므로 개선 방법의 독립 효과나 전역 최적을 주장할 수 없다. '
            'LR/SVM은 Train 기준 스케일링, RF는 무스케일이다. 모든 모델은 Train median 결측값 처리와 '
            '동일 특징 128개를 사용한다. PCA·특징 선택·Validation 합산 재학습은 하지 않았다.</p>')
    selected = decision['family_representatives']
    chosen = summary[summary.trial_id.isin(selected)]
    improvements = []
    for trial in selected:
        family = trial.split('_')[1]
        for part in ['validation', 'evaluation']:
            a = summary[(summary.trial_id == f'B_{family}_base') & (summary.partition == part)].iloc[0]
            b = chosen[(chosen.trial_id == trial) & (chosen.partition == part)].iloc[0]
            improvements.append(dict(
                trial_id=trial, partition=part,
                macro_delta_pp=100 * (b.equal_batch_macro_f1 - a.equal_batch_macro_f1),
                toluene_recall_delta_pp=100 * (b.toluene_recall - a.toluene_recall),
                acetaldehyde_recall_delta_pp=100 * (b.acetaldehyde_recall - a.acetaldehyde_recall),
                other_four_f1_delta_pp=100 * (b.other_four_f1 - a.other_four_f1),
            ))
    improvement = pd.DataFrame(improvements)
    improvement.to_csv(OUT / 'improvement_deltas.csv', index=False, encoding='utf-8')
    per_class = classes[(classes.trial_id.isin(selected)) & (classes.scope == 'pooled')]
    zero = per_class[(per_class.support > 0) & (per_class.recall == 0)]
    section('6. Toluene·Acetaldehyde 및 클래스 균형', table(chosen) + table(improvement) +
            table(per_class[['trial_id', 'partition', 'gas', 'support', 'precision', 'recall', 'f1']]) +
            '<p>계산 결과 Recall=0인 후보·클래스 목록:</p>' +
            (table(zero[['trial_id', 'partition', 'gas', 'support', 'recall']]) if len(zero) else '<p>없음.</p>') +
            '<p>일부 가스 개선만으로 6종의 안정적 분류를 달성했다고 결론 내리지 않는다. '
            '나머지 4종 평균 F1 보호 조건은 개별 가스의 악화를 모두 막는 보장은 아니다.</p>')
    batch = metrics[(metrics.trial_id.isin(selected)) & (metrics.scope == 'batch')]
    fig, ax = plt.subplots(figsize=(10, 4))
    for trial in selected:
        sub = batch[batch.trial_id == trial].sort_values('batch')
        ax.plot(sub.batch, sub.macro_f1, marker='o', label=trial)
    ax.axvline(8.5, linestyle='--', color='gray')
    ax.set(title='Selected candidates by chronological batch', xlabel='Batch number',
           ylabel='Macro F1 (six classes)', xticks=[7, 8, 9, 10], ylim=(0, 1))
    ax.legend(fontsize=8)
    cm_data = pd.read_csv(OUT / 'confusion_matrices.csv')
    images = figure('candidate_batch_scores', fig)
    for part in ['validation', 'evaluation']:
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        for ax, trial in zip(axes, selected):
            cm = cm_data[(cm_data.trial_id == trial) & (cm_data.partition == part) &
                         (cm_data.scope == 'pooled')].pivot(
                             index='true_class', columns='predicted_class', values='count').to_numpy()
            image = ax.imshow(cm, cmap='Blues')
            for i in range(6):
                for j in range(6):
                    ax.text(j, i, str(cm[i, j]), ha='center', va='center', fontsize=8)
            ax.set(title=trial, xlabel='Predicted gas', ylabel='Actual gas',
                   xticks=range(6), yticks=range(6),
                   xticklabels=list(GASES.values()), yticklabels=list(GASES.values()))
            ax.tick_params(axis='x', rotation=75)
            fig.colorbar(image, ax=ax, shrink=.6, label='Sample count')
        images += figure(f'confusion_{part}', fig)
    section('7. Batch별 분류 성능 및 오분류', images +
            table(batch[['trial_id', 'partition', 'batch', 'n', 'macro_f1',
                         'toluene_recall', 'acetaldehyde_recall', 'min_class_recall']]) +
            '<p>동일 가중 평균은 작은 Batch 8·9에도 같은 비중을 준다. '
            'pooled 지표는 큰 Batch 7·10의 영향을 더 받는다. 두 방식 모두 보고하며 '
            '두 Batch의 표준편차를 장기 안정성의 확정 증거로 보지 않는다.</p>')
    section('8. 선정 후보와 선정 근거',
            f'<p><strong>Validation 우선 후보: {html.escape(decision["priority_candidate"])}</strong>. '
            f'근접 공동 후보: {html.escape(str(decision["close_joint_candidates"]))}. 최종 확정 모델은 아니다.</p>' +
            '<p>주 지표는 Validation Batch별 Macro F1 동일 가중 평균. 나머지 4종 F1의 '
            '동일 계열 B 기본 대비 3pp 초과 하락 설정은 제외한다. 최고 주 지표 0.5pp 이내에서 '
            '두 집중 가스의 최소 F1 → 최저 클래스 Recall → pooled Macro F1 → 작은 Batch SD → '
            '고정 순서로 결정한다. 근접 범위는 유의성 검정이 아니다.</p>' +
            table(validation[validation.trial_id.isin(selected)][columns]) +
            table(pd.DataFrame(records)[['trial_id', 'fit_seconds', 'validation_predict_seconds',
                                         'model_bytes', 'support_vectors', 'tree_count']]) +
            '<p>학습·추론 시간은 현재 환경의 단일 실행값이며 전용 벤치마크가 아니다. '
            '평가 점수로 후보나 하이퍼파라미터를 변경하지 않았다.</p>')
    section('9. 데이터 누수 및 보존 검사', '<p>Train/Validation/평가 간 행·정확 특징 중복 0건. '
            '동일 특징의 근접 표본이나 측정 세션 의존성은 정확 중복 검사만으로 배제할 수 없다. '
            '스케일러·결측값 처리는 각 Train만 Fit. 선정 시각·선정 파일 SHA와 평가 시작 시각을 '
            'evaluation_gate.json에 기록한다. 기존 파일 및 원본 해시 비교는 run_manifest.json에 기록한다. '
            '전체 테스트 실행 결과는 outputs/temporal_expansion/tests.txt와 test_results.xml에서 확인한다. '
            '과거 소스 해시 불일치와 과거 기록의 누락 임시 파일 관련 기존 실패는 임의 수정하지 않는다.</p>')
    section('10. 해석의 한계 및 독립 검증 조건', '<p>차이는 센서 드리프트, 농도·측정 환경 변화, '
            '학습 시기·표본 수·클래스 구성, 모델의 일반화 한계가 함께 관련될 수 있다. '
            '원인을 드리프트 하나로 확정할 수 없다. Stage 5는 370개 Train과 다른 분할을 사용했으므로 '
            '그 점수와 현재 점수의 차이를 통제된 개선 효과로 제시하지 않는다. '
            '새로운 측정 시기의 미관찰 자료와 농도·환경·세션 정보를 확보하고, '
            '모델·전처리·선정 규칙을 고정한 뒤 독립 평가해야 한다.</p>')
    document = '<!doctype html><html lang="ko"><meta charset="utf-8"><title>시간순 확장 학습 실험</title>'
    document += '<style>body{font:16px/1.6 sans-serif;max-width:1500px;margin:30px auto;padding:20px}'
    document += 'section{overflow-x:auto;margin:35px 0}table{border-collapse:collapse;font-size:12px}'
    document += 'td,th{border:1px solid #bbb;padding:6px}img{max-width:100%}h1,h2{color:#173a58}</style>'
    document += '<h1>6단계: 시간순 확장 학습 및 가스 분류 성능 개선</h1>' + ''.join(sections) + '</html>'
    (ROOT / 'reports/temporal_expansion_report.html').write_text(document, encoding='utf-8')
    text = '# 시간순 확장 실험 후보 선정 근거\n\n기존 자료를 재사용한 탐색적 결과. 최종 확정 모델 아님.\n\n'
    text += f'Validation 우선 후보: **{decision["priority_candidate"]}**\n\n'
    text += f'근접 공동 후보: {decision["close_joint_candidates"]}\n\n'
    text += '사전 선정 규칙은 temporal_expansion_protocol.md 및 experiment_plan.json 참조.\n'
    text += 'Batch 9–10 평가 전에 selection_frozen.json과 모델 바이트를 고정했음.\n\n'
    text += '## Validation 선정 근거\n\n```text\n' + validation[
        validation.trial_id.isin(selected)][columns].to_string(index=False) + '\n```\n\n'
    text += '## 선정 이후 탐색적 평가\n\n```text\n' + chosen.to_string(index=False) + '\n```\n\n'
    text += '## 학습 범위 차이\n\n```text\n' + delta.to_string(index=False) + '\n```\n\n'
    text += '기본 설정 A/B 비교만 학습 범위의 통제 비교임. 표본 수·가스 구성·시기가 함께 변함.\n'
    text += 'Batch 8 Toluene 18개, Validation 2개 Batch만으로 장기 안정성을 확정할 수 없음.\n'
    text += '0.5pp 근접 규칙은 통계적 동등성 기준이 아님. 개별 클래스와 최저 Recall 검토 필요.\n'
    text += '독립 검증에는 새 시기의 미관찰 데이터, 농도·환경 기록 및 사전 고정된 평가가 필요함.\n'
    (ROOT / 'reports/temporal_expansion_model_selection.md').write_text(text, encoding='utf-8')
