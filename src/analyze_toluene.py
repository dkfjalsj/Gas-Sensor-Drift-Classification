# 저장 모델로 Toluene 분류 실패와 학습 표본 구성 분석
# 새 학습 없이 기존 예측·원본·해시 기록 대조

import ast
import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from scipy.stats import wasserstein_distance
from threadpoolctl import threadpool_limits

from .data import ROOT, FEATURES, GASES

OUT = ROOT / 'outputs' / 'toluene_analysis'
OLD = ROOT / 'outputs' / 'model_comparison'
COMMON = [6, 7, 8, 9, 10]
SELECTED = [1, 2, 3, 6, 9, 17, 65, 121]


# 파일 내용의 해시 계산
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# 주석과 공백을 제외한 코드 구조의 해시 계산
def ast_sha(path):
    tree = ast.parse(Path(path).read_text(encoding='utf-8'))
    return hashlib.sha256(ast.dump(tree, include_attributes=False).encode()).hexdigest()


# 기존 해시 기록과 현재 원본·결과·코드 구조 대조


# 훈련 자료의 고정 구간을 사용한 분포 겹침 계산
def marginal_overlap(reference, target, edges):
    first = np.histogram(reference, bins=edges)[0].astype(float)
    second = np.histogram(target, bins=edges)[0].astype(float)
    return float(np.minimum(first / first.sum(), second / second.sum()).sum())


# 동일 가스의 시간 변화와 다른 가스와의 분포 겹침 계산
def feature_comparison(frame, assignments):
    records = []
    centers = []
    stats = frame.groupby(['batch', 'gas'])[FEATURES].agg(['mean', 'median', 'std'])
    stats = stats.stack(level=0, future_stack=True).reset_index().rename(columns={'level_2': 'feature'})
    for exp in ['B_early', 'B_history']:
        train_ids = assignments[(assignments.experiment == exp) & (assignments.partition == 'train')].row_id
        train = frame[frame.row_id.isin(train_ids)]
        scale = train[FEATURES].std(ddof=0)
        edges = {}
        for feature in FEATURES:
            inner = np.unique(np.quantile(train[feature], np.linspace(0, 1, 21)[1:-1]))
            edges[feature] = np.r_[-np.inf, inner, np.inf]
        for batch in [1, 2, *COMMON]:
            target = frame[(frame.gas == 6) & (frame.batch == batch)]
            for gas in GASES:
                reference = train[train.gas == gas]
                for feature in FEATURES:
                    distance = wasserstein_distance(reference[feature], target[feature])
                    records.append(dict(
                        experiment=exp, batch=batch, reference_gas=GASES[gas],
                        reference_gas_id=gas, feature=feature, reference_n=len(reference),
                        target_toluene_n=len(target), wasserstein_raw=distance,
                        wasserstein_scaled=distance / scale[feature] if scale[feature] > 0 else np.nan,
                        histogram_overlap=marginal_overlap(reference[feature], target[feature], edges[feature]),
                    ))
        # 기존 훈련 전처리로만 좌표 변환
        pipe = joblib.load(ROOT / 'models' / f'{exp}__LogisticRegression.joblib')
        z_train = pipe[:-1].transform(train[FEATURES])
        means = np.vstack([z_train[train.gas.to_numpy() == gas].mean(axis=0) for gas in GASES])
        target = frame[frame.gas == 6]
        z = pipe[:-1].transform(target[FEATURES])
        distances = cdist(z, means) / np.sqrt(len(FEATURES))
        for i, row in enumerate(target.itertuples(index=False)):
            nearest = int(np.argmin(distances[i])) + 1
            for j, gas in enumerate(GASES):
                centers.append(dict(experiment=exp, row_id=row.row_id, batch=row.batch,
                                    reference_gas=GASES[gas], rms_distance=float(distances[i, j]),
                                    nearest_centroid_gas=GASES[nearest]))
    return pd.DataFrame(records), pd.DataFrame(centers), stats


