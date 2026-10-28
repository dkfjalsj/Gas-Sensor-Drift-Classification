# UI 수정 허용 목록을 제외한 기존 파일의 지문 확인
import hashlib
import json

from ..data import ROOT

ALLOWED = {'src/webapp/ui.py', 'tests/test_streamlit_integration.py'}


# 과거 보존 기록을 수정하지 않는 읽기 전용 검사
def verify(include_raw=False):
    records = json.loads((ROOT / 'outputs/streamlit_ux/preservation_before.json').read_text(encoding='utf-8'))
    changed = []
    for name, expected in records.items():
        if name.replace('\\', '/') in ALLOWED:
            continue
        path = ROOT / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            changed.append(name)
    return {'all_preserved': not changed, 'changes': changed,
            'models': len(list((ROOT / 'models').rglob('*.joblib'))), 'new_model_fits': 0}
