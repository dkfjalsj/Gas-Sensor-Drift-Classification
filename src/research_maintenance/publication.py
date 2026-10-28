# 기존 연구 결과를 독립 HTML·PNG·CSV 자료집으로 구성
# 새 모델 학습과 센서 원본의 성능 재평가는 수행하지 않음

import base64
from collections import Counter
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import html
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import zipfile

from PIL import Image

from ..data import ROOT
from .consolidate import CHAPTERS, STAGES, body

OUT = ROOT / 'outputs/report_publication'
MATERIALS = ROOT / 'reports/report_materials'
ARCHIVE = ROOT / 'reports/research_archive'
FINAL = ROOT / 'reports/Gas_Sensor_Drift_Final_Report.html'


# 바이트를 변경하지 않고 지문 계산
def sha(payload):
    return hashlib.sha256(payload).hexdigest()


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


# 프로젝트 밖 삭제나 연결 경로 사용 차단
def checked_path(relative):
    path = ROOT / relative
    resolved = path.resolve()
    resolved.relative_to(ROOT.resolve())
    if path.is_symlink():
        raise ValueError('연결 경로 정리 금지: ' + relative)
    return path


# 기존 본문에 포함된 실제 그림의 이름·바이트 추출
class Pictures(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = []

    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            self.items.append(dict(attrs))


def images(text):
    parser = Pictures()
    parser.feed(text)
    return parser.items


# 계획과 정리 직전의 파일 지문 고정
def freeze():
    if OUT.exists() or MATERIALS.exists() or ARCHIVE.exists():
        raise RuntimeError('기존 자료집 실행 흔적 덮어쓰기 금지')
    records = []
    totals = Counter()
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        totals['all_files'] += 1
        totals['all_bytes'] += path.stat().st_size
        if path.relative_to(ROOT).parts[0] in {'.git', '.venv'}:
            continue
        records.append(dict(path=relative, bytes=path.stat().st_size,
                            sha256=sha(path.read_bytes())))
    OUT.mkdir()
    save_json(OUT / 'preservation_before.json', records)
    save_json(OUT / 'counts_before.json', dict(totals))
    targets = []
    for row in records:
        name = row['path']
        report = name.startswith('reports/')
        legacy_html = name.endswith('.html') and name != FINAL.relative_to(ROOT).as_posix()
        duplicate_md = report and name.endswith('.md') and name not in {
            'reports/project_cleanup_report.md', 'reports/research_evidence_index.md'}
        cache = '.pytest_cache/' in name or '/__pycache__/' in name
        if legacy_html or duplicate_md or cache:
            targets.append(dict(**row, reason='통합된 옛 열람 문서의 지문 보관' if not cache else '재생성 가능한 캐시; 검증 보관본 유지'))
    save_json(OUT / 'cleanup_candidates.json', targets)
    (OUT / 'plan.md').write_text('''# 연구 자료집 제작·정리 고정 계획

- 신규 학습·튜닝·원본 Batch 9–10 재평가 없음. 저장된 표와 그림을 그대로 사용함.
- 기존 보고서·그림·CSV를 조사하고 최종 HTML에 원문과 주요 결과·목차를 포함함.
- PNG는 원본 해상도 그대로 복사하거나 기존 HTML 내 PNG를 그대로 추출함. 임의 수치·초해상도 생성 없음.
- CSV는 저장된 집계표의 바이트 그대로 복사함. 표본별 예측·분할·대형 원시 특징은 원래 위치에 보존함.
- 상관 그림의 범위(같은 센서의 8개 특징)를 명시하며 전체 128×128 행렬로 오해시키지 않음.
- ZIP 외부 해제·HTML 오프라인 자원·PNG·CSV 지문·원문 포함 검증 후에만 정리 실행.
- 옛 HTML·중복 Markdown·캐시는 개별 gzip 보관본과 원문 지문을 확인한 뒤 실제 기존 파일 삭제.
- 원본 CSV·그래프·모델·실험 코드·보존 manifest는 삭제하지 않음. 연구 근거를 ZIP 하나로 대체하지 않음.
- 기존 테스트는 필요 문서를 검증된 보관본에서 일시 복원한 상태로 실행하고 동일 바이트인 복원본만 제거함.
- 전체 테스트 신규 실패나 보존 결함이 있으면 Commit·Push 중단. 강제 push·이력 변경 없음.
''', encoding='utf-8')
    print('사전 계획과 기준선 고정', len(records), '정리 후보', len(targets))


# 실험별 사용 조건과 한계를 기존 선정 기록에 맞춰 표시
def context(stage):
    if stage in {'1', '2', '3', '4'}:
        return '전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.'
    if stage == '5':
        return '기존 Test를 제외한 제한된 과거 개발 표본. 6단계 이후 확장 실험과 학습 범위가 다름.'
    if stage in {'6', '7', '10', '11'}:
        return 'Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.'
    if stage in {'8', '9', '12', '13', '14', '15', '16'}:
        return '과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.'
    if stage == '17':
        return '목표 Batch6/7/8의 평가50%를 먼저 고정한 뒤 별도5/10/20% 정답 Calibration으로 SVM 적응. 0%와 같은 평가 행 비교. 시드별 평가 집합이 겹치며 새 시기 무정답 일반화와 다름.'
    if stage in {'18', '18.5'}:
        return 'Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.'
    return '고정 Model A와 감지기를 사용하는 웹앱·20-A 기능 검증. 합성 fixture는 기능 테스트용이며 실제 가스 분류 정확도나 현장 정답으로 취급하지 않음.'


KEY_FINDINGS = {
    '1': '가스·Batch 구성은 불균형이며 Batch3–5에 Toluene이 없음. 값 변화와 센서 드리프트의 인과관계는 별도 문제임.',
    '6': 'Model A Validation 동일 Batch 가중 Macro F1 0.897000. 9–10은 동일 가중0.602705, pooled0.558657로 구분함.',
    '7': 'Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.',
    '10': '확장 Model B의 9–10 동일 가중 Macro F1 0.700451이나 개발 구간·특정 가스 손실이 남아 Model A를 유지함.',
    '13': '시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.',
    '14': 'signed-log 과거 Fold 평균0.800290 대 기준0.797082. 사전 개선 기준 미달이며 일관된 균형 개선을 확인하지 못함.',
    '15': 'hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.',
    '16': 'HGB 평균0.660984 대 SVM0.797082. 이번 고정 비교에서 우수성 근거 부족.',
    '17': '정답 적응 0/5/10/20% 평균 Macro F1=0.802428/0.922580/0.939445/0.946083. 같은 Batch 일부 정답 사용 조건이며 독립 Test 성능이 아님.',
    '18': 'Batch7의36창·Batch8의2창 모두 경고. 이는 실제 고장·노화 또는 분류 실패 확정이 아님.',
    '18.5': '같은 행의 재배열·가스 구성에 점수가 민감함. 경고율만으로 드리프트 탐지 정확도를 주장할 수 없음.',
    '20-A': '출처·정답·세션·시각·중복·6종 지원·과거 Validation 재사용 검사 후 불변 저장. 실제 데이터의 진위·물리적 독립성은 검증하지 못함.',
}


# 기존 그래프와 저장된 집계 CSV를 그대로 자료집에 복사
def build():
    if not OUT.exists() or MATERIALS.exists():
        raise RuntimeError('freeze 후 한 번만 build 가능')
    png_dir, table_dir = MATERIALS / 'png', MATERIALS / 'tables'
    png_dir.mkdir(parents=True)
    table_dir.mkdir()
    assets, sources = [], []
    used = {}
    for stage, chapter, report, code, folder in STAGES:
        source = ROOT / 'reports' / report
        text = source.read_text(encoding='utf-8-sig')
        sources.append(dict(stage=stage, report=source.relative_to(ROOT).as_posix(),
                            code=code, text=text, folder=folder))
        prefix = stage.replace('.', '_').replace('-', '_')
        originals = sorted((ROOT / 'outputs' / folder).rglob('*.png'))
        if folder == 'figures':
            tables = sorted((ROOT / 'outputs').glob('*.csv'))
        else:
            tables = sorted((ROOT / 'outputs' / folder).glob('*.csv'))
        for path in originals:
            payload = path.read_bytes()
            token = sha(payload)
            if token in used:
                continue
            name = prefix + '_' + path.stem + '.png'
            if (png_dir / name).exists():
                name = prefix + '_' + path.stem + '_' + token[:8] + '.png'
            (png_dir / name).write_bytes(payload)
            with Image.open(io.BytesIO(payload)) as picture:
                width, height = picture.size
                picture.verify()
            record = dict(kind='png', stage=stage, file='png/' + name,
                          source=path.relative_to(ROOT).as_posix(), sha256=token,
                          width=width, height=height, title=path.stem)
            assets.append(record)
            used[token] = record
        # 원본 보고서 안에만 있는 그림도 빠짐없이 추출
        for number, item in enumerate(images(text), 1):
            value = item.get('src', '')
            if not value.startswith('data:image/png;base64,'):
                continue
            payload = base64.b64decode(value.split(',', 1)[1], validate=True)
            token = sha(payload)
            if token in used:
                continue
            label = re.sub(r'[^a-zA-Z0-9_-]+', '_', item.get('alt', ''))[:70] or 'embedded'
            name = f'{prefix}_{label}_{number:02d}_{token[:6]}.png'
            (png_dir / name).write_bytes(payload)
            with Image.open(io.BytesIO(payload)) as picture:
                width, height = picture.size
                picture.verify()
            record = dict(kind='png', stage=stage, file='png/' + name,
                          source=source.relative_to(ROOT).as_posix() + f'#image-{number}',
                          sha256=token, width=width, height=height, title=item.get('alt', label))
            assets.append(record)
            used[token] = record
        for path in tables:
            # 행별 원시 특징·예측·분할은 원래 위치에서 유지
            if any(word in path.stem for word in ['prediction', 'assignments', 'split_manifest', 'membership', 'coordinates', 'preservation', 'row_', 'feature_values']):
                continue
            if path.stat().st_size > 2_000_000:
                continue
            payload = path.read_bytes()
            name = prefix + '_' + path.name
            (table_dir / name).write_bytes(payload)
            with path.open(encoding='utf-8-sig', newline='') as stream:
                rows = list(csv.reader(stream))
            assets.append(dict(kind='csv', stage=stage, file='tables/' + name,
                               source=path.relative_to(ROOT).as_posix(), sha256=sha(payload),
                               rows=max(0, len(rows) - 1), columns=rows[0] if rows else [], title=path.stem))
    # CSV가 없는20-A 기능 검증 수치도 저장 JSON의 원문 값만 표로 제공
    source = ROOT / 'outputs/retraining_data_preparation/synthetic_quality_record.json'
    values = json.loads(source.read_text(encoding='utf-8'))
    name = '20_A_saved_quality_record.csv'
    with (table_dir / name).open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['key', 'saved_value_json', 'source'])
        for key, value in values.items():
            writer.writerow([key, json.dumps(value, ensure_ascii=False), source.relative_to(ROOT).as_posix()])
    assets.append(dict(kind='csv', stage='20-A', file='tables/' + name,
                       source=source.relative_to(ROOT).as_posix(), sha256=sha((table_dir / name).read_bytes()),
                       title='저장된20-A 합성 기능 검증 기록', rows=len(values), derived='JSON 항목을 값 변경 없이 CSV로 펼침; 현장 성능 아님'))
    guide = ['# Word 보고서용 연구 자료집',
             '\nBatch9–10은 독립 Test가 아닌 반복 사용한 회고적 평가 자료임. PNG는 실제 기존 그림의 원래 픽셀을 그대로 보존함. 이미지 추출본은 원본 파일과 DPI·크기가 다를 수 있어 동일 그림의 원본 고해상도 파일을 우선 사용할 수 있음. 표는 원본 소수 자릿수·평가 조건을 유지함.\n',
             '외부 ZIP의 원본 근거 경로는 출처 식별자이며 프로젝트 파일이 없어도 HTML·PNG·표를 열 수 있음. 소스 코드·모델·행별 예측은 이 배포 자료집에 포함하지 않음. 전체128×128 상관행렬은 저장되어 있지 않으며 11단계 동일 센서8특징 상관 그림을 명확한 범위로 제공함.\n']
    for asset in assets:
        guide += [f'\n## {asset["file"]}\n',
                  f'- 자료 제목: {asset["title"]}',
                  f'- 실험 목적: {asset["stage"]}단계 기존 결과의 설명·비교·사후 진단.',
                  f'- 데이터·학습/검증/평가 구간: {context(asset["stage"])}',
                  '- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.',
                  '- 핵심 결과: ' + KEY_FINDINGS.get(asset['stage'], '해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.'),
                  '- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.',
                  '- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.',
                  f'- 원본 근거: `{asset["source"]}`',
                  f'- 파일 지문 SHA-256: `{asset["sha256"]}`']
    (MATERIALS / 'materials_guide.md').write_text('\n'.join(guide), encoding='utf-8')
    save_json(MATERIALS / 'materials_manifest.json', assets)
    save_json(OUT / 'source_reports.json', [{k: v for k, v in row.items() if k != 'text'} | dict(sha256=sha(row['text'].encode('utf-8'))) for row in sources])
    make_html(sources, assets)
    print('자료집 생성', dict(Counter(a['kind'] for a in assets)), 'HTML', FINAL.stat().st_size)


