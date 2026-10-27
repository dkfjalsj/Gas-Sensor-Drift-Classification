# 시간순 반복 검증으로 특징 선택·단순 결합 모델 비교
# 과거 Fold로 후보 고정 후 Batch 9–10 탐색적 평가 수행

import importlib.metadata
import json
import logging
import shutil
import sys
import time
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from threadpoolctl import threadpool_limits

from .data import ROOT, FEATURES, GASES, load_dataset, read_config
from .improve_models import make_pipeline
from .temporal_expansion import measured_scores, sha, now, write_json

OUT = ROOT / 'outputs/temporal_robustness'
MODELS = ROOT / 'models/temporal_robustness'
FOLDS = {'A': (3, 6), 'B': (6, 7), 'C': (7, 8)}
FAMILIES = {'LR': 'LogisticRegression', 'RF': 'RandomForest', 'SVM': 'SVM_RBF'}
METHODS = ['all', 'variance', 'correlation', 'stability64', 'kbest32', 'kbest64']

# 모듈 실행으로 저장한 사용자 정의 클래스의 재로딩 경로 고정
if __name__ == '__main__':
    sys.modules['src.temporal_robustness'] = sys.modules[__name__]


# Train 통계만으로 입력 특징 선택
class TrainFeatureSelector(BaseEstimator, TransformerMixin):
    __module__ = 'src.temporal_robustness'

    def __init__(self, method='all'):
        self.method = method

    def fit(self, X, y, batches=None, row_ids=None):
        values = np.asarray(X, dtype=float)
        self.n_samples_ = len(values)
        self.n_features_in_ = values.shape[1]
        self.feature_names_in_ = np.asarray(FEATURES, dtype=object)
        self.train_row_ids_sha256_ = sha_rows(row_ids)
        self.train_batches_ = sorted(map(int, np.unique(batches)))
        self.training_mean_ = values.mean(axis=0)
        self.training_std_ = values.std(axis=0, ddof=0)
        self.scores_ = np.zeros(values.shape[1])
        if self.method == 'all':
            selected = np.arange(values.shape[1])
        elif self.method == 'variance':
            span = np.ptp(values, axis=0)
            safe = np.where(span == 0, 1, span)
            self.scores_ = np.var((values - values.min(axis=0)) / safe, axis=0)
            selected = np.argsort(-self.scores_, kind='stable')[:115]
        elif self.method == 'correlation':
            correlation = np.nan_to_num(np.corrcoef(values, rowvar=False), nan=0)
            selected = []
            for j in range(values.shape[1]):
                if not selected or np.max(np.abs(correlation[j, selected])) <= .98:
                    selected.append(j)
            self.scores_ = np.max(np.abs(correlation - np.eye(values.shape[1])), axis=0)
        elif self.method == 'stability64':
            # 같은 가스의 Train 내부 Batch 평균 이동 비교
            labels, batch_values = np.asarray(y), np.asarray(batches)
            distances = []
            for gas in GASES:
                mask = labels == gas
                gas_batches = np.unique(batch_values[mask])
                if len(gas_batches) < 2:
                    continue
                reference = values[mask].mean(axis=0)
                for batch in gas_batches:
                    group_mean = values[mask & (batch_values == batch)].mean(axis=0)
                    distances.append(np.abs(group_mean - reference) /
                                     np.where(self.training_std_ == 0, 1, self.training_std_))
            if not distances:
                raise ValueError('No within-Train repeated gas/batch groups')
            self.scores_ = np.mean(distances, axis=0)
            selected = np.argsort(self.scores_, kind='stable')[:64]
        elif self.method in ['kbest32', 'kbest64']:
            self.kbest_ = SelectKBest(f_classif, k=int(self.method[5:])).fit(values, y)
            self.scores_ = self.kbest_.scores_
            selected = self.kbest_.get_support(indices=True)
        else:
            raise ValueError('Unknown feature selection method')
        self.selected_indices_ = np.sort(np.asarray(selected, dtype=int))
        self.selected_features_ = self.feature_names_in_[self.selected_indices_].tolist()
        return self

    def transform(self, X):
        values = np.asarray(X, dtype=float)
        return pd.DataFrame(values[:, self.selected_indices_], columns=self.selected_features_)

    def get_feature_names_out(self, input_features=None):
        return np.asarray(self.selected_features_, dtype=object)


