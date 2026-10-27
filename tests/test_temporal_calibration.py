# 중첩 교정 표본·동일 평가·Train 전처리·대응 보호 기준 검사

from datetime import datetime
import json

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import f1_score,precision_recall_fscore_support

from src.data import ROOT,FEATURES,GASES,load_dataset,read_config
from src.temporal_expansion import sha
from src.temporal_calibration import (
    OUT,MODEL_DIR,FOLDS,SEEDS,RATES,evaluation_counts,nested_counts,make_split,
    check_partition,rate_decisions,verify,row_digest,digest,
)


def read(name):
    return pd.read_csv(OUT/f'{name}.csv')


def read_json(name):
    return json.loads((OUT/name).read_text(encoding='utf-8'))


@pytest.fixture(scope='module')
def state():
    frame,_=load_dataset(read_config())
    return frame[frame.batch<=8].copy(),read_json('model_registry.json')


def test_stratified_half_rounding_and_support():
    counts=np.array([30,30,40,33,143,18])
    result=evaluation_counts(counts)
    np.testing.assert_array_equal(result,[15,15,20,17,71,9])
    assert result.sum()==147 and (result>=1).all() and (result<counts).all()


def test_nested_quota_prefix_and_capacity():
    quotas=nested_counts([15,15,20,16,72,9],[14,29,58])
    for n,q in quotas.items():
        assert q.sum()==n and (q>=1).all() and (q<=np.array([15,15,20,16,72,9])).all()
    assert (quotas[14]<=quotas[29]).all() and (quotas[29]<=quotas[58]).all()


def test_impossible_split_rejected_without_relaxation():
    with pytest.raises(ValueError):
        evaluation_counts([1,3,3,3,3,3])
    with pytest.raises(ValueError):
        nested_counts([2]*6,[5,6,7])
    with pytest.raises(ValueError):
        nested_counts([2]*6,[14])


def synthetic_inputs():
    metrics,classes=[],[]
    for fold in FOLDS:
        for seed in SEEDS:
            for rate in RATES:
                metrics.append(dict(fold=fold,seed=seed,rate=rate,macro_f1=.5 if rate==0 else .505))
                for gas in GASES:
                    classes.append(dict(fold=fold,seed=seed,rate=rate,gas_id=gas,
                        precision=.5 if rate==0 else .45,recall=.5 if rate==0 else .45,f1=.5 if rate==0 else .48))
    return pd.DataFrame(metrics),pd.DataFrame(classes)


def test_inclusive_guards_and_consistency():
    metrics,classes=synthetic_inputs()
    result=rate_decisions(metrics,classes)
    assert all(r['all_passed'] and r['conclusion']=='A' for r in result)
    classes.loc[(classes.rate==5)&(classes.fold=='C')&(classes.seed==11)&(classes.gas_id==6),'recall']=0
    result=rate_decisions(metrics,classes)
    assert not result[0]['checks']['no_new_zero_guard']


def test_plan_budget_and_frozen_before_fit():
    plan,lock=read_json('experiment_plan.json'),read_json('plan_lock.json')
    assert sha(OUT/'experiment_plan.json')==lock['plan_sha256']
    assert sha(OUT/'protocol.md')==lock['protocol_sha256']
    assert plan['seeds']==SEEDS and plan['rates']==RATES and not plan['independent_test']
    assert plan['budget']['max_new_adaptive_SVM_fits']==27
    assert datetime.fromisoformat(plan['frozen_at'])<=datetime.fromisoformat(read_json('started.json')['started_at'])


def test_calibration_evaluation_disjoint_nested_and_exact_counts(state):
    frame,_=state
    for fold in FOLDS:
        for seed in SEEDS:
            split=make_split(frame,fold,seed)
            check_partition(frame,split,fold)
            n=int((frame.batch==FOLDS[fold][1]).sum())
            assert len(split['evaluation'])==n//2
            for rate in RATES[1:]:
                assert len(split['calibration'][rate])==n*rate//100
                assert set(frame.loc[split['calibration'][rate],'gas'])==set(GASES)
            assert set(frame.loc[split['evaluation'],'gas'])==set(GASES)


