# 기존 보고서·표·그래프를 연결한 통합 문서 생성
# 학습과 원본 센서 데이터 분석은 수행하지 않음

import base64
import csv
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re

from ..data import ROOT
REPORTS = ROOT / 'reports'
OUT = ROOT / 'outputs/project_cleanup'

CHAPTERS = [
    ('프로젝트 개요', '센서 특징 128개로 가스 6종을 분류하고 기준 분포와의 차이를 알리는 연구 프로토타입임. 현재 완료 범위는 20-A이며 모델 재학습·승인·교체는 미구현임.'),
    ('연구 배경 및 문제 정의', '같은 시기 자료를 섞은 분류 성능과 새로운 시기의 일반화는 별도 연구 질문임. 분포 변화, 가스 구성 변화, 모델 오류, 물리적 센서 노화·고장은 같은 의미가 아님.'),
    ('실제 산업 활용 및 사용자 시나리오', 'CSV 업로드→가스 분류→100행 창의 분포 변화 안내→정답이 있는 경우 사후 비교→관리자 신규 정답 자료 검증 흐름을 제공함. 산업 현장 안전 장치나 농도 측정기로 검증한 시스템은 아님.'),
    ('UCI 가스 센서 데이터셋 소개', 'UCI Gas Sensor Array Drift Dataset. 실제 검증 기록은 13,910행·10개 Batch·6종 가스·128개 특징임. 원본은 config.json의 외부 경로에서 읽고 저장소에 포함하지 않음.'),
    ('16개 센서와 128개 특징의 의미', '16개 센서×8개 특징. 각 센서의 delta_R, normalized_R 및 상승·하강 EMA 특징(0.001/0.01/0.1)으로 구성됨. 원시 시계열이나 행별 농도·정확한 측정 시각이 아님. src/data.py의 FEATURES·KINDS가 해석 기준임.'),
    ('Batch 구조 및 시간에 따른 센서 반응', 'Batch 번호를 측정 시기 구분에 사용함. 행 번호로 측정 시각을 만들지 않음. Batch 3–5에는 Toluene이 없고 Batch 8의 Toluene은 18개뿐임. 평가 support와 실제 존재 클래스 수를 함께 해석해야 함.'),
    ('EDA 및 데이터 시각화', '결측·무한대·중복·값 범위·가스 및 Batch 구성·PCA를 탐색함. 전체 자료로 만든 EDA 변환기는 모델 평가 파이프라인에 재사용하지 않음. 원본 검증표와 그림은 그대로 보존함.'),
    ('전처리와 데이터 분할 전략', '랜덤 60/20/20과 시간순 분할을 구분함. 이후 반복 사용한 Batch 9–10은 회고적·탐색적 평가이며 독립 Test가 아님. 전처리·가중치·특징 선택은 각 Train에서만 학습함. 기존 Test 미사용 원칙을 엄격히 적용한 5단계와 재지정한 6단계를 혼동하지 않음.'),
    ('기본 머신러닝 모델 학습', 'training_config.json의 고정 설정으로 LR·RF·RBF SVM을 동일 분할에 적용함. LR/SVM은 Train 중앙값 처리+StandardScaler, RF는 Train 중앙값 처리. 이후 개선 실험과 최초 기준선의 설정을 구분함.'),
    ('Logistic Regression·Random Forest·SVM 비교', '동일 분할에서 Accuracy·Macro/Weighted F1·클래스별 성능을 비교함. 단일 Accuracy 순위로 공식 모델을 결정하지 않음. 모델 계수·불순도 중요도·비선형 경계 해석의 차이와 상관 특징의 한계를 유지함.'),
    ('랜덤 분할과 시간순 분할 성능 비교', '랜덤 분할의 높은 점수는 여러 시기의 유사한 분포를 함께 학습한 조건의 결과임. 미래 Batch 성능 저하를 모두 센서 드리프트로 귀속할 수 없음. 클래스·농도·환경·수집 조건 변화 가능성을 분리하여 논의함.'),
    ('Batch별·가스별 오분류 분석', '공식 Model A의 Batch 9 Toluene은 0/101 정분류, Batch 10 Acetaldehyde Recall은 0.14임. 합산 지표만 보면 특정 Batch의 완전 실패가 가려짐. 오분류 조합이 화학적 유사성을 입증하는 것은 아님.'),
    ('모델 성능 개선 실험', '5–16단계의 범위 확장·반복 검증·특징 선택·가중치·시기 구성 통제·비선형 변환·앙상블·HGB 비교를 모두 보존함. 실패한 조건과 보호 기준 미달도 포함함. 반복 개발 검증에 의한 선택 편향은 남음.'),
    ('최종 공식 SVM 모델 선정', '운영에 고정한 Model A는 6단계 B_SVM_balanced임. 공식 사용 모델이라는 뜻이며 독립 검증이 완료된 최종 성능 모델이라는 뜻은 아님. Train 1–6(5,933), Validation 7–8(3,907), 회고적 평가 9–10(4,070). Train median+StandardScaler+RBF SVC(C=1, gamma=scale, class_weight=balanced, seed=42).'),
    ('정답 데이터 기반 모델 적응 실험', '17단계는 대상 시기 일부 정답을 사용하는 지도학습 적응임. 대상 Batch의 평가 50%를 먼저 고정하고 별도 Calibration을 추가함. 새 시기 정답 없는 일반화와 직접 비교하지 않음. 같은 Batch의 무작위 분할이 시간 선후나 물리적 독립성을 증명하지 못함.'),
    ('RFF-MMD² 분포 변화 감지 시스템', '1–6의 5,933행을 Reference 2,966 / Calibration 1,483 / 내부 평가 1,484로 분리함. Reference만으로 중앙값·표준화·커널 폭을 학습함. RFF 512, 창 100행, 임계값 0.00825701197565701 고정. 감지기는 정답을 입력으로 사용하지 않음.'),
    ('분포 변화 감지기의 민감도 및 한계', '18.5는 가스 구성·원본 순서·Batch 내부 재배열·구성 통제 진단임. 임계값 재설정이나 탐지 정확도 검증이 아님. MMD² 경고를 센서 고장 또는 분류 정확도 하락으로 단정하지 않음.'),
    ('Streamlit 웹앱 개발', '공식 모델·감지기의 SHA와 입력 스키마를 확인하고 메모리에서 예측함. 정답 gas는 입력 특징과 분리하여 사후 비교만 수행함. 특징 128열의 순서 재정렬·잘못된 입력 차단·3종 CSV 다운로드를 제공함.'),
    ('사용자 중심 UI/UX 개선', '일반 분석·결과·상세 분석·모델 관리 화면으로 구성함. 사용자 설명과 기술 상세를 구분하고 파일 교체 시 이전 결과를 초기화함. 표시만 바꾸고 기존 CSV 바이트·분류·감지 결과 동등성을 검증한 기록을 보존함.'),
    ('20-A 재학습 데이터 검증·분리 시스템', '신규 정답·출처 확인과 행별 세션·timezone 포함 측정 시각을 요구함. 공식 Train 5,933행과 완전·근접·부분 관측 중복을 검사함. 최신 세션은 Validation, 이전 세션은 Train. 두 분할의 6종 존재·세션 중복·과거 Validation 재사용을 검사하고 불변 버전으로 저장함. 실제 정답의 진위·물리적 독립성은 소프트웨어만으로 보장하지 못함.'),
    ('전체 시스템 아키텍처', 'app_streamlit.py → src/webapp/ui.py → service.py → 공식 분류 Pipeline / drift_detection/detector.py. 모델 관리 → management_ui.py → data_preparation.py → dataset_registry.py → data/retraining/. 연구 단계별 entrypoint는 그대로 유지함. src/common/hashing.py는 20-A의 동일 바이트 지문 계산만 공통화함.'),
    ('핵심 실험 결과 종합', '6단계 Model A의 Validation Batch 평균 Macro F1=0.897000, 회고적 9–10 Batch 평균=0.602705, pooled=0.558657임. 10단계 확장 Model B는 각각 회고적 Batch 평균=0.700451, pooled=0.677537이나 공식 모델로 교체하지 않음. 17단계 5/10/20% 정답 적응의 평균 Macro F1=0.922580/0.939445/0.946083은 별도 평가 집합·문제 조건임. 아래 원본 표에서 단위·집계법을 확인해야 함.'),
    ('연구의 한계 및 검증되지 않은 내용', '새 독립 Test, 산업 환경 검증, 물리적 드리프트 정답, 농도·환경·세션별 인과 분리가 없음. 중첩 Train Fold와 반복 사용한 Validation은 독립 반복 표본이 아님. 표본 수가 작은 클래스·Batch와 pooled/동일 Batch 가중 평균을 구분함. 18단계의 당시 Streamlit 미설치 기록과 19단계 이후 구현 완료는 시점 차이이며 충돌이 아님.'),
    ('20-B·20-C 개발 계획', '20-B는 승인된 불변 데이터셋에서 Train만으로 후보 전처리·학습, 예약 Validation으로 보호 지표와 과거 유지 성능을 검토하도록 별도 사전 계획이 필요함. 20-C는 모델 지문·버전·승인·rollback·감사 이력을 갖춘 원자적 교체가 필요함. 기존 공식 모델을 덮어쓰지 않음. Notebook은 공유 API를 호출하되 과거 실험 entrypoint의 기존 경로 덮어쓰기를 피해야 함. 이번 작업에서 구현하지 않음.'),
    ('최종 결론', '여러 시기에 걸친 클래스 경계의 변화와 불균형이 주요 연구 문제임. 현재 근거에서는 일반적인 튜닝·앙상블만으로 일관된 균형 개선을 확정하지 못함. 대상 시기 정답을 일부 이용한 적응은 회복 가능성을 보였으나 독립 미래 성능의 증명은 아님. 분류·분포 변화 안내·신규 정답 자료 검증이 연결된 연구 프로토타입으로 정리함.'),
]