# 행 식별자와 기록용 표 저장
def sha_rows(row_ids):
    import hashlib
    return hashlib.sha256('\n'.join(map(str, row_ids)).encode('utf-8')).hexdigest()


def save(name, rows):
    data = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    data.to_csv(OUT / f'{name}.csv', index=False, encoding='utf-8')
    return data


# 확률 보정 없이 순위 또는 다수결로만 결합
class FrozenCombination(BaseEstimator):
    __module__ = 'src.temporal_robustness'

    def __init__(self, models, mode='hard', weights=(1, 1, 1)):
        self.models = models
        self.mode = mode
        self.weights = weights
        self.classes_ = np.arange(1, 7)

    def predict(self, X):
        return combine_predictions(self.models, X, self.mode, self.weights)


def combine_predictions(models, X, mode, weights):
    predictions = np.column_stack([model.predict(X) for model in models])
    if mode == 'hard':
        totals = np.column_stack([(predictions == gas).sum(axis=1) for gas in GASES]).astype(float)
        secondary = np.zeros_like(totals)
        secondary[np.arange(len(X)), predictions[:, 2] - 1] = 1
    else:
        points = []
        for model in models:
            classifier = model.named_steps['classifier']
            scores = model.predict_proba(X) if hasattr(classifier, 'predict_proba') else model.decision_function(X)
            # 점수 크기 대신 모델 내부의 클래스 순위만 사용
            order = np.argsort(-scores, axis=1, kind='stable')
            ranked = np.empty_like(scores, dtype=float)
            np.put_along_axis(ranked, order, np.tile(np.arange(5, -1, -1), (len(X), 1)), axis=1)
            points.append(ranked)
        totals = sum(weight * points[i] for i, weight in enumerate(weights))
        secondary = points[2]
    # 동점은 SVM 선택·순위 우선, 이후 작은 클래스 번호
    primary_mask = totals == totals.max(axis=1, keepdims=True)
    tiebreak = np.where(primary_mask, secondary, -np.inf)
    return np.argmax(tiebreak, axis=1) + 1


# 기존 설정을 유지한 새로운 특징 선택 파이프라인 구성
def build_pipeline(family, method):
    scaler = 'none' if family == 'RF' else 'standard'
    overrides = {'C': .1} if family == 'LR' else {}
    base = make_pipeline(FAMILIES[family], scaler, 'balanced', overrides)
    return Pipeline([
        ('imputer', SimpleImputer(strategy='median', keep_empty_features=True)),
        ('selector', TrainFeatureSelector(method)),
        *base.steps[1:],
    ])


# Fold별 과거·미래 분할 및 정확 중복 확인
def split_folds(frame):
    hashes = pd.util.hash_pandas_object(frame[FEATURES], index=False)
    rows = []
    for fold, (end, validation_batch) in FOLDS.items():
        train = frame[frame.batch <= end]
        validation = frame[frame.batch == validation_batch]
        assert train.batch.max() < validation_batch
        assert set(train.gas) == set(validation.gas) == set(GASES)
        assert set(train.row_id).isdisjoint(validation.row_id)
        assert set(hashes.loc[train.index]).isdisjoint(hashes.loc[validation.index])
        for partition, subset in [('train', train), ('validation', validation)]:
            for gas in GASES:
                rows.append(dict(fold=fold, partition=partition, gas_id=gas,
                                 gas=GASES[gas], n=int((subset.gas == gas).sum()),
                                 total_n=len(subset), first_batch=int(subset.batch.min()),
                                 last_batch=int(subset.batch.max())))
    development = frame[frame.batch <= 8]
    evaluation = frame[frame.batch >= 9]
    assert set(hashes.loc[development.index]).isdisjoint(hashes.loc[evaluation.index])
    return pd.DataFrame(rows)