def test_original_row_ids_and_split_reproducibility(state):
    frame,_=state
    planned=read('split_assignments')
    indexed=frame.set_index('row_id')
    for row in planned.itertuples():
        raw=indexed.loc[row.row_id]
        assert raw.batch==row.batch and raw.source_line==row.source_line and raw.gas==row.gas_id
    for fold in FOLDS:
        for seed in SEEDS:
            split=make_split(frame,fold,seed)
            for part,key in [('past','past'),('evaluation','evaluation'),('pool','pool')]:
                ids=planned[(planned.fold==fold)&(planned.seed==seed)&(planned.partition==part)].row_id.tolist()
                assert ids==frame.loc[split[key],'row_id'].tolist()
            for rate in RATES[1:]:
                ids=planned[(planned.fold==fold)&(planned.seed==seed)&(planned.partition==f'cal{rate:02d}')].row_id.tolist()
                assert ids==frame.loc[split['calibration'][rate],'row_id'].tolist()


def test_same_evaluation_for_every_rate_and_exact_past_train(state):
    frame,_=state
    audit=read('train_only_audit')
    predictions=read('predictions')
    for fold,(end,batch) in FOLDS.items():
        for seed in SEEDS:
            sub=audit[(audit.fold==fold)&(audit.seed==seed)]
            assert sub.evaluation_row_sha256.nunique()==1
            split=make_split(frame,fold,seed)
            assert set(split['past'])==set(frame.index[frame.batch<=end])
            for rate in RATES:
                p=predictions[(predictions.fold==fold)&(predictions.seed==seed)&(predictions.rate==rate)&(predictions.scope=='evaluation')]
                assert p.row_id.tolist()==frame.loc[split['evaluation'],'row_id'].tolist()


def test_train_only_preprocessing_and_classifier_parameters(state):
    frame,registry=state
    for entry in registry:
        split=make_split(frame,entry['fold'],entry['seed'])
        ids=np.sort(np.concatenate([split['past'],split['calibration'][entry['rate']]]))
        train=frame.loc[ids]
        model=joblib.load(ROOT/entry['path'])
        assert list(model.named_steps)==['imputer','scaler','classifier']
        np.testing.assert_array_equal(model['imputer'].feature_names_in_,FEATURES)
        np.testing.assert_allclose(model['imputer'].statistics_,train[FEATURES].median())
        x=model['imputer'].transform(train[FEATURES])
        assert x.shape==(len(train),128) and model['scaler'].n_samples_seen_==len(train)
        np.testing.assert_allclose(model['scaler'].mean_,x.mean(axis=0),atol=1e-10)
        np.testing.assert_allclose(model['scaler'].var_,x.var(axis=0),rtol=1e-9)
        classifier=model['classifier']
        assert classifier.C==1. and classifier.gamma=='scale' and classifier.kernel=='rbf'
        assert classifier.class_weight=='balanced' and classifier.probability is False
        assert classifier.random_state==42
        np.testing.assert_array_equal(classifier.classes_,list(GASES))


def test_balanced_weights_combined_train_only(state):
    frame,registry=state
    weights=read('class_weights')
    for entry in registry:
        split=make_split(frame,entry['fold'],entry['seed'])
        train=frame.loc[np.sort(np.concatenate([split['past'],split['calibration'][entry['rate']]]))]
        counts=train.gas.value_counts().sort_index()
        actual=weights[(weights.fold==entry['fold'])&(weights.seed==entry['seed'])&(weights.rate==entry['rate'])].sort_values('gas_id')
        np.testing.assert_array_equal(actual.train_support,counts)
        np.testing.assert_allclose(actual.class_weight,len(train)/(6*counts))
        np.testing.assert_allclose(actual.expected_weight,actual.class_weight)


