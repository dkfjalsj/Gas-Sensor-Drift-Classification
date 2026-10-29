# 공개 배포의 무매니페스트 추론·무결성·오류 로그 검사
# 운영 자료를 생성하거나 실제 모델을 교체하지 않음

import hashlib
import json
import logging
import os
from pathlib import Path
import shutil
import subprocess
import sys
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from src.data import FEATURES, ROOT
from src.model_management import runtime
from src.webapp import deployment as d, service


@pytest.fixture
def cloud(monkeypatch, tmp_path):
    monkeypatch.setenv("GAS_SENSOR_DEPLOYMENT", "cloud")
    monkeypatch.setattr(d, "REGISTRY_PATH", tmp_path / "missing_registry.json")
    return tmp_path


def test_new_checkout_uses_read_only_without_creating_registry(monkeypatch, tmp_path):
    monkeypatch.delenv("GAS_SENSOR_DEPLOYMENT", raising=False)
    monkeypatch.setattr(d, "REGISTRY_PATH", tmp_path / "registry.json")
    assert d.read_only_deployment()
    with patch.object(
        runtime, "active_bundle", side_effect=AssertionError("No local ledger access")
    ):
        bundle = d.analysis_bundle()
    assert bundle.model_sha == service.MODEL_SHA
    assert bundle.version_id == "deployment_model_a"
    assert not list(tmp_path.iterdir())


def test_explicit_cloud_never_reads_private_ledger(cloud, monkeypatch):
    d.REGISTRY_PATH.write_text("{private corrupted state", encoding="utf-8")
    before = d.REGISTRY_PATH.read_bytes()
    with patch.object(
        runtime, "active_bundle", side_effect=AssertionError("private registry read")
    ):
        assert d.analysis_bundle().model_sha == service.MODEL_SHA
    assert d.REGISTRY_PATH.read_bytes() == before


def test_local_existing_ledger_delegates_and_does_not_hide_corruption(tmp_path, monkeypatch):
    monkeypatch.delenv("GAS_SENSOR_DEPLOYMENT", raising=False)
    path = tmp_path / "registry.json"
    path.write_text("{corrupt", encoding="utf-8")
    monkeypatch.setattr(d, "REGISTRY_PATH", path)
    with patch.object(
        runtime, "active_bundle", side_effect=ValueError("ledger corrupted")
    ) as load:
        with pytest.raises(ValueError, match="ledger corrupted"):
            d.analysis_bundle()
    load.assert_called_once_with()
    assert path.read_text() == "{corrupt"


@pytest.mark.parametrize("defect", ["missing", "lfs", "hash"])
def test_artifact_failure_is_specific_and_logged(cloud, monkeypatch, caplog, defect):
    path = cloud / "classifier.joblib"
    if defect == "lfs":
        path.write_bytes(b"version https://git-lfs.github.com/spec/v1\noid sha256:abc")
    elif defect == "hash":
        path.write_bytes(b"wrong model")
    monkeypatch.setattr(d, "MODEL_PATH", path)
    with caplog.at_level(logging.ERROR), pytest.raises((ValueError, FileNotFoundError)) as error:
        d.analysis_bundle()
    assert str(path) in str(error.value)
    assert "Model loading failed" in caplog.text and "sklearn=1.9.1" in caplog.text
    assert caplog.records[-1].exc_info is not None


def test_cloud_and_local_official_outputs_and_downloads_match(cloud):
    data = service.read_upload((ROOT / "sample_data/test_sensor.csv").read_bytes())
    old = service.load_models()
    reference = service.ModelBundle(old.classifier, old.detector, version_id="deployment_model_a")
    expected = service.analyze(data, reference)
    actual = service.analyze(data, d.analysis_bundle())
    assert len(actual["rows"]) == 200 and len(actual["windows"]) == 2
    pd.testing.assert_frame_equal(expected["rows"], actual["rows"], check_exact=True)
    pd.testing.assert_frame_equal(expected["windows"], actual["windows"], check_exact=True)
    assert expected["drift"] == actual["drift"]
    assert expected["summary"] == actual["summary"]
    assert service.downloads(expected) == service.downloads(actual)