# 실행 전 설정과 선정 규칙 고정
def freeze_protocol(frame):
    if OUT.exists() or MODELS.exists():
        raise FileExistsError('Robustness experiment output already exists')
    reports = ['temporal_robustness_improvement_report.html', 'temporal_robustness_model_selection.md',
               'temporal_robustness_protocol.md']
    if any((ROOT / 'reports' / name).exists() for name in reports):
        raise FileExistsError('Robustness experiment report already exists')
    supports = split_folds(frame)
    OUT.mkdir(parents=True)
    MODELS.mkdir(parents=True)
    supports.to_csv(OUT / 'fold_support.csv', index=False, encoding='utf-8')
    configs = [dict(config_id=f'{family}_{method}', family=family, method=method)
               for family in FAMILIES for method in METHODS]
    plan = dict(
        frozen_at_seoul=now(), seed=42, folds=FOLDS, single_configurations=configs,
        single_settings=18, ensemble_settings=4, total_settings=22, classifier_fits=54,
        final_train_batches=list(range(1, 7)), final_uses_existing_fold_B_fits=True,
        exploratory_evaluation_batches=[9, 10], baseline='saved B_SVM_balanced',
        variance='Keep 115 highest Train variances after Train min-max range normalization; '
        'remove bottom 13 (approximately 10%); not raw-unit variance.',
        correlation='Greedy original feature order; remove a feature if abs(Train Pearson r)>.98 '
        'with any retained earlier feature.',
        stability='Keep 64 lowest mean absolute same-gas Train batch mean shifts divided by '
        'global Train SD; equal gas/batch groups, exclude gases appearing in only one batch.',
        supervised='SelectKBest ANOVA f_classif k=32 or64; fit y uses Train only.',
        model_settings='LR balanced C=.1; RF balanced100 trees; SVM balanced C1 gamma=scale. '
        'StandardScaler LR/SVM, RF unscaled; median imputer then selector then scaling/classifier.',
        ensembles='hard_full; hard_representatives; rank_equal; rank_svm2. '
        'Rank points5..0; weights(1,1,1) or(1,1,2); no probability averaging.',
        soft_voting='Not run: saved SVM probability=False; no time-respecting calibration validated.',
        primary='Equal-weight mean of three Fold macro F1 values',
        protection='Mean other-four F1 >= reference-.03 and each other-four mean class F1 >= '
        'reference-.10. Reference own-family full for family representatives; SVM_all globally.',
        ties='Within .005 primary: fewer zero-recall fold/class pairs; higher minimum recall; '
        'higher min(mean Toluene F1, mean Acetaldehyde F1); higher pooled fold macro F1; '
        'lower fold SD; fixed config order.',
        fold_dependence='Overlapping training ranges; no independent-replicate significance claims. '
        'Family selection followed by ensemble validation is not nested; optimistic exploration.',
        evaluation_gate='Freeze candidate, weights, selected model hashes before 9–10 predictions.',
        prior_test_reuse=True, independent_test=False,
        training_config_sha256=sha(ROOT / 'training_config.json'),
    )
    write_json(OUT / 'experiment_plan.json', plan)
    text = '''# 8단계 사전 실험 계획

## 고정 분할 및 목적
Fold A: Train 1–3 → Validation 6. Fold B: Train 1–6 → Validation 7.
Fold C: Train 1–7 → Validation 8. Train/Validation 6종 및 support·중복 점검.
Train 범위가 겹치고 이전 Validation이 다음 Train에 포함되는 확장 창이므로 독립 반복 표본이 아님.
후보 확정 후 Batch 9–10은 기존 Test를 재사용한 회고적·탐색적 평가로만 사용.
최종 평가 모델은 Fold B(Train1–6) 바이트를 유지해 기존 6단계와 학습 범위를 통제함.
Train1–8 재학습은 이번 실험에 포함하지 않음.

## 설정 수와 전처리
3모델×6특징 조건=18개 설정, 3 Fold에서 분류기54회 Fit. 추가 결합4개=총22개 설정.
전체128 / min-max 범위 정규화 Train 분산 상위115 / abs Pearson>.98 중복 제거 /
Train 동일 가스 Batch 평균 이동이 작은64 / ANOVA SelectKBest32 / SelectKBest64.
분산법은 특징 단위 차이를 줄인 후 하위13개를 제거하는 제한적 대조임.
안정성은 같은 가스 Train 평균과 각 Train Batch 평균의 절대차를 전체 Train SD로 나눈 뒤
가스·Batch 그룹 동일 가중 평균. 2개 이상 Train Batch가 있는 가스만 사용.
작은 그룹의 평균 불확실성, 낮은 이동이 높은 구별 능력을 보장하지 않는 한계 보고.
상관 제거는 원래 특징 순서의 탐욕적 결정이며 최적 특징 집합을 의미하지 않음.
7단계 미래 특징 목록은 사용하지 않음. 미래 Batch·정답·통계로 특징 선택 Fit 금지.
median 결측값 처리 → 특징 선택 → LR/SVM StandardScaler → 분류기. RF 무스케일.
LR balanced C=.1 / RF balanced100 trees / SVM balanced C1,gamma=scale. 기존 나머지 설정 유지.
seed42, BLAS2, RF n_jobs=-1. 이번에는 특징 효과 분리를 위해 추가 파라미터 탐색 없음.

## 결합
full3 hard voting, 각 계열 대표3 hard voting, 대표3 순위점수 동일 가중,
대표3 순위점수 SVM2배(LR/RF/SVM=1/1/2). 순위점수5..0, 모델 내부 순위만 결합.
hard 동점은 SVM 예측 우선, 순위 동점은 SVM 순위 우선, 이후 작은 클래스 번호.
SVM probability=False이고 시간순 확률 보정 품질을 검증하지 않았으므로 Soft Voting 미실행.
순위 결합은 확률 결합이 아니며 신뢰도 크기 정보는 버림.
계열 대표 선정 후 같은 Fold로 결합을 비교하므로 중첩 검증이 아니며 선택 낙관 편향이 남음.

## 선정 규칙
주 지표는 세 Fold Macro F1 동일 가중 평균. 전체 Fold 합산 Macro F1 별도 기록.
계열 대표는 동일 계열 all을, 전체 후보는 SVM_all을 보호 기준의 참조로 사용.
나머지4종 평균 F1이 참조보다3pp 초과 하락하거나 그4종 각각의 Fold 평균 F1이
10pp 초과 하락하면 제외. 기준 모델은 항상 포함 가능.
유효 설정 최고 주 지표의0.5pp 이내에서 Recall0 Fold/가스 조합 수가 적은 것,
높은 최소Recall, 높은 min(Toluene 평균F1,Acetaldehyde 평균F1), 높은 합산Macro F1,
낮은 Fold SD, 고정 설정 순서로 선택. 이 수치는 사전 탐색 규칙이며 통계적 동등성·운영 기준 아님.
최고 평균 설정과 보호·동점 규칙을 적용한 후보를 구분해서 보고.
0% Recall은 숨기지 않으며 후보라도 최종 확정 모델이라고 주장하지 않음.
후보 및 모델 SHA를 고정한 뒤에만9–10 평가. 결과가 나빠도 후보·가중치·특징 변경 금지.

## 보존과 테스트
1–7단계 코드·원본·모델·보고서·과거 해시 수정 금지. 모델은 신규 경로에 저장.
기존2건 실패와 별도로7단계 전체 모델 목록 고정 검사는 승인된 신규 모델 추가로 실패 예상.
기존 테스트 수정 없이 과거 모델 각각의 해시 보존과 신규 재현성·누수 검사를 추가.
Commit·Push 금지.
'''
    (ROOT / 'reports/temporal_robustness_protocol.md').write_text(text, encoding='utf-8')
    return configs, plan


