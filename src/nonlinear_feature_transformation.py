# 비선형 특징 변환과 고정 SVM의 시간순 성능 비교
# 실행 전 계획 고정 및 기존 자료 보존 검사

import argparse
import base64
import copy
import hashlib
import html
import importlib.metadata
import json
import time
import warnings
from pathlib import Path

import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.metrics import precision_recall_fscore_support
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PowerTransformer, StandardScaler
from sklearn.svm import SVC
from threadpoolctl import threadpool_limits

from .data import ROOT, FEATURES, GASES, load_dataset, read_config
from .temporal_expansion import now, sha, write_json

OUT = ROOT / 'outputs/nonlinear_feature_transformation'
MODEL_DIR = ROOT / 'models/nonlinear_feature_transformation'
REPORT_NAMES = [f'nonlinear_feature_transformation_{suffix}' for suffix in
                ['report.html', 'summary.md', 'limitations.md']]
FOLDS = {'A': (3, 6), 'B': (6, 7), 'C': (7, 8)}
METHODS = ['baseline', 'signed_log', 'yeo_johnson']
LIMITATION = ('새 독립 Test 없음. 과거 Fold는 반복 사용된 개발 자료이며 서로 독립적인 반복 표본이 아님. '
              'Batch 9~10 신규 평가 없음. 공식 Model A 유지.')


# 배열과 행 순서 지문 계산
def digest(values):
    array = np.ascontiguousarray(values, dtype='<f8')
    return hashlib.sha256(array.tobytes()).hexdigest()


def row_digest(values):
    return hashlib.sha256('\n'.join(map(str, values)).encode('utf-8')).hexdigest()


# Train 통계만 학습하는 부호 보존 로그·Yeo–Johnson 변환
class TrainTransform(TransformerMixin, BaseEstimator):
    def __init__(self, method='signed_log'):
        self.method = method

    def fit(self, X, y=None):
        values = np.asarray(X, dtype=float)
        if values.ndim != 2 or not np.isfinite(values).all():
            raise ValueError('Finite two-dimensional Train data required')
        if self.method not in ['signed_log', 'yeo_johnson']:
            raise ValueError('Unknown transform')
        self.n_features_in_ = values.shape[1]
        self.n_samples_seen_ = len(values)
        self.fit_input_sha256_ = digest(values)
        absolute = np.median(np.abs(values), axis=0)
        # 아주 작은 중앙값은 해당 Train 특징의 최대 크기로 보완
        self.floor_ = np.maximum(1e-12, 1e-12 * np.max(np.abs(values), axis=0))
        self.scale_ = np.maximum(absolute, self.floor_)
        self.constant_ = np.ptp(values, axis=0) == 0
        self.lambdas_ = np.full(values.shape[1], np.nan)
        self.status_ = ['not_applicable'] * values.shape[1]
        self.transformers_ = {}
        if self.method == 'yeo_johnson':
            for j in range(values.shape[1]):
                if self.constant_[j]:
                    self.status_[j] = 'constant_identity'
                    continue
                transformer = PowerTransformer(method='yeo-johnson', standardize=False)
                # 수치 경고·오류는 해당 특징의 원값 유지 및 기록
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter('error', RuntimeWarning)
                        transformed = transformer.fit_transform(values[:, [j]])
                    if not np.isfinite(transformed).all():
                        raise ValueError('Nonfinite fitted transform')
                    self.transformers_[j] = transformer
                    self.lambdas_[j] = transformer.lambdas_[0]
                    self.status_[j] = 'fitted'
                except (ValueError, ArithmeticError, RuntimeWarning) as exc:
                    self.status_[j] = f'train_failure_identity:{type(exc).__name__}'
        return self

    def transform(self, X):
        values = np.asarray(X, dtype=float)
        if values.ndim != 2 or values.shape[1] != self.n_features_in_:
            raise ValueError('Feature count/order contract violation')
        if not np.isfinite(values).all():
            raise ValueError('Finite transform input required')
        with np.errstate(over='raise', invalid='raise', divide='raise'):
            if self.method == 'signed_log':
                result = np.sign(values) * np.log1p(np.abs(values) / self.scale_)
            else:
                result = values.copy()
                for j, transformer in self.transformers_.items():
                    result[:, j] = transformer.transform(values[:, [j]])[:, 0]
        if not np.isfinite(result).all():
            raise ValueError('Nonfinite output: abort candidate without changing transform')
        return result

    def get_feature_names_out(self, input_features=None):
        return np.asarray(input_features if input_features is not None else
                          [f'x{i}' for i in range(self.n_features_in_)], dtype=object)


# 동일한 특징 순서·SVM 설정으로 파이프라인 구성
def build_pipeline(method):
    steps = [('imputer', SimpleImputer(strategy='median', keep_empty_features=True))]
    if method != 'baseline':
        steps.append(('transform', TrainTransform(method)))
    steps.extend([
        ('scaler', StandardScaler()),
        ('classifier', SVC(C=1., gamma='scale', kernel='rbf', class_weight='balanced',
                           probability=False, random_state=42, cache_size=512)),
    ])
    return Pipeline(steps)


