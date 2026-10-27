# Toluene 진단 수치와 기존 파일 보존 검증
# 새 분류기 학습 없이 저장된 분석 결과 대조

import ast
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy.stats import wasserstein_distance

from src.data import ROOT, read_config, load_dataset
from src.analyze_toluene import OUT, marginal_overlap


# Train·Validation·Test의 Toluene 표본 수 확인
def test_toluene_partition_counts_and_scope():
    counts = pd.read_csv(OUT / 'partition_counts.csv')
    expected = {'A_random': (1099, 367, 367), 'B_early': (74, 5, 1754), 'B_history': (79, 0, 1754)}
    for exp, values in expected.items():
        actual = counts[counts.experiment == exp].set_index('partition')
        assert tuple(actual.loc[['train', 'validation', 'test'], 'toluene_n']) == values
    metrics = pd.read_csv(OUT / 'toluene_metrics.csv')
    sub = metrics[(metrics.experiment == 'B_history') & (metrics.scope == 'pooled')]
    assert sub[sub.partition == 'test'].toluene_recall.eq(0).all()
    assert sub[sub.partition == 'validation'].toluene_recall.isna().all()
    early = metrics[(metrics.experiment == 'B_early') & (metrics.model == 'LogisticRegression') & (metrics.partition == 'test') & (metrics.scope == 'pooled')].iloc[0]
    assert early.correct_toluene == 12 and early.toluene_recall == pytest.approx(12 / 1754)


# 기존 모델의 클래스와 예측 재현 확인
def test_classes_and_exact_prediction_replay():
    audit = pd.read_csv(OUT / 'model_audit.csv')
    assert len(audit) == 9 and audit.exact_prediction_replay.all()
    assert audit.has_toluene_class.all() and audit.declared_classes.eq('1,2,3,4,5,6').all()
    predictions = pd.read_csv(OUT / 'predictions.csv')
    old = pd.read_csv(ROOT / 'outputs/model_comparison/predictions.csv')
    keys = ['experiment', 'model', 'partition', 'row_id']
    joined = old.merge(predictions, on=keys, validate='one_to_one', suffixes=('_old', '_new'))
    assert len(joined) == len(old)
    assert np.array_equal(joined.y_pred_old, joined.y_pred_new)
    assert np.array_equal(joined.y_true_old, joined.y_true_new)


# 같은 표본의 공통 오분류 개수 확인
def test_toluene_consensus_and_confusion_sums():
    consensus = pd.read_csv(OUT / 'consensus.csv')
    history = consensus[consensus.experiment == 'B_history']
    assert len(history) == 1754 and history.all_three_wrong.all()
    errors = pd.read_csv(OUT / 'toluene_confusion.csv')
    for _, group in errors.groupby(['experiment', 'model', 'partition', 'scope', 'batch']):
        assert group['count'].sum() == group.toluene_support.iloc[0]


# 거리와 겹침 계산의 기본 성질 및 원본 대조
def test_distance_and_overlap_reference():
    assert marginal_overlap([0, 1], [0, 1], [-np.inf, .5, np.inf]) == 1
    assert marginal_overlap([0, 0], [1, 1], [-np.inf, .5, np.inf]) == 0
    frame, _ = load_dataset(read_config())
    train = frame[frame.batch <= 3]
    ref = train[train.gas == 6].f001
    target = frame[(frame.batch == 10) & (frame.gas == 6)].f001
    d = pd.read_csv(OUT / 'feature_distances.csv')
    row = d[(d.experiment == 'B_history') & (d.reference_gas_id == 6) & (d.batch == 10) & (d.feature == 'f001')].iloc[0]
    assert row.wasserstein_raw == pytest.approx(wasserstein_distance(ref, target))
    assert row.wasserstein_scaled == pytest.approx(wasserstein_distance(ref, target) / train.f001.std(ddof=0))
    # 비율 합산의 미세한 부동소수점 오차만 허용
    assert d.histogram_overlap.between(-1e-12, 1 + 1e-12).all()


# 원본·모델·기존 결과와 코드 구조 보존 확인
def test_historical_and_current_preservation():
    history = pd.read_csv(OUT / 'historical_hash_audit.csv')
    material = ~history.is_python & ~history.transient_name_candidate
    assert history.loc[material, 'exact_match'].all()
    assert (~history.loc[history.is_python, 'exact_match']).any()
    assert pd.read_csv(OUT / 'source_ast_audit.csv').ast_unchanged.all()
    state = json.loads((OUT / 'run_manifest.json').read_text(encoding='utf-8'))
    assert state['before'] == state['after']
    for name, expected in state['before'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected
    for name, expected in state['raw_hashes'].items():
        assert hashlib.sha256((Path(read_config()['data_dir']) / name).read_bytes()).hexdigest() == expected


# 개선 설계안의 시간 순서와 평가 성격 확인
def test_proposed_protocol_is_forward_and_exploratory():
    plan = pd.read_csv(OUT / 'exploratory_protocol.csv')
    for row in plan.itertuples(index=False):
        end = int(row.train_batches.split('–')[1])
        assert end < row.validation_batch < row.test_batch
        assert min(row.train_toluene_n, row.validation_toluene_n, row.test_toluene_n) > 0
        assert row.evaluation_type.startswith('exploratory')


# 이번 분석에서 Fit이나 모델 저장이 없는지 확인
def test_no_fit_or_model_overwrite_and_report_complete():
    for name in ['analyze_toluene.py', 'toluene_report.py']:
        tree = ast.parse((ROOT / 'src' / name).read_text(encoding='utf-8'))
        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)]
        assert not any(node.func.attr in ['fit', 'fit_transform'] for node in calls)
        assert not any(
            node.func.attr == 'dump'
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == 'joblib'
            for node in calls
        )
    state = json.loads((OUT / 'run_manifest.json').read_text(encoding='utf-8'))
    assert state['classifier_fits'] == state['tuning_runs'] == state['model_overwrites'] == 0
    assert not state['final_model_selected']
    report = (ROOT / 'reports/toluene_failure_analysis.html').read_text(encoding='utf-8')
    assert report.count('<section>') == 10
    assert report.count('data:image/png;base64,') >= 6
