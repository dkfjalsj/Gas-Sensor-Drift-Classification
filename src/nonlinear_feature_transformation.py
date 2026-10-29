# 비선형 특징 변환과 고정 SVM의 시간순 성능 비교
# 실행 전 계획 고정 및 기존 자료 보존 검사

import hashlib
import warnings

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.metrics import precision_recall_fscore_support
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PowerTransformer, StandardScaler
from sklearn.svm import SVC

from .data import ROOT, FEATURES, GASES

OUT = ROOT / 'outputs/nonlinear_feature_transformation'
MODEL_DIR = ROOT / 'models/nonlinear_feature_transformation'
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


# 과거 기준 모델의 정확한 학습 조건 검증 후 재사용


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


# 9개 파이프라인만 평가하고 신규 변환 모델 저장


# 표·그림을 포함하는 UTF-8 보고서 작성


# 명령별 계획 고정·학습·보고서 갱신 분리


