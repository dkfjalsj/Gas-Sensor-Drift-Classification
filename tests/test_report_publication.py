# 자료집 바이트·옛 원문·단일 HTML·모델 보존 검사

import gzip
import json
from pathlib import Path
import re
import zipfile

from src.data import ROOT
from src.research_maintenance.publication import (
    ARCHIVE, FINAL, MATERIALS, OUT, sha, validate,
)
from src.research_maintenance.publication_archive import archived_bytes, records


def test_external_bundle_validation_record():
    result = json.loads((OUT / 'bundle_validation.json').read_text(encoding='utf-8'))
    assert result['valid'] and result['standalone']
    assert result['external_resources'] == 0
    assert result['assets']['png'] > 100
    assert result['assets']['csv'] > 30


def test_archives_preserve_original_bytes():
    source = {row['path']: row for row in json.loads((OUT / 'preservation_before.json').read_text(encoding='utf-8'))}
    for row in records():
        payload = archived_bytes(row)
        assert sha(payload) == source[row['path']]['sha256']
        assert len(payload) == source[row['path']]['bytes']


def test_actual_sources_are_unchanged():
    archived = {row['path'] for row in records()}
    allowed = {'reports/Gas_Sensor_Drift_Final_Report.html',
               'reports/research_evidence_index.md', 'reports/project_cleanup_report.md'}
    for row in json.loads((OUT / 'preservation_before.json').read_text(encoding='utf-8')):
        if row['path'] in archived or row['path'] in allowed:
            continue
        path = ROOT / row['path']
        assert path.is_file(), row['path']
        assert sha(path.read_bytes()) == row['sha256'], row['path']


def test_png_and_tables_match_manifest():
    assets = json.loads((MATERIALS / 'materials_manifest.json').read_text(encoding='utf-8'))
    for row in assets:
        assert sha((MATERIALS / row['file']).read_bytes()) == row['sha256']
        if row['source'].endswith('.csv'):
            assert (MATERIALS / row['file']).read_bytes() == (ROOT / row['source']).read_bytes()


def test_current_html_has_all_sections_and_no_external_resources():
    text = FINAL.read_text(encoding='utf-8')
    assert len(re.findall(r'id="section-\d+"', text)) == 25
    assert all(f'id="stage-{stage}"' in text for stage in ['1', '6', '13', '17', '18.5', '20-A'])
    assert not re.search(r'<(?:script|link|iframe)\b', text, re.I)
    assert '전체128개 특징 상관행렬은 아님' in text
    assert '독립 Test가 아니' in text


def test_single_persistent_html_with_temporary_legacy_excluded():
    temporary = {row['path'] for row in records() if row['path'].endswith('.html')}
    current = [path.relative_to(ROOT).as_posix() for path in ROOT.rglob('*.html')
               if path.relative_to(ROOT).parts[0] not in {'.git', '.venv'}
               and path.relative_to(ROOT).as_posix() not in temporary]
    assert current == ['reports/Gas_Sensor_Drift_Final_Report.html']


def test_zip_crc_and_current_report_bytes():
    with zipfile.ZipFile(ROOT / 'Gas_Sensor_Report_Materials.zip') as archive:
        assert archive.testzip() is None
        assert archive.read('Gas_Sensor_Report_Materials/' + FINAL.name) == FINAL.read_bytes()


def test_model_and_detector_sha_still_fixed():
    assert sha((ROOT / 'models/temporal_expansion/B_SVM_balanced.joblib').read_bytes()) == '1d6b20c94d1580d799e05ab5a9ce746bdb272d74f70ec2ff964011fffecfde32'
    assert sha((ROOT / 'models/drift_detection/rff_mmd_v1.joblib').read_bytes()) == 'de47661f66c69cdc7553f73acf1df9b721f65771d0301fe69a7a326f814fa4c5'
