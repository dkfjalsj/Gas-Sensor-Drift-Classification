# 진단 결과 표·그림을 담은 한글 HTML 보고서 생성
# 저장된 실제 예측으로 성능 계산
import base64
import html
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from .data import ROOT, GASES, FEATURES, feature_label
from .diagnose_models import OUT, COMMON, SELECTED

MODELS = ['LogisticRegression', 'RandomForest', 'SVM_RBF']
EXPS = ['B_early', 'B_history']


# 긴 표에 가로 스크롤 적용
def table(frame, index=False):
    return (
        '<div class="table">'
        + frame.to_html(index=index, border=0, na_rep='NA', float_format=lambda v: f'{v:.4f}')
        + '</div>'
    )


# 계산 결과를 그림과 설명으로 연결
def build_report(t, manifest):
    metrics, gas, selection = t['metrics'], t['gas_errors'], t['selection_evidence']
    figures = {}
    folder = OUT / 'figures'
    folder.mkdir(exist_ok=True)
    plt.rcParams.update(
        {'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.grid': True, 'grid.alpha': 0.2}
    )

    def save(fig, name, caption):
        fig.tight_layout()
        p = folder / f'{name}.png'
        fig.savefig(p, dpi=125, bbox_inches='tight')
        plt.close(fig)
        figures[name] = (
            '<figure><img alt="'
            + html.escape(caption)
            + '" src="data:image/png;base64,'
            + base64.b64encode(p.read_bytes()).decode()
            + '"><figcaption>'
            + html.escape(caption)
            + '</figcaption></figure>'
        )

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    for row, exp in enumerate(EXPS):
        for col, metric in enumerate(['accuracy', 'macro_f1']):
            ax = axes[row, col]
            for model in MODELS:
                s = metrics[
                    (metrics.experiment == exp)
                    & (metrics.model == model)
                    & (metrics.partition == 'test')
                    & (metrics.scope == 'batch')
                ]
                ax.plot(s.batch, s[metric], marker='o', label=model)
            ax.set(
                title=exp + ': ' + metric,
                xlabel='Batch (ordered category)',
                ylabel=metric,
                ylim=(0, 1.02),
                xticks=range(3 if row == 0 else 5, 11),
            )
            ax.axvspan(5.5, 10.5, color='#e2f0f7', alpha=0.4)
            ax.legend(fontsize=8)
    save(
        fig,
        'batch_performance',
        '관찰: 파란 구간은 공통 6종이 존재하는 Batch 6–10. 나머지 Batch는 클래스 구성이 다르다. 선을 실제 경과 시간으로 해석하지 않는다.',
    )
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    for row, exp in enumerate(EXPS):
        for col, model in enumerate(MODELS):
            sub = gas[
                (gas.experiment == exp)
                & (gas.model == model)
                & (gas.partition == 'test')
                & (gas.scope == 'batch')
            ]
            p = sub.pivot(index='gas', columns='batch', values='recall').reindex(GASES.values())
            ax = axes[row, col]
            im = ax.imshow(
                np.ma.masked_invalid(p.to_numpy()), vmin=0, vmax=1, cmap='RdYlGn', aspect='auto'
            )
            for i in range(len(p)):
                for j in range(len(p.columns)):
                    v = p.iloc[i, j]
                    ax.text(
                        j,
                        i,
                        'NA' if pd.isna(v) else f'{v:.2f}',
                        ha='center',
                        va='center',
                        fontsize=8,
                    )
            ax.set(
                title=f'{exp} / {model}',
                xlabel='Test batch (ordered category)',
                ylabel='True gas class',
                xticks=range(len(p.columns)),
                xticklabels=p.columns,
                yticks=range(6),
                yticklabels=p.index,
            )
            fig.colorbar(im, ax=ax, label='Recall')
    save(
        fig,
        'gas_recall',
        '관찰: 가스별 Recall. NA는 실제 표본 없음, 0은 표본이 있지만 맞힌 예측 없음이다. support 및 F1은 gas_errors.csv에 함께 저장했다.',
    )
    for model in MODELS:
        fig, axes = plt.subplots(1, 3, figsize=(17, 6))
        for ax, exp, scope in zip(
            axes, ['A_random', *EXPS], ['pooled', 'common_6_10', 'common_6_10']
        ):
            cm = t['confusion_matrices']
            s = cm[
                (cm.experiment == exp)
                & (cm.model == model)
                & (cm.partition == 'test')
                & (cm.scope == scope)
            ]
            values = s['count'].to_numpy().reshape(6, 6)
            support = values.sum(axis=1)
            normalized = np.divide(
                values,
                support[:, None],
                out=np.zeros_like(values, dtype=float),
                where=support[:, None] > 0,
            )
            im = ax.imshow(normalized, vmin=0, vmax=1, cmap='Blues')
            for i in range(6):
                for j in range(6):
                    ax.text(
                        j,
                        i,
                        f'{values[i,j]}\n{normalized[i,j]:.2f}',
                        ha='center',
                        va='center',
                        fontsize=7,
                        color='white' if normalized[i, j] > 0.5 else 'black',
                    )
            ax.set(
                title=f'{model}\n{exp}: '
                + ('all Test rows' if exp == 'A_random' else 'same Test batches 6–10'),
                xlabel='Predicted gas class',
                ylabel='True gas class',
                xticks=range(6),
                xticklabels=GASES.values(),
                yticks=range(6),
                yticklabels=GASES.values(),
            )
            ax.tick_params(axis='x', rotation=45)
            ax.grid(False)
            fig.colorbar(im, ax=ax, label='Within-true-class fraction', fraction=0.046)
        save(
            fig,
            'cm_' + model,
            '숫자 첫 줄은 개수, 둘째 줄은 실제 클래스 안의 비율. 두 B 조건은 동일한 10,277개 표본을 평가한다. A는 부분 Test 표본으로 직접적인 쌍 비교가 아니다.',
        )
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    stats = t['feature_stats']
    for ax, index in zip(axes.flat, [1, 2, 65, 121]):
        for g, name in GASES.items():
            s = (
                stats[(stats.gas == g) & (stats.feature == f'f{index:03d}')]
                .set_index('batch')
                .reindex(range(1, 11))
            )
            ax.plot(s.index, s['median'], marker='o', label=name)
        ax.set_yscale('symlog', linthresh=1)
        ax.set(
            title=feature_label(index),
            xlabel='Batch (ordered category)',
            ylabel='Same-gas median (symlog)',
            xticks=range(1, 11),
        )
    axes[0, 0].legend(fontsize=8)
    save(
        fig,
        'feature_medians',
        '사전에 지정한 대표 특징의 가스별 중앙값. 평균·표준편차도 전체 128개 특징에 대해 feature_stats.csv에 제공한다. 가스 누락 구간은 끊었다.',
    )
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for ax, exp in zip(axes, EXPS):
        s = t['gas_shift']
        p = (
            s[(s.experiment == exp) & s.batch.isin(COMMON)]
            .pivot(index='gas', columns='batch', values='shift')
            .reindex(GASES.values())
        )
        im = ax.imshow(p, aspect='auto', cmap='viridis')
        ax.set(
            title=exp + ': within-gas Wasserstein shift',
            xlabel='Common future batch',
            ylabel='Gas class',
            xticks=range(5),
            xticklabels=COMMON,
            yticks=range(6),
            yticklabels=p.index,
        )
        fig.colorbar(im, ax=ax, label='Mean of 128 normalized feature distances')
    save(
        fig,
        'wasserstein',
        '동일 가스 Train 분포와 미래 Batch 분포의 Wasserstein 거리. 각 특징을 해당 Train 전체의 SD로 나눈 뒤 128개 특징을 동일 가중 평균했다. 두 Train 기준의 척도가 달라 B 간 절대값을 직접 비교하지 않는다.',
    )
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    for row, exp in enumerate(EXPS):
        for col, model in enumerate(MODELS):
            shifts = t['batch_shift']
            s = (
                shifts[(shifts.experiment == exp) & shifts.batch.isin(COMMON)]
                .set_index('batch')
                .reindex(COMMON)
            )
            m = (
                metrics[
                    (metrics.experiment == exp)
                    & (metrics.model == model)
                    & (metrics.partition == 'test')
                    & (metrics.scope == 'batch')
                ]
                .set_index('batch')
                .reindex(COMMON)
            )
            ax = axes[row, col]
            ax.scatter(s['shift'], 1 - m.macro_f1)
            for b in COMMON:
                ax.annotate(str(b), (s.loc[b, 'shift'], 1 - m.loc[b, 'macro_f1']))
            a = t['batch_associations']
            value = a[(a.experiment == exp) & (a.model == model)].spearman_shift_vs_f1_loss.iloc[0]
            ax.set(
                title=f'{exp}/{model}\nSpearman rho={value:.2f}, n=5',
                xlabel='Equal-gas mean normalized Wasserstein',
                ylabel='1 - Test macro F1',
            )
    save(
        fig,
        'shift_error_association',
        '각 점은 Batch 6–10 중 하나다. 단 5점의 기술적 순위 상관이며 인과·유의성 검정이 아니다. 전체 128개 특징 및 가스별 관련성도 CSV에 보존했다.',
    )
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    coords = t['pca_coordinates']
    pc = coords[coords.experiment == 'B_history']
    for ax, (g, name) in zip(axes.flat, GASES.items()):
        s = pc[pc.gas == g]
        im = ax.scatter(
            s.pc1, s.pc2, c=s.batch, cmap='viridis', s=5, alpha=0.4, vmin=0.5, vmax=10.5
        )
        ax.set(
            title='Same-gas PCA: ' + name, xlabel='PC1 (Train basis)', ylabel='PC2 (Train basis)'
        )
        fig.colorbar(im, ax=ax, label='Batch (ordered category)', ticks=[1, 3, 6, 8, 10])
    save(
        fig,
        'pca_same_gas',
        'B_history의 기존 Train 스케일러를 그대로 적용하고 Train에만 새 탐색용 PCA를 Fit했다. 평가 모델에는 사용하지 않는다. 가스별로 분리해 클래스 구성 혼합을 줄였다. 2차원 중첩은 분류 가능성의 확정 근거가 아니다.',
    )
    for name, source, value in [
        ('lr_coefficients', 'lr_coefficients', 'abs_coefficient'),
        ('rf_importance', 'rf_importance', 'importance'),
    ]:
        fig, axes = plt.subplots(1, 2, figsize=(15, 7))
        for ax, exp in zip(axes, EXPS):
            s = t[source]
            top = s[s.experiment == exp].groupby('feature')[value].mean().nlargest(12).sort_values()
            ax.barh(top.index, top.values)
            ax.set(
                title=exp + ': ' + name,
                xlabel=(
                    'Mean absolute standardized coefficient'
                    if name.startswith('lr')
                    else 'Impurity importance (MDI)'
                ),
                ylabel='Feature index',
            )
        save(
            fig,
            name,
            '상위 12개는 설명용 표시이며 특징 선택에 사용하지 않았다. LR은 클래스별 절대 계수의 평균, RF는 불순도 감소 중요도다. 서로 다른 중요도 값을 모델 간 동일 척도로 비교하지 않는다.',
        )
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for ax, exp in zip(axes, EXPS):
        s = t['svm_sensitivity']
        s = s[(s.experiment == exp) & (s.partition == 'test')].sort_values('batch')
        ax.plot(
            s.batch, s.similarity_median, 'o-', label='Median max RBF similarity to support vectors'
        )
        ax.plot(s.batch, s.accuracy, 's-', label='Batch accuracy')
        ax.set(
            title=exp + ': fixed SVM diagnostics',
            xlabel='Test batch (ordered category)',
            ylabel='Similarity / accuracy (0–1)',
            ylim=(0, 1.02),
            xticks=s.batch,
        )
        ax.legend(fontsize=8)
    save(
        fig,
        'svm_sensitivity',
        '기존 SVM의 gamma와 지지 벡터를 고정하고 exp(-gamma × 최소거리²)를 계산했다. 확률·신뢰도·이상치 임계값이 아니며 새 의사결정 규칙을 만들지 않았다.',
    )

    pooled = metrics[(metrics.partition == 'test') & (metrics.scope == 'pooled')]
    common = selection[selection.experiment.isin(EXPS)]
    common_gas = gas[
        (gas.partition == 'test') & (gas.scope == 'common_6_10') & gas.experiment.isin(EXPS)
    ]
    batch = metrics[(metrics.partition == 'test') & (metrics.scope == 'batch')]
    winner = (
        common[common.experiment == 'B_history']
        .sort_values('equal_batch_mean_f1', ascending=False)
        .iloc[0]
    )
    alternate = common[common.experiment == 'B_history'].sort_values('batch_sd_f1').iloc[0]
    worst = (
        common_gas.sort_values('error_rate', ascending=False)
        .groupby(['experiment', 'model'], sort=False)
        .head(1)
    )
    pair = t['error_pairs']
    top_pairs = (
        pair[
            (pair.partition == 'test') & (pair.scope == 'common_6_10') & pair.experiment.isin(EXPS)
        ]
        .sort_values('count', ascending=False)
        .groupby(['experiment', 'model'], sort=False)
        .head(4)
    )
    early_patterns = t['gas_errors']
    early_patterns = early_patterns[
        (early_patterns.partition.isin(['train', 'validation']))
        & (early_patterns.scope == 'pooled')
        & early_patterns.experiment.isin(EXPS)
    ]
    sections = []

    def section(title, body):
        sections.append('<section><h2>' + title + '</h2>' + body + '</section>')

    section(
        '1. 분석 목적 및 연구 질문',
        '''<p>랜덤 분할의 높은 성능, 미래 Batch에서의 성능 저하, 가스별 오류 집중, 동일 가스 특징 변화와 오류의 관련성,
모델 선정 기준을 조사한다. 기존 보고서·학습 코드·9개 저장 파이프라인·예측을 확인했다.</p>
<p><b>관찰</b>은 파일과 예측에서 계산한 사실, <b>해석</b>은 가능한 설명이다. 분류기 재학습, 튜닝, 임계값 변경,
전처리 변경, 특징 선택은 수행하지 않았다. 새 PCA는 그림을 위한 Train 전용 탐색 변환이다.</p>''',
    )
    section(
        '2. 기존 모델 비교 결과 요약',
        table(pooled[['experiment', 'model', 'n', 'accuracy', 'macro_f1', 'weighted_f1']])
        + '''
<p>A는 Train/Validation/Test=60/20/20, seed=42이고 모든 Batch의 표본을 학습한다.
B_early는 Train 1 / Validation 2 / Test 3–10, B_history는 Train 1–3 / Validation 4 / Test 5–10이다.
Train 크기는 각각 8,346 / 445 / 3,275다. 기존 예측을 재예측으로 대조해 일치시켰고 지표도 재계산했다.</p>
<p><b>해석:</b> A는 같은 수집 Batch의 다른 표본을 이미 학습했으므로 동일 수집 집합 내부의 구분 능력을 보여 준다.
약 99%의 F1만으로 미래 자료 성능을 보장하지 않는다. 정확 중복과 Train 외 전처리 Fit의 증거는 없지만,
근접 반복 측정·수집 의존성은 배제되지 않는다. 수집 Batch 혼합, 더 많은 학습량, 클래스 구성은 유력한 대안 설명이며 기여율은 분리하지 못했다.</p>''',
    )
    section(
        '3. Batch별 성능 변화',
        figures['batch_performance']
        + table(common)
        + '''
<p>동일 미래 Batch 6–10에는 6종이 모두 있고 총 10,277개 표본이 있다. 두 B 조건은 동일 행 전체를 사용한다.
A의 같은 Batch 지표는 그중 일부 Test 표본에 대한 값이다. 평균은 Batch 동일 가중, SD는 ddof=0의 기술적 표준편차다.</p>
<p>Batch 3–5는 Toluene이 없다. 해당 Batch의 macro 지표는 존재하는 5종 평균, fixed6는 누락 클래스를 0으로 둔 평균이다.
클래스 집합·support가 다른 Batch끼리 macro-F1을 단순 비교하지 않는다. 최저/최고 Batch 번호는 공통 6–10 범위에서 산출했다.</p>
<details><summary>전체 Batch별 표본 수·클래스 수·점수</summary>'''
        + table(
            batch[
                [
                    'experiment',
                    'model',
                    'batch',
                    'n',
                    'n_classes',
                    'accuracy',
                    'macro_f1',
                    'macro_f1_fixed6',
                    'missing_classes',
                ]
            ]
        )
        + '</details>',
    )
    section(
        '4. 가스별 오분류 패턴',
        figures['gas_recall']
        + ''.join(figures['cm_' + model] for model in MODELS)
        + '<h3>공통 미래 Batch의 클래스별 지표와 오류</h3>'
        + table(
            common_gas[
                ['experiment', 'model', 'gas', 'support', 'errors', 'error_rate', 'recall', 'f1']
            ]
        )
        + '<h3>실제 가스→잘못 예측한 가스: 개수 기준 상위 조합</h3>'
        + table(
            top_pairs[
                [
                    'experiment',
                    'model',
                    'true_gas',
                    'predicted_gas',
                    'count',
                    'true_support',
                    'true_class_fraction',
                ]
            ]
        )
        + '<h3>오류율이 가장 높은 가스 (개수와 구분)</h3>'
        + table(
            worst[['experiment', 'model', 'gas', 'support', 'errors', 'error_rate', 'recall', 'f1']]
        )
        + '<details><summary>초기 Train/Validation의 가스별 패턴</summary>'
        + table(
            early_patterns[
                [
                    'experiment',
                    'model',
                    'partition',
                    'gas',
                    'support',
                    'errors',
                    'error_rate',
                    'recall',
                    'f1',
                ]
            ]
        )
        + '</details>'
        + '''
<p>Train 점수는 학습 자료 재대입 점수이며 독립 성능이 아니다. Validation 2와 Validation 4는 서로 다른 표본/클래스 구성이다.
오류 개수에는 가스별 표본 수가 영향을 주므로 오류율과 support를 함께 봐야 한다.
두 가스 사이의 오분류가 많다는 사실은 화학적 유사성의 증거가 아니다.</p>''',
    )
    section(
        '5. 주요 센서 특징의 분포 변화',
        figures['feature_medians']
        + figures['wasserstein']
        + figures['pca_same_gas']
        + table(t['pca_variance'])
        + '''
<p>모든 128개 특징·가스·Batch의 mean/median/std(ddof=1)를 feature_stats.csv에 저장했다.
wasserstein.csv에는 특징별 원래 거리, 정규화 거리, 기준 SD, 양쪽 표본 수를 제공한다.
동일 가스 Train과 목표 Batch를 먼저 비교하고, 특징 거리→가스별 평균→가스 동일 가중 평균 순서로 합쳤다.
표본 수가 큰 가스가 전체 지표를 지배하지 않도록 했지만, 작은 표본의 분포 추정 오차는 남는다.
Train 기준 SD가 0이면 정규화 거리는 NA로 처리한다. PSI 임계값이나 정상/이상 임계값은 만들지 않았다.</p>
<p>각 B 조건의 기준 분포와 SD가 달라 두 B의 절대 거리는 직접적인 개선량이 아니다.
공통 6–10의 동일 가스 비교에서도 농도 구성·실험 조건 차이를 제거하지 못했다.
PCA는 기존 LR 파이프라인의 Train 전처리를 유지하고 Train만으로 축을 만든 뒤 전체 자료를 투영했다.
모델 입력이나 예측에는 사용하지 않았고 기존 모델을 저장하지도 않았다.</p>''',
    )
    train_comparison = t['train_scores'][
        ['experiment', 'model', 'n', 'accuracy', 'macro_f1']
    ].rename(columns={'accuracy': 'train_accuracy', 'macro_f1': 'train_macro_f1', 'n': 'train_n'})
    train_comparison = train_comparison.merge(
        selection[['experiment', 'model', 'pooled_macro_f1', 'equal_batch_mean_f1']],
        on=['experiment', 'model'],
    )
    section(
        '6. 모델별 장단점',
        table(train_comparison)
        + figures['lr_coefficients']
        + figures['rf_importance']
        + figures['svm_sensitivity']
        + '''
<p><b>LR:</b> 기존 다중 클래스 선형 점수의 계수를 분석했다. 계수는 Train 표준화 특징 1 SD 증가에 따른 클래스 점수 변화이며,
클래스 간 상대 비교로 해석해야 한다. 계수 부호는 원인·센서의 물리적 효과가 아니다.
단순 선형 구조가 비선형 관계를 놓칠 가능성은 있지만 원인 분리를 위한 새 실험은 하지 않았다.</p>
<p><b>RF:</b> feature_importances_는 학습 중 불순도 감소에 따른 MDI다. 중요도는 해당 Train의 분할에 대한 값이며
미래 예측 기여도나 시간 드리프트의 원인을 뜻하지 않는다. 높은 Train과 낮은 미래 점수의 격차는 초기 패턴 의존/분포 변화와 양립하지만
이것만으로 과적합 하나를 원인으로 확정하지 못한다. 높은 중요도의 특징을 삭제하거나 재학습하지 않았다.</p>
<p><b>SVM:</b> RBF의 비선형 경계가 랜덤 분할에서도 유일하게 우수하지 않았고 초기 Train의 미래 성능도 낮았다.
지지 벡터와의 커널 유사도는 고정 gamma에서 분포 이탈에 대한 참고 신호다.
유사도와 정확도가 항상 같이 움직이는 것은 아니며 확률 보정이나 새 판정 기준은 적용하지 않았다.</p>
<p>LR 계수와 RF 중요도는 계산 방식이 달라 값 자체를 비교하지 않는다. 입력은 128개 수치 특징이고 batch/정답/행 번호를 제외했다.
gas 1–6은 클래스 이름의 코드이며 연속적인 수치 순서가 아니다. feature index는 센서·추출 방식에 대응한다.
센서 특징 사이의 높은 상관은 계수와 중요도를 여러 변수에 나눠 보이게 할 수 있다.
Train의 |Spearman|≥0.9인 모든 특징 쌍을 correlated_feature_pairs.csv에 기록했으며 이 기준으로 특징을 선택하지 않았다.</p>''',
    )
    section(
        '7. 드리프트와 성능 저하의 연관성 및 대안 설명',
        figures['shift_error_association']
        + table(t['batch_associations'])
        + '<details><summary>가스별 특징 변화와 Recall 저하의 순위 상관</summary>'
        + table(t['gas_associations'])
        + '</details>'
        + '''
<p>공통 5개 Batch에서 특징 변화와 1−macro-F1 또는 1−recall의 Spearman 상관을 계산했다.
값이 일정하면 NA다. 128개 특징의 관련성도 전부 저장했지만 최고 상관 특징을 골라 성능 개선에 사용하지 않았다.
5점의 불안정한 순위 상관이며 독립 표본 가정, 클래스 간 의존성, 다중 탐색 문제가 있어 p값·유의성·인과를 주장하지 않는다.</p>
<p>분포 변화가 커도 클래스 구분에 중요하지 않은 방향일 수 있고, 작은 변화라도 경계 근처에서는 오류를 늘릴 수 있다.
가스 농도, 수집 환경, 센서 관리, 학습량, 클래스 구성, 수집·전처리 변화 등의 대안 설명이 있다.
따라서 센서 드리프트의 독립 효과나 성능 저하 중 설명 비율을 확정할 수 없다.</p>''',
    )
    section(
        '8. 모델 선정 평가표',
        table(common)
        + table(t['costs'])
        + f'''
<p>현재 관측 조건에서 <b>가장 유력한 탐색 후보는 {winner['model']}</b>다. B_history의 동일 미래 6–10에서
동일 가중 평균 macro-F1={winner['equal_batch_mean_f1']:.4f}, 최저 Batch={winner['min_batch_f1']:.4f},
pooled 최저 클래스 Recall={winner['min_class_recall']:.4f}({winner['worst_gas']})다.
변동성 대안 후보 {alternate['model']}는 SD={alternate['batch_sd_f1']:.4f}, 평균={alternate['equal_batch_mean_f1']:.4f}다.
이는 평균 하나로 최종 선택한 결과가 아니다. 심각한 가스별 실패와 support, 비용·해석성을 함께 검토해야 한다.</p>
<p>비용은 과거 fit 시간과 이번 동일 10,277개 입력에 대한 파이프라인 예측 3회 중앙값이다.
예열 128행, 전처리 포함, BLAS thread 한도 2이며 RF의 기존 n_jobs=-1은 유지했다.
운영 장치·동시 부하에 따라 달라지고 이 수치를 성능 보장으로 사용하지 않는다.
LR은 계수 설명이 쉽고 RF는 경로/중요도 설명이 가능하지만 상관 변수 영향이 있으며, SVM RBF는 직접적인 특징 계수가 없어 설명이 제한된다.</p>
<p>가스별 허용 가능한 오류 수준과 운영 비용 한도는 아직 정해지지 않았다. 이 Test를 보고 허용 기준이나 가중치를 맞추지 않는다.</p>''',
    )
    section(
        '9. 데이터 및 실험의 한계',
        '''<p>정확한 측정 시각과 농도·환경 기록이 부족하며 Batch는 불규칙한 시기 구간이다.
같은 시기를 Train과 Test가 공유하는 A와 시간순 B는 평가 목적이 다르다.
B_early와 B_history는 학습량·학습 시기·가스별 support가 동시에 바뀌므로 순수 시간 효과 실험이 아니다.
가스 구성과 표본 수를 맞춘 학습량 대조·반복 시드·독립 외부 검증·신뢰구간을 새로 수행하지 않았다.</p>
<p>지금은 Test 결과를 본 뒤 수행한 탐색적 해석이다. 중요도·관련성·최저 Batch를 보고 다음 실험을 고르면 선택 편향이 생길 수 있다.
작은 Batch와 소수 클래스의 변동, feature 간 상관, 같은 수집의 의존성으로 결과의 불확실성이 있다.</p>''',
    )
    section(
        '10. 최종 모델 선정 전 검토 사항',
        f'''
<p>{winner['model']}를 우선 검증 후보로, {alternate['model']}를 비교 후보로 유지한다.
가스별 심각한 실패가 허용 가능한지 먼저 검토하고, 독립 검증 전에 업무 중요도·허용 오류·비용을 확정해야 한다.
새로운 독립 Batch 또는 사전에 유보한 별도 자료에서 최종 검증이 필요하다.
Test에 맞춘 파라미터·전처리·임계값·특징 선택은 이번에 하지 않았다.</p>
<p>산출물은 outputs/model_diagnostics/와 이 보고서에만 생성했다. 기존 모델·EDA·모델 비교 결과는 실행 전후 해시로 보존을 확인했다.
재실행은 기존 진단 산출물이 있으면 중단한다. 사용자가 기존 진단을 별도로 보관한 뒤 실행할 수 있다.
실행: <code>.venv\\Scripts\\python.exe -B -m src.diagnose_models</code>.
기존 Python 파일에는 요청한 짧은 한글 주석만 추가했으며, 코드 구조 비교는 comment_audit.json에 기록한다.
주석 때문에 과거 소스 파일 해시를 고정한 기존 테스트 1건은 불일치할 수 있으며, 사용자 지시에 따라 해당 테스트와 과거 결과는 변경하지 않는다.
새 실험 모델 학습·튜닝·최종 확정·Commit·Push는 하지 않았다.</p>''',
    )
    doc = '''<!doctype html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Gas Sensor 모델 진단 보고서</title><style>
body{font-family:"Malgun Gothic",Arial,sans-serif;max-width:1280px;margin:30px auto;padding:0 24px;background:#f5f8fc;color:#20364c;line-height:1.8}section{background:white;border:1px solid #dae4ef;padding:24px;margin:24px 0;border-radius:10px}h1,h2{color:#174f73}.table{overflow-x:auto}table{border-collapse:collapse;font-size:12px;white-space:nowrap}th,td{border:1px solid #dae4ef;padding:7px;text-align:right}th{background:#edf4fa}img{max-width:100%;height:auto}figure{margin:24px 0}figcaption{font-size:13px;color:#536c80}summary{cursor:pointer;color:#155a82}code{background:#edf4fa;padding:3px}</style></head><body><h1>Gas Sensor Drift Classification · 모델 진단</h1>'''
    doc += (
        '<p>계산 시각(서울): '
        + html.escape(manifest['generated_at_seoul'])
        + '</p>'
        + ''.join(sections)
        + '</body></html>'
    )
    (ROOT / 'reports' / 'model_diagnostic_report.html').write_text(doc, encoding='utf-8')
