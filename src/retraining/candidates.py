# 공식 설정을 복제한 후보 학습·동일Validation 비교·불변 저장
# 공식 분류 모델·감지기·데이터셋은 읽기만 수행

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import tempfile
import time
import uuid

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.base import clone
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from threadpoolctl import threadpool_limits

from ..common.hashing import sha256_bytes
from ..data import ROOT, FEATURES, GASES
from ..webapp.data_preparation import LOCAL_ROOT, fingerprints
from ..webapp.dataset_registry import read_manifest
from ..webapp.service import (
    MODEL_PATH, MODEL_SHA, DETECTOR_PATH, DETECTOR_SHA, load_models,
)
from .datasets import load_training_data, official_training_frame
from .evaluation import compare, evaluate_model

STORE = ROOT / 'models/retraining_candidates'
VERSION = 'candidate_svm_v1'
FILES = {
    'model.joblib', 'metrics.csv', 'class_metrics.csv', 'class_changes.csv',
    'confusion.csv', 'predictions.csv', 'roc_auc.csv', 'roc_points.csv',
}


# JSON에서NaN을 숫자로 오해하지 않도록 명시
def json_value(value):
    if isinstance(value, dict):
        return {str(key): json_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [json_value(item) for item in value]
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and not np.isfinite(value):
        return {'special_float': str(value)}
    return value


def json_bytes(value):
    return json.dumps(json_value(value), ensure_ascii=False, indent=2,
                      sort_keys=True, allow_nan=False).encode('utf-8')


# 실제 공식 모델의 단계와 설정만 학습 기준으로 사용
def pipeline_settings(model):
    if not isinstance(model, Pipeline) or [name for name, _ in model.steps] != [
            'imputer', 'scaler', 'classifier']:
        raise ValueError('공식 Pipeline 구조가 다릅니다.')
    if not all(isinstance(step, kind) for (_, step), kind in zip(
            model.steps, [SimpleImputer, StandardScaler, SVC])):
        raise ValueError('공식 전처리·분류기 종류가 다릅니다.')
    if list(model.classes_) != list(GASES) or list(model.feature_names_in_) != FEATURES:
        raise ValueError('공식 특징 순서·가스 매핑이 다릅니다.')
    return {name: step.get_params(deep=False) for name, step in model.steps}


# 모델과 감지기 바이트는 작업 전후 동일해야 함
def verify_official():
    for path, expected in [(MODEL_PATH, MODEL_SHA), (DETECTOR_PATH, DETECTOR_SHA)]:
        if sha256_bytes(path.read_bytes()) != expected:
            raise ValueError('공식 모델 또는 감지기 지문이 다릅니다.')


def candidate_directory(candidate_id, storage=STORE):
    if not re.fullmatch(r'candidate_[a-f0-9]{24}', candidate_id):
        raise ValueError('후보ID 형식이 다릅니다.')
    root = Path(storage)
    path = root / candidate_id
    if path.is_symlink() or path.resolve().parent != root.resolve():
        raise ValueError('외부 연결 후보 경로는 허용하지 않습니다.')
    return path


# 로컬 생성 후보의 메타데이터·모든 파일 지문을 대조
def read_candidate(candidate_id, storage=STORE, load_model=False):
    directory = candidate_directory(candidate_id, storage)
    payload = (directory / 'manifest.json').read_bytes()
    if sha256_bytes(payload) != (directory / 'manifest.sha256').read_text(encoding='ascii').strip():
        raise ValueError('후보 메타데이터 지문이 다릅니다.')
    meta = json.loads(payload)
    if (meta['candidate_id'] != candidate_id or meta['status'] != 'completed_review_only'
            or set(meta['files']) != FILES or meta['official_model_sha256'] != MODEL_SHA):
        raise ValueError('후보 버전·구조·상태가 다릅니다.')
    expected_id = 'candidate_' + sha256_bytes(json_bytes(meta['request']))[:24]
    if (expected_id != candidate_id
            or meta['candidate_model_sha256'] != meta['files']['model.joblib']
            or meta['review']['approval_eligible'] is not False
            or meta['review']['automatic_replacement'] is not False):
        raise ValueError('후보 요청·모델 지문·검토 전용 상태가 다릅니다.')
    for name, expected in meta['files'].items():
        path = directory / name
        if path.is_symlink() or sha256_bytes(path.read_bytes()) != expected:
            raise ValueError('후보 파일 지문이 다릅니다: ' + name)
    result = dict(metadata=meta, directory=directory)
    for name in ['metrics', 'class_metrics', 'class_changes', 'confusion', 'roc_auc', 'roc_points']:
        try:
            result[name] = pd.read_csv(directory / (name + '.csv'))
        except pd.errors.EmptyDataError:
            result[name] = pd.DataFrame()
    if load_model:
        verify_official()
        model = joblib.load(directory / 'model.joblib')
        settings = pipeline_settings(model)
        if json_value(settings) != meta['pipeline_settings']:
            raise ValueError('후보 모델 설정이 기록과 다릅니다.')
        result['model'] = model
    return result


def list_candidates(storage=STORE, dataset_id=None):
    rows = []
    for directory in sorted(Path(storage).glob('candidate_*')):
        try:
            item = read_candidate(directory.name, storage)
            if dataset_id is None or item['metadata']['dataset_id'] == dataset_id:
                rows.append(item)
        except (OSError, ValueError, KeyError) as exc:
            rows.append(dict(error=str(exc), candidate_id=directory.name))
    return rows


# 이번 작업이 만든 비공개 임시 폴더만 정리
def discard_staging(staging, root):
    if staging is None or not staging.exists():
        return
    if staging.resolve().parent != root.resolve() or not staging.name.startswith('.staging_candidate_'):
        raise ValueError('임시 정리 경로 불일치')
    allowed = FILES | {'manifest.json', 'manifest.sha256'}
    for path in staging.iterdir():
        if path.name not in allowed or path.is_symlink() or not path.is_file():
            raise ValueError('알 수 없는 임시 파일은 삭제하지 않습니다.')
        path.unlink()
    staging.rmdir()


# 명시적 요청 한 번에 고정 설정 후보 하나만 학습
def train_candidate(dataset_id, *, feature_contract_confirmed,
                    dataset_storage=LOCAL_ROOT, candidate_storage=STORE,
                    synthetic_only=False, progress=None):
    if feature_contract_confirmed is not True:
        raise ValueError('128개 특징의 정의·순서·단위가 공식 자료와 같음을 확인해야 합니다.')
    root = Path(candidate_storage)
    if root.is_symlink():
        raise ValueError('연결된 후보 저장소는 허용하지 않습니다.')
    root.mkdir(parents=True, exist_ok=True)
    lock = root / 'training.lock'
    token = uuid.uuid4().hex
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise ValueError('다른 후보 학습이 진행 중이거나 잠금 확인이 필요합니다.') from exc
    with os.fdopen(descriptor, 'w', encoding='ascii') as stream:
        stream.write(token)
    staging = None
    try:
        notify = progress or (lambda message: None)
        notify('불변 데이터셋과 기존5933행 재검증')
        data = load_training_data(dataset_id, dataset_storage)
        official = load_models().classifier
        settings = pipeline_settings(official)
        request = dict(version=VERSION, dataset_id=dataset_id,
                       dataset_manifest_sha256=data.manifest_sha,
                       official_model_sha256=MODEL_SHA, pipeline=settings,
                       sklearn_version=sklearn.__version__, synthetic_only=bool(synthetic_only),
                       feature_contract_confirmed=True)
        candidate_id = 'candidate_' + sha256_bytes(json_bytes(request))[:24]
        destination = candidate_directory(candidate_id, root)
        if destination.exists():
            saved = read_candidate(candidate_id, root, load_model=True)
            if saved['metadata']['request'] != json_value(request):
                raise ValueError('후보ID 충돌: 덮어쓰지 않습니다.')
            saved['reused'] = True
            return saved
        base_x, base_y = official_training_frame(data.reference)
        train_x = pd.concat([base_x, data.train_x], ignore_index=True)
        train_y = np.concatenate([base_y, data.train_y])
        if pd.Series(fingerprints(train_x, near=True)).duplicated().any():
            raise ValueError('결합 Train에 중복이 있어 학습을 중단합니다.')
        notify('Train 자료만으로 전처리와 후보SVM 학습')
        candidate = clone(official)
        started = time.perf_counter()
        with threadpool_limits(limits=1):
            candidate.fit(train_x, train_y)
        fit_seconds = time.perf_counter() - started
        if (list(candidate.classes_) != list(GASES)
                or candidate.named_steps['scaler'].n_samples_seen_ != len(train_x)):
            raise ValueError('후보 클래스·전처리 학습 표본 수 불일치')
        notify('동일한 신규Validation에서 기존·후보 모델 비교')
        evaluated, rows = {}, {}
        for label, model in [('official', official), ('candidate', candidate)]:
            started = time.perf_counter()
            with threadpool_limits(limits=1):
                evaluated[label] = evaluate_model(model, data.validation_x, data.validation_y)
            evaluated[label][0]['predict_and_metrics_seconds'] = time.perf_counter() - started
            rows[label] = dict(model=label, **evaluated[label][0])
        review, changes = compare(evaluated['official'][0], evaluated['candidate'][0],
                                  evaluated['official'][1], evaluated['candidate'][1], data.manifest)
        verify_official()
        read_manifest(data.directory)
        if sha256_bytes((data.directory / 'manifest.json').read_bytes()) != data.manifest_sha:
            raise ValueError('학습 중 데이터셋이 변경됐습니다.')
        notify('후보 파일과 재로딩 예측 확인 후 불변 저장')
        staging = Path(tempfile.mkdtemp(prefix='.staging_candidate_', dir=root))
        joblib.dump(candidate, staging / 'model.joblib', compress=3)
        loaded = joblib.load(staging / 'model.joblib')
        np.testing.assert_array_equal(loaded.predict(data.validation_x), evaluated['candidate'][3])
        pd.DataFrame(list(rows.values())).to_csv(staging / 'metrics.csv', index=False, encoding='utf-8-sig')
        changes.to_csv(staging / 'class_changes.csv', index=False, encoding='utf-8-sig')
        classes, matrices, aucs, curves = [], [], [], []
        for label, result in evaluated.items():
            classes.append(result[1].assign(model=label))
            aucs.append(result[4].assign(model=label))
            if not result[5].empty:
                curves.append(result[5].assign(model=label))
            for actual_index, actual in enumerate(GASES):
                for predicted_index, predicted in enumerate(GASES):
                    matrices.append(dict(model=label, actual_gas=actual,
                                         predicted_gas=predicted, n=int(result[2][actual_index, predicted_index])))
        pd.concat(classes).to_csv(staging / 'class_metrics.csv', index=False, encoding='utf-8-sig')
        pd.concat(aucs).to_csv(staging / 'roc_auc.csv', index=False, encoding='utf-8-sig')
        curve_table = (pd.concat(curves) if curves else pd.DataFrame(
            columns=['gas_id', 'fpr', 'tpr', 'threshold', 'threshold_is_infinite', 'model']))
        curve_table.to_csv(staging / 'roc_points.csv', index=False, encoding='utf-8-sig')
        pd.DataFrame(matrices).to_csv(staging / 'confusion.csv', index=False, encoding='utf-8-sig')
        prediction = data.assignments.loc[data.assignments.partition.eq('validation'), ['row_id', 'gas']].copy()
        prediction['official'] = evaluated['official'][3]
        prediction['candidate'] = evaluated['candidate'][3]
        prediction.to_csv(staging / 'predictions.csv', index=False, encoding='utf-8-sig')
        meta = dict(
            schema_version=1, version=VERSION, candidate_id=candidate_id,
            status='completed_review_only', created_at_utc=datetime.now(timezone.utc).isoformat(),
            request=request, dataset_id=dataset_id, dataset_manifest_sha256=data.manifest_sha,
            dataset_file_hashes=data.manifest['files'], dataset_provenance=data.manifest['provenance'],
            dataset_partition_rows=data.manifest['partition_rows'],
            sessions=data.manifest['quality']['sessions'], synthetic_only=bool(synthetic_only),
            official_model_path=str(MODEL_PATH), official_model_sha256=MODEL_SHA,
            detector_sha256=DETECTOR_SHA, pipeline_settings=settings,
            sklearn_version=sklearn.__version__, base_rows=len(base_x), new_train_rows=len(data.train_x),
            fitted_rows=len(train_x), validation_rows=len(data.validation_x),
            train_class_counts=pd.Series(train_y).value_counts().sort_index().to_dict(),
            effective_class_weights=dict(zip(candidate.classes_, candidate.named_steps['classifier'].class_weight_)),
            fit_seconds=fit_seconds, review=review, metrics=rows,
            validation_fitted=False, hyperparameter_search=False, feature_contract_confirmed=True,
            feature_unit_verification='관리자 확인; 물리적 단위·정답·독립성 자동 보증 불가',
            candidate_model_sha256=sha256_bytes((staging / 'model.joblib').read_bytes()),
            prediction_reload_exact=True, warnings=data.warnings,
            preprocessing_audit=dict(fitted_rows=len(train_x), base_batches=[1, 2, 3, 4, 5, 6],
                                     combined_feature_sha256=sha256_bytes(train_x.to_numpy(dtype='<f8').tobytes()),
                                     new_train_row_ids=data.assignments.loc[data.assignments.partition.eq('train'), 'row_id'].tolist(),
                                     validation_row_ids=prediction.row_id.tolist()),
            files={path.name: sha256_bytes(path.read_bytes()) for path in staging.iterdir()},
        )
        (staging / 'manifest.json').write_bytes(json_bytes(meta))
        (staging / 'manifest.sha256').write_text(
            sha256_bytes((staging / 'manifest.json').read_bytes()), encoding='ascii')
        verify_official()
        os.rename(staging, destination)
        staging = None
        saved = read_candidate(candidate_id, root, load_model=True)
        saved['reused'] = False
        return saved
    finally:
        try:
            discard_staging(staging, root)
        finally:
            if lock.exists() and lock.read_text(encoding='ascii') == token:
                lock.unlink()
