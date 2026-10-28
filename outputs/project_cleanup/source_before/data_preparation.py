# 신규 정답 데이터의 품질·출처·시간순 분리 조건 검사
# 모델 학습과 전처리 통계 계산 없이 원본 값만 준비

import csv
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re

import numpy as np
import pandas as pd

from ..data import ROOT, FEATURES, GASES, parse_line, read_config
from .service import MODEL_PATH, MODEL_SHA, MAX_BYTES, InputError, read_upload

POLICY = "session_latest_v1"
LOCAL_ROOT = ROOT / "data/retraining"


# 같은 숫자 표본의 완전 일치와 보수적인 근접 일치 식별
def fingerprints(frame, near=False):
    values = frame[FEATURES].to_numpy(dtype="<f8", copy=True)
    values[values == 0] = 0
    values[np.isnan(values)] = np.nan
    if near:
        return [hashlib.sha256("|".join(format(v, ".12g") for v in row).encode()).hexdigest()
                for row in values]
    return [hashlib.sha256(row.tobytes()).hexdigest() for row in values]


@dataclass(frozen=True)
class TrainingReference:
    exact: frozenset
    near: frozenset
    labeled: frozenset
    files: tuple
    rows: int
    values: object = None


# 공식 모델 학습에 사용된 1~6번 원본만 읽고 기존 지문 대조
def load_training_reference():
    if hashlib.sha256(MODEL_PATH.read_bytes()).hexdigest() != MODEL_SHA:
        raise ValueError("공식 모델의 지문이 달라 기존 학습 범위를 확인할 수 없습니다.")
    plan = json.loads((ROOT / "outputs/temporal_expansion/experiment_plan.json").read_text(encoding="utf-8"))
    split_path = ROOT / "outputs/temporal_expansion/split_assignments.csv"
    if plan["train_B_batches"] != list(range(1, 7)) or hashlib.sha256(split_path.read_bytes()).hexdigest() != plan["split_sha256"]:
        raise ValueError("기존 학습 분할 기록의 지문 또는 범위가 다릅니다.")
    split = pd.read_csv(split_path)
    expected = split[split.train_B.astype(str).str.lower().eq("true")]
    if len(expected) != 5933 or not expected.batch.between(1, 6).all():
        raise ValueError("공식 모델의 학습 표본 구성을 확인할 수 없습니다.")
    inventory = pd.read_csv(ROOT / "outputs/file_validation.csv").set_index("batch")
    directory = Path(read_config()["data_dir"])
    records, rows, row_ids = [], [], []
    for batch in range(1, 7):
        path = directory / f"batch{batch}.dat"
        payload = path.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        if digest != inventory.loc[batch, "sha256"]:
            raise ValueError(f"Batch {batch} 원본 지문이 과거 검증 기록과 다릅니다.")
        for number, line in enumerate(payload.decode("utf-8").splitlines(), 1):
            gas, values = parse_line(line)
            rows.append([*values, gas])
            row_ids.append(f"b{batch:02d}_r{number:05d}")
        records.append((path.name, digest))
    if set(row_ids) != set(expected.row_id) or len(rows) != len(expected):
        raise ValueError("원본과 공식 학습 분할의 행 구성이 다릅니다.")
    frame = pd.DataFrame(rows, columns=[*FEATURES, "gas"])
    exact = fingerprints(frame)
    values = frame[FEATURES].to_numpy(copy=True)
    values.setflags(write=False)
    return TrainingReference(frozenset(exact), frozenset(fingerprints(frame, near=True)),
                             frozenset(zip(exact, frame.gas.astype(int))), tuple(records), len(frame), values)