# 지표·클래스별 값과 예측 행 기록
def score_predictions(config_id, fold, subset, predicted, fit_seconds=0, predict_seconds=0, n_features=128):
    metric, classes, cm = measured_scores(subset.gas, predicted)
    metric.update(config_id=config_id, fold=fold, fit_seconds=fit_seconds,
                  predict_seconds=predict_seconds, n_features=n_features,
                  zero_recall_classes=','.join(str(c['gas_id']) for c in classes if c['recall'] == 0))
    per_class = [dict(config_id=config_id, fold=fold, **row) for row in classes]
    matrices = [dict(config_id=config_id, fold=fold, actual_id=g, predicted_id=h, count=int(cm[i, j]))
                for i, g in enumerate(GASES) for j, h in enumerate(GASES)]
    prediction = subset[['row_id', 'batch', 'gas']].rename(columns={'gas': 'y_true'}).copy()
    prediction['config_id'], prediction['fold'], prediction['y_pred'] = config_id, fold, predicted
    return metric, per_class, matrices, prediction


# 여러 Fold 결과의 동일 가중 평균과 실패 수 계산
def summarize(rows, classes, predictions, order):
    data, class_data = pd.DataFrame(rows), pd.DataFrame(classes)
    summary = []
    for config_id, group in data.groupby('config_id', sort=False):
        per_class = class_data[class_data.config_id == config_id]
        pred = predictions[predictions.config_id == config_id]
        pooled, _, _ = measured_scores(pred.y_true, pred.y_pred)
        row = dict(
            config_id=config_id, order=order[config_id], mean_macro_f1=float(group.macro_f1.mean()),
            sd_macro_f1=float(group.macro_f1.std(ddof=0)), pooled_macro_f1=pooled['macro_f1'],
            mean_accuracy=float(group.accuracy.mean()), mean_weighted_f1=float(group.weighted_f1.mean()),
            mean_toluene_recall=float(group.toluene_recall.mean()),
            mean_toluene_f1=float(group.toluene_f1.mean()),
            mean_acetaldehyde_recall=float(group.acetaldehyde_recall.mean()),
            mean_acetaldehyde_f1=float(group.acetaldehyde_f1.mean()),
            min_recall=float(per_class.recall.min()), zero_recall_pairs=int((per_class.recall == 0).sum()),
            mean_other_four_f1=float(group.other_four_f1.mean()),
            fit_seconds_sum=float(group.fit_seconds.sum()), predict_seconds_sum=float(group.predict_seconds.sum()),
            mean_n_features=float(group.n_features.mean()),
        )
        row['focus_min_f1'] = min(row['mean_toluene_f1'], row['mean_acetaldehyde_f1'])
        for gas in [1, 2, 3, 5]:
            row[f'mean_class{gas}_f1'] = float(per_class[per_class.gas_id == gas].f1.mean())
        summary.append(row)
    return pd.DataFrame(summary)


