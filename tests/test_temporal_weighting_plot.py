# Batch 그래프의 숫자 순서와 실제 지표 일치 확인

import json

import pandas as pd
import pytest

from src.data import ROOT
from src.temporal_expansion import sha

OUT = ROOT / 'outputs/temporal_weighting'


def test_numeric_batch_plot_matches_metrics_and_preserves_history():
    audit = json.loads((OUT / 'plot_order_correction.json').read_text(encoding='utf-8'))
    coordinates = pd.read_csv(OUT / 'plot_coordinates.csv')
    metrics = pd.read_csv(OUT / 'evaluation_metrics.csv', dtype={'fold': str})
    for (_, name), sub in coordinates.groupby(['panel_train_end', 'model_id'], sort=False):
        assert sub.batch.tolist() == [9, 10]
        for _, point in sub.iterrows():
            expected = metrics[(metrics.config_id == name) & (metrics.fold == str(point.batch))].iloc[0]
            assert point.macro_f1 == pytest.approx(expected.macro_f1)
    for name, expected in audit['snapshots'].items():
        assert sha(OUT / name) == expected
    previous = json.loads((OUT / 'final_verification.json').read_text(encoding='utf-8'))
    assert audit['snapshots']['report_before_plot_order_fix.html'] == previous['report_final_sha256']
    assert sha(ROOT / 'reports/temporal_weighting_report.html') == audit['report_current_sha256']
    assert sha(OUT / 'evaluation_range_comparison.png') == audit['corrected_plot_sha256']
    assert sha(OUT / 'selection_frozen.json') == audit['frozen_selection_sha256']
