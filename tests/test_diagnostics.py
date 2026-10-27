# 진단 계산값과 기존 결과의 보존 여부를 확인합니다.
# 이 테스트에서는 분류기를 학습하지 않습니다.
import ast
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from scipy.stats import wasserstein_distance
from src.data import ROOT,FEATURES,read_config,load_dataset
from src.diagnose_models import OUT,rho,COMMON

# 값이 일정한 경우와 순서가 같은 경우를 확인합니다.
def test_rank_correlation_edge_cases():
    assert np.isnan(rho([1,1,1],[1,2,3]))
    assert rho([1,2,3,4,5],[10,20,30,40,50])==pytest.approx(1)
    assert rho([1,2,3,4,5],[50,40,30,20,10])==pytest.approx(-1)

# 주석 추가 전후에 실행 코드의 구조가 같은지 확인합니다.
def test_comment_changes_preserve_ast():
    audit=json.loads((ROOT/'reports'/'python_comment_audit.json').read_text(encoding='utf-8'))
    assert len(audit)>=7
    for item in audit:
        assert item['before_ast_sha256']==item['after_ast_sha256']
        code=(ROOT/item['file']).read_text(encoding='utf-8')
        current=hashlib.sha256(ast.dump(ast.parse(code),include_attributes=False).encode()).hexdigest()
        assert current==item['after_ast_sha256']
        assert code.startswith('# ')

# 기존 보고서와 모델 파일을 그대로 보존했는지 확인합니다.
def test_existing_results_and_models_unchanged():
    state=json.loads((OUT/'preservation.json').read_text(encoding='utf-8'))
    assert state['existing_artifacts_unchanged'] and state['raw_files_unchanged']
    for name,expected in state['before'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected
    for name,expected in state['raw_hashes'].items():
        assert hashlib.sha256((Path(read_config()['data_dir'])/name).read_bytes()).hexdigest()==expected

# 저장된 예측을 다시 계산해 같은 결과인지 확인합니다.
def test_all_saved_predictions_replayed():
    replay=pd.read_csv(OUT/'prediction_replay.csv')
    assert len(replay)==9 and replay.exact_match.all()
    assert replay.rows.sum()==len(pd.read_csv(ROOT/'outputs'/'model_comparison'/'predictions.csv'))

# 같은 미래 자료의 표본 수와 가스 수가 올바른지 확인합니다.
def test_common_batch_comparison_and_error_rates():
    evidence=pd.read_csv(OUT/'selection_evidence.csv')
    future=evidence[evidence.experiment.isin(['B_early','B_history'])]
    assert future.common_n.eq(10277).all()
    gas=pd.read_csv(OUT/'gas_errors.csv')
    cells=gas[(gas.partition=='test')&(gas.scope=='batch')&gas.batch.isin(COMMON)&gas.experiment.isin(['B_early','B_history'])]
    assert cells.groupby(['experiment','model','batch']).size().eq(6).all()
    assert np.allclose(cells.error_rate,1-cells.recall)
    assert cells.support.gt(0).all()
    metrics=pd.read_csv(OUT/'metrics.csv')
    for row in future.itertuples(index=False):
        sub=metrics[(metrics.experiment==row.experiment)&(metrics.model==row.model)&(metrics.partition=='test')&(metrics.scope=='batch')&metrics.batch.isin(COMMON)]
        assert row.equal_batch_mean_f1==pytest.approx(sub.macro_f1.mean())
        assert row.batch_sd_f1==pytest.approx(sub.macro_f1.std(ddof=0))

# 특징 거리 하나를 원본에서 직접 계산해 대조합니다.
def test_wasserstein_same_gas_train_reference():
    frame,_=load_dataset(read_config())
    assignments=pd.read_csv(ROOT/'outputs'/'model_comparison'/'split_assignments.csv')
    ids=assignments[(assignments.experiment=='B_history')&(assignments.partition=='train')].row_id
    train=frame[frame.row_id.isin(ids)]
    ref=train[train.gas==5].f001
    target=frame[(frame.gas==5)&(frame.batch==10)].f001
    expected=wasserstein_distance(ref,target)
    d=pd.read_csv(OUT/'wasserstein.csv')
    row=d[(d.experiment=='B_history')&(d.gas_id==5)&(d.batch==10)&(d.feature=='f001')].iloc[0]
    assert row.wasserstein_raw==pytest.approx(expected)
    assert row.wasserstein_scaled==pytest.approx(expected/train.f001.std(ddof=0))
    assert row.reference_n==len(ref) and row.target_n==len(target)

# 새 분류기 학습이 없고 보고서 구성이 완성됐는지 확인합니다.
def test_no_classifier_training_and_report_complete():
    manifest=json.loads((OUT/'run_manifest.json').read_text(encoding='utf-8'))
    assert manifest['new_classifier_fits']==0
    assert not manifest['final_model_selected']
    code=(ROOT/'src'/'diagnose_models.py').read_text(encoding='utf-8')
    tree=ast.parse(code)
    fits=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='fit']
    assert len(fits)==1 and isinstance(fits[0].func.value,ast.Call) and fits[0].func.value.func.id=='PCA'
    doc=(ROOT/'reports'/'model_diagnostic_report.html').read_text(encoding='utf-8')
    assert doc.count('<section>')==10
    assert doc.count('data:image/png;base64,')==12
