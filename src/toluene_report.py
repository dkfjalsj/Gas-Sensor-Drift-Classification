# Toluene 실패 원인과 개선 설계 보고서 생성
# 실제 계산값과 해석을 분리해 표·그림으로 정리

import base64
import html

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .data import ROOT, GASES, FEATURES, feature_label
from .analyze_toluene import OUT, COMMON, SELECTED

MODELS = ['LogisticRegression', 'RandomForest', 'SVM_RBF']


# 긴 표에 가로 스크롤 적용
def table(frame):
    return '<div class="table">' + frame.to_html(index=False, border=0, na_rep='NA', float_format=lambda v: f'{v:.4f}') + '</div>'


# 계산 결과로만 진단 보고서 생성
def make_report(t):
    folder = OUT / 'figures'
    folder.mkdir(exist_ok=True)
    figures = {}
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.grid': True, 'grid.alpha': .2})

    # 그림 파일과 HTML 내장 이미지 저장
    def save(fig, name, caption):
        fig.tight_layout()
        path = folder / f'{name}.png'
        fig.savefig(path, dpi=130, bbox_inches='tight')
        plt.close(fig)
        figures[name] = '<figure><img alt="' + html.escape(caption) + '" src="data:image/png;base64,' + base64.b64encode(path.read_bytes()).decode() + '"><figcaption>' + html.escape(caption) + '</figcaption></figure>'

    counts = t['batch_class_counts'].set_index('batch')
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    counts.plot.bar(stacked=True, ax=axes[0], colormap='tab10')
    axes[0].set(title='All class counts by batch', xlabel='Batch (ordered category)', ylabel='Number of samples')
    bars = axes[1].bar(counts.index, counts.Toluene, color='#7857a3')
    axes[1].bar_label(bars)
    axes[1].set(title='Toluene support by batch', xlabel='Batch (ordered category)', ylabel='Toluene samples', xticks=counts.index)
    axes[0].legend(fontsize=8)
    save(fig, 'class_counts', '관찰: Batch 3–5의 Toluene은 0개. Batch 2는 5개. Batch 번호는 시기 순서이며 실제 경과 시간을 뜻하지 않는다.')

    s = t['toluene_metrics']
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    for ax, exp in zip(axes, ['A_random', 'B_early', 'B_history']):
        selected = s[(s.experiment == exp) & (s.scope == 'pooled')]
        for i, part in enumerate(['train', 'validation', 'test']):
            values = selected[selected.partition == part].set_index('model').reindex(MODELS).toluene_recall
            bars = ax.bar(np.arange(3) + (i - 1) * .25, values, width=.25, label=part)
            for bar, value in zip(bars, values):
                if np.isfinite(value):
                    ax.text(bar.get_x() + bar.get_width()/2, value + .015, f'{value:.3f}', ha='center', fontsize=7)
                else:
                    ax.text(bar.get_x() + bar.get_width()/2, .04, 'NA', ha='center', fontsize=8)
        ax.set(title=exp + ': Toluene recall', xlabel='Classifier', ylabel='Toluene recall', xticks=np.arange(3), xticklabels=['LR', 'RF', 'SVM'], ylim=(0, 1.12))
        ax.legend(fontsize=8)
    save(fig, 'partition_recall', 'Train은 학습 자료 재대입 진단이며 독립 평가가 아니다. B_history Validation은 Toluene 0개이므로 Recall이 0%가 아니라 NA다.')

    fig, axes = plt.subplots(2, 1, figsize=(12, 9))
    for ax, exp in zip(axes, ['B_early', 'B_history']):
        for model in MODELS:
            sub = s[(s.experiment == exp) & (s.model == model) & (s.partition == 'test') & (s.scope == 'batch')]
            ax.plot(sub.batch, sub.toluene_recall, marker='o', label=model)
        ax.set(title=exp + ': Toluene recall by future batch', xlabel='Test batch (ordered category)', ylabel='Toluene recall', ylim=(-.015, 1.02), xticks=range(3 if exp == 'B_early' else 5, 11))
        ax.legend(fontsize=8)
    save(fig, 'batch_recall', 'Toluene이 없는 Batch는 선을 끊어 표시했다. 0%는 실제 표본이 있지만 맞힌 예측이 0개인 경우다. 표본 수는 함께 제공한 표에서 확인한다.')

    errors = t['toluene_confusion']
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    for ax, exp in zip(axes, ['B_early', 'B_history']):
        sub = errors[(errors.experiment == exp) & (errors.partition == 'test') & (errors.scope == 'pooled')]
        fractions = sub.pivot(index='model', columns='predicted_gas', values='fraction').reindex(index=MODELS, columns=GASES.values())
        numbers = sub.pivot(index='model', columns='predicted_gas', values='count').reindex(index=MODELS, columns=GASES.values())
        im = ax.imshow(fractions, vmin=0, vmax=1, cmap='Blues', aspect='auto')
        for i in range(3):
            for j in range(6):
                v = fractions.iloc[i, j]
                ax.text(j, i, f'{numbers.iloc[i,j]}\n{v:.1%}', ha='center', va='center', fontsize=8, color='white' if v > .5 else 'black')
        ax.set(title=exp + ': true Toluene -> predicted gas', xlabel='Predicted gas class', ylabel='Classifier', xticks=range(6), xticklabels=GASES.values(), yticks=range(3), yticklabels=MODELS)
        ax.tick_params(axis='x', rotation=30)
        ax.grid(False)
        fig.colorbar(im, ax=ax, label='Fraction of true Toluene samples')
    save(fig, 'toluene_confusion', '각 Test의 실제 Toluene 1,754개에 대한 예측. 첫 줄은 개수, 둘째 줄은 Toluene 내부 비율. 오류율은 가스의 화학적 유사성을 뜻하지 않는다.')

    profiles = t['gas_profiles']
    fig, axes = plt.subplots(2, 2, figsize=(15, 11))
    for col, exp in enumerate(['B_early', 'B_history']):
        for row, field in enumerate(['mean_scaled_wasserstein', 'mean_marginal_overlap']):
            sub = profiles[(profiles.experiment == exp) & profiles.batch.isin(COMMON)]
            values = sub.pivot(index='reference_gas', columns='batch', values=field).reindex(GASES.values())
            ax = axes[row, col]
            im = ax.imshow(values, cmap='viridis', aspect='auto', vmin=0, vmax=1 if row else None)
            for i in range(6):
                for j in range(5):
                    ax.text(j, i, f'{values.iloc[i,j]:.2f}', ha='center', va='center', fontsize=8, color='white')
            ax.set(title=exp + (': normalized distance (lower = closer)' if row == 0 else ': marginal overlap (higher = more overlap)'), xlabel='Future Toluene batch', ylabel='Reference Train gas', xticks=range(5), xticklabels=COMMON, yticks=range(6), yticklabels=GASES.values())
            fig.colorbar(im, ax=ax, label='Mean of 128 normalized distances' if row == 0 else 'Mean histogram overlap (0–1)')
    save(fig, 'distribution_profiles', '각 미래 Toluene을 Train의 각 가스와 비교한 주변 분포 지표. 거리의 분모는 해당 Train 전체 특징 SD. 겹침은 Train에서 정한 최대 20개 구간의 비율 최솟값 합이다. 두 B 조건은 기준·척도가 달라 절대 거리를 직접 비교하지 않는다.')

    stats = t['feature_stats']
    source_pred = t['predictions']
    raw_ids = source_pred[(source_pred.experiment == 'B_history') & (source_pred.model == 'LogisticRegression') & (source_pred.partition == 'train')]
    from .data import load_dataset, read_config
    frame, _ = load_dataset(read_config())
    training = frame[frame.row_id.isin(raw_ids.row_id)]
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    for ax, index in zip(axes.flat, [1, 2, 65, 121]):
        feature = f'f{index:03d}'
        groups = [training[training.gas == gas][feature] for gas in [6, 1, 4]]
        groups += [frame[(frame.gas == 6) & (frame.batch == b)][feature] for b in COMMON]
        ax.boxplot(groups, tick_labels=['Train Tol', 'Train Ethanol', 'Train Acetald.', *[f'Tol B{b}' for b in COMMON]], showfliers=False)
        ax.set_yscale('symlog', linthresh=1)
        ax.tick_params(axis='x', rotation=35)
        ax.set(title=feature_label(index), xlabel='Reference gas / future Toluene batch', ylabel='Feature value (symlog)')
    save(fig, 'feature_boxes', 'B_history Train과 미래 Toluene의 사전 지정 대표 특징 비교. 상자=IQR, 중앙선=중앙값, 수염=1.5×IQR. 극단점은 그림에서만 생략하고 분석에서는 제거하지 않았다.')

    centers = t['centroid_distances'].drop_duplicates(['experiment', 'row_id'])
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for ax, exp in zip(axes, ['B_early', 'B_history']):
        sub = centers[(centers.experiment == exp) & centers.batch.isin(COMMON)]
        nearest = pd.crosstab(sub.batch, sub.nearest_centroid_gas).reindex(index=COMMON, columns=GASES.values(), fill_value=0)
        nearest.div(nearest.sum(axis=1), axis=0).plot.bar(stacked=True, ax=ax, colormap='tab10')
        ax.set(title=exp + ': nearest Train class centroid', xlabel='Future Toluene batch', ylabel='Fraction of true Toluene samples')
        ax.legend(fontsize=7)
    save(fig, 'centroid_diagnostic', '기존 Train 전처리 좌표에서 각 Train 가스 중심까지 RMS 거리 비교. 새로운 분류기를 학습하거나 모델의 예측을 대체한 결과가 아니다. 공분산·다봉형 분포를 반영하지 못하는 설명용 거리다.')

    pcs = pd.read_csv(ROOT / 'outputs/model_diagnostics/pca_coordinates.csv')
    pcs = pcs[pcs.experiment == 'B_history']
    fig, ax = plt.subplots(figsize=(10, 7))
    for gas, label, color in [(6, 'Train Toluene', '#7857a3'), (1, 'Train Ethanol', '#2796b0'), (4, 'Train Acetaldehyde', '#e89d3c')]:
        sub = pcs[(pcs.gas == gas) & (pcs.partition == 'train')]
        ax.scatter(sub.pc1, sub.pc2, s=14, alpha=.6, label=label, color=color)
    sub = pcs[(pcs.gas == 6) & pcs.batch.isin(COMMON)]
    ax.scatter(sub.pc1, sub.pc2, s=8, alpha=.25, label='Future Toluene B6–10', color='#c14747')
    ax.set(title='Existing Train-basis PCA: Toluene and common error classes', xlabel='PC1 (existing diagnostic Train basis)', ylabel='PC2 (existing diagnostic Train basis)')
    ax.legend()
    save(fig, 'existing_pca', '3단계에서 저장한 Train 기준 PCA 좌표를 그대로 재사용했다. 이번에는 PCA도 Fit하지 않았다. 2차원 겹침과 분리는 전체 128차원의 분류 난이도를 확정하지 못한다.')

    sections = []
    def section(title, body):
        sections.append('<section><h2>' + title + '</h2>' + body + '</section>')

    pooled = s[s.scope == 'pooled']
    tol_batch = s[(s.scope == 'batch') & (s.partition == 'test')]
    wrong = errors[(errors.scope == 'pooled') & (errors.partition == 'test') & (errors.predicted_gas_id != 6)]
    top = wrong.sort_values('count', ascending=False).groupby(['experiment', 'model'], sort=False).head(2)
    consensus = t['consensus'].groupby('experiment').agg(n=('row_id', 'size'), all_wrong=('all_three_wrong', 'sum')).reset_index()
    votes = t['consensus'].groupby(['experiment', 'unanimous_prediction']).size().rename('samples').reset_index()
    summary = profiles[(profiles.reference_gas == 'Toluene') & profiles.batch.isin(COMMON)]
    closest = profiles[profiles.batch.isin(COMMON)].sort_values('mean_scaled_wasserstein').groupby(['experiment', 'batch'], sort=False).head(1)
    history = t['historical_hash_audit']
    mismatches = history[~history.exact_match]
    semantic = t['source_ast_audit']

    section('1. 연구 배경 및 분석 목적', '''<p>이번 단계는 Toluene 실패의 조건과 근거를 분리하고 타당한 개선 실험을 설계하는 작업이다.
기존 EDA·모델 비교·진단 보고서, 학습 코드, 저장 파이프라인 9개와 예측을 확인했다.
<b>관찰</b>은 실제 파일·모델·예측에서 계산한 사실, <b>해석</b>은 가능한 설명이며 확인되지 않은 원인은 별도로 표시한다.</p>
<p>이번 분석에서는 모델·PCA·스케일러를 새로 Fit하지 않았다. 예측 임계값·전처리·특징 선택·파라미터를 바꾸지 않았으며
기존 원본, 모델, 보고서와 학습 결과는 보존했다.</p>''')
    section('2. Toluene 분류 실패 현황', figures['partition_recall'] + table(pooled[['experiment', 'model', 'partition', 'total_n', 'toluene_n', 'correct_toluene', 'toluene_recall', 'toluene_f1', 'predicted_toluene_n', 'predicted_toluene_ratio']]) + '''
<p><b>범위 정정:</b> “세 모델 모두 Recall 0%”는 B_history의 미래 Test(Toluene 1,754개)에 해당한다.
B_early에서는 LR이 12개를 맞혀 Recall 12/1,754=0.6842%이며 RF와 SVM은 0%다.
A_random Test는 Toluene 367개이고 높은 Recall을 보였다. B_history Validation은 Toluene이 없으므로 Recall은 NA다.
Train의 높은 Recall은 학습 자료 재대입 결과이며 미래 일반화를 증명하지 않는다.</p>''')
    section('3. Batch별 클래스 및 학습 표본 분포', figures['class_counts'] + table(t['batch_class_counts']) + table(t['partition_counts']) + '''
<p><b>확인:</b> B_early Train은 Toluene 74/445=16.63%, B_history Train은 79/3,275=2.41%다.
학습 전체 표본은 약 7.36배가 되지만 Toluene은 5개(약 6.76%)만 늘었다. Batch 3–5에는 Toluene이 없어,
과거 Batch 수만 늘리는 것이 Toluene의 시기·농도 범위를 넓힌다는 보장은 없다.</p>
<p>B_history의 Toluene 훈련 표본은 Batch 1의 74개와 Batch 2의 5개뿐이다.
따라서 <b>학습 클래스 누락은 아니며, 소수·초기 시기에 치우친 학습 범위</b>가 문제 후보이다.
B_history Validation Batch 4의 Toluene 누락은 사전 검증에서 이 클래스의 일반화를 평가하지 못한 설계 한계다.
79개가 절대적으로 부족하다는 임계값은 없으며, 부족함의 독립 효과를 측정한 실험도 하지 않았다.</p>''')
    section('4. 모델별 Toluene 오분류 분석', figures['batch_recall'] + figures['toluene_confusion'] +
            '<h3>실제 Toluene의 주요 오분류 조합</h3>' + table(top[['experiment', 'model', 'predicted_gas', 'count', 'toluene_support', 'fraction']]) +
            '<h3>같은 표본에서 세 모델이 모두 틀린 수와 일치한 예측</h3>' + table(consensus) + table(votes) +
            '<h3>모델 클래스 및 예측 재현 검사</h3>' + table(t['model_audit']) +
            '<details><summary>Batch별 Toluene 표본·Recall·예측 비율·실제 예측 클래스</summary>' + table(tol_batch[['experiment', 'model', 'batch', 'total_n', 'toluene_n', 'correct_toluene', 'toluene_recall', 'predicted_toluene_n', 'predicted_toluene_ratio', 'observed_predicted_classes']]) + '</details>' + '''
<p>classes_=[1,2,3,4,5,6]와 입력 f001–f128을 확인했다. 원본 label, 저장 정답, 분할 목록과 모델 재예측을 대조했다.
별도 LabelEncoder나 inverse_transform이 없고 정수 예측을 그대로 비교한다. 클래스 코드 6은 기존 UCI 224 매핑의 Toluene이다.
실제 실험에서 표본의 화학적 정체가 올바르게 기록됐는지까지 독립적으로 검증한 것은 아니다.</p>
<p>B_history LR은 Test 전체에서 Toluene으로 44개를 예측했지만 실제 Toluene을 맞힌 것은 0개다.
따라서 Recall 0%와 “클래스 6을 출력할 수 없음”은 다르다. RF와 SVM은 해당 Test에서 클래스 6을 출력하지 않았다.
모든 모델은 Train에서 Toluene을 맞히고 B_early Validation의 Toluene 5개도 모두 맞혔다.
이는 클래스를 학습하지 않았다는 설명보다 미래 조건에서 학습 경계가 맞지 않았다는 설명을 지지한다.</p>''')
    section('5. 특징 분포 변화 분석', figures['distribution_profiles'] + table(summary) +
            '<h3>미래 Toluene과 주변 분포 거리가 가장 작은 Train 가스</h3>' + table(closest) +
            figures['feature_boxes'] + figures['centroid_diagnostic'] + figures['existing_pca'] + '''
<p>동일 Toluene 내 비교를 우선하고, 같은 미래 Toluene을 Train의 다른 가스와도 비교했다.
모든 128개 특징의 평균·중앙값·표준편차(ddof=1), 원래 Wasserstein 거리, Train SD 정규화 거리, 겹침 지표를 CSV로 제공한다.
대표 도표는 EDA에서 지정한 특징을 사용하며 결과를 보고 특징을 선택하지 않았다.</p>
<p>Wasserstein은 값이 이동한 거리를, 겹침은 Train 자료에서 정한 구간의 표본 비율이 얼마나 겹치는지를 나타낸다.
겹침은 최대 20개 Train 분위수 구간과 양 끝 무한대 경계로 계산했다. 이는 특징별 주변 분포의 평균이며
변수 사이의 상관관계·다봉형 구조·분류 경계를 모두 설명하지 못한다. 표본 5개인 Batch 2의 분포 추정은 특히 불안정하다.</p>
<p>다른 가스와 가까운 거리나 겹침, 오분류는 <b>센서 특징 공간의 유사성</b>이지 화학적 유사성의 증명이 아니다.
미래 Toluene 표본 수가 많아도 초기 Train의 시기 다양성 부족을 보완하지 못한다. 농도와 환경 정보가 없어 드리프트의 독립 효과는 확정할 수 없다.</p>''')
    causes = pd.DataFrame([
        ['훈련 클래스 누락', '배제 근거 있음', '모든 Train에 Toluene 포함; classes_에 6 존재; Train에서 실제 정답 검출', '클래스가 없어서 학습하지 못했다는 설명과 불일치'],
        ['표본 수·시기 다양성 부족', '확인된 구성 / 영향은 추정', 'B_history 79개, 2.41%; Batch 1과 2에서만 수집', '학습량 통제 실험 없이 독립 효과·필요 표본 수 미확정'],
        ['시간순 특징 분포 변화', '거리·겹침으로 확인', '동일 Toluene의 Train 대비 미래 분포 차이 및 Recall 저하 공존', '변화 자체와 센서 노화의 원인은 구분 필요'],
        ['농도·환경 변화', '가능한 대안 설명', '원본에 농도·환경·측정별 timestamp 열 없음', '현재 자료로 효과 분리 불가'],
        ['다른 가스와 특징 유사성', '공간별 부분 근거', '오분류 조합·주변 분포 거리·겹침·중심 거리·PCA', '화학적 유사성, 전체 다변량 분포 동일성은 확정 불가'],
        ['일반화 한계', '관측 결과로 확인', 'Train/초기 Validation에서 검출하나 미래 Test에서 거의 또는 전혀 검출 못 함', 'LR/RF/SVM 각각의 구조가 미친 원인 비율은 미확정'],
        ['처리·클래스 매핑 오류', '현재 코드상 증거 없음', '정수 label 직접 사용; 모든 저장 예측 재현; 클래스·입력 확인', '원래 수집 실험의 화학 레이블 오류까지 검증한 것은 아님'],
    ], columns=['가능성', '판정', '근거', '미확인 사항'])
    section('6. 원인별 검증 결과', table(causes) + '''
<p><b>가장 유력한 해석:</b> 초기에 치우친 Toluene 학습 범위와 미래 특징 분포의 차이를 기존 경계가 일반화하지 못한 상황이다.
상대적 소수 클래스 구성과 Toluene 없는 Validation이 이 문제를 드러내거나 대응할 기회를 제한했을 수 있다.
분포 변화의 원인은 센서 드리프트뿐 아니라 농도·환경·수집 조건일 수 있다. 각 요인의 기여율이나 인과관계는 확정하지 않았다.</p>''')
    improvements = pd.DataFrame([
        ['1. 클래스·시기 범위 확보', '각 Train/Validation/Test에 6종 존재 및 support 기록', '클래스 누락 평가 방지; Toluene 시기 다양성 확보', '미래 표본을 과거 Train에 소급 추가 금지', '시간순 Fold별 클래스 support·Recall·F1 확인'],
        ['2. 과거 학습 범위 확장', '과거 Batch 6 이후 Toluene을 포함한 정당한 forward 실험', '다양한 과거 반응 패턴 확보', '각 Test보다 뒤의 Batch 사용 금지', '같은 외부 Batch에서 고정 창/확장 창 비교; 학습량 통제 보조 실험'],
        ['3. 불균형 보정', 'Train 내부 class_weight 또는 재표본화 후보 비교', 'Toluene의 학습 손실 기여 확대 가능', '전체 자료에서 가중치·재표본화 계산 금지', '같은 Fold에서 무보정 기준선 대비 macro-F1·Toluene precision/recall 비교'],
        ['4. 표준화/강건 스케일링', 'LR/SVM의 StandardScaler와 RobustScaler를 사전 후보로 정의; RF 무스케일 기준 유지', '극단값 영향 완화 가능; 분포 변화 자체 해결은 보장 안 됨', '각 내부 Train에서만 Fit; Test 범위로 clipping 기준 선택 금지', '시기 검증에서 동일 예산 비교; 표본 삭제 없이 민감도 확인'],
        ['5. 특징 선택/PCA', '상관 특징·과한 차원을 Train 내부에서 검토', '잡음·중복 정보 감소 가능; 유용 신호 손실 위험', '기존 EDA/PCA·Test 중요도로 특징 선택 금지', '내부 Train/Fold에만 Fit하는 Pipeline; 선택 없음 기준선 유지'],
        ['6. 제한된 파라미터 탐색', 'LR의 규제, RF 복잡도, SVM C/gamma 후보를 실행 전 고정', '현재 고정 설정의 편향/복잡도 개선 가능', '기존 Test를 보며 범위·예산·모델 선택 반복 금지', '모델별 동일 탐색 예산; 과거 내부 Validation만 사용'],
    ], columns=['우선순위/방법', '필요한 이유·구성', '기대효과·주의', '누수 위험', '검증 방법'])
    section('7. 개선 실험 설계안', table(improvements) + '<h3>기존 자료를 재사용하는 사전 시간순 설계안 — 모두 탐색적</h3>' + table(t['exploratory_protocol']) + '''
<p>표의 외부 Train/Validation/Test 구간을 실행 전에 고정한다. Train에는 그 이전 Batch만 포함한다.
모델·전처리 후보는 동일 Validation 규칙과 사전 예산으로 비교하고 외부 Test는 한 번만 보고한다.
세 모델은 같은 표본·분할을 사용한다. 튜닝이 필요하면 외부 Train 안에서만 추가 과거→미래 내부 분할을 만들며,
6종 검증이 가능한 내부 Fold가 없으면 해당 튜닝을 생략한다. 외부 Validation으로 설정을 선택했다면 이를 명시하고
외부 Test를 설정 선택에 사용하지 않는다. 재학습 여부도 실행 전 고정한다.</p>
<p>이미 Batch 1–10의 Test를 관찰했으므로, 위 구간을 다시 나눠도 <b>독립 최종 평가가 아니다</b>.
Val 8의 Toluene은 18개뿐이므로 정밀도와 불확실성이 제한된다. 임의로 미래 표본을 보충해 support를 늘리지 않는다.</p>
<h3>독립 최종 검증</h3><p>현재까지의 자료는 개발 자료로 선언하고 방법·전처리·탐색 예산·클래스별 허용 오류·모델 선정 기준을 사전에 고정한다.
그 뒤 새로 수집하고 한 번도 관찰하지 않은 시기의 자료를 유보한다. 새 자료의 6종·농도·환경·실험 식별자를 기록하고,
반복 측정의 독립성도 점검한다. 별도 개발용 새 구간을 썼다면 그보다 뒤의 최종 구간을 다시 유보해야 한다.
미래 자료가 실제로 확보되기 전에는 독립 평가 결과를 보고할 수 없다.</p>''')
    section('8. 모델 선정에 미치는 영향', '''<p>이전 평균 성능에서 SVM, 변동성과 비용에서 LR을 탐색 후보로 제시했지만,
B_history의 세 모델 모두 Toluene 1,754개에서 Recall 0%라는 클래스별 실패가 있다.
6종 분류가 목표라면 평균 macro-F1이나 accuracy만으로 운영 모델을 확정하기 어렵다.</p>
<p>최종 선정에는 모든 가스의 support, 최저 클래스 Recall, Toluene precision/recall/F1, Batch별 변동,
학습·예측 비용, 해석 가능성을 함께 사용해야 한다. 허용 오류와 trade-off는 업무 요구로 독립 검증 전에 정하고,
이미 본 Test에 맞춰 정하지 않는다. 이번에는 우승 모델·최종 모델을 선정하지 않았다.</p>''')
    proposal = '''# 보존 검사 방식 제안 (기존 테스트 미수정)

기존 test_eda_and_sources_preserved_report_complete는 stage2 preservation_checks.json의 before 항목 전체를 바이트 단위 SHA-256으로 검사한다.
그 목록에는 원본 분석 산출물뿐 아니라 src/data.py와 src/analysis.py도 포함된다.
따라서 주석·공백 수정이 허용된 이후에도 “과거 소스와 바이트 단위로 동일함”을 요구하는 부분은 실패한다.
실패는 원본 .dat나 보고서 손상을 직접 의미하지 않는다. 또한 앞선 소스 단언 실패로 뒤의 원본 검사까지 실행되지 않는 보호 공백이 있다.

제안:
1. 원본 .dat, EDA·학습 결과, 저장 모델은 기존 SHA-256을 영구 보존하고 각각 독립적인 검사로 분리한다.
2. 과거 소스 SHA-256은 실행 provenance 기록으로 유지한다. 현재 버전과 같다고 주장하거나 과거 값을 교체하지 않는다.
3. 주석·공백 변경은 승인된 과거 AST 지문, 변경 이력, 저장 예측 재현, 동작 테스트로 별도 확인한다.
4. 향후 기능 변경은 새 버전 소스 해시·설명·검증 기록을 별도 manifest로 추가한다. 자동 기준 갱신은 하지 않는다.
5. AST 일치는 문법 구조 동일성의 증거이며 의존성·환경·외부 상태까지 포함하는 완전한 기능 동일성 증명은 아니다.
6. 과거 기록에 포함된 ~$ 이름의 파일은 현재 없어 검증할 수 없다. 임시 파일 후보로 별도 표시하며 과거 기록은 유지한다. 향후 보존 목록은 정식 산출물과 캐시·잠금 파일을 분리하되 누락을 조용히 통과시키지 않는다.

이번 조치: 기존 테스트·기준·기존 해시 기록은 수정하지 않았다. 별도 historical_hash_audit.csv와 source_ast_audit.csv로 원래 보존 목적을 재검증한다.
향후 테스트 분리는 별도 검토·승인 후 수행할 변경 제안일 뿐 이번에는 적용하지 않는다.
전체 테스트에는 이전부터 있던 4행 예제 전처리 단위 테스트의 Fit이 포함된다. 이번 연구 모델 9개는 재학습하지 않는다.
'''
    (ROOT / 'reports/toluene_preservation_proposal.md').write_text(proposal, encoding='utf-8')
    section('9. 현재 분석의 한계', '''<p>특징 분포의 이동과 실패가 함께 관찰됐지만, 센서 드리프트·농도·환경의 독립 효과는 분리하지 못했다.
Train Toluene 79개와 Batch 2의 5개는 다양한 조건을 대표하지 못할 수 있으나 필요한 최소 표본 수를 정하는 실험은 하지 않았다.
주변 분포 평균과 2차원 PCA는 전체 다변량 분류 경계를 완전히 표현하지 못한다. Test 관찰 후 진단이므로 사후 선택 편향도 있다.</p>
<h3>기존 테스트의 목적과 보존 검증</h3><p>기존 실패 테스트는 과거 before 목록 전체의 바이트 보존을 검사한다.
목록에는 EDA 산출물·보고서와 함께 Python 소스 2개도 들어 있다. 주석·공백 변경으로 이 소스 해시가 달라졌고,
첫 소스 단언 실패로 뒤의 원본 데이터 검사까지 실행되지 않는다. 이번에는 원본·모델·보고서·기존 결과를 별도 해시로 재확인했다.</p>''' +
            '<h3>기존 해시와 다르거나 현재 없는 항목 (기록은 수정하지 않음)</h3>' + table(mismatches[['registry', 'file', 'is_python', 'exists', 'transient_name_candidate', 'exact_match']]) +
            '<h3>과거 코드 구조 지문과 현재 AST 비교</h3>' + table(semantic[['registry', 'file', 'ast_unchanged']]) + '''
<p>원본·EDA·저장 모델·정식 학습 결과의 해시는 일치했으며, 코드 구조 비교도 일치해야 분석이 진행되도록 했다.
다만 과거 기록 2개에 포함된 outputs/model_comparison/zNex~$haremetrics.csv는 현재 없다.
이름상 임시 파일 후보로 구분했지만 실제 내용이나 삭제 경위는 확인하지 못했다. 보존됐다고 처리하거나 기존 기록에서 삭제하지 않았다.
이 누락 때문에 과거 스냅샷 전체를 검증하는 기존 테스트에 추가 실패가 발생할 수 있으며 실제 결과를 별도 보고한다.
이번 실행 전후의 코드·테스트·모든 기존 결과도 별도 manifest로 검사했다.
보존 목적을 유지하는 제안은 toluene_preservation_proposal.md에 기록했다. 기존 테스트나 과거 해시를 덮어쓰지 않았다.
전체 테스트의 실제 결과는 outputs/toluene_analysis/test_results.txt와 XML에 실행 후 기록한다.</p>''')
    section('10. 다음 단계 제안', '''<p>첫째, Toluene이 존재하는 과거 시기 범위와 6종 Validation을 확보하는 시간순 실험 설계를 먼저 확정한다.
둘째, 같은 분할에서 학습 범위 확장과 불균형 보정을 제한된 실험으로 비교한다.
셋째, Train 내부의 강건 스케일링·차원 축소·특징 선택·제한된 파라미터 탐색을 각각 기준선과 비교한다.
그 뒤 새로운 독립 시기의 자료로 모든 가스의 성능을 검증한다.</p>
<p>이번 단계는 분석과 설계만 수행했다. 기존 모델·PCA를 다시 Fit하거나 .joblib을 덮어쓰지 않았다.
실행: <code>.venv\\Scripts\\python.exe -B -m src.analyze_toluene</code>.
동일 경로의 4단계 산출물이 이미 있으면 덮어쓰기를 거부한다. 모든 새 표·예측·검사 결과는 outputs/toluene_analysis/에 저장한다.
원본과 기존 분석은 보존하며 최종 모델 선정·Commit·Push 없이 종료한다.</p>''')

    doc = '''<!doctype html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Toluene 분류 실패 분석</title><style>
body{font-family:"Malgun Gothic",Arial,sans-serif;max-width:1280px;margin:32px auto;padding:0 24px;color:#21384f;background:#f6f8fc;line-height:1.8}section{padding:24px;background:white;border:1px solid #dce4ed;border-radius:10px;margin:24px 0}h1,h2{color:#1c4e75}.table{overflow-x:auto;margin:16px 0}table{border-collapse:collapse;font-size:12px;white-space:nowrap}td,th{border:1px solid #dce4ed;padding:7px;text-align:right}th{background:#edf3fa}img{max-width:100%;height:auto}figure{margin:24px 0}figcaption{font-size:13px;color:#526b80}summary{cursor:pointer;color:#1c5e89}code{background:#edf3fa;padding:3px}</style></head><body><h1>Toluene 분류 실패 원인 분석 및 개선 실험 설계</h1><p>재학습 없음 · 기존 평가 설정 유지 · 탐색적 진단</p>'''
    doc += ''.join(sections) + '</body></html>'
    (ROOT / 'reports/toluene_failure_analysis.html').write_text(doc, encoding='utf-8')
