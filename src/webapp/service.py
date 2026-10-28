# CSV 검증·공식 SVM 예측·고정 감지기 호출 및 다운로드 변환
# 업로드는 메모리에서 처리하며 정답은 별도 평가에만 사용

import csv
from dataclasses import dataclass
import hashlib
import io
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_recall_fscore_support

from ..data import ROOT, FEATURES, GASES
from ..drift_detection.detector import load_detector, validate_features

MODEL_PATH = ROOT / "models/temporal_expansion/B_SVM_balanced.joblib"
DETECTOR_PATH = ROOT / "models/drift_detection/rff_mmd_v1.joblib"
MODEL_SHA = "1d6b20c94d1580d799e05ab5a9ce746bdb272d74f70ec2ff964011fffecfde32"
DETECTOR_SHA = "de47661f66c69cdc7553f73acf1df9b721f65771d0301fe69a7a326f814fa4c5"
THRESHOLD = 0.00825701197565701
MAX_BYTES = 20 * 1024 * 1024
MAX_ROWS = 20000
WARNING = ("설정된 참조 데이터와 다른 센서 측정 분포가 감지되었습니다. 가스 구성 및 평가 창 구성 "
           "방식의 영향을 받을 수 있습니다. 실제 센서 드리프트나 가스 분류 성능 저하를 의미하는 것은 "
           "아니므로 필요시 기준 가스 측정과 모델 재검증을 권장합니다.")
NORMAL = "유효한 평가 창의 점수가 설정된 기준 범위 내에 있습니다. 이는 가스 분류 정확도를 보장하지 않습니다."


class InputError(ValueError):
    pass


@dataclass
class ModelBundle:
    classifier: object
    detector: object


@dataclass
class InputData:
    features: pd.DataFrame
    truth: object
    digest: str
    reordered: bool
    missing_cells: int


# 신뢰한 로컬 파일의 지문과 설정을 확인한 뒤 한 번 로딩
def load_models():
    for path, expected in [(MODEL_PATH, MODEL_SHA), (DETECTOR_PATH, DETECTOR_SHA)]:
        if not path.is_file():
            raise RuntimeError("저장 모델을 찾을 수 없습니다. 프로젝트의 models 폴더를 확인해 주세요.")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise RuntimeError("저장 모델 버전이 확인된 버전과 다릅니다. 임의 모델은 사용하지 않습니다.")
    classifier = joblib.load(MODEL_PATH)
    detector = load_detector(DETECTOR_PATH)
    if list(classifier.feature_names_in_) != FEATURES or list(classifier.classes_) != list(GASES):
        raise RuntimeError("공식 모델의 특징 순서 또는 가스 매핑이 일치하지 않습니다.")
    if detector.threshold_ != THRESHOLD or detector.window_size != 100:
        raise RuntimeError("감지기 설정이 기존 고정 조건과 다릅니다.")
    return ModelBundle(classifier, detector)


# 중복 열을 먼저 확인하고 선택적 정답을 명시적으로 분리
def read_upload(payload):
    if not payload or not payload.strip():
        raise InputError("빈 파일입니다. 제목 행과 센서 측정값이 있는 CSV를 선택해 주세요.")
    if len(payload) > MAX_BYTES:
        raise InputError("파일 크기는20MB 이하여야 합니다.")
    try:
        text = payload.decode("utf-8-sig")
    except UnicodeError as exc:
        raise InputError("UTF-8 형식의 CSV가 필요합니다.") from exc
    try:
        reader = csv.reader(io.StringIO(text, newline=""), strict=True)
        header = next(reader)
        if len(header) != len(set(header)):
            raise InputError("중복된 열 이름이 있습니다. 각 특징은 한 번만 포함해 주세요.")
        missing = [name for name in FEATURES if name not in header]
        extra = [name for name in header if name not in FEATURES and name != "gas"]
        if missing:
            raise InputError("필수 특징이 없습니다: " + ", ".join(missing[:8]))
        if extra:
            raise InputError("허용되지 않은 열입니다: " + ", ".join(extra[:8]) + ". 정답 열은 gas만 허용합니다.")
        rows = 0
        for line_n, record in enumerate(reader, 2):
            if len(record) != len(header):
                raise InputError(f"CSV의{line_n}번째 레코드 열 수가 제목과 다릅니다. 빈 행도 확인해 주세요.")
            rows += 1
            if rows > MAX_ROWS:
                raise InputError("한 번에20,000행까지 분석할 수 있습니다.")
        if not rows:
            raise InputError("센서 측정 행이 없습니다. 제목 아래에 데이터를 넣어 주세요.")
        frame = pd.read_csv(io.StringIO(text))
    except (csv.Error, StopIteration, pd.errors.ParserError) as exc:
        raise InputError("CSV 구조를 읽을 수 없습니다. 쉼표와 따옴표를 확인해 주세요.") from exc
    if len(frame) != rows:
        raise InputError("데이터 행을 정확히 읽지 못했습니다. 빈 행과 CSV 구조를 확인해 주세요.")
    truth = None
    if "gas" in frame:
        if pd.api.types.is_bool_dtype(frame.gas):
            raise InputError("gas 정답은1~6의 정수여야 합니다.")
        try:
            labels = pd.to_numeric(frame.gas, errors="raise").to_numpy(dtype=float)
        except (TypeError, ValueError) as exc:
            raise InputError("gas 정답은1~6의 정수여야 합니다. 평가하지 않으려면 gas 열을 제거해 주세요.") from exc
        if not np.isfinite(labels).all() or not np.equal(labels, np.floor(labels)).all() or not np.isin(labels, list(GASES)).all():
            raise InputError("gas 열에 결측 또는1~6 이외의 값이 있습니다. 정답을 확인해 주세요.")
        truth = labels.astype(int)
    feature_names = [name for name in header if name != "gas"]
    try:
        features = validate_features(frame[feature_names])
    except ValueError as exc:
        raise InputError("센서 특징을 확인해 주세요: " + str(exc)) from exc
    return InputData(features, truth, hashlib.sha256(payload).hexdigest(),
                     feature_names != FEATURES, int(features.isna().sum().sum()))


