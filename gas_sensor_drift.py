import csv
import hashlib
import io
import json
import os
import re
import tempfile
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath

import altair as alt
import joblib
import numpy as np
import pandas as pd
import sklearn
import streamlit as st
from joblib.numpy_pickle import NumpyUnpickler, _validate_fileobject_and_memmap
from sklearn.base import clone
from sklearn.impute import SimpleImputer
from sklearn.kernel_approximation import RBFSampler
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
    roc_auc_score,
    roc_curve,
)
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from threadpoolctl import threadpool_limits


# 저장 감지기의 과거 클래스 경로를 이 파일의 동일 구현에 연결
class PortableModelUnpickler(NumpyUnpickler):
    # 과거 감지기 클래스만 현재 파일 구현으로 연결
    def find_class(self, module, name):
        if (module, name) == ("src.drift_detection.detector", "DriftDetector"):
            return drift_DriftDetector
        if module in {"src", "app_streamlit"} or module.startswith("src."):
            raise ValueError("지원하지 않는 프로젝트 내부 모델 클래스: " + module)
        return super().find_class(module, name)


# 신뢰한 로컬 joblib만 읽으며 프로젝트 Python 모듈 import 없이 복원
def portable_joblib_load(path):
    filename = str(Path(path))
    with open(filename, "rb") as stream:
        with _validate_fileobject_and_memmap(stream, filename, None) as (handle, mode):
            return PortableModelUnpickler(
                filename, handle, ensure_native_byte_order=True, mmap_mode=mode
            ).load()


# 1. 파일 지문 및 공통 설정


# 파일·업로드의 바이트 지문 반환
def hashing_sha256_bytes(payload):
    return hashlib.sha256(payload).hexdigest()


# 2. 원본 자료 형식과 설정


data_ROOT = Path(__file__).resolve().parent

data_GASES = {
    1: "Ethanol",
    2: "Ethylene",
    3: "Ammonia",
    4: "Acetaldehyde",
    5: "Acetone",
    6: "Toluene",
}

data_FEATURES = [f"f{i:03d}" for i in range(1, 129)]


# 설정 파일에서 원본 자료 경로 불러오기
def data_read_config(path=None):
    path = Path(path) if path else data_ROOT / "config.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    directory = Path(config["data_dir"])
    config["data_dir"] = str(directory if directory.is_absolute() else path.parent / directory)
    return config


# 원본 한 줄을 정답과 특징값으로 분리
def data_parse_line(line, n_features=128):
    tokens = line.split()
    if not tokens:
        raise ValueError("Blank data row")
    try:
        label = int(tokens[0])
    except ValueError as exc:
        raise ValueError("Expected integer gas label, without concentration field") from exc
    if label not in data_GASES:
        raise ValueError(f"Unknown label: {label}")
    if len(tokens) != n_features + 1:
        raise ValueError(f"Expected {n_features} explicit features, got {len(tokens) - 1}")
    values, indices = ([], [])
    for token in tokens[1:]:
        try:
            key, value = token.split(":")
            indices.append(int(key))
            values.append(float(value))
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Malformed index:value token: {token}") from exc
    if indices != list(range(1, n_features + 1)):
        raise ValueError("Feature indices must appear exactly once in order 1..128")
    return (label, values)


# 3. 고정 분포 변화 감지


drift_FEATURES = tuple(data_FEATURES)

drift_MESSAGES = {
    "기준 범위": "입력된 센서 데이터의 분포가 설정된 기준 범위 내에 있습니다. 이는 가스 분류 정확도를 보장하지 않습니다.",
    "분포 변화 감지": "기존 학습 데이터와 다른 센서 측정 분포가 감지되었습니다. 가스 분류 성능 저하 가능성을 확인하기 위해 기준 가스 측정 및 모델 재검증을 권장합니다.",
    "평가 불가": "입력 데이터가 부족하거나 센서 특징 형식이 일치하지 않아 드리프트 평가를 수행할 수 없습니다.",
}


# 특징 이름 확인 후 정해진 순서로 정렬
def drift_validate_features(frame):
    if not isinstance(frame, pd.DataFrame):
        raise ValueError("128개 특징 이름이 있는 DataFrame 필요")
    if frame.columns.has_duplicates:
        raise ValueError("중복 특징 이름")
    if len(frame.columns) != 128 or set(frame.columns) != set(drift_FEATURES):
        raise ValueError("f001~f128만 필요하며 정답·Batch·추가 열은 허용하지 않음")
    data = frame.loc[:, drift_FEATURES].copy()
    if any((pd.api.types.is_bool_dtype(data[c]) for c in drift_FEATURES)):
        raise ValueError("참/거짓 대신 센서 수치 필요")
    try:
        data = data.apply(pd.to_numeric, errors="raise").astype(float)
    except (TypeError, ValueError) as exc:
        raise ValueError("숫자로 변환 불가능한 값") from exc
    values = data.to_numpy()
    if np.isinf(values).any():
        raise ValueError("무한대 값은 허용하지 않음")
    if len(data) and (data.isna().all(axis=0).any() or data.isna().all(axis=1).any()):
        raise ValueError("전체 결측 특징 또는 전체 결측 행")
    return data


