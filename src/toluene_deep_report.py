# 실제 진단 수치와 해석을 구분한 HTML·요약·가설 보고서 생성

import base64
import html
import json

import pandas as pd

from .data import ROOT, GASES
from .toluene_deep_diagnostic import OUT, REPORTS, SOURCES, save


# CSV 기반 가설 근거와 후속 검증 제안 작성
def hypothesis_table():
    neighbor = pd.read_csv(OUT / 'neighbor_summary.csv')
    score = pd.read_csv(OUT / 'decision_summary.csv')
    selected = pd.read_csv(OUT / 'sensor_plot_selection.csv')
    b9 = score[(score.model == 'B') & (score.batch == 9) & (score.gas_id == 6)].iloc[0]
    near = neighbor[(neighbor.space == 'B_native') & (neighbor.batch == 9) & (neighbor.gas_id == 6)].iloc[0]
    top = selected.iloc[0]
    return save('hypothesis_evidence', [
        dict(hypothesis='1. 시기별 대표성 부족', assessment='일부 부합',
             observed=f'B의 Batch9 Toluene은 다른 가스가 더 가까운 표본 {int(near.other_closer_n)}/101. '
             'Train1–7에는 Toluene이 존재하고 Batch10 Recall79%로 Batch 특이성이 남음.',
             interpretation='관측된 미래 Toluene과 학습 Toluene의 국소 대표성 부족과 양립함. '
             '전체 거리 증가나 학습 수 부족만의 설명은 충분하지 않음.',
             unresolved='농도·환경·세션 메타데이터 없이 대표성의 물리적 원인과 인과 기여도 미확인.',
             next_test='동일 가스별 표본 예산을 맞춘 시기 분산/집중 대조를 과거 시간순 창에서 사전 설계.'),
        dict(hypothesis='2. 다른 가스와의 특징 중첩', assessment='관찰 결과와 부합' if near.other_closer_n > 50 else '일부 부합',
             observed=f'B Batch9 Toluene의 Ac 대 T 이진 판별이 Ac를 지지한 표본 {int(b9.pair_Ac_favored_n)}/101. '
             f'다른 가스 근접 {int(near.other_closer_n)}/101. 전체 가스·k5 거리 표 별도 저장.',
             interpretation='고정 표준화·관측 특징 공간에서 혼동 영역과 양립. 최근접 구조는 SVM의 직접 원인 증명이 아님.',
             unresolved='화학적 유사성·실제 확률분포 중첩·라벨 오류는 이 결과만으로 확정 불가.',
             next_test='농도와 환경이 기록된 참조 측정으로 두 가스의 조건별 분리 정도 확인.'),
        dict(hypothesis='3. 결정 경계의 변화', assessment='관찰 결과와 부합',
             observed='동일101개에서 A Ethanol101 → B Acetaldehyde96/Ethanol4/Toluene1. '
             'OvO 점수·투표·OvR 재구성과 저장 예측 일치 검사 수행.',
             interpretation='두 고정 파이프라인의 결정 함수가 달라진 사실은 확인. Batch7의 특정 요소 하나가 원인이라는 뜻은 아님.',
             unresolved='학습 표본·표준화 통계·클래스 가중치가 함께 바뀌어 독립 효과 분리 불가. 수치 gamma는 두 모델 모두0.0078125로 동일.',
             next_test='향후 전처리 고정/자료 범위/가중치의 작은 통제 대조. 기존9–10을 선정에 사용하지 않음.'),
        dict(hypothesis='4. 특정 센서 특징의 변화', assessment='일부 부합',
             observed=f'B 기준 Batch9 Toluene 정규화 분포 차이 1위 센서 S{int(top.sensor)}: '
             f'8특징 평균 {top.mean_normalized_wasserstein:.3f}. 전체16센서 및 상관 변화 표 저장.',
             interpretation='단변량 이동과 특징 조합·상관 변화는 관찰. 사후 순위는 분류기 중요도나 센서 고장의 증거가 아님.',
             unresolved='어떤 센서가 오류에 필요·충분한지, 드리프트·농도·환경 중 원인은 미확인.',
             next_test='과거 Train 내부만으로 센서 묶음 안정성 기준을 정한 뒤 제한적 제거/보정 대조. '
             '사후 상위 센서를 곧바로 제거하지 않음.'),
    ])


