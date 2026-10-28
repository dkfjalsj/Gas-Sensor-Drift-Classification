# 연구 자료의 파일 목록과 보존 기준선 수집

import ast
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
import subprocess

from ..data import ROOT
OUT = ROOT / 'outputs/project_cleanup'


# 대용량 파일을 나누어 읽어 지문 계산
def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


# 실행 환경과 Git 내부 파일은 개수만 별도 기록
def main():
    if OUT.exists():
        raise RuntimeError('기존 정리 기록 덮어쓰기 금지')
    paths = sorted(p for p in ROOT.rglob('*') if p.is_file())
    tracked = set(subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', '-z']).decode().split('\0'))
    texts = {}
    for p in paths:
        rel = p.relative_to(ROOT).as_posix()
        if rel.split('/')[0] in {'.venv', '.git'}:
            continue
        if p.suffix in {'.py', '.md', '.json', '.txt', '.html'} and p.stat().st_size < 20_000_000:
            if p.name.startswith('.env'):
                continue
            texts[rel] = p.read_text(encoding='utf-8-sig', errors='replace')
    records, functions = [], defaultdict(list)
    for p in paths:
        rel = p.relative_to(ROOT).as_posix()
        if rel.split('/')[0] in {'.venv', '.git'}:
            continue
        cache = '__pycache__' in p.parts or '.pytest_cache' in p.parts
        refs = [r for r, text in texts.items() if r != rel and (rel in text or (p.name in text and len(p.name) > 8))]
        category = 'D' if cache else 'B'
        role = '研究 근거 및 재현 자료'
        if rel.startswith(('src/webapp/', 'src/drift_detection/', 'tests/', 'sample_data/')) or p.name in {'app_streamlit.py', 'config.json'}:
            category, role = 'A', '운영·검증 의존 파일'
        elif rel.startswith('src/'):
            category, role = 'C', '과거 실험 재현 코드·공통화 검토'
        elif rel.startswith('models/'):
            role = '저장 모델·재학습 없이 재현 필요'
        elif cache:
            role = '재생성 가능한 실행 캐시'
        records.append(dict(path=rel, absolute_path=str(p), bytes=p.stat().st_size,
                            sha256=sha(p), category=category, role=role,
                            tracked=rel in tracked, reproducibility_required=not cache,
                            references=refs, code_referenced=any(r.endswith('.py') and not r.startswith('tests/') for r in refs),
                            test_referenced=any(r.startswith('tests/') for r in refs),
                            report_referenced=any(r.startswith('reports/') for r in refs),
                            reference_method='정적 경로·파일명 검색; 동적 참조 누락 가능하므로 미확인 파일 보존'))
        if p.suffix == '.py' and not cache:
            try:
                tree = ast.parse(texts.get(rel, ''), filename=rel)
                for node in tree.body:
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        functions[ast.dump(node, include_attributes=False)].append(dict(path=rel, name=node.name, line=node.lineno, end=node.end_lineno))
            except SyntaxError:
                pass
    OUT.mkdir(parents=True)
    (OUT / 'inventory_before.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    groups = defaultdict(list)
    for row in records:
        groups[row['sha256']].append(row['path'])
    (OUT / 'exact_duplicates.json').write_text(json.dumps([v for v in groups.values() if len(v) > 1], ensure_ascii=False, indent=2), encoding='utf-8')
    duplicated = [v for v in functions.values() if len(v) > 1]
    (OUT / 'duplicate_functions.json').write_text(json.dumps(duplicated, ensure_ascii=False, indent=2), encoding='utf-8')
    summary = dict(project_files=len(paths), project_bytes=sum(p.stat().st_size for p in paths),
                   research_files=len(records), research_bytes=sum(r['bytes'] for r in records),
                   models=sum(r['path'].endswith('.joblib') for r in records),
                   figures=sum(Path(r['path']).suffix in {'.png', '.svg', '.jpg'} for r in records))
    (OUT / 'summary_before.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    with (OUT / 'file_inventory.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    print(json.dumps(summary))
    print('EXACT FUNCTION GROUPS')
    for group in duplicated:
        print(json.dumps(group))


if __name__ == '__main__':
    main()
