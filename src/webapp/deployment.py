# 공개 배포에서는 고정 Model A만 읽고 운영 저장소 변경 차단
# 기존 로컬 매니페스트가 있으면 원래 버전 관리 흐름 유지

import hashlib
import logging
import os
from pathlib import Path
import sys

import numpy as np
import scipy
import sklearn
import streamlit as st

from ..data import ROOT
from .service import DETECTOR_PATH, DETECTOR_SHA, MODEL_PATH, MODEL_SHA, ModelBundle, load_models

LOGGER = logging.getLogger(__name__)
REGISTRY_PATH = ROOT / "data/model_registry/registry.json"
READ_ONLY_NOTICE = (
    "공개 배포는 공식 Model A의 읽기 전용 분석 모드입니다. "
    "Streamlit Cloud의 로컬 파일 저장은 재시작·재배포 후 보존을 보장하지 않습니다. "
    "신규 정답 데이터 등록·재학습·승인·교체·롤백은 영구 저장소를 갖춘 로컬 환경에서 실행하세요. "
    "개인·현장 데이터를 공개 앱에 등록하지 마세요."
)


# 명시적 Cloud 설정 또는 운영 이력이 없는 새 배포는 읽기 전용
def read_only_deployment():
    requested = os.environ.get("GAS_SENSOR_DEPLOYMENT", "").strip().lower()
    # Community Cloud의 실행 경로도 확인하며 경로가 없어도 무매니페스트 모드 적용
    community = sys.platform == "linux" and ROOT.is_relative_to(Path("/mount/src"))
    missing_registry = not (REGISTRY_PATH.exists() or REGISTRY_PATH.is_symlink())
    return requested == "cloud" or community or missing_registry


# 파일명·Git LFS 포인터·SHA 오류를 모델 복원 전에 구분
def verify_deployment_artifacts():
    for path, expected in [(MODEL_PATH, MODEL_SHA), (DETECTOR_PATH, DETECTOR_SHA)]:
        if not path.is_file():
            raise FileNotFoundError(f"필수 배포 모델 누락: {path}")
        payload = path.read_bytes()
        if payload.startswith(b"version https://git-lfs.github.com/spec/v1"):
            raise ValueError(f"실제 모델 대신 Git LFS 포인터만 존재함: {path}")
        if hashlib.sha256(payload).hexdigest() != expected:
            raise ValueError(f"배포 모델 SHA-256 불일치: {path}")


# 캐시는 공식 모델·감지기에만 사용하며 운영 이력은 만들지 않음
@st.cache_resource(show_spinner=False, max_entries=1)
def fixed_deployment_bundle():
    models = load_models()
    return ModelBundle(models.classifier, models.detector, version_id="deployment_model_a")


# 로컬의 손상된 기존 매니페스트를 고정 모델로 자동 대체하지 않음
def analysis_bundle():
    try:
        if read_only_deployment():
            verify_deployment_artifacts()
            return fixed_deployment_bundle()
        from ..model_management.runtime import active_bundle

        return active_bundle()
    except Exception:
        LOGGER.exception(
            "Model loading failed: python=%s sklearn=%s numpy=%s scipy=%s root=%s",
            sys.version.split()[0],
            sklearn.__version__,
            np.__version__,
            scipy.__version__,
            ROOT,
        )
        raise
