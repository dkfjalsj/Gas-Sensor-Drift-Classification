# 기준 자료에서 정한 RFF-MMD 점수와 고정 임계값으로 분포 변화 감지
# 정답·Batch 정보 없이 CSV 입력 검증 및 경고 생성

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.kernel_approximation import RBFSampler
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.preprocessing import StandardScaler

FEATURES = tuple(f"f{i:03d}" for i in range(1, 129))
MESSAGES = {
    "기준 범위": "입력된 센서 데이터의 분포가 설정된 기준 범위 내에 있습니다. 이는 가스 분류 정확도를 보장하지 않습니다.",
    "분포 변화 감지": "기존 학습 데이터와 다른 센서 측정 분포가 감지되었습니다. 가스 분류 성능 저하 가능성을 확인하기 위해 기준 가스 측정 및 모델 재검증을 권장합니다.",
    "평가 불가": "입력 데이터가 부족하거나 센서 특징 형식이 일치하지 않아 드리프트 평가를 수행할 수 없습니다.",
}


# 특징 이름 확인 후 정해진 순서로 정렬
def validate_features(frame):
    if not isinstance(frame, pd.DataFrame):
        raise ValueError("128개 특징 이름이 있는 DataFrame 필요")
    if frame.columns.has_duplicates:
        raise ValueError("중복 특징 이름")
    if len(frame.columns) != 128 or set(frame.columns) != set(FEATURES):
        raise ValueError("f001~f128만 필요하며 정답·Batch·추가 열은 허용하지 않음")
    data = frame.loc[:, FEATURES].copy()
    if any(pd.api.types.is_bool_dtype(data[c]) for c in FEATURES):
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


class DriftDetector:
    # 감지 설정 초기화
    def __init__(self):
        self.version = "rff_mmd_v1"
        self.window_size = 100
        self.random_state = 42
        self.n_components = 512
        self.bandwidth_sample_limit = 1024
        self.imputer = SimpleImputer(strategy="median")
        self.scaler = StandardScaler()

    # 참조 자료만으로 전처리·커널 폭·기준 평균 계산
    def fit_reference(self, reference):
        if hasattr(self, "reference_mean_"):
            raise ValueError("참조 자료 재적합 금지")
        data = validate_features(reference)
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
            gamma=self.gamma_, n_components=self.n_components,
            random_state=self.random_state,
        )
        embedded = self.rff.fit_transform(values)
        self.reference_mean_ = embedded.mean(axis=0)
        self.metadata_ = {
            "version": self.version, "features": list(FEATURES),
            "reference_n": len(data), "random_state": self.random_state,
            "n_components": self.n_components, "window_size": self.window_size,
            "bandwidth_sample_n": len(take), "distance_epsilon": 1e-12,
            "excluded_near_zero_pairs": int(len(distances) - len(positive)),
            "gamma": self.gamma_, "median_squared_distance": self.median_squared_distance_,
            "reference_missing_cells": int(data.isna().sum().sum()),
            "reference_constant_features": int((np.nanstd(data, axis=0) == 0).sum()),
            "score": "squared L2 distance between RFF means; not probability",
        }
        return self

    # 정확히100개 측정값과 고정 참조 평균의 차이 계산
    def score_window(self, frame):
        if not hasattr(self, "reference_mean_"):
            raise ValueError("참조 자료 적합 전")
        data = validate_features(frame)
        if len(data) != self.window_size:
            raise ValueError("점수 계산에는 정확히100개 행 필요")
        values = self.scaler.transform(self.imputer.transform(data))
        difference = self.rff.transform(values).mean(axis=0) - self.reference_mean_
        score = float(difference @ difference)
        if not np.isfinite(score):
            raise ValueError("유효하지 않은 점수")
        return score

    # 별도 교정 창의95백분위수를 한 번만 설정
    def calibrate(self, calibration):
        if hasattr(self, "threshold_"):
            raise ValueError("임계값 재설정 금지")
        data = validate_features(calibration)
        n = len(data) // self.window_size
        if n < 10:
            raise ValueError("임계값 산정에는 최소10개 창 필요")
        scores = [self.score_window(data.iloc[i * 100:(i + 1) * 100]) for i in range(n)]
        self.threshold_ = float(np.quantile(scores, 0.95, method="linear"))
        self.metadata_.update({
            "threshold": self.threshold_, "quantile": 0.95,
            "quantile_method": "linear", "calibration_windows": n,
            "calibration_dropped_rows": len(data) % 100,
        })
        return np.asarray(scores)

    # 임계값 경계와 사용자 메시지 판정
    def status(self, score):
        if not hasattr(self, "threshold_"):
            raise ValueError("임계값 설정 전")
        if not np.isfinite(score) or score < 0:
            raise ValueError("유효하지 않은 점수")
        state = "분포 변화 감지" if score > self.threshold_ else "기준 범위"
        return state, MESSAGES[state]

    # 입력 순서를 유지한 비중복100행 창 평가
    def evaluate(self, frame):
        try:
            if not hasattr(self, "threshold_"):
                raise ValueError("임계값 설정 전")
            data = validate_features(frame)
            if len(data) < 100:
                raise ValueError("유효 측정값100개 미만")
        except (ValueError, TypeError) as exc:
            return {"status": "평가 불가", "message": MESSAGES["평가 불가"],
                    "reason": str(exc), "windows": [], "input_rows": len(frame) if hasattr(frame, "__len__") else 0,
                    "valid_windows": 0, "excluded_tail_rows": len(frame) if hasattr(frame, "__len__") else 0}
        windows = []
        for i in range(len(data) // 100):
            piece = data.iloc[i * 100:(i + 1) * 100]
            item = {"window": i + 1, "start_position": i * 100 + 1,
                    "end_position": (i + 1) * 100, "n": 100,
                    "missing_cells": int(piece.isna().sum().sum())}
            try:
                score = self.score_window(piece)
                state, message = self.status(score)
                item.update(score=score, status=state, message=message,
                            alert=state == "분포 변화 감지")
            except ValueError as exc:
                item.update(score=None, status="평가 불가", message=MESSAGES["평가 불가"],
                            alert=None, reason=str(exc))
            windows.append(item)
        valid = [w for w in windows if w["score"] is not None]
        alert_n = sum(w["alert"] for w in valid)
        state = ("평가 불가" if not valid else
                 "분포 변화 감지" if alert_n else "기준 범위")
        return {"status": state, "message": MESSAGES[state], "windows": windows,
                "input_rows": len(data), "valid_windows": len(valid),
                "invalid_windows": len(windows) - len(valid),
                "excluded_tail_rows": len(data) % 100, "alert_windows": alert_n,
                "alert_rate": alert_n / len(valid) if valid else None,
                "threshold": self.threshold_, "schema_reordered": list(frame.columns) != list(FEATURES)}


# 웹앱과 명령행에서 재사용할 CSV 입력 경계
def evaluate_csv(detector, source):
    try:
        frame = pd.read_csv(source, encoding="utf-8-sig")
    except (ValueError, OSError, UnicodeError, pd.errors.ParserError) as exc:
        return {"status": "평가 불가", "message": MESSAGES["평가 불가"],
                "reason": str(exc), "windows": []}
    return detector.evaluate(frame)


# 신뢰할 수 있는 로컬 감지기만 불러오기
def load_detector(path):
    detector = joblib.load(Path(path))
    if not isinstance(detector, DriftDetector) or not hasattr(detector, "threshold_"):
        raise ValueError("지원하지 않는 감지기 파일")
    return detector
