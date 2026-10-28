# 검증된 원본·분리 계획·지문을 불변 데이터셋 버전으로 저장
# 재학습과 모델 승인은 후속 단계에서 별도 수행

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import uuid

from ..data import FEATURES
from .data_preparation import (
    LOCAL_ROOT, POLICY, inspect_candidate, load_training_reference,
)


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


# 입력·출처·고정 정책으로 동일 등록의 버전 결정
def identity(payload, session_payload, source, truth_method):
    value = {"input_sha256": digest(payload), "sessions_sha256": digest(session_payload or b""),
             "source": source.strip(), "truth_method": truth_method.strip(), "policy": POLICY}
    token = digest(json.dumps(value, sort_keys=True, ensure_ascii=False).encode())
    return "dataset_" + token[:24], value


# 저장 파일의 지문과 원본 추적 정보 확인
def read_manifest(directory):
    directory = Path(directory)
    if directory.is_symlink():
        raise ValueError("연결된 외부 데이터셋 경로는 허용하지 않습니다.")
    payload = (directory / "manifest.json").read_bytes()
    if digest(payload) != (directory / "manifest.sha256").read_text(encoding="ascii").strip():
        raise ValueError("저장 메타데이터 지문이 달라 확인이 필요합니다.")
    manifest = json.loads(payload.decode("utf-8"))
    expected = {"original.csv", "sessions_original.csv", "sessions.csv", "assignments.csv", "train.csv", "validation.csv"}
    if set(manifest["files"]) != expected or manifest["dataset_id"] != directory.name:
        raise ValueError("저장된 데이터셋 구조 또는 버전이 달라 확인이 필요합니다.")
    for name, expected_sha in manifest["files"].items():
        path = directory / name
        if path.is_symlink() or digest(path.read_bytes()) != expected_sha:
            raise ValueError("저장된 데이터셋 파일 지문이 다릅니다: " + name)
    return manifest


# 과거 검증 행과 세션을 새 학습 자료로 재사용하지 않도록 차단
def check_reservations(check, dataset_id, source, storage=LOCAL_ROOT):
    import pandas as pd

    storage = Path(storage)
    errors = []
    if not check.ready:
        return errors
    train = check.assignments[check.assignments.partition.eq("train")]
    for directory in sorted((storage / "datasets").glob("dataset_*")):
        manifest = read_manifest(directory)
        if directory.name == dataset_id:
            continue
        assignments = pd.read_csv(directory / "assignments.csv", dtype={"session_id": str})
        reserved = assignments[assignments.partition.eq("validation")]
        if set(train.near_feature_sha256) & set(reserved.near_feature_sha256):
            errors.append("과거 등록에서 검증용으로 예약한 행이 신규 학습에 포함됩니다: " + directory.name)
        if manifest["provenance"]["source"] == source.strip() and set(train.session_id) & set(reserved.session_id):
            errors.append("과거 검증 세션을 신규 학습으로 재사용할 수 없습니다: " + directory.name)
    return errors


# 저장 직전 품질·출처·기존 학습 중복을 다시 확인
def register_dataset(payload, session_payload, filename, source, truth_method,
                     confirmed, warnings_accepted, storage=LOCAL_ROOT):
    storage = Path(storage)
    reference = load_training_reference()
    check = inspect_candidate(payload, session_payload, source, truth_method, confirmed, reference)
    if not check.ready:
        raise ValueError("데이터 준비 조건 미충족: " + " / ".join(check.errors + check.holds))
    if check.warnings and not warnings_accepted:
        raise ValueError("품질 경고를 확인하고 승인해야 합니다.")
    dataset_id, provenance = identity(payload, session_payload, source, truth_method)
    destination = storage / "datasets" / dataset_id
    if destination.exists():
        return read_manifest(destination), False
    storage.mkdir(parents=True, exist_ok=True)
    # 같은 저장소의 동시 등록은 하나만 허용
    lock = storage / "registration.lock"
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise ValueError("다른 데이터 등록이 진행 중이거나 잠금이 남았습니다. 관리자 확인이 필요합니다.") from exc
    try:
        os.close(descriptor)
        if destination.exists():
            return read_manifest(destination), False
        errors = check_reservations(check, dataset_id, source, storage)
        if errors:
            raise ValueError(" / ".join(errors))
        staging = storage / (".staging_" + uuid.uuid4().hex)
        staging.mkdir()
        (staging / "original.csv").write_bytes(payload)
        (staging / "sessions_original.csv").write_bytes(session_payload)
        check.sessions.to_csv(staging / "sessions.csv", index=False, encoding="utf-8-sig")
        check.assignments.to_csv(staging / "assignments.csv", index=False, encoding="utf-8-sig")
        data = check.data.features.copy()
        data["gas"] = check.data.truth
        for part in ["train", "validation"]:
            selected = check.assignments.partition.eq(part)
            data.loc[selected, [*FEATURES, "gas"]].to_csv(
                staging / (part + ".csv"), index=False, encoding="utf-8-sig")
        files = {path.name: digest(path.read_bytes()) for path in staging.iterdir()}
        assignments = check.assignments
        manifest = {
            "schema_version": 1, "dataset_id": dataset_id, "dataset_version": dataset_id,
            "registered_at_utc": datetime.now(timezone.utc).isoformat(),
            "original_filename": PureWindowsPath(filename).name,
            "original_sha256": check.data.digest,
            "policy": POLICY, "provenance": provenance,
            "truth_confirmed_by_operator": bool(confirmed), "warnings_accepted": bool(warnings_accepted),
            "quality": check.summary, "warnings": check.warnings,
            "split_rule": "최신 한 세션을 validation, 이전 세션을 train으로 고정",
            "row_order": "원본 input_row 순서를 각 분할에서 유지",
            "reference_files": dict(reference.files), "reference_rows": reference.rows,
            "leakage_checks": {"cross_partition_feature_overlap": 0, "session_overlap": 0,
                               "reference_feature_or_near_overlap": 0, "prior_validation_reuse": False},
            "partition_rows": assignments.partition.value_counts().astype(int).to_dict(),
            "preprocessing_fitted": False, "new_model_fits": 0,
            "independent_final_test": False, "physical_independence_verified": False,
            "duplicate_check_scope": "공식 Train 5933행과 완전·근접·관측된 결측 표본 비교",
            "limits": ["동일·근접 수치와 자기신고 출처만 검사하며 물리적 표본의 독립성을 증명하지 못함",
                       "외부 시험으로 확인한 정답인지 소프트웨어가 보증하지 못함",
                       "검증 자료는 개발용이며 독립 최종 Test로 지정하지 않음"],
            "files": files,
        }
        (staging / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
        (staging / "manifest.sha256").write_text(
            digest((staging / "manifest.json").read_bytes()), encoding="ascii")
        destination.parent.mkdir(exist_ok=True)
        os.rename(staging, destination)
        read_manifest(destination)
        return manifest, True
    finally:
        lock.unlink()
