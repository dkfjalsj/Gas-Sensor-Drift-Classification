# 제출용 단일 앱의 독립 실행 및 기존 기능 동등성 검사
# 합성 후보의 학습·승인·복구는 임시 저장소에서만 수행

import ast
import importlib
import json
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

import gas_sensor_drift as app
from src.data import ROOT, FEATURES
from src.model_management.registry import ModelRegistry
from src.retraining import candidates, datasets
from src.webapp import dataset_registry, data_preparation, service
from tests.test_retraining_candidates import synthetic_source, payload

EVIDENCE = dict(
    source="테스트 생성 출처의 확인 근거 기록",
    truth="테스트 생성 정답의 확인 근거 기록",
    independence="서로 다른 임시 세션의 확인 근거 기록",
)


# 실제 기준 자료는 읽기만 수행
@pytest.fixture(scope="module")
def reference():
    return data_preparation.load_training_reference()


@pytest.fixture(scope="module")
def bundles():
    return service.load_models(), app.service_load_models()


# 기존·신규 구현으로 동일 합성 후보를 각각 한 번 학습
@pytest.fixture(scope="module")
def pair(tmp_path_factory, reference):
    directory = tmp_path_factory.mktemp("standalone_workflows")
    frame, sessions = synthetic_source()
    raw, session_raw = payload(frame), payload(sessions)
    options = (
        "synthetic.csv",
        "synthetic_functional_test_only",
        "known_generator_labels_not_AI",
        True,
        True,
    )
    with patch.object(
        dataset_registry, "load_training_reference", return_value=reference
    ), patch.object(datasets, "load_training_reference", return_value=reference), patch.object(
        app, "preparation_load_training_reference", return_value=reference
    ):
        old_meta, _ = dataset_registry.register_dataset(
            raw, session_raw, *options, storage=directory / "old_data"
        )
        new_meta, _ = app.datasets_register_dataset(
            raw, session_raw, *options, storage=directory / "new_data"
        )
        old = candidates.train_candidate(
            old_meta["dataset_id"],
            feature_contract_confirmed=True,
            dataset_storage=directory / "new_data",
            candidate_storage=directory / "old_models",
            synthetic_only=True,
        )
        new = app.candidates_train_candidate(
            new_meta["dataset_id"],
            feature_contract_confirmed=True,
            dataset_storage=directory / "new_data",
            candidate_storage=directory / "new_models",
            synthetic_only=True,
        )
    return directory, frame, sessions, old, new, reference