# 주요 실험의 원문·수치·그림·코드를 장별로 연결
STAGES = [
    ('1', 7, 'eda_report.html', 'src/analysis.py', 'figures'),
    ('2', 10, 'model_comparison_report.html', 'src/train_models.py', 'model_comparison'),
    ('3', 12, 'model_diagnostic_report.html', 'src/diagnose_models.py', 'model_diagnostics'),
    ('4', 12, 'toluene_failure_analysis.html', 'src/analyze_toluene.py', 'toluene_analysis'),
    ('5', 13, 'model_improvement_report.html', 'src/improve_models.py', 'model_improvement'),
    ('6', 14, 'temporal_expansion_report.html', 'src/temporal_expansion.py', 'temporal_expansion'),
    ('7', 12, 'temporal_failure_diagnostic_report.html', 'src/temporal_failure_diagnostics.py', 'temporal_failure_diagnostics'),
    ('8', 13, 'temporal_robustness_improvement_report.html', 'src/temporal_robustness.py', 'temporal_robustness'),
    ('9', 13, 'temporal_weighting_report.html', 'src/temporal_weighting.py', 'temporal_weighting'),
    ('10', 14, 'temporal_generalization_validation_report.html', 'src/temporal_generalization_validation.py', 'temporal_generalization_validation'),
    ('11', 12, 'toluene_failure_deep_diagnostic_report.html', 'src/toluene_deep_diagnostic.py', 'toluene_failure_deep_diagnostic'),
    ('12', 13, 'temporal_representativeness_control_report.html', 'src/temporal_representativeness_control.py', 'temporal_representativeness_control'),
    ('13', 13, 'gas_specific_temporal_balancing_report.html', 'src/gas_specific_temporal_balancing.py', 'gas_specific_temporal_balancing'),
    ('14', 13, 'nonlinear_feature_transformation_report.html', 'src/nonlinear_feature_transformation.py', 'nonlinear_feature_transformation'),
    ('15', 13, 'temporal_svm_ensemble_report.html', 'src/temporal_svm_ensemble.py', 'temporal_svm_ensemble'),
    ('16', 13, 'hgb_algorithm_comparison_report.html', 'src/hgb_algorithm_comparison.py', 'hgb_algorithm_comparison'),
    ('17', 15, 'temporal_calibration_report.html', 'src/temporal_calibration.py', 'temporal_calibration'),
    ('18', 16, 'drift_detection_report.html', 'src/drift_detection/experiment.py', 'drift_detection'),
    ('18.5', 17, 'drift_detection_sensitivity_report.html', 'src/drift_detection_sensitivity/experiment.py', 'drift_detection_sensitivity'),
    ('19', 18, 'streamlit_integration_report.md', 'src/webapp/service.py', 'streamlit_integration'),
    ('19.5', 19, 'streamlit_ux_improvement_report.md', 'src/webapp/ui.py', 'streamlit_ux'),
    ('19.6', 19, 'streamlit_ui_readability_report.md', 'src/webapp/ui.py', 'streamlit_ui_readability'),
    ('20-A', 20, 'retraining_data_preparation_report.md', 'src/webapp/data_preparation.py', 'retraining_data_preparation'),
]


