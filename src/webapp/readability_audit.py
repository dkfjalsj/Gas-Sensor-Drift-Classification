# UI 표시 변경을 제외한 기존 연구 파일의 지문 확인
import hashlib
import json

from ..data import ROOT


def verify():
    records = json.loads((ROOT / 'outputs/streamlit_ui_readability/preservation_before.json').read_text(encoding='utf-8'))
    changed = []
    for name, expected in records.items():
        if name.replace('\\', '/') == 'src/webapp/ui.py':
            continue
        path = ROOT / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            changed.append(name)
    return {'all_preserved': not changed, 'changes': changed, 'checked_files': len(records) - 1,
            'models': len(list((ROOT / 'models').rglob('*.joblib')))}