# 기존 정식 파일의 바이트 지문 수집
def snapshot():
    result = {}
    for folder in ['src', 'tests', 'models', 'reports', 'outputs']:
        for path in (ROOT / folder).rglob('*'):
            if (not path.is_file() or '__pycache__' in path.parts or
                    OUT in path.parents or MODEL_DIR in path.parents or
                    (path.parent == ROOT / 'reports' and path.name in REPORT_NAMES)):
                continue
            result[str(path.relative_to(ROOT))] = sha(path)
    for name in ['README.md', 'config.json', 'training_config.json', '.gitignore',
                 'requirements.txt', 'requirements-lock.txt']:
        result[name] = sha(ROOT / name)
    return result


# 세 Fold의 시간순·정확 중복·클래스 검사
def validate_splits(frame):
    if (frame.batch > 8).any():
        raise ValueError('No Batch9/10 rows permitted in development frame')
    fingerprints = pd.util.hash_pandas_object(frame[FEATURES], index=False)
    rows, supports = [], []
    for fold, (end, batch) in FOLDS.items():
        train = frame[frame.batch <= end]
        validation = frame[frame.batch == batch]
        assert train.batch.max() < validation.batch.min()
        assert set(train.row_id).isdisjoint(validation.row_id)
        assert set(fingerprints.loc[train.index]).isdisjoint(fingerprints.loc[validation.index])
        assert set(train.gas) == set(GASES)
        for part, sub in [('train', train), ('validation', validation)]:
            rows.extend(dict(fold=fold, partition=part, row_id=row.row_id,
                             batch=int(row.batch), gas_id=int(row.gas))
                        for row in sub.itertuples())
            supports.extend(dict(fold=fold, partition=part, gas_id=g, gas=GASES[g],
                                 support=int((sub.gas == g).sum())) for g in GASES)
    return pd.DataFrame(rows), pd.DataFrame(supports)


def save(name, rows):
    table = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    table.to_csv(OUT / f'{name}.csv', index=False, encoding='utf-8')
    return table


# 신규 학습 전에 계획·분할·수치 규칙 동결
def freeze():
    if OUT.exists() or MODEL_DIR.exists() or any((ROOT / 'reports' / n).exists()
                                               for n in REPORT_NAMES):
        raise FileExistsError('Stage14 outputs already exist; refuse overwrite')
    frame, raw = load_dataset(read_config())
    development = frame[frame.batch <= 8].copy()
    assignments, supports = validate_splits(development)
    before = snapshot()
    OUT.mkdir()
    MODEL_DIR.mkdir()
    save('split_assignments', assignments)
    save('fold_support', supports)
    plan = dict(
        stage=14, frozen_at=now(), folds=FOLDS, methods=METHODS,
        maximum_pipeline_evaluations=9, maximum_new_classifier_fits=9,
        train_policy='All rows; same ordered 128 features and rows for every condition',
        signed_log='sign(x)*log1p(abs(x)/s); s=max(median(abs(imputed Train)), '
                   '1e-12, 1e-12*max(abs(imputed Train))) per feature',
        yeo_johnson='PowerTransformer(yeo-johnson, standardize=False) per column; '
                    'constant column identity; numerical Train failure identity with reason; '
                    'any Validation transform failure invalidates candidate; no refit/replacement',
        fit_boundary='Only each Fold Train; metadata contains input and ordered-row hashes',
        svm=dict(C=1., gamma='scale', kernel='rbf', class_weight='balanced',
                 probability=False, random_state=42),
        metrics='Accuracy, equal-present-class macro F1, weighted F1; six-class P/R/F1/support; '
                'confusion, prediction fractions, directional errors, min recall, zero count',
        aggregation='Equal Fold mean macro F1; per-gas means over positive-support Folds only; '
                    'other-four F1 = equal gas means for ids1,2,3,5; missing truth metrics NaN '
                    '(not zero); zero precision for supported but never-predicted class',
        guards=dict(macro_gain_min=.005, per_gas_mean_recall_loss_max=.05,
                    other_four_mean_f1_loss_max=.02, zero_pair_increase_max=0,
                    no_new_zero_when_baseline_positive=True, inclusive=True, tolerance=1e-12),
        conclusion='A iff all guards and 3 complete Folds; B iff any positive macro or gas '
                   'P/R/F1 change but not all guards; C otherwise; no auto ModelA replacement',
        tie='Among all-guard candidates: higher mean macro F1; within1e-12 use fewer zeros, '
            'higher minimum recall, then signed_log before yeo_johnson',
        uncertainty=LIMITATION, future_evaluation=False,
        stop='No additional candidates, tuning, feature selection or ensembles. Technical failure '
             'invalidates condition, no replacement. Leakage/preservation failure aborts run.',
        reuse='Stage8 SVM_all only after file hash, ordered rows, all-feature identity selector, '
              'imputer, scaler, SVM params and feature shape checks; unwrap identity only; '
              'reference predictions must match stored Stage8 validation predictions',
        distribution_features='Train1-3 only: top3 absolute standardized third moments, '
                              'stable original feature order for ties; no validation ranking',
        split_sha256=sha(OUT / 'split_assignments.csv'),
        versions={name: importlib.metadata.version(name) for name in
                  ['numpy', 'pandas', 'scikit-learn', 'scipy', 'joblib', 'matplotlib']},
    )
    write_json(OUT / 'experiment_plan.json', plan)
    write_json(OUT / 'preservation_before.json', dict(files=before,
               raw={r.file: r.sha256 for r in raw.itertuples()}))
    protocol = ('# 14단계 실행 전 고정 계획\n\n' + LIMITATION + '\n\n' +
                '정확한 공식·보호 기준·결측 클래스·경계값·재사용·중단 규칙은 아래 JSON과 동일함.\n\n' +
                '```json\n' + json.dumps(plan, ensure_ascii=False, indent=2) + '\n```\n')
    (OUT / 'protocol.md').write_text(protocol, encoding='utf-8')
    write_json(OUT / 'plan_lock.json', {'plan_sha256': sha(OUT / 'experiment_plan.json'),
                                      'protocol_sha256': sha(OUT / 'protocol.md')})
    print('Protocol frozen:', OUT, flush=True)