# 행별 세션과 실제 시각을 별도 CSV에서 확인
def read_sessions(payload, size):
    if not payload:
        raise ValueError("행별 세션·측정 시각 정보가 없어 시간순 분리를 보류합니다.")
    if len(payload) > MAX_BYTES:
        raise ValueError("세션 정보 파일은 20MB 이하여야 합니다.")
    text = payload.decode("utf-8-sig")
    parsed = list(csv.reader(io.StringIO(text), strict=True))
    columns = ["input_row", "session_id", "measured_at"]
    if not parsed or len(set(parsed[0])) != len(parsed[0]) or set(parsed[0]) != set(columns):
        raise ValueError("세션 CSV에는 input_row, session_id, measured_at 열이 각각 한 번 필요합니다.")
    if any(len(row) != 3 for row in parsed[1:]) or len(parsed) - 1 != size:
        raise ValueError("세션 CSV의 행 수와 센서 CSV의 측정 샘플 수가 일치해야 합니다.")
    table = pd.DataFrame(parsed[1:], columns=parsed[0])[columns]
    row_ids = pd.to_numeric(table.input_row, errors="raise").to_numpy(dtype=float)
    if not np.isfinite(row_ids).all() or not np.equal(row_ids, np.floor(row_ids)).all():
        raise ValueError("input_row는 측정 번호 1부터 시작하는 정수여야 합니다.")
    table["input_row"] = row_ids.astype(int)
    if sorted(table.input_row) != list(range(1, size + 1)):
        raise ValueError("각 측정 번호의 세션 정보가 누락·중복 없이 한 번씩 필요합니다.")
    if not table.session_id.map(lambda value: bool(re.fullmatch(r"[\w.:-]{1,100}", value))).all():
        raise ValueError("세션 ID는 1~100자의 문자·숫자·밑줄·점·하이픈·콜론으로 입력하세요.")
    dates = []
    for value in table.measured_at:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if "T" not in value or stamp.utcoffset() is None:
            raise ValueError("측정 시각에 시간대를 포함하세요. 예: 2026-10-28T09:00:00+09:00")
        dates.append(stamp.astimezone(timezone.utc).isoformat())
    table["measured_at"] = dates
    return table.sort_values("input_row").reset_index(drop=True)


@dataclass
class PreparationCheck:
    data: object = None
    sessions: object = None
    assignments: object = None
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    holds: list = field(default_factory=list)
    summary: dict = field(default_factory=dict)
    reference: object = None

    @property
    def ready(self):
        return not self.errors and not self.holds and self.assignments is not None


