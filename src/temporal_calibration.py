# 정답이 확인된 동일 시기 소량 자료를 추가한 SVM 적응 비교
# 고정 평가 집합·중첩 교정 표본·과거 회귀 검사 및 기존 자료 보존

import json

import numpy as np
import pandas as pd

from .data import ROOT, FEATURES, GASES

OUT = ROOT/'outputs/temporal_calibration'
MODEL_DIR = ROOT/'models/temporal_calibration'
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




# 과거+교정 자료만 학습하고 고정 평가·회귀 집합 예측




