# 변경 허용 파일과 나머지 연구 자료의 지문을 독립 검사
# 과거 보존 기록은 갱신하지 않음

import json

from ..common.hashing import sha256_bytes
from ..data import ROOT

OUT = ROOT / 'outputs/model_approval'
ALLOWED = {
    'src/webapp/ui.py', 'src/webapp/service.py', '.gitignore', 'README_streamlit.md',
    'requirements-streamlit.txt', 'tests/test_retraining_candidate_ui.py',
}


def verify():
    before = json.loads((OUT / 'preservation_before.json').read_bytes())
    approved = json.loads((OUT / 'approved_source_changes.json').read_bytes())
    changes = []
    for name, expected in before.items():
        if name in ALLOWED:
            expected = approved[name]
        path = ROOT / name
        if not path.is_file() or sha256_bytes(path.read_bytes()) != expected:
            changes.append(name)
    production = ROOT / 'data/model_registry/registry.json'
    initial = (OUT / 'initial_operating_manifest.sha256').read_text().strip()
    return dict(all_preserved=not changes, unexpected_changes=changes,
                checked_files=len(before), allowed_changes=sorted(ALLOWED),
                production_pointer_unchanged=sha256_bytes(production.read_bytes()) == initial,
                existing_model_count=len(list((ROOT / 'models').rglob('*.joblib'))))