# 보호·근접 점수 규칙으로 후보 선택
def choose(summary, reference_id):
    reference = summary[summary.config_id == reference_id].iloc[0]
    eligible = summary.mean_other_four_f1 >= reference.mean_other_four_f1 - .03 - 1e-12
    for gas in [1, 2, 3, 5]:
        eligible &= summary[f'mean_class{gas}_f1'] >= reference[f'mean_class{gas}_f1'] - .10 - 1e-12
    valid = summary[eligible]
    near = valid[valid.mean_macro_f1 >= valid.mean_macro_f1.max() - .005 - 1e-12]
    near = near.sort_values(
        ['zero_recall_pairs', 'min_recall', 'focus_min_f1', 'pooled_macro_f1', 'sd_macro_f1', 'order'],
        ascending=[True, False, False, False, True, True])
    return near.iloc[0].config_id, valid.config_id.tolist()


# Fold 내부에서만 전처리와 분류기 학습
def train_folds(frame, configs):
    rows, classes, matrices, predictions, records = [], [], [], [], []
    order = {config['config_id']: i for i, config in enumerate(configs)}
    for fold, (end, target) in FOLDS.items():
        train, validation = frame[frame.batch <= end], frame[frame.batch == target]
        (MODELS / fold).mkdir()
        for config in configs:
            model = build_pipeline(config['family'], config['method'])
            start = time.perf_counter()
            with warnings.catch_warnings(record=True) as caught, threadpool_limits(limits=2):
                warnings.simplefilter('always')
                model.fit(train[FEATURES], train.gas,
                          selector__batches=train.batch.to_numpy(), selector__row_ids=train.row_id.to_numpy())
            fit_seconds = time.perf_counter() - start
            with threadpool_limits(limits=2):
                start = time.perf_counter()
                predicted = model.predict(validation[FEATURES])
                predict_seconds = time.perf_counter() - start
            selector = model.named_steps['selector']
            metric, per_class, cm, pred = score_predictions(
                config['config_id'], fold, validation, predicted, fit_seconds, predict_seconds,
                len(selector.selected_indices_))
            rows.append(metric)
            classes.extend(per_class)
            matrices.extend(cm)
            predictions.append(pred)
            path = MODELS / fold / f'{config["config_id"]}.joblib'
            joblib.dump(model, path, compress=3)
            records.append(dict(
                **config, fold=fold, model_file=str(path.relative_to(ROOT)), sha256=sha(path),
                train_n=len(train), train_row_ids_sha256=sha_rows(train.row_id),
                validation_n=len(validation), selected_features=selector.selected_features_,
                selector_scores=np.nan_to_num(selector.scores_).tolist(),
                classifier_params=model.named_steps['classifier'].get_params(),
                fit_seconds=fit_seconds, predict_seconds=predict_seconds,
                warnings=[dict(category=w.category.__name__, message=str(w.message)) for w in caught],
            ))
            print(f'Fold {fold} {config["config_id"]}: F1={metric["macro_f1"]:.6f}; '
                  f'features={len(selector.selected_indices_)}', flush=True)
    predictions = pd.concat(predictions, ignore_index=True)
    summary = summarize(rows, classes, predictions, order)
    family_representatives = {}
    for family in FAMILIES:
        subset = summary[summary.config_id.str.startswith(family + '_')]
        family_representatives[family] = choose(subset, family + '_all')[0]
    ensembles = [
        dict(config_id='hard_full', components=[f'{name}_all' for name in FAMILIES], mode='hard', weights=[1, 1, 1]),
        dict(config_id='hard_representatives', components=list(family_representatives.values()), mode='hard', weights=[1, 1, 1]),
        dict(config_id='rank_equal', components=list(family_representatives.values()), mode='rank', weights=[1, 1, 1]),
        dict(config_id='rank_svm2', components=list(family_representatives.values()), mode='rank', weights=[1, 1, 2]),
    ]
    for i, spec in enumerate(ensembles, start=len(configs)):
        order[spec['config_id']] = i
        for fold, (_, target) in FOLDS.items():
            validation = frame[frame.batch == target]
            components = [joblib.load(MODELS / fold / f'{name}.joblib') for name in spec['components']]
            model = FrozenCombination(components, spec['mode'], tuple(spec['weights']))
            with threadpool_limits(limits=2):
                start = time.perf_counter()
                predicted = model.predict(validation[FEATURES])
                seconds = time.perf_counter() - start
            component_records = [r for r in records if r['fold'] == fold and r['config_id'] in spec['components']]
            metric, per_class, cm, pred = score_predictions(
                spec['config_id'], fold, validation, predicted,
                sum(r['fit_seconds'] for r in component_records), seconds,
                len(set(f for r in component_records for f in r['selected_features'])))
            rows.append(metric)
            classes.extend(per_class)
            matrices.extend(cm)
            predictions = pd.concat([predictions, pred], ignore_index=True)
            path = MODELS / fold / f'{spec["config_id"]}.joblib'
            joblib.dump(model, path, compress=3)
    summary = summarize(rows, classes, predictions, order)
    selected, eligible = choose(summary, 'SVM_all')
    raw_leader = summary.sort_values(['mean_macro_f1', 'order'], ascending=[False, True]).iloc[0].config_id
    targets = list(dict.fromkeys([selected, 'SVM_all', *family_representatives.values()]))
    selected_files = {}
    for config_id in targets:
        source = MODELS / 'B' / f'{config_id}.joblib'
        path = MODELS / f'candidate_{config_id}.joblib'
        shutil.copy2(source, path)
        selected_files[config_id] = dict(path=str(path.relative_to(ROOT)), sha256=sha(path))
    decision = dict(
        frozen_at_seoul=now(), selected_candidate=selected, raw_mean_leader=raw_leader,
        family_representatives=family_representatives, eligible_candidates=eligible,
        selected_models=selected_files, ensembles=ensembles,
        final_train_batches=list(range(1, 7)), based_on='Folds A/B/C only',
        evaluation_seen_in_this_run=False, final_confirmed_model=False,
    )
    for name, data in [('fold_metrics', rows), ('fold_class_metrics', classes),
                       ('fold_confusion', matrices), ('cv_summary', summary)]:
        save(name, data)
    predictions.to_csv(OUT / 'fold_predictions.csv.gz', index=False, encoding='utf-8', compression='gzip')
    write_json(OUT / 'fit_records.json', records)
    write_json(OUT / 'selection_frozen.json', decision)
    return decision


