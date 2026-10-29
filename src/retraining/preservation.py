# 기존 자료 전체 지문과20-A 화면 로직의 최소 확장 확인
# 과거 해시 기록을 수정하거나 현재 해시로 덮어쓰지 않음

import ast
import hashlib
import json

from ..data import ROOT

OUT = ROOT / 'outputs/retraining_candidates'


# 새 화면 호출3개만 제거하면 기존 AST와 같아야 함
def management_extension_valid():
    source = OUT / 'source_before/management_ui.py'
    current = ROOT / 'src/webapp/management_ui.py'
    old_tree = ast.parse(source.read_text(encoding='utf-8'))
    new_tree = ast.parse(current.read_text(encoding='utf-8'))
    function = next(node for node in new_tree.body if isinstance(node, ast.FunctionDef)
                    and node.name == 'render_management')
    expected = ast.parse(
        'from ..retraining.ui import render_candidates\n'
        'render_candidates()\n'
        'st.subheader("신규 정답 데이터 준비 (20-A)")\n').body
    if [ast.dump(node) for node in function.body[:3]] != [ast.dump(node) for node in expected]:
        return False
    function.body = function.body[3:]
    return ast.dump(old_tree, include_attributes=False) == ast.dump(new_tree, include_attributes=False)


# 모델·통합HTML·ZIP·데이터 저장소 포함 전체 보존 확인
def verify():
    snapshot = json.loads((OUT / 'preservation_before.json').read_text(encoding='utf-8'))
    edited = 'src/webapp/management_ui.py'
    backup = OUT / 'source_before/management_ui.py'
    backup_ok = hashlib.sha256(backup.read_bytes()).hexdigest() == snapshot[edited]
    unexpected, checked = [], 0
    for name, expected in snapshot.items():
        if name == edited:
            continue
        path = ROOT / name
        checked += 1
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            unexpected.append(name)
    extension = backup_ok and management_extension_valid()
    return dict(all_preserved=not unexpected and extension, checked_files=checked,
                unexpected_changes=unexpected, management_extension_only=extension,
                original_management_backup_sha_verified=backup_ok,
                models=len(list((ROOT / 'models').rglob('*.joblib'))))