def test_cloud_ui_upload_analysis_download_and_management_lock(cloud):
    tested = AppTest.from_file(str(ROOT / "app_streamlit.py"), default_timeout=60).run()
    assert not tested.exception
    tested.file_uploader[0].set_value(
        ("test_sensor.csv", (ROOT / "sample_data/test_sensor.csv").read_bytes(), "text/csv")
    ).run()
    tested.button(key="analyze").click().run()
    assert not tested.exception and not tested.error
    assert tested.session_state["analysis"]["summary"]["valid_windows"] == 2
    tested.radio(key="page").set_value("상세 분석").run()
    assert not tested.exception and len(tested.download_button) == 3
    tested.radio(key="page").set_value("모델 관리").run()
    assert not tested.exception
    assert any("보존을 보장하지 않습니다" in warning.value for warning in tested.warning)
    assert len(tested.file_uploader) == 1
    assert not any(
        button.key in {"approval_apply", "rollback_apply", "preparation_save", "candidate_train"}
        for button in tested.button
    )


def test_analysis_exception_is_in_server_log(cloud, monkeypatch, caplog):
    def failed_load():
        raise ImportError("model dependency unavailable")

    monkeypatch.setattr("src.webapp.ui.analysis_bundle", failed_load)
    tested = AppTest.from_file(str(ROOT / "app_streamlit.py"), default_timeout=60).run()
    tested.file_uploader[0].set_value(
        ("test_sensor.csv", (ROOT / "sample_data/test_sensor.csv").read_bytes(), "text/csv")
    ).run()
    with caplog.at_level(logging.ERROR):
        tested.button(key="analyze").click().run()
    assert not tested.exception and tested.error
    assert "CSV analysis failed" in caplog.text
    assert any(record.exc_info for record in caplog.records)


def test_deployment_ignore_allows_only_two_public_models():
    paths = [service.MODEL_PATH, service.DETECTOR_PATH]
    other = next(path for path in (ROOT / "models").rglob("*.joblib") if path not in paths)
    for path in paths:
        result = subprocess.run(
            ["git", "-c", f"safe.directory={ROOT.as_posix()}", "check-ignore", "-q", str(path)],
            cwd=ROOT,
        )
        assert result.returncode == 1, path
    result = subprocess.run(
        ["git", "-c", f"safe.directory={ROOT.as_posix()}", "check-ignore", "-q", str(other)],
        cwd=ROOT,
    )
    assert result.returncode == 0


def test_minimal_checkout_without_raw_data_or_manifest(tmp_path):
    checkout = tmp_path / "clean"
    checkout.mkdir()
    shutil.copyfile(ROOT / "app_streamlit.py", checkout / "app_streamlit.py")
    shutil.copytree(ROOT / "src", checkout / "src", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copyfile(ROOT / "sample_data/test_sensor.csv", checkout / "input.csv")
    for original in [service.MODEL_PATH, service.DETECTOR_PATH]:
        target = checkout / original.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, target)
    script = """
import pathlib,sys
sys.path.insert(0,sys.argv[1])
from src.webapp.service import read_upload, analyze
from src.webapp.deployment import analysis_bundle,read_only_deployment
from streamlit.testing.v1 import AppTest
root=pathlib.Path(sys.argv[1])
assert read_only_deployment()
result=analyze(read_upload((root/'input.csv').read_bytes()),analysis_bundle())
assert len(result['rows'])==200 and len(result['windows'])==2
tested=AppTest.from_file(str(root/'app_streamlit.py'),default_timeout=60).run()
tested.file_uploader[0].set_value(('input.csv',(root/'input.csv').read_bytes(),'text/csv')).run()
tested.button(key='analyze').click().run()
assert not tested.exception and not tested.error
tested.radio(key='page').set_value('상세 분석').run()
assert not tested.exception and len(tested.download_button)==3
assert not (root/'data').exists() and not (root/'outputs').exists()
assert not (root/'config.json').exists()
print('CLEAN_DEPLOYMENT_OK')
"""
    environment = os.environ.copy()
    environment.pop("GAS_SENSOR_DEPLOYMENT", None)
    environment.update(
        PYTHONDONTWRITEBYTECODE="1",
        OPENBLAS_NUM_THREADS="1",
        OMP_NUM_THREADS="1",
        MKL_NUM_THREADS="1",
    )
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-X", "utf8", "-c", script, str(checkout)],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=90,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "CLEAN_DEPLOYMENT_OK" in result.stdout
