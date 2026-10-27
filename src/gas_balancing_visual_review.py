# 추가 학습 없이 겹친 그래프 라벨과 과거풀 표기 정리
# 첫 마감 기록 보관 후 신규 검사 재확인

import argparse
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
from unittest.mock import patch

from matplotlib.figure import Figure
from matplotlib.text import Annotation
import pandas as pd

from .data import ROOT
from .temporal_expansion import now, sha, write_json
from .gas_specific_temporal_balancing import OUT, REPORTS


# 그림의 수치와 분류 결과를 유지한 표시 보완
def prepare():
    archive = OUT / 'visual_review_before'
    if archive.exists():
        raise FileExistsError('Stage13 visual review exists')
    archive.mkdir()
    names = ['focus_joint_recall.png', 'gas_batch_composition.png',
             'exploratory_confusion_9.png', 'exploratory_confusion_10.png',
             'graph_metadata.csv', 'graph_value_checks.csv', 'final_verification.json']
    for name in names:
        shutil.copy2(OUT / name, archive / name)
    for name in REPORTS:
        shutil.copy2(ROOT / 'reports' / name, archive / name)
    before = pd.read_csv(OUT / 'graph_value_checks.csv')
    original = Figure.savefig

    def savefig(figure, target, *args, **kwargs):
        name = Path(target).name
        if name == 'focus_joint_recall.png':
            offsets = {'분산843': (9, 7), '최근843': (10, 20),
                       '가스혼합843': (-85, -20), '최소대표843': (10, -25)}
            for annotation in figure.findobj(match=Annotation):
                if annotation.get_text() in offsets:
                    annotation.set_position(offsets[annotation.get_text()])
        if name in ['gas_batch_composition.png', 'exploratory_confusion_9.png', 'exploratory_confusion_10.png']:
            for axis in figure.axes:
                axis.set_title(axis.get_title().replace('Train1–7', '과거풀1–7'))
        return original(figure, target, *args, **kwargs)

    from .gas_balancing_visuals import create_visuals
    with patch.object(Figure, 'savefig', savefig):
        create_visuals()
    pd.testing.assert_frame_equal(before, pd.read_csv(OUT / 'graph_value_checks.csv'))
    from .gas_balancing_report import build_report
    status = json.loads((archive / 'final_verification.json').read_text(encoding='utf-8'))['test_status']
    build_report(status)
    summary = pd.read_csv(OUT / 'mid_summary.csv').set_index('setting')
    comparison = (
        f'단순 최근형의 과거 평균 Macro F1은 {summary.loc["recent_mid", "mean_macro_f1"] * 100:.2f}%로, '
        f'가스혼합 {summary.loc["mixed_mid", "mean_macro_f1"] * 100:.2f}%와 '
        f'최소대표 {summary.loc["coverage_mid", "mean_macro_f1"] * 100:.2f}%보다 높았다. '
        '이번 결과에서 새 구성의 추가 복잡성을 정당화할 안정적인 우월성은 확인하지 못했다. '
        '이는 과거 개발 구간의 기술적 평가이며 회고적 미래 점수로 후보를 재선정한 것이 아니다.'
    )
    report_path = ROOT / 'reports' / REPORTS[0]
    document = report_path.read_text(encoding='utf-8')
    marker = '<h2>9. 최종 연구 결론과 한계</h2>'
    assert marker in document
    report_path.write_text(document.replace(marker, marker + '<p><b>추가 복잡성 평가:</b> ' + comparison + '</p>'), encoding='utf-8')
    with (ROOT / 'reports' / REPORTS[1]).open('a', encoding='utf-8') as handle:
        handle.write('\n## 추가 복잡성 평가\n\n' + comparison + '\n')
    (OUT / 'visual_review.md').write_text(
        '# 그래프 최종 검토\n\n가까운 점의 주석을 분리하고 Train1–7을 과거풀1–7로 명확화. '
        '최근형의 실제 선택은Batch7뿐일 수 있어 실제 구성표와구분. 수치·조건·모델·판정 변경없음. '
        '추가학습0회. 초기 마감 기록은visual_review_before/보관.\n\n'
        '기본 분석·전체테스트·finalize 후 재현할 마감 명령:\n'
        'python -B -X utf8 -m src.gas_balancing_visual_review --prepare\n'
        'python -B -X utf8 -m pytest tests/test_gas_specific_temporal_balancing.py -q -p no:cacheprovider '
        '--junitxml=outputs/gas_specific_temporal_balancing/visual_review_test_results.xml\n'
        'python -B -X utf8 -m src.gas_balancing_visual_review --finalize\n', encoding='utf-8')


# 전체 검사 결과를 유지하고 최종 그림·보고서 지문 확정
def finalize():
    old = json.loads((OUT / 'visual_review_before/final_verification.json').read_text(encoding='utf-8'))
    cases = ET.parse(OUT / 'visual_review_test_results.xml').getroot().findall('.//testcase')
    assert len(cases) == old['test_status']['new_tests']
    assert all(c.find('failure') is None and c.find('error') is None for c in cases)
    manifest = json.loads((OUT / 'run_manifest.json').read_text(encoding='utf-8'))
    assert all(sha(ROOT / n) == value for n, value in manifest['before'].items())
    final = dict(old, completed_at=now(), final_visual_tests_passed=len(cases),
                 report_sha256={n: sha(ROOT / 'reports' / n) for n in REPORTS},
                 graph_metadata_sha256=sha(OUT / 'graph_metadata.csv'),
                 visual_review_source_sha256=sha(ROOT / 'src/gas_balancing_visual_review.py'),
                 first_stage13_final_record_sha256=sha(OUT / 'visual_review_before/final_verification.json'),
                 additional_fits=0, numeric_results_changed=False)
    write_json(OUT / 'final_verification.json', final)
    print('FINAL VISUAL REVIEW', final['test_status'], 'post-review tests', len(cases), flush=True)


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