# 제목·목차·표·범위 설명을 갖춘 독립 HTML 구성
def make_html(sources, assets):
    required = [
        '프로젝트 개요', '연구 배경 및 목적', 'UCI 데이터셋 설명', '16개 센서와128개 특징',
        'Batch별 데이터 분포', '가스별 데이터 분포', 'EDA 분석', '상관관계 히트맵',
        '데이터 전처리', 'Logistic Regression·Random Forest·SVM 비교', '랜덤 분할과 시간순 분할 성능 비교',
        'Confusion Matrix', '가스별 Precision·Recall·F1', 'Batch별 성능 변화', '모델 성능 개선 실험',
        '공식 SVM 선정 과정', '정답 데이터 기반 모델 적응 실험', 'RFF-MMD² 분포 변화 감지',
        '감지 임계값 및 경고 결과', '18.5단계 민감도 분석', 'Streamlit 웹앱 구현',
        '20-A 재학습 데이터 검증 및 분리', '전체 연구 결과 요약', '실험의 한계 및 트러블슈팅', '향후20-B·20-C 개발 계획',
    ]
    explanations = [CHAPTERS[i][1] for i in [0, 1, 3, 4, 5, 3, 6, 11, 7, 9, 10, 11, 9, 11, 12, 13, 14, 15, 15, 16, 17, 19, 21, 22, 23]]
    explanations[7] = '11단계 저장된 sensor_correlations.csv와 sensor_correlations.png를 사용함. 동일 센서의8개 특징 간 Pearson r의 가스·시기 비교이며 전체128개 특징 상관행렬은 아님. 미래 Batch를 관찰한 사후 설명 자료로 모델 특징 선택에 재사용하지 않음.'
    explanations[23] += ' 기존 테스트의 임시 파일 부재·고정 모델 목록 충돌은 별도 기록함. 정리 후 옛 보고서를 검사하는 테스트는 개별 gzip 보관본을 SHA 확인하여 일시 복원한 상태로 실행함. 과거 해시 기록은 변경하지 않음.'
    relevant = {5: ['1'], 6: ['1'], 7: ['1'], 8: ['11'], 10: ['2'], 11: ['2'], 12: ['7'], 13: ['7'], 14: ['6'],
                15: ['5', '8', '9', '12', '13', '14', '15', '16'], 16: ['6', '10'], 17: ['17'], 18: ['18'], 19: ['18'],
                20: ['18.5'], 21: ['19', '19.5', '19.6'], 22: ['20-A']}
    plot_patterns = {5: ['batch_counts'], 6: ['class_counts'], 7: ['feature_distributions'], 8: ['sensor_correlations'],
                     10: ['model_comparison', 'performance'], 11: ['pooled_performance', 'comparison'], 12: ['confusion'],
                     13: ['recall'], 14: ['batch_macro', 'training_range'], 15: ['feature_effect', 'mean_macro', 'comparison'],
                     17: ['mean_macro_by_rate'], 18: ['calibration_distribution'], 19: ['batch7_windows'],
                     20: ['window_method_means', 'seed_stability']}
    parts = ['<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>가스 센서 연구 결과 통합 보고서</title>',
             '<style>html{scroll-behavior:smooth}body{font-family:"Malgun Gothic",system-ui,sans-serif;max-width:1240px;margin:auto;padding:25px;color:#193047;line-height:1.75;overflow-wrap:anywhere}nav{background:#edf3f8;padding:18px;columns:2}nav a{display:block;color:#234d70}section{margin:40px 0}h2{border-bottom:2px solid #345e7d;padding-bottom:8px}img{max-width:100%;height:auto;display:block;margin:12px auto}figure{margin:18px 0}figcaption{font-size:.9rem;color:#46586b}table{border-collapse:collapse;display:block;max-width:100%;overflow-x:auto;font-size:.84rem}td,th{padding:7px;border:1px solid #c7d0dc;white-space:normal}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f1f4f7;padding:14px}details{border:1px solid #ccd5de;padding:12px;margin:14px 0}summary{font-weight:600;cursor:pointer}.notice{background:#fff0cf;padding:18px}.back{font-size:.85rem}@media(max-width:700px){nav{columns:1}body{padding:14px}}</style></head><body>',
             '<h1>가스 센서 드리프트: 1–20-A 연구 결과 통합</h1><p class="notice">저장된 실제 실험 결과를 보존한 연구 자료집. 신규 학습·튜닝·성능 재평가 없음. Batch9–10은 독립 Test가 아니며 물리적 센서 드리프트의 인과 효과를 확정하지 않음. 공식 Model A·감지기·임계값·100행 창 유지.</p>',
             '<nav id="toc">' + ''.join(f'<a href="#section-{i}">{i}. {html.escape(title)}</a>' for i, title in enumerate(required, 1)) + '<a href="#original-evidence">원본 단계별 전체 결과</a><a href="#figure-catalog">PNG 그림 전체</a><a href="#table-catalog">CSV 결과표 전체</a></nav>']
    by_stage = {source['stage']: source for source in sources}
    for number, title in enumerate(required, 1):
        parts += [f'<section id="section-{number}"><h2>{number}. {html.escape(title)}</h2><p>{html.escape(explanations[number - 1])}</p>']
        stages = relevant.get(number, [])
        if stages:
            parts.append('<p>전체 조건·수치·한계: ' + ' / '.join(f'<a href="#stage-{s}">{s}단계 원문</a>' for s in stages) + '</p>')
        candidates = [a for a in assets if a['kind'] == 'png' and a['stage'] in stages]
        chosen = [a for pattern in plot_patterns.get(number, []) for a in candidates if pattern in a['title']][:2]
        for asset in chosen:
            parts.append(figure(asset))
        if number in {5, 6}:
            parts.append(csv_html(ROOT / 'outputs/batch_class_counts.csv'))
        if number == 17:
            parts.append(csv_html(ROOT / 'outputs/temporal_calibration/ratio_summary.csv'))
        if number == 19:
            parts.append(csv_html(ROOT / 'outputs/drift_detection/partition_summary.csv'))
        parts.append('<p class="back"><a href="#toc">목차로</a></p></section>')
    parts.append('<section id="original-evidence"><h2>부록A. 단계별 원본 전체 결과·설정·선정 근거</h2><p>각 원문의 시점·분할·집계·단위를 유지함. 과거 테스트 개수와 현재 구현 상태를 혼동하지 않음.</p>')
    for source in sources:
        text = source['text']
        if source['report'].endswith('.html'):
            fragment = body(text)
            # 옛 문서 내부 링크는 아래 원문 전체 결과를 가리키게 변경
            fragment = re.sub(r'href=([\"\'])[^\"\']*\.html(?:#[^\"\']*)?\1', 'href="#original-evidence"', fragment, flags=re.I)
        else:
            fragment = '<pre>' + html.escape(text) + '</pre>'
        parts.append(f'<details id="stage-{source["stage"]}"><summary>{source["stage"]}단계 — {html.escape(source["report"])}</summary><p>{html.escape(context(source["stage"]))}</p>{fragment}</details>')
    # 과거 요약·프로토콜도 이전 통합본에서 원문 그대로 보존
    previous = FINAL.read_text(encoding='utf-8')
    marker = '<h2>부록 A. 선정 근거·프로토콜·요약 원문</h2>'
    if marker not in previous:
        raise RuntimeError('이전 통합 문서의 부속 원문을 찾지 못함')
    supplements = previous.split(marker, 1)[1].rsplit('</body>', 1)[0]
    parts += ['<details><summary>당시 요약·선정·프로토콜 전체 원문</summary>' + supplements + '</details></section>',
              '<section id="figure-catalog"><h2>부록B. Word용 PNG 전체</h2>']
    for source in sources:
        group = [asset for asset in assets if asset['kind'] == 'png' and asset['stage'] == source['stage']]
        parts.append(f'<details><summary>{source["stage"]}단계 PNG {len(group)}개</summary>')
        parts.extend(figure(asset) for asset in group)
        parts.append('</details>')
    parts += ['</section><section id="table-catalog"><h2>부록C. 결과표 전체</h2><p>CSV의 원본 문자열·소수 자릿수를 보존함. 행별 원시 예측·대형 중간값은 프로젝트에 그대로 남김.</p>']
    for asset in assets:
        if asset['kind'] == 'csv':
            parts.append(f'<details><summary>{html.escape(asset["file"])}</summary><p>근거: {html.escape(asset["source"])}</p>{csv_html(MATERIALS / asset["file"])}</details>')
    parts.append('</section></body></html>')
    # 교체 전 통합본도 개별 압축 원문으로 보존
    ARCHIVE.mkdir()
    payload = FINAL.read_bytes()
    (ARCHIVE / 'previous_consolidated_report.html.gz').write_bytes(gzip.compress(payload, mtime=0))
    save_json(OUT / 'previous_final.json', dict(path='reports/research_archive/previous_consolidated_report.html.gz', sha256=sha(payload)))
    FINAL.write_text('\n'.join(parts), encoding='utf-8')
    save_json(OUT / 'required_content.json', dict(sections=required, correlation_scope='11단계 센서별8×8 Pearson r; 전체128×128 행렬 아님', new_experiments=0, new_fits=0))


