import json
from pathlib import Path
import hashlib
import numpy as np
import pandas as pd
import pytest
import joblib
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from src.data import ROOT, FEATURES, GASES, load_dataset, read_config
from src.train_models import OUT, make_splits, audit_splits, make_pipeline, evaluate

@pytest.fixture(scope='module')
def real_data():
    frame,_ = load_dataset(read_config())
    settings = json.loads((ROOT/'training_config.json').read_text(encoding='utf-8'))
    return frame,settings,make_splits(frame,settings)

def test_metric_conventions_for_missing_and_unpredicted_classes():
    metrics,rows,cm = evaluate([1,1,2],[1,6,1])
    assert metrics['accuracy'] == pytest.approx(1/3)
    assert metrics['macro_precision'] == pytest.approx(.25)
    assert metrics['macro_recall'] == pytest.approx(.25)
    assert metrics['macro_f1'] == pytest.approx(.25)
    assert metrics['macro_f1_fixed6'] == pytest.approx(.5/6)
    assert metrics['weighted_f1'] == pytest.approx(1/3)
    assert rows[5]['support'] == 0 and rows[5]['predicted_count'] == 1
    assert rows[5]['precision'] is None and rows[5]['recall'] is None
    assert rows[1]['precision'] == 0 and rows[1]['f1'] == 0
    assert cm.shape == (6,6) and cm.sum() == 3

def test_preprocessing_fit_does_not_see_future_rows():
    settings={'models':{'LogisticRegression':{'C':1.0,'solver':'lbfgs','max_iter':1000,'random_state':42}}}
    train=pd.DataFrame({'f001':[-2.,-1.,1.,2.], 'f002':[np.nan,2.,4.,6.]})
    future=pd.DataFrame({'f001':[1e9], 'f002':[np.nan]})
    pipeline=make_pipeline('LogisticRegression',settings)
    pipeline.fit(train,[1,1,2,2])
    assert pipeline.named_steps['imputer'].statistics_[1] == 4
    assert np.allclose(pipeline.named_steps['scaler'].mean_,[0,4])
    before=pipeline.named_steps['scaler'].mean_.copy()
    pipeline.predict(future)
    assert np.array_equal(before,pipeline.named_steps['scaler'].mean_)
    assert pipeline.named_steps['scaler'].n_samples_seen_ == 4

def test_real_split_sizes_disjointness_and_chronology(real_data):
    frame,settings,splits=real_data
    audit,assignments=audit_splits(frame,splits)
    assert [len(splits['A_random'][p]) for p in ('train','validation','test')] == [8346,2782,2782]
    assert [len(splits['B_early'][p]) for p in ('train','validation','test')] == [445,1244,12221]
    assert [len(splits['B_history'][p]) for p in ('train','validation','test')] == [3275,161,10474]
    saved=pd.read_csv(OUT/'split_assignments.csv')
    pd.testing.assert_frame_equal(saved,assignments)
    assert audit == json.loads((OUT/'split_audit.json').read_text(encoding='utf-8'))
    assert set(frame.iloc[splits['B_early']['validation']].gas) == set(GASES)
    assert set(frame.iloc[splits['B_history']['validation']].gas) == {1,2,3,4,5}
    # The old EDA holdout remains the same seeded 20% in the new A design.
    old=pd.read_csv(ROOT/'outputs'/'split_manifest.csv')
    assert set(frame.iloc[splits['A_random']['test']].row_id) == set(old.loc[old.random_split=='test','row_id'])

def test_split_guard_rejects_cross_partition_duplicate(real_data):
    frame,_,splits=real_data
    changed=frame.copy()
    train=splits['A_random']['train'][0]
    test=splits['A_random']['test'][0]
    changed.loc[test,FEATURES]=changed.loc[train,FEATURES].to_numpy()
    with pytest.raises(ValueError,match='duplicates cross partitions'):
        audit_splits(changed,splits)