# 과거 기준 모델의 정확한 학습 조건 검증 후 재사용
def reuse_baseline(fold, train):
    old = ROOT / 'outputs/temporal_robustness'
    records = json.loads((old / 'fit_records.json').read_text(encoding='utf-8'))
    record = next(r for r in records if r['config_id'] == 'SVM_all' and r['fold'] == fold)
    path = ROOT / record['model_file']
    assert sha(path) == record['sha256']
    assert record['train_n'] == len(train)
    assert record['train_row_ids_sha256'] == row_digest(train.row_id)
    original = joblib.load(path)
    assert np.array_equal(original.named_steps['selector'].selected_indices_, np.arange(128))
    model = Pipeline([(k, copy.deepcopy(original.named_steps[k]))
                      for k in ['imputer', 'scaler', 'classifier']])
    values = train[FEATURES]
    np.testing.assert_allclose(model['imputer'].statistics_, values.median())
    filled = model['imputer'].transform(values)
    np.testing.assert_allclose(model['scaler'].mean_, filled.mean(axis=0), rtol=1e-10)
    np.testing.assert_allclose(model['scaler'].var_, filled.var(axis=0), rtol=1e-10)
    assert model['scaler'].n_samples_seen_ == len(train)
    for key, expected in build_pipeline('baseline')['classifier'].get_params().items():
        assert model['classifier'].get_params()[key] == expected, key
    np.testing.assert_array_equal(model['classifier'].classes_, list(GASES))
    return model, record


# 실제 존재하는 정답 클래스의 지표·오분류 방향 계산
def score_predictions(y, predicted):
    y, predicted = np.asarray(y), np.asarray(predicted)
    precision, recall, f1, support = precision_recall_fscore_support(
        y, predicted, labels=list(GASES), zero_division=0)
    classes = pd.DataFrame(dict(gas_id=list(GASES), gas=list(GASES.values()),
                                precision=precision, recall=recall, f1=f1, support=support))
    classes['predicted_n'] = [(predicted == g).sum() for g in GASES]
    classes['predicted_fraction'] = classes.predicted_n / len(y)
    classes.loc[classes.support == 0, ['precision', 'recall', 'f1']] = np.nan
    matrix = confusion_matrix(y, predicted, labels=list(GASES))
    for i, g in enumerate(GASES):
        wrong = matrix[i].copy()
        wrong[i] = 0
        classes.loc[i, 'main_wrong_gas'] = GASES[int(np.argmax(wrong)) + 1] if wrong.sum() else ''
        classes.loc[i, 'main_wrong_n'] = wrong.max()
    valid = classes[classes.support > 0]
    metrics = dict(n=len(y), accuracy=accuracy_score(y, predicted),
                   macro_f1=f1_score(y, predicted, labels=valid.gas_id.tolist(), average='macro', zero_division=0),
                   weighted_f1=f1_score(y, predicted, average='weighted', zero_division=0),
                   min_recall=float(valid.recall.min()), zero_recall=int(valid.recall.eq(0).sum()),
                   toluene_to_acetaldehyde=int(matrix[5, 3]),
                   acetaldehyde_to_toluene=int(matrix[3, 5]))
    return metrics, classes, matrix


