# 학습 없이 그래프 범례 배치 보완 및 최종 검증 기록
# 첫 마감 기록은 보관하고 기존1–11단계는 변경하지 않음

import argparse
import json
import shutil
import xml.etree.ElementTree as ET
from unittest.mock import patch

from matplotlib.axes import Axes
import pandas as pd

from .data import ROOT
from .temporal_expansion import now, sha, write_json
from .temporal_representativeness_control import OUT, REPORTS


# Recall 히트맵의 제목과 범례 겹침만 조정
def prepare():
    archive = OUT / 'visual_review_before'
    if archive.exists():
        raise FileExistsError('Visual review already prepared')
    archive.mkdir()
    for name in ['class_recall_heatmap.png', 'graph_metadata.csv', 'graph_value_checks.csv',
                 'final_verification.json', 'test_results.xml', 'tests.txt']:
        shutil.copy2(OUT / name, archive / name)
    for name in REPORTS:
        shutil.copy2(ROOT / 'reports' / name, archive / name)
    before = pd.read_csv(OUT / 'graph_value_checks.csv')
    original = Axes.legend

    def legend(axis, *args, **kwargs):
        if axis.get_title().startswith('6종 가스 Recall'):
            kwargs['loc'] = 'upper center'
            kwargs['bbox_to_anchor'] = (.5, -.25)
        return original(axis, *args, **kwargs)

    from .representativeness_visuals import create_visuals
    with patch.object(Axes, 'legend', legend):
        create_visuals()
    pd.testing.assert_frame_equal(before, pd.read_csv(OUT / 'graph_value_checks.csv'))
    from .representativeness_report import build_report
    status = json.loads((archive / 'final_verification.json').read_text(encoding='utf-8'))['test_status']
    build_report(status)
    (OUT / 'visual_review.md').write_text(
        '# 그래프 최종 검토\n\nRecall 히트맵 범례를 아래로 옮겨 제목 겹침 해소. '
        '학습·모델·예측·지표·조건 변경 없음. 표시 수치 CSV가 완전히 같은지 대조. '
        '초기 마감 기록·보고서·그래프는visual_review_before/에 보존.\n\n'
        '전체 재현 시 기본 분석·테스트·finalize 후 다음을 실행:\n'
        'python -B -X utf8 -m src.representativeness_visual_review --prepare\n'
        'python -B -X utf8 -m pytest -q -p no:cacheprovider '
        '--junitxml=outputs/temporal_representativeness_control/test_results.xml\n'
        'python -B -X utf8 -m src.representativeness_visual_review --finalize\n', encoding='utf-8')


# 최신 검사와 보고서 지문 확정
def finalize():
    manifest = json.loads((OUT / 'run_manifest.json').read_text(encoding='utf-8'))
    assert all(sha(ROOT / n) == value for n, value in manifest['before'].items())
    old = json.loads((OUT / 'visual_review_before/final_verification.json').read_text(encoding='utf-8'))
    cases = ET.parse(OUT / 'test_results.xml').getroot().findall('.//testcase')
    failures = [f"{c.get('classname')}::{c.get('name')}" for c in cases
                if c.find('failure') is not None or c.find('error') is not None]
    assert set(failures) == set(old['test_status']['failed_tests'])
    status = dict(old['test_status'], passed=len(cases) - len(failures), failed=len(failures))
    from .representativeness_report import build_report
    build_report(status)
    final = dict(old, completed_at=now(), test_status=status,
                 report_sha256={name: sha(ROOT / 'reports' / name) for name in REPORTS},
                 visual_review_source_sha256=sha(ROOT / 'src/representativeness_visual_review.py'),
                 graph_metadata_sha256=sha(OUT / 'graph_metadata.csv'),
                 initial_stage12_record_sha256=sha(OUT / 'visual_review_before/final_verification.json'),
                 additional_classifier_fits=0, numeric_results_changed=False)
    write_json(OUT / 'final_verification.json', final)
    print('VISUAL REVIEW FINAL', status, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--finalize', action='store_true')
    args = parser.parse_args()
    if args.prepare:
        prepare()
    elif args.finalize:
        finalize()
    else:
        parser.error('Choose --prepare or --finalize')
