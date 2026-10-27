# 통제 실험의 실제 수치·표본 수·시드 변동 시각화
# 표시값과 CSV 및 한글 폰트 자동 대조

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager, ft2font
from matplotlib.patches import Patch
from matplotlib.text import Text
import numpy as np
import pandas as pd

from .data import ROOT, GASES
from .temporal_expansion import sha
from .temporal_representativeness_control import OUT, save

LABELS = {'early_mid': '초기843', 'spread_mid': '분산843', 'recent_mid': '최근843',
          'spread_small': '분산419', 'spread_max': '분산1689',
          'spread_mid_unit': '분산843·동일벌점',
          'spread_mid_anchor': '분산843·고정통계',
          'spread_mid_anchor_unit': '분산843·고정통계·동일벌점'}
PRIMARY = ['early_mid', 'spread_mid', 'recent_mid']
COLORS = ['#4384b0', '#429b76', '#ce7952']


# 주요9개 그래프와 표시 수치 검증 생성
def create_visuals():
    font = font_manager.findfont(font_manager.FontProperties(family='Malgun Gothic'), fallback_to_default=False)
    glyphs = ft2font.FT2Font(font).get_charmap()
    plt.rcParams.update({'font.family': 'Malgun Gothic', 'axes.unicode_minus': False, 'font.size': 10})
    summary = pd.read_csv(OUT / 'historical_summary.csv').set_index('setting')
    folds = pd.read_csv(OUT / 'fold_summary.csv')
    classes = pd.read_csv(OUT / 'class_summary.csv')
    seed = pd.read_csv(OUT / 'seed_summary.csv')
    checks, metadata = [], []

    def check(figure, source, key, field, actual, expected):
        assert np.isclose(actual, expected, atol=1e-10, equal_nan=True)
        checks.append(dict(figure=figure, source=source, key=key, field=field,
                           displayed_value=float(actual), expected_value=float(expected), matches=True))

    def finish(name, fig, axes):
        fig.tight_layout()
        fig.canvas.draw()
        missing = {c for text in fig.findobj(match=Text) for c in text.get_text()
                   if not c.isspace() and ord(c) >= 32 and ord(c) not in glyphs}
        assert not missing, missing
        assert all(ax.get_title() and ax.get_xlabel() and ax.get_ylabel() for ax in axes)
        assert all(ax.get_legend() is not None or fig.legends for ax in axes)
        path = OUT / f'{name}.png'
        fig.savefig(path, dpi=145, bbox_inches='tight')
        metadata.append(dict(figure=name, path=str(path.relative_to(ROOT)), sha256=sha(path),
                             font_file=font, font_sha256=sha(font), missing_used_glyphs=0,
                             titles_axes_legends_present=True))
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5))
    values = summary.loc[PRIMARY, 'mean_macro_f1'].to_numpy() * 100
    error = summary.loc[PRIMARY, 'seed_sd_macro_f1'].to_numpy() * 100
    bars = ax.bar(range(3), values, yerr=error, color=COLORS, capsize=5, label='5시드 평균 ± 시드 SD')
    for setting, bar, value in zip(PRIMARY, bars, values):
        check('composition_macro_f1', 'historical_summary', setting, 'mean_macro_f1_pct', bar.get_height(), value)
        ax.text(bar.get_x() + bar.get_width() / 2, value + 2, f'{value:.2f}', ha='center')
    ax.set(title='동일843개·동일 가스 구성의 시기 비교', xlabel='학습 구성 · 가스별127/216/91/69/301/39개',
           ylabel='Fold6·7·8 동일 가중 Macro F1 (%)', xticks=range(3),
           xticklabels=[LABELS[s] for s in PRIMARY], ylim=(0, 100))
    ax.legend()
    finish('composition_macro_f1', fig, [ax])

    fig, ax = plt.subplots(figsize=(9, 5))
    ordered = ['spread_small', 'spread_mid', 'spread_max']
    x = np.array([419, 843, 1689])
    y = summary.loc[ordered, 'mean_macro_f1'].to_numpy() * 100
    line = ax.errorbar(x, y, yerr=summary.loc[ordered, 'seed_sd_macro_f1'].to_numpy() * 100,
                      marker='o', capsize=5, label='분산 구성 · 5시드 평균 ± SD')
    for setting, actual, expected in zip(ordered, line.lines[0].get_ydata(), y):
        check('sample_size_effect', 'historical_summary', setting, 'mean_macro_f1_pct', actual, expected)
    ax.set(title='분산 구성 내 표본 예산 비교 · 과거Fold6·7·8', xlabel='분류기 학습 표본 수',
           ylabel='동일 가중 Macro F1 (%)', xticks=x, ylim=(0, 100))
    ax.legend()
    finish('sample_size_effect', fig, [ax])

    fig, ax = plt.subplots(figsize=(10, 6))
    matrix = np.array([[classes[(classes.setting == setting) & (classes.gas_id == gas)].recall_mean.mean()
                        for gas in GASES] for setting in PRIMARY]) * 100
    image = ax.imshow(matrix, vmin=0, vmax=100, cmap='YlGnBu', aspect='auto')
    for i, setting in enumerate(PRIMARY):
        for j, gas in enumerate(GASES):
            check('class_recall_heatmap', 'class_summary', f'{setting}|{gas}', 'equal_fold_recall_pct', image.get_array()[i, j], matrix[i, j])
            ax.text(j, i, f'{matrix[i, j]:.1f}', ha='center', va='center')
    ax.set(title='6종 가스 Recall · Fold별 평균을 동일 가중 · 시드5회', xlabel='가스 종류 · 각Fold support는CSV에 별도 기록',
           ylabel='동일843개 학습 구성', xticks=range(6), xticklabels=list(GASES.values()),
           yticks=range(3), yticklabels=[LABELS[s] for s in PRIMARY])
    ax.tick_params(axis='x', labelrotation=20)
    ax.legend(handles=[Patch(color='#4085a9', label='Recall (%) ·6/7/8 평가 · support는Fold마다 다름')], loc='lower left', bbox_to_anchor=(0, 1.02), fontsize=8)
    fig.colorbar(image, ax=ax, label='Recall (%)')
    finish('class_recall_heatmap', fig, [ax])

    fig, ax = plt.subplots(figsize=(10, 5))
    for setting, color in zip(PRIMARY, COLORS):
        sub = folds[folds.setting == setting].sort_values('scope')
        line = ax.errorbar([6, 7, 8], sub.macro_f1_mean * 100, yerr=sub.macro_f1_seed_sd * 100,
                          marker='o', capsize=4, label=LABELS[setting], color=color)
        for batch, actual, expected in zip([6, 7, 8], line.lines[0].get_ydata(), sub.macro_f1_mean * 100):
            check('batch_macro_f1', 'fold_summary', f'{setting}|{batch}', 'macro_f1_mean_pct', actual, expected)
    supports = folds[folds.setting == 'spread_mid'].sort_values('scope').validation_n.astype(int).tolist()
    ax.set(title='과거 시간순 평가 Batch별 성능 · Train843개 · 5시드 평균 ± SD', xlabel='평가 Batch · 표본 수',
           ylabel='Macro F1 (%)', xticks=[6, 7, 8], xticklabels=[f'{b}\nn={n}' for b, n in zip([6, 7, 8], supports)], ylim=(0, 100))
    ax.legend()
    finish('batch_macro_f1', fig, [ax])

    ordered = list(LABELS)
    fig, ax = plt.subplots(figsize=(14, 6))
    values = [seed[seed.setting == setting].equal_fold_macro_f1.to_numpy() * 100 for setting in ordered]
    boxes = ax.boxplot(values, tick_labels=[LABELS[s] for s in ordered])
    for i, (setting, array, median) in enumerate(zip(ordered, values, boxes['medians'])):
        ax.scatter(np.full(5, i + 1), array, s=24, alpha=.7, color='#367d9a')
        check('seed_distributions', 'seed_summary', setting, 'median_equal_fold_macro_f1_pct', median.get_ydata()[0], np.median(array))
    ax.set(title='반복 부분표본 시드5개의 결과 · 평가Fold6·7·8 동일 가중', xlabel='구성·예산·추가 대조 조건',
           ylabel='Macro F1 (%)')
    ax.tick_params(axis='x', labelrotation=25)
    ax.legend(handles=[Patch(color='#367d9a', label='점=고정 시드 결과 · 상자=사분위수 · 미래 불확실성 아님')])
    finish('seed_distributions', fig, [ax])

    composition = pd.read_csv(OUT / 'sample_composition.csv')
    fig, axes = plt.subplots(1, 3, figsize=(17, 6))
    for ax, setting in zip(axes, PRIMARY):
        sub = composition[(composition.fold == 'C') & (composition.setting == setting) & (composition.seed == 42)]
        matrix = sub.pivot(index='gas_id', columns='batch', values='n').reindex(index=GASES, columns=range(1, 8)).to_numpy()
        image = ax.imshow(matrix, cmap='Blues', aspect='auto', vmin=0, vmax=301)
        for i, gas in enumerate(GASES):
            for j, batch in enumerate(range(1, 8)):
                ax.text(j, i, str(matrix[i, j]), ha='center', va='center', fontsize=8,
                        color='white' if matrix[i, j] > 150 else 'black')
                check('training_composition', 'sample_composition', f'C|{setting}|42|{gas}|{batch}', 'n', image.get_array()[i, j], matrix[i, j])
        ax.set(title=f'{LABELS[setting]} · Train1–7→8\n가스별 배분량은5시드 공통',
               xlabel='학습 Batch 번호', ylabel='실제 가스', xticks=range(7), xticklabels=range(1, 8),
               yticks=range(6), yticklabels=list(GASES.values()))
        ax.legend(handles=[Patch(color='#4683a7', label='셀=분류기 학습 표본 수 ·0=미선택/부재')], fontsize=7)
    finish('training_composition', fig, axes)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for ax, gas in zip(axes, [6, 4]):
        for setting, color in zip(PRIMARY, COLORS):
            sub = classes[(classes.setting == setting) & (classes.gas_id == gas)].sort_values('fold')
            line = ax.errorbar([6, 7, 8], sub.recall_mean * 100, yerr=sub.recall_sd * 100,
                              marker='o', capsize=4, color=color, label=LABELS[setting])
            for batch, actual, expected in zip([6, 7, 8], line.lines[0].get_ydata(), sub.recall_mean * 100):
                check('focus_recall', 'class_summary', f'{setting}|{batch}|{gas}', 'recall_mean_pct', actual, expected)
        support = classes[(classes.setting == 'spread_mid') & (classes.gas_id == gas)].sort_values('fold').support.astype(int).tolist()
        ax.set(title=f'{GASES[gas]} Recall · Train843개 · 5시드 평균 ± SD', xlabel='평가 Batch · 해당 가스 표본 수',
               ylabel='Recall (%)', xticks=[6, 7, 8], xticklabels=[f'{b}\nn={n}' for b, n in zip([6, 7, 8], support)], ylim=(-3, 105))
        ax.legend()
    finish('focus_recall', fig, axes)

    controls = ['spread_mid', 'spread_mid_unit', 'spread_mid_anchor', 'spread_mid_anchor_unit']
    weights = pd.read_csv(OUT / 'class_weights.csv')
    fits = pd.read_csv(OUT / 'fit_records.csv')
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    bars = axes[0].bar(range(4), summary.loc[controls, 'mean_macro_f1'] * 100,
                       yerr=summary.loc[controls, 'seed_sd_macro_f1'] * 100, capsize=4, color='#4587a6',
                       label='5시드 평균 ± SD')
    for setting, bar in zip(controls, bars):
        check('preprocessing_weight_controls', 'historical_summary', setting, 'mean_macro_f1_pct', bar.get_height(), summary.loc[setting, 'mean_macro_f1'] * 100)
    axes[0].set(title='분산843개: 전처리×가중치 대조', xlabel='동일 분류기 표본 · 과거Fold6·7·8',
                ylabel='동일 가중 Macro F1 (%)', xticks=range(4), xticklabels=['기본', '동일벌점', '고정통계', '둘 다'], ylim=(0, 100))
    axes[0].legend()
    for offset, setting, label in [(-.18, 'spread_mid', 'balanced'), (.18, 'spread_mid_unit', '고정1.0')]:
        sub = weights[(weights.fold == 'C') & (weights.seed == 42) & (weights.setting == setting)].sort_values('gas_id')
        bars = axes[1].bar(np.arange(6) + offset, sub.class_weight, width=.36, label=label)
        for gas, bar, expected in zip(GASES, bars, sub.class_weight):
            check('preprocessing_weight_controls', 'class_weights', f'C|{setting}|42|{gas}', 'class_weight', bar.get_height(), expected)
    axes[1].set(title='동일 가스 예산의 클래스 가중치',
                xlabel='가스 ID ·1~6 원래 인코딩', ylabel='C에 곱해지는 클래스 승수', xticks=range(6), xticklabels=range(1, 7))
    axes[1].legend()
    for setting, marker in [('spread_mid', 'o'), ('spread_mid_anchor', 's')]:
        sub = fits[fits.setting == setting].groupby('fold').gamma_numeric.mean().reindex(['A', 'B', 'C'])
        line, = axes[2].plot([6, 7, 8], sub, marker=marker, label=LABELS[setting])
        for batch, actual, expected in zip([6, 7, 8], line.get_ydata(), sub):
            check('preprocessing_weight_controls', 'fit_records', f'{setting}|{batch}', 'gamma_mean', actual, expected)
    axes[2].set(title='gamma=scale의 실제 값 · Train 통계로 결정', xlabel='평가 Batch · 과거 Train만 사용',
                ylabel='RBF gamma ·5시드 평균', xticks=[6, 7, 8])
    axes[2].legend(fontsize=8)
    finish('preprocessing_weight_controls', fig, axes)

    future = pd.read_csv(OUT / 'exploratory_metrics.csv', dtype={'scope': str})
    references = pd.read_csv(OUT / 'reference_model_metrics.csv', dtype={'scope': str})
    fig, ax = plt.subplots(figsize=(12, 6))
    for setting in ['early_mid', 'spread_mid', 'recent_mid', 'spread_max']:
        sub = future[future.setting == setting].groupby('scope').macro_f1.agg(['mean', 'std']).reindex(['9', '10'])
        line = ax.errorbar([9, 10], sub['mean'] * 100, yerr=sub['std'] * 100, marker='o', capsize=4, label=LABELS[setting])
        for batch, actual, expected in zip([9, 10], line.lines[0].get_ydata(), sub['mean'] * 100):
            check('exploratory_macro_f1', 'exploratory_metrics', f'{setting}|{batch}', 'macro_f1_mean_pct', actual, expected)
    for model, n in [('A', 5933), ('B', 9546)]:
        sub = references[(references.model == model) & references.scope.isin(['9', '10'])].set_index('scope').loc[['9', '10']]
        line, = ax.plot([9, 10], sub.macro_f1 * 100, linestyle='--', label=f'기존{model} · Train{n}개 · 비통제 참조')
        for batch, actual, expected in zip([9, 10], line.get_ydata(), sub.macro_f1 * 100):
            check('exploratory_macro_f1', 'reference_model_metrics', f'{model}|{batch}', 'macro_f1_pct', actual, expected)
    ax.set(title='사전 지정 구성만 회고적 평가 · 독립 Test 아님', xlabel='평가 Batch ·9:470개 /10:3600개',
           ylabel='Macro F1 (%) · 신규 구성5시드 평균 ± SD', xticks=[9, 10], ylim=(0, 100))
    ax.legend(fontsize=9)
    finish('exploratory_macro_f1', fig, [ax])
    save('graph_value_checks', checks)
    save('graph_metadata', metadata)