# 사전 수치 기준으로 균형 개선 판정
def judge(metrics, classes):
    baseline = classes[classes.method == 'baseline'].set_index(['fold', 'gas_id'])
    summary, guard_rows = [], []
    for method in METHODS:
        sub = metrics[(metrics.method == method) & (metrics.status == 'ok')]
        gas = classes[classes.method == method].set_index(['fold', 'gas_id'])
        paired = gas[['precision', 'recall', 'f1']].join(
            baseline[['precision', 'recall', 'f1']], rsuffix='_base')
        mean_recall_delta = (paired.recall - paired.recall_base).groupby('gas_id').mean()
        other_delta = (paired.f1 - paired.f1_base).loc[
            paired.index.get_level_values('gas_id').isin([1, 2, 3, 5])].groupby('gas_id').mean().mean()
        baseline_macro = metrics[(metrics.method == 'baseline') & (metrics.status == 'ok')].macro_f1.mean()
        gain = sub.macro_f1.mean() - baseline_macro
        new_zero = int(((paired.recall_base > 0) & paired.recall.eq(0)).sum())
        zero = int(gas.recall.eq(0).sum())
        complete = len(sub) == 3 and len(paired) == 18
        checks = dict(complete=complete, macro_guard=bool(gain >= .005 - 1e-12),
                      gas_recall_guard=bool(len(mean_recall_delta) == 6 and
                                            (mean_recall_delta >= -.05 - 1e-12).all()),
                      other_four_guard=bool(other_delta >= -.02 - 1e-12),
                      zero_count_guard=zero <= int(baseline.recall.eq(0).sum()),
                      no_new_zero_guard=new_zero == 0)
        passed = all(checks.values())
        positive = gain > 1e-12 or bool(((paired[['precision', 'recall', 'f1']].to_numpy() -
                                        paired[['precision_base', 'recall_base', 'f1_base']].to_numpy()) > 1e-12).any())
        conclusion = 'A' if passed else ('B' if positive else 'C')
        summary.append(dict(method=method, mean_macro_f1=sub.macro_f1.mean(),
                            fold_sd=sub.macro_f1.std(ddof=0), mean_accuracy=sub.accuracy.mean(),
                            mean_weighted_f1=sub.weighted_f1.mean(), macro_delta=gain,
                            zero_pairs=zero, min_recall=gas.recall.min(),
                            other_four_f1=gas[gas.index.get_level_values('gas_id').isin([1, 2, 3, 5])].f1.mean(),
                            new_zero_pairs=new_zero, balanced_success=passed,
                            conclusion='reference' if method == 'baseline' else conclusion))
        guard_rows.append(dict(method=method, **checks, macro_delta=gain,
                               worst_mean_gas_recall_delta=mean_recall_delta.min(),
                               other_four_f1_delta=other_delta, balanced_success=passed))
    return pd.DataFrame(summary), pd.DataFrame(guard_rows)


# 보존 지문과 실행 전 계획 잠금 검사
def verify_preservation():
    before = json.loads((OUT / 'preservation_before.json').read_text(encoding='utf-8'))
    rows = [dict(kind='project', path=name, expected=value,
                 actual=sha(ROOT / name) if (ROOT / name).is_file() else 'MISSING')
            for name, value in before['files'].items()]
    raw_dir = Path(read_config()['data_dir'])
    rows.extend(dict(kind='raw', path=name, expected=value, actual=sha(raw_dir / name))
                for name, value in before['raw'].items())
    audit = save('preservation_audit', rows)
    assert audit.expected.eq(audit.actual).all(), 'Existing file changed'
    lock = json.loads((OUT / 'plan_lock.json').read_text(encoding='utf-8'))
    assert sha(OUT / 'experiment_plan.json') == lock['plan_sha256']
    assert sha(OUT / 'protocol.md') == lock['protocol_sha256']
    return dict(existing_files=len(before['files']), raw_files=len(before['raw']),
                all_preserved=True, plan_unchanged=True)


