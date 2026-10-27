# 정답이 확인된 동일 시기 소량 자료를 추가한 SVM 적응 비교
# 고정 평가 집합·중첩 교정 표본·과거 회귀 검사 및 기존 자료 보존

import argparse
import json
import logging
import importlib.metadata
import platform
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from .data import ROOT, FEATURES, GASES, load_dataset, read_config
from .temporal_expansion import now, sha
from .temporal_svm_ensemble import audit_model
from .nonlinear_feature_transformation import build_pipeline, score_predictions, row_digest, digest

OUT = ROOT/'outputs/temporal_calibration'
MODEL_DIR = ROOT/'models/temporal_calibration'
REPORTS = [f'temporal_calibration_{s}' for s in ['report.html','summary.md','limitations.md']]
FOLDS = {'A':(3,6),'B':(6,7),'C':(7,8)}
SEEDS = [11,23,42]
RATES = [0,5,10,20]
CAUTION = ('정답이 확인된 새 시기 자료를 이용한 지도학습 모델 적응이며 물리적 센서 교정이나 '
           '드리프트 감지 실험이 아님. 반복 사용한 개발 Batch 내부의 평가이며 독립 Test가 아님. '
           'Batch 9~10 신규 평가 없음. 공식 Model A 유지.')


def write(name, value):
    def convert(x):
        if isinstance(x,np.generic):
            return x.item()
        if isinstance(x,np.ndarray):
            return x.tolist()
        raise TypeError(type(x).__name__)
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False,default=convert),encoding='utf-8')


def save(name, rows):
    table = rows if isinstance(rows,pd.DataFrame) else pd.DataFrame(rows)
    table.to_csv(OUT/f'{name}.csv',index=False,encoding='utf-8')
    return table