def csv_html(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.reader(stream))
        preview = rows[:201]
        notice = '<p>긴 상세표는 앞200행 표시. 전체 원문 값은 자료집 CSV에 보존함.</p>' if len(rows) > 201 else ''
        return notice + '<table>' + ''.join('<tr>' + ''.join('<td>' + html.escape(cell) + '</td>' for cell in row) + '</tr>' for row in preview) + '</table>'


def figure(asset):
    payload = (MATERIALS / asset['file']).read_bytes()
    return '<figure><img loading="lazy" alt="' + html.escape(asset['file']) + '" src="data:image/png;base64,' + base64.b64encode(payload).decode() + '"><figcaption>' + html.escape(asset['file'] + ' | ' + asset['source']) + '</figcaption></figure>'


# ZIP을 외부 폴더에 풀고 원본 바이트와 비교
def bundle(external):
    external = Path(external)
    if external.exists():
        raise RuntimeError('기존 외부 검증 폴더 덮어쓰기 금지')
    package = ROOT / 'Gas_Sensor_Report_Materials.zip'
    if package.exists():
        raise RuntimeError('기존 ZIP 덮어쓰기 금지')
    with zipfile.ZipFile(package, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        archive.write(FINAL, 'Gas_Sensor_Report_Materials/' + FINAL.name)
        for path in sorted(MATERIALS.rglob('*')):
            if path.is_file():
                archive.write(path, 'Gas_Sensor_Report_Materials/' + path.relative_to(MATERIALS).as_posix())
    with zipfile.ZipFile(package) as archive:
        assert archive.testzip() is None
        for name in archive.namelist():
            destination = (external / name).resolve()
            destination.relative_to(external.resolve())
        archive.extractall(external)
    checked = validate(external / 'Gas_Sensor_Report_Materials')
    checked.update(zip_bytes=package.stat().st_size, zip_sha256=sha(package.read_bytes()), external_path=str(external), zip_crc_ok=True)
    save_json(OUT / 'bundle_validation.json', checked)
    print(json.dumps(checked, ensure_ascii=False))


# 외부 파일·네트워크 없이 모든 그림·표·한글 원문 검사
def validate(directory):
    directory = Path(directory)
    report = directory / FINAL.name
    text = report.read_text(encoding='utf-8')
    assert '\ufffd' not in text
    assert len(re.findall(r'id="section-\d+"', text)) == 25
    items = images(text)
    for item in items:
        source = item['src']
        assert source.startswith('data:image/'), source
        payload = base64.b64decode(source.split(',', 1)[1], validate=True)
        with Image.open(io.BytesIO(payload)) as picture:
            picture.verify()
    assert not re.search(r'<(?:script|link|iframe)\b', text, re.I)
    assert not re.search(r'url\(\s*[\"\']?https?://', text, re.I)
    assets = json.loads((directory / 'materials_manifest.json').read_text(encoding='utf-8'))
    for asset in assets:
        payload = (directory / asset['file']).read_bytes()
        assert sha(payload) == asset['sha256'], asset['file']
        if asset['kind'] == 'png':
            with Image.open(io.BytesIO(payload)) as picture:
                picture.verify()
        else:
            payload.decode('utf-8-sig')
            assert '\ufffd' not in payload.decode('utf-8-sig')
    assert report.read_bytes() == FINAL.read_bytes()
    return dict(valid=True, embedded_images=len(items), assets=dict(Counter(asset['kind'] for asset in assets)), html_bytes=report.stat().st_size,
                standalone=True, external_resources=0, utf8_valid=True, all_asset_sha_match=True)


# 검증이 끝난 자료만 개별 보관 후 기존 파일 삭제
def cleanup():
    state = json.loads((OUT / 'bundle_validation.json').read_text(encoding='utf-8'))
    if not state['valid']:
        raise RuntimeError('자료집 검증 전 정리 금지')
    manifest = []
    for row in json.loads((OUT / 'cleanup_candidates.json').read_text(encoding='utf-8')):
        path = checked_path(row['path'])
        payload = path.read_bytes()
        assert sha(payload) == row['sha256'], row['path']
        stored = ARCHIVE / (row['sha256'] + '.gz')
        if not stored.exists():
            stored.write_bytes(gzip.compress(payload, mtime=0))
        assert gzip.decompress(stored.read_bytes()) == payload
        manifest.append(dict(**row, archive=stored.relative_to(ROOT).as_posix(), compressed_sha256=sha(stored.read_bytes())))
    save_json(ARCHIVE / 'manifest.json', manifest)
    # 전체 보관본 검증이 끝난 뒤 한 파일씩 삭제
    for row in manifest:
        path = checked_path(row['path'])
        assert sha(path.read_bytes()) == row['sha256']
        path.unlink()
    save_json(OUT / 'deletion_log.json', manifest)
    print('검증 보관 후 기존 파일 실제 삭제', len(manifest))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['freeze', 'build', 'bundle', 'cleanup'])
    parser.add_argument('--external')
    args = parser.parse_args()
    if args.action == 'bundle':
        bundle(args.external)
    else:
        globals()[args.action]()