# 저장 모델의 학습 클래스와 예측 재현 여부 확인
def model_inspection(frame, assignments):
    saved = pd.read_csv(OLD / 'predictions.csv')
    lookup = frame.set_index('row_id', drop=False)
    records = json.loads((OLD / 'fit_records.json').read_text(encoding='utf-8'))
    predictions = []
    audits = []
    scores = []
    for record in records:
        exp, model = record['experiment'], record['model']
        path = ROOT / record['model_file']
        if sha(path) != record['sha256']:
            raise ValueError('Saved model bytes changed: ' + path.name)
        pipe = joblib.load(path)
        classifier = pipe.named_steps['classifier']
        if list(classifier.classes_) != list(GASES) or list(pipe.feature_names_in_) != FEATURES:
            raise ValueError('Unexpected model classes or input features')
        selected = saved[(saved.experiment == exp) & (saved.model == model)]
        if not np.array_equal(lookup.loc[selected.row_id, 'gas'], selected.y_true):
            raise ValueError('Saved true labels do not match raw labels')
        parts = assignments[assignments.experiment == exp]
        mapping = parts.set_index('row_id')
        if not np.array_equal(mapping.loc[selected.row_id, 'partition'], selected.partition):
            raise ValueError('Saved evaluation partitions do not match')
        for part in ['train', 'validation', 'test']:
            ids = parts[parts.partition == part].row_id
            subset = lookup.loc[ids]
            with threadpool_limits(limits=2):
                predicted = pipe.predict(subset[FEATURES])
            if not set(predicted).issubset(set(GASES)):
                raise ValueError('Unknown predicted class')
            temp = subset[['row_id', 'batch', 'gas']].rename(columns={'gas': 'y_true'}).copy()
            temp['y_pred'] = predicted
            temp['experiment'] = exp
            temp['model'] = model
            temp['partition'] = part
            if part != 'train':
                old = selected[selected.partition == part].set_index('row_id').y_pred
                if not np.array_equal(temp.y_pred, old.loc[temp.row_id]):
                    raise ValueError('Prediction replay mismatch')
            predictions.append(temp)
            # 기존 점수만 확인하고 새 판정 기준은 만들지 않음
            if model == 'RandomForest':
                decision = pipe.predict_proba(subset[FEATURES])
                score_type = 'uncalibrated_tree_vote_fraction'
            else:
                decision = pipe.decision_function(subset[FEATURES])
                score_type = 'linear_class_score' if model == 'LogisticRegression' else 'ovr_vote_transformed_score'
            position = list(classifier.classes_).index(6)
            others = np.delete(decision, position, axis=1).max(axis=1)
            mask = subset.gas.to_numpy() == 6
            for row_id, batch, value, gap in zip(subset.row_id[mask], subset.batch[mask], decision[mask, position], (decision[:, position] - others)[mask]):
                scores.append(dict(experiment=exp, model=model, partition=part, row_id=row_id,
                                   batch=int(batch), score_type=score_type,
                                   toluene_score=float(value), toluene_minus_best_other=float(gap)))
        audits.append(dict(experiment=exp, model=model, declared_classes=','.join(map(str, classifier.classes_)),
                           has_toluene_class=True, label_mapping='raw integer 6 -> Toluene; no inverse transform',
                           toluene_train_n=int(((parts.partition == 'train') & (parts.gas == 6)).sum()),
                           replay_n=len(selected), exact_prediction_replay=True,
                           svm_toluene_support_vectors=int(classifier.n_support_[5]) if model == 'SVM_RBF' else None))
        print('Replayed', exp, model, flush=True)
    return pd.concat(predictions, ignore_index=True), pd.DataFrame(audits), pd.DataFrame(scores)


# Toluene 정답 비율과 예측 비율을 분리해 계산
def summarize_predictions(predictions):
    rows = []
    errors = []
    for (exp, model, part), sub in predictions.groupby(['experiment', 'model', 'partition'], sort=False):
        scopes = [('pooled', 0, sub)] + [('batch', int(b), group) for b, group in sub.groupby('batch')]
        for scope, batch, group in scopes:
            actual = group.y_true == 6
            predicted = group.y_pred == 6
            support = int(actual.sum())
            correct = int((actual & predicted).sum())
            precision = correct / predicted.sum() if predicted.any() else 0.0
            recall = correct / support if support else np.nan
            f1 = 2 * precision * recall / (precision + recall) if support and precision + recall > 0 else (0.0 if support else np.nan)
            rows.append(dict(experiment=exp, model=model, partition=part, scope=scope, batch=batch,
                             total_n=len(group), toluene_n=support, correct_toluene=correct,
                             toluene_recall=recall, toluene_f1=f1, toluene_precision=precision if support else np.nan,
                             predicted_toluene_n=int(predicted.sum()), predicted_toluene_ratio=float(predicted.mean()),
                             true_toluene_ratio=float(actual.mean()), observed_predicted_classes=','.join(map(str, sorted(group.y_pred.unique())))))
            for gas in GASES:
                count = int((actual & (group.y_pred == gas)).sum())
                errors.append(dict(experiment=exp, model=model, partition=part, scope=scope, batch=batch,
                                   predicted_gas=GASES[gas], predicted_gas_id=gas, count=count,
                                   toluene_support=support, fraction=count / support if support else np.nan))
    return pd.DataFrame(rows), pd.DataFrame(errors)


# 세 모델이 같은 Toluene 표본에서 같은 예측을 했는지 확인
def consensus_errors(predictions):
    rows = []
    for exp in ['B_early', 'B_history']:
        sub = predictions[(predictions.experiment == exp) & (predictions.partition == 'test') & (predictions.y_true == 6)]
        pivot = sub.pivot(index='row_id', columns='model', values='y_pred')
        for row_id, row in pivot.iterrows():
            values = row.to_numpy()
            rows.append(dict(experiment=exp, row_id=row_id,
                             all_three_wrong=bool(np.all(values != 6)),
                             unanimous_prediction=GASES[int(values[0])] if len(set(values)) == 1 else 'mixed',
                             lr_prediction=int(row.LogisticRegression), rf_prediction=int(row.RandomForest),
                             svm_prediction=int(row.SVM_RBF)))
    return pd.DataFrame(rows)


# 이미 관찰한 자료를 쓰는 시간순 개선 설계안 작성
def experimental_plan(frame):
    rows = []
    for end in [5, 6, 7, 8]:
        train = frame[frame.batch <= end]
        validation = frame[frame.batch == end + 1]
        test = frame[frame.batch == end + 2]
        rows.append(dict(train_batches=f'1–{end}', validation_batch=end + 1, test_batch=end + 2,
                         train_n=len(train), validation_n=len(validation), test_n=len(test),
                         train_toluene_n=int((train.gas == 6).sum()),
                         validation_toluene_n=int((validation.gas == 6).sum()),
                         test_toluene_n=int((test.gas == 6).sum()), evaluation_type='exploratory: previously observed batches'))
    return pd.DataFrame(rows)


# 기존 산출물 보존 및 새 분석만 별도 저장