# 업로드 변경 시 이전 결과를 재사용하지 않도록 상태 초기화
def reset_on_upload_change(state, digest):
    if state.get("input_digest") != digest:
        state.pop("analysis", None)
        state.pop("analysis_error", None)
        state["input_digest"] = digest
        return True
    return False


# 저장 모델 추론과 독립적인 분포 감지 수행
def analyze(data, models):
    predicted = np.asarray(models.classifier.predict(data.features), dtype=int)
    if len(predicted) != len(data.features) or not np.isin(predicted, list(GASES)).all():
        raise RuntimeError("모델의 예측 결과를 확인할 수 없습니다.")
    drift = models.detector.evaluate(data.features)
    row_table = data.features.copy()
    row_table.insert(0, "input_row", np.arange(1, len(row_table) + 1))
    if data.truth is not None:
        row_table["gas"] = data.truth
    row_table["predicted_gas_id"] = predicted
    row_table["predicted_gas"] = [GASES[int(g)] for g in predicted]
    row_table["classification_model"] = "Model A / B_SVM_balanced"
    row_table["classification_sha256"] = MODEL_SHA
    row_table["input_sha256"] = data.digest
    counts = pd.DataFrame({"gas_id": list(GASES), "gas": list(GASES.values())})
    counts["n"] = [int((predicted == g).sum()) for g in GASES]
    counts["proportion"] = counts.n / len(predicted)
    window_columns = ["window", "start_position", "end_position", "n", "missing_cells",
                      "score", "status", "alert", "reason"]
    window_table = pd.DataFrame(drift["windows"]).reindex(columns=window_columns)
    window_table["threshold"] = THRESHOLD
    window_table["detector_version"] = "rff_mmd_v1"
    window_table["detector_sha256"] = DETECTOR_SHA
    window_table["window_size"] = 100
    window_table["input_sha256"] = data.digest
    evaluation = None
    if data.truth is not None:
        supported = np.unique(data.truth)
        precision, recall, f1, support = precision_recall_fscore_support(
            data.truth, predicted, labels=list(GASES), zero_division=0)
        evaluation = {
            "accuracy": float(accuracy_score(data.truth, predicted)),
            "macro_f1": float(f1_score(data.truth, predicted, labels=supported, average="macro", zero_division=0)),
            "supported_classes": len(supported),
            "confusion": pd.DataFrame(confusion_matrix(data.truth, predicted, labels=list(GASES)),
                                      index=list(GASES.values()), columns=list(GASES.values())),
            "per_class": pd.DataFrame({"gas": list(GASES.values()), "precision": precision,
                "recall": np.where(support > 0, recall, np.nan),
                "f1": np.where(support > 0, f1, np.nan), "support": support}),
        }
    summary = {
        "input_rows": len(predicted), "predicted_classes": int(counts.n.gt(0).sum()),
        "valid_windows": drift.get("valid_windows", 0),
        "invalid_windows": drift.get("invalid_windows", 0),
        "alert_windows": drift.get("alert_windows", 0),
        "alert_rate": drift.get("alert_rate"), "excluded_tail_rows": drift.get("excluded_tail_rows", 0),
        "distribution_status": drift["status"], "unavailable_reason": drift.get("reason", ""),
        "window_size": 100, "threshold": THRESHOLD, "missing_feature_cells": data.missing_cells,
        "feature_order_rearranged": data.reordered, "classification_model": "Model A / B_SVM_balanced",
        "classification_sha256": MODEL_SHA, "detector_version": "rff_mmd_v1",
        "detector_sha256": DETECTOR_SHA, "input_sha256": data.digest,
        "truth_evaluation_available": evaluation is not None,
    }
    if evaluation:
        summary.update(upload_accuracy=evaluation["accuracy"], upload_macro_f1=evaluation["macro_f1"],
                       truth_supported_classes=evaluation["supported_classes"])
    return {"rows": row_table, "counts": counts, "windows": window_table,
            "drift": drift, "summary": summary, "evaluation": evaluation}


# 사용자 기기로만 전달할 UTF-8 CSV 생성
def export_csv(table):
    return table.to_csv(index=False).encode("utf-8-sig")


def downloads(result):
    return {
        "gas_classification.csv": export_csv(result["rows"]),
        "distribution_windows.csv": export_csv(result["windows"]),
        "analysis_summary.csv": export_csv(pd.DataFrame([result["summary"]])),
    }
