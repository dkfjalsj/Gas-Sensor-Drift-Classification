# 동일 자료 분할로 세 모델 학습 및 성능 비교

"""Fixed baseline experiments; no tuning, refit on validation, or EDA transformer reuse.

Run from project root: .venv/Scripts/python.exe -m src.train_models
"""

import argparse
import hashlib
import importlib.metadata
import json
import logging
import platform
import sys
import time
import warnings
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from threadpoolctl import threadpool_limits

from .data import ROOT, FEATURES, GASES, load_dataset, read_config, duplicate_summary

OUT = ROOT / 'outputs' / 'model_comparison'
LABELS = list(GASES)


# 파일 변경 확인용 해시 계산
def fingerprint(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# 결과를 JSON 파일로 저장
def write_json(path, value):
    Path(path).write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8'
    )


# 훈련·검증·테스트 자료를 동일 기준으로 분할
def make_splits(frame, settings):
    """A keeps the old seeded 20% Test, then splits remaining 80% 75:25."""
    indices = np.arange(len(frame))
    splits = {}
    for name, spec in settings['experiments'].items():
        if name == 'A_random':
            # 가스 비율을 유지하며 자료 분할
            development, test = train_test_split(
                indices, test_size=0.2, stratify=frame.gas, random_state=settings['random_state']
            )
            # 가스 비율을 유지하며 자료 분할
            train, validation = train_test_split(
                development,
                test_size=0.25,
                stratify=frame.gas.iloc[development],
                random_state=settings['random_state'],
            )
            splits[name] = {'train': train, 'validation': validation, 'test': test}
        else:
            splits[name] = {
                part: indices[frame.batch.isin(spec[f'{part}_batches'])]
                for part in ('train', 'validation', 'test')
            }
    return splits


# 자료 분할의 중복과 시간 순서 검사
def audit_splits(frame, splits):
    groups = pd.util.hash_pandas_object(frame[FEATURES], index=False).astype(str)
    records, assignments = [], []
    for experiment, parts in splits.items():
        if any(len(idx) == 0 for idx in parts.values()):
            raise ValueError(f'Empty partition: {experiment}')
        sets = {part: set(map(int, idx)) for part, idx in parts.items()}
        if any(
            sets[a] & sets[b]
            for a, b in [('train', 'validation'), ('train', 'test'), ('validation', 'test')]
        ):
            raise ValueError(f'Overlapping rows: {experiment}')
        if set.union(*sets.values()) != set(range(len(frame))):
            raise ValueError(f'Partitions do not cover the dataset: {experiment}')
        if set(frame.gas.iloc[parts['train']]) != set(LABELS):
            raise ValueError(f'Train missing a gas class: {experiment}')
        for a, b in [('train', 'validation'), ('train', 'test'), ('validation', 'test')]:
            if set(groups.iloc[parts[a]]) & set(groups.iloc[parts[b]]):
                raise ValueError(
                    f'Exact feature duplicates cross partitions: {experiment}/{a}/{b}; resolve group splitting before training'
                )
        if experiment.startswith('B_'):
            if not (
                frame.batch.iloc[parts['train']].max() < frame.batch.iloc[parts['validation']].min()
                and frame.batch.iloc[parts['validation']].max()
                < frame.batch.iloc[parts['test']].min()
            ):
                raise ValueError(f'Future information in chronological split: {experiment}')
        for part, idx in parts.items():
            subset = frame.iloc[idx]
            records.append(
                dict(
                    experiment=experiment,
                    partition=part,
                    n=len(idx),
                    batches=sorted(map(int, subset.batch.unique())),
                    class_counts={str(g): int((subset.gas == g).sum()) for g in LABELS},
                    missing_classes=[GASES[g] for g in LABELS if not (subset.gas == g).any()],
                    row_overlap=0,
                    cross_partition_exact_duplicate_groups=0,
                )
            )
            for row in subset[['row_id', 'batch', 'gas']].itertuples(index=False):
                assignments.append(
                    dict(
                        experiment=experiment,
                        partition=part,
                        row_id=row.row_id,
                        batch=row.batch,
                        gas=row.gas,
                    )
                )
    return records, pd.DataFrame(assignments)


