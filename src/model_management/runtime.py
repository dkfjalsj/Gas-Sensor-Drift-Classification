# 운영 버전과 모델 지문을 키로 분류기 캐시 분리
# 고정 감지기 캐시는 운영 모델 교체와 별개로 유지

import json

import streamlit as st

from ..webapp.service import ModelBundle, load_models
from .registry import ModelRegistry


@st.cache_resource(show_spinner=False, max_entries=1)
def fixed_detector():
    return load_models().detector


@st.cache_resource(show_spinner=False, max_entries=8)
def cached_classifier(version_json, registry_root, candidate_store, dataset_store, testing):
    manager = ModelRegistry(registry_root, candidate_store, dataset_store, testing=testing)
    return manager.load_version(json.loads(version_json))


# 전환 전에 새 캐시 로딩까지 성공해야 포인터 저장 허용
def load_bundle(version, manager):
    model = cached_classifier(json.dumps(version, sort_keys=True), str(manager.root),
                              str(manager.candidates), str(manager.datasets), manager.testing)
    return ModelBundle(model, fixed_detector(), version['model']['name'],
                       version['model']['model_sha256'], version['version_id'],
                       version['applied_at_utc'])


def active_bundle(manager=None):
    manager = manager or ModelRegistry()
    return load_bundle(manager.current(), manager)