# 고정 후보 확정 이후에만 동일 평가 Batch 예측
def evaluate_candidates(frame, configs, decision):
    selection_hash = sha(OUT / 'selection_frozen.json')
    started = now()
    rows, classes, matrices, predictions, times, hashes = [], [], [], [], [], []
    evaluation = frame[frame.batch >= 9]
    config_ids = [c['config_id'] for c in configs] + [c['config_id'] for c in decision['ensembles']]
    for config_id in config_ids + ['stage6_saved_SVM']:
        if config_id == 'stage6_saved_SVM':
            prior = json.loads((ROOT / 'outputs/temporal_expansion/selection_frozen.json').read_text(encoding='utf-8'))
            path = ROOT / prior['selected_models']['B_SVM_balanced']['path']
        else:
            path = MODELS / 'B' / f'{config_id}.joblib'
        hashes.append(dict(config_id=config_id, model_file=str(path.relative_to(ROOT)), sha256=sha(path)))
        model = joblib.load(path)
        with threadpool_limits(limits=2):
            start = time.perf_counter()
            predicted = model.predict(evaluation[FEATURES])
            seconds = time.perf_counter() - start
        times.append(dict(config_id=config_id, n=len(evaluation), predict_seconds=seconds,
                          ms_per_1000=seconds * 1e6 / len(evaluation)))
        for scope in ['pooled', 9, 10]:
            mask = np.ones(len(evaluation), dtype=bool) if scope == 'pooled' else evaluation.batch.to_numpy() == scope
            metric, per_class, cm, pred = score_predictions(
                config_id, str(scope), evaluation[mask], predicted[mask])
            rows.append(metric)
            classes.extend(per_class)
            matrices.extend(cm)
            if scope == 'pooled':
                predictions.append(pred)
    predictions = pd.concat(predictions, ignore_index=True)
    fresh = predictions[predictions.config_id == 'SVM_all'].sort_values('row_id')
    previous = predictions[predictions.config_id == 'stage6_saved_SVM'].sort_values('row_id')
    np.testing.assert_array_equal(fresh.y_pred, previous.y_pred)
    stored = pd.read_csv(ROOT / 'outputs/temporal_expansion/predictions.csv.gz')
    stored = stored[(stored.trial_id == 'B_SVM_balanced') & (stored.partition == 'evaluation')].sort_values('row_id')
    np.testing.assert_array_equal(previous.y_pred, stored.y_pred)
    assert sha(OUT / 'selection_frozen.json') == selection_hash
    for name, data in [('evaluation_metrics', rows), ('evaluation_class_metrics', classes),
                       ('evaluation_confusion', matrices), ('evaluation_times', times),
                       ('evaluation_model_hashes', hashes)]:
        save(name, data)
    predictions.to_csv(OUT / 'evaluation_predictions.csv.gz', index=False, encoding='utf-8', compression='gzip')
    write_json(OUT / 'evaluation_gate.json', dict(
        evaluation_started_at_seoul=started, selection_sha256=selection_hash,
        selection_frozen_at_seoul=decision['frozen_at_seoul'],
        selection_before_evaluation=decision['frozen_at_seoul'] <= started,
        evaluation_used_for_selection=False, baseline_exact_replay=True,
        fresh_full_SVM_matches_stage6=True,
    ))