# 품질 확인 후 최신 한 세션만 검증으로 고정 배정
def inspect_candidate(payload, session_payload, source, truth_method, confirmed, reference):
    result = PreparationCheck(reference=reference)
    if not source.strip():
        result.errors.append("데이터 출처를 입력하세요.")
    if not truth_method.strip() or not confirmed:
        result.errors.append("AI 예측이 아닌 실제 정답의 확인 방식과 확인 동의가 필요합니다.")
    try:
        result.data = read_upload(payload)
    except InputError as exc:
        result.errors.append(str(exc))
        return result
    data = result.data
    if data.truth is None:
        result.errors.append("재학습 데이터에는 실제 정답 gas 열이 반드시 필요합니다.")
        return result
    exact, near = fingerprints(data.features), fingerprints(data.features, near=True)
    stats = pd.DataFrame({"exact": exact, "near": near, "gas": data.truth})
    counts = pd.Series(data.truth).value_counts().reindex(GASES, fill_value=0)
    result.summary = {
        "rows": len(stats), "gas_counts": {str(k): int(v) for k, v in counts.items()},
        "missing_cells": data.missing_cells,
        "missing_fraction": data.missing_cells / (len(stats) * len(FEATURES)),
        "duplicate_extra": int(stats.exact.duplicated().sum()),
        "feature_order_rearranged": data.reordered,
        "reference_check": "미확인",
    }
    if data.missing_cells:
        result.warnings.append("부분 결측값이 있습니다. 이번 단계에서는 대치하지 않습니다. 향후 Train 중앙값으로만 처리해야 합니다.")
    if result.summary["duplicate_extra"]:
        result.warnings.append("같은 센서 특징이 반복됩니다. 반복 측정 여부를 확인하고 표본 수를 독립 표본 수로 해석하지 마세요.")
    if stats.groupby("exact").gas.nunique().gt(1).any():
        result.errors.append("같은 특징값에 서로 다른 정답이 있습니다. 정답 충돌을 확인하세요.")
    if counts.eq(0).any():
        result.holds.append("전체 데이터에 6종 가스가 모두 필요합니다.")
    positive = counts[counts > 0]
    ratio = float(positive.max() / positive.min())
    result.summary["class_imbalance_ratio"] = ratio
    if ratio > 10:
        result.warnings.append("가스별 최대/최소 표본 수 차이가 10배를 초과합니다.")
    if reference is None:
        result.holds.append("기존 학습 데이터와 중복을 확인하지 못해 준비를 보류합니다.")
    else:
        hits = [key in reference.exact for key in exact]
        near_hits = [key in reference.near for key in near]
        same_label = sum((key, int(gas)) in reference.labeled for key, gas in zip(exact, data.truth))
        result.summary.update({"reference_check": "특징 완전 일치 및 12자리 유효숫자 근접 검사 완료",
                               "old_feature_matches": sum(hits), "old_labeled_matches": same_label,
                               "old_near_matches": sum(near_hits), "reference_rows": reference.rows})
        partial_hits = 0
        if data.missing_cells and reference.rows:
            if reference.values is None:
                result.holds.append("결측 표본을 기존 학습 자료와 비교할 수 없어 보류합니다.")
            else:
                for row in data.features.to_numpy():
                    present = np.isfinite(row)
                    if present.all():
                        continue
                    anchors = np.flatnonzero(present)[:4]
                    possible = np.all(np.isclose(reference.values[:, anchors], row[anchors],
                                                 rtol=1e-11, atol=1e-14), axis=1)
                    if possible.any() and np.all(np.isclose(
                            reference.values[possible][:, present], row[present],
                            rtol=1e-11, atol=1e-14), axis=1).any():
                        partial_hits += 1
        result.summary["old_partial_possible_matches"] = partial_hits
        if any(hits) or any(near_hits) or partial_hits:
            result.errors.append("기존 Model A 학습 자료와 일치하거나 매우 가까운 행이 있습니다. 신규 독립 자료로 준비하지 않습니다.")
    try:
        result.sessions = read_sessions(session_payload, len(stats))
    except (ValueError, UnicodeError, csv.Error, OverflowError) as exc:
        result.holds.append("세션 정보 확인 필요: " + str(exc))
        return result
    sessions = result.sessions
    stats["session_id"] = sessions.session_id
    if stats.groupby("near").session_id.nunique().gt(1).any():
        result.errors.append("같거나 매우 가까운 표본이 여러 세션에 있습니다. 세션 간 중복을 해소해야 합니다.")
    bounds = sessions.groupby("session_id").measured_at.agg(["min", "max"]).sort_values(["min", "max"])
    result.summary["sessions"] = bounds.reset_index().to_dict(orient="records")
    if len(bounds) < 2:
        result.holds.append("한 세션만 있어 세션이 분리된 미래 검증 자료가 부족합니다.")
        return result
    if any(bounds.iloc[i]["max"] >= bounds.iloc[i + 1]["min"] for i in range(len(bounds) - 1)):
        result.holds.append("세션 측정 구간이 겹치거나 같은 시각입니다. 엄격한 과거→미래 분리를 확인할 수 없습니다.")
        return result
    assignments = sessions.copy()
    assignments["partition"] = np.where(sessions.session_id.eq(bounds.index[-1]), "validation", "train")
    assignments["gas"] = data.truth
    assignments["feature_sha256"] = exact
    assignments["near_feature_sha256"] = near
    assignments["row_id"] = [f"{data.digest}:r{number:05d}" for number in assignments.input_row]
    for partition in ["train", "validation"]:
        support = assignments[assignments.partition.eq(partition)].gas.value_counts().reindex(GASES, fill_value=0)
        result.summary[partition + "_counts"] = {str(k): int(v) for k, v in support.items()}
        partition_features = data.features.loc[assignments.partition.eq(partition)]
        if partition_features.isna().all().any():
            message = f"{partition}에 전체가 결측인 특징 열이 있습니다."
            if partition == "train":
                result.holds.append(message + " 학습 기준을 만들 수 없어 보류합니다.")
            else:
                result.warnings.append(message + " 측정 상태를 확인하세요.")
        if support.eq(0).any():
            result.holds.append(f"{partition}에 6종 가스가 모두 존재하지 않습니다. 분리 경계를 바꾸지 않고 추가 데이터를 요청합니다.")
        if support.lt(5).any():
            result.warnings.append(f"{partition}의 일부 가스 표본이 5개 미만입니다. 검증 불확실성이 큽니다.")
    train = assignments[assignments.partition.eq("train")]
    valid = assignments[assignments.partition.eq("validation")]
    if not set(train.session_id).isdisjoint(valid.session_id):
        result.errors.append("동일 세션이 양쪽에 포함되어 분리를 차단합니다.")
    if not set(train.near_feature_sha256).isdisjoint(valid.near_feature_sha256):
        result.errors.append("학습·검증 사이 중복 가능 표본이 있어 분리를 차단합니다.")
    result.assignments = assignments
    return result
