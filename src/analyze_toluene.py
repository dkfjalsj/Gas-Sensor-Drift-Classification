# 저장 모델로 Toluene 분류 실패와 학습 표본 구성 분석
# 새 학습 없이 기존 예측·원본·해시 기록 대조

import ast
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import joblib
import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from scipy.stats import wasserstein_distance
from threadpoolctl import threadpool_limits

from .data import ROOT, FEATURES, GASES, load_dataset, read_config
from .train_models import evaluate

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
def audit_history():
    rows = []
    sources = []
    registries = [
        ('stage2', OLD / 'preservation_checks.json', 'before'),
        ('stage3', ROOT / 'outputs/model_diagnostics/preservation.json', 'before'),
        ('readability', ROOT / 'reports/python_readability_audit.json', 'preserved_hashes'),
    ]
    for label, path, key in registries:
        content = json.loads(path.read_text(encoding='utf-8'))
        for name, expected in content[key].items():
            exists = (ROOT / name).is_file()
            current = sha(ROOT / name) if exists else None
            rows.append(dict(registry=label, file=name, expected=expected, current=current,
                             exact_match=current == expected, is_python=name.endswith('.py'),
                             exists=exists, transient_name_candidate='~$' in Path(name).name))
    manifest = json.loads((OLD / 'run_manifest.json').read_text(encoding='utf-8'))
    for name, expected in manifest['source_sha256'].items():
        current = sha(Path(read_config()['data_dir']) / name)
        rows.append(dict(registry='raw', file=name, expected=expected, current=current,
                         exact_match=current == expected, is_python=False, exists=True,
                         transient_name_candidate=False))
    records = json.loads((OLD / 'fit_records.json').read_text(encoding='utf-8'))
    for record in records:
        name = record['model_file']
        current = sha(ROOT / name)
        rows.append(dict(registry='models', file=name, expected=record['sha256'],
                         current=current, exact_match=current == record['sha256'], is_python=False,
                         exists=True, transient_name_candidate=False))
    comments = json.loads((ROOT / 'reports/python_comment_audit.json').read_text(encoding='utf-8'))
    for record in comments:
        current = ast_sha(ROOT / record['file'])
        sources.append(dict(registry='comment', file=record['file'],
                            expected_ast=record['before_ast_sha256'], current_ast=current,
                            ast_unchanged=current == record['before_ast_sha256']))
    readable = json.loads((ROOT / 'reports/python_readability_audit.json').read_text(encoding='utf-8'))
    for record in readable['source_files']:
        current = ast_sha(ROOT / record['file'])
        sources.append(dict(registry='readability', file=record['file'],
                            expected_ast=record['ast_sha256'], current_ast=current,
                            ast_unchanged=current == record['ast_sha256']))
    return pd.DataFrame(rows), pd.DataFrame(sources)


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
def run():
    report = ROOT / 'reports' / 'toluene_failure_analysis.html'
    if (OUT.exists() and any(OUT.iterdir())) or report.exists():
        raise FileExistsError('Stage 4 output exists; refuse to overwrite')
    baseline = [p for directory in ['src', 'tests', 'outputs', 'reports', 'models']
                for p in (ROOT / directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    before = {str(p.relative_to(ROOT)): sha(p) for p in baseline}
    OUT.mkdir(parents=True, exist_ok=True)
    history, source_ast = audit_history()
    history.to_csv(OUT / 'historical_hash_audit.csv', index=False, encoding='utf-8')
    source_ast.to_csv(OUT / 'source_ast_audit.csv', index=False, encoding='utf-8')
    material = ~history.is_python & ~history.transient_name_candidate
    if not source_ast.ast_unchanged.all() or (~history.exact_match & material).any():
        raise ValueError('Unexpected historical artifact or AST change; audit before continuing')
    frame, source = load_dataset(read_config())
    assignments = pd.read_csv(OLD / 'split_assignments.csv')
    counts = pd.crosstab(frame.batch, frame.gas).reindex(columns=GASES, fill_value=0)
    counts.columns = list(GASES.values())
    partitions = assignments.groupby(['experiment', 'partition'], sort=False).agg(total_n=('row_id', 'size'),
        toluene_n=('gas', lambda s: int((s == 6).sum())), class_n=('gas', 'nunique')).reset_index()
    partitions['toluene_ratio'] = partitions.toluene_n / partitions.total_n
    predictions, models, scores = model_inspection(frame, assignments)
    summary, errors = summarize_predictions(predictions)
    distances, centroids, stats = feature_comparison(frame, assignments)
    profiles = distances.groupby(['experiment', 'batch', 'reference_gas'], as_index=False).agg(
        mean_scaled_wasserstein=('wasserstein_scaled', 'mean'),
        mean_marginal_overlap=('histogram_overlap', 'mean'), reference_n=('reference_n', 'first'),
        target_toluene_n=('target_toluene_n', 'first'))
    consensus = consensus_errors(predictions)
    plan = experimental_plan(frame)
    tables = dict(batch_class_counts=counts.reset_index(), partition_counts=partitions,
                  model_audit=models, predictions=predictions, toluene_metrics=summary,
                  toluene_confusion=errors, model_scores=scores, consensus=consensus,
                  feature_distances=distances, gas_profiles=profiles, centroid_distances=centroids,
                  feature_stats=stats, exploratory_protocol=plan, historical_hash_audit=history,
                  source_ast_audit=source_ast)
    for name, table in tables.items():
        table.to_csv(OUT / f'{name}.csv', index=False, encoding='utf-8')
    from .toluene_report import make_report
    make_report(tables)
    after = {name: sha(ROOT / name) for name in before}
    raw_match = all(sha(Path(read_config()['data_dir']) / row['file']) == row['sha256'] for row in source.to_dict('records'))
    if before != after or not raw_match:
        raise RuntimeError('Existing source, model, result, or raw data changed')
    state = dict(generated_at_seoul=datetime.now(ZoneInfo('Asia/Seoul')).isoformat(),
                 classifier_fits=0, tuning_runs=0, model_overwrites=0, final_model_selected=False,
                 existing_files_unchanged=True, raw_files_unchanged=True, before=before, after=after,
                 raw_hashes=dict(zip(source.file, source.sha256)),
                 test_note='Full existing suite includes its pre-existing four-row synthetic fit test; no research model training',
                 code_sha256={name: sha(ROOT / 'src' / name) for name in ['analyze_toluene.py', 'toluene_report.py']})
    (OUT / 'run_manifest.json').write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
    print(partitions.to_string(index=False), flush=True)
    print(summary[(summary.scope == 'pooled') & (summary.partition == 'test')].to_string(index=False), flush=True)


if __name__ == '__main__':
    try:
        run()
    except Exception:
        logging.exception('Toluene analysis failed')
        raise
