# Batch별 분류 실패의 관찰값과 해석을 진단 보고서로 정리

import base64
import html
import io

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .data import ROOT, FEATURES, GASES

OUT = ROOT / 'outputs/temporal_failure_diagnostics'
NAMES = ['LR', 'RF', 'SVM']


# 계산표를 UTF-8 HTML로 변환
def table(data):
    return data.to_html(index=False, escape=True, float_format=lambda x: f'{x:.4f}')


# 그래프와 보고서 내 이미지 함께 저장
def figure(name, fig):
    fig.tight_layout()
    fig.savefig(OUT / f'{name}.png', dpi=150)
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=110)
    plt.close(fig)
    encoded = base64.b64encode(buffer.getvalue()).decode('ascii')
    return f'<img alt="{html.escape(name)}" src="data:image/png;base64,{encoded}">'


# 표본별 정답·오답 수와 특징 변화에 근거한 보고서 생성
def build_report(frame, wide, scores, classes, confusion, agreement, shifts,
                 chosen, proximity, dependence):
    sections = []

    def section(title, body):
        sections.append(f'<section><h2>{title}</h2>{body}</section>')

    def counts(batch, gas):
        return confusion[(confusion.batch == batch) & (confusion.actual_id == gas)].pivot(
            index='model', columns='predicted_gas', values='count').reset_index()

    train = frame[frame.batch <= 6]
    train_counts = train.groupby('gas').size()
    train_table = pd.DataFrame([
        dict(gas=GASES[g], train_n=int(train_counts[g]),
             train_fraction=float(train_counts[g] / len(train)),
             batch6_n=int(((train.gas == g) & (train.batch == 6)).sum()),
             batch6_fraction_within_gas=float(((train.gas == g) &
                                             (train.batch == 6)).sum() / train_counts[g]))
        for g in GASES
    ])
    section('1. 분석 목적과 기존 실험 요약',
            '<p>6단계 Validation으로 선정한 SVM과 LR·RF 대표의 실패를 진단한다. '
            'Train=Batch 1–6(5,933), Validation=7–8(3,907), 탐색적 평가=9–10(4,070)을 유지했다. '
            'B_SVM_balanced, B_LR_tune_C0p1, B_RF_balanced의 저장 파이프라인을 그대로 사용했다.</p>'
            '<p><strong>새 분류기 학습, 튜닝, 전처리 Fit, PCA·UMAP, 임계값 변경은 수행하지 않았다.</strong> '
            '기존 1–6단계 보고서·코드·모델을 확인하고, 3개 모델 각각 미래 7,977개 예측을 완전히 재현했다. '
            '입력은 f001–f128만이며 클래스 1–6 매핑과 Train 전처리 통계를 확인했다.</p>'
            '<p>이 보고서의 표·그래프는 <b>관찰</b>이다. 가능한 설명은 <b>해석</b>, 원인 분리에 '
            '필요하지만 없는 정보는 <b>미확인</b>으로 구분한다.</p>' + table(train_table))
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for name in NAMES:
        part = scores[scores.model == name].sort_values('batch')
        axes[0].plot(part.batch, part.macro_f1, marker='o', label=name)
        axes[1].plot(part.batch, part.min_class_recall, marker='o', label=name)
    for ax, title, ylabel in zip(axes, ['Batch Macro F1', 'Worst class recall'],
                                ['Macro F1', 'Minimum class recall']):
        ax.axvline(8.5, color='gray', linestyle='--')
        ax.set(title=title, xlabel='Batch number', ylabel=ylabel, xticks=[7, 8, 9, 10], ylim=(0, 1.05))
        ax.legend()
    performance_image = figure('batch_performance', fig)
    fig, axes = plt.subplots(4, 3, figsize=(18, 22))
    for row, batch in enumerate([7, 8, 9, 10]):
        for col, name in enumerate(NAMES):
            data = confusion[(confusion.batch == batch) & (confusion.model == name)]
            cm = data.pivot(index='actual_id', columns='predicted_id', values='count').to_numpy()
            ax = axes[row, col]
            image = ax.imshow(cm, cmap='Blues')
            for i in range(6):
                for j in range(6):
                    ax.text(j, i, str(cm[i, j]), ha='center', va='center', fontsize=8)
            ax.set(title=f'{name}: Batch {batch}', xlabel='Predicted gas', ylabel='Actual gas',
                   xticks=range(6), yticks=range(6),
                   xticklabels=list(GASES.values()), yticklabels=list(GASES.values()))
            ax.tick_params(axis='x', rotation=65)
            fig.colorbar(image, ax=ax, shrink=.6, label='Sample count')
    confusion_image = figure('batch_confusion_matrices', fig)
    section('2. Batch별 클래스 분류 성능', performance_image + table(
        scores[['model', 'batch', 'n', 'accuracy', 'macro_f1', 'weighted_f1', 'min_class_recall']]) +
        confusion_image + '<details><summary>6종 전체 Precision·Recall·F1 및 예측 수</summary>' +
        table(classes) + '</details><p><b>관찰:</b> 모든 Batch에 6종이 존재하므로 이 구간의 '
        'Macro F1은 6종 동일 가중 평균이다. 최소 Recall도 함께 확인해야 한다. '
        '전체 Validation과 평가의 크기·가스 비율이 달라 합산 Accuracy만으로 비교하지 않는다.</p>')
    target_agreement = agreement[((agreement.batch == 9) & (agreement.gas_id == 6)) |
                                 ((agreement.batch == 10) & (agreement.gas_id == 4))]
    focus_rows = confusion[(confusion.actual_id.isin([4, 6]))]
    distributions = focus_rows.pivot(index=['batch', 'actual_gas', 'model'],
                                     columns='predicted_gas', values='count').reset_index()
    section('3. Toluene·Acetaldehyde 오분류 상세',
            '<h3>Batch 9 — Toluene 101개</h3>' + table(counts(9, 6)) +
            '<p><b>관찰:</b> SVM은 101개 전부 Ethanol로 예측했다. '
            'LR은 Ethanol 44·Ethylene 57, RF는 Ethanol 17·Ethylene 1·Ammonia 83으로 예측했다. '
            '세 모델 모두 Recall=0이지만 같은 예측을 한 것은 아니다.</p>'
            '<h3>Batch 10 — Acetaldehyde 600개</h3>' + table(counts(10, 4)) +
            '<p><b>관찰:</b> SVM 정분류 84·오분류 516(Recall 14%). '
            'LR 정분류 0·오분류 600, RF 정분류 51·오분류 549. '
            'LR→Ethanol 470개, SVM→Ethanol 261개·Toluene 150개로 오분류가 집중됐다. '
            'RF가 맞힌 51개와 SVM이 맞힌 84개는 겹치지 않는다. '
            '세 모델 모두 틀린 465개가 있어 단순한 모델 조합만으로 해결을 보장하지 않는다.</p>' +
            table(target_agreement) + '<h3>Batch 7–10의 두 가스 예측 분포</h3>' + table(distributions) +
            '<p><b>해석:</b> 같은 표본의 다른 오분류 방향은 모델별 결정 방식의 차이와 부합한다. '
            '<b>미확인:</b> 오분류된 가스의 화학적 유사성이나 센서 노화의 단독 효과는 판정할 수 없다.</p>')
    shift_mean = shifts[shifts.gas_id > 0].groupby(['batch', 'gas_id']).agg(
        normalized_wasserstein=('wasserstein_same_gas_train_sd', 'mean')).reset_index()
    shift_mean['gas'] = shift_mean.gas_id.map(GASES)
    heat = shift_mean.pivot(index='gas', columns='batch', values='normalized_wasserstein')
    fig, ax = plt.subplots(figsize=(8, 5))
    image = ax.imshow(heat.to_numpy(), cmap='YlOrRd', aspect='auto')
    for i in range(len(heat)):
        for j in range(4):
            ax.text(j, i, f'{heat.iloc[i, j]:.2f}', ha='center', va='center')
    ax.set(title='Same-gas shift across 128 features', xlabel='Batch number', ylabel='Actual gas',
           xticks=range(4), xticklabels=heat.columns, yticks=range(6), yticklabels=heat.index)
    fig.colorbar(image, ax=ax, label='Mean Wasserstein / same-gas Train SD')
    feature_images = figure('conditional_feature_shift', fig)
    svm_scale = json_scaler(frame)
    for gas, batch in [(6, 9), (4, 10)]:
        selected = chosen[(chosen.gas_id == gas) & (chosen.batch == batch)]
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
        for ax, feature in zip(axes, selected.feature):
            j = FEATURES.index(feature)
            subsets = [train[train.gas == gas]] + [
                frame[(frame.gas == gas) & (frame.batch == b)] for b in [7, 8, 9, 10]]
            values = [(sub[feature].to_numpy() - svm_scale[0][j]) / svm_scale[1][j]
                      for sub in subsets]
            ax.boxplot(values, tick_labels=['Train', '7', '8', '9', '10'], showfliers=True,
                       flierprops=dict(markersize=2))
            ax.set(title=f'{GASES[gas]}: {feature}', xlabel='Train / batch number',
                   ylabel='Value standardized by frozen Train scaler')
        feature_images += figure(f'focus_{GASES[gas]}_distribution', fig)
    extremes = pd.read_csv(OUT / 'extreme_response_summary.csv')
    focus_extremes = extremes[(extremes.gas_id.isin([4, 6])) &
                             (extremes.partition.isin(['train', 'batch7', 'batch8', 'batch9', 'batch10']))]
    focus_proximity = proximity[proximity.gas_id.isin([4, 6])]
    dependence_top = pd.concat([
        dependence.sort_values('lr_mean_abs_coefficient', ascending=False).head(8).assign(rank_type='LR'),
        dependence.sort_values('rf_impurity_importance', ascending=False).head(8).assign(rank_type='RF'),
    ])
    section('4. 센서 특징 분포 변화',
            '<p><b>계산 방법:</b> 전체 128개 특징의 Batch 1–10 및 Train/Validation/평가별 '
            '평균·표준편차(ddof=0)·중앙값·범위를 저장했다. 같은 가스의 Train을 기준으로 '
            '1차원 Wasserstein 거리를 계산하고 같은 가스 Train SD로 나눴다. '
            '전체 Train SD로 나눈 결과도 CSV에 함께 기록했다. 동일 가스 비교는 가스 혼합 비율의 '
            '영향을 줄이지만 농도 구성 차이를 제거하지 못한다.</p>'
            '<p><b>그림 특징 선정:</b> Toluene Batch 9, Acetaldehyde Batch 10 각각 '
            '정규화 Wasserstein 상위 3개(동점은 특징명 순)를 사용했다. 이는 실패를 확인한 이후의 '
            '진단용 선택이며 분류 모델 입력 선택이나 튜닝에 사용하지 않았다. 128개 전체 결과도 보존했다.</p>' +
            table(chosen[['selection_target', 'rank', 'feature', 'train_n', 'n',
                          'wasserstein_same_gas_train_sd', 'wasserstein_train_global_sd',
                          'outside_same_gas_train_range']]) + feature_images +
            '<p>상자 중앙선은 중앙값, 상자는 IQR, 수염은 1.5×IQR, 점은 수염 밖 값이다. '
            '모든 표본을 계산에 유지했다. 그림 표준화는 저장된 SVM Train 스케일러를 그대로 사용했다. '
            'PCA·UMAP은 사용하지 않았다.</p>' + table(focus_extremes) +
            '<p>|z|>3·5는 탐색적 꼬리값 기준이며 센서 오류나 제거 대상의 판정 기준이 아니다. '
            '128개 중 하나라도 기준을 넘는 비율은 특징 간 상관관계와 다중 특징 수의 영향을 받는다.</p>' +
            '<h3>동일 가스의 Train 근접성</h3>' + table(focus_proximity) +
            '<p>저장 SVM 전처리의 128차원 유클리드 거리로 가장 가까운 같은 가스·다른 가스 Train 표본을 '
            '비교했다. RBF 유사도는 exp(-저장 gamma×거리²)의 지지벡터 최대값이다. '
            '이는 확률·분류 신뢰도·새 1NN 모델 성능이 아니다. 거리에는 상관 특징의 중복과 차원의 영향이 있다.</p>' +
            '<h3>기존 모델의 특징 의존 지표</h3>' + table(dependence_top) +
            '<p>LR 계수는 표준화된 단위당 조건부 선형 방향, RF는 불순도 감소 중요도다. '
            '두 수치를 직접 비교할 수 없으며 상관 특징은 계수·중요도를 분산하거나 불안정하게 할 수 있다. '
            'SVM의 단일 전역 특징 중요도는 이 분석에서 산출하지 않았다. '
            '이 지표와 분포 이동만으로 특정 특징이 실패를 일으켰다고 확정하지 않는다.</p>')
    pairwise = pd.read_csv(OUT / 'pairwise_agreement.csv')
    pair_focus = pairwise[pairwise.gas_id.isin([4, 6])]
    correct_patterns = []
    for batch, group in wide.groupby('batch'):
        for gas in [4, 6]:
            sub = group[group.gas == gas]
            code = sub[NAMES].eq(sub.gas, axis=0).astype(int)
            code['pattern'] = code.apply(lambda row: ''.join(row.astype(str)), axis=1)
            for pattern, n in code.pattern.value_counts().items():
                correct_patterns.append(dict(batch=int(batch), gas=GASES[gas],
                                             LR_RF_SVM_correct_pattern=pattern, n=int(n)))
    pd.DataFrame(correct_patterns).to_csv(OUT / 'correctness_patterns.csv', index=False, encoding='utf-8')
    section('5. 모델 간 예측 결과 비교',
            table(agreement[agreement.gas_id.isin([4, 6])]) +
            '<details><summary>전체 가스 및 전체 Batch의 단독 정분류·공통 실패</summary>' +
            table(agreement) + '</details>' + table(pair_focus) +
            '<p>only_correct는 나머지 두 모델이 모두 틀린 표본이다. '
            'disagree_rate는 세 모델 예측이 모두 같지는 않은 비율이다. '
            '모델 간 불일치는 정답 보장을 의미하지 않는다. Batch 9 Toluene은 '
            '86.14%에서 예측이 서로 달라도 세 모델 모두 오답이었다.</p>' +
            table(pd.read_csv(OUT / 'prediction_bias.csv').query('gas in ["Toluene", "Acetaldehyde", "Ethanol"]')))
    tol_train = train_table[train_table.gas == 'Toluene'].iloc[0]
    facts = [
        dict(hypothesis='1. 가스별 학습 불균형',
             observed=f'Train Toluene {int(train_counts[6])}, Acetaldehyde {int(train_counts[4])}; '
             f'Toluene의 {100 * tol_train.batch6_fraction_within_gas:.2f}%가 Batch 6. 세 모델 모두 balanced 사용.',
             interpretation='시기별 대표성 부족이 남을 수 있음. 클래스 가중치만으로 시기·농도 범위는 복구되지 않음.',
             unknown='동일 분할의 새 대조 학습 없이 불균형의 독립 효과 추정 불가.'),
        dict(hypothesis='2. Train–미래 특징 이동',
             observed='동일 가스의 128개 특징 Wasserstein·표준화 꼬리값·Train 근접성 계산표 참조.',
             interpretation='관측 특징 공간의 이동이 오류와 함께 존재하는지 검토 가능.',
             unknown='분포 이동의 원인과 성능 저하의 인과 기여도는 미확인.'),
        dict(hypothesis='3. 특정 특징 의존',
             observed='고정 LR 표준화 계수 및 RF 중요도·상관관계 CSV 기록. SVM 전역 중요도 미산출.',
             interpretation='이동이 큰 특징과 모델 사용 특징의 겹침은 후속 Train 내부 검증 후보.',
             unknown='특징 제거·대조 재학습 없이 해당 특징이 실패 원인인지 확정 불가.'),
        dict(hypothesis='4. 다른 가스 특징 공간 중첩',
             observed='같은 가스보다 다른 가스 Train 표본이 가까운 비율과 실제 오분류 방향 기록.',
             interpretation='표준화 거리에서 경계 혼동과 양립하는 근거. 화학적 유사성의 증거는 아님.',
             unknown='128차원 거리와 일부 그림만으로 실제 클래스 분포 중첩의 전체 구조 확정 불가.'),
        dict(hypothesis='5. 새로운 시기·조건 일반화 부족',
             observed='Batch 9 Toluene은 3개 모두 실패. Batch 10 Acetaldehyde Recall은 LR 0%, RF 8.5%, SVM 14%.',
             interpretation='일부 가스·Batch의 공통 어려움과 모델별 한계가 함께 존재함.',
             unknown='농도·환경·측정 세션 및 새 시기 자료 없이 드리프트·환경 효과를 분리할 수 없음.'),
    ]
    fact_table = pd.DataFrame(facts)
    fact_table.to_csv(OUT / 'hypothesis_evidence.csv', index=False, encoding='utf-8')
    section('6. 실패 원인 가설별 검토', table(fact_table) +
            '<p>모든 Train 클래스와 저장 모델의 예측 가능한 클래스 1–6을 확인했다. '
            '기존 예측·매핑이 정확히 재현됐으므로 이번 실패를 단순한 클래스 누락이나 변환 오류로 '
            '설명할 근거는 발견되지 않았다. Batch 번호는 시기 구분이며 실제 경과 시간으로 변환하지 않았다.</p>')
    proposal = proposal_table()
    proposal.to_csv(OUT / 'improvement_priorities.csv', index=False, encoding='utf-8')
    section('7. 개선 실험 우선순위와 선정 근거', table(proposal) +
            '<p>우선순위 1은 학습 시기·가스 대표성 확보와 시간순 반복 검증이다. '
            '그다음 특징 안정성 및 제한된 LR/SVM 결합을 검토한다. '
            'Batch 전체의 평균·분산이나 정답으로 Batch를 보정하면 실제 배포 시점에 없는 정보를 '
            '사용할 수 있어 별도 운영 가정이 필요하다. 이번에는 어느 개선 방법도 구현하지 않았다.</p>')
    section('8. 데이터·평가 한계 및 보존 검증',
            '<p>이번 분석은 이미 여러 번 확인한 과거 Test의 탐색적 진단이다. '
            '이 결과를 이용한 다음 선택은 다시 같은 Batch를 독립 Test라고 주장할 수 없다. '
            'Validation Batch 8 Toluene은 18개로 작고, Batch 9 Toluene 101개와 '
            'Batch 10 Acetaldehyde 600개도 측정 세션 독립성을 보장하지 않는다. '
            '유의확률이나 인과 효과를 추정하지 않았다.</p>'
            '<p>센서 드리프트·농도·환경 변화 중 원인을 특정할 수 없다. '
            '분포 거리·오분류·모델 계수는 관찰의 연결이지 인과관계의 증명은 아니다. '
            '새 시기·농도·환경·반복 측정 정보를 확보한 독립 평가가 필요하다.</p>'
            '<p>분할 간 정확 특징 중복과 모델 입력·클래스·전처리 통계·저장 예측을 확인했다. '
            '원본 및 기존 파일 해시 보존 결과는 run_manifest.json에 기록한다. '
            '전체 테스트는 tests.txt·test_results.xml에 기록하며 기존 실패 2건을 신규 실패와 구분한다. '
            '기존 해시·테스트를 수정하지 않으며 Commit·Push는 하지 않는다.</p>')
    document = '<!doctype html><html lang="ko"><meta charset="utf-8">'
    document += '<title>시간순 센서 데이터 실패 진단</title><style>'
    document += 'body{font:16px/1.6 sans-serif;max-width:1500px;margin:25px auto;padding:20px}'
    document += 'section{overflow-x:auto;margin:35px 0}table{border-collapse:collapse;font-size:12px}'
    document += 'th,td{border:1px solid #bbb;padding:6px}img{max-width:100%}h1,h2{color:#173a58}</style>'
    document += '<h1>7단계: 시간순 센서 데이터의 Batch별 분류 실패 원인 분석</h1>'
    document += ''.join(sections) + '</html>'
    (ROOT / 'reports/temporal_failure_diagnostic_report.html').write_text(document, encoding='utf-8')
    text = '# 8단계 개선 실험 제안 — 7단계 관찰에 근거한 설계\n\n'
    text += '이번 단계는 저장 모델 진단만 수행했으며 새 학습·튜닝·전처리 변경 없음.\n\n'
    text += 'Batch 9 Toluene 101개를 세 모델 모두 틀림. SVM은 전부 Ethanol. '
    text += 'Batch 10 Acetaldehyde 정분류 LR 0/RF 51/SVM 84개, 모두 오답 465개.\n\n'
    text += '## 관찰·해석·미확인\n\n'
    for row in facts:
        text += f'### {row["hypothesis"]}\n\n- 관찰: {row["observed"]}\n'
        text += f'- 해석: {row["interpretation"]}\n- 미확인: {row["unknown"]}\n\n'
    text += '## 개선 우선순위\n\n'
    for row in proposal.to_dict('records'):
        text += f'### {row["priority"]}. {row["method"]}\n\n'
        for key in ['purpose', 'expected', 'leakage_risk', 'validation_scope']:
            text += f'- {key}: {row[key]}\n'
        text += '\n'
    text += '## 사전 설계와 평가 제한\n\n'
    text += '현재 모델과 6단계 선정은 유지. 다음 단계 실행 시 먼저 후보 수·동점 규칙·클래스 보호 기준을 고정할 것.\n'
    text += '과거 구간 예시: Train 1–3→Validation 6, Train 1–6→Validation 7, '
    text += 'Train 1–7→Validation 8. 첫 창 Train의 Toluene 79개, Validation 6의 Acetaldehyde 29개, '
    text += 'Validation 8의 Toluene 18개로 시기·표본 제한을 함께 보고할 것. '
    text += '각 창의 전처리·특징 선택·가중치·앙상블 설정은 그 창의 Train 안에서만 결정하거나 '
    text += '내부 시간순 검증을 사용할 것. Batch 9–10은 현재 진단에 이미 노출됐으므로 '
    text += '나중에 고정 평가하더라도 탐색적 평가로만 표현할 것.\n\n'
    text += 'Batch 9/10의 정답이나 전체 배치 통계로 보정·특징 선택·결합 가중치를 맞추지 말 것. '
    text += '새 시기 자료를 확보하면 후보를 고정한 뒤 독립적으로 평가할 것. '
    text += '드리프트 보정은 기준 가스·농도·환경 또는 운영 시 확보 가능한 참조 자료의 조건을 명확히 할 것.\n\n'
    text += '특징 그림은 동일 가스 Train 대비 Wasserstein/동일 가스 Train SD 상위 3개씩을 '
    text += '진단 목적으로 선정했음. 이 목록을 바로 모델 입력 선택으로 사용하면 평가 기반 선택 편향이 생김.\n'
    (ROOT / 'reports/temporal_failure_improvement_proposal.md').write_text(text, encoding='utf-8')


