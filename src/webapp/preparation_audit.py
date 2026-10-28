# 20-A 변경 허용 파일과 기존 연구 파일의 보존 확인
import hashlib
import json

from ..data import ROOT

ALLOWED = {"src/webapp/ui.py", "tests/test_streamlit_integration.py", ".gitignore", "README_streamlit.md"}


def verify():
    records = json.loads((ROOT / "outputs/retraining_data_preparation/preservation_before.json").read_text(encoding="utf-8"))
    changes = []
    for name, expected in records.items():
        if name.replace("\\", "/") in ALLOWED:
            continue
        path = ROOT / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            changes.append(name)
    return {"all_preserved": not changes, "changes": changes,
            "checked_files": len(records) - len(ALLOWED),
            "models": len(list((ROOT / "models").rglob("*.joblib")))}
