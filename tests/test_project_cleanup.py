# 공통 지문 계산·연구 보존·통합 보고서 연결 검사

import ast
import hashlib
import json
from pathlib import Path
import re

import pytest

from src.common.hashing import sha256_bytes
from src.data import ROOT
from src.webapp.dataset_registry import digest

OUT = ROOT / 'outputs/project_cleanup'


# 기존 바이트 입력의 계산 결과와 예외 동등성 확인
@pytest.mark.parametrize('payload', [b'', b'abc', bytes(range(256)), '가스 센서'.encode('utf-8')])
def test_digest_equivalence(payload):
    expected = hashlib.sha256(payload).hexdigest()
    assert sha256_bytes(payload) == digest(payload) == expected


def test_digest_rejects_text():
    with pytest.raises(TypeError):
        sha256_bytes('abc')


# 해시 호출 공통화 외 계산·제어 흐름 변경 없음 확인
def test_refactor_ast_equivalence():
    class Restore(ast.NodeTransformer):
        def visit_Call(self, node):
            self.generic_visit(node)
            if isinstance(node.func, ast.Name) and node.func.id == 'sha256_bytes':
                original = ast.parse('hashlib.sha256(payload).hexdigest()', mode='eval').body
                original.func.value.args = node.args
                return original
            return node

    def normalized(text):
        tree = Restore().visit(ast.parse(text))
        tree.body = [node for node in tree.body if not (
            isinstance(node, ast.ImportFrom) and node.module == 'common.hashing')]
        # hashlib import 유무는 공통 함수로 옮긴 의존성 차이
        tree.body = [node for node in tree.body if not (
            isinstance(node, ast.Import) and len(node.names) == 1 and node.names[0].name == 'hashlib')]
        return ast.dump(tree, include_attributes=False)

    for name in ['data_preparation.py', 'dataset_registry.py']:
        assert normalized((OUT / 'source_before' / name).read_text(encoding='utf-8')) == normalized(
            (ROOT / 'src/webapp' / name).read_text(encoding='utf-8'))


# 모델·보고서·표·그래프·관련 코드를 원래 위치에서 보존
def test_prior_research_preserved():
    allowed = {'src/webapp/data_preparation.py', 'src/webapp/dataset_registry.py'}
    records = json.loads((OUT / 'inventory_before.json').read_text(encoding='utf-8'))
    for row in records:
        if row['path'] in allowed or row['category'] == 'D':
            continue
        path = ROOT / row['path']
        assert path.is_file(), row['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'], row['path']


# 통합 보고서의 실제 근거 경로와 그림 링크 검사
def test_evidence_and_report_links():
    evidence = json.loads((OUT / 'research_evidence.json').read_text(encoding='utf-8'))
    assert len(evidence) == 23
    for row in evidence:
        for name in [row['report'], row['code'], *row['csv'], *row['figures'], *row['models'], *row['settings']]:
            assert (ROOT / name).is_file(), name
    md = (ROOT / 'reports/Gas_Sensor_Drift_Final_Report.md').read_text(encoding='utf-8')
    for target in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', md):
        if target.startswith(('http', 'data:')):
            continue
        assert (ROOT / 'reports' / target).resolve().is_file(), target


def test_official_assets_unchanged():
    expected = {
        'models/temporal_expansion/B_SVM_balanced.joblib': '1d6b20c94d1580d799e05ab5a9ce746bdb272d74f70ec2ff964011fffecfde32',
        'models/drift_detection/rff_mmd_v1.joblib': 'de47661f66c69cdc7553f73acf1df9b721f65771d0301fe69a7a326f814fa4c5',
    }
    for name, value in expected.items():
        assert sha256_bytes((ROOT / name).read_bytes()) == value
    assert len(list((ROOT / 'models').rglob('*.joblib'))) == 325


def test_html_self_contained_images():
    text = (ROOT / 'reports/Gas_Sensor_Drift_Final_Report.html').read_text(encoding='utf-8')
    sources = re.findall(r'<img\b[^>]*src=[\"\']([^\"\']+)', text, re.I)
    assert len(sources) > 100
    assert all(source.startswith('data:image/') for source in sources)