def test_saved_models_and_reloaded_predictions(state):
    frame,registry=state
    predictions=read('predictions')
    assert len(registry)==36 and sum(e['new_fit'] for e in registry)==27
    assert len(list(MODEL_DIR.glob('*.joblib')))==27
    for entry in registry:
        assert sha(ROOT/entry['path'])==entry['sha256']
        p=predictions[(predictions.fold==entry['fold'])&(predictions.seed==entry['seed'])&
                      (predictions.rate==entry['rate'])&(predictions.scope=='evaluation')]
        model=joblib.load(ROOT/entry['path'])
        np.testing.assert_array_equal(model.predict(frame.set_index('row_id').loc[p.row_id,FEATURES]),p.y_pred)


def test_metric_calculations_and_focus_error_directions():
    predictions=read('predictions')
    classes=read('class_metrics')
    metrics=read('metrics')
    for key,p in predictions.groupby(['fold','seed','rate','scope']):
        fold,seed,rate,scope=key
        actual=classes[(classes.fold==fold)&(classes.seed==seed)&(classes.rate==rate)&(classes.scope==scope)].sort_values('gas_id')
        pr,re,f,support=precision_recall_fscore_support(p.y_true,p.y_pred,labels=list(GASES),zero_division=0)
        mask=support>0
        np.testing.assert_allclose(actual.loc[mask,['precision','recall','f1']],np.column_stack([pr,re,f])[mask])
        assert actual.loc[~mask,'recall'].isna().all()
        row=metrics[(metrics.fold==fold)&(metrics.seed==seed)&(metrics.rate==rate)&(metrics.scope==scope)].iloc[0]
        assert row.macro_f1==pytest.approx(f1_score(p.y_true,p.y_pred,labels=np.unique(p.y_true),average='macro',zero_division=0))
        assert row.toluene_to_acetaldehyde==((p.y_true==6)&(p.y_pred==4)).sum()


def test_protection_decisions_and_aggregation_reproducible():
    metrics=read('metrics')
    classes=read('class_metrics')
    computed=rate_decisions(metrics[metrics.scope=='evaluation'],classes[classes.scope=='evaluation'])
    saved=read_json('rate_decisions.json')['rates']
    for a,b in zip(computed,saved):
        assert a['rate']==b['rate'] and a['checks']==b['checks'] and a['conclusion']==b['conclusion']
        assert a['mean_macro_delta']==pytest.approx(b['mean_macro_delta'])
    seed_summary=read('seed_summary')
    for rate in RATES:
        expected=metrics[(metrics.rate==rate)&(metrics.scope=='evaluation')].groupby('seed').macro_f1.mean()
        np.testing.assert_allclose(seed_summary[seed_summary.rate==rate].sort_values('seed').macro_f1,expected)


def test_regression_set_is_existing_heldout_and_no_train_score_proxy(state):
    frame,_=state
    p=read('predictions')
    regression=p[p.scope=='regression']
    assert set(regression.fold)=={'A'} and set(regression.batch)=={4,5}
    assert set(regression.y_true)=={1,2,3,4,5}
    assert regression.groupby(['seed','rate']).size().eq(358).all()
    assert set(regression.row_id).isdisjoint(frame.loc[frame.batch<=3,'row_id'])
    assert set(regression.row_id).isdisjoint(p[p.scope=='evaluation'].query("fold=='A'").row_id)


def test_no_future_evaluation_and_historical_files_preserved():
    assert verify()['all_preserved']
    p=read('predictions')
    assert set(p[p.scope=='evaluation'].batch)=={6,7,8}
    assert not p.batch.isin([9,10]).any()
    assert read_json('rate_decisions.json')['future_batches_evaluated']==[]


def test_report_graphs_and_limitations():
    graph=read('graph_manifest')
    assert len(graph)==9 and graph.fixed_evaluation.all()
    for row in graph.itertuples():
        assert sha(ROOT/row.path)==row.sha256
    text=(ROOT/'reports/temporal_calibration_report.html').read_text(encoding='utf-8')
    assert text.count('data:image/png;base64,')==9
    assert '독립 Test가 아님' in text and '물리적 센서 교정' in text
