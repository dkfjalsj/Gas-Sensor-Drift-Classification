# 불변20-A 원본·세션·분리·저장값을 학습 전에 다시 검증

from dataclasses import dataclass
import io
import re
from pathlib import Path

import numpy as np
import pandas as pd

from ..common.hashing import sha256_bytes
from ..data import FEATURES, GASES
from ..webapp.data_preparation import (
    LOCAL_ROOT, POLICY, fingerprints, inspect_candidate, load_training_reference,
)
from ..webapp.dataset_registry import (
    check_reservations, identity, read_manifest,
)


@dataclass
class TrainingData:
    directory: Path
    manifest: dict
    manifest_sha: str
    reference: object
    train_x: pd.DataFrame
    train_y: np.ndarray
    validation_x: pd.DataFrame
    validation_y: np.ndarray
    assignments: pd.DataFrame
    warnings: list


# 선택한ID만 저장소 안에서 확인
def dataset_directory(dataset_id, storage=LOCAL_ROOT):
    if not re.fullmatch(r'dataset_[0-9a-f]{24}', dataset_id):
        raise ValueError('등록 데이터셋ID 형식이 다릅니다.')
    parent = Path(storage) / 'datasets'
    directory = parent / dataset_id
    if directory.resolve().parent != parent.resolve() or directory.is_symlink():
        raise ValueError('외부 연결 데이터셋은 허용하지 않습니다.')
    if not directory.is_dir():
        raise ValueError('등록된20-A 데이터셋이 없습니다.')
    return directory


# 화면 표시 전 필수 등록 정보 확인
def validate_header(manifest):
    provenance = manifest.get('provenance', {})
    if not all(isinstance(provenance.get(key), str) and provenance[key].strip()
               for key in ['source', 'truth_method']):
        raise ValueError('출처 또는 정답 확인 방법이 없습니다.')
    quality = manifest.get('quality', {})
    if not isinstance(quality.get('sessions'), list) or len(quality['sessions']) < 2:
        raise ValueError('세션 기록이 부족합니다.')


# 선택 화면은 등록 파일을 수정하지 않고 메타데이터만 읽음
def list_datasets(storage=LOCAL_ROOT):
    rows = []
    for directory in sorted((Path(storage) / 'datasets').glob('dataset_*')):
        try:
            dataset_directory(directory.name, storage)
            manifest = read_manifest(directory)
            validate_header(manifest)
            rows.append(dict(dataset_id=directory.name, manifest=manifest, error=None))
        except (OSError, ValueError, KeyError) as exc:
            rows.append(dict(dataset_id=directory.name, manifest=None, error=str(exc)))
    return rows


# 열·행 순서·숫자값을 원본에서 다시 만든 분리 결과와 대조
def same_frame(actual, expected, name):
    try:
        pd.testing.assert_frame_equal(
            actual.reset_index(drop=True), expected.reset_index(drop=True),
            check_dtype=False, check_exact=True,
        )
    except AssertionError as exc:
        raise ValueError(name + ' 저장값이 원본 또는 고정 분리와 다릅니다.') from exc


def read_frame(directory, name, **kwargs):
    return pd.read_csv(directory / name, float_precision='round_trip', **kwargs)


# 기존5933행의 특징과 정답을 검증된 참조에서 복원
def official_training_frame(reference):
    if reference.rows != 5933 or reference.values.shape != (5933, 128):
        raise ValueError('공식 학습 자료5933행을 확인할 수 없습니다.')
    frame = pd.DataFrame(reference.values, columns=FEATURES)
    labels = dict(reference.labeled)
    try:
        target = np.array([labels[key] for key in fingerprints(frame)], dtype=int)
    except KeyError as exc:
        raise ValueError('공식 특징과 가스 정답 대응이 다릅니다.') from exc
    if set(target) != set(GASES):
        raise ValueError('공식 학습 자료에6종 가스가 필요합니다.')
    return frame, target


#20-A 통과 여부만 믿지 않고 동일 정책을 재실행
def load_training_data(dataset_id, storage=LOCAL_ROOT):
    directory = dataset_directory(dataset_id, storage)
    manifest = read_manifest(directory)
    validate_header(manifest)
    original_sha = sha256_bytes((directory / 'manifest.json').read_bytes())
    if (manifest.get('schema_version') != 1 or manifest.get('policy') != POLICY
            or manifest.get('truth_confirmed_by_operator') is not True):
        raise ValueError('20-A 정책 또는 실제 정답 확인 기록이 없습니다.')
    provenance = manifest['provenance']
    source, method = provenance['source'], provenance['truth_method']
    original = (directory / 'original.csv').read_bytes()
    sessions = (directory / 'sessions_original.csv').read_bytes()
    computed_id, computed_provenance = identity(original, sessions, source, method)
    if computed_id != dataset_id or computed_provenance != provenance:
        raise ValueError('데이터셋ID·원본 지문·출처가 일치하지 않습니다.')
    if manifest.get('original_sha256') != sha256_bytes(original):
        raise ValueError('원본 지문 기록이 다릅니다.')
    reference = load_training_reference()
    check = inspect_candidate(original, sessions, source, method, True, reference)
    if not check.ready:
        raise ValueError('20-A 재검증 실패: ' + ' / '.join(check.errors + check.holds))
    if check.warnings and manifest.get('warnings_accepted') is not True:
        raise ValueError('기존 품질 경고 확인 기록이 없습니다.')
    if (manifest.get('quality') != check.summary
            or manifest.get('warnings') != check.warnings
            or manifest.get('preprocessing_fitted') is not False
            or manifest.get('new_model_fits') != 0):
        raise ValueError('20-A 품질·전처리 기록이 원본 재검사와 다릅니다.')
    if check.summary['duplicate_extra'] or pd.Series(
            fingerprints(check.data.features, near=True)).duplicated().any():
        raise ValueError('학습 자료에 중복 또는 매우 가까운 표본이 있어 중단합니다.')
    errors = check_reservations(check, dataset_id, source, storage)
    if errors:
        raise ValueError(' / '.join(errors))
    if (manifest.get('reference_files') != dict(reference.files)
            or manifest.get('reference_rows') != reference.rows):
        raise ValueError('기존 학습 자료 검사 범위 기록이 다릅니다.')
    if manifest.get('partition_rows') != check.assignments.partition.value_counts().to_dict():
        raise ValueError('Train·Validation 표본 수 기록이 다릅니다.')
    same_frame(read_frame(directory, 'sessions.csv', dtype={'session_id': str}),
               check.sessions, '세션')
    same_frame(read_frame(directory, 'assignments.csv', dtype={'session_id': str}),
               check.assignments, '분리')
    full = check.data.features.copy()
    full['gas'] = check.data.truth
    parts = {}
    for part in ['train', 'validation']:
        expected = full.loc[check.assignments.partition.eq(part)]
        stored = read_frame(directory, part + '.csv')
        if list(stored.columns) != [*FEATURES, 'gas']:
            raise ValueError('입력 특징·정답 열 또는 순서가 다릅니다.')
        same_frame(stored, expected, part)
        if set(stored.gas) != set(GASES):
            raise ValueError(part + '에6종 가스가 필요합니다.')
        parts[part] = stored
    if sha256_bytes((directory / 'manifest.json').read_bytes()) != original_sha:
        raise ValueError('검사 중 데이터셋이 변경됐습니다.')
    return TrainingData(
        directory, manifest, original_sha, reference,
        parts['train'][FEATURES], parts['train'].gas.to_numpy(dtype=int),
        parts['validation'][FEATURES], parts['validation'].gas.to_numpy(dtype=int),
        check.assignments, check.warnings,
    )