# 원본 HTML의 수치·표는 유지하고 본문만 추출
def body(text):
    match = re.search(r'<body[^>]*>(.*)</body>', text, re.I | re.S)
    result = match.group(1) if match else text
    return re.sub(r'<(script|style)\b[^>]*>.*?</\1>', '', result, flags=re.I | re.S)


# HTML 그림을 별도 결과 파일 없이 본문에 포함
def standalone(fragment, source):
    def replace(match):
        value = html.unescape(match.group(2))
        if value.startswith(('data:', 'http:', 'https:')):
            return match.group(0)
        path = (source.parent / value).resolve()
        if path.is_file() and path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.svg'}:
            mime = 'svg+xml' if path.suffix == '.svg' else ('jpeg' if path.suffix in {'.jpg', '.jpeg'} else 'png')
            encoded = base64.b64encode(path.read_bytes()).decode('ascii')
            return 'src=' + match.group(1) + f'data:image/{mime};base64,{encoded}' + match.group(1)
        return match.group(0)
    return re.sub(r'src=([\"\'])(.*?)\1', replace, fragment)


# Markdown에 표와 설명을 보존하고 그림은 기존 파일로 연결
def markdown_body(fragment, original):
    fragment = re.sub(r'<img\b[^>]*>', f'<p>원본 삽입 그래프: <a href="{original.name}">{original.name}</a></p>', fragment, flags=re.I)
    return fragment


