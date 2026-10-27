# 한글 그래프와 CSV 수치·숫자 Batch 순서의 자동 일치 검사
# 저장 모델 기준 변환만 사용한 진단 시각화

import json

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager, ft2font
from matplotlib.patches import Patch
from matplotlib.text import Text
import numpy as np
import pandas as pd

from .data import ROOT, FEATURES, GASES
from .temporal_expansion import sha, write_json

OUT = ROOT / 'outputs/temporal_generalization_validation'


# 모든 그래프의 실제 표시값과 기준 표를 대조
def create_visuals(frame, model_A):
    font = font_manager.findfont(font_manager.FontProperties(family='Malgun Gothic'), fallback_to_default=False)
    glyphs = ft2font.FT2Font(font).get_charmap()
    plt.rcParams.update({'font.family': 'Malgun Gothic', 'axes.unicode_minus': False, 'font.size': 10})
    metrics = pd.read_csv(OUT / 'evaluation_metrics.csv', dtype={'scope': str})
    classes = pd.read_csv(OUT / 'class_metrics.csv', dtype={'scope': str})
    cm = pd.read_csv(OUT / 'confusion_matrices.csv', dtype={'scope': str})
    checks, metadata, sensor_stats = [], [], []

    def check(figure, series, model, batch, gas, statistic, displayed, expected, source, predicted_id=0):
        if not np.isclose(displayed, expected, rtol=1e-12, atol=1e-10):
            raise AssertionError(f'Plot mismatch: {figure} {series} {batch} {displayed} {expected}')
        checks.append(dict(figure=figure, series=series, model=model, scope=str(batch), gas_id=gas,
                           predicted_id=predicted_id, statistic=statistic, displayed_value=float(displayed),
                           expected_value=float(expected), source=source, matches=True))

    def finish(name, fig, axes):
        fig.tight_layout()
        fig.canvas.draw()
        missing = set()
        for text in fig.findobj(match=Text):
            missing.update(char for char in text.get_text() if not char.isspace() and ord(char) >= 32 and ord(char) not in glyphs)
        if missing:
            raise RuntimeError(f'Korean glyphs missing: {missing}')
        assert all(ax.get_title() and ax.get_xlabel() and ax.get_ylabel() for ax in axes)
        assert all(ax.get_legend() is not None or fig.legends for ax in axes)
        path = OUT / f'{name}.png'
        fig.savefig(path, dpi=150, bbox_inches='tight')
        metadata.append(dict(figure=name, path=str(path.relative_to(ROOT)), sha256=sha(path),
                             font_family='Malgun Gothic', font_file=font, missing_korean_glyphs=0,
                             titles_axes_legends_present=True, missing_used_glyphs=0))
        plt.close(fig)

    def metric(name, batch, field):
        return float(metrics[(metrics.model == name) & (metrics.scope == str(batch))][field].iloc[0])

    # 1. 숫자 순서의 Batch별 Macro F1 막대
    fig, ax = plt.subplots(figsize=(10, 5))
    for offset, name in [(-.18, 'A'), (.18, 'B')]:
        values = [metric(name, batch, 'macro_f1') * 100 for batch in [8, 9, 10]]
        bars = ax.bar(np.arange(3) + offset, values, width=.36, label=f'모델 {name}')
        for batch, bar, expected in zip([8, 9, 10], bars, values):
            check('batch_macro_f1', 'macro_f1', name, batch, 0, 'macro_f1_pct', bar.get_height(), expected, 'evaluation_metrics.csv')
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f'{expected:.2f}', ha='center')
    ax.set(title='Batch별 모델 Macro F1 비교', xlabel='Batch 번호 · 표본 수', ylabel='Macro F1 (%)',
           xticks=range(3), xticklabels=['8 · n=294', '9 · n=470', '10 · n=3600'], ylim=(0, 105))
    ax.legend()
    finish('batch_macro_f1', fig, [ax])

    # 2. 클래스별 Recall과 실제 정답 수
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    for ax, name in zip(axes, ['A', 'B']):
        data = classes[(classes.model == name) & (classes.scope.isin(['8', '9', '10']))]
        matrix = data.pivot(index='gas_id', columns='scope', values='recall').reindex(index=range(1, 7), columns=['8', '9', '10'])
        image = ax.imshow(matrix.to_numpy() * 100, vmin=0, vmax=100, cmap='YlGnBu', aspect='auto')
        for i, gas in enumerate(GASES):
            for j, batch in enumerate([8, 9, 10]):
                row = data[(data.gas_id == gas) & (data.scope == str(batch))].iloc[0]
                actual = float(image.get_array()[i, j])
                check('class_recall_heatmap', 'recall', name, batch, gas, 'recall_pct', actual,
                      row.recall * 100, 'class_metrics.csv')
                ax.text(j, i, f'{actual:.1f}%\n{row.correct_n}/{row.support}', ha='center', va='center', fontsize=8)
        ax.set(title=f'모델 {name} · 가스별 Recall', xlabel='Batch 번호', ylabel='실제 가스',
               xticks=range(3), xticklabels=[8, 9, 10], yticks=range(6), yticklabels=list(GASES.values()))
        ax.legend(handles=[Patch(facecolor='#b8dfe0', label='셀: Recall · 정답/표본 수')], loc='upper center', bbox_to_anchor=(.5, -.1), fontsize=8)
        fig.colorbar(image, ax=ax, label='Recall (%)', shrink=.7)
    finish('class_recall_heatmap', fig, axes)

    # 3·4. 원래 개수와 정답 행 기준 비율 병기
    for name in ['A', 'B']:
        fig, axes = plt.subplots(1, 3, figsize=(19, 6))
        for ax, batch in zip(axes, [8, 9, 10]):
            sub = cm[(cm.model == name) & (cm.scope == str(batch))]
            matrix = sub.pivot(index='actual_id', columns='predicted_id', values='row_fraction').to_numpy() * 100
            counts = sub.pivot(index='actual_id', columns='predicted_id', values='count').to_numpy()
            image = ax.imshow(matrix, cmap='Blues', vmin=0, vmax=100)
            for i, gas in enumerate(GASES):
                for j, predicted in enumerate(GASES):
                    check(f'confusion_model_{name}', 'row_fraction', name, batch, gas, 'row_fraction_pct',
                          float(image.get_array()[i, j]), matrix[i, j], 'confusion_matrices.csv', predicted)
                    ax.text(j, i, f'{counts[i, j]}\n({matrix[i, j]:.0f}%)', ha='center', va='center', fontsize=7)
            ax.set(title=f'모델 {name} · Batch {batch}', xlabel='예측 가스', ylabel='실제 가스',
                   xticks=range(6), yticks=range(6), xticklabels=list(GASES.values()), yticklabels=list(GASES.values()))
            ax.tick_params(axis='x', rotation=65)
            ax.legend(handles=[Patch(facecolor='#99c6e3', label='셀: 개수 · 실제 가스 행 내 비율')],
                      loc='upper center', bbox_to_anchor=(.5, -.32), fontsize=7)
            fig.colorbar(image, ax=ax, shrink=.65, label='정답 행 기준 예측 비율 (%)')
        finish(f'confusion_model_{name}', fig, axes)

    # 5. 두 집중 가스의 정답·오답 개수
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    for ax, gas in zip(axes, [6, 4]):
        labels, correct, errors, rows = [], [], [], []
        for batch in [8, 9, 10]:
            for name in ['A', 'B']:
                row = classes[(classes.model == name) & (classes.scope == str(batch)) & (classes.gas_id == gas)].iloc[0]
                labels.append(f'{batch}-{name}\nn={row.support}')
                correct.append(row.correct_n)
                errors.append(row.error_n)
                rows.append((batch, name, row))
        first = ax.bar(range(6), correct, label='정분류', color='#2c8b67')
        second = ax.bar(range(6), errors, bottom=correct, label='오분류', color='#e59b4a')
        for i, (batch, name, row) in enumerate(rows):
            check('focus_correct_errors', 'correct', name, batch, gas, 'correct_n', first[i].get_height(), row.correct_n, 'class_metrics.csv')
            check('focus_correct_errors', 'error', name, batch, gas, 'error_n', second[i].get_height(), row.error_n, 'class_metrics.csv')
            ax.text(i, row.support + 5, f'정답 {row.correct_n}', ha='center', fontsize=8)
        ax.set(title=f'{GASES[gas]} · 정분류와 오분류', xlabel='Batch-모델 · 실제 표본 수', ylabel='표본 수',
               xticks=range(6), xticklabels=labels, ylim=(0, max(correct[i] + errors[i] for i in range(6)) * 1.16))
        ax.legend()
    finish('focus_correct_errors', fig, axes)

    # 6. 시기별 성능과 클래스별 변화 함께 표시
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    for name in ['A', 'B']:
        line, = axes[0].plot([8, 9, 10], [metric(name, b, 'macro_f1') * 100 for b in [8, 9, 10]], marker='o', label=f'모델 {name}')
        for batch, value in zip(line.get_xdata(), line.get_ydata()):
            check('performance_changes', 'macro_f1', name, int(batch), 0, 'macro_f1_pct', value,
                  metric(name, int(batch), 'macro_f1') * 100, 'evaluation_metrics.csv')
    axes[0].set(title='관찰된 Batch의 Macro F1 변화', xlabel='Batch 번호', ylabel='Macro F1 (%)', xticks=[8, 9, 10], ylim=(0, 100))
    axes[0].legend()
    for j, gas in enumerate(GASES):
        deltas = []
        for batch in [8, 9, 10]:
            sub = classes[(classes.gas_id == gas) & (classes.scope == str(batch))].set_index('model')
            deltas.append(100 * (sub.loc['B', 'recall'] - sub.loc['A', 'recall']))
        bars = axes[1].bar(np.arange(3) + (j - 2.5) * .12, deltas, .12, label=GASES[gas])
        for batch, bar, delta in zip([8, 9, 10], bars, deltas):
            check('performance_changes', 'recall_delta', 'B_minus_A', batch, gas, 'recall_delta_pp',
                  bar.get_height(), delta, 'class_metrics.csv')
    axes[1].axhline(0, color='black', linewidth=.8)
    axes[1].set(title='같은 표본에서 가스별 Recall 변화', xlabel='Batch 번호', ylabel='B - A Recall (%p)',
                xticks=range(3), xticklabels=[8, 9, 10])
    axes[1].legend(fontsize=7, ncol=2)
    finish('performance_changes', fig, axes)

    # 7. 기존 진단 특징을 그림에만 사용
    chosen = pd.read_csv(ROOT / 'outputs/temporal_failure_diagnostics/selected_plot_features.csv')
    scaler = model_A.named_steps['scaler']
    for gas in [6, 4]:
        selected = chosen[chosen.gas_id == gas].feature.tolist()
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        for ax, feature in zip(axes, selected):
            j = FEATURES.index(feature)
            subsets = [(f'Train1–{end}', frame[(frame.batch <= end) & (frame.gas == gas)]) for end in [6, 7]]
            subsets += [(str(batch), frame[(frame.batch == batch) & (frame.gas == gas)]) for batch in [8, 9, 10]]
            values = [(sub[feature].to_numpy() - scaler.mean_[j]) / scaler.scale_[j] for _, sub in subsets]
            boxes = ax.boxplot(values, tick_labels=[f'{label}\nn={len(sub)}' for label, sub in subsets], showfliers=True,
                               flierprops=dict(markersize=2))
            for index, ((label, sub), value) in enumerate(zip(subsets, values)):
                actual_median = float(boxes['medians'][index].get_ydata()[0])
                check(f'sensor_distribution_{gas}', feature, 'frozen_A_scaler', label, gas, 'median_z',
                      actual_median, np.median(value), 'sensor_plot_statistics.csv')
                sensor_stats.append(dict(gas_id=gas, feature=feature, partition=label, n=len(sub),
                                         median_z=actual_median, mean_z=float(value.mean()), std_z=float(value.std(ddof=0)),
                                         q25_z=float(np.quantile(value, .25)), q75_z=float(np.quantile(value, .75))))
            ax.set(title=f'{GASES[gas]} · {feature}', xlabel='학습 범위 / Batch · 표본 수', ylabel='모델 A Train 기준 표준화 값')
            ax.tick_params(axis='x', labelsize=8)
            ax.legend(handles=[Patch(facecolor='white', edgecolor='black', label='상자 IQR · 중앙선 중앙값 · 점 극단값')], fontsize=7)
        finish(f'sensor_distribution_{gas}', fig, axes)
    pd.DataFrame(sensor_stats).to_csv(OUT / 'sensor_plot_statistics.csv', index=False, encoding='utf-8')
    pd.DataFrame(checks).to_csv(OUT / 'graph_value_checks.csv', index=False, encoding='utf-8')
    pd.DataFrame(metadata).to_csv(OUT / 'graph_metadata.csv', index=False, encoding='utf-8')
    write_json(OUT / 'korean_font_verification.json', dict(font_family='Malgun Gothic', font_file=font,
                                                        font_sha256=sha(font), missing_used_korean_glyphs=0,
                                                        missing_used_glyphs=0))