# 자료 정리 단계와 분류 모델을 파이프라인으로 연결
def make_pipeline(name, settings):
    constructors = {
        'LogisticRegression': LogisticRegression,
        'RandomForest': RandomForestClassifier,
        'SVM_RBF': SVC,
    }
    # 훈련 중앙값으로 결측값 처리 준비
    steps = [('imputer', SimpleImputer(strategy='median', keep_empty_features=True))]
    if name != 'RandomForest':
        steps.append(('scaler', StandardScaler()))
    steps.append(('classifier', constructors[name](**settings['models'][name])))
    return Pipeline(steps)


# 실제 정답과 예측 비교 및 성능 계산
def evaluate(y, pred):
    y, pred = np.asarray(y), np.asarray(pred)
    p, r, f, support = precision_recall_fscore_support(y, pred, labels=LABELS, zero_division=0)
    present = support > 0
    metrics = dict(
        n=len(y),
        accuracy=float(accuracy_score(y, pred)),
        macro_precision=float(p[present].mean()),
        macro_recall=float(r[present].mean()),
        macro_f1=float(f[present].mean()),
        weighted_f1=float(np.average(f, weights=support)),
        macro_precision_fixed6=float(p.mean()),
        macro_recall_fixed6=float(r.mean()),
        macro_f1_fixed6=float(f.mean()),
        missing_classes=','.join(GASES[g] for g, mask in zip(LABELS, present) if not mask),
    )
    per_class = []
    for i, g in enumerate(LABELS):
        per_class.append(
            dict(
                gas_id=g,
                gas=GASES[g],
                support=int(support[i]),
                predicted_count=int((pred == g).sum()),
                precision=float(p[i]) if present[i] else None,
                recall=float(r[i]) if present[i] else None,
                f1=float(f[i]) if present[i] else None,
            )
        )
    # 실제 가스·예측 가스 조합별 개수 계산
    return metrics, per_class, confusion_matrix(y, pred, labels=LABELS)