# 원본 CSV에서 선택한 표를 그대로 읽기
def csv_table(path, limit=20):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.reader(stream))
    chosen = rows[:limit + 1]
    escaped = [[html.escape(cell) for cell in row] for row in chosen]
    table = '<table>' + ''.join('<tr>' + ''.join(f'<td>{v}</td>' for v in row) + '</tr>' for row in escaped) + '</table>'
    return table, len(rows) - 1


# 기존 근거의 상대 경로와 파일 존재 여부 확인
def link(path):
    relative = Path(path).relative_to(ROOT).as_posix()
    return f'../{relative}'


def main():
    targets = ['Gas_Sensor_Drift_Final_Report.md', 'Gas_Sensor_Drift_Final_Report.html', 'research_evidence_index.md']
    if any((REPORTS / name).exists() for name in targets):
        raise RuntimeError('통합 문서 덮어쓰기 금지')
    md = ['# AI 기반 가스 센서 드리프트 감지 및 분류 성능 보정 시스템',
          '20-A까지의 보존형 통합 연구 보고서. 새 실험·학습 없음. 기존 결과는 원문 그대로 보존함.\n',
          'Word 수행내역서 작성 중이므로 기존 파일 삭제·이동 및 Git Stage·Commit·Push 보류.\n',
          'HTML에는 기존 주요 HTML 보고서의 표·설명·삽입 그래프 전체를 포함함. Markdown에는 원문 본문·표와 기존 그림 상대 경로를 포함함. 원문 당시 상태와 현재 상태를 구분해야 함.\n']
    web = ['<!doctype html><html lang="ko"><meta charset="utf-8"><title>Gas Sensor Drift — 통합 연구 보고서</title>',
           '<style>body{font-family:system-ui,sans-serif;max-width:1240px;margin:30px auto;padding:0 22px;line-height:1.7;color:#172434}img{max-width:100%;height:auto}table{border-collapse:collapse;display:block;overflow:auto;font-size:.84rem}td,th{border:1px solid #ccd4df;padding:5px}section{margin:35px 0}details{border:1px solid #c9d3df;margin:14px 0;padding:12px}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f2f5f8;padding:14px}summary{cursor:pointer;font-weight:bold}.notice{background:#fff4da;padding:16px}h2{border-bottom:2px solid #315884}</style><body>',
           '<h1>AI 기반 가스 센서 드리프트 감지 및 분류 성능 보정 시스템</h1>',
           '<p class="notice">20-A까지의 기존 연구 통합. 새 학습·평가 없음. Batch 9–10은 독립 Test가 아님. 기존 파일 삭제·이동 및 Git 반영은 Word 문서 완성 확인 이후로 보류함.</p>']
    index = ['# 연구 근거 자료 목록', '\n기존 파일 삭제·이동 없음. 결과를 새로 계산하지 않고 저장된 수치·표·그림을 연결함.\n']
    evidence = []
    for number, (title, explanation) in enumerate(CHAPTERS, 1):
        md += [f'\n## {number}. {title}\n', explanation + '\n']
        web += [f'<section id="chapter-{number}"><h2>{number}. {title}</h2><p>{html.escape(explanation)}</p>']
        if number == 6:
            table, total = csv_table(ROOT / 'outputs/batch_class_counts.csv')
            md += [table, '\n근거: [Batch별 가스 표본 수](../outputs/batch_class_counts.csv)\n']
            web.append(table)
        for stage, chapter, report, code, folder in STAGES:
            if chapter != number:
                continue
            source = REPORTS / report
            text = source.read_text(encoding='utf-8-sig')
            md += [f'\n### {stage}단계 원본 연구 내용\n', f'[원본 보고서]({report}) · [실행 코드](../{code})\n']
            web += [f'<details open><summary>{stage}단계 — {html.escape(report)}</summary>']
            if source.suffix == '.html':
                fragment = body(text)
                md.append(markdown_body(fragment, source))
                web.append(standalone(fragment, source))
            else:
                md.append(text)
                web.append('<pre>' + html.escape(text) + '</pre>')
            web.append('</details>')
            out = ROOT / 'outputs' / folder
            csvs = sorted(out.glob('*.csv'))
            settings = sorted(p for p in out.glob('*.json') if any(x in p.name for x in ['plan', 'settings', 'selection', 'decision', 'lock']))
            figures = sorted(out.rglob('*.png'))
            models = sorted((ROOT / 'models' / folder).glob('*.joblib'))
            if stage == '2':
                models = sorted((ROOT / 'models').glob('*.joblib'))
            if stage == '1':
                csvs = sorted((ROOT / 'outputs').glob('*.csv'))
            md += ['\n#### 원본 수치·설정 및 이미지\n',
                   '모든 원본 결과 CSV: ' + ' · '.join(f'[{p.name}]({link(p)})' for p in csvs) + '\n',
                   '사전 계획·설정: ' + ' · '.join(f'[{p.name}]({link(p)})' for p in settings) + '\n']
            for picture in figures[:2]:
                md.append(f'\n![{picture.stem}]({link(picture)})\n')
            if figures:
                web.append('<p>원본 별도 이미지 파일 수: ' + str(len(figures)) + '</p>')
            row = dict(stage=stage, chapter=number, report=str(source.relative_to(ROOT)).replace('\\', '/'), code=code,
                       csv=[p.relative_to(ROOT).as_posix() for p in csvs], figures=[p.relative_to(ROOT).as_posix() for p in figures],
                       models=[p.relative_to(ROOT).as_posix() for p in models], settings=[p.relative_to(ROOT).as_posix() for p in settings])
            evidence.append(row)
            index += [f'\n## {stage}단계 / 통합 보고서 {chapter}절\n', f'- 원문·수치·결론: [{report}]({report})',
                      f'- 코드: [{code}](../{code})', '- 표·상세 수치: ' + ' · '.join(f'[{p.name}]({link(p)})' for p in csvs),
                      '- 그림: ' + ' · '.join(f'[{p.name}]({link(p)})' for p in figures),
                      '- 모델: ' + (' · '.join(f'[{p.name}]({link(p)})' for p in models) or '모델 전체 목록·SHA는 아래 model_inventory.csv 참조'),
                      '- 설정: ' + ' · '.join(f'[{p.name}]({link(p)})' for p in settings)]
        web.append('</section>')
    # 요약 문서에만 있는 판정·제외 근거도 누락 없이 연결
    supplements = sorted(p for p in REPORTS.glob('*.md') if p.name not in targets)
    md += ['\n## 부록 A. 당시 요약·선정·프로토콜 전체\n', '아래는 각 단계 작성 시점의 원문이며 최신 구현 상태·테스트 개수와 구분해야 함.\n']
    web.append('<h2>부록 A. 선정 근거·프로토콜·요약 원문</h2>')
    for source in supplements:
        text = source.read_text(encoding='utf-8-sig')
        md += [f'\n### {source.name}\n', f'[원본]({source.name})\n', text]
        web.append(f'<details><summary>{html.escape(source.name)}</summary><pre>{html.escape(text)}</pre></details>')
    md += ['\n## 부록 B. 수치 해석 및 상태 차이 기록\n',
           '- 6단계 Model A의 0.602705는 두 Batch 동일 가중 평균이고 0.558657은 4,070행 pooled Macro F1임. 서로 다른 집계라 충돌이 아님.\n',
           '- 10단계 Model B는 Train 1–7이며 Model A는 1–6임. B의 회고적 개선만으로 공식 모델을 교체하지 않았음.\n',
           '- 14단계 baseline 0.797082는 세 과거 Fold 평균이며 6단계 Validation 7–8 평균 0.897000과 평가 조건이 다름.\n',
           '- 17단계 적응은 새 시기 일부 정답을 사용하고 별도 50% 평가 집합을 사용함. 무정답 미래 일반화 점수와 순위 비교 금지.\n',
           '- 과거 테스트 실패 개수는 실행 시점·검사 제한·누적 모델 수가 다름. 최신 완료된 20-A 기준은 230 통과/2 기존 실패/90 제한 skip임. 이번 정리 테스트는 별도 로그로 보고함.\n',
           '- 옛 README의 Commit·Push 없음과 초기 모델 미선정 설명은 당시 상태 기록임. 현재 Git 상태 및 공식 Model A와 구분함.\n',
           '- 이번 통합은 원문 간 모든 수치의 의미적 일치를 자동 증명하지 않음. 해석되지 않은 불일치는 원문과 CSV를 함께 제시하며 임의 수정하지 않음.\n']
    index += ['\n## 공식 자산과 정리 기록\n',
              '- 공식 모델: [B_SVM_balanced](../models/temporal_expansion/B_SVM_balanced.joblib)',
              '- 고정 감지기: [rff_mmd_v1](../models/drift_detection/rff_mmd_v1.joblib)',
              '- [모델 전체 경로·지문](../outputs/project_cleanup/model_inventory.csv)',
              '- [파일별 목록](../outputs/project_cleanup/file_inventory.csv)',
              '- [정리 보고서](project_cleanup_report.md)',
              '- 1–25절 개요의 근거는 각 절에 연결된 원문 및 설정·코드임. 산업 시나리오·20-B/C는 제안이며 측정 결과가 아님.']
    (REPORTS / targets[0]).write_text('\n\n'.join(md), encoding='utf-8')
    (REPORTS / targets[1]).write_text('\n'.join(web) + '</body></html>', encoding='utf-8')
    (REPORTS / targets[2]).write_text('\n'.join(index), encoding='utf-8')
    (OUT / 'research_evidence.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
    original = json.loads((OUT / 'inventory_before.json').read_text(encoding='utf-8'))
    models = [row for row in original if row['path'].endswith('.joblib')]
    with (OUT / 'model_inventory.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['path', 'bytes', 'sha256', 'role', 'references'])
        writer.writeheader()
        writer.writerows({key: row[key] for key in writer.fieldnames} for row in models)
    print(json.dumps({'chapters': len(CHAPTERS), 'major_reports': len(STAGES), 'supplements': len(supplements),
                      'model_records': len(models), 'markdown_bytes': (REPORTS / targets[0]).stat().st_size,
                      'html_bytes': (REPORTS / targets[1]).stat().st_size}))


if __name__ == '__main__':
    main()