# 저장된 SVM 표준화 값만 읽기
def json_scaler(frame):
    import json
    import joblib
    decision = json.loads((ROOT / 'outputs/temporal_expansion/selection_frozen.json').read_text(encoding='utf-8'))
    path = ROOT / decision['selected_models']['B_SVM_balanced']['path']
    scaler = joblib.load(path).named_steps['scaler']
    return scaler.mean_, scaler.scale_


# 관찰된 문제와 연결한 개선 제안 표 작성
def proposal_table():
    return pd.DataFrame([
        dict(priority=1, method='학습 데이터의 시기·가스 대표성 및 시간순 반복 검증',
             purpose='Toluene Train의 Batch 6 집중, 미래의 공통 실패와 작은 Validation 가스 표본',
             expected='어떤 시기에 효과가 유지되는지 확인하고 농도·조건 범위의 공백 파악',
             leakage_risk='평가 Batch를 창 선택·튜닝에 재사용하면 낙관 편향',
             validation_scope='기존 과거 창으로 탐색 가능. 대표성 확보 효과의 독립 확인은 새 자료 필요'),
        dict(priority=2, method='Train 내부의 특징 안정성 평가·선택',
             purpose='조건부 특징 이동과 상관 특징 중복, LR/RF 의존 지표',
             expected='불안정 특징의 영향 감소 여부 검증; 유용한 정보 손실도 점검',
             leakage_risk='이번 평가 기반 상위 이동 특징 목록을 바로 제거하면 평가 정보 유입',
             validation_scope='각 과거 Train 내부에서 선택 Fit, 외부 미래 창에서 6종 성능·최저 Recall 확인'),
        dict(priority=3, method='제한된 LR/SVM/RF 결합 가능성 검토',
             purpose='Batch 10 Acetaldehyde에서 RF·SVM의 정분류 표본은 다르나 공통 실패 465개',
             expected='상보적 오류 일부 감소 가능. 단순 다수결은 공통 실패와 소수 정답을 놓칠 수 있음',
             leakage_risk='Batch 9/10 정답으로 가중치·게이트 선택 금지',
             validation_scope='Train 내부 시간순 예측으로 결합 설정 결정 후 미래 창 평가; 독립 성능 미확인'),
        dict(priority=4, method='드리프트 보정 및 Batch 특성 정규화의 운영 가능성 검토',
             purpose='같은 가스에서도 관측 특징 이동이 있고 센서·농도·환경 원인 분리가 어려움',
             expected='참조 측정이 확보되면 시기별 편차 감소 가능; 가스 신호 제거 위험도 있음',
             leakage_risk='평가 정답·미래 전체 Batch 평균으로 정규화하면 누수 또는 전이적 설정이 됨',
             validation_scope='과거 Train 기반 보정 또는 운영 시 확보 가능한 무정답 참조 조건부터 사전 정의'),
        dict(priority=5, method='다른 모델의 소규모 대조 실험',
             purpose='모델별 오분류 방향이 다르지만 세 모델 공통 실패도 존재',
             expected='결정 경계 가정의 영향을 비교; 데이터 범위 부족을 모델 교체만으로 해결 못할 수 있음',
             leakage_risk='같은 미래 Batch를 반복 보고 모델 종류를 늘리는 선택 편향',
             validation_scope='대표성·반복 검증을 먼저 정한 후 제한된 후보 수로 탐색; 이번 단계 미실행'),
    ])
