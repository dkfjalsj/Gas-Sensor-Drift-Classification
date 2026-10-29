# 대표 연구 Notebook·기존 수치·입출력 지문과 운영 보존 검사
import importlib
import json
from pathlib import Path

import nbformat
import numpy as np
import pandas as pd

from src.common.hashing import sha256_bytes
from src.data import ROOT
from src.train_models import evaluate
from src.model_management.registry import ModelRegistry
from src.webapp.service import MODEL_PATH, MODEL_SHA, DETECTOR_PATH, DETECTOR_SHA


def test_notebook_sections_outputs_and_no_errors():
    book = nbformat.read(ROOT / 'gas_sensor_drift.ipynb', as_version=4)
    nbformat.validate(book)
    assert len([c for c in book.cells if c.cell_type == 'markdown' and c.source.startswith('## ')]) == 11
    code = [c for c in book.cells if c.cell_type == 'code']
    assert all(c.execution_count is not None for c in code)
    assert not [o for c in code for o in c.outputs if o.output_type == 'error']
    assert any('image/png' in o.get('data', {}) for c in code for o in c.outputs)
    assert not any('.activate(' in c.source or '.rollback(' in c.source or '.initialize(' in c.source for c in code)
    assert any('RUN_BASELINE_REPLAY = False' in c.source for c in code)


def test_retained_research_result_bytes_match_originals():
    records = json.loads((ROOT / 'research/retained_results.json').read_text(encoding='utf-8'))
    for relative, expected in records['files'].items():
        assert sha256_bytes((ROOT / relative).read_bytes()) == expected, relative


def test_original_baseline_metrics_reproduce_from_saved_predictions():
    predictions = pd.read_csv(ROOT / 'outputs/model_comparison/predictions.csv')
    metrics = pd.read_csv(ROOT / 'outputs/model_comparison/metrics.csv')
    for keys, rows in predictions.groupby(['experiment', 'model', 'partition']):
        expected = metrics[(metrics.experiment == keys[0]) & (metrics.model == keys[1])
                           & (metrics.partition == keys[2]) & (metrics.scope == 'pooled')].iloc[0]
        actual, _, _ = evaluate(rows.y_true, rows.y_pred)
        for key in ['n', 'accuracy', 'macro_precision', 'macro_recall', 'macro_f1',
                    'macro_f1_fixed6', 'weighted_f1']:
            np.testing.assert_allclose(actual[key], expected[key], rtol=0, atol=1e-12)


def test_kept_python_modules_import_without_report_dependencies():
    for path in (ROOT / 'src').rglob('*.py'):
        if '__pycache__' not in path.parts:
            module = '.'.join(path.relative_to(ROOT).with_suffix('').parts)
            if module.endswith('.__init__'):
                module = module.removesuffix('.__init__')
            importlib.import_module(module)


def test_official_models_and_operating_state_preserved():
    assert sha256_bytes(MODEL_PATH.read_bytes()) == MODEL_SHA
    assert sha256_bytes(DETECTOR_PATH.read_bytes()) == DETECTOR_SHA
    manager = ModelRegistry()
    assert manager.current()['model']['kind'] == 'official'
    assert len(manager.read()['events']) == 1