# 자료 불러오기 및 분석 결과 저장
def run():
    settings_path = ROOT / 'training_config.json'
    settings = json.loads(settings_path.read_text(encoding='utf-8'))
    OUT.mkdir(parents=True, exist_ok=True)
    models_dir = ROOT / 'models'
    models_dir.mkdir(exist_ok=True)
    # Freeze hashes of pre-existing EDA files; model outputs are kept in a separate directory.
    preserved = [p for p in (ROOT / 'outputs').rglob('*') if p.is_file() and OUT not in p.parents]
    preserved += [
        ROOT / 'reports' / 'eda_report.html',
        ROOT / 'reports' / 'evaluation_design.md',
        ROOT / 'src' / 'data.py',
        ROOT / 'src' / 'analysis.py',
    ]
    before = {str(p.relative_to(ROOT)): fingerprint(p) for p in preserved}
    config = read_config()
    # 원본 자료 불러오기
    frame, source_files = load_dataset(config)
    if (
        len(frame) != config['expected_samples']
        or not np.isfinite(frame[FEATURES].to_numpy()).all()
    ):
        raise ValueError(
            'Dataset shape or finite-value checks failed; inspect data before training'
        )
    _, duplicate_info = duplicate_summary(frame)
    if duplicate_info['conflicting_label_groups']:
        raise ValueError('Conflicting labels for identical features')
    splits = make_splits(frame, settings)
    audits, assignments = audit_splits(frame, splits)
    assignments.to_csv(OUT / 'split_assignments.csv', index=False, encoding='utf-8')
    write_json(OUT / 'split_audit.json', audits)
    source_files.to_csv(OUT / 'source_validation.csv', index=False, encoding='utf-8')
    write_json(OUT / 'experiment_config.json', settings)
    metric_rows, class_rows, predictions, confusion_rows, fit_records = [], [], [], [], []
    for experiment, parts in splits.items():
        train = frame.iloc[parts['train']]
        for name in settings['models']:
            print(f'Training {experiment}/{name}: {len(train)} samples', flush=True)
            pipeline = make_pipeline(name, settings)
            start = time.perf_counter()
            with warnings.catch_warnings(record=True) as captured, threadpool_limits(limits=2):
                warnings.simplefilter('always')
                # 훈련 자료로만 전처리와 모델 학습
                pipeline.fit(train[FEATURES], train.gas)
            fit_seconds = time.perf_counter() - start
            model_path = models_dir / f'{experiment}__{name}.joblib'
            # 전처리와 모델을 함께 파일로 저장
            joblib.dump(pipeline, model_path, compress=3)
            classifier = pipeline.named_steps['classifier']
            record = dict(
                experiment=experiment,
                model=name,
                fit_seconds=fit_seconds,
                model_file=str(model_path.relative_to(ROOT)),
                sha256=fingerprint(model_path),
                train_n=len(train),
                warnings=[
                    {'category': w.category.__name__, 'message': str(w.message)} for w in captured
                ],
                params=classifier.get_params(),
                n_iter=(
                    np.asarray(classifier.n_iter_).tolist()
                    if hasattr(classifier, 'n_iter_')
                    else None
                ),
                feature_columns=FEATURES,
                trained_only_on='train',
            )
            fit_records.append(record)
            write_json(model_path.with_suffix('.json'), record)
            for partition in ('validation', 'test'):
                subset = frame.iloc[parts[partition]]
                with threadpool_limits(limits=2):
                    # 학습된 모델로 가스 종류 예측
                    pred = pipeline.predict(subset[FEATURES])
                identity = dict(experiment=experiment, model=name, partition=partition)
                prediction_frame = (
                    subset[['row_id', 'batch', 'gas']].rename(columns={'gas': 'y_true'}).copy()
                )
                prediction_frame['y_pred'] = pred
                for key, value in identity.items():
                    prediction_frame[key] = value
                predictions.append(prediction_frame)
                scopes = [('pooled', 0, np.ones(len(subset), dtype=bool))]
                scopes += [
                    ('batch', int(b), subset.batch.to_numpy() == b)
                    for b in sorted(subset.batch.unique())
                ]
                for scope, batch, mask in scopes:
                    metrics, per_class, cm = evaluate(subset.gas.to_numpy()[mask], pred[mask])
                    meta = dict(**identity, scope=scope, batch=batch)
                    metric_rows.append({**meta, **metrics})
                    class_rows.extend({**meta, **row} for row in per_class)
                    for i, g in enumerate(LABELS):
                        for j, h in enumerate(LABELS):
                            confusion_rows.append(
                                dict(**meta, true_class=g, predicted_class=h, count=int(cm[i, j]))
                            )
                print(f'  {partition}: accuracy={accuracy_score(subset.gas,pred):.6f}', flush=True)
            pd.DataFrame(metric_rows).to_csv(OUT / 'metrics.csv', index=False, encoding='utf-8')
            pd.DataFrame(class_rows).to_csv(
                OUT / 'per_class_metrics.csv', index=False, encoding='utf-8'
            )
            pd.concat(predictions, ignore_index=True).to_csv(
                OUT / 'predictions.csv', index=False, encoding='utf-8'
            )
            pd.DataFrame(confusion_rows).to_csv(
                OUT / 'confusion_matrices.csv', index=False, encoding='utf-8'
            )
            write_json(OUT / 'fit_records.json', fit_records)
    metrics = pd.DataFrame(metric_rows)
    stability = []
    for (experiment, model), sub in metrics[
        (metrics.partition == 'test') & (metrics.scope == 'batch')
    ].groupby(['experiment', 'model'], sort=False):
        for scope, selected in [
            ('all_test_batches_present_class', sub),
            ('common_full6_batches_6_to_10', sub[sub.batch.isin([6, 7, 8, 9, 10])]),
        ]:
            stability.append(
                dict(
                    experiment=experiment,
                    model=model,
                    scope=scope,
                    batches=','.join(map(str, selected.batch)),
                    n_batches=len(selected),
                    mean_accuracy=selected.accuracy.mean(),
                    mean_macro_f1=selected.macro_f1.mean(),
                    std_macro_f1=selected.macro_f1.std(ddof=0),
                    min_macro_f1=selected.macro_f1.min(),
                    max_macro_f1=selected.macro_f1.max(),
                    note='equal batch weight; descriptive population SD; A has seen other rows from these batches',
                )
            )
    stability = pd.DataFrame(stability)
    stability.to_csv(OUT / 'batch_stability.csv', index=False, encoding='utf-8')
    pooled = metrics[(metrics.partition == 'test') & (metrics.scope == 'pooled')]
    gap = pooled.pivot(index='model', columns='experiment', values=['accuracy', 'macro_f1'])
    for metric in ('accuracy', 'macro_f1'):
        gap[(metric, 'A_minus_B_early')] = gap[(metric, 'A_random')] - gap[(metric, 'B_early')]
        gap[(metric, 'A_minus_B_history')] = gap[(metric, 'A_random')] - gap[(metric, 'B_history')]
    gap.to_csv(OUT / 'random_batch_gap.csv', encoding='utf-8')
    after = {name: fingerprint(ROOT / name) for name in before}
    if before != after:
        raise RuntimeError('Pre-existing EDA files changed during training')
    for row in source_files.to_dict('records'):
        if fingerprint(Path(config['data_dir']) / row['file']) != row['sha256']:
            raise RuntimeError('Source bytes changed during training')
    write_json(
        OUT / 'preservation_checks.json',
        dict(eda_files_unchanged=True, source_files_unchanged=True, before=before, after=after),
    )
    manifest = dict(
        generated_at_seoul=datetime.now(ZoneInfo('Asia/Seoul')).isoformat(),
        python=platform.python_version(),
        package_versions={
            p: importlib.metadata.version(p)
            for p in ['numpy', 'pandas', 'scikit-learn', 'scipy', 'matplotlib', 'joblib', 'pytest']
        },
        training_config_sha256=fingerprint(settings_path),
        code_sha256={
            f'src/{name}': fingerprint(ROOT / 'src' / name)
            for name in ['train_models.py', 'model_report.py', 'data.py']
        },
        random_state=settings['random_state'],
        threadpool_limits=2,
        validation_used_for_tuning=False,
        refit_on_train_plus_validation=False,
        models_fitted=len(fit_records),
        final_model_selected=False,
        raw_data_dir=config['data_dir'],
        source_sha256={r['file']: r['sha256'] for r in source_files.to_dict('records')},
    )
    write_json(OUT / 'run_manifest.json', manifest)
    from .model_report import make_report

    make_report(
        metrics,
        pd.DataFrame(class_rows),
        pd.concat(predictions, ignore_index=True),
        stability,
        audits,
        fit_records,
        manifest,
    )
    print(
        pooled[
            [
                'experiment',
                'model',
                'n',
                'accuracy',
                'macro_precision',
                'macro_recall',
                'macro_f1',
                'weighted_f1',
            ]
        ].to_string(index=False),
        flush=True,
    )


# 프로그램 실행 및 오류 안내
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try:
        run()
    except (OSError, ValueError, RuntimeError, KeyError) as exc:
        logging.exception('Model experiment failed: %s', exc)
        sys.exit(1)


if __name__ == '__main__':
    main()