# 기존 자료를 보존하면서 신규 실험 실행
def run():
    before = {str(p.relative_to(ROOT)): sha(p)
              for directory in ['src', 'tests', 'reports', 'models', 'outputs']
              for p in (ROOT / directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    before.update({name: sha(ROOT / name) for name in
                   ['config.json', 'training_config.json', 'README.md', 'requirements.txt', '.gitignore']})
    frame, source = load_dataset(read_config())
    raw = dict(zip(source.file, source.sha256))
    prior = json.loads((ROOT / 'outputs/temporal_failure_diagnostics/run_manifest.json').read_text(encoding='utf-8'))
    assert raw == prior['raw_hashes']
    configs, plan = freeze_protocol(frame)
    plan_hash = sha(OUT / 'experiment_plan.json')
    protocol_hash = sha(ROOT / 'reports/temporal_robustness_protocol.md')
    decision = train_folds(frame, configs)
    print('FROZEN CANDIDATE', decision['selected_candidate'], flush=True)
    evaluate_candidates(frame, configs, decision)
    from .temporal_robustness_report import build_report
    build_report(plan, decision)
    after = {name: sha(ROOT / name) for name in before}
    assert before == after
    assert sha(OUT / 'experiment_plan.json') == plan_hash
    assert all(sha(Path(read_config()['data_dir']) / name) == value for name, value in raw.items())
    write_json(OUT / 'run_manifest.json', dict(
        completed_at_seoul=now(), before=before, after=after, raw_hashes=raw,
        classifier_fits=54, single_settings=18, ensemble_settings=4, total_settings=22,
        plan_sha256=plan_hash, protocol_sha256=protocol_hash,
        final_train_batches=list(range(1, 7)), independent_test=False,
        code_sha256={name: sha(ROOT / 'src' / name) for name in
                     ['temporal_robustness.py', 'temporal_robustness_report.py']},
        package_versions={name: importlib.metadata.version(name) for name in
                          ['numpy', 'pandas', 'scikit-learn', 'scipy', 'joblib', 'matplotlib']},
    ))
    print(pd.read_csv(OUT / 'cv_summary.csv').to_string(index=False), flush=True)


if __name__ == '__main__':
    try:
        run()
    except Exception:
        logging.exception('Temporal robustness experiment failed')
        raise