def test_no_project_imports_or_embedded_execution():
    tree = ast.parse((ROOT / "gas_sensor_drift.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert node.level == 0
            assert not (node.module or "").startswith(("src", "app_streamlit"))
        if isinstance(node, ast.Import):
            assert all(not item.name.startswith(("src", "app_streamlit")) for item in node.names)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in {"exec", "eval", "__import__"}
    assert app.data_ROOT == ROOT


# 함수명 접두사와 호환 로더를 제외한 계산·승인 로직 AST 대조
@pytest.mark.parametrize(
    "module",
    [
        "src.common.hashing",
        "src.data",
        "src.drift_detection.detector",
        "src.webapp.service",
        "src.webapp.data_preparation",
        "src.webapp.dataset_registry",
        "src.retraining.datasets",
        "src.retraining.evaluation",
        "src.retraining.candidates",
        "src.model_management.registry",
        "src.model_management.runtime",
    ],
)
def test_core_calculation_ast_preserved(module):
    prefixes = {
        "src.common.hashing": "hashing",
        "src.data": "data",
        "src.drift_detection.detector": "drift",
        "src.webapp.service": "service",
        "src.webapp.data_preparation": "preparation",
        "src.webapp.dataset_registry": "datasets",
        "src.retraining.datasets": "training",
        "src.retraining.evaluation": "evaluation",
        "src.retraining.candidates": "candidates",
        "src.model_management.registry": "registry",
        "src.model_management.runtime": "runtime",
    }
    names = {}
    for source_module, prefix in prefixes.items():
        source_tree = ast.parse(
            (ROOT / (source_module.replace(".", "/") + ".py")).read_text(encoding="utf-8")
        )
        for definition in source_tree.body:
            if isinstance(definition, (ast.FunctionDef, ast.ClassDef)):
                names[prefix + "_" + definition.name] = definition.name
            elif isinstance(definition, ast.Assign):
                for target in definition.targets:
                    if isinstance(target, ast.Name):
                        names[prefix + "_" + target.id] = target.id

    class Normalize(ast.NodeTransformer):
        def original_name(self, name):
            return names.get(name, name)

        def visit_Name(self, node):
            if node.id == "portable_joblib_load":
                return ast.Attribute(
                    value=ast.Name(id="joblib", ctx=ast.Load()), attr="load", ctx=ast.Load()
                )
            node.id = self.original_name(node.id)
            return node

        def visit_FunctionDef(self, node):
            node.name = self.original_name(node.name)
            return self.generic_visit(node)

        visit_ClassDef = visit_FunctionDef

    integrated = ast.parse((ROOT / "gas_sensor_drift.py").read_text(encoding="utf-8"))
    actual = {
        node.name: node
        for node in integrated.body
        if isinstance(node, (ast.FunctionDef, ast.ClassDef))
    }
    source = ast.parse((ROOT / (module.replace(".", "/") + ".py")).read_text(encoding="utf-8"))
    for node in source.body:
        if not isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            continue
        key = prefixes[module] + "_" + node.name
        if module == "src.data" and key not in actual:
            continue
        assert ast.dump(Normalize().visit(actual[key]), include_attributes=False) == ast.dump(
            node, include_attributes=False
        ), key


@pytest.mark.parametrize("n", [1, 99, 100, 101, 200])
@pytest.mark.parametrize("truth", [False, True])
def test_predictions_scores_metrics_and_downloads_match(bundles, n, truth):
    frame = pd.DataFrame(np.random.default_rng(42).normal(size=(n, 128)), columns=FEATURES)
    if truth:
        frame["gas"] = np.arange(n) % 6 + 1
    raw = payload(frame)
    old = service.analyze(service.read_upload(raw), bundles[0])
    new = app.service_analyze(app.service_read_upload(raw), bundles[1])
    for key in ["rows", "counts", "windows"]:
        pd.testing.assert_frame_equal(old[key], new[key], check_exact=True)
    assert old["summary"] == new["summary"]
    assert old["drift"] == new["drift"]
    assert service.downloads(old) == app.service_downloads(new)
    if truth:
        for key in ["accuracy", "macro_f1", "supported_classes"]:
            assert old["evaluation"][key] == new["evaluation"][key]
        pd.testing.assert_frame_equal(
            old["evaluation"]["per_class"], new["evaluation"]["per_class"]
        )
        pd.testing.assert_frame_equal(
            old["evaluation"]["confusion"], new["evaluation"]["confusion"]
        )
    assert new["summary"]["threshold"] == 0.00825701197565701


@pytest.mark.parametrize("defect", ["empty", "extra", "missing", "infinite", "gas", "duplicate"])
def test_input_rejections_match(defect):
    frame = pd.DataFrame(np.ones((2, 128)), columns=FEATURES)
    if defect == "extra":
        frame["batch"] = 1
    elif defect == "missing":
        frame = frame.drop(columns="f001")
    elif defect == "infinite":
        frame.iloc[0, 0] = np.inf
    elif defect == "gas":
        frame["gas"] = 7
    elif defect == "duplicate":
        frame.columns = ["f002", *FEATURES[1:]]
    raw = b"" if defect == "empty" else payload(frame)
    with pytest.raises(service.InputError) as old:
        service.read_upload(raw)
    with pytest.raises(app.service_InputError) as new:
        app.service_read_upload(raw)
    assert str(old.value) == str(new.value)


def test_registration_and_training_are_interchangeable(pair):
    directory, frame, sessions, old, new, reference = pair
    assert old["metadata"]["candidate_id"] == new["metadata"]["candidate_id"]
    assert old["metadata"]["request"] == new["metadata"]["request"]
    assert old["metadata"]["pipeline_settings"] == new["metadata"]["pipeline_settings"]
    for key in ["class_metrics", "class_changes", "confusion", "roc_auc", "roc_points"]:
        pd.testing.assert_frame_equal(old[key], new[key], check_exact=True)
    for name in [
        "predictions.csv",
        "confusion.csv",
        "class_metrics.csv",
        "roc_auc.csv",
        "roc_points.csv",
    ]:
        assert (old["directory"] / name).read_bytes() == (new["directory"] / name).read_bytes()
    np.testing.assert_array_equal(
        old["model"].predict(frame[FEATURES]), new["model"].predict(frame[FEATURES])
    )
    assert new["metadata"]["fitted_rows"] == 5993
    assert new["metadata"]["validation_fitted"] is False
    with patch.object(app, "preparation_load_training_reference", return_value=reference):
        loaded = app.training_load_training_data(
            new["metadata"]["dataset_id"], directory / "new_data"
        )
    combined = pd.concat([app.training_official_training_frame(reference)[0], loaded.train_x])
    np.testing.assert_allclose(
        new["model"].named_steps["imputer"].statistics_, np.nanmedian(combined, axis=0)
    )
    assert new["model"].named_steps["scaler"].n_samples_seen_ == len(combined)
    assert set(loaded.assignments.query("partition=='train'").row_id).isdisjoint(
        loaded.assignments.query("partition=='validation'").row_id
    )
    # 기존 구현이 신규 저장 후보를 읽고 신규 구현이 기존 후보를 읽는지 확인
    candidates.read_candidate(
        new["metadata"]["candidate_id"], directory / "new_models", load_model=True
    )
    app.candidates_read_candidate(
        old["metadata"]["candidate_id"], directory / "old_models", load_model=True
    )


def test_preparation_checks_match(reference):
    frame, sessions = synthetic_source()
    arguments = (payload(frame), payload(sessions), "synthetic source", "known generator", True)
    old = data_preparation.inspect_candidate(*arguments, reference)
    new = app.preparation_inspect_candidate(*arguments, reference)
    assert old.summary == new.summary
    assert old.errors == new.errors and old.holds == new.holds and old.warnings == new.warnings
    pd.testing.assert_frame_equal(old.assignments, new.assignments)
    assert old.ready and new.ready
    sessions["session_id"] = "only_one"
    arguments = (payload(frame), payload(sessions), "synthetic source", "known generator", True)
    assert (
        data_preparation.inspect_candidate(*arguments, reference).holds
        == app.preparation_inspect_candidate(*arguments, reference).holds
    )


def test_approval_rollback_cache_and_shared_ledger(pair, tmp_path, monkeypatch):
    directory, frame, _, _, new, reference = pair
    monkeypatch.setattr(app, "preparation_load_training_reference", lambda: reference)
    monkeypatch.setattr(datasets, "load_training_reference", lambda: reference)
    manager = app.registry_ModelRegistry(
        tmp_path / "registry", directory / "new_models", directory / "new_data", testing=True
    )
    legacy = ModelRegistry(manager.root, manager.candidates, manager.datasets, testing=True)
    manager.initialize()
    original = manager.current()
    review = manager.review(new["metadata"]["candidate_id"], EVIDENCE)
    assert review["eligible"]
    old_review = legacy.review(new["metadata"]["candidate_id"], EVIDENCE)
    assert old_review["token"] == review["token"]
    before = manager.path.read_bytes()
    with pytest.raises(RuntimeError):
        manager.activate(
            new["metadata"]["candidate_id"],
            confirmed=True,
            evidence=EVIDENCE,
            expected_version=original["version_id"],
            comparison_token=review["token"],
            preflight=lambda version: (_ for _ in ()).throw(RuntimeError("cache failure")),
        )
    assert manager.path.read_bytes() == before
    version = manager.activate(
        new["metadata"]["candidate_id"],
        confirmed=True,
        evidence=EVIDENCE,
        expected_version=original["version_id"],
        comparison_token=review["token"],
        preflight=lambda v: app.runtime_load_bundle(v, manager),
    )
    assert legacy.current() == version
    active = app.runtime_active_bundle(manager)
    np.testing.assert_array_equal(
        active.classifier.predict(frame[FEATURES]), new["model"].predict(frame[FEATURES])
    )
    restored = legacy.rollback(
        original["version_id"], confirmed=True, expected_version=version["version_id"]
    )
    assert manager.current() == restored
    assert [event["action"] for event in manager.read()["events"]] == [
        "initialize",
        "activate",
        "rollback",
    ]
    assert app.runtime_active_bundle(manager).model_sha == app.service_MODEL_SHA


def test_production_blocks_synthetic_candidate(pair, tmp_path, monkeypatch):
    directory, _, _, _, new, reference = pair
    monkeypatch.setattr(app, "preparation_load_training_reference", lambda: reference)
    manager = app.registry_ModelRegistry(
        tmp_path / "production", directory / "new_models", directory / "new_data"
    )
    manager.initialize()
    before = manager.path.read_bytes()
    review = manager.review(new["metadata"]["candidate_id"], EVIDENCE)
    assert not review["eligible"] and any("합성" in reason for reason in review["reasons"])
    with pytest.raises(ValueError, match="합성"):
        manager.activate(
            new["metadata"]["candidate_id"],
            confirmed=True,
            evidence=EVIDENCE,
            expected_version=review["active"]["version_id"],
            comparison_token=review["token"],
        )
    assert before == manager.path.read_bytes()


@pytest.mark.parametrize("page", ["데이터 분석", "분석 결과", "상세 분석", "모델 관리"])
def test_streamlit_pages_start_without_errors(page):
    tested = AppTest.from_file(str(ROOT / "gas_sensor_drift.py"), default_timeout=60).run()
    tested.sidebar.radio[0].set_value(page).run()
    assert not tested.exception
    assert not tested.error


def test_uploaded_result_ui_and_downloads(bundles):
    frame, _ = synthetic_source()
    result = app.service_analyze(app.service_read_upload(payload(frame)), bundles[1])
    # 운영 버전은 실제 저장소에서 읽되 운영 이력은 변경하지 않음
    result = app.service_analyze(
        app.service_read_upload(payload(frame)), app.runtime_active_bundle()
    )
    tested = AppTest.from_file(str(ROOT / "gas_sensor_drift.py"), default_timeout=60).run()
    tested.session_state["analysis"] = result
    tested.sidebar.radio[0].set_value("상세 분석").run()
    assert not tested.exception
    assert len(tested.get("download_button")) == 3
    assert any("Macro Precision" in metric.label for metric in tested.metric)
    assert any("Macro Recall" in metric.label for metric in tested.metric)


@pytest.mark.parametrize("n", [1, 99, 100, 101, 200])
def test_actual_csv_upload_button_and_window_boundaries(n):
    frame = pd.DataFrame(np.random.default_rng(42).normal(size=(n, 128)), columns=FEATURES)
    frame["gas"] = np.arange(n) % 6 + 1
    tested = AppTest.from_file(str(ROOT / "gas_sensor_drift.py"), default_timeout=60).run()
    tested.file_uploader[0].set_value(("input.csv", payload(frame), "text/csv")).run()
    assert not tested.exception
    tested.button(key="analyze").click().run()
    assert not tested.exception
    assert tested.session_state["analysis"]["summary"]["input_rows"] == n
    assert tested.session_state["analysis"]["summary"]["valid_windows"] == n // 100
    tested.radio(key="page").set_value("상세 분석").run()
    assert not tested.exception and len(tested.download_button) == 3


def test_upload_change_error_and_download_flow():
    frame, _ = synthetic_source()
    tested = AppTest.from_file(str(ROOT / "gas_sensor_drift.py"), default_timeout=60).run()
    tested.file_uploader[0].set_value(("input.csv", payload(frame), "text/csv")).run()
    tested.button(key="analyze").click().run()
    tested.radio(key="page").set_value("상세 분석").run()
    tested.download_button[0].click().run()
    assert not tested.exception and len(tested.session_state["analysis"]["rows"]) == 120
    tested.file_uploader[0].set_value(("bad.csv", b"f001\nwrong\n", "text/csv")).run()
    assert not tested.exception and tested.error
    assert tested.button(key="analyze").disabled
    assert "analysis" not in tested.session_state


def test_management_ui_with_registered_data_and_synthetic_candidate(pair, tmp_path, monkeypatch):
    directory, _, _, _, _, reference = pair
    manager = app.registry_ModelRegistry(
        tmp_path / "manager", directory / "new_models", directory / "new_data"
    )
    manager.initialize()
    monkeypatch.setattr(app, "operation_ui_MANAGER_FACTORY", lambda: manager)
    monkeypatch.setattr(app, "preparation_LOCAL_ROOT", directory / "new_data")
    monkeypatch.setattr(app, "candidate_ui_DATA_STORAGE", directory / "new_data")
    monkeypatch.setattr(app, "candidate_ui_CANDIDATE_STORAGE", directory / "new_models")
    monkeypatch.setattr(app, "preparation_load_training_reference", lambda: reference)
    tested = AppTest.from_string(
        "from gas_sensor_drift import main\nmain()", default_timeout=60
    ).run()
    tested.radio(key="page").set_value("모델 관리").run()
    assert not tested.exception and not tested.error
    assert tested.button(key="approval_apply").disabled
    assert any("합성 후보" in warning.value for warning in tested.warning)


def test_corrupt_local_ledger_not_reinitialized(tmp_path):
    manager = app.registry_ModelRegistry(tmp_path / "bad_ledger")
    manager.root.mkdir()
    manager.path.write_bytes(b"{bad json")
    before = manager.path.read_bytes()
    with pytest.raises((ValueError, KeyError)):
        manager.initialize()
    assert manager.path.read_bytes() == before


# 프로젝트 Python 파일 없이 모델·원본·분할 근거만 복사한 독립 실행
def test_isolated_no_src_execution_and_training(tmp_path):
    destination = tmp_path / "isolated"
    destination.mkdir()
    shutil.copyfile(ROOT / "gas_sensor_drift.py", destination / "gas_sensor_drift.py")
    artifacts = [
        "models/temporal_expansion/B_SVM_balanced.joblib",
        "models/drift_detection/rff_mmd_v1.joblib",
        "outputs/file_validation.csv",
        "outputs/temporal_expansion/experiment_plan.json",
        "outputs/temporal_expansion/split_assignments.csv",
    ]
    for name in artifacts:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    original = Path(json.loads((ROOT / "config.json").read_text())["data_dir"])
    raw = destination / "data" / "original"
    raw.mkdir(parents=True)
    for batch in range(1, 7):
        shutil.copyfile(original / f"batch{batch}.dat", raw / f"batch{batch}.dat")
    (destination / "config.json").write_text(json.dumps({"data_dir": "data/original"}))
    script = r"""
import importlib.abc, importlib.util, sys, pathlib, numpy as np, pandas as pd
class BlockProject(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'src' or fullname.startswith('src.') or fullname == 'app_streamlit':
            raise AssertionError('Project import attempted: ' + fullname)
sys.meta_path.insert(0, BlockProject())
root = pathlib.Path(sys.argv[1])
spec = importlib.util.spec_from_file_location('standalone', root/'gas_sensor_drift.py')
s = importlib.util.module_from_spec(spec); sys.modules['standalone'] = s; spec.loader.exec_module(s)
m = s.service_load_models()
ref = s.preparation_load_training_reference(); assert ref.rows == 5933
y = np.arange(120)%6+1
f = pd.DataFrame(np.random.default_rng(142).normal(0,.2,(120,128))+y[:,None]*50, columns=s.data_FEATURES)
f['gas'] = y
sessions = pd.DataFrame({'input_row':np.arange(1,121), 'session_id':['synthetic_early']*60+['synthetic_late']*60,
 'measured_at':['2026-01-01T00:00:00+00:00']*60+['2026-01-02T00:00:00+00:00']*60})
payload = lambda x:x.to_csv(index=False).encode('utf-8-sig')
result = s.service_analyze(s.service_read_upload(payload(f)), m)
assert result['summary']['valid_windows'] == 1
meta, _ = s.datasets_register_dataset(payload(f), payload(sessions), 'synthetic.csv',
 'synthetic_functional_test_only', 'known_generator_labels_not_AI', True, True)
item = s.candidates_train_candidate(meta['dataset_id'], feature_contract_confirmed=True, synthetic_only=True)
assert item['metadata']['fitted_rows'] == 5993
manager = s.registry_ModelRegistry(); manager.initialize()
assert manager.current()['model']['kind'] == 'official'
from streamlit.testing.v1 import AppTest
tested = AppTest.from_file(str(root/'gas_sensor_drift.py'), default_timeout=60).run()
tested.sidebar.radio[0].set_value('모델 관리').run()
assert not tested.exception, str(tested.exception)
assert not tested.error, str(tested.error)
assert not any(k=='src' or k.startswith('src.') for k in sys.modules)
print('ISOLATED_FULL_WORKFLOW_OK')
"""
    environment = os.environ.copy()
    environment.update(
        OPENBLAS_NUM_THREADS="1",
        OMP_NUM_THREADS="1",
        MKL_NUM_THREADS="1",
        PYTHONDONTWRITEBYTECODE="1",
        PYTHONUTF8="1",
    )
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-X", "utf8", "-c", script, str(destination)],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=150,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "ISOLATED_FULL_WORKFLOW_OK" in result.stdout
    assert not (destination / "src").exists()


# 22-B 회귀 검사: 기존 46개 검사의 조건은 변경하지 않음
# 표 공통 함수만 펼친 UI AST를 리팩터링 전 고정 지문과 대조
UI_AST_BEFORE_22B = {
    "candidate_ui_reset_candidate_state": "8164727f9e8e6e1b32ba00f6bc375960e8bca3b2d6d8d1897ae1d5e114b954b6",
    "candidate_ui_render_result": "f6569a7207e6737c30b7a9011f9ed8b56b9d16da46c363b80734ead651a6d9e3",
    "candidate_ui_render_candidates": "39e0c45411519f09a6a49ea8d02a5cae314212602ebe9f4cf2b1a19aa0ee7920",
    "preparation_ui_reset_preparation": "d4ec960fcc0ec44ec4b7143392d55b0fbf1b10e55647f1a8c9cbf3b22781f30c",
    "preparation_ui_render_management": "63a9c5576eb771b7ea6f1b660c20a6f6affd083d1ef502f98d3f5900d82f371a",
    "operation_ui_reset_review": "4777236b905ba4f452391cdcefcccf48cb33a30fa1a82acce08449b66b0bbe36",
    "operation_ui_render_comparison": "e99d7e31393cca89ad94afe328245dc7638a905e7290e959fc84513c3ef28d61",
    "operation_ui_render_operations": "00d2371a2c817eb52c454a106c70166b668efff1896935f9583eecda60fd167f",
    "ui_style": "ebc68a9adbbfa3a518743fd577cdd75dc93052814405d8de932d3b2db018c2f3",
    "ui_result_metrics": "5aa0230f33650b751716bdc604f46d96021effc72971a8bb73672cbd06323943",
    "ui_gas_chart": "0c7c476f9664e66a82ddd542f17c8909571fad8a1bd23948088f13e48f0f2b38",
    "ui_drift_notice": "ee53de752e5454274b1e2d5c804f35ba25d3f7998305902d03f89c1f5379557a",
    "ui_drift_chart": "f3aaffb67e7dc50e6aff86f62b2cee7f9e35a0cc776d779de4fbc1042d247ae7",
    "ui_optional_evaluation": "ab9affc08b70d6db457a35d899205bd70a75fde1a3623e0bb736d413668839df",
    "ui_model_notes": "e164785a3b7a9a3398491f0dd988c1316e68f7042fa7211c928254e6c54711d8",
    "ui_prediction_table": "652655a8bc57b625b047bf8805a363161d1a08f7887b0ca1384308e7286023b3",
    "ui_pattern_table": "6beb7a032a7c1bc220a0db623cf4a5be9c6582cf95528efbd007cea8d9247b4f",
    "ui_details": "6305a722abe80678e6adb0e6cfee2ba381138fa93a883f70abfeaa8865ded450",
    "ui_main": "e3e0970324fa1cdb0999ad62fc4546ef6cdc7f5df645daed94cb747456554140",
}


@pytest.mark.parametrize("name", sorted(UI_AST_BEFORE_22B))
def test_22b_ui_flow_and_messages_match_pre_refactor_ast(name):
    import hashlib

    class NormalizeTables(ast.NodeTransformer):
        def visit_Call(self, node):
            self.generic_visit(node)
            if isinstance(node.func, ast.Name) and node.func.id == "ui_show_table":
                node.func = ast.Attribute(
                    value=ast.Name(id="st", ctx=ast.Load()), attr="dataframe", ctx=ast.Load()
                )
                node.keywords.append(ast.keyword(arg="width", value=ast.Constant(value="stretch")))
            if (
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "st"
                and node.func.attr == "dataframe"
            ):
                node.keywords = [k for k in node.keywords if k.arg != "width"] + [
                    k for k in node.keywords if k.arg == "width"
                ]
            return node

    tree = ast.parse((ROOT / "gas_sensor_drift.py").read_text(encoding="utf-8"))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    digest = hashlib.sha256(
        ast.dump(NormalizeTables().visit(function), include_attributes=False).encode()
    ).hexdigest()
    assert digest == UI_AST_BEFORE_22B[name]


def test_22b_common_table_preserves_options_and_return_value():
    frame = pd.DataFrame({"value": [1, 2]})
    sentinel = object()
    options = dict(hide_index=False, column_config={"value": "원본 서식"})
    with patch.object(app.st, "dataframe", return_value=sentinel) as display:
        assert app.ui_show_table(frame, **options) is sentinel
        display.assert_called_once_with(frame, width="stretch", **options)


def test_22b_imports_and_feature_schema_are_canonical():
    tree = ast.parse((ROOT / "gas_sensor_drift.py").read_text(encoding="utf-8"))
    bindings = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            bindings.extend(alias.asname or alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            bindings.extend(alias.asname or alias.name for alias in node.names)
    assert len(bindings) == len(set(bindings))
    assert app.drift_FEATURES == tuple(app.data_FEATURES)
    assert len(app.drift_FEATURES) == 128
    assert not any(
        isinstance(n, ast.FunctionDef) and n.name == "ui_cached_models" for n in tree.body
    )


@pytest.mark.parametrize("failure", ["cancel", "stale", "token", "save", "lock"])
def test_22b_failed_approval_preserves_exact_operating_state(pair, tmp_path, monkeypatch, failure):
    directory, _, _, _, candidate, reference = pair
    monkeypatch.setattr(app, "preparation_load_training_reference", lambda: reference)
    manager = app.registry_ModelRegistry(
        tmp_path / "registry", directory / "new_models", directory / "new_data", testing=True
    )
    manager.initialize()
    review = manager.review(candidate["metadata"]["candidate_id"], EVIDENCE)
    assert review["eligible"]
    before = manager.path.read_bytes()
    arguments = dict(
        confirmed=True,
        evidence=EVIDENCE,
        expected_version=review["active"]["version_id"],
        comparison_token=review["token"],
    )
    if failure == "cancel":
        arguments["confirmed"] = False
    elif failure == "stale":
        arguments["expected_version"] = "outdated_version"
    elif failure == "token":
        arguments["comparison_token"] = "outdated_token"
    elif failure == "save":

        def fail_save(state):
            raise RuntimeError("임시 저장 실패")

        monkeypatch.setattr(manager, "save", fail_save)
    elif failure == "lock":
        (manager.root / "registry.lock").write_text("another_request", encoding="ascii")
    with pytest.raises((ValueError, RuntimeError)):
        manager.activate(candidate["metadata"]["candidate_id"], **arguments)
    assert manager.path.read_bytes() == before
    assert manager.current()["model"]["kind"] == "official"
    assert len(manager.read()["events"]) == 1
