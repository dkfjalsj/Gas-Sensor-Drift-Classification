# 가스별 시기 구성·성능 보호·회고적 혼동행렬 시각화
# 실제 표시값과 CSV·한글 글꼴 검증

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
from .gas_specific_temporal_balancing import OUT, MID_SETTINGS, save

LABELS = {'spread_mid': '분산843', 'recent_mid': '최근843', 'mixed_mid': '가스혼합843',
          'coverage_mid': '최소대표843', 'spread_max': '분산1689',
          'mixed_max': '가스혼합1689', 'coverage_max': '최소대표1689'}
COLORS = ['#357da5', '#d18343', '#439b79', '#a16aac']


# 필수8종을포함한10개 그림 생성
def create_visuals():
    font = font_manager.findfont(font_manager.FontProperties(family='Malgun Gothic'), fallback_to_default=False)
    glyphs = ft2font.FT2Font(font).get_charmap()
    plt.rcParams.update({'font.family': 'Malgun Gothic', 'axes.unicode_minus': False, 'font.size': 10})
    summary = pd.read_csv(OUT / 'all_summary.csv').set_index('setting')
    mid_seed = pd.read_csv(OUT / 'mid_seed_summary.csv')
    metric = pd.read_csv(OUT / 'historical_metrics.csv')
    classes = pd.read_csv(OUT / 'historical_class_metrics.csv')
    checks, metadata = [], []

    def check(fig, source, key, field, actual, expected):
        assert np.isclose(actual, expected, atol=1e-10, equal_nan=True)
        checks.append(dict(figure=fig, source=source, key=key, field=field,
                           displayed_value=float(actual), expected_value=float(expected), matches=True))

    def finish(name, fig, axes):
        fig.tight_layout(rect=(0, .07, 1, 1) if fig.legends else None)
        fig.canvas.draw()
        missing = {c for t in fig.findobj(match=Text) for c in t.get_text()
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

    fig, ax = plt.subplots(figsize=(10, 5))
    values = summary.loc[MID_SETTINGS, 'mean_macro_f1'].to_numpy() * 100
    bars = ax.bar(range(4), values, yerr=summary.loc[MID_SETTINGS, 'seed_sd_macro_f1'] * 100,
                  capsize=5, color=COLORS, label='5시드 평균 ± 시드 SD')
    for setting, bar, expected in zip(MID_SETTINGS, bars, values):
        check('strategy_macro_f1', 'all_summary', setting, 'mean_macro_f1_pct', bar.get_height(), expected)
        ax.text(bar.get_x() + bar.get_width() / 2, expected + 2, f'{expected:.2f}', ha='center')
    ax.set(title='가스별 시기 구성 비교 · Train843개 · 시드11/23/42/67/101',
           xlabel='구성 · Train1–3/1–6/1–7 → Validation6/7/8',
           ylabel='Fold 동일 가중 Macro F1 (%)', xticks=range(4),
           xticklabels=[LABELS[s] for s in MID_SETTINGS], ylim=(0, 100))
    ax.legend()
    finish('strategy_macro_f1', fig, [ax])

    fig, ax = plt.subplots(figsize=(10, 6))
    for setting, color in zip(MID_SETTINGS, COLORS):
        sub = mid_seed[mid_seed.setting == setting]
        x, y = sub.mean_toluene_recall.mean() * 100, sub.mean_acetaldehyde_recall.mean() * 100
        artist = ax.errorbar(x, y, xerr=sub.mean_toluene_recall.std() * 100,
                            yerr=sub.mean_acetaldehyde_recall.std() * 100,
                            marker='o', capsize=4, color=color, label=LABELS[setting])
        ax.annotate(LABELS[setting], (x, y), xytext=(7, 7), textcoords='offset points')
        check('focus_joint_recall', 'mid_seed_summary', setting, 'toluene_recall_pct', artist.lines[0].get_xdata()[0], x)
        check('focus_joint_recall', 'mid_seed_summary', setting, 'acetaldehyde_recall_pct', artist.lines[0].get_ydata()[0], y)
    ax.axvline(summary.loc['spread_mid', 'toluene_recall'] * 100 - 5, linestyle='--', color='grey')
    ax.axhline(summary.loc['spread_mid', 'acetaldehyde_recall'] * 100 - 5, linestyle='--', color='grey')
    ax.set(title='집중2가스 Recall 동시 비교 · Train843 · 3Fold/5시드\nT support=467/568/18 · Ac support=29/744/33',
           xlabel='Toluene 평균 Recall (%)', ylabel='Acetaldehyde 평균 Recall (%)', xlim=(0, 100), ylim=(0, 100))
    ax.legend(fontsize=9)
    finish('focus_joint_recall', fig, [ax])

    fig, ax = plt.subplots(figsize=(11, 6))
    matrix = np.array([[classes[(classes.setting == s) & (classes.gas_id == g)].recall.mean()
                        for g in GASES] for s in MID_SETTINGS]) * 100
    image = ax.imshow(matrix, cmap='YlGnBu', vmin=0, vmax=100, aspect='auto')
    for i, setting in enumerate(MID_SETTINGS):
        for j, gas in enumerate(GASES):
            ax.text(j, i, f'{matrix[i, j]:.1f}', ha='center', va='center', color='white' if matrix[i, j] > 70 else 'black')
            check('gas_recall_heatmap', 'historical_class_metrics', f'{setting}|{gas}', 'mean_recall_pct', image.get_array()[i, j], matrix[i, j])
    ax.set(title='6종 가스 Recall · Train843개 · 과거Fold6/7/8 · 5시드 평균', xlabel='실제 가스 · Fold별 support는 보고서 표 참조',
           ylabel='학습 시기 구성', xticks=range(6), xticklabels=list(GASES.values()),
           yticks=range(4), yticklabels=[LABELS[s] for s in MID_SETTINGS])
    ax.tick_params(axis='x', labelrotation=20)
    fig.colorbar(image, ax=ax, label='Recall (%)')
    fig.legend(handles=[Patch(color='#4886ab', label='Fold 동일 가중 · 독립 반복 아님 · 전체 학습843개')], loc='lower center')
    finish('gas_recall_heatmap', fig, [ax])

    composition = pd.read_csv(OUT / 'executed_sample_composition.csv')
    fig, axes = plt.subplots(2, 2, figsize=(15, 11))
    for ax, setting in zip(axes.ravel(), MID_SETTINGS):
        sub = composition[(composition.fold == 'C') & (composition.seed == 42) & (composition.setting == setting)]
        matrix = sub.pivot(index='gas_id', columns='batch', values='n').reindex(index=GASES, columns=range(1, 8)).to_numpy()
        available = sub.pivot(index='gas_id', columns='batch', values='available').reindex(index=GASES, columns=range(1, 8)).to_numpy()
        cmap = plt.colormaps['Blues'].copy()
        cmap.set_bad('#dddddd')
        ax.imshow(np.ma.masked_where(available == 0, matrix), vmin=0, vmax=301, cmap=cmap, aspect='auto')
        for i, gas in enumerate(GASES):
            for j, batch in enumerate(range(1, 8)):
                text = '부재' if available[i, j] == 0 else str(matrix[i, j])
                ax.text(j, i, text, ha='center', va='center', fontsize=8,
                        color='white' if matrix[i, j] > 150 else 'black')
                check('gas_batch_composition', 'executed_sample_composition', f'C|{setting}|42|{gas}|{batch}', 'n', matrix[i, j], matrix[i, j])
        ax.set(title=f'{LABELS[setting]} · Train1–7→8 · seed42 · n=843', xlabel='학습 Batch 번호', ylabel='학습 가스',
               xticks=range(7), xticklabels=range(1, 8), yticks=range(6), yticklabels=list(GASES.values()))
    fig.legend(handles=[Patch(color='#4687aa', label='숫자=학습 수 (5시드 배분량 같음)'),
                        Patch(color='#dddddd', label='회색=해당 가스의 실제 표본 부재 · Recall0 뜻 아님')],
               loc='lower center', ncol=2)
    finish('gas_batch_composition', fig, axes.ravel())

    fig, ax = plt.subplots(figsize=(11, 6))
    for setting, color in zip(MID_SETTINGS, COLORS):
        sub = metric[metric.setting == setting].groupby('scope').macro_f1.agg(['mean', 'std']).reindex([6, 7, 8])
        artist = ax.errorbar([6, 7, 8], sub['mean'] * 100, yerr=sub['std'] * 100,
                             marker='o', capsize=4, label=LABELS[setting], color=color)
        for batch, actual, expected in zip([6, 7, 8], artist.lines[0].get_ydata(), sub['mean'] * 100):
            check('fold_macro_f1', 'historical_metrics', f'{setting}|{batch}', 'mean_macro_f1_pct', actual, expected)
    ax.set(title='Fold별 성능 · Train843개 · 5시드 평균 ± SD', xlabel='시간순 Validation Batch ·6:n2300 /7:n3613 /8:n294',
           ylabel='Macro F1 (%)', xticks=[6, 7, 8], ylim=(0, 100))
    ax.legend()
    finish('fold_macro_f1', fig, [ax])

    seeds = pd.read_csv(OUT / 'all_seed_summary.csv')
    settings = [s for s in LABELS if s in set(seeds.setting)]
    fig, ax = plt.subplots(figsize=(13, 6))
    values = [seeds[seeds.setting == s].equal_fold_macro_f1.to_numpy() * 100 for s in settings]
    boxes = ax.boxplot(values, tick_labels=[LABELS[s] for s in settings])
    for i, (setting, array, median) in enumerate(zip(settings, values, boxes['medians'])):
        ax.scatter(np.full(5, i + 1), array, color='#357d9a', s=22)
        check('seed_distribution', 'all_seed_summary', setting, 'median_macro_f1_pct', median.get_ydata()[0], np.median(array))
    ax.set(title='고정5시드의 성능 분포 · 과거Validation6/7/8 동일 가중',
           xlabel='구성·학습 표본 수 · 확대 미실행 조건은 표시하지 않음', ylabel='Macro F1 (%)')
    ax.tick_params(axis='x', labelrotation=20)
    ax.legend(handles=[Patch(color='#357d9a', label='점=시드별 결과 · 상자=사분위수 · 미래 신뢰구간 아님')])
    finish('seed_distribution', fig, [ax])

    delta = pd.read_csv(OUT / 'mid_class_deltas.csv')
    matrix = delta.pivot(index='setting', columns='gas_id', values='mean_recall_delta').reindex(index=MID_SETTINGS, columns=GASES).to_numpy() * 100
    limit = max(10., float(np.abs(matrix).max()))
    fig, ax = plt.subplots(figsize=(11, 6))
    image = ax.imshow(matrix, cmap='RdBu', vmin=-limit, vmax=limit, aspect='auto')
    for i, setting in enumerate(MID_SETTINGS):
        for j, gas in enumerate(GASES):
            ax.text(j, i, f'{matrix[i, j]:+.1f}', ha='center', va='center', color='white' if abs(matrix[i, j]) > .7 * limit else 'black')
            check('recall_changes', 'mid_class_deltas', f'{setting}|{gas}', 'delta_pp', image.get_array()[i, j], matrix[i, j])
    ax.set(title='분산843 기준 가스별 Recall 증감 · 3Fold×5시드 평균', xlabel='실제 가스 · 같은 Fold와 시드끼리 비교',
           ylabel='학습 시기 구성 · 모두843개', xticks=range(6), xticklabels=list(GASES.values()),
           yticks=range(4), yticklabels=[LABELS[s] for s in MID_SETTINGS])
    ax.tick_params(axis='x', labelrotation=20)
    fig.colorbar(image, ax=ax, label='Recall 차이 (%p)')
    fig.legend(handles=[Patch(color='#b34b50', label='음수=손실'), Patch(color='#4478a4', label='양수=증가')], loc='lower center', ncol=2)
    finish('recall_changes', fig, [ax])

    cm = pd.read_csv(OUT / 'exploratory_confusion.csv', dtype={'scope': str})
    for batch, total in [(9, 470), (10, 3600)]:
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        for ax, setting in zip(axes.ravel(), MID_SETTINGS):
            sub = cm[(cm.setting == setting) & (cm.scope == str(batch))]
            counts = sub.groupby(['actual_id', 'predicted_id'])['count'].mean().unstack().reindex(index=GASES, columns=GASES).to_numpy()
            supports = sub.groupby('actual_id').support.first().reindex(GASES).to_numpy()
            matrix = counts / supports[:, None] * 100
            image = ax.imshow(matrix, vmin=0, vmax=100, cmap='Blues')
            for i, actual in enumerate(GASES):
                for j, predicted in enumerate(GASES):
                    ax.text(j, i, f'{matrix[i, j]:.1f}', ha='center', va='center', fontsize=8,
                            color='white' if matrix[i, j] > 60 else 'black')
                    check(f'exploratory_confusion_{batch}', 'exploratory_confusion', f'{setting}|{batch}|{actual}|{predicted}',
                          'mean_row_pct', image.get_array()[i, j], matrix[i, j])
            ax.set(title=f'{LABELS[setting]} · Train1–7 · Batch{batch} n={total}\n5시드 평균 행비율 · 회고적 진단',
                   xlabel='예측 가스', ylabel='실제 가스 · 실제 support', xticks=range(6), xticklabels=list(GASES.values()),
                   yticks=range(6), yticklabels=[f'{GASES[g]} n={n}' for g, n in zip(GASES, supports)])
            ax.tick_params(axis='x', labelrotation=30, labelsize=8)
        fig.legend(handles=[Patch(color='#4687aa', label='색·숫자=실제 가스별 행비율(%)의 시드 평균 · 반복 예측은 새 표본 아님')], loc='lower center')
        finish(f'exploratory_confusion_{batch}', fig, axes.ravel())

    sizes = pd.read_csv(OUT / 'size_comparisons.csv')
    fig, ax = plt.subplots(figsize=(11, 6))
    for offset, level in [(-.18, 'mid'), (.18, 'max')]:
        for i, scheme in enumerate(['spread', 'mixed', 'coverage']):
            setting = scheme + '_' + level
            if setting not in summary.index:
                ax.text(i + offset, 3, '미실행', rotation=90, ha='center')
                continue
            value = summary.loc[setting, 'mean_macro_f1'] * 100
            bar = ax.bar(i + offset, value, width=.35, color='#4084a8' if level == 'mid' else '#d18b4c',
                         yerr=summary.loc[setting, 'seed_sd_macro_f1'] * 100, capsize=4)
            check('expansion_comparison', 'all_summary', setting, 'mean_macro_f1_pct', bar[0].get_height(), value)
    ax.set(title='사전 지정·보호 통과 조건의 표본 확대 · 과거Fold6/7/8',
           xlabel='구성 · 미실행은0점 아님 ·5시드 평균 ± SD', ylabel='Macro F1 (%)',
           xticks=range(3), xticklabels=['분산', '가스혼합', '최소대표'], ylim=(0, 100))
    ax.legend(handles=[Patch(color='#4084a8', label='843개'), Patch(color='#d18b4c', label='1689개')])
    finish('expansion_comparison', fig, [ax])
    save('graph_value_checks', checks)
    save('graph_metadata', metadata)