def test_all_reported_metrics_from_saved_predictions():
    predictions=pd.read_csv(OUT/'predictions.csv')
    metrics=pd.read_csv(OUT/'metrics.csv')
    matrices=pd.read_csv(OUT/'confusion_matrices.csv')
    per_class=pd.read_csv(OUT/'per_class_metrics.csv')
    for row in metrics.itertuples(index=False):
        subset=predictions[(predictions.experiment==row.experiment)&(predictions.model==row.model)&(predictions.partition==row.partition)]
        if row.scope=='batch':
            subset=subset[subset.batch==row.batch]
        assert len(subset)==row.n
        p,r,f,s=precision_recall_fscore_support(subset.y_true,subset.y_pred,labels=list(GASES),zero_division=0)
        present=s>0
        assert row.accuracy == pytest.approx(accuracy_score(subset.y_true,subset.y_pred))
        assert row.macro_precision == pytest.approx(p[present].mean())
        assert row.macro_recall == pytest.approx(r[present].mean())
        assert row.macro_f1 == pytest.approx(f[present].mean())
        assert row.weighted_f1 == pytest.approx(np.average(f,weights=s))
        assert row.macro_f1_fixed6 == pytest.approx(f.mean())
        selected=matrices[(matrices.experiment==row.experiment)&(matrices.model==row.model)&(matrices.partition==row.partition)&(matrices.scope==row.scope)&(matrices.batch==row.batch)]
        assert np.array_equal(selected['count'].to_numpy().reshape(6,6),confusion_matrix(subset.y_true,subset.y_pred,labels=list(GASES)))
        classes=per_class[(per_class.experiment==row.experiment)&(per_class.model==row.model)&(per_class.partition==row.partition)&(per_class.scope==row.scope)&(per_class.batch==row.batch)].sort_values('gas_id')
        assert np.array_equal(classes.support,s)
        assert np.allclose(classes.loc[present,'precision'],p[present])
        assert classes.loc[~present,['precision','recall','f1']].isna().all().all()

def test_saved_pipelines_train_statistics_and_reload_predictions(real_data):
    frame,settings,splits=real_data
    predictions=pd.read_csv(OUT/'predictions.csv')
    records=json.loads((OUT/'fit_records.json').read_text(encoding='utf-8'))
    assert len(records)==9
    lookup=frame.set_index('row_id',drop=False)
    for record in records:
        path=ROOT/record['model_file']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==record['sha256']
        pipeline=joblib.load(path)
        train=frame.iloc[splits[record['experiment']]['train']]
        assert list(pipeline.feature_names_in_) == FEATURES
        assert np.allclose(pipeline.named_steps['imputer'].statistics_,train[FEATURES].median().to_numpy())
        if record['model']!='RandomForest':
            scaler=pipeline.named_steps['scaler']
            assert scaler.n_samples_seen_==len(train)
            assert np.allclose(scaler.mean_,train[FEATURES].mean().to_numpy())
        else:
            assert 'scaler' not in pipeline.named_steps
        # Full validation+test prediction replay verifies serialization and all three shared split uses.
        selected=predictions[(predictions.experiment==record['experiment'])&(predictions.model==record['model'])]
        actual=pipeline.predict(lookup.loc[selected.row_id,FEATURES])
        assert np.array_equal(actual,selected.y_pred)

def test_eda_and_sources_preserved_report_complete(real_data):
    state=json.loads((OUT/'preservation_checks.json').read_text(encoding='utf-8'))
    assert state['eda_files_unchanged'] and state['source_files_unchanged']
    for name,expected in state['before'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected
    for name,expected in json.loads((OUT/'run_manifest.json').read_text(encoding='utf-8'))['source_sha256'].items():
        assert hashlib.sha256((Path(read_config()['data_dir'])/name).read_bytes()).hexdigest()==expected
    doc=(ROOT/'reports'/'model_comparison_report.html').read_text(encoding='utf-8')
    assert doc.count('<section>')==10
    assert doc.count('data:image/png;base64,')==11
    assert '<meta charset="UTF-8">' in doc
    assert len(list((ROOT/'models').glob('*.joblib')))==9