# 9개 파이프라인만 평가하고 신규 변환 모델 저장
def run():
    if (OUT / 'run_started.json').exists():
        raise FileExistsError('Run already started; refuse duplicate training')
    verify_preservation()
    write_json(OUT / 'run_started.json', dict(started_at=now()))
    plan = json.loads((OUT / 'experiment_plan.json').read_text(encoding='utf-8'))
    frame, _ = load_dataset(read_config())
    frame = frame[frame.batch <= 8].copy()
    assignments, _ = validate_splits(frame)
    assert assignments.equals(pd.read_csv(OUT / 'split_assignments.csv'))
    old_predictions = pd.read_csv(ROOT / 'outputs/temporal_robustness/fold_predictions.csv.gz')
    metrics, class_rows, confusion_rows, predictions = [], [], [], []
    registry, stats, audits, failures = [], [], [], []
    with threadpool_limits(limits=1):
        for fold, (end, batch) in FOLDS.items():
            train, validation = frame[frame.batch <= end], frame[frame.batch == batch]
            for method in METHODS:
                started = now()
                fit_seconds = 0.
                print(f'{fold} {method}: Train={len(train)}, Validation={len(validation)}', flush=True)
                try:
                    if method == 'baseline':
                        model, source = reuse_baseline(fold, train)
                    else:
                        model = build_pipeline(method)
                        tick = time.perf_counter()
                        model.fit(train[FEATURES], train.gas)
                        fit_seconds = time.perf_counter() - tick
                    tick = time.perf_counter()
                    predicted = model.predict(validation[FEATURES])
                    predict_seconds = time.perf_counter() - tick
                    if method == 'baseline':
                        old = old_predictions[(old_predictions.config_id == 'SVM_all') &
                                              (old_predictions.fold == fold)].set_index('row_id')
                        np.testing.assert_array_equal(predicted, old.loc[validation.row_id, 'y_pred'])
                    path = MODEL_DIR / f'{fold}_{method}.joblib'
                    joblib.dump(model, path)
                    np.testing.assert_array_equal(joblib.load(path).predict(validation[FEATURES]), predicted)
                    row, gas_table, matrix = score_predictions(validation.gas, predicted)
                    metrics.append(dict(fold=fold, method=method, batch=batch, status='ok',
                                        fit_seconds=fit_seconds, predict_seconds=predict_seconds, **row))
                    class_rows.extend(gas_table.assign(fold=fold, method=method, batch=batch).to_dict('records'))
                    confusion_rows.extend(dict(fold=fold, method=method, batch=batch,
                                               true_gas=g, predicted_gas=h, n=int(matrix[g-1, h-1]))
                                          for g in GASES for h in GASES)
                    predictions.extend(dict(fold=fold, method=method, batch=batch, row_id=r,
                                            y_true=int(y), y_pred=int(p)) for r, y, p in
                                       zip(validation.row_id, validation.gas, predicted))
                    raw = model['imputer'].transform(train[FEATURES])
                    transformed = model['transform'].transform(raw) if method != 'baseline' else raw
                    scaler = model['scaler']
                    np.testing.assert_allclose(scaler.mean_, transformed.mean(axis=0), rtol=1e-9, atol=1e-10)
                    np.testing.assert_allclose(scaler.var_, transformed.var(axis=0), rtol=1e-9)
                    transform = model.named_steps.get('transform')
                    for j, feature in enumerate(FEATURES):
                        stats.append(dict(fold=fold, method=method, feature=feature,
                                          imputer_median=model['imputer'].statistics_[j],
                                          transform_scale=transform.scale_[j] if transform else np.nan,
                                          transform_lambda=transform.lambdas_[j] if transform else np.nan,
                                          transform_status=transform.status_[j] if transform else 'identity',
                                          scaler_mean=scaler.mean_[j], scaler_var=scaler.var_[j],
                                          scaler_scale=scaler.scale_[j]))
                    audits.append(dict(fold=fold, method=method, train_n=len(train),
                                       train_row_sha256=row_digest(train.row_id),
                                       validation_row_sha256=row_digest(validation.row_id),
                                       feature_order_sha256=row_digest(FEATURES),
                                       imputed_train_sha256=digest(raw),
                                       transform_fit_sha256=transform.fit_input_sha256_ if transform else digest(raw),
                                       scaler_train_n=int(scaler.n_samples_seen_),
                                       transformed_train_sha256=digest(transformed),
                                       actual_gamma=float(model['classifier']._gamma),
                                       train_only=True, predictions_reloaded_equal=True))
                    registry.append(dict(fold=fold, method=method, path=str(path.relative_to(ROOT)),
                                         sha256=sha(path), new_fit=method != 'baseline',
                                         source_path=source['model_file'] if method == 'baseline' else '',
                                         source_sha256=source['sha256'] if method == 'baseline' else '',
                                         fit_started_at=started, fit_seconds=fit_seconds,
                                         historical_fit_seconds=source.get('fit_seconds', 0.) if method == 'baseline' else fit_seconds))
                except Exception as exc:
                    if method == 'baseline' or isinstance(exc, AssertionError):
                        raise
                    failures.append(dict(fold=fold, method=method, error=repr(exc)))
                    metrics.append(dict(fold=fold, method=method, batch=batch, status='failed'))
                    print('Candidate failed without replacement:', repr(exc), flush=True)
    tables = {}
    for name, rows in [('fold_metrics', metrics), ('class_metrics', class_rows),
                       ('confusion', confusion_rows), ('predictions', predictions),
                       ('model_registry', registry), ('preprocessing_statistics', stats),
                       ('train_only_audit', audits)]:
        tables[name] = save(name, rows)
    write_json(OUT / 'failures.json', failures)
    summary, guards = judge(tables['fold_metrics'], tables['class_metrics'])
    save('summary', summary)
    save('protection_checks', guards)
    successful = summary[summary.balanced_success & summary.method.ne('baseline')]
    near_best = successful[successful.mean_macro_f1 >=
                           successful.mean_macro_f1.max() - 1e-12]
    candidates = near_best.sort_values(['zero_pairs', 'min_recall', 'method'],
                                      ascending=[True, False, True])
    conclusion = 'A' if len(candidates) else ('B' if summary.conclusion.eq('B').any() else 'C')
    write_json(OUT / 'selection_frozen.json', dict(
        selected_candidate=candidates.method.iloc[0] if len(candidates) else None,
        conclusion=conclusion, official_model='Model A unchanged',
        pipeline_evaluations=9, new_classifier_fits=sum(r['new_fit'] for r in registry),
        reused_classifier_fits=sum(not r['new_fit'] for r in registry),
        frozen_at=now(), future_batches_evaluated=[], limitation=LIMITATION,
    ))
    render(frame, tables)
    verification = verify_preservation()
    verification.update(completed_at=now(), experiment_plan_sha256=sha(OUT / 'experiment_plan.json'))
    write_json(OUT / 'final_verification.json', verification)
    print(summary.to_string(index=False), flush=True)