# 50% 평가 수를 최대 잔여 방식으로 가스별 배분
def evaluation_counts(counts):
    counts = np.asarray(counts,dtype=int)
    if len(counts) != 6 or (counts < 2).any():
        raise ValueError('Every gas needs at least2 rows before splitting')
    target = int(counts.sum()//2)
    ideal = counts*target/counts.sum()
    result = np.clip(np.floor(ideal).astype(int),1,counts-1)
    while result.sum() < target:
        eligible = np.flatnonzero(result < counts-1)
        j = eligible[np.argmax(ideal[eligible]-result[eligible])]
        result[j] += 1
    while result.sum() > target:
        eligible = np.flatnonzero(result > 1)
        j = eligible[np.argmax(result[eligible]-ideal[eligible])]
        result[j] -= 1
    return result


# 최소1개씩 확보 후 비례 부족분이 큰 가스부터 순차 추가
def nested_counts(capacity, targets):
    capacity = np.asarray(capacity,dtype=int)
    if (capacity < 1).any() or min(targets) < 6 or max(targets) > capacity.sum():
        raise ValueError('Insufficient calibration capacity; no silent replacement')
    allocated = np.ones(6,dtype=int)
    result = {}
    for target in sorted(targets):
        while allocated.sum() < target:
            eligible = np.flatnonzero(allocated < capacity)
            ideal = capacity/capacity.sum()*(allocated.sum()+1)
            j = eligible[np.argmax(ideal[eligible]-allocated[eligible])]
            allocated[j] += 1
        result[target] = allocated.copy()
    return result


# 원본 행 ID를 유지한 층화 평가·중첩 교정 집합 구성
def make_split(frame, fold, seed):
    end,batch = FOLDS[fold]
    target = frame[frame.batch == batch]
    counts = target.gas.value_counts().reindex(GASES,fill_value=0).to_numpy()
    eval_n = evaluation_counts(counts)
    pool_n = counts-eval_n
    totals = {r:len(target)*r//100 for r in RATES if r}
    allocation = nested_counts(pool_n,list(totals.values()))
    evaluation, pools, calibration = [],[],{r:[] for r in RATES}
    for j,g in enumerate(GASES):
        ids = target.index[target.gas == g].to_numpy()
        rng = np.random.default_rng(np.random.SeedSequence([seed,batch,g]))
        shuffled = rng.permutation(ids)
        evaluation.extend(shuffled[:eval_n[j]])
        pool = shuffled[eval_n[j]:]
        pools.extend(pool)
        for r in RATES[1:]:
            calibration[r].extend(pool[:allocation[totals[r]][j]])
    return dict(past=frame.index[frame.batch <= end].to_numpy(),
                evaluation=np.array(sorted(evaluation),dtype=int),
                pool=np.array(sorted(pools),dtype=int),
                calibration={r:np.array(sorted(ids),dtype=int) for r,ids in calibration.items()})


# 기존 코드·모델·산출물의 바이트 지문 기록
def snapshot():
    result = {}
    for folder in ['src','tests','outputs','reports','models']:
        for p in (ROOT/folder).rglob('*'):
            if (not p.is_file() or '__pycache__' in p.parts or OUT in p.parents or
                    MODEL_DIR in p.parents or (p.parent == ROOT/'reports' and p.name in REPORTS)):
                continue
            result[str(p.relative_to(ROOT))] = sha(p)
    for name in ['README.md','config.json','training_config.json','.gitignore','requirements.txt','requirements-lock.txt']:
        result[name] = sha(ROOT/name)
    return result


# 학습·평가·교정·과거 회귀 자료의 정확 중복 검사
def check_partition(frame, split, fold):
    h = pd.util.hash_pandas_object(frame[FEATURES],index=False)
    evaluation = split['evaluation']
    for rate,ids in split['calibration'].items():
        train = np.sort(np.concatenate([split['past'],ids]))
        assert set(train).isdisjoint(evaluation)
        assert set(h.loc[train]).isdisjoint(h.loc[evaluation])
        assert len(train) == len(set(train))
        assert set(frame.loc[train,'gas']) == set(frame.loc[evaluation,'gas']) == set(GASES)
    assert set(split['pool']).isdisjoint(evaluation)
    assert set(split['pool']) == set(frame.index[frame.batch == FOLDS[fold][1]])-set(evaluation)
    assert set(split['calibration'][5]) <= set(split['calibration'][10]) <= set(split['calibration'][20])
    if fold == 'A':
        regression = frame.index[frame.batch.isin([4,5])]
        combined = np.concatenate([split['past'],split['pool'],evaluation])
        assert set(regression).isdisjoint(combined)
        assert set(h.loc[regression]).isdisjoint(h.loc[combined])


# 표본을 뽑기 전에 추출 규칙·예산·판정 기준 먼저 고정
def freeze():
    if OUT.exists() or MODEL_DIR.exists() or any((ROOT/'reports'/n).exists() for n in REPORTS):
        raise FileExistsError('Stage17 outputs already exist')
    frame, raw = load_dataset(read_config())
    frame = frame[frame.batch <= 8].copy()
    source = pd.read_csv(ROOT/'outputs/nonlinear_feature_transformation/model_registry.csv')
    source_records = []
    for fold,(end,_) in FOLDS.items():
        r = source[(source.fold == fold)&(source.method == 'baseline')].iloc[0]
        assert sha(ROOT/r.path) == r.sha256
        audit_model(joblib.load(ROOT/r.path),frame[frame.batch <= end],end)
        source_records.append(dict(fold=fold,path=r.path,sha256=r.sha256))
    old_splits = pd.read_csv(ROOT/'outputs/model_comparison/split_assignments.csv')
    regression_ids = frame.loc[frame.batch.isin([4,5]),'row_id']
    prior = old_splits[(old_splits.experiment == 'B_history')&old_splits.batch.isin([4,5])]
    assert set(prior.row_id) == set(regression_ids) and set(prior.partition) == {'validation','test'}
    before = snapshot()
    OUT.mkdir()
    plan = dict(stage=17,frozen_at=now(),folds=FOLDS,seeds=SEEDS,rates=RATES,
        split='Per Fold/seed whole target Batch: Evaluation=floor(N/2); remaining rows candidate pool. '
              'Evaluation per-gas Hamilton allocation with >=1 and <=n_g-1; ties lower gas id. '
              'Per-gas SeedSequence(seed,target_batch,gas) permutation, first quota Evaluation, rest pool.',
        calibration='Counts floor(N*rate/100), denominator full target Batch. Start1 per gas; '
                    'sequential proportional-deficit fill using pool class counts, capacity-capped, '
                    'tie lower gas id. Same per-gas pool permutation prefix for5/10/20 so nested.',
        impossible='If any class<2 or calibration target<6 or capacity insufficient, stop before fits; '
                   'no class synthesis, silent relaxation, new seed or ratio.',
        labels='True labels used for retrospective stratified split. Only selected calibration labels '
               'enter refit. Collecting class-balanced calibration prospectively may require controlled '
               'gas exposures/additional labels; percentages are training-label counts, not proven deployment cost.',
        temporal='Past Train precedes target Batch. Calibration/Evaluation are random same-Batch subsets; '
                 'no exact within-Batch timestamps, so not proof of chronological online adaptation.',
        svm=dict(kernel='rbf',C=1.,gamma='scale',class_weight='balanced',probability=False,random_state=42),
        pipeline='Train-only median imputer -> StandardScaler -> SVC. Refit from scratch on past+calibration. '
                 'balanced n/(6*n_g) from combined Train labels only; no sample_weight.',
        metric='Accuracy, MacroF1 present true classes, WeightedF1, per-gas P/R/F1/support/predicted_n, '
               '6x6 confusion, zero recall, directional focus errors. Unsupported truth NA not zero.',
        aggregation='Primary: for each seed equal3-Fold MacroF1 mean, then equal3-seed mean. '
                    'Per-gas supported-Fold mean within seed then equal-seed mean; other-four F1 '
                    'equal gas means1,2,3,5. Seed SD ddof1 descriptive only; overlapping repeated data.',
        protection=dict(macro_gain_min=.005,per_gas_mean_recall_loss_max=.05,
                        focus_mean_precision_recall_f1_loss_max=.05,
                        other_four_mean_f1_loss_max=.02,no_new_zero=True,inclusive=True,tolerance=1e-12),
        consistency='A requires all3 Fold mean paired MacroF1 deltas>1e-12, >=2/3 seed mean '
                    'deltas>1e-12 and>=6/9 paired Fold-seed deltas>1e-12, plus all guards.',
        conclusion='Per rate independently: A if guards+consistency; B otherwise if any paired '
                   'Fold-seed MacroF1 gain>1e-12 or any gas aggregate F1 gain>1e-12; C otherwise. '
                   'Do not pick a winning ratio or replace official Model A.',
        regression='Fold A only: existing B_history Validation Batch4 and Test Batch5,358 rows, '
                   'five true gas classes with no Toluene. Re-register as past held-out retention '
                   'diagnostic, not independent future test; disjoint from Train1-3 and target6. '
                   'B/C no past rows outside full past Train; retention unavailable. No Train-score proxy.',
        budget=dict(max_new_adaptive_SVM_fits=27,baseline_unique_models=3,
                    baseline_evaluation_conditions=9,adaptive_evaluation_conditions=27,
                    regression_logical_conditions=12,baseline_fallback_fits=0),
        reuse='Verify source sha, Train medians/scaler/support vectors/classes/params before fitting. '
              'If unavailable stop and report required replacements, do not train extra baseline.',
        stop='No tuning, extra seeds/ratios, feature selection, weighting experiment, new algorithm, '
             'ensemble, drift detector or Batch9/10 scientific evaluation. Fit failure recorded; '
             'no altered retry. Leakage or preservation failure aborts.',
        source_models=source_records,
        official_model=dict(path='models/temporal_expansion/B_SVM_balanced.joblib',train_end=6,
                            sha256=sha(ROOT/'models/temporal_expansion/B_SVM_balanced.joblib')),
        environment=dict(python=platform.python_version(),packages={k:importlib.metadata.version(k)
                         for k in ['scikit-learn','numpy','pandas','scipy','joblib']}),
        independent_test=False,future_batches_evaluated=[],warning=CAUTION)
    write('experiment_plan.json',plan)
    (OUT/'protocol.md').write_text('# 17단계 사전 고정 계획\n\n'+CAUTION+'\n\n```json\n'+
        json.dumps(plan,ensure_ascii=False,indent=2)+'\n```',encoding='utf-8')
    write('plan_lock.json',dict(plan_sha256=sha(OUT/'experiment_plan.json'),protocol_sha256=sha(OUT/'protocol.md')))
    write('preservation_before.json',dict(files=before,raw={r.file:r.sha256 for r in raw.itertuples()}))
    # 계획을 쓴 다음에만 실제 신규 분할 생성
    rows, supports, overlaps = [],[],[]
    for fold in FOLDS:
        for seed in SEEDS:
            split = make_split(frame,fold,seed)
            check_partition(frame,split,fold)
            parts = dict(past=split['past'],evaluation=split['evaluation'],pool=split['pool'],
                         **{f'cal{r:02d}':ids for r,ids in split['calibration'].items() if r})
            if fold == 'A':
                parts['regression'] = frame.index[frame.batch.isin([4,5])].to_numpy()
            for part,ids in parts.items():
                sub = frame.loc[ids]
                rows.extend(dict(fold=fold,seed=seed,partition=part,row_id=r.row_id,
                                 batch=int(r.batch),source_line=int(r.source_line),gas_id=int(r.gas))
                            for r in sub.itertuples())
                supports.extend(dict(fold=fold,seed=seed,partition=part,gas_id=g,n=int((sub.gas == g).sum())) for g in GASES)
            for rate in RATES:
                overlaps.append(dict(fold=fold,seed=seed,rate=rate,train_n=len(split['past'])+len(split['calibration'][rate]),
                                     calibration_n=len(split['calibration'][rate]),evaluation_n=len(split['evaluation']),
                                     whole_batch_n=int((frame.batch == FOLDS[fold][1]).sum()),
                                     train_evaluation_overlap=0,exact_feature_overlap=0,nested=True))
    save('split_assignments',rows)
    save('split_support',supports)
    save('overlap_checks',overlaps)
    write('split_lock.json',dict(assignments_sha256=sha(OUT/'split_assignments.csv'),support_sha256=sha(OUT/'split_support.csv')))
    print('Stage17 protocol and nested splits frozen; no classifier fits',flush=True)


# 각 비율을 같은 평가 행의 0%와 대응 비교
def rate_decisions(metrics,classes):
    base = metrics[metrics.rate == 0].set_index(['fold','seed']).macro_f1
    base_classes = classes[classes.rate == 0].set_index(['fold','seed','gas_id'])
    decisions = []
    for rate in RATES[1:]:
        sub = metrics[metrics.rate == rate].set_index(['fold','seed'])
        delta = sub.macro_f1-base
        current = classes[classes.rate == rate].set_index(['fold','seed','gas_id'])
        paired = current[['precision','recall','f1']].join(base_classes[['precision','recall','f1']],rsuffix='_base')
        # 지원되는 Fold를 먼저 평균하고 시드를 같은 가중으로 집계
        def aggregate_delta(metric):
            difference = paired[metric]-paired[metric+'_base']
            return difference.groupby(['seed','gas_id']).mean().groupby('gas_id').mean()
        recall_delta,f1_delta = aggregate_delta('recall'),aggregate_delta('f1')
        focus = paired[paired.index.get_level_values('gas_id').isin([4,6])]
        focus_guard = True
        for name in ['precision','recall','f1']:
            d = (focus[name]-focus[name+'_base']).groupby(['seed','gas_id']).mean().groupby('gas_id').mean()
            focus_guard = focus_guard and bool((d >= -.05-1e-12).all())
        mean_gain = float(delta.groupby('seed').mean().mean())
        other_delta = float(f1_delta.loc[[1,2,3,5]].mean())
        new_zero = int((paired.recall.eq(0)&(paired.recall_base > 0)).sum())
        checks = dict(complete=len(sub)==9 and len(paired)==54,
                      macro_guard=mean_gain >= .005-1e-12,
                      recall_guard=bool((recall_delta >= -.05-1e-12).all()),focus_guard=focus_guard,
                      other_four_guard=other_delta >= -.02-1e-12,no_new_zero_guard=new_zero==0,
                      fold_consistency=bool((delta.groupby('fold').mean() > 1e-12).all()),
                      seed_consistency=int((delta.groupby('seed').mean() > 1e-12).sum())>=2,
                      cell_consistency=int((delta > 1e-12).sum())>=6)
        positive = bool((delta > 1e-12).any()) or bool((f1_delta > 1e-12).any())
        verdict = 'A' if all(checks.values()) else ('B' if positive else 'C')
        decisions.append(dict(rate=rate,mean_macro_delta=mean_gain,other_four_f1_delta=other_delta,
                              new_zero_pairs=new_zero,positive_cells=int((delta>1e-12).sum()),
                              min_cell_macro_delta=float(delta.min()),checks=checks,
                              conclusion=verdict,all_passed=all(checks.values())))
    return decisions


def verify():
    before = json.loads((OUT/'preservation_before.json').read_text(encoding='utf-8'))
    checks = [dict(kind='existing',path=n,expected=s,actual=sha(ROOT/n)) for n,s in before['files'].items()]
    raw_dir = Path(read_config()['data_dir'])
    checks.extend(dict(kind='raw',path=n,expected=s,actual=sha(raw_dir/n)) for n,s in before['raw'].items())
    table = save('preservation_audit',checks)
    assert table.expected.eq(table.actual).all()
    lock = json.loads((OUT/'plan_lock.json').read_text(encoding='utf-8'))
    assert sha(OUT/'experiment_plan.json') == lock['plan_sha256']
    assert sha(OUT/'protocol.md') == lock['protocol_sha256']
    split_lock = json.loads((OUT/'split_lock.json').read_text(encoding='utf-8'))
    assert sha(OUT/'split_assignments.csv') == split_lock['assignments_sha256']
    assert sha(OUT/'split_support.csv') == split_lock['support_sha256']
    return dict(all_preserved=True,plan_unchanged=True,raw_files=len(before['raw']),
                existing_models=sum(n.endswith('.joblib') for n in before['files']),existing_files=len(before['files']))


# 과거+교정 자료만 학습하고 고정 평가·회귀 집합 예측
def run():
    if (OUT/'started.json').exists():
        raise FileExistsError('Already started; no duplicate fit')
    verify()
    write('started.json',dict(started_at=now()))
    logging.basicConfig(filename=OUT/'execution_log.txt',encoding='utf-8',level=logging.INFO)
    plan = json.loads((OUT/'experiment_plan.json').read_text(encoding='utf-8'))
    frame,_ = load_dataset(read_config())
    frame = frame[frame.batch <= 8].copy()
    models = {}
    for source in plan['source_models']:
        assert sha(ROOT/source['path']) == source['sha256']
        model = joblib.load(ROOT/source['path'])
        audit_model(model,frame[frame.batch <= FOLDS[source['fold']][0]],FOLDS[source['fold']][0])
        models[source['fold']] = model
    MODEL_DIR.mkdir()
    records,metrics,classes,predictions,matrices,audits,weights = [],[],[],[],[],[],[]
    old_predictions = pd.read_csv(ROOT/'outputs/nonlinear_feature_transformation/predictions.csv')
    with threadpool_limits(limits=1):
        for fold,(end,batch) in FOLDS.items():
            for seed in SEEDS:
                split = make_split(frame,fold,seed)
                check_partition(frame,split,fold)
                evaluation = frame.loc[split['evaluation']]
                for rate in RATES:
                    ids = np.sort(np.concatenate([split['past'],split['calibration'][rate]]))
                    train = frame.loc[ids]
                    if rate == 0:
                        model = models[fold]
                        path = ROOT/next(s['path'] for s in plan['source_models'] if s['fold']==fold)
                        fit_seconds = 0.
                    else:
                        model = build_pipeline('baseline')
                        write(f'fit_started_{fold}_{seed}_{rate:02d}.json',dict(at=now(),train_n=len(train),
                              train_rows_sha256=row_digest(train.row_id),train_input_sha256=digest(train[FEATURES])))
                        tick = time.perf_counter()
                        model.fit(train[FEATURES],train.gas)
                        fit_seconds = time.perf_counter()-tick
                        path = MODEL_DIR/f'{fold}_seed{seed}_cal{rate:02d}.joblib'
                        joblib.dump(model,path)
                    # 적응 모델은 같은 target Batch의 선택 Calibration만 추가한 과거 학습
                    audit_model(model,train,batch if rate else end)
                    transformed = model['scaler'].transform(model['imputer'].transform(train[FEATURES]))
                    audits.append(dict(fold=fold,seed=seed,rate=rate,train_n=len(train),
                        calibration_n=len(split['calibration'][rate]),train_row_sha256=row_digest(train.row_id),
                        train_input_sha256=digest(train[FEATURES]),evaluation_row_sha256=row_digest(evaluation.row_id),
                        feature_order_sha256=row_digest(FEATURES),scaler_n=int(model['scaler'].n_samples_seen_),
                        actual_gamma=float(model['classifier']._gamma),transformed_variance=float(np.var(transformed)),
                        train_only=True,evaluation_in_fit=False))
                    for g in GASES:
                        count = int((train.gas == g).sum())
                        weights.append(dict(fold=fold,seed=seed,rate=rate,gas_id=g,train_support=count,
                                            class_weight=float(model['classifier'].class_weight_[g-1]),
                                            expected_weight=len(train)/(6*count)))
                    records.append(dict(fold=fold,seed=seed,rate=rate,path=str(path.relative_to(ROOT)),
                                        sha256=sha(path),new_fit=rate>0,fit_seconds=fit_seconds,
                                        train_n=len(train),calibration_n=len(split['calibration'][rate]),
                                        classifier_params=model['classifier'].get_params()))
                    scopes = [('evaluation',evaluation)]
                    if fold == 'A':
                        scopes.append(('regression',frame[frame.batch.isin([4,5])]))
                    for scope,sub in scopes:
                        tick = time.perf_counter()
                        predicted = model.predict(sub[FEATURES])
                        predict_seconds = time.perf_counter()-tick
                        np.testing.assert_array_equal(joblib.load(path).predict(sub[FEATURES]),predicted)
                        if rate==0 and scope=='evaluation':
                            old = old_predictions[(old_predictions.fold==fold)&(old_predictions.method=='baseline')].set_index('row_id')
                            np.testing.assert_array_equal(predicted,old.loc[sub.row_id,'y_pred'])
                        score,gas,cm = score_predictions(sub.gas,predicted)
                        meta = dict(fold=fold,seed=seed,rate=rate,scope=scope,target_batch=batch,
                                    calibration_n=len(split['calibration'][rate]),train_n=len(train))
                        metrics.append(dict(**meta,**score,fit_seconds=fit_seconds,predict_seconds=predict_seconds))
                        classes.extend(gas.assign(**meta).to_dict('records'))
                        predictions.extend(dict(**meta,row_id=r,batch=int(b),y_true=int(y),y_pred=int(p))
                            for r,b,y,p in zip(sub.row_id,sub.batch,sub.gas,predicted))
                        matrices.extend(dict(**meta,true_gas=g,predicted_gas=h,n=int(cm[g-1,h-1])) for g in GASES for h in GASES)
                    logging.info('%s seed%s rate%s cal%s fit%.3fs',fold,seed,rate,len(split['calibration'][rate]),fit_seconds)
                    print(f'{fold} seed{seed} calibration{rate}% n={len(split["calibration"][rate])}',flush=True)
                    write('model_registry.json',records)
    metric_table = save('metrics',metrics)
    class_table = save('class_metrics',classes)
    save('predictions',predictions)
    save('confusion',matrices)
    save('train_only_audit',audits)
    save('class_weights',weights)
    matrix_table = pd.DataFrame(matrices)
    save('error_directions',matrix_table[matrix_table.true_gas != matrix_table.predicted_gas])
    decisions = rate_decisions(metric_table[metric_table.scope=='evaluation'],class_table[class_table.scope=='evaluation'])
    write('rate_decisions.json',dict(rates=decisions,official_model='Model A unchanged',
          new_adaptive_fits=27,reused_unique_models=3,baseline_evaluation_conditions=9,
          adaptive_evaluation_conditions=27,regression_conditions=12,future_batches_evaluated=[]))
    write('actual_settings.json',dict(pipeline='Median Imputer -> StandardScaler -> SVC',
          classifier=models['A']['classifier'].get_params(),rates=RATES,seeds=SEEDS,
          label_budget='Selected training labels only; retrospective label-aware split',physical_sensor_calibration=False))
    from .temporal_calibration_report import render
    render()
    write('final_verification.json',{**verify(),'completed_at':now()})
    print(json.dumps(decisions,ensure_ascii=False,default=lambda x:x.item()),flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action',choices=['freeze','run','report'])
    action = parser.parse_args().action
    if action=='freeze':
        freeze()
    elif action=='run':
        run()
    else:
        from .temporal_calibration_report import render
        render()
        write('final_verification.json',{**verify(),'checked_at':now()})


if __name__=='__main__':
    main()