# 자료 구조 및 동작 정의
class drift_DriftDetector:

    # 저장 경로 및 기본 상태 설정
    def __init__(self):
        self.version = "rff_mmd_v1"
        self.window_size = 100
        self.random_state = 42
        self.n_components = 512
        self.bandwidth_sample_limit = 1024
        self.imputer = SimpleImputer(strategy="median")
        self.scaler = StandardScaler()

    # 연구용 참조 적합 함수이며 운영 중 호출하지 않음
    def fit_reference(self, reference):
        if hasattr(self, "reference_mean_"):
            raise ValueError("참조 자료 재적합 금지")
        data = drift_validate_features(reference)
        if len(data) < self.window_size:
            raise ValueError("참조 자료 최소100개 필요")
        values = self.scaler.fit_transform(self.imputer.fit_transform(data))
        rng = np.random.default_rng(self.random_state)
        take = rng.choice(len(data), min(len(data), self.bandwidth_sample_limit), replace=False)
        squared = euclidean_distances(values[take], squared=True)
        distances = squared[np.triu_indices(len(take), k=1)]
        positive = distances[distances > 1e-12]
        if not len(positive):
            raise ValueError("양의 거리 없음: 커널 폭 결정 불가")
        self.median_squared_distance_ = float(np.median(positive))
        self.gamma_ = 1.0 / (2.0 * self.median_squared_distance_)
        self.rff = RBFSampler(
            gamma=self.gamma_, n_components=self.n_components, random_state=self.random_state
        )
        embedded = self.rff.fit_transform(values)
        self.reference_mean_ = embedded.mean(axis=0)
        self.metadata_ = {
            "version": self.version,
            "features": list(drift_FEATURES),
            "reference_n": len(data),
            "random_state": self.random_state,
            "n_components": self.n_components,
            "window_size": self.window_size,
            "bandwidth_sample_n": len(take),
            "distance_epsilon": 1e-12,
            "excluded_near_zero_pairs": int(len(distances) - len(positive)),
            "gamma": self.gamma_,
            "median_squared_distance": self.median_squared_distance_,
            "reference_missing_cells": int(data.isna().sum().sum()),
            "reference_constant_features": int((np.nanstd(data, axis=0) == 0).sum()),
            "score": "squared L2 distance between RFF means; not probability",
        }
        return self

    # 고정 참조와 100행 분포 차이 계산
    def score_window(self, frame):
        if not hasattr(self, "reference_mean_"):
            raise ValueError("참조 자료 적합 전")
        data = drift_validate_features(frame)
        if len(data) != self.window_size:
            raise ValueError("점수 계산에는 정확히100개 행 필요")
        values = self.scaler.transform(self.imputer.transform(data))
        difference = self.rff.transform(values).mean(axis=0) - self.reference_mean_
        score = float(difference @ difference)
        if not np.isfinite(score):
            raise ValueError("유효하지 않은 점수")
        return score

    # 연구용 임계값 산정 함수이며 운영 중 호출하지 않음
    def calibrate(self, calibration):
        if hasattr(self, "threshold_"):
            raise ValueError("임계값 재설정 금지")
        data = drift_validate_features(calibration)
        n = len(data) // self.window_size
        if n < 10:
            raise ValueError("임계값 산정에는 최소10개 창 필요")
        scores = [self.score_window(data.iloc[i * 100 : (i + 1) * 100]) for i in range(n)]
        self.threshold_ = float(np.quantile(scores, 0.95, method="linear"))
        self.metadata_.update(
            {
                "threshold": self.threshold_,
                "quantile": 0.95,
                "quantile_method": "linear",
                "calibration_windows": n,
                "calibration_dropped_rows": len(data) % 100,
            }
        )
        return np.asarray(scores)

    # 고정 임계값과 경고 문구 판정
    def status(self, score):
        if not hasattr(self, "threshold_"):
            raise ValueError("임계값 설정 전")
        if not np.isfinite(score) or score < 0:
            raise ValueError("유효하지 않은 점수")
        state = "분포 변화 감지" if score > self.threshold_ else "기준 범위"
        return (state, drift_MESSAGES[state])

    # 입력 순서대로 고정 창 평가
    def evaluate(self, frame):
        try:
            if not hasattr(self, "threshold_"):
                raise ValueError("임계값 설정 전")
            data = drift_validate_features(frame)
            if len(data) < 100:
                raise ValueError("유효 측정값100개 미만")
        except (ValueError, TypeError) as exc:
            return {
                "status": "평가 불가",
                "message": drift_MESSAGES["평가 불가"],
                "reason": str(exc),
                "windows": [],
                "input_rows": len(frame) if hasattr(frame, "__len__") else 0,
                "valid_windows": 0,
                "excluded_tail_rows": len(frame) if hasattr(frame, "__len__") else 0,
            }
        windows = []
        for i in range(len(data) // 100):
            piece = data.iloc[i * 100 : (i + 1) * 100]
            item = {
                "window": i + 1,
                "start_position": i * 100 + 1,
                "end_position": (i + 1) * 100,
                "n": 100,
                "missing_cells": int(piece.isna().sum().sum()),
            }
            try:
                score = self.score_window(piece)
                state, message = self.status(score)
                item.update(
                    score=score, status=state, message=message, alert=state == "분포 변화 감지"
                )
            except ValueError as exc:
                item.update(
                    score=None,
                    status="평가 불가",
                    message=drift_MESSAGES["평가 불가"],
                    alert=None,
                    reason=str(exc),
                )
            windows.append(item)
        valid = [w for w in windows if w["score"] is not None]
        alert_n = sum((w["alert"] for w in valid))
        state = "평가 불가" if not valid else "분포 변화 감지" if alert_n else "기준 범위"
        return {
            "status": state,
            "message": drift_MESSAGES[state],
            "windows": windows,
            "input_rows": len(data),
            "valid_windows": len(valid),
            "invalid_windows": len(windows) - len(valid),
            "excluded_tail_rows": len(data) % 100,
            "alert_windows": alert_n,
            "alert_rate": alert_n / len(valid) if valid else None,
            "threshold": self.threshold_,
            "schema_reordered": list(frame.columns) != list(drift_FEATURES),
        }


# 웹앱과 명령행에서 재사용할 CSV 입력 경계
def drift_evaluate_csv(detector, source):
    try:
        frame = pd.read_csv(source, encoding="utf-8-sig")
    except (ValueError, OSError, UnicodeError, pd.errors.ParserError) as exc:
        return {
            "status": "평가 불가",
            "message": drift_MESSAGES["평가 불가"],
            "reason": str(exc),
            "windows": [],
        }
    return detector.evaluate(frame)


# 신뢰할 수 있는 로컬 감지기만 불러오기
def drift_load_detector(path):
    detector = portable_joblib_load(Path(path))
    if not isinstance(detector, drift_DriftDetector) or not hasattr(detector, "threshold_"):
        raise ValueError("지원하지 않는 감지기 파일")
    return detector


# 4. CSV 검증·예측·평가·다운로드


service_MODEL_PATH = data_ROOT / "models/temporal_expansion/B_SVM_balanced.joblib"
service_DETECTOR_PATH = data_ROOT / "models/drift_detection/rff_mmd_v1.joblib"
service_MODEL_SHA = "1d6b20c94d1580d799e05ab5a9ce746bdb272d74f70ec2ff964011fffecfde32"
service_DETECTOR_SHA = "de47661f66c69cdc7553f73acf1df9b721f65771d0301fe69a7a326f814fa4c5"
service_THRESHOLD = 0.00825701197565701
service_MAX_BYTES = 20 * 1024 * 1024
service_MAX_ROWS = 20000

# 자료 구조 및 동작 정의
class service_InputError(ValueError):
    pass

# 자료 구조 및 동작 정의
@dataclass
class service_ModelBundle:
    classifier: object
    detector: object
    model_name: str = "Model A / B_SVM_balanced"
    model_sha: str = service_MODEL_SHA
    version_id: str = "fixed_model_a"
    applied_at_utc: object = None

# 자료 구조 및 동작 정의
@dataclass
class service_InputData:
    features: pd.DataFrame
    truth: object
    digest: str
    reordered: bool
    missing_cells: int

# 신뢰한 로컬 파일의 지문과 설정을 확인한 뒤 한 번 로딩
def service_load_models():
    for path, expected in [
        (service_MODEL_PATH, service_MODEL_SHA),
        (service_DETECTOR_PATH, service_DETECTOR_SHA),
    ]:
        if not path.is_file():
            raise RuntimeError(
                "저장 모델을 찾을 수 없습니다. 프로젝트의 models 폴더를 확인해 주세요."
            )
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise RuntimeError(
                "저장 모델 버전이 확인된 버전과 다릅니다. 임의 모델은 사용하지 않습니다."
            )
    classifier = portable_joblib_load(service_MODEL_PATH)
    detector = drift_load_detector(service_DETECTOR_PATH)
    if list(classifier.feature_names_in_) != data_FEATURES or list(classifier.classes_) != list(
        data_GASES
    ):
        raise RuntimeError("공식 모델의 특징 순서 또는 가스 매핑이 일치하지 않습니다.")
    if detector.threshold_ != service_THRESHOLD or detector.window_size != 100:
        raise RuntimeError("감지기 설정이 기존 고정 조건과 다릅니다.")
    return service_ModelBundle(classifier, detector)

# 중복 열을 먼저 확인하고 선택적 정답을 명시적으로 분리
def service_read_upload(payload):
    if not payload or not payload.strip():
        raise service_InputError(
            "빈 파일입니다. 제목 행과 센서 측정값이 있는 CSV를 선택해 주세요."
        )
    if len(payload) > service_MAX_BYTES:
        raise service_InputError("파일 크기는20MB 이하여야 합니다.")
    try:
        text = payload.decode("utf-8-sig")
    except UnicodeError as exc:
        raise service_InputError("UTF-8 형식의 CSV가 필요합니다.") from exc
    try:
        reader = csv.reader(io.StringIO(text, newline=""), strict=True)
        header = next(reader)
        if len(header) != len(set(header)):
            raise service_InputError("중복된 열 이름이 있습니다. 각 특징은 한 번만 포함해 주세요.")
        missing = [name for name in data_FEATURES if name not in header]
        extra = [name for name in header if name not in data_FEATURES and name != "gas"]
        if missing:
            raise service_InputError("필수 특징이 없습니다: " + ", ".join(missing[:8]))
        if extra:
            raise service_InputError(
                "허용되지 않은 열입니다: " + ", ".join(extra[:8]) + ". 정답 열은 gas만 허용합니다."
            )
        rows = 0
        for line_n, record in enumerate(reader, 2):
            if len(record) != len(header):
                raise service_InputError(
                    f"CSV의{line_n}번째 레코드 열 수가 제목과 다릅니다. 빈 행도 확인해 주세요."
                )
            rows += 1
            if rows > service_MAX_ROWS:
                raise service_InputError("한 번에20,000행까지 분석할 수 있습니다.")
        if not rows:
            raise service_InputError("센서 측정 행이 없습니다. 제목 아래에 데이터를 넣어 주세요.")
        frame = pd.read_csv(io.StringIO(text))
    except (csv.Error, StopIteration, pd.errors.ParserError) as exc:
        raise service_InputError(
            "CSV 구조를 읽을 수 없습니다. 쉼표와 따옴표를 확인해 주세요."
        ) from exc
    if len(frame) != rows:
        raise service_InputError(
            "데이터 행을 정확히 읽지 못했습니다. 빈 행과 CSV 구조를 확인해 주세요."
        )
    truth = None
    if "gas" in frame:
        if pd.api.types.is_bool_dtype(frame.gas):
            raise service_InputError("gas 정답은1~6의 정수여야 합니다.")
        try:
            labels = pd.to_numeric(frame.gas, errors="raise").to_numpy(dtype=float)
        except (TypeError, ValueError) as exc:
            raise service_InputError(
                "gas 정답은1~6의 정수여야 합니다. 평가하지 않으려면 gas 열을 제거해 주세요."
            ) from exc
        if (
            not np.isfinite(labels).all()
            or not np.equal(labels, np.floor(labels)).all()
            or (not np.isin(labels, list(data_GASES)).all())
        ):
            raise service_InputError(
                "gas 열에 결측 또는1~6 이외의 값이 있습니다. 정답을 확인해 주세요."
            )
        truth = labels.astype(int)
    feature_names = [name for name in header if name != "gas"]
    try:
        features = drift_validate_features(frame[feature_names])
    except ValueError as exc:
        raise service_InputError("센서 특징을 확인해 주세요: " + str(exc)) from exc
    return service_InputData(
        features,
        truth,
        hashlib.sha256(payload).hexdigest(),
        feature_names != data_FEATURES,
        int(features.isna().sum().sum()),
    )

# 업로드 변경 시 이전 결과를 재사용하지 않도록 상태 초기화
def service_reset_on_upload_change(state, digest):
    if state.get("input_digest") != digest:
        state.pop("analysis", None)
        state.pop("analysis_error", None)
        state["input_digest"] = digest
        return True
    return False

# 저장 모델 추론과 독립적인 분포 감지 수행
def service_analyze(data, models):
    predicted = np.asarray(models.classifier.predict(data.features), dtype=int)
    if len(predicted) != len(data.features) or not np.isin(predicted, list(data_GASES)).all():
        raise RuntimeError("모델의 예측 결과를 확인할 수 없습니다.")
    drift = models.detector.evaluate(data.features)
    row_table = data.features.copy()
    row_table.insert(0, "input_row", np.arange(1, len(row_table) + 1))
    if data.truth is not None:
        row_table["gas"] = data.truth
    row_table["predicted_gas_id"] = predicted
    row_table["predicted_gas"] = [data_GASES[int(g)] for g in predicted]
    row_table["classification_model"] = models.model_name
    row_table["classification_sha256"] = models.model_sha
    if models.version_id != "fixed_model_a":
        row_table["classification_version"] = models.version_id
    row_table["input_sha256"] = data.digest
    counts = pd.DataFrame({"gas_id": list(data_GASES), "gas": list(data_GASES.values())})
    counts["n"] = [int((predicted == g).sum()) for g in data_GASES]
    counts["proportion"] = counts.n / len(predicted)
    window_columns = [
        "window",
        "start_position",
        "end_position",
        "n",
        "missing_cells",
        "score",
        "status",
        "alert",
        "reason",
    ]
    window_table = pd.DataFrame(drift["windows"]).reindex(columns=window_columns)
    window_table["threshold"] = service_THRESHOLD
    window_table["detector_version"] = "rff_mmd_v1"
    window_table["detector_sha256"] = service_DETECTOR_SHA
    window_table["window_size"] = 100
    window_table["input_sha256"] = data.digest
    evaluation = None
    if data.truth is not None:
        supported = np.unique(data.truth)
        precision, recall, f1, support = precision_recall_fscore_support(
            data.truth, predicted, labels=list(data_GASES), zero_division=0
        )
        evaluation = {
            "accuracy": float(accuracy_score(data.truth, predicted)),
            "macro_f1": float(
                f1_score(data.truth, predicted, labels=supported, average="macro", zero_division=0)
            ),
            "supported_classes": len(supported),
            "confusion": pd.DataFrame(
                confusion_matrix(data.truth, predicted, labels=list(data_GASES)),
                index=list(data_GASES.values()),
                columns=list(data_GASES.values()),
            ),
            "per_class": pd.DataFrame(
                {
                    "gas": list(data_GASES.values()),
                    "precision": precision,
                    "recall": np.where(support > 0, recall, np.nan),
                    "f1": np.where(support > 0, f1, np.nan),
                    "support": support,
                }
            ),
        }
    summary = {
        "input_rows": len(predicted),
        "predicted_classes": int(counts.n.gt(0).sum()),
        "valid_windows": drift.get("valid_windows", 0),
        "invalid_windows": drift.get("invalid_windows", 0),
        "alert_windows": drift.get("alert_windows", 0),
        "alert_rate": drift.get("alert_rate"),
        "excluded_tail_rows": drift.get("excluded_tail_rows", 0),
        "distribution_status": drift["status"],
        "unavailable_reason": drift.get("reason", ""),
        "window_size": 100,
        "threshold": service_THRESHOLD,
        "missing_feature_cells": data.missing_cells,
        "feature_order_rearranged": data.reordered,
        "classification_model": models.model_name,
        "classification_sha256": models.model_sha,
        "detector_version": "rff_mmd_v1",
        "detector_sha256": service_DETECTOR_SHA,
        "input_sha256": data.digest,
        "truth_evaluation_available": evaluation is not None,
    }
    if evaluation:
        summary.update(
            upload_accuracy=evaluation["accuracy"],
            upload_macro_f1=evaluation["macro_f1"],
            truth_supported_classes=evaluation["supported_classes"],
        )
    if models.version_id != "fixed_model_a":
        summary.update(
            classification_version=models.version_id, model_applied_at_utc=models.applied_at_utc
        )
    return {
        "rows": row_table,
        "counts": counts,
        "windows": window_table,
        "drift": drift,
        "summary": summary,
        "evaluation": evaluation,
    }


# 사용자 기기로만 전달할 UTF-8 CSV 생성
def service_export_csv(table):
    return table.to_csv(index=False).encode("utf-8-sig")


# 예측·분포 점수·요약 CSV 묶음 생성
def service_downloads(result):
    return {
        "gas_classification.csv": service_export_csv(result["rows"]),
        "distribution_windows.csv": service_export_csv(result["windows"]),
        "analysis_summary.csv": service_export_csv(pd.DataFrame([result["summary"]])),
    }


# 5. 신규 정답 자료 검증 및 시간순 분리

preparation_POLICY = "session_latest_v1"
preparation_LOCAL_ROOT = data_ROOT / "data/retraining"

# 같은 숫자 표본의 완전 일치와 보수적인 근접 일치 식별
def preparation_fingerprints(frame, near=False):
    values = frame[data_FEATURES].to_numpy(dtype="<f8", copy=True)
    values[values == 0] = 0
    values[np.isnan(values)] = np.nan
    if near:
        return [
            hashlib.sha256("|".join((format(v, ".12g") for v in row)).encode()).hexdigest()
            for row in values
        ]
    return [hashlib.sha256(row.tobytes()).hexdigest() for row in values]

# 자료 구조 및 동작 정의
@dataclass(frozen=True)
class preparation_TrainingReference:
    exact: frozenset
    near: frozenset
    labeled: frozenset
    files: tuple
    rows: int
    values: object = None

# 공식 모델 학습에 사용된 1~6번 원본만 읽고 기존 지문 대조
def preparation_load_training_reference():
    if hashing_sha256_bytes(service_MODEL_PATH.read_bytes()) != service_MODEL_SHA:
        raise ValueError("공식 모델의 지문이 달라 기존 학습 범위를 확인할 수 없습니다.")
    plan = json.loads(
        (data_ROOT / "outputs/temporal_expansion/experiment_plan.json").read_text(encoding="utf-8")
    )
    split_path = data_ROOT / "outputs/temporal_expansion/split_assignments.csv"
    if (
        plan["train_B_batches"] != list(range(1, 7))
        or hashing_sha256_bytes(split_path.read_bytes()) != plan["split_sha256"]
    ):
        raise ValueError("기존 학습 분할 기록의 지문 또는 범위가 다릅니다.")
    split = pd.read_csv(split_path)
    expected = split[split.train_B.astype(str).str.lower().eq("true")]
    if len(expected) != 5933 or not expected.batch.between(1, 6).all():
        raise ValueError("공식 모델의 학습 표본 구성을 확인할 수 없습니다.")
    inventory = pd.read_csv(data_ROOT / "outputs/file_validation.csv").set_index("batch")
    directory = Path(data_read_config()["data_dir"])
    records, rows, row_ids = ([], [], [])
    for batch in range(1, 7):
        path = directory / f"batch{batch}.dat"
        payload = path.read_bytes()
        digest = hashing_sha256_bytes(payload)
        if digest != inventory.loc[batch, "sha256"]:
            raise ValueError(f"Batch {batch} 원본 지문이 과거 검증 기록과 다릅니다.")
        for number, line in enumerate(payload.decode("utf-8").splitlines(), 1):
            gas, values = data_parse_line(line)
            rows.append([*values, gas])
            row_ids.append(f"b{batch:02d}_r{number:05d}")
        records.append((path.name, digest))
    if set(row_ids) != set(expected.row_id) or len(rows) != len(expected):
        raise ValueError("원본과 공식 학습 분할의 행 구성이 다릅니다.")
    frame = pd.DataFrame(rows, columns=[*data_FEATURES, "gas"])
    exact = preparation_fingerprints(frame)
    values = frame[data_FEATURES].to_numpy(copy=True)
    values.setflags(write=False)
    return preparation_TrainingReference(
        frozenset(exact),
        frozenset(preparation_fingerprints(frame, near=True)),
        frozenset(zip(exact, frame.gas.astype(int))),
        tuple(records),
        len(frame),
        values,
    )

# 행별 세션과 실제 시각을 별도 CSV에서 확인
def preparation_read_sessions(payload, size):
    if not payload:
        raise ValueError("행별 세션·측정 시각 정보가 없어 시간순 분리를 보류합니다.")
    if len(payload) > service_MAX_BYTES:
        raise ValueError("세션 정보 파일은 20MB 이하여야 합니다.")
    text = payload.decode("utf-8-sig")
    parsed = list(csv.reader(io.StringIO(text), strict=True))
    columns = ["input_row", "session_id", "measured_at"]
    if not parsed or len(set(parsed[0])) != len(parsed[0]) or set(parsed[0]) != set(columns):
        raise ValueError(
            "세션 CSV에는 input_row, session_id, measured_at 열이 각각 한 번 필요합니다."
        )
    if any((len(row) != 3 for row in parsed[1:])) or len(parsed) - 1 != size:
        raise ValueError("세션 CSV의 행 수와 센서 CSV의 측정 샘플 수가 일치해야 합니다.")
    table = pd.DataFrame(parsed[1:], columns=parsed[0])[columns]
    row_ids = pd.to_numeric(table.input_row, errors="raise").to_numpy(dtype=float)
    if not np.isfinite(row_ids).all() or not np.equal(row_ids, np.floor(row_ids)).all():
        raise ValueError("input_row는 측정 번호 1부터 시작하는 정수여야 합니다.")
    table["input_row"] = row_ids.astype(int)
    if sorted(table.input_row) != list(range(1, size + 1)):
        raise ValueError("각 측정 번호의 세션 정보가 누락·중복 없이 한 번씩 필요합니다.")
    if not table.session_id.map(lambda value: bool(re.fullmatch("[\\w.:-]{1,100}", value))).all():
        raise ValueError("세션 ID는 1~100자의 문자·숫자·밑줄·점·하이픈·콜론으로 입력하세요.")
    dates = []
    for value in table.measured_at:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if "T" not in value or stamp.utcoffset() is None:
            raise ValueError("측정 시각에 시간대를 포함하세요. 예: 2026-10-28T09:00:00+09:00")
        dates.append(stamp.astimezone(timezone.utc).isoformat())
    table["measured_at"] = dates
    return table.sort_values("input_row").reset_index(drop=True)

# 자료 구조 및 동작 정의
@dataclass
class preparation_PreparationCheck:
    data: object = None
    sessions: object = None
    assignments: object = None
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    holds: list = field(default_factory=list)
    summary: dict = field(default_factory=dict)
    reference: object = None

    @property
    # 품질 오류 및 분리 보류 여부 확인
    def ready(self):
        return not self.errors and (not self.holds) and (self.assignments is not None)

# 품질 확인 후 최신 한 세션만 검증으로 고정 배정
def preparation_inspect_candidate(
    payload, session_payload, source, truth_method, confirmed, reference
):
    result = preparation_PreparationCheck(reference=reference)
    if not source.strip():
        result.errors.append("데이터 출처를 입력하세요.")
    if not truth_method.strip() or not confirmed:
        result.errors.append("AI 예측이 아닌 실제 정답의 확인 방식과 확인 동의가 필요합니다.")
    try:
        result.data = service_read_upload(payload)
    except service_InputError as exc:
        result.errors.append(str(exc))
        return result
    data = result.data
    if data.truth is None:
        result.errors.append("재학습 데이터에는 실제 정답 gas 열이 반드시 필요합니다.")
        return result
    exact, near = (
        preparation_fingerprints(data.features),
        preparation_fingerprints(data.features, near=True),
    )
    stats = pd.DataFrame({"exact": exact, "near": near, "gas": data.truth})
    counts = pd.Series(data.truth).value_counts().reindex(data_GASES, fill_value=0)
    result.summary = {
        "rows": len(stats),
        "gas_counts": {str(k): int(v) for k, v in counts.items()},
        "missing_cells": data.missing_cells,
        "missing_fraction": data.missing_cells / (len(stats) * len(data_FEATURES)),
        "duplicate_extra": int(stats.exact.duplicated().sum()),
        "feature_order_rearranged": data.reordered,
        "reference_check": "미확인",
    }
    if data.missing_cells:
        result.warnings.append(
            "부분 결측값이 있습니다. 이번 단계에서는 대치하지 않습니다. 향후 Train 중앙값으로만 처리해야 합니다."
        )
    if result.summary["duplicate_extra"]:
        result.warnings.append(
            "같은 센서 특징이 반복됩니다. 반복 측정 여부를 확인하고 표본 수를 독립 표본 수로 해석하지 마세요."
        )
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
        same_label = sum(
            ((key, int(gas)) in reference.labeled for key, gas in zip(exact, data.truth))
        )
        result.summary.update(
            {
                "reference_check": "특징 완전 일치 및 12자리 유효숫자 근접 검사 완료",
                "old_feature_matches": sum(hits),
                "old_labeled_matches": same_label,
                "old_near_matches": sum(near_hits),
                "reference_rows": reference.rows,
            }
        )
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
                    possible = np.all(
                        np.isclose(
                            reference.values[:, anchors], row[anchors], rtol=1e-11, atol=1e-14
                        ),
                        axis=1,
                    )
                    if (
                        possible.any()
                        and np.all(
                            np.isclose(
                                reference.values[possible][:, present],
                                row[present],
                                rtol=1e-11,
                                atol=1e-14,
                            ),
                            axis=1,
                        ).any()
                    ):
                        partial_hits += 1
        result.summary["old_partial_possible_matches"] = partial_hits
        if any(hits) or any(near_hits) or partial_hits:
            result.errors.append(
                "기존 Model A 학습 자료와 일치하거나 매우 가까운 행이 있습니다. 신규 독립 자료로 준비하지 않습니다."
            )
    try:
        result.sessions = preparation_read_sessions(session_payload, len(stats))
    except (ValueError, UnicodeError, csv.Error, OverflowError) as exc:
        result.holds.append("세션 정보 확인 필요: " + str(exc))
        return result
    sessions = result.sessions
    stats["session_id"] = sessions.session_id
    if stats.groupby("near").session_id.nunique().gt(1).any():
        result.errors.append(
            "같거나 매우 가까운 표본이 여러 세션에 있습니다. 세션 간 중복을 해소해야 합니다."
        )
    bounds = (
        sessions.groupby("session_id").measured_at.agg(["min", "max"]).sort_values(["min", "max"])
    )
    result.summary["sessions"] = bounds.reset_index().to_dict(orient="records")
    if len(bounds) < 2:
        result.holds.append("한 세션만 있어 세션이 분리된 미래 검증 자료가 부족합니다.")
        return result
    if any((bounds.iloc[i]["max"] >= bounds.iloc[i + 1]["min"] for i in range(len(bounds) - 1))):
        result.holds.append(
            "세션 측정 구간이 겹치거나 같은 시각입니다. 엄격한 과거→미래 분리를 확인할 수 없습니다."
        )
        return result
    assignments = sessions.copy()
    assignments["partition"] = np.where(
        sessions.session_id.eq(bounds.index[-1]), "validation", "train"
    )
    assignments["gas"] = data.truth
    assignments["feature_sha256"] = exact
    assignments["near_feature_sha256"] = near
    assignments["row_id"] = [f"{data.digest}:r{number:05d}" for number in assignments.input_row]
    for partition in ["train", "validation"]:
        support = (
            assignments[assignments.partition.eq(partition)]
            .gas.value_counts()
            .reindex(data_GASES, fill_value=0)
        )
        result.summary[partition + "_counts"] = {str(k): int(v) for k, v in support.items()}
        partition_features = data.features.loc[assignments.partition.eq(partition)]
        if partition_features.isna().all().any():
            message = f"{partition}에 전체가 결측인 특징 열이 있습니다."
            if partition == "train":
                result.holds.append(message + " 학습 기준을 만들 수 없어 보류합니다.")
            else:
                result.warnings.append(message + " 측정 상태를 확인하세요.")
        if support.eq(0).any():
            result.holds.append(
                f"{partition}에 6종 가스가 모두 존재하지 않습니다. 분리 경계를 바꾸지 않고 추가 데이터를 요청합니다."
            )
        if support.lt(5).any():
            result.warnings.append(
                f"{partition}의 일부 가스 표본이 5개 미만입니다. 검증 불확실성이 큽니다."
            )
    train = assignments[assignments.partition.eq("train")]
    valid = assignments[assignments.partition.eq("validation")]
    if not set(train.session_id).isdisjoint(valid.session_id):
        result.errors.append("동일 세션이 양쪽에 포함되어 분리를 차단합니다.")
    if not set(train.near_feature_sha256).isdisjoint(valid.near_feature_sha256):
        result.errors.append("학습·검증 사이 중복 가능 표본이 있어 분리를 차단합니다.")
    result.assignments = assignments
    return result

# 6. 불변 데이터셋 등록

# 기존 저장소 API를 유지하며 공통 지문 계산 사용
def datasets_digest(payload):
    return hashing_sha256_bytes(payload)

# 입력·출처·고정 정책으로 동일 등록의 버전 결정
def datasets_identity(payload, session_payload, source, truth_method):
    value = {
        "input_sha256": datasets_digest(payload),
        "sessions_sha256": datasets_digest(session_payload or b""),
        "source": source.strip(),
        "truth_method": truth_method.strip(),
        "policy": preparation_POLICY,
    }
    token = datasets_digest(json.dumps(value, sort_keys=True, ensure_ascii=False).encode())
    return ("dataset_" + token[:24], value)

# 저장 파일의 지문과 원본 추적 정보 확인
def datasets_read_manifest(directory):
    directory = Path(directory)
    if directory.is_symlink():
        raise ValueError("연결된 외부 데이터셋 경로는 허용하지 않습니다.")
    payload = (directory / "manifest.json").read_bytes()
    if (
        datasets_digest(payload)
        != (directory / "manifest.sha256").read_text(encoding="ascii").strip()
    ):
        raise ValueError("저장 메타데이터 지문이 달라 확인이 필요합니다.")
    manifest = json.loads(payload.decode("utf-8"))
    expected = {
        "original.csv",
        "sessions_original.csv",
        "sessions.csv",
        "assignments.csv",
        "train.csv",
        "validation.csv",
    }
    if set(manifest["files"]) != expected or manifest["dataset_id"] != directory.name:
        raise ValueError("저장된 데이터셋 구조 또는 버전이 달라 확인이 필요합니다.")
    for name, expected_sha in manifest["files"].items():
        path = directory / name
        if path.is_symlink() or datasets_digest(path.read_bytes()) != expected_sha:
            raise ValueError("저장된 데이터셋 파일 지문이 다릅니다: " + name)
    return manifest

# 과거 검증 행과 세션을 새 학습 자료로 재사용하지 않도록 차단
def datasets_check_reservations(check, dataset_id, source, storage=preparation_LOCAL_ROOT):
    import pandas as pd

    storage = Path(storage)
    errors = []
    if not check.ready:
        return errors
    train = check.assignments[check.assignments.partition.eq("train")]
    for directory in sorted((storage / "datasets").glob("dataset_*")):
        manifest = datasets_read_manifest(directory)
        if directory.name == dataset_id:
            continue
        assignments = pd.read_csv(directory / "assignments.csv", dtype={"session_id": str})
        reserved = assignments[assignments.partition.eq("validation")]
        if set(train.near_feature_sha256) & set(reserved.near_feature_sha256):
            errors.append(
                "과거 등록에서 검증용으로 예약한 행이 신규 학습에 포함됩니다: " + directory.name
            )
        if manifest["provenance"]["source"] == source.strip() and set(train.session_id) & set(
            reserved.session_id
        ):
            errors.append("과거 검증 세션을 신규 학습으로 재사용할 수 없습니다: " + directory.name)
    return errors

# 저장 직전 품질·출처·기존 학습 중복을 다시 확인
def datasets_register_dataset(
    payload,
    session_payload,
    filename,
    source,
    truth_method,
    confirmed,
    warnings_accepted,
    storage=preparation_LOCAL_ROOT,
):
    storage = Path(storage)
    reference = preparation_load_training_reference()
    check = preparation_inspect_candidate(
        payload, session_payload, source, truth_method, confirmed, reference
    )
    if not check.ready:
        raise ValueError("데이터 준비 조건 미충족: " + " / ".join(check.errors + check.holds))
    if check.warnings and (not warnings_accepted):
        raise ValueError("품질 경고를 확인하고 승인해야 합니다.")
    dataset_id, provenance = datasets_identity(payload, session_payload, source, truth_method)
    destination = storage / "datasets" / dataset_id
    if destination.exists():
        return (datasets_read_manifest(destination), False)
    storage.mkdir(parents=True, exist_ok=True)
    lock = storage / "registration.lock"
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise ValueError(
            "다른 데이터 등록이 진행 중이거나 잠금이 남았습니다. 관리자 확인이 필요합니다."
        ) from exc
    try:
        os.close(descriptor)
        if destination.exists():
            return (datasets_read_manifest(destination), False)
        errors = datasets_check_reservations(check, dataset_id, source, storage)
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
            data.loc[selected, [*data_FEATURES, "gas"]].to_csv(
                staging / (part + ".csv"), index=False, encoding="utf-8-sig"
            )
        files = {path.name: datasets_digest(path.read_bytes()) for path in staging.iterdir()}
        assignments = check.assignments
        manifest = {
            "schema_version": 1,
            "dataset_id": dataset_id,
            "dataset_version": dataset_id,
            "registered_at_utc": datetime.now(timezone.utc).isoformat(),
            "original_filename": PureWindowsPath(filename).name,
            "original_sha256": check.data.digest,
            "policy": preparation_POLICY,
            "provenance": provenance,
            "truth_confirmed_by_operator": bool(confirmed),
            "warnings_accepted": bool(warnings_accepted),
            "quality": check.summary,
            "warnings": check.warnings,
            "split_rule": "최신 한 세션을 validation, 이전 세션을 train으로 고정",
            "row_order": "원본 input_row 순서를 각 분할에서 유지",
            "reference_files": dict(reference.files),
            "reference_rows": reference.rows,
            "leakage_checks": {
                "cross_partition_feature_overlap": 0,
                "session_overlap": 0,
                "reference_feature_or_near_overlap": 0,
                "prior_validation_reuse": False,
            },
            "partition_rows": assignments.partition.value_counts().astype(int).to_dict(),
            "preprocessing_fitted": False,
            "new_model_fits": 0,
            "independent_final_test": False,
            "physical_independence_verified": False,
            "duplicate_check_scope": "공식 Train 5933행과 완전·근접·관측된 결측 표본 비교",
            "limits": [
                "동일·근접 수치와 자기신고 출처만 검사하며 물리적 표본의 독립성을 증명하지 못함",
                "외부 시험으로 확인한 정답인지 소프트웨어가 보증하지 못함",
                "검증 자료는 개발용이며 독립 최종 Test로 지정하지 않음",
            ],
            "files": files,
        }
        (staging / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8"
        )
        (staging / "manifest.sha256").write_text(
            datasets_digest((staging / "manifest.json").read_bytes()), encoding="ascii"
        )
        destination.parent.mkdir(exist_ok=True)
        os.rename(staging, destination)
        datasets_read_manifest(destination)
        return (manifest, True)
    finally:
        lock.unlink()

# 7. 재학습 입력과 누수 검사

# 자료 구조 및 동작 정의
@dataclass
class training_TrainingData:
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
def training_dataset_directory(dataset_id, storage=preparation_LOCAL_ROOT):
    if not re.fullmatch("dataset_[0-9a-f]{24}", dataset_id):
        raise ValueError("등록 데이터셋ID 형식이 다릅니다.")
    parent = Path(storage) / "datasets"
    directory = parent / dataset_id
    if directory.resolve().parent != parent.resolve() or directory.is_symlink():
        raise ValueError("외부 연결 데이터셋은 허용하지 않습니다.")
    if not directory.is_dir():
        raise ValueError("등록된20-A 데이터셋이 없습니다.")
    return directory

# 화면 표시 전 필수 등록 정보 확인
def training_validate_header(manifest):
    provenance = manifest.get("provenance", {})
    if not all(
        (
            isinstance(provenance.get(key), str) and provenance[key].strip()
            for key in ["source", "truth_method"]
        )
    ):
        raise ValueError("출처 또는 정답 확인 방법이 없습니다.")
    quality = manifest.get("quality", {})
    if not isinstance(quality.get("sessions"), list) or len(quality["sessions"]) < 2:
        raise ValueError("세션 기록이 부족합니다.")

# 선택 화면은 등록 파일을 수정하지 않고 메타데이터만 읽음
def training_list_datasets(storage=preparation_LOCAL_ROOT):
    rows = []
    for directory in sorted((Path(storage) / "datasets").glob("dataset_*")):
        try:
            training_dataset_directory(directory.name, storage)
            manifest = datasets_read_manifest(directory)
            training_validate_header(manifest)
            rows.append(dict(dataset_id=directory.name, manifest=manifest, error=None))
        except (OSError, ValueError, KeyError) as exc:
            rows.append(dict(dataset_id=directory.name, manifest=None, error=str(exc)))
    return rows

# 열·행 순서·숫자값을 원본에서 다시 만든 분리 결과와 대조
def training_same_frame(actual, expected, name):
    try:
        pd.testing.assert_frame_equal(
            actual.reset_index(drop=True),
            expected.reset_index(drop=True),
            check_dtype=False,
            check_exact=True,
        )
    except AssertionError as exc:
        raise ValueError(name + " 저장값이 원본 또는 고정 분리와 다릅니다.") from exc

# 저장 CSV를 원래 수치 정밀도로 불러오기
def training_read_frame(directory, name, **kwargs):
    return pd.read_csv(directory / name, float_precision="round_trip", **kwargs)


# 기존5933행의 특징과 정답을 검증된 참조에서 복원
def training_official_training_frame(reference):
    if reference.rows != 5933 or reference.values.shape != (5933, 128):
        raise ValueError("공식 학습 자료5933행을 확인할 수 없습니다.")
    frame = pd.DataFrame(reference.values, columns=data_FEATURES)
    labels = dict(reference.labeled)
    try:
        target = np.array([labels[key] for key in preparation_fingerprints(frame)], dtype=int)
    except KeyError as exc:
        raise ValueError("공식 특징과 가스 정답 대응이 다릅니다.") from exc
    if set(target) != set(data_GASES):
        raise ValueError("공식 학습 자료에6종 가스가 필요합니다.")
    return (frame, target)

# 20-A 통과 여부만 믿지 않고 동일 정책을 재실행
def training_load_training_data(dataset_id, storage=preparation_LOCAL_ROOT):
    directory = training_dataset_directory(dataset_id, storage)
    manifest = datasets_read_manifest(directory)
    training_validate_header(manifest)
    original_sha = hashing_sha256_bytes((directory / "manifest.json").read_bytes())
    if (
        manifest.get("schema_version") != 1
        or manifest.get("policy") != preparation_POLICY
        or manifest.get("truth_confirmed_by_operator") is not True
    ):
        raise ValueError("20-A 정책 또는 실제 정답 확인 기록이 없습니다.")
    provenance = manifest["provenance"]
    source, method = (provenance["source"], provenance["truth_method"])
    original = (directory / "original.csv").read_bytes()
    sessions = (directory / "sessions_original.csv").read_bytes()
    computed_id, computed_provenance = datasets_identity(original, sessions, source, method)
    if computed_id != dataset_id or computed_provenance != provenance:
        raise ValueError("데이터셋ID·원본 지문·출처가 일치하지 않습니다.")
    if manifest.get("original_sha256") != hashing_sha256_bytes(original):
        raise ValueError("원본 지문 기록이 다릅니다.")
    reference = preparation_load_training_reference()
    check = preparation_inspect_candidate(original, sessions, source, method, True, reference)
    if not check.ready:
        raise ValueError("20-A 재검증 실패: " + " / ".join(check.errors + check.holds))
    if check.warnings and manifest.get("warnings_accepted") is not True:
        raise ValueError("기존 품질 경고 확인 기록이 없습니다.")
    if (
        manifest.get("quality") != check.summary
        or manifest.get("warnings") != check.warnings
        or manifest.get("preprocessing_fitted") is not False
        or (manifest.get("new_model_fits") != 0)
    ):
        raise ValueError("20-A 품질·전처리 기록이 원본 재검사와 다릅니다.")
    if (
        check.summary["duplicate_extra"]
        or pd.Series(preparation_fingerprints(check.data.features, near=True)).duplicated().any()
    ):
        raise ValueError("학습 자료에 중복 또는 매우 가까운 표본이 있어 중단합니다.")
    errors = datasets_check_reservations(check, dataset_id, source, storage)
    if errors:
        raise ValueError(" / ".join(errors))
    if (
        manifest.get("reference_files") != dict(reference.files)
        or manifest.get("reference_rows") != reference.rows
    ):
        raise ValueError("기존 학습 자료 검사 범위 기록이 다릅니다.")
    if manifest.get("partition_rows") != check.assignments.partition.value_counts().to_dict():
        raise ValueError("Train·Validation 표본 수 기록이 다릅니다.")
    training_same_frame(
        training_read_frame(directory, "sessions.csv", dtype={"session_id": str}),
        check.sessions,
        "세션",
    )
    training_same_frame(
        training_read_frame(directory, "assignments.csv", dtype={"session_id": str}),
        check.assignments,
        "분리",
    )
    full = check.data.features.copy()
    full["gas"] = check.data.truth
    parts = {}
    for part in ["train", "validation"]:
        expected = full.loc[check.assignments.partition.eq(part)]
        stored = training_read_frame(directory, part + ".csv")
        if list(stored.columns) != [*data_FEATURES, "gas"]:
            raise ValueError("입력 특징·정답 열 또는 순서가 다릅니다.")
        training_same_frame(stored, expected, part)
        if set(stored.gas) != set(data_GASES):
            raise ValueError(part + "에6종 가스가 필요합니다.")
        parts[part] = stored
    if hashing_sha256_bytes((directory / "manifest.json").read_bytes()) != original_sha:
        raise ValueError("검사 중 데이터셋이 변경됐습니다.")
    return training_TrainingData(
        directory,
        manifest,
        original_sha,
        reference,
        parts["train"][data_FEATURES],
        parts["train"].gas.to_numpy(dtype=int),
        parts["validation"][data_FEATURES],
        parts["validation"].gas.to_numpy(dtype=int),
        check.assignments,
        check.warnings,
    )

# 8. 동일 검증 자료의 모델 비교

evaluation_LABELS = list(data_GASES)
evaluation_RECALL_DROP_NOTICE = 0.05
evaluation_MIN_VALIDATION_SUPPORT = 5

# 모든 모델에 같은 정답·클래스 순서 적용
def evaluation_evaluate_model(model, features, target):
    predicted = model.predict(features)
    precision, recall, f1, support = precision_recall_fscore_support(
        target, predicted, labels=evaluation_LABELS, zero_division=0
    )
    classes = pd.DataFrame(
        dict(
            gas_id=evaluation_LABELS,
            gas=list(data_GASES.values()),
            precision=precision,
            recall=recall,
            f1=f1,
            support=support,
            predicted_count=[int((predicted == gas).sum()) for gas in evaluation_LABELS],
        )
    )
    result = dict(
        accuracy=float(accuracy_score(target, predicted)),
        macro_f1=float(
            f1_score(target, predicted, labels=evaluation_LABELS, average="macro", zero_division=0)
        ),
        weighted_f1=float(
            f1_score(
                target, predicted, labels=evaluation_LABELS, average="weighted", zero_division=0
            )
        ),
        rows=len(target),
    )
    matrix = confusion_matrix(target, predicted, labels=evaluation_LABELS)
    auc_rows, curve_rows = ([], [])
    classifier = model.named_steps["classifier"]
    reason = None
    if classifier.decision_function_shape != "ovr":
        reason = "OVR 클래스 점수 형식이 아님"
    elif list(model.classes_) != evaluation_LABELS:
        reason = "모델 클래스 열 대응이 다름"
    scores = None if reason else model.decision_function(features)
    if scores is not None and (scores.shape != (len(target), 6) or not np.isfinite(scores).all()):
        reason, scores = ("유효한6개 클래스 점수 열이 아님", None)
    for column, gas in enumerate(evaluation_LABELS):
        binary = np.asarray(target) == gas
        positives, negatives = (int(binary.sum()), int((~binary).sum()))
        unavailable = reason or ("양성·음성 각5개 미만" if min(positives, negatives) < 5 else None)
        auc = None
        if not unavailable:
            auc = float(roc_auc_score(binary, scores[:, column]))
            false_positive, true_positive, thresholds = roc_curve(binary, scores[:, column])
            for fp, tp, threshold in zip(false_positive, true_positive, thresholds):
                curve_rows.append(
                    dict(
                        gas_id=gas,
                        fpr=float(fp),
                        tpr=float(tp),
                        threshold=None if np.isinf(threshold) else float(threshold),
                        threshold_is_infinite=bool(np.isinf(threshold)),
                    )
                )
        auc_rows.append(
            dict(
                gas_id=gas,
                gas=data_GASES[gas],
                positives=positives,
                negatives=negatives,
                auc=auc,
                unavailable_reason=unavailable,
            )
        )
    result["roc_note"] = (
        "SVC OVR 변환 결정점수의 클래스별 이진 ROC; 확률·자동 임계값·드리프트 판정 아님"
    )
    result["score_argmax_disagrees_with_predict"] = (
        int((np.array(evaluation_LABELS)[scores.argmax(axis=1)] != predicted).sum())
        if scores is not None
        else None
    )
    return (result, classes, matrix, predicted, pd.DataFrame(auc_rows), pd.DataFrame(curve_rows))


# 관찰한 점수 변화와 승인 가능 여부를 분리
def evaluation_compare(baseline, candidate, old_classes, new_classes, manifest):
    delta = candidate["macro_f1"] - baseline["macro_f1"]
    change = new_classes[["gas_id", "gas", "support"]].copy()
    for metric in ["precision", "recall", "f1", "predicted_count"]:
        change["official_" + metric] = old_classes[metric]
        change["candidate_" + metric] = new_classes[metric]
        change[metric + "_delta"] = new_classes[metric] - old_classes[metric]
    change["recall_drop_notice"] = change.recall_delta < -evaluation_RECALL_DROP_NOTICE
    reasons = []
    if change.support.lt(evaluation_MIN_VALIDATION_SUPPORT).any():
        reasons.append("일부 가스의Validation 표본이5개 미만")
    if manifest.get("physical_independence_verified") is not True:
        reasons.append("세션의 물리적 독립성은 확인되지 않음")
    reasons.append("단일 개발Validation이며 독립 최종Test가 아님")
    result = dict(
        observed_outcome="향상 관찰" if delta > 0 else "저하 관찰" if delta < 0 else "변화 없음",
        macro_f1_delta=delta,
        accuracy_delta=candidate["accuracy"] - baseline["accuracy"],
        severe_recall_drop_gases=change.loc[change.recall_drop_notice, "gas"].tolist(),
        diagnostic_recall_drop_threshold=evaluation_RECALL_DROP_NOTICE,
        assessment="평가 불충분 · 후보 검토 전용",
        assessment_reasons=reasons,
        approval_eligible=False,
        automatic_replacement=False,
    )
    return (result, change)

# 9. 후보 SVM 학습 및 불변 저장

candidates_STORE = data_ROOT / "models/retraining_candidates"
candidates_VERSION = "candidate_svm_v1"
candidates_FILES = {
    "model.joblib",
    "metrics.csv",
    "class_metrics.csv",
    "class_changes.csv",
    "confusion.csv",
    "predictions.csv",
    "roc_auc.csv",
    "roc_points.csv",
}

# JSON에서NaN을 숫자로 오해하지 않도록 명시
def candidates_json_value(value):
    if isinstance(value, dict):
        return {str(key): candidates_json_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [candidates_json_value(item) for item in value]
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and (not np.isfinite(value)):
        return {"special_float": str(value)}
    return value

# 정렬된 UTF-8 JSON 바이트 생성
def candidates_json_bytes(value):
    return json.dumps(
        candidates_json_value(value), ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False
    ).encode("utf-8")

# 실제 공식 모델의 단계와 설정만 학습 기준으로 사용
def candidates_pipeline_settings(model):
    if not isinstance(model, Pipeline) or [name for name, _ in model.steps] != [
        "imputer",
        "scaler",
        "classifier",
    ]:
        raise ValueError("공식 Pipeline 구조가 다릅니다.")
    if not all(
        (
            isinstance(step, kind)
            for (_, step), kind in zip(model.steps, [SimpleImputer, StandardScaler, SVC])
        )
    ):
        raise ValueError("공식 전처리·분류기 종류가 다릅니다.")
    if list(model.classes_) != list(data_GASES) or list(model.feature_names_in_) != data_FEATURES:
        raise ValueError("공식 특징 순서·가스 매핑이 다릅니다.")
    return {name: step.get_params(deep=False) for name, step in model.steps}

# 모델과 감지기 바이트는 작업 전후 동일해야 함
def candidates_verify_official():
    for path, expected in [
        (service_MODEL_PATH, service_MODEL_SHA),
        (service_DETECTOR_PATH, service_DETECTOR_SHA),
    ]:
        if hashing_sha256_bytes(path.read_bytes()) != expected:
            raise ValueError("공식 모델 또는 감지기 지문이 다릅니다.")

# 후보 ID와 저장 경로 확인
def candidates_candidate_directory(candidate_id, storage=candidates_STORE):
    if not re.fullmatch("candidate_[a-f0-9]{24}", candidate_id):
        raise ValueError("후보ID 형식이 다릅니다.")
    root = Path(storage)
    path = root / candidate_id
    if path.is_symlink() or path.resolve().parent != root.resolve():
        raise ValueError("외부 연결 후보 경로는 허용하지 않습니다.")
    return path

# 로컬 생성 후보의 메타데이터·모든 파일 지문을 대조
def candidates_read_candidate(candidate_id, storage=candidates_STORE, load_model=False):
    directory = candidates_candidate_directory(candidate_id, storage)
    payload = (directory / "manifest.json").read_bytes()
    if (
        hashing_sha256_bytes(payload)
        != (directory / "manifest.sha256").read_text(encoding="ascii").strip()
    ):
        raise ValueError("후보 메타데이터 지문이 다릅니다.")
    meta = json.loads(payload)
    if (
        meta["candidate_id"] != candidate_id
        or meta["status"] != "completed_review_only"
        or set(meta["files"]) != candidates_FILES
        or (meta["official_model_sha256"] != service_MODEL_SHA)
    ):
        raise ValueError("후보 버전·구조·상태가 다릅니다.")
    expected_id = "candidate_" + hashing_sha256_bytes(candidates_json_bytes(meta["request"]))[:24]
    if (
        expected_id != candidate_id
        or meta["candidate_model_sha256"] != meta["files"]["model.joblib"]
        or meta["review"]["approval_eligible"] is not False
        or (meta["review"]["automatic_replacement"] is not False)
    ):
        raise ValueError("후보 요청·모델 지문·검토 전용 상태가 다릅니다.")
    for name, expected in meta["files"].items():
        path = directory / name
        if path.is_symlink() or hashing_sha256_bytes(path.read_bytes()) != expected:
            raise ValueError("후보 파일 지문이 다릅니다: " + name)
    result = dict(metadata=meta, directory=directory)
    for name in [
        "metrics",
        "class_metrics",
        "class_changes",
        "confusion",
        "roc_auc",
        "roc_points",
    ]:
        try:
            result[name] = pd.read_csv(directory / (name + ".csv"))
        except pd.errors.EmptyDataError:
            result[name] = pd.DataFrame()
    if load_model:
        candidates_verify_official()
        model = portable_joblib_load(directory / "model.joblib")
        settings = candidates_pipeline_settings(model)
        if candidates_json_value(settings) != meta["pipeline_settings"]:
            raise ValueError("후보 모델 설정이 기록과 다릅니다.")
        result["model"] = model
    return result

# 저장 후보 목록과 검증 오류 수집
def candidates_list_candidates(storage=candidates_STORE, dataset_id=None):
    rows = []
    for directory in sorted(Path(storage).glob("candidate_*")):
        try:
            item = candidates_read_candidate(directory.name, storage)
            if dataset_id is None or item["metadata"]["dataset_id"] == dataset_id:
                rows.append(item)
        except (OSError, ValueError, KeyError) as exc:
            rows.append(dict(error=str(exc), candidate_id=directory.name))
    return rows

# 이번 작업이 만든 비공개 임시 폴더만 정리
def candidates_discard_staging(staging, root):
    if staging is None or not staging.exists():
        return
    if staging.resolve().parent != root.resolve() or not staging.name.startswith(
        ".staging_candidate_"
    ):
        raise ValueError("임시 정리 경로 불일치")
    allowed = candidates_FILES | {"manifest.json", "manifest.sha256"}
    for path in staging.iterdir():
        if path.name not in allowed or path.is_symlink() or (not path.is_file()):
            raise ValueError("알 수 없는 임시 파일은 삭제하지 않습니다.")
        path.unlink()
    staging.rmdir()

# 명시적 요청 한 번에 고정 설정 후보 하나만 학습
def candidates_train_candidate(
    dataset_id,
    *,
    feature_contract_confirmed,
    dataset_storage=preparation_LOCAL_ROOT,
    candidate_storage=candidates_STORE,
    synthetic_only=False,
    progress=None,
):
    if feature_contract_confirmed is not True:
        raise ValueError("128개 특징의 정의·순서·단위가 공식 자료와 같음을 확인해야 합니다.")
    root = Path(candidate_storage)
    if root.is_symlink():
        raise ValueError("연결된 후보 저장소는 허용하지 않습니다.")
    root.mkdir(parents=True, exist_ok=True)
    lock = root / "training.lock"
    token = uuid.uuid4().hex
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise ValueError("다른 후보 학습이 진행 중이거나 잠금 확인이 필요합니다.") from exc
    with os.fdopen(descriptor, "w", encoding="ascii") as stream:
        stream.write(token)
    staging = None
    try:
        notify = progress or (lambda message: None)
        notify("불변 데이터셋과 기존5933행 재검증")
        data = training_load_training_data(dataset_id, dataset_storage)
        official = service_load_models().classifier
        settings = candidates_pipeline_settings(official)
        request = dict(
            version=candidates_VERSION,
            dataset_id=dataset_id,
            dataset_manifest_sha256=data.manifest_sha,
            official_model_sha256=service_MODEL_SHA,
            pipeline=settings,
            sklearn_version=sklearn.__version__,
            synthetic_only=bool(synthetic_only),
            feature_contract_confirmed=True,
        )
        candidate_id = "candidate_" + hashing_sha256_bytes(candidates_json_bytes(request))[:24]
        destination = candidates_candidate_directory(candidate_id, root)
        if destination.exists():
            saved = candidates_read_candidate(candidate_id, root, load_model=True)
            if saved["metadata"]["request"] != candidates_json_value(request):
                raise ValueError("후보ID 충돌: 덮어쓰지 않습니다.")
            saved["reused"] = True
            return saved
        base_x, base_y = training_official_training_frame(data.reference)
        train_x = pd.concat([base_x, data.train_x], ignore_index=True)
        train_y = np.concatenate([base_y, data.train_y])
        if pd.Series(preparation_fingerprints(train_x, near=True)).duplicated().any():
            raise ValueError("결합 Train에 중복이 있어 학습을 중단합니다.")
        notify("Train 자료만으로 전처리와 후보SVM 학습")
        candidate = clone(official)
        started = time.perf_counter()
        with threadpool_limits(limits=1):
            # 결합 Train에서만 전처리 및 후보 학습
            candidate.fit(train_x, train_y)
        fit_seconds = time.perf_counter() - started
        if list(candidate.classes_) != list(data_GASES) or candidate.named_steps[
            "scaler"
        ].n_samples_seen_ != len(train_x):
            raise ValueError("후보 클래스·전처리 학습 표본 수 불일치")
        notify("동일한 신규Validation에서 기존·후보 모델 비교")
        evaluated, rows = ({}, {})
        for label, model in [("official", official), ("candidate", candidate)]:
            started = time.perf_counter()
            with threadpool_limits(limits=1):
                evaluated[label] = evaluation_evaluate_model(
                    model, data.validation_x, data.validation_y
                )
            evaluated[label][0]["predict_and_metrics_seconds"] = time.perf_counter() - started
            rows[label] = dict(model=label, **evaluated[label][0])
        review, changes = evaluation_compare(
            evaluated["official"][0],
            evaluated["candidate"][0],
            evaluated["official"][1],
            evaluated["candidate"][1],
            data.manifest,
        )
        candidates_verify_official()
        datasets_read_manifest(data.directory)
        if (
            hashing_sha256_bytes((data.directory / "manifest.json").read_bytes())
            != data.manifest_sha
        ):
            raise ValueError("학습 중 데이터셋이 변경됐습니다.")
        notify("후보 파일과 재로딩 예측 확인 후 불변 저장")
        staging = Path(tempfile.mkdtemp(prefix=".staging_candidate_", dir=root))
        joblib.dump(candidate, staging / "model.joblib", compress=3)
        loaded = portable_joblib_load(staging / "model.joblib")
        np.testing.assert_array_equal(loaded.predict(data.validation_x), evaluated["candidate"][3])
        pd.DataFrame(list(rows.values())).to_csv(
            staging / "metrics.csv", index=False, encoding="utf-8-sig"
        )
        changes.to_csv(staging / "class_changes.csv", index=False, encoding="utf-8-sig")
        classes, matrices, aucs, curves = ([], [], [], [])
        for label, result in evaluated.items():
            classes.append(result[1].assign(model=label))
            aucs.append(result[4].assign(model=label))
            if not result[5].empty:
                curves.append(result[5].assign(model=label))
            for actual_index, actual in enumerate(data_GASES):
                for predicted_index, predicted in enumerate(data_GASES):
                    matrices.append(
                        dict(
                            model=label,
                            actual_gas=actual,
                            predicted_gas=predicted,
                            n=int(result[2][actual_index, predicted_index]),
                        )
                    )
        pd.concat(classes).to_csv(staging / "class_metrics.csv", index=False, encoding="utf-8-sig")
        pd.concat(aucs).to_csv(staging / "roc_auc.csv", index=False, encoding="utf-8-sig")
        curve_table = (
            pd.concat(curves)
            if curves
            else pd.DataFrame(
                columns=["gas_id", "fpr", "tpr", "threshold", "threshold_is_infinite", "model"]
            )
        )
        curve_table.to_csv(staging / "roc_points.csv", index=False, encoding="utf-8-sig")
        pd.DataFrame(matrices).to_csv(staging / "confusion.csv", index=False, encoding="utf-8-sig")
        prediction = data.assignments.loc[
            data.assignments.partition.eq("validation"), ["row_id", "gas"]
        ].copy()
        prediction["official"] = evaluated["official"][3]
        prediction["candidate"] = evaluated["candidate"][3]
        prediction.to_csv(staging / "predictions.csv", index=False, encoding="utf-8-sig")
        meta = dict(
            schema_version=1,
            version=candidates_VERSION,
            candidate_id=candidate_id,
            status="completed_review_only",
            created_at_utc=datetime.now(timezone.utc).isoformat(),
            request=request,
            dataset_id=dataset_id,
            dataset_manifest_sha256=data.manifest_sha,
            dataset_file_hashes=data.manifest["files"],
            dataset_provenance=data.manifest["provenance"],
            dataset_partition_rows=data.manifest["partition_rows"],
            sessions=data.manifest["quality"]["sessions"],
            synthetic_only=bool(synthetic_only),
            official_model_path=str(service_MODEL_PATH),
            official_model_sha256=service_MODEL_SHA,
            detector_sha256=service_DETECTOR_SHA,
            pipeline_settings=settings,
            sklearn_version=sklearn.__version__,
            base_rows=len(base_x),
            new_train_rows=len(data.train_x),
            fitted_rows=len(train_x),
            validation_rows=len(data.validation_x),
            train_class_counts=pd.Series(train_y).value_counts().sort_index().to_dict(),
            effective_class_weights=dict(
                zip(candidate.classes_, candidate.named_steps["classifier"].class_weight_)
            ),
            fit_seconds=fit_seconds,
            review=review,
            metrics=rows,
            validation_fitted=False,
            hyperparameter_search=False,
            feature_contract_confirmed=True,
            feature_unit_verification="관리자 확인; 물리적 단위·정답·독립성 자동 보증 불가",
            candidate_model_sha256=hashing_sha256_bytes((staging / "model.joblib").read_bytes()),
            prediction_reload_exact=True,
            warnings=data.warnings,
            preprocessing_audit=dict(
                fitted_rows=len(train_x),
                base_batches=[1, 2, 3, 4, 5, 6],
                combined_feature_sha256=hashing_sha256_bytes(
                    train_x.to_numpy(dtype="<f8").tobytes()
                ),
                new_train_row_ids=data.assignments.loc[
                    data.assignments.partition.eq("train"), "row_id"
                ].tolist(),
                validation_row_ids=prediction.row_id.tolist(),
            ),
            files={
                path.name: hashing_sha256_bytes(path.read_bytes()) for path in staging.iterdir()
            },
        )
        (staging / "manifest.json").write_bytes(candidates_json_bytes(meta))
        (staging / "manifest.sha256").write_text(
            hashing_sha256_bytes((staging / "manifest.json").read_bytes()), encoding="ascii"
        )
        candidates_verify_official()
        os.rename(staging, destination)
        staging = None
        saved = candidates_read_candidate(candidate_id, root, load_model=True)
        saved["reused"] = False
        return saved
    finally:
        try:
            candidates_discard_staging(staging, root)
        finally:
            if lock.exists() and lock.read_text(encoding="ascii") == token:
                lock.unlink()

# 10. 수동 승인·버전·롤백

registry_REGISTRY = data_ROOT / "data/model_registry"

# 현재 UTC 시각 기록
def registry_now():
    return datetime.now(timezone.utc).isoformat()

# 승인자는 인증된 계정이 아닌 로컬 사용자 확인으로 기록
def registry_evidence_check(evidence):
    required = ["source", "truth", "independence"]
    if not isinstance(evidence, dict) or any(
        (
            not isinstance(evidence.get(key), str) or len(evidence[key].strip()) < 10
            for key in required
        )
    ):
        raise ValueError("출처·정답·검증 세션 독립성의 확인 근거를 각각 작성해야 합니다.")
    return {key: evidence[key].strip() for key in required}

# 자료 구조 및 동작 정의
class registry_ModelRegistry:

    # 저장 경로 및 기본 상태 설정
    def __init__(
        self,
        root=registry_REGISTRY,
        candidate_store=candidates_STORE,
        dataset_store=preparation_LOCAL_ROOT,
        *,
        testing=False,
    ):
        self.root = Path(root)
        self.candidates = Path(candidate_store)
        self.datasets = Path(dataset_store)
        self.testing = testing
        if testing:
            temporary = Path(tempfile.gettempdir()).resolve()
            for path in [self.root, self.candidates, self.datasets]:
                if not path.resolve().is_relative_to(temporary):
                    raise ValueError("테스트 모드는 시스템 임시 경로 안에서만 허용됩니다.")
        if self.root.is_symlink():
            raise ValueError("연결된 운영 저장소는 허용하지 않습니다.")
        self.path = self.root / "registry.json"

    @staticmethod
    # 고정 Model A 설명 정보 반환
    def official():
        return dict(
            kind="official",
            name="Model A / B_SVM_balanced",
            model_sha256=service_MODEL_SHA,
            candidate_id=None,
            dataset_id=None,
        )

    @contextmanager
    # 공유 잠금으로 동시 운영 변경 차단
    def locked(self):
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / "registry.lock"
        token = uuid.uuid4().hex
        try:
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise ValueError("다른 운영 변경이 진행 중이거나 잠금 확인이 필요합니다.") from exc
        with os.fdopen(descriptor, "w", encoding="ascii") as stream:
            stream.write(token)
        try:
            yield
        finally:
            if path.exists() and path.read_text(encoding="ascii") == token:
                path.unlink()

    # 전체 운영 상태를 임시 파일에서 원자적으로 교체
    def save(self, state):
        raw = candidates_json_bytes(
            dict(payload=state, sha256=hashing_sha256_bytes(candidates_json_bytes(state)))
        )
        descriptor, name = tempfile.mkstemp(prefix=".pending_", dir=self.root)
        temporary = Path(name)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
        finally:
            if temporary.exists():
                temporary.unlink()

    # 운영 이력이 없는 경우에만 최초 상태 생성
    def initialize(self):
        with self.locked():
            if self.path.exists():
                return self.read()
            candidates_verify_official()
            state = dict(schema=1, test_environment=self.testing, events=[])
            self.append(state, "initialize", self.official(), None, None)
            self.save(state)
            return state

    # 운영 이력 및 해시 연결 확인
    def read(self):
        envelope = json.loads(self.path.read_bytes())
        state = envelope["payload"]
        if hashing_sha256_bytes(candidates_json_bytes(state)) != envelope["sha256"]:
            raise ValueError("운영 매니페스트 지문이 다릅니다.")
        if (
            state["schema"] != 1
            or state["test_environment"] is not self.testing
            or (not state["events"])
        ):
            raise ValueError("운영 매니페스트 환경·버전이 다릅니다.")
        previous = None
        for event in state["events"]:
            copy = dict(event)
            digest = copy.pop("sha256")
            if (
                copy["previous_event_sha256"] != previous
                or hashing_sha256_bytes(candidates_json_bytes(copy)) != digest
            ):
                raise ValueError("운영 모델 이력이 손상됐습니다.")
            previous = digest
        if state["active"] != state["events"][-1]["version"]:
            raise ValueError("운영 포인터와 마지막 이력이 다릅니다.")
        return state

    # 이전 해시와 연결한 운영 이벤트 추가
    def append(self, state, action, descriptor, previous, details):
        event_id = "version_" + uuid.uuid4().hex
        version = dict(version_id=event_id, applied_at_utc=registry_now(), model=descriptor)
        event = dict(
            action=action,
            version=version,
            previous_version_id=previous,
            details=details,
            actor="local_user_not_authenticated",
            previous_event_sha256=state["events"][-1]["sha256"] if state["events"] else None,
        )
        event["sha256"] = hashing_sha256_bytes(candidates_json_bytes(event))
        state["events"].append(event)
        state["active"] = version
        return version

    # 검증된 모델 ID에서 로컬 경로 결정
    def model_path(self, descriptor):
        if descriptor["kind"] == "official":
            if descriptor != self.official():
                raise ValueError("Model A 설명 정보가 다릅니다.")
            return service_MODEL_PATH
        if descriptor["kind"] != "candidate":
            raise ValueError("알 수 없는 운영 모델 종류입니다.")
        item = candidates_read_candidate(descriptor["candidate_id"], self.candidates)
        meta = item["metadata"]
        if (
            meta["candidate_model_sha256"] != descriptor["model_sha256"]
            or hashing_sha256_bytes((item["directory"] / "manifest.json").read_bytes())
            != descriptor["candidate_manifest_sha256"]
            or meta["dataset_id"] != descriptor["dataset_id"]
        ):
            raise ValueError("운영 후보의 기록 지문이 다릅니다.")
        if meta["synthetic_only"] and (not self.testing):
            raise ValueError("합성 후보는 운영에서 사용할 수 없습니다.")
        return item["directory"] / "model.joblib"

    # 현재 모델 파일과 저장 지문 대조
    def validate_version(self, version):
        path = self.model_path(version["model"])
        if (
            not path.is_file()
            or path.is_symlink()
            or hashing_sha256_bytes(path.read_bytes()) != version["model"]["model_sha256"]
        ):
            raise ValueError("운영 모델 파일이 없거나 지문이 다릅니다.")
        return path

    # 모델 로딩 후 특징·클래스 대응 확인
    def load_version(self, version):
        path = self.validate_version(version)
        model = portable_joblib_load(path)
        candidates_pipeline_settings(model)
        probe = pd.DataFrame(np.zeros((1, 128)), columns=data_FEATURES)
        predicted = model.predict(probe)
        if len(predicted) != 1 or int(predicted[0]) not in data_GASES:
            raise ValueError("128개 특징 입력·6종 가스 출력 검사를 통과하지 못했습니다.")
        return model

    # 현재 운영 버전 및 무결성 확인
    def current(self):
        version = self.read()["active"]
        self.validate_version(version)
        return version

    # 결합 Train 통계와 저장 전처리 통계 대조
    def training_audit(self, item, data):
        meta, model = (item["metadata"], item["model"])
        base, _ = training_official_training_frame(data.reference)
        train = pd.concat([base, data.train_x], ignore_index=True)
        audit = meta["preprocessing_audit"]
        if (
            meta["dataset_manifest_sha256"] != data.manifest_sha
            or meta["dataset_file_hashes"] != data.manifest["files"]
            or meta["validation_fitted"] is not False
            or (meta["hyperparameter_search"] is not False)
            or (meta["feature_contract_confirmed"] is not True)
            or (meta["fitted_rows"] != len(train))
            or (
                audit["combined_feature_sha256"]
                != hashing_sha256_bytes(train.to_numpy(dtype="<f8").tobytes())
            )
            or (
                audit["validation_row_ids"]
                != data.assignments.loc[
                    data.assignments.partition.eq("validation"), "row_id"
                ].tolist()
            )
        ):
            raise ValueError("후보의 데이터셋·학습·검증 분리 기록이 다릅니다.")
        imputer, scaler = (model.named_steps["imputer"], model.named_steps["scaler"])
        np.testing.assert_allclose(imputer.statistics_, np.nanmedian(train, axis=0))
        values = imputer.transform(train)
        np.testing.assert_allclose(scaler.mean_, values.mean(axis=0), rtol=1e-10, atol=1e-10)
        np.testing.assert_allclose(scaler.var_, values.var(axis=0), rtol=1e-10, atol=1e-10)
        if scaler.n_samples_seen_ != len(train):
            raise ValueError("Train 외 전처리 학습 가능성이 있습니다.")

    # 동일 검증 자료 및 승인 조건 재확인
    def review(self, candidate_id, evidence=None):
        version = self.current()
        item = candidates_read_candidate(candidate_id, self.candidates, load_model=True)
        meta = item["metadata"]
        data = training_load_training_data(meta["dataset_id"], self.datasets)
        self.training_audit(item, data)
        current = evaluation_evaluate_model(
            self.load_version(version), data.validation_x, data.validation_y
        )
        candidate = evaluation_evaluate_model(item["model"], data.validation_x, data.validation_y)
        original = meta["metrics"]["candidate"]
        for metric in ["accuracy", "macro_f1", "weighted_f1"]:
            if not np.isclose(candidate[0][metric], original[metric], rtol=0, atol=1e-12):
                raise ValueError("저장된 후보 평가값이 재계산 결과와 다릅니다.")
        if not np.array_equal(
            candidate[3], pd.read_csv(item["directory"] / "predictions.csv").candidate
        ):
            raise ValueError("저장된 후보 예측을 재현하지 못했습니다.")
        reasons = []
        text = json.dumps(meta["dataset_provenance"], ensure_ascii=False).lower()
        synthetic = meta["synthetic_only"] or any(
            (word in text for word in ["synthetic", "known_generator", "합성"])
        )
        if synthetic and (not self.testing):
            reasons.append("합성 후보는 실제 운영 모델로 적용할 수 없음")
        if candidate[0]["macro_f1"] < current[0]["macro_f1"]:
            reasons.append("동일 Validation에서 후보 Macro F1이 현재 운영 모델보다 낮음")
        if candidate[0]["macro_f1"] < meta["metrics"]["official"]["macro_f1"]:
            reasons.append("20-B 기준 Model A 대비 Macro F1 개선 조건 미달")
        try:
            confirmed_evidence = registry_evidence_check(evidence)
        except ValueError as exc:
            confirmed_evidence = None
            reasons.append(str(exc))
        changes = candidate[1][["gas", "support", "recall"]].rename(
            columns={"recall": "candidate_recall"}
        )
        changes["current_recall"] = current[1].recall.to_numpy()
        changes["recall_delta"] = changes.candidate_recall - changes.current_recall
        descriptor = dict(
            kind="candidate",
            name=candidate_id,
            model_sha256=meta["candidate_model_sha256"],
            candidate_id=candidate_id,
            dataset_id=meta["dataset_id"],
            candidate_manifest_sha256=hashing_sha256_bytes(
                (item["directory"] / "manifest.json").read_bytes()
            ),
        )
        token = hashing_sha256_bytes(
            candidates_json_bytes(
                dict(
                    active=version,
                    candidate=descriptor,
                    dataset=data.manifest_sha,
                    evidence=confirmed_evidence,
                    current_macro=current[0]["macro_f1"],
                    candidate_macro=candidate[0]["macro_f1"],
                )
            )
        )
        return dict(
            eligible=not reasons,
            reasons=reasons,
            token=token,
            active=version,
            descriptor=descriptor,
            dataset_manifest_sha256=data.manifest_sha,
            current=current,
            candidate=candidate,
            changes=changes,
            evidence=confirmed_evidence,
            synthetic=bool(synthetic),
        )

    # 재검사 후 수동 승인 및 원자적 전환
    def activate(
        self,
        candidate_id,
        *,
        confirmed,
        evidence,
        expected_version,
        comparison_token,
        preflight=None,
    ):
        if confirmed is not True:
            raise ValueError("운영 모델 변경 확인이 필요합니다.")
        with self.locked():
            state = self.read()
            if state["active"]["version_id"] != expected_version:
                raise ValueError("현재 모델이 변경됐습니다. 다시 비교해 주세요.")
            result = self.review(candidate_id, evidence)
            if not result["eligible"]:
                raise ValueError(" / ".join(result["reasons"]))
            if result["token"] != comparison_token:
                raise ValueError("비교 정보가 변경됐습니다. 다시 비교해 주세요.")
            if state["active"]["model"]["model_sha256"] == result["descriptor"]["model_sha256"]:
                raise ValueError("이미 같은 모델이 적용돼 있습니다.")
            details = dict(
                candidate_id=candidate_id,
                dataset_manifest_sha256=result["dataset_manifest_sha256"],
                confirmation_evidence=result["evidence"],
                evidence_status="local_operator_declaration_not_external_certification",
                comparison_token=result["token"],
                current_metrics=result["current"][0],
                candidate_metrics=result["candidate"][0],
                recall_changes=result["changes"].to_dict("records"),
                independent_final_test=False,
                synthetic_test_only=result["synthetic"],
            )
            version = self.append(
                state, "activate", result["descriptor"], expected_version, details
            )
            self.load_version(version)
            if preflight:
                preflight(version)
            self.save(state)
            return version

    # 과거 적용 버전으로 복구하며 새 이력 기록
    def rollback(self, target_version, *, confirmed, expected_version, preflight=None):
        if confirmed is not True:
            raise ValueError("이전 모델 복구 확인이 필요합니다.")
        with self.locked():
            state = self.read()
            if state["active"]["version_id"] != expected_version:
                raise ValueError("현재 모델이 변경됐습니다. 다시 확인해 주세요.")
            matches = [
                event["version"]
                for event in state["events"]
                if event["version"]["version_id"] == target_version
            ]
            if not matches:
                raise ValueError("복구 대상은 기존 적용 이력에서 선택해야 합니다.")
            target = matches[0]
            if target["model"] == state["active"]["model"]:
                raise ValueError("이미 현재 사용 중인 모델입니다.")
            version = self.append(
                state,
                "rollback",
                target["model"],
                expected_version,
                dict(restored_from_version=target_version),
            )
            self.load_version(version)
            if preflight:
                preflight(version)
            self.save(state)
            return version


# 11. 운영 버전별 모델 캐시

# 고정 감지기 캐시 유지
@st.cache_resource(show_spinner=False, max_entries=1)
def runtime_fixed_detector():
    return service_load_models().detector

# 운영 버전별 분류기 캐시 유지
@st.cache_resource(show_spinner=False, max_entries=8)
def runtime_cached_classifier(
    version_json, registry_root, candidate_store, dataset_store, testing
):
    manager = registry_ModelRegistry(
        registry_root, candidate_store, dataset_store, testing=testing
    )
    return manager.load_version(json.loads(version_json))

# 전환 전에 새 캐시 로딩까지 성공해야 포인터 저장 허용
def runtime_load_bundle(version, manager):
    model = runtime_cached_classifier(
        json.dumps(version, sort_keys=True),
        str(manager.root),
        str(manager.candidates),
        str(manager.datasets),
        manager.testing,
    )
    return service_ModelBundle(
        model,
        runtime_fixed_detector(),
        version["model"]["name"],
        version["model"]["model_sha256"],
        version["version_id"],
        version["applied_at_utc"],
    )

# 현재 운영 버전의 분류기와 감지기 준비
def runtime_active_bundle(manager=None):
    manager = manager or registry_ModelRegistry()
    return runtime_load_bundle(manager.current(), manager)

# 12. 공통 표 표시 및 후보 학습 화면

# 화면 표의 공통 너비만 설정하며 개별 서식과 인덱스는 유지
def ui_show_table(table, **options):
    return st.dataframe(table, width="stretch", **options)

candidate_ui_DATA_STORAGE = preparation_LOCAL_ROOT
candidate_ui_CANDIDATE_STORAGE = candidates_STORE

# 다른 데이터셋의 검사·결과가 화면에 남지 않도록 초기화
def candidate_ui_reset_candidate_state(state, token):
    if state.get("candidate_selection_token") == token:
        return False
    for key in [
        "candidate_check",
        "candidate_receipt",
        "candidate_contract",
        "candidate_history",
        "candidate_roc_gas",
    ]:
        state.pop(key, None)
    state["candidate_selection_token"] = token
    return True

# 지표 변화와 평가의 한계를 함께 표시
def candidate_ui_render_result(item):
    meta = item["metadata"]
    st.subheader("기존 모델과 후보 비교")
    if meta["synthetic_only"]:
        st.warning("합성 기능 검증용 결과입니다. 실제 센서 성능 개선을 검증하지 않았습니다.")
    official, candidate = (meta["metrics"]["official"], meta["metrics"]["candidate"])
    a, b, c = st.columns(3)
    a.metric("기존 Macro F1", f"{official['macro_f1']:.2%}")
    b.metric(
        "후보 Macro F1",
        f"{candidate['macro_f1']:.2%}",
        f"{100 * meta['review']['macro_f1_delta']:+.2f}%p",
    )
    c.metric("동일 검증 표본", f"{meta['validation_rows']:,}개")
    st.write(meta["review"]["observed_outcome"])
    st.info(meta["review"]["assessment"] + " · 자동 승인·교체하지 않습니다.")
    for reason in meta["review"]["assessment_reasons"]:
        st.caption(reason)
    drops = meta["review"]["severe_recall_drop_gases"]
    if drops:
        st.warning("Recall이5%p 초과 하락한 가스: " + ", ".join(drops))
    st.caption("5%p는 손실을 눈에 띄게 알리는 진단 기준이며20-C 승인 기준이 아닙니다.")
    ui_show_table(
        item["metrics"].rename(
            columns={
                "model": "모델",
                "accuracy": "Accuracy",
                "macro_f1": "Macro F1",
                "weighted_f1": "Weighted F1",
                "rows": "검증 표본 수",
            }
        ),
        hide_index=True,
    )
    st.subheader("가스별 Recall·Precision·F1·표본 수")
    ui_show_table(
        item["class_changes"].rename(
            columns={
                "gas": "가스",
                "support": "정답 표본 수",
                "official_recall": "기존 Recall",
                "candidate_recall": "후보 Recall",
                "recall_delta": "Recall 차이",
                "official_f1": "기존 F1",
                "candidate_f1": "후보 F1",
            }
        ),
        hide_index=True,
    )
    for name, label in [("official", "기존 Model A"), ("candidate", "후보 SVM")]:
        sub = item["confusion"][item["confusion"].model.eq(name)]
        matrix = sub.pivot(index="actual_gas", columns="predicted_gas", values="n")
        matrix = matrix.rename(index=data_GASES, columns=data_GASES)
        st.write(label + " Confusion Matrix · 행: 실제 / 열: 예측")
        ui_show_table(matrix)
    with st.expander("보조 ROC/AUC · 확률이 아닌 결정점수"):
        st.caption(
            "클래스별 One-vs-Rest 순위 평가입니다. Macro F1·Recall을 대체하거나 예측 임계값을 바꾸지 않습니다."
        )
        ui_show_table(item["roc_auc"], hide_index=True)
        curves = item["roc_points"]
        if not curves.empty:
            gas = st.selectbox(
                "ROC를 확인할 가스",
                list(data_GASES),
                format_func=lambda value: data_GASES[value],
                key="candidate_roc_gas",
            )
            sub = curves[curves.gas_id.eq(gas)]
            chart = (
                alt.Chart(sub)
                .mark_line()
                .encode(
                    x=alt.X("fpr:Q", title="False Positive Rate", scale=alt.Scale(domain=[0, 1])),
                    y=alt.Y("tpr:Q", title="True Positive Rate", scale=alt.Scale(domain=[0, 1])),
                    color=alt.Color("model:N", title="모델"),
                    tooltip=["model:N", "fpr:Q", "tpr:Q"],
                )
                .properties(title=data_GASES[gas] + " · 신규Validation OvR ROC", height=320)
            )
            st.altair_chart(chart, width="stretch")
    with st.expander("후보 저장·전처리·학습 정보"):
        st.write("후보ID: " + meta["candidate_id"])
        st.write("생성 시각(UTC): " + meta["created_at_utc"])
        st.write("데이터셋ID: " + meta["dataset_id"])
        st.write("후보 경로: " + str(item["directory"] / "model.joblib"))
        st.write("평가 경로: " + str(item["directory"]))
        st.code(meta["candidate_model_sha256"])
        st.json(meta)
    st.download_button(
        "후보 비교표 CSV 다운로드",
        item["class_changes"].to_csv(index=False).encode("utf-8-sig"),
        file_name="candidate_class_comparison.csv",
        mime="text/csv",
        key="candidate_comparison_download",
        on_click="ignore",
    )

# 등록 데이터 선택 및 후보 학습 화면 구성
def candidate_ui_render_candidates():
    st.button("등록 데이터셋 목록 새로고침", key="candidate_refresh")
    st.subheader("후보 모델 학습·비교 (20-B)")
    st.caption(
        "20-A 등록 데이터만 사용합니다. 공식 모델과 감지기는 유지하며 후보를 자동 승인·교체하지 않습니다."
    )
    try:
        rows = training_list_datasets(candidate_ui_DATA_STORAGE)
    except OSError as exc:
        st.error("데이터셋 저장소 확인 실패: " + str(exc))
        return
    if not rows:
        st.info(
            "등록된 실제 신규 데이터셋이 없습니다. 아래20-A에서 데이터 검증·고정 분리를 먼저 완료해 주세요."
        )
        st.button("후보 모델 학습 시작", key="candidate_train", disabled=True)
        return
    lookup = {row["dataset_id"]: row for row in rows}
    dataset_id = st.selectbox("준비된 데이터셋", list(lookup), key="candidate_dataset")
    row = lookup[dataset_id]
    if row["error"]:
        candidate_ui_reset_candidate_state(st.session_state, dataset_id + ":invalid")
        st.error("무결성 확인 실패: " + row["error"])
        st.button("후보 모델 학습 시작", key="candidate_train", disabled=True)
        return
    manifest = row["manifest"]
    token = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    candidate_ui_reset_candidate_state(st.session_state, token)
    st.write("데이터셋ID: " + dataset_id)
    st.write("출처: " + manifest["provenance"]["source"])
    st.write("실제 정답 확인 방식: " + manifest["provenance"]["truth_method"])
    st.write(manifest["partition_rows"])
    ui_show_table(pd.DataFrame(manifest["quality"]["sessions"]), hide_index=True)
    support = pd.DataFrame(
        {part: manifest["quality"][part + "_counts"] for part in ["train", "validation"]}
    )
    support.index = [data_GASES[int(value)] for value in support.index]
    ui_show_table(support)
    if st.button("재학습 조건 다시 검사", key="candidate_validate"):
        try:
            with st.spinner("원본·분리·세션·기존5933행 중복 재검증 중…"):
                check = training_load_training_data(dataset_id, candidate_ui_DATA_STORAGE)
            st.session_state["candidate_check"] = check.manifest_sha
            st.success("원본 지문과 시간순 분리 조건 재검증 통과")
        except (OSError, ValueError, KeyError) as exc:
            st.session_state.pop("candidate_check", None)
            st.error("재학습 보류: " + str(exc))
    compatible = st.checkbox(
        "128개 특징의 정의·순서·측정 단위가 기존 공식 학습 자료와 같음을 별도로 확인했습니다.",
        key="candidate_contract",
    )
    st.caption(
        "이 확인은 소프트웨어의 단위 검증이나 물리적 독립성 증명이 아닙니다. 다르면 학습하지 마세요."
    )
    busy = st.session_state.get("candidate_busy", False)
    allowed = bool(st.session_state.get("candidate_check")) and compatible and (not busy)
    if st.button(
        "후보 모델 학습 시작", key="candidate_train", disabled=not allowed, type="primary"
    ):
        st.session_state["candidate_busy"] = True
        status = st.empty()
        try:
            with st.spinner("고정 설정으로 후보 하나를 학습·검증 중…"):
                item = candidates_train_candidate(
                    dataset_id,
                    feature_contract_confirmed=True,
                    dataset_storage=candidate_ui_DATA_STORAGE,
                    candidate_storage=candidate_ui_CANDIDATE_STORAGE,
                    progress=status.info,
                )
            st.session_state["candidate_receipt"] = item["metadata"]["candidate_id"]
            st.success(
                "동일 요청의 기존 후보를 재사용했습니다."
                if item["reused"]
                else "후보 저장 완료 · 공식 모델은 유지합니다."
            )
        except Exception as exc:
            st.error("후보 학습·저장 실패: " + str(exc))
        finally:
            st.session_state["candidate_busy"] = False
            status.empty()
    try:
        saved = candidates_list_candidates(candidate_ui_CANDIDATE_STORAGE, dataset_id)
        valid = [item for item in saved if "error" not in item]
        for item in saved:
            if "error" in item:
                st.error("후보 이력 확인 실패: " + item["error"])
        if valid:
            choices = {item["metadata"]["candidate_id"]: item for item in valid}
            selected = st.selectbox("저장된 후보 이력", list(choices), key="candidate_history")
            candidate_ui_render_result(choices[selected])
    except (OSError, ValueError, KeyError) as exc:
        st.error("후보 결과 확인 실패: " + str(exc))
    st.divider()


# 13. 데이터 등록 화면

preparation_ui_NAMES = ["에탄올", "에틸렌", "암모니아", "아세트알데하이드", "아세톤", "톨루엔"]

# 입력 변경 시 이전 검사와 등록 결과 폐기
def preparation_ui_reset_preparation(state, token):
    if state.get("preparation_token") != token:
        state.pop("preparation_check", None)
        state.pop("preparation_receipt", None)
        state.pop("preparation_accepted", None)
        state["preparation_token"] = token
        return True
    return False

# 일반 분석과 별도 업로드·상태로 데이터 준비
def preparation_ui_render_management():
    candidate_ui_render_candidates()
    st.subheader("신규 정답 데이터 준비 (20-A)")
    with st.expander("등록 데이터셋 이력"):
        for item in training_list_datasets(preparation_LOCAL_ROOT):
            if item.get("error"):
                st.error(str(item["error"]))
            else:
                st.write(item["manifest"] if "manifest" in item else item)
    st.info(
        "로컬 관리자용 데이터 준비 화면입니다. 사용자 인증은 제공하지 않습니다. 이번 단계에서는 재학습하지 않습니다."
    )
    st.caption("데이터 업로드 → 품질 검사 → 구성 확인 → 세션별 분리 → 불변 버전 저장")
    upload = st.file_uploader(
        "신규 실제 정답 CSV", type=["csv"], key="preparation_csv", max_upload_size=20
    )
    session_file = st.file_uploader(
        "행별 세션 정보 CSV", type=["csv"], key="preparation_sessions", max_upload_size=20
    )
    payload = upload.getvalue() if upload else None
    session_payload = session_file.getvalue() if session_file else None
    file_token = hashlib.sha256((payload or b"") + (session_payload or b"")).hexdigest()
    if st.session_state.get("preparation_file_token") != file_token:
        st.session_state.pop("preparation_confirmed", None)
        st.session_state["preparation_file_token"] = file_token
    with st.expander("등록 파일 형식 안내"):
        st.write(
            "센서 CSV: f001~f128, gas 필수. gas는 1~6 실제 정답입니다. AI 예측값을 정답으로 등록하지 마세요."
        )
        st.write(
            "세션 CSV: input_row, session_id, measured_at. 모든 측정 번호에 세션과 시간대가 있는 실제 시각이 필요합니다."
        )
        st.code("input_row,session_id,measured_at\n1,session_01,2026-10-28T09:00:00+09:00")
        st.caption(
            "시각 예시는 형식 안내입니다. 실제 수집 시각을 입력하세요. 한 세션·시기 누락·기간 겹침이면 준비를 보류합니다."
        )
    source = st.text_input(
        "데이터 출처", key="preparation_source", placeholder="측정 장비·기관·실험 식별 정보"
    )
    method = st.text_input(
        "실제 정답 확인 방식",
        key="preparation_truth",
        placeholder="기준 가스 시험·별도 검증 기록 등",
    )
    confirmed = st.checkbox(
        "AI 예측이 아닌 실제 시험·별도 확인으로 확보한 정답임을 확인합니다.",
        key="preparation_confirmed",
    )
    payload = upload.getvalue() if upload else None
    session_payload = session_file.getvalue() if session_file else None
    token = hashlib.sha256(
        json.dumps(
            {
                "file": hashlib.sha256(payload or b"").hexdigest(),
                "sessions": hashlib.sha256(session_payload or b"").hexdigest(),
                "source": source,
                "method": method,
                "confirmed": confirmed,
                "filename": upload.name if upload else None,
            },
            sort_keys=True,
        ).encode()
    ).hexdigest()
    preparation_ui_reset_preparation(st.session_state, token)
    if st.button(
        "데이터 품질 검사", key="preparation_inspect", disabled=payload is None, type="primary"
    ):
        with st.spinner("입력과 기존 학습 자료의 중복 확인 중…"):
            try:
                reference = preparation_load_training_reference()
                reference_problem = None
            except (OSError, ValueError, KeyError) as exc:
                reference, reference_problem = (None, str(exc))
            check = preparation_inspect_candidate(
                payload, session_payload, source, method, confirmed, reference
            )
            if reference_problem:
                check.holds.append("기존 학습 자료 확인 실패: " + reference_problem)
            if check.ready:
                try:
                    check.holds.extend(
                        datasets_check_reservations(
                            check,
                            datasets_identity(payload, session_payload, source, method)[0],
                            source,
                        )
                    )
                except (OSError, ValueError, KeyError) as exc:
                    check.holds.append("이전 데이터 등록 이력을 확인할 수 없습니다: " + str(exc))
            st.session_state["preparation_check"] = check
    check = st.session_state.get("preparation_check")
    if check is None:
        st.write("실제 정답과 세션 정보를 준비한 뒤 품질 검사를 눌러 주세요.")
        return
    if check.errors:
        st.error("데이터 검증 실패")
        for message in check.errors:
            st.error(message)
    elif check.warnings:
        st.warning("품질 경고 존재 · 관리자 확인 필요")
    else:
        st.success("데이터 형식·품질 검사 통과")
    for warning in check.warnings:
        st.warning(warning)
    for hold in check.holds:
        st.info("분리 조건 미충족 · " + hold)
    if check.summary:
        summary = check.summary
        st.subheader("데이터 구성 확인")
        st.write(
            f"총 {summary['rows']:,}개의 측정값을 검사했습니다. 실제 정답 열이 포함되어 있습니다."
        )
        a, b = st.columns(2)
        a.metric(
            "결측 특징값",
            f"{summary['missing_cells']:,}개",
            help=f"전체 특징값 중 {summary['missing_fraction']:.3%}",
        )
        b.metric("중복 추가 행", f"{summary['duplicate_extra']:,}개")
        counts = pd.DataFrame(
            {
                "가스": preparation_ui_NAMES,
                "표본 수": [summary["gas_counts"][str(g)] for g in data_GASES],
            }
        )
        counts["비율"] = counts["표본 수"] / summary["rows"]
        st.altair_chart(
            alt.Chart(counts)
            .mark_bar(color="#167c91")
            .encode(
                x=alt.X("표본 수:Q", title="측정 샘플 수"),
                y=alt.Y(
                    "가스:N", title=None, sort=preparation_ui_NAMES, axis=alt.Axis(labelLimit=0)
                ),
                tooltip=["가스:N", "표본 수:Q", alt.Tooltip("비율:Q", format=".1%")],
            )
            .properties(height=260),
            width="stretch",
        )
        ui_show_table(counts, hide_index=True)
        if "sessions" in summary:
            st.write("등록된 수집 세션과 실제 측정 기간")
            ui_show_table(
                pd.DataFrame(summary["sessions"]).rename(
                    columns={
                        "session_id": "세션",
                        "min": "첫 측정 시각 (UTC)",
                        "max": "마지막 측정 시각 (UTC)",
                    }
                ),
                hide_index=True,
            )
        if check.assignments is not None:
            st.subheader("학습·검증 고정 계획")
            st.write(
                "최신 한 세션을 검증용, 나머지 과거 세션을 학습용으로 고정합니다. 비율을 임의로 바꾸지 않습니다."
            )
            table = (
                check.assignments.groupby(["partition", "session_id", "gas"])
                .size()
                .rename("표본 수")
                .reset_index()
            )
            ui_show_table(
                table.rename(
                    columns={"partition": "분리", "session_id": "세션", "gas": "가스 ID"}
                ),
                hide_index=True,
            )
        with st.expander("품질·중복 검사 기술 정보"):
            st.json(summary)
            st.caption(
                "정확 수치와 유효숫자 12자리 근접 검사를 수행합니다. 반올림·가공·미신고 출처의 모든 중복을 증명할 수는 없습니다."
            )
    accepted = st.checkbox(
        "품질 경고와 출처 확인의 한계를 검토했습니다.", key="preparation_accepted"
    )
    allowed = check.ready and (not check.warnings or accepted)
    if st.button("고정 분리 데이터셋 저장", key="preparation_save", disabled=not allowed):
        try:
            manifest, created = datasets_register_dataset(
                payload,
                session_payload,
                upload.name,
                source,
                method,
                confirmed,
                accepted,
                storage=preparation_LOCAL_ROOT,
            )
            st.session_state["preparation_receipt"] = manifest
            st.success(
                "데이터 준비 완료" if created else "동일한 불변 데이터셋이 이미 등록되어 있습니다."
            )
        except (OSError, ValueError, KeyError) as exc:
            st.error("저장 보류: " + str(exc))
    receipt = st.session_state.get("preparation_receipt")
    if receipt:
        st.success("데이터 준비 완료 · 재학습은 수행하지 않았습니다.")
        st.write("데이터셋 버전: " + receipt["dataset_id"])
        st.write(receipt["partition_rows"])
        st.caption(
            "원본·세션·분리 행 목록·Train/Validation CSV와 지문을 로컬에 저장했습니다. 독립 최종 Test는 아닙니다."
        )
    elif check.ready:
        st.info("분리 조건 확인 완료 · 경고 확인 후 저장해야 준비가 완료됩니다.")
    with st.expander("후속 단계와 사용 범위"):
        st.write(
            "20-B는 저장된 Train에서만 전처리와 후보 모델을 학습해야 합니다. Validation은 개발용으로 예약되며 최종 Test가 아닙니다."
        )
        st.caption(
            "원본 데이터와 출처는 Git 제외 경로에 저장합니다. 외부에 공개하려면 별도 인증·접근 제어가 필요합니다."
        )


# 14. 승인·복구 화면

operation_ui_MANAGER_FACTORY = registry_ModelRegistry

# 기존 분석 결과는 지우지 않고 승인 화면의 오래된 확인만 초기화
def operation_ui_reset_review(state, token):
    if state.get("approval_scope") != token:
        for key in ["approval_review", "approval_confirm"]:
            state.pop(key, None)
        state["approval_scope"] = token

# 현재 모델과 후보의 동일 검증 결과 표시
def operation_ui_render_comparison(review):
    ui_show_table(
        pd.DataFrame(
            [
                dict(model="현재 운영 모델", **review["current"][0]),
                dict(model="후보 모델", **review["candidate"][0]),
            ]
        )[["model", "accuracy", "macro_f1", "weighted_f1", "rows"]],
        hide_index=True,
    )
    ui_show_table(review["changes"], hide_index=True)
    drops = review["changes"].query("recall_delta < 0").gas.tolist()
    if drops:
        st.warning("Recall이 하락한 가스: " + ", ".join(drops))
    for label, key in [("현재 운영 모델", "current"), ("후보 모델", "candidate")]:
        st.write(label + " · 혼동행렬 (행: 실제 / 열: 예측)")
        ui_show_table(
            pd.DataFrame(
                review[key][2], index=list(data_GASES.values()), columns=list(data_GASES.values())
            )
        )
    for reason in review["reasons"]:
        st.warning(reason)
    if review["eligible"]:
        st.info("단순 승인 조건 충족 · 독립 최종 성능 검증이나 운영 안전성 인증은 아닙니다.")

# 수동 승인 및 버전 복구 화면 구성
def operation_ui_render_operations():
    st.subheader("운영 모델 승인·버전·복구 (20-C)")
    st.caption("로컬 포트폴리오용 수동 확인입니다. 승인자의 신원을 인증하지 않습니다.")
    manager = operation_ui_MANAGER_FACTORY()
    if manager.testing:
        st.warning("테스트 전용 임시 운영 환경 · 실제 운영 모델에 적용되지 않습니다.")
    try:
        state = manager.read()
    except Exception as exc:
        st.error("운영 매니페스트 확인 실패 · 자동 복구하지 않습니다: " + str(exc))
        return
    active = state["active"]
    st.write("현재 운영 모델: " + active["model"]["name"])
    st.write("버전: " + active["version_id"])
    st.write("적용 시각 (UTC): " + active["applied_at_utc"])
    st.code("모델 SHA-256: " + active["model"]["model_sha256"])
    st.caption("원본 Model A 여부: " + str(active["model"]["kind"] == "official"))
    try:
        manager.validate_version(active)
    except Exception as exc:
        st.error(
            "현재 모델 무결성 오류 · 새 분석은 차단됩니다. 정상 이력으로 복구하세요: " + str(exc)
        )
    st.markdown("#### 후보 선택과 승인")
    rows = candidates_list_candidates(manager.candidates)
    valid = []
    for row in rows:
        if "error" in row:
            st.error("후보 확인 실패: " + row["error"])
        else:
            valid.append(row)
    if not valid:
        st.info(
            "승인할 등록 후보가 없습니다. 합성 기능 검증 후보는 운영 목록에 포함하지 않습니다."
        )
        st.button("후보 모델 승인 및 적용", key="approval_apply", disabled=True)
    else:
        lookup = {row["metadata"]["candidate_id"]: row["metadata"] for row in valid}
        ui_show_table(
            pd.DataFrame(
                [
                    dict(
                        candidate_id=meta["candidate_id"],
                        created_at_utc=meta["created_at_utc"],
                        dataset_id=meta["dataset_id"],
                        status=meta["status"],
                        synthetic_only=meta["synthetic_only"],
                        approval_status=(
                            "실운영 불가: 합성 후보"
                            if meta["synthetic_only"]
                            else "동일 Validation·확인 근거 재검사 필요"
                        ),
                        validation_macro_f1=meta["metrics"]["candidate"]["macro_f1"],
                    )
                    for meta in lookup.values()
                ]
            ),
            hide_index=True,
        )
        selected = st.selectbox("승인 검토 후보", list(lookup), key="approval_candidate")
        meta = lookup[selected]
        if meta["synthetic_only"]:
            st.warning("합성 후보는 실제 운영에 적용할 수 없습니다.")
        st.caption(
            "측정·정답·독립성을 확인할 수 없다면 적용하지 마세요. 입력 근거는 자기신고로 기록됩니다."
        )
        evidence, checks = ({}, [])
        for key, label in [
            ("source", "실제 측정 데이터 출처"),
            ("truth", "실제 가스 정답 확인"),
            ("independence", "검증 세션의 물리적 독립성 확인"),
        ]:
            checks.append(st.checkbox(label + " 완료", key="approval_" + key + "_checked"))
            evidence[key] = st.text_input(label + " 근거 (10자 이상)", key="approval_" + key)
        evidence = evidence if all(checks) else None
        operation_ui_reset_review(
            st.session_state, json.dumps([active, selected, evidence], sort_keys=True)
        )
        if st.button("동일 Validation 승인 조건 검사", key="approval_validate"):
            try:
                with st.spinner("데이터셋·학습 분리·예측 재현·동일 Validation 비교 중…"):
                    st.session_state["approval_review"] = manager.review(selected, evidence)
            except Exception as exc:
                st.session_state.pop("approval_review", None)
                st.error("승인 보류: " + str(exc))
        review = st.session_state.get("approval_review")
        if review:
            operation_ui_render_comparison(review)
        confirmed = st.checkbox(
            "현재 운영 모델을 선택한 후보 모델로 변경합니다. 기존 모델은 보존되며 이전 버전으로 복구할 수 있습니다.",
            key="approval_confirm",
        )
        if st.button(
            "후보 모델 승인 및 적용",
            key="approval_apply",
            type="primary",
            disabled=not (review and review["eligible"] and confirmed),
        ):
            try:
                manager.activate(
                    selected,
                    confirmed=confirmed,
                    evidence=evidence,
                    expected_version=active["version_id"],
                    comparison_token=review["token"],
                    preflight=lambda version: runtime_load_bundle(version, manager),
                )
                st.session_state.pop("approval_review", None)
                st.rerun()
            except Exception as exc:
                st.error("적용 실패 · 운영 매니페스트 유지: " + str(exc))
    st.markdown("#### 버전 이력과 이전 모델 복구")
    ui_show_table(
        pd.DataFrame(
            [
                dict(
                    version_id=event["version"]["version_id"],
                    action=event["action"],
                    applied_at_utc=event["version"]["applied_at_utc"],
                    model=event["version"]["model"]["name"],
                    sha256=event["version"]["model"]["model_sha256"],
                    previous=event["previous_version_id"],
                    candidate_id=event["version"]["model"]["candidate_id"],
                    dataset_id=event["version"]["model"]["dataset_id"],
                )
                for event in state["events"]
            ]
        ),
        hide_index=True,
    )
    previous = {
        event["version"]["version_id"]: event["version"]
        for event in state["events"]
        if event["version"]["model"] != active["model"]
    }
    if not previous:
        st.info("복구할 다른 모델의 적용 이력이 없습니다.")
        st.button("이전 모델로 복구", key="rollback_apply", disabled=True)
    else:
        target = st.selectbox("복구 가능한 이전 버전", list(previous), key="rollback_target")
        scope = active["version_id"] + ":" + target
        if st.session_state.get("rollback_scope") != scope:
            st.session_state.pop("rollback_confirm", None)
            st.session_state["rollback_scope"] = scope
        confirm = st.checkbox(
            "선택한 이전 모델로 복구하고 복구 이력을 남깁니다.", key="rollback_confirm"
        )
        if st.button("이전 모델로 복구", key="rollback_apply", disabled=not confirm):
            try:
                manager.rollback(
                    target,
                    confirmed=confirm,
                    expected_version=active["version_id"],
                    preflight=lambda version: runtime_load_bundle(version, manager),
                )
                st.rerun()
            except Exception as exc:
                st.error("복구 실패 · 운영 매니페스트 유지: " + str(exc))
    st.divider()

# 15. 데이터 분석 및 결과 화면

ui_PAGES = ["데이터 분석", "분석 결과", "상세 분석", "모델 관리"]

ui_GAS_NAMES = dict(
    zip(
        data_GASES.values(),
        [
            "에탄올 (Ethanol)",
            "에틸렌 (Ethylene)",
            "암모니아 (Ammonia)",
            "아세트알데하이드 (Acetaldehyde)",
            "아세톤 (Acetone)",
            "톨루엔 (Toluene)",
        ],
    )
)

# 작은 화면에서도 읽을 수 있는 기본 스타일
def ui_style():
    st.markdown(
        '<style>\n    .stApp {background:#f5f7fb;color:#17283b}\n    [data-testid="stSidebar"] {background:#102b42}\n    [data-testid="stSidebar"] * {color:#edf4fb}\n    .block-container {max-width:1150px;padding-top:4rem}\n    h1,h2,h3 {letter-spacing:-.035em}\n    .hero {background:#102b42;border-radius:18px;padding:28px;margin-bottom:24px}\n    .hero h1 {color:white;font-size:32px;padding:0 0 12px}\n    .hero p {color:#d1e1ef;line-height:1.7;margin:0}\n    [data-testid="stMetric"] {background:white;border:1px solid #dce5ef;border-radius:12px;padding:18px}\n    [data-testid="stMetricValue"] {font-size:28px!important}\n    [data-testid="stMetricLabel"] p {white-space:normal!important}\n    button[kind="primary"] {background:#126e82;border-color:#126e82}\n    div[data-testid="stAlert"] {border-radius:12px}\n    @media(max-width:700px) {\n      .block-container {padding:4rem 1rem 1rem}\n      .hero {padding:20px}.hero h1 {font-size:26px}\n      .st-key-result_metrics [data-testid="stHorizontalBlock"] {display:grid;grid-template-columns:1fr}\n      .st-key-result_metrics [data-testid="stColumn"] {width:100%!important;min-width:0}\n    }\n    </style>',
        unsafe_allow_html=True,
    )

# 실제 결과의 개수로 요약 카드 구성
def ui_result_metrics(result):
    summary = result["summary"]
    with st.container(key="result_metrics"):
        a, b, c = st.columns(3)
        a.metric("분석 완료 · 측정값", f"{summary['input_rows']:,}개")
        b.metric("AI가 예측한 가스", f"{summary['predicted_classes']}종")
        c.metric(
            "기준과 다른 구간",
            f"{summary['alert_windows']}개" if summary["valid_windows"] else "확인 불가",
        )

# 가스 이름을 두 줄로 나눠 좁은 화면에서도 표시
def ui_gas_chart(result):
    table = result["counts"].assign(
        label=lambda frame: frame.gas.map(ui_GAS_NAMES).str.replace(" (", "\n(", regex=False)
    )
    st.markdown("#### 가스별 예측 분포")
    chart = (
        alt.Chart(table)
        .mark_bar(color="#167c91", cornerRadiusEnd=4)
        .encode(
            y=alt.Y(
                "label:N",
                title=None,
                sort=list(table.label),
                axis=alt.Axis(
                    labelExpr="split(datum.label, '\\n')",
                    labelLimit=0,
                    labelFontSize=11,
                    labelLineHeight=14,
                    labelPadding=8,
                ),
            ),
            x=alt.X(
                "n:Q",
                title="측정값 수 (개)",
                axis=alt.Axis(tickCount=4, tickMinStep=1, titlePadding=12),
            ),
            tooltip=[
                alt.Tooltip("gas:N", title="예측 가스"),
                alt.Tooltip("n:Q", title="개수"),
                alt.Tooltip("proportion:Q", title="전체 예측 중 비율", format=".1%"),
            ],
        )
        .properties(height=300)
        .configure_view(stroke=None)
    )
    st.altair_chart(chart, width="stretch")

# 패턴 상태와 다음 행동을 함께 안내
def ui_drift_notice(result):
    summary = result["summary"]
    st.subheader("센서 측정 패턴 확인")
    if summary["alert_windows"]:
        st.warning("⚠️ 기존 기준과 다른 측정 패턴이 발견됐어요.")
        st.write(
            "가스 구성이나 측정 데이터의 묶음 방식도 영향을 줄 수 있습니다. 센서 고장이 확정된 것은 아닙니다."
        )
        action = "측정 조건을 확인하고, 필요하면 기준 가스로 다시 측정하거나 AI 모델의 분류 성능을 점검하세요."
    elif not summary["valid_windows"]:
        if summary["input_rows"] < 100:
            st.info("측정 패턴을 확인하려면 데이터가 더 필요해요.")
            action = "패턴 분석에는 최소 100개의 센서 데이터가 필요합니다. 가스 예측 결과는 확인할 수 있습니다."
        else:
            st.info("입력 데이터의 일부 값 때문에 측정 패턴을 확인할 수 없어요.")
            action = "상세 분석에서 확인 불가 사유를 확인하고, 누락된 센서 값을 점검하세요."
    else:
        st.success("기존 기준과 큰 차이가 감지되지 않았어요.")
        action = "현재 설정된 기준에서 큰 차이는 확인되지 않았습니다. 다만 분류 정확도를 보장하는 결과는 아닙니다."
    if summary["invalid_windows"]:
        st.caption(
            f"{summary['invalid_windows']}개 구간은 확인할 수 없습니다. 상세 분석에서 사유를 확인하세요."
        )
    st.subheader("다음에 할 일")
    st.write(action)

# 원본 점수와 경고 상태를 반응형 그래프로 표시
def ui_drift_chart(result):
    valid = result["windows"].dropna(subset=["score"])
    if valid.empty:
        st.info("표시할 측정 패턴 차이 점수가 없습니다.")
        return
    st.markdown("#### 구간별 측정 패턴 변화")
    st.write("과거에 설정한 기준 데이터와 현재 측정값의 분포를 비교합니다.")
    base = alt.Chart(valid).encode(
        x=alt.X(
            "window:Q",
            title="분석 구간",
            axis=alt.Axis(tickMinStep=1, tickCount=4, titlePadding=12),
        ),
        y=alt.Y(
            "score:Q",
            title="패턴 차이 점수",
            axis=alt.Axis(format=".3f", tickCount=4, titlePadding=10),
        ),
        tooltip=[
            alt.Tooltip("window:Q", title="분석 구간"),
            alt.Tooltip("start_position:Q", title="시작 측정 번호"),
            alt.Tooltip("end_position:Q", title="마지막 측정 번호"),
            alt.Tooltip("score:Q", title="MMD²", format=".7f"),
            alt.Tooltip("status:N", title="분석 상태"),
        ],
    )
    rule = (
        alt.Chart(pd.DataFrame({"threshold": [service_THRESHOLD]}))
        .mark_rule(color="#c43d49", strokeDash=[6, 4])
        .encode(y="threshold:Q", tooltip=[alt.Tooltip("threshold:Q", title="고정 기준")])
    )
    alerts = base.transform_filter(alt.datum.alert == True).mark_point(color="#d77330", size=100)
    st.altair_chart(
        (base.mark_line(point=True, color="#167c91") + rule + alerts)
        .properties(height=280)
        .configure_view(stroke=None),
        width="stretch",
    )
    st.caption(
        f"지표: RFF-MMD² · 빨간 점선: 고정 기준 {service_THRESHOLD} · 주황 점: 기준과 다른 구간"
    )
    st.caption("점수는 확률이나 예상 정확도가 아닙니다. 100행은 실제 시간 길이를 뜻하지 않습니다.")

# 업로드 정답이 있는 경우에만 기존 정책으로 평가 표시
def ui_optional_evaluation(result):
    evaluation = result["evaluation"]
    if evaluation is None:
        st.info("정답 gas 열이 없어 실제 분류 성능을 계산하지 않았습니다.")
        return
    correct = int((result["rows"].gas == result["rows"].predicted_gas_id).sum())
    st.write(
        f"업로드한 정답 데이터 기준 {len(result['rows']):,}개 중 {correct:,}개를 올바르게 분류했습니다."
    )
    st.write("업로드한 실제 가스 정보와 AI의 예측 결과를 비교한 평가입니다.")
    st.caption(
        "기존 학습 자료일 수 있는 업로드 정답과의 비교입니다. 독립적인 미래 시기 성능이 아닙니다."
    )
    a, b = st.columns(2)
    a.metric("정답과 일치한 비율 · Accuracy", f"{evaluation['accuracy']:.2%}")
    b.metric("가스별 분류 성능 종합 점수 · Macro F1", f"{evaluation['macro_f1']:.2%}")
    supported = evaluation["per_class"].query("support > 0")
    c, d = st.columns(2)
    c.metric("Macro Precision · 정답 존재 가스", f"{supported.precision.mean():.2%}")
    d.metric("Macro Recall · 정답 존재 가스", f"{supported.recall.mean():.2%}")
    st.caption(
        f"Macro F1 계산 대상: 정답에 존재하는 {evaluation['supported_classes']}종. support는 정답 표본 수입니다."
    )
    if evaluation["supported_classes"] < 6:
        st.warning(
            "일부 가스의 정답이 없어 이 결과만으로 가스 6종 전체의 분류 성능을 판단할 수 없습니다."
        )
    matrix = (
        evaluation["confusion"]
        .rename_axis("실제 가스")
        .reset_index()
        .melt(id_vars="실제 가스", var_name="예측 가스", value_name="개수")
    )
    matrix["실제 가스"] = matrix["실제 가스"].map(lambda name: ui_GAS_NAMES[name].split(" (")[0])
    matrix["예측 가스"] = matrix["예측 가스"].map(lambda name: ui_GAS_NAMES[name].split(" (")[0])
    st.markdown("#### 실제 가스와 AI 예측 비교")
    st.caption("Confusion Matrix · 숫자는 측정 샘플 수입니다.")
    heat = alt.Chart(matrix).encode(
        x=alt.X(
            "예측 가스:N",
            sort=[name.split(" (")[0] for name in ui_GAS_NAMES.values()],
            axis=alt.Axis(labelAngle=-45, labelLimit=0),
        ),
        y=alt.Y(
            "실제 가스:N",
            sort=[name.split(" (")[0] for name in ui_GAS_NAMES.values()],
            axis=alt.Axis(labelLimit=0),
        ),
        tooltip=["실제 가스:N", "예측 가스:N", "개수:Q"],
    )
    st.altair_chart(
        (
            heat.mark_rect().encode(color=alt.Color("개수:Q", scale=alt.Scale(scheme="blues")))
            + heat.mark_text().encode(text="개수:Q")
        ).properties(height=300),
        width="stretch",
    )
    ui_show_table(evaluation["per_class"], hide_index=True)

# 모델 지문과 해석 범위 제공
def ui_model_notes(result):
    summary = result["summary"]
    st.write("이 분석에 사용한 모델: " + summary["classification_model"])
    st.caption("분석 당시 버전: " + summary["classification_version"])
    st.code(
        f"분류 모델 SHA-256: {summary['classification_sha256']}\n감지기 SHA-256: {service_DETECTOR_SHA}\n감지기 버전: rff_mmd_v1\n고정 임계값: {service_THRESHOLD}\n감지 창: 100행"
    )
    st.write(
        "가스 구성·구간 구성·측정 조건이 점수에 영향을 줄 수 있습니다. 실제 센서 드리프트나 장비 이상을 확정하지 않습니다."
    )
    st.caption(
        "Batch 9–10은 반복 사용한 회고적 자료이며 독립 Test가 아닙니다. 자동 재학습이나 모델 교체는 수행하지 않습니다."
    )

# 원본 결과에서 화면용 한글 요약만 생성
def ui_prediction_table(result):
    rows = result["rows"]
    names = {gas: ui_GAS_NAMES[name].split(" (")[0] for gas, name in data_GASES.items()}
    table = pd.DataFrame(
        {"측정 번호": rows.input_row, "AI 예측 가스": rows.predicted_gas_id.map(names)}
    )
    if "gas" in rows:
        table["실제 가스"] = rows.gas.map(names)
        table["예측 결과"] = (rows.gas == rows.predicted_gas_id).map(
            {True: "일치", False: "불일치"}
        )
    return table

# 경고는 원래 출력값으로 표시하고 점수는 반올림하지 않음
def ui_pattern_table(result):
    rows = result["windows"]
    table = pd.DataFrame(
        {
            "분석 구간": rows.window,
            "측정 범위": rows.start_position.astype(str) + "~" + rows.end_position.astype(str),
            "패턴 차이 점수": rows.score,
            "결과": rows.apply(
                lambda row: (
                    "평가 불가"
                    if row.status == "평가 불가"
                    else "기준과 다른 패턴" if row.alert else "기준 범위"
                ),
                axis=1,
            ),
            "시작 측정 번호": rows.start_position,
            "마지막 측정 번호": rows.end_position,
            "분석한 측정값 수": rows.n,
            "결측값 수": rows.missing_cells,
        }
    )
    return table

# 핵심 결과와 원본 특징·기술 정보를 분리
def ui_details(result):
    with st.expander("가스 예측 결과", expanded=True):
        st.write(
            "한 행은 하나의 센서 측정 샘플을 의미하며, AI가 각 측정값에 해당하는 가스 종류를 예측합니다."
        )
        st.caption("AI 예측은 실제 가스가 확인됐다는 의미가 아닙니다.")
        table = ui_prediction_table(result)
        if "gas" not in result["rows"]:
            st.info("정답 미제공 · 실제 가스와 일치 여부는 표시하지 않습니다.")
        ui_show_table(
            table,
            hide_index=True,
            column_config={
                "측정 번호": st.column_config.NumberColumn(
                    width="small", format="%d", pinned=True
                ),
                "AI 예측 가스": st.column_config.TextColumn(width="medium"),
                "실제 가스": st.column_config.TextColumn(width="medium"),
                "예측 결과": st.column_config.TextColumn(width="small"),
            },
        )
        with st.expander("측정값 상세 보기"):
            selected = st.number_input(
                "측정 번호 선택", min_value=1, max_value=len(table), value=1, step=1
            )
            selected_row = table.iloc[int(selected) - 1]
            st.write(
                f"측정 번호 **{int(selected_row['측정 번호'])}** · AI 예측 가스 **{selected_row['AI 예측 가스']}**"
            )
            if "실제 가스" in table:
                st.write(f"실제 가스: {selected_row['실제 가스']} · {selected_row['예측 결과']}")
        with st.expander("원본 센서 측정 데이터 보기"):
            st.write(
                "각 행은 하나의 센서 측정 샘플이며, f001~f128은 센서 반응에서 추출한 128개의 특징값입니다."
            )
            st.caption(
                "128개 특징은 가스 128종을 뜻하지 않습니다. 표 내부를 가로로 이동하면 모든 특징을 확인할 수 있습니다."
            )
            mode = st.radio("원본 표시 범위", ["선택한 측정값", "전체 측정값"], horizontal=True)
            raw = result["rows"][["input_row", *data_FEATURES]].rename(
                columns={"input_row": "측정 번호"}
            )
            ui_show_table(
                raw.iloc[[int(selected) - 1]] if mode == "선택한 측정값" else raw,
                hide_index=True,
                column_config={
                    "측정 번호": st.column_config.NumberColumn(width="small", pinned=True),
                    **{
                        name: st.column_config.NumberColumn(width="small", format="%.5g")
                        for name in data_FEATURES
                    },
                },
            )
        with st.expander("가스별 예측 개수"):
            counts = result["counts"].copy()
            counts["gas"] = counts.gas.map(ui_GAS_NAMES)
            ui_show_table(
                counts[["gas", "n", "proportion"]].rename(
                    columns={"gas": "예측 가스", "n": "측정값 수", "proportion": "예측 비율"}
                ),
                hide_index=True,
                column_config={
                    "예측 가스": st.column_config.TextColumn(width="large"),
                    "예측 비율": st.column_config.NumberColumn(format="percent"),
                },
            )
    with st.expander("측정 패턴 분석", expanded=True):
        ui_drift_chart(result)
        st.write(
            f"분석한 구간: {result['summary']['valid_windows']}개 · 패턴 분석에서 제외된 측정값: {result['summary']['excluded_tail_rows']}개"
        )
        if result["windows"].empty:
            st.info(
                "측정 패턴 분석에는 최소 100행이 필요합니다. 가스 예측은 위에서 확인할 수 있습니다."
            )
        else:
            ui_show_table(
                ui_pattern_table(result),
                hide_index=True,
                column_config={
                    "분석 구간": st.column_config.NumberColumn(
                        width="small", format="%d", pinned=True
                    ),
                    "측정 범위": st.column_config.TextColumn(width="small"),
                    "패턴 차이 점수": st.column_config.NumberColumn(width="medium", format="%.6f"),
                    "결과": st.column_config.TextColumn(width="medium"),
                },
            )
        with st.expander("기술 정보 보기"):
            st.code(f"고정 임계값: {service_THRESHOLD}\n감지 창: 100행")
            if not result["windows"].empty:
                ui_show_table(result["windows"], hide_index=True)
            st.caption(
                "평가 불가 사유는 reason 열에 표시됩니다. CSV에는 원래 필드와 전체 정밀도를 유지합니다."
            )
    with st.expander("정답 기반 성능 평가"):
        ui_optional_evaluation(result)
    with st.expander("모델 정보와 검증 범위"):
        ui_model_notes(result)
        ui_show_table(pd.DataFrame([result["summary"]]), hide_index=True)
    with st.expander("분석 결과 다운로드", expanded=True):
        labels = [
            "가스 예측 결과 다운로드",
            "측정 패턴 분석 결과 다운로드",
            "전체 분석 요약 다운로드",
        ]
        for label, (name, data) in zip(labels, service_downloads(result).items()):
            st.download_button(
                label,
                data=data,
                file_name=name,
                mime="text/csv",
                key="download_" + name,
                on_click="ignore",
                width="stretch",
            )
        st.caption(
            "입력 행 순서와 기존 CSV 내용을 유지합니다. 100행 미만의 패턴 CSV에는 제목 행만 포함됩니다."
        )

# 업로드 상태를 유지하며 분석 후 결과 화면으로 이동
def ui_main():
    st.set_page_config(page_title="가스 센서 AI 분석", page_icon="◈", layout="wide")
    ui_style()
    if st.session_state.pop("show_results", False):
        st.session_state["page"] = ui_PAGES[1]
    with st.sidebar:
        st.markdown("### 가스 센서 AI 분석")
        page = st.radio("분석 화면", ui_PAGES, key="page")
        st.caption("① 파일 선택 → ② 분석 시작 → ③ 결과 확인")
    st.markdown(
        "<div class='hero'><h1>가스 센서 AI 분석</h1><p>센서 데이터를 업로드하면 AI가 가스 종류를 분석하고,<br>기존 측정 패턴과 달라진 부분을 확인합니다.</p></div>",
        unsafe_allow_html=True,
    )
    with st.expander("센서 데이터 선택", expanded=page == ui_PAGES[0]):
        upload = st.file_uploader(
            "센서 데이터 CSV", type=["csv"], key="sensor_csv", max_upload_size=20
        )
        payload = upload.getvalue() if upload is not None else None
        digest = hashlib.sha256(payload).hexdigest() if payload is not None else None
        service_reset_on_upload_change(st.session_state, digest)
        preview = None
        if payload is not None:
            try:
                preview = service_read_upload(payload)
                st.success(f"{len(preview.features):,}개의 센서 데이터가 준비되었습니다.")
                with st.expander("입력 데이터 구조와 기본 통계"):
                    st.write(
                        {
                            "행 수": len(preview.features),
                            "특징 수": 128,
                            "결측값 수": preview.missing_cells,
                            "정답 제공": preview.truth is not None,
                        }
                    )
                    ui_show_table(preview.features.describe().T)
                    if preview.truth is not None:
                        counts = (
                            pd.Series(preview.truth)
                            .value_counts()
                            .reindex(data_GASES, fill_value=0)
                        )
                        st.dataframe(
                            pd.DataFrame(
                                {
                                    "가스": list(data_GASES.values()),
                                    "정답 표본 수": counts.to_numpy(),
                                }
                            ),
                            hide_index=True,
                        )
            except service_InputError as exc:
                st.error(str(exc))
        submitted = st.button(
            "분석 시작", key="analyze", type="primary", disabled=preview is None, width="stretch"
        )
        with st.expander("파일 형식 안내"):
            st.write(
                "UTF-8 CSV · f001~f128 센서 열 필수 · 20MB / 20,000행 이하. 정답 gas 열은 선택 사항입니다."
            )
            st.caption(
                "gas: 1 에탄올, 2 에틸렌, 3 암모니아, 4 아세트알데하이드, 5 아세톤, 6 톨루엔. 일부 결측값은 저장 모델의 기존 기준으로 처리합니다. 알 수 없는 열·중복 열·비수치·무한대·전체 결측은 허용하지 않습니다."
            )
        st.caption("파일은 세션 메모리에서 처리합니다. 파일 변경·제거 시 이전 결과를 비웁니다.")
    if submitted:
        st.session_state.pop("analysis", None)
        try:
            with st.spinner("가스 종류와 측정 패턴 분석 중…"):
                st.session_state["analysis"] = service_analyze(preview, runtime_active_bundle())
            st.session_state.pop("analysis_error", None)
            st.session_state["show_results"] = True
            st.rerun()
        except (OSError, ValueError, RuntimeError, OverflowError, KeyError, TypeError):
            st.session_state["analysis_error"] = (
                "분석을 완료하지 못했습니다. 저장 모델과 센서 입력값을 확인해 주세요."
            )
    if "analysis_error" in st.session_state:
        st.error(st.session_state["analysis_error"])
    result = st.session_state.get("analysis")
    st.subheader(page)
    if page == ui_PAGES[3]:
        st.caption("일반 분석용 업로드와 신규 정답 데이터 등록은 서로 분리됩니다.")
        operation_ui_render_operations()
        preparation_ui_render_management()
    elif page == ui_PAGES[0]:
        st.write(
            "CSV를 선택한 뒤 분석 시작을 눌러 주세요. 결과에서 가스 예측, 측정 패턴, 다음 행동을 확인할 수 있습니다."
        )
        st.caption("가스 예측은 한 행부터 가능합니다. 측정 패턴 비교에는 최소 100행이 필요합니다.")
    elif result is None:
        st.info("데이터 분석 화면에서 CSV를 업로드하고 분석을 시작해 주세요.")
    elif page == ui_PAGES[1]:
        ui_result_metrics(result)
        st.caption(
            "분석 모델: "
            + result["summary"]["classification_model"]
            + " · 버전: "
            + result["summary"]["classification_version"]
        )
        st.subheader("AI 가스 분석 결과")
        counts = result["counts"]
        leaders = counts[counts.n == counts.n.max()]
        names = ", ".join(leaders.gas.map(ui_GAS_NAMES))
        st.write(
            f"가장 많이 예측된 가스: **{names}**" + (" · 공동 최다" if len(leaders) > 1 else "")
        )
        top = leaders.iloc[0]
        st.write(
            f"각 {int(top.n):,}개 / 전체 {result['summary']['input_rows']:,}개 ({top.proportion:.1%})"
            if len(leaders) > 1
            else f"{int(top.n):,}개 / 전체 {result['summary']['input_rows']:,}개 ({top.proportion:.1%})"
        )
        ui_gas_chart(result)
        st.caption("모델이 예측한 가스 종류입니다. 실제 가스 존재 여부를 확정한 결과는 아닙니다.")
        ui_drift_notice(result)
        st.caption(
            "행별 결과, 기술 정보, 정답 기반 평가 및 다운로드는 상세 분석에서 확인할 수 있습니다."
        )
    else:
        ui_details(result)
    st.divider()
    st.caption("연구용 분석 서비스 · 측정 패턴 변화는 센서 고장이나 분류 정확도를 확정하지 않음")

# 16. 최초 실행 저장소 준비 및 메인 실행
# 기존 손상 이력은 덮어쓰지 않고 사용자에게 오류 안내
def main():
    manager = registry_ModelRegistry()
    try:
        if not manager.path.exists():
            manager.initialize()
            st.session_state["standalone_initialized"] = True
    except (OSError, ValueError, RuntimeError, KeyError) as exc:
        st.error("초기 운영 저장소 준비 불가: " + str(exc))
        st.info(
            "파일 상단의 모델·자료 준비 안내를 확인하세요. 기존 파일은 자동 교체하지 않습니다."
        )
        st.stop()
    if st.session_state.pop("standalone_initialized", False):
        st.info(
            "새 로컬 운영 저장소를 공식 Model A로 초기화했습니다. 과거 이력은 자동 복구하지 않습니다."
        )
    ui_main()

if __name__ == "__main__":
    main()