# 표·그림을 포함하는 UTF-8 보고서 작성
def render(frame=None, tables=None):
    summary = pd.read_csv(OUT / 'summary.csv')
    metrics = pd.read_csv(OUT / 'fold_metrics.csv')
    classes = pd.read_csv(OUT / 'class_metrics.csv')
    guards = pd.read_csv(OUT / 'protection_checks.csv')
    confusion = pd.read_csv(OUT / 'confusion.csv')
    selection = json.loads((OUT / 'selection_frozen.json').read_text(encoding='utf-8'))
    plt.rcParams.update({'font.family': 'Malgun Gothic', 'axes.unicode_minus': False})
    figures = []

    def finish(name, title, fig):
        fig.suptitle(title)
        fig.tight_layout()
        path = OUT / f'{name}.png'
        fig.savefig(path, dpi=150)
        plt.close(fig)
        figures.append((title, path))

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(summary.method, summary.mean_macro_f1 * 100)
    ax.set(xlabel='특징 변환 조건', ylabel='Fold 동일 가중 평균 Macro F1 (%)', ylim=(0, 100))
    for i, row in summary.iterrows():
        ax.text(i, row.mean_macro_f1 * 100 + 1, f'{row.mean_macro_f1*100:.2f}%', ha='center')
    finish('mean_macro_f1', '과거 개발 Fold A~C 평균 Macro F1', fig)
    fig, ax = plt.subplots(figsize=(9, 4))
    for method in METHODS:
        sub = metrics[(metrics.method == method) & metrics.status.eq('ok')]
        ax.plot(sub.fold + ' / Batch ' + sub.batch.astype(str), sub.macro_f1 * 100,
                marker='o', label=method)
    ax.set(xlabel='Fold / Validation Batch', ylabel='Macro F1 (%)', ylim=(0, 100))
    ax.legend()
    finish('fold_macro_f1', '시간순 Validation 성능', fig)
    for delta in [False, True]:
        pivot = classes.pivot(index=['method', 'fold'], columns='gas', values='recall')
        pivot = pivot.reindex(pd.MultiIndex.from_product([METHODS, list(FOLDS)]))
        if delta:
            pivot = pivot - pd.concat([pivot.loc['baseline']] * 3, keys=METHODS)
        fig, ax = plt.subplots(figsize=(10, 6))
        im = ax.imshow(pivot.to_numpy()*100, aspect='auto', cmap='RdBu_r' if delta else 'viridis',
                       vmin=-100 if delta else 0, vmax=100)
        ax.set_xticks(range(6), pivot.columns, rotation=25, ha='right')
        ax.set_yticks(range(9), [f'{m} / {f} (Batch {FOLDS[f][1]})' for m, f in pivot.index])
        ax.set(xlabel='실제 가스', ylabel='특징 변환 / Validation Fold')
        for i in range(9):
            for j in range(6):
                ax.text(j, i, f'{pivot.iloc[i,j]*100:.1f}', ha='center', va='center', fontsize=8)
        fig.colorbar(im, ax=ax, label='Recall 증감 (%p)' if delta else 'Recall (%)')
        finish('recall_delta' if delta else 'recall_heatmap',
               '기준 대비 가스 Recall 증감' if delta else '6종 가스 Recall', fig)
    focus = classes[classes.gas_id.isin([4, 6])].groupby(['method', 'gas'])[['precision', 'recall', 'f1']].mean()
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for ax, gas in zip(axes, ['Toluene', 'Acetaldehyde']):
        focus.xs(gas, level='gas').reindex(METHODS).mul(100).plot.bar(ax=ax)
        ax.set(title=gas, xlabel='변환 조건', ylabel='Fold 동일 가중 평균 (%)', ylim=(0, 100))
        ax.tick_params(axis='x', rotation=15)
    finish('focus_precision_recall_f1', 'Toluene·Acetaldehyde P/R/F1', fig)
    directions = metrics.groupby('method')[['toluene_to_acetaldehyde', 'acetaldehyde_to_toluene']].sum().reindex(METHODS)
    fig, ax = plt.subplots(figsize=(10, 4))
    directions.plot.bar(ax=ax)
    ax.set(xlabel='변환 조건', ylabel='Fold 6·7·8 오분류 표본 수 합계')
    ax.tick_params(axis='x', rotation=0)
    finish('directional_errors', 'Toluene ↔ Acetaldehyde 오분류 방향', fig)
    fig, axes = plt.subplots(3, 3, figsize=(16, 15))
    for i, method in enumerate(METHODS):
        for j, fold in enumerate(FOLDS):
            ax = axes[i, j]
            sub = confusion[(confusion.method == method) & (confusion.fold == fold)]
            if sub.empty:
                ax.set_title(f'{method} / {fold}: failed')
                continue
            matrix = sub.pivot(index='true_gas', columns='predicted_gas', values='n').to_numpy()
            ax.imshow(matrix, cmap='Blues')
            ax.set(title=f'{method} / {fold}: Batch {FOLDS[fold][1]}',
                   xlabel='예측 가스 (클래스 번호)', ylabel='실제 가스 (클래스 번호)')
            ax.set_xticks(range(6), list(GASES))
            ax.set_yticks(range(6), list(GASES))
            for a in range(6):
                for b in range(6):
                    ax.text(b, a, str(matrix[a,b]), ha='center', va='center', fontsize=8,
                            color='white' if matrix[a,b] > matrix.max()/2 else 'black')
    finish('confusion_matrices', '조건·Fold별 Confusion Matrix (표본 수)', fig)
    # 특징 예시는 Fold A Train 왜도가 큰 순서로만 선정
    if frame is None:
        frame, _ = load_dataset(read_config())
        frame = frame[frame.batch <= 8].copy()
    train = frame[frame.batch <= 3]
    values = train[FEATURES].to_numpy()
    std = np.std(values, axis=0)
    skew = np.abs(np.mean(((values-values.mean(axis=0))/np.where(std == 0, 1, std))**3, axis=0))
    selected = np.argsort(-skew, kind='stable')[:3]
    distribution = []
    fig, axes = plt.subplots(3, 3, figsize=(14, 10))
    for i, j in enumerate(selected):
        for k, method in enumerate(METHODS):
            path = MODEL_DIR / f'A_{method}.joblib'
            ax = axes[i, k]
            if not path.exists():
                continue
            model = joblib.load(path)
            filled = model['imputer'].transform(train[FEATURES])
            transformed = model['transform'].transform(filled) if method != 'baseline' else filled
            ax.hist(transformed[:, j], bins=40)
            ax.set(title=f'{FEATURES[j]} / {method}', xlabel='표준화 전 변환 특징값', ylabel='Train 표본 수')
            distribution.append(dict(feature=FEATURES[j], method=method, train_n=len(train),
                                     train_abs_skew=skew[j], minimum=transformed[:,j].min(),
                                     median=np.median(transformed[:,j]), maximum=transformed[:,j].max()))
    save('distribution_examples', distribution)
    finish('train_distributions', 'Fold A Train1~3 특징 분포 — 미래 자료 미사용', fig)
    save('graph_manifest', [dict(title=t, path=str(p.relative_to(ROOT)), sha256=sha(p)) for t, p in figures])
    means = classes.groupby(['method', 'gas'])[['precision', 'recall', 'f1']].mean().reset_index()
    save('mean_class_metrics', means)
    code = selection['conclusion']
    conclusion_text = {'A': '균형 개선 근거 관찰', 'B': '부분 개선', 'C': '개선 근거 부족'}[code]
    summary_text = (f'# 14단계 비선형 특징 변환 요약\n\n{LIMITATION}\n\n'
                    f'연구 결론: **{code} — {conclusion_text}**\n\n'
                    f'파이프라인 평가 9건, 신규 학습 {selection["new_classifier_fits"]}건, '
                    f'기준 모델 재사용 {selection["reused_classifier_fits"]}건. '
                    '기준 파이프라인은 Stage8의 항등 특징 선택 단계를 제거하여 재사용하고 '
                    '기존 Validation 예측과 전부 일치하는지 확인함.\n\n'
                    f'```text\n{summary.to_string(index=False)}\n```\n\n'
                    f'```text\n{metrics.to_string(index=False)}\n```\n\n'
                    f'```text\n{means.to_string(index=False)}\n```\n\n'
                    '점수 차이는 이 개발 Fold에서 계산한 사실임. 비선형 거리 변화가 도움이 되는지는 '
                    '관찰 가능하나 센서 드리프트의 인과 효과나 독립 미래 성능을 입증하지 못함.\n')
    limitations = ('# 14단계 연구 한계\n\n' + LIMITATION + '\n\n'
                   '- 6종 가스의 균형 개선은 모든 사전 보호 조건 통과로만 판정함.\n'
                   '- Fold A Toluene 학습 79개, Fold C Validation Toluene 18개. 작은 support의 불확실성 존재.\n'
                   '- 겹치는 학습 구간과 반복 사용한 Validation으로 선택 편향 존재. 독립 미래 CI·통계적 유의성 미주장.\n'
                   '- C와 gamma 정책은 고정하되 실제 gamma 및 거리 구조는 각각 기록.\n'
                   '- Train 수치 오류의 특징별 항등 처리와 상수 특징은 통계 CSV에 공개. 평가 오류는 조건 실패로 기록.\n'
                   '- 농도·환경·세션 정보 부족으로 드리프트 단독 원인 확정 불가.\n'
                   '- 학습 시간은 재사용 기준의 이번 학습 0초와 과거 시간을 구분. 실행 환경에 따른 시간 변동 존재.\n'
                   '- 기존 테스트 5개 실패는 변경하지 않음. 과거 보존 기록과 전역 모델 목록 충돌을 신규 결함과 구분.\n'
                   '- 추가 튜닝·앙상블·미래 Batch 신규 평가·공식 모델 교체 없음.\n')
    (ROOT / 'reports' / REPORT_NAMES[1]).write_text(summary_text, encoding='utf-8')
    (ROOT / 'reports' / REPORT_NAMES[2]).write_text(limitations, encoding='utf-8')
    sections = []
    def section(title, body):
        sections.append(f'<h2>{html.escape(title)}</h2>{body}')
    section('1. 연구 목적과 사전 고정 조건', '<p>학습 행과 SVM을 고정하고 특징 변환만 비교. '
            '12~13단계 부분표본 구성 및 8단계 특징 선택과 다른 대조.</p><p>' + LIMITATION + '</p>')
    section('2. 분할과 클래스 표본 수', pd.read_csv(OUT/'fold_support.csv').to_html(index=False))
    section('3. 파이프라인·수치 안정성', '<p>baseline / signed_log / yeo_johnson만 사용. '
            '전처리·변환 Fit은 Train만 사용. 계획 고정 후 조건 변경 없음.</p><pre>' +
            html.escape((OUT/'experiment_plan.json').read_text(encoding='utf-8')) + '</pre>')
    section('4. 계산된 평균 및 Fold별 성능', summary.to_html(index=False, float_format=lambda v:f'{v:.6f}') +
            metrics.to_html(index=False, float_format=lambda v:f'{v:.6f}'))
    section('5. 6종 가스 Precision·Recall·F1', means.to_html(index=False) + classes.to_html(index=False))
    section('6. 사전 보호 조건과 연구 결론', f'<p>{code} — {conclusion_text}. 공식 Model A 유지.</p>' + guards.to_html(index=False))
    image_blocks = ''.join('<figure><img alt="'+html.escape(t)+'" src="data:image/png;base64,'+
                           base64.b64encode(p.read_bytes()).decode('ascii')+'"><figcaption>'+html.escape(t)+
                           '</figcaption></figure>' for t, p in figures)
    section('7. 성능·오분류·Train 분포 시각화', '<p>가스 번호: '+html.escape(str(GASES))+'</p>'+image_blocks)
    section('8. 전처리·gamma·실행 비용', pd.read_csv(OUT/'train_only_audit.csv').to_html(index=False)+
            pd.read_csv(OUT/'model_registry.csv').to_html(index=False))
    section('9. 관찰과 해석·한계', '<pre>'+html.escape(limitations)+'</pre><p>보호 조건 통과는 '
            '개발 Fold의 기술적 근거이며 센서 드리프트 보정 성공 또는 미래 일반화 보증이 아님.</p>')
    test_path = OUT / 'test_summary.json'
    section('10. 보존과 테스트', '<p>기존 원본·모델·코드·보고서 SHA-256은 preservation_audit.csv 참조. '
            'Commit·Push 없음.</p><pre>'+html.escape(test_path.read_text(encoding='utf-8') if test_path.exists()
            else '전체 테스트 실행 전. 완료 후 동일 결과로 보고서 갱신 예정.')+'</pre>')
    document = ('<!doctype html><html lang="ko"><meta charset="utf-8"><title>14단계 비선형 특징 변환</title>'
                '<style>body{font-family:Malgun Gothic,sans-serif;margin:32px;color:#172536}table{border-collapse:collapse;'
                'display:block;overflow:auto;font-size:13px}td,th{border:1px solid #bbc;padding:6px}'
                'img{max-width:100%;height:auto}pre{white-space:pre-wrap;overflow-wrap:anywhere}'
                'h2{margin-top:38px}figure{margin:24px 0}</style><body><h1>비선형 특징 변환 시간순 비교</h1>'+
                ''.join(sections)+'</body></html>')
    (ROOT/'reports'/REPORT_NAMES[0]).write_text(document, encoding='utf-8')


# 명령별 계획 고정·학습·보고서 갱신 분리
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['freeze', 'run', 'report'])
    args = parser.parse_args()
    if args.action == 'freeze':
        freeze()
    elif args.action == 'run':
        run()
    else:
        render()
        write_json(OUT/'final_verification.json', {**verify_preservation(), 'checked_at': now()})


if __name__ == '__main__':
    # 모듈 실행 때도 저장 클래스의 정식 import 경로 유지
    import sys
    sys.modules['src.nonlinear_feature_transformation'] = sys.modules[__name__]
    TrainTransform.__module__ = 'src.nonlinear_feature_transformation'
    main()