# 수치 표와 해석을 포함한 새 보고서 생성
def build_report(test_status):
    def read(name):
        return pd.read_csv(OUT / f'{name}.csv')

    def table(data, limit=None):
        data = data.head(limit) if limit else data
        return '<div class="table">' + data.to_html(index=False, float_format=lambda x: f'{x:.4f}', escape=True) + '</div>'

    def image(name, caption):
        encoded = base64.b64encode((OUT / f'{name}.png').read_bytes()).decode('ascii')
        return f'<figure><img alt="{html.escape(caption)}" src="data:image/png;base64,{encoded}"><figcaption>{caption}</figcaption></figure>'

    score = read('decision_summary')
    neighbors = read('neighbor_summary')
    groups = read('prediction_group_summary')
    ranks = read('sensor_plot_selection')
    weights = read('class_weights')
    geometry = read('pair_geometry')
    hypotheses = hypothesis_table()
    status = '전체 테스트 실행 전 · 최종 검증 후 확정 예정' if test_status is None else (
        f'전체 {test_status["passed"]}개 통과, 기존 {test_status["failed"]}개 실패. '
        f'신규 {test_status["new_tests"]}개 모두 통과, 신규 실패 {test_status["new_failures"]}개.')
    b9 = score[(score.model == 'B') & (score.batch == 9) & (score.gas_id == 6)].iloc[0]
    a9 = score[(score.model == 'A') & (score.batch == 9) & (score.gas_id == 6)].iloc[0]
    sections = []

    def section(title, body):
        sections.append(f'<section><h2>{title}</h2>{body}</section>')

    section('1. 분석 목적과 보존 원칙', '''
    <p>Batch9 Toluene 101개가 A에서는 Ethanol, B에서는 주로 Acetaldehyde로 바뀌는 실패 구조 진단.
    성능 개선·모델 재선정 단계가 아님. 분류기 학습·튜닝·전처리 재학습 0회.
    공식 주 후보 A 유지. 기존1–10단계 파일·원본·모델·해시 기록 수정 없음.</p>
    <p class="warning">Batch8은 재사용 개발 자료, Batch9–10은 이미 관찰한 회고적·탐색적 자료.
    새 독립 Test 없음. 사후 진단 특징이나 군집을 모델 선택·평가 개선의 근거로 사용하지 않음.</p>''')
    section('2. 모델·자료·특징 순서 확인',
            '<p><b>확인:</b> A Train1–6 5,933개, B Train1–7 9,546개. '
            '128특징, RBF C=1, gamma=scale, balanced, 저장 imputer/StandardScaler 유지. '
            'Batch8·9·10의 Toluene/Acetaldehyde 모두 분석(요청 구간에 Batch8 Ac도 대조 추가).</p>' +
            table(read('model_audit')) +
            '<p>UCI 원본 설명은 센서1의8특징 다음 센서2의8특징 순서를 명시함. '
            '각 블록은 ΔR, 정규화 반응, 상승EMA(.001/.01/.1), 하강EMA(.001/.01/.1). '
            '센서 번호는 원본 특징 블록 번호이며 실제 하드웨어 일련번호 매핑은 미확인.</p>' +
            table(read('sensor_feature_mapping').head(16)) +
            f'<p>근거: <a href="{SOURCES["uci"]}">UCI224 원본 특징 설명</a>. '
            '공식 Batch 단위 시기 정보와 개별 표본 시각은 구분하며 새 시각을 생성하지 않음.</p>')
    section('3. 기존 실패와 이번 예측 재현',
            '<p><b>확인:</b> A Batch9 Toluene0/101, B1/101. B는 Batch10에서474/600 정분류. '
            'A/B의 이번 대상 예측은10단계 저장 예측과 전부 일치. Train 재대입 성능은 '
            '학습 상태 확인용이며 일반화 성능이 아님.</p>' +
            image('toluene_prediction_distribution', '숫자 Batch 순서 8→9→10. 막대는 실제 Toluene 표본의 예측 가스 수.') +
            table(read('train_class_recall')) +
            '<p><b>해석:</b> Toluene 클래스 누락이나 전체 클래스 매핑 오류라는 설명으로 '
            '특정 Batch의 실패를 설명할 수 없음. 분류 자체가 불가능한 가스라는 결론도 부적절.</p>')
    section('4. 결정 점수·OvO 투표·이진 경계',
            '<p><b>방법:</b> 설치된 sklearn SVC는15개 OvO 이진 판별을 계산하고, '
            'OvR 점수는 투표수에 제한된 보정항을 더한 값임. 양의 OvO(i,j)는 classes_의 앞 클래스 i 지지. '
            '15개 점수·투표·OvR을 재구성해 공개 API 및 predict와 대조함. '
            'predict는 break_ties=False의 OvO 투표를 쓰므로 OvR argmax와 다른 경우도 표에 명시.</p>' +
            table(score) + image('decision_score_comparison',
            'Acetaldehyde 대 Toluene: 양수는 Ac, 음수는 T 지지. 상자 중앙값·사분위수·이상점 표시. 확률 아님.') +
            f'<p><b>확인:</b> Batch9 실제 Toluene 중 Ac 대 T 이진 점수가 Ac를 지지한 수는 '
            f'A {int(a9.pair_Ac_favored_n)}/101, B {int(b9.pair_Ac_favored_n)}/101. '
            f'해당 RKHS 절대 거리 중앙값 A {a9.abs_rkhs_Ac_T_median:.5f}, '
            f'B {b9.abs_rkhs_Ac_T_median:.5f}. Train 두 가스 절대 거리의 하위25% 기준 이내는 '
            f'A {int(a9.within_train_abs_q25_n)}, B {int(b9.within_train_abs_q25_n)}개.</p>' +
            '<p><b>해석:</b> B의 Batch9 Toluene은98/101개가 이 Train 기준 하위25% 범위 밖에 있음. '
            '따라서 전부 이 이진 경계 바로 근처에서 갈린 표본이라는 설명은 충분하지 않음. '
            '반대로 Batch10 Toluene의474/600은 이진 판별에서T를 지지하며 실제 정분류 수와 같음. '
            '이는 두 Batch의 이진 점수 방향 차이라는 관찰이며 확신도·확률의 차이로 해석하지 않음.</p>' +
            '<p><b>해석 제한:</b> raw 점수를 w의 RKHS 길이로 나눈 값은 해당 이진 초평면의 '
            '특징 공간 부호 거리임. 입력 공간 거리·다중 클래스에서 가장 가까운 경계 거리·확률·확신도가 아님. '
            'Train 사분위수는 설명용 비교이며 새 판정 임계값이 아님. 모델별 kernel/표준화가 달라 '
            'A/B 거리 크기 자체를 공통 물리 단위로 해석하지 않음.</p>' +
            table(geometry) + f'<p><a href="{SOURCES["svm"]}">scikit-learn SVM 설명</a> 및 '
            '설치된 sklearn/svm/_base.py, utils/multiclass.py의 구현을 확인함.</p>')
    section('5. 가스별 거리와 최근접 학습 시기',
            '<p><b>방법:</b> 각 저장 전처리로128차원 유클리드 거리 계산. 최근접1개와5개 저장. '
            'A native/B native 외에 A의 동일 척도에서 Train1–7을 조회하는 기하 대조를 추가함. '
            'A_space_train7은 모델 A 재학습이나 실제 A 학습 범위 변경이 아님.</p>' +
            table(neighbors) + image('nearest_train_gas', '최근접1개 가스 비율. 분모는 Batch9 Toluene101개.') +
            image('nearest_train_batch', '가까운 학습 표본의 Batch 구성. A native는 Batch7 학습 자료 없음.') +
            '<p><b>확인:</b> A native의 Batch9 Toluene 최근접 가스·거리는7단계 기록과 일치. '
            '7단계에는 Ac97/Ethanol3/Acetone1이 가장 가까웠으나 A는 Ethanol101로 예측했음. '
            '<b>해석:</b> 이 반례는 최근접 가스와 RBF SVM의 투표 구조가 동일하지 않음을 보여줌. '
            'Train 점수·거리만으로 두 가스의 실제 화학적 유사성을 주장하지 않음.</p>')
    section('6. 센서별 특징 분포와 조합',
            '<p><b>방법:</b>16센서 전체, 각8특징의 동일 가스 Wasserstein을 기준Train의 '
            '동일 가스 SD로 나누고 센서 내 평균을 계산함. 평균·중앙값·표준편차는 '
            '공통 A의 저장 표준화 척도로 저장. B 기준 Batch9 Toluene 이동 상위2센서를 '
            '사후 진단용 그림에만 선택. 모델 입력128개는 유지.</p>' +
            table(ranks) + image('sensor_shift_heatmap', '센서별 동일 가스 분포 차이. 큰 값은 단변량 상대 이동이며 모델 중요도가 아님.') +
            image('sensor_joint_profiles', '동일 센서의8특징 평균 반응 조합. 공통 A 척도, 실제 각 가스 support 표시.') +
            image('sensor_correlations', '사후 상위2센서의 Train·미래 가스 내 Pearson 상관. 작은 support와 범위 차이에 민감함.') +
            '<p><b>해석:</b> 단일 평균뿐 아니라 특징 조합과 상관 구조의 변화도 비교 가능. '
            '상관 변화는 센서 고장·노화·인과적 오류 기여의 증거가 아님. '
            '동일 가스에서도 농도 구성 차이가 반응 크기·상관관계에 영향을 줄 가능성이 남음.</p>')
    section('7. Train 전용 PCA와 Batch9 내부 하위집단',
            '<p><b>방법:</b> A/B 각각의 전체 Train만으로2차원 PCA를 Fit하고 미래 표본을 Transform함. '
            '분류기·특징 선택과 완전히 분리된 시각화임. A/B의 좌표축은 서로 다른 투영이므로 직접 좌표 차이를 비교하지 않음.</p>' +
            image('pca_feature_space', 'Train3가스와 미래 Toluene 표시. 전체 좌표는 CSV 저장; 겹쳐 보이거나 분리돼도128차원 분류 경계 증명은 아님.') +
            image('batch9_subgroups', '101개 표본에 Ward k2 사후 분할 표시. k3/k4도 모두 보고하며 최적 군집 수를 선정하지 않음.') +
            table(read('batch9_cluster_summary')) +
            '<p><b>확인:</b> Ward k2는7개와94개, k3는7개·93개·1개로 분할됨. '
            'k3에서7개는 원본371–377행,93개는378–470행,1개는54행. '
            'B의 유일한 Toluene 정답은54행이고, Ethanol 오답4개는7개 집단에 포함됨. '
            '나머지93개 집단은 모두Acetaldehyde 오답. 행 위치는 사실이며 세션·농도 구분은 미확인.</p>' +
            '<p><b>해석:</b> 계층 군집은 모든 자료를 강제로 나눌 수 있음. silhouette는 이 거리·표본 내부 기술 통계이며 '
            '농도·세션의 실재성 검증이 아님. 원본 행 순서는 실제 시각으로 해석하지 않음. '
            'B의 정답1개·Ethanol4개 집단은 너무 작아 안정적인 하위집단 특성을 일반화하기 어려움.</p>')
    section('8. 동일 표본의 A→B 예측 변경',
            image('prediction_change_crosstab', '실제 가스는 모두 Toluene. 행=A, 열=B 예측, 정규화하지 않은 표본 수.') +
            table(groups) +
            '<p><b>확인:</b>101개 중4개는 같은 Ethanol 오답,96개는 Ethanol→Acetaldehyde 오답 변경, '
            '1개만 Ethanol→Toluene 정답 변경. 그룹별128특징 평균·중앙값·표준편차와 표본ID 저장.</p>' +
            table(weights) +
            '<p><b>해석:</b> Batch7을 포함한 새 파이프라인에서 결정 영역과 예측 방향이 바뀐 것은 관찰 가능. '
            '학습 표본·표준화 통계·balanced 클래스 승수가 함께 달라졌으므로 '
            '특정 Batch7 가스나 특징 하나의 독립적인 영향으로 단정하지 않음.</p>')
    section('9. 실패 원인 가설 평가', table(hypotheses) +
            '<p>분류는 관찰과의 일치 정도이며 통계적 인과 검정 결과가 아님. '
            '가설들은 서로 배타적이지 않고 동시에 성립할 수 있음.</p>')
    section('10. 아직 설명하지 못한 부분과12단계 우선순위',
            '<p>① Toluene–Acetaldehyde의 관측 조건별 대표성 공백을 확인할 참조 농도·환경·세션 정보 확보. '
            '② 표본 수를 가능한 범위에서 맞춘 시기 분산 대조로 자료 양과 시기 효과를 구분. '
            '③ 이번 사후 센서 순위를 그대로 사용하지 않고 과거Train 내부에서 정의한 센서 묶음 안정성 기준을 '
            '작은 대조 실험으로 검증. 새 모델·기준은 독립 자료 확보 전까지 탐색적 후보로만 취급.</p>' +
            '<p>Batch9의 라벨·화학 조건·물리적 센서 상태가 왜 다른지는 현재 파일만으로 확정 불가. '
            '원자료 오류가 의심돼도 예측 결과만으로 레이블을 고치지 않음. '
            '이번 진단은 성능 개선·주 후보 교체의 근거로 사용하지 않음.</p>')
    section('11. 테스트·보존·재현 기록',
            f'<p><b>{status}</b></p>' +
            '<p>기존 실패3건: 과거 소스 SHA 불일치, 과거 기록의 zNex~$haremetrics.csv 부재, '
            '7단계 고정 모델 목록과 승인된8–9단계 모델 추가 충돌. 기존 테스트·해시 기록 수정 없음. '
            '분류기·전처리 Fit0회, 진단 PCA Train Fit2회, 신규 joblib0개. 원본10개·기존모델140개 및 '
            '기존 파일 SHA 비교. 그래프 표시 수치·숫자 순서·폰트와 점수 재구성 검사.</p>' +
            '<pre>.venv\\Scripts\\python.exe -B -X utf8 -m src.toluene_deep_diagnostic\n'
            '.venv\\Scripts\\python.exe -B -X utf8 -m pytest -q -p no:cacheprovider '
            '--junitxml=outputs/toluene_failure_deep_diagnostic/test_results.xml\n'
            '.venv\\Scripts\\python.exe -B -X utf8 -m src.toluene_deep_diagnostic --finalize</pre>' +
            '<p>1–10단계 보존 복제본에서11단계 산출물이 없는 상태로 재현. 이미 경로가 있으면 중단. '
            '기존 산출물 덮어쓰기·Commit·Push 없음.</p>')
    body = '<!DOCTYPE html><html lang="ko"><meta charset="utf-8"><title>Toluene 실패 심층 진단</title>'
    body += '''<style>body{font-family:'Malgun Gothic',sans-serif;max-width:1250px;margin:35px auto;padding:0 22px;color:#243244;line-height:1.7;background:#f7f9fc}h1{font-size:30px}h2{font-size:22px;color:#174d70}section{background:white;padding:25px;margin:22px 0;border-radius:10px}img{width:100%;height:auto}figure{margin:25px 0}figcaption{font-size:14px;color:#526578}.table{overflow:auto;margin:18px 0}table{border-collapse:collapse;font-size:12px;white-space:nowrap}td,th{border:1px solid #d5dfe7;padding:7px;text-align:left}th{background:#e9f1f7}.warning{background:#fff0d8;padding:15px}pre{overflow:auto;background:#eef3f7;padding:15px}</style>'''
    body += '<h1>11단계 · Toluene 분류 실패 심층 진단</h1><p>실제 계산값과 해석을 구분한 회고적 진단 · 모델A/B 고정</p>'
    body += ''.join(sections) + '</html>'
    (ROOT / 'reports' / REPORTS[0]).write_text(body, encoding='utf-8')
    summary = f'''# 11단계 Toluene 실패 심층 진단 요약

신규 분류기 학습·튜닝·전처리 재학습0회. Train 전용 진단 PCA2회. 공식 주 후보A 유지.
새 독립 Test 없음. Batch8 재사용 개발,9–10 회고적·탐색적 자료.

## 핵심 관찰

A Batch9 Toluene101개 모두 Ethanol. B는 Acetaldehyde96/Ethanol4/Toluene1.
B Batch10은474/600 정분류. 클래스 누락·일반적 클래스 매핑 오류만으로 설명 불가.

```text
{score.to_string(index=False)}
```

OvO 양수는 앞 클래스 지지. Ac–T 점수 양수는Ac 지지이며 OvR/거리/점수는 확률이 아님.
이진 경계 RKHS 거리와Train 사분위수를 비교했으며 입력 공간 또는 다중 클래스 최근접 경계 거리로 해석하지 않음.

```text
{neighbors.to_string(index=False)}
```

A native 거리·가스는7단계와 일치. 최근접 분류와 SVM은 다르며 직접 원인 증명이 아님.
센서 매핑은UCI 원본의16개 연속8특징 블록과 대조. 실제 기기 일련번호는 미확인.
사후 상위센서 {ranks[ranks.plot_selected].sensor.astype(int).tolist()}는 진단 그림에만 사용.
Ward k2/3/4는 탐색적 분할이며 세션·농도 구분의 증거가 아님.

## 검사

{status}
기존 실패3건의 과거 기록·검사 유지. 기존 파일·모델·원본 SHA 보존 확인.
Commit·Push 없음. 모델 선정 변경 없음.

## 다음 단계

조건별 대표성/가스 혼동 가설과 여러 요소가 함께 바뀐 경계 변화를 구분할 통제 대조 우선.
농도·환경·세션 정보를 가진 새 참조 자료 확보가 인과 설명과 독립 평가에 필요.
그래프와 전체 CSV: outputs/toluene_failure_deep_diagnostic/.
'''
    (ROOT / 'reports' / REPORTS[1]).write_text(summary, encoding='utf-8')
    review = '# 11단계 가설 평가 및12단계 검증 제안\n\n'
    for row in hypotheses.to_dict('records'):
        review += f'## {row["hypothesis"]}: {row["assessment"]}\n\n'
        for key, label in [('observed', '관찰'), ('interpretation', '해석'), ('unresolved', '미확인'), ('next_test', '다음 검증')]:
            review += f'- {label}: {row[key]}\n'
        review += '\n'
    review += '새 독립 Test 없음. 사후 진단은 모델 선정·특징 변경 근거로 사용하지 않았음. 센서 드리프트·농도·환경 중 원인 확정 불가.\n'
    (ROOT / 'reports' / REPORTS[2]).write_text(review, encoding='utf-8')
