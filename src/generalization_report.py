# 고정 모델의 탐색적 비교와 독립 검증 부재를 시각화 중심으로 보고
# 계산 사실·조건부 불확실성·미확인 원인을 구분한 문서 생성

import base64
import html
import json

import numpy as np
import pandas as pd

from .data import ROOT, GASES

OUT = ROOT / 'outputs/temporal_generalization_validation'


def table(data):
    return data.to_html(index=False, escape=True, float_format=lambda x: f'{x:.4f}')


def graph(name, interpretation):
    encoded = base64.b64encode((OUT / f'{name}.png').read_bytes()).decode('ascii')
    return f'<figure><img alt="{html.escape(name)}" src="data:image/png;base64,{encoded}"><figcaption>{interpretation}</figcaption></figure>'


# 이전 연구의 노출 역할과 실제 재현 결과 정리
def history_table():
    descriptions = {
        1: ('전체 자료 검증·EDA', '모든 Batch의 분포를 이미 관찰. 분류기 학습 없음.'),
        2: ('랜덤60/20/20 및 시간순 기준', 'A_random은 모든 시기의 표본을 Train/Validation/Test에 포함. B_early와 B_history 별도.'),
        3: ('저장 모델 진단', '기존 예측·Train 점수·특징 변화 분석. 새 분류기 없음.'),
        4: ('Toluene 실패 진단', '기존 시간순 클래스·분포·매핑 검증. 새 분류기 없음.'),
        5: ('과거 Test 엄격 제외 개선', 'Train370, Validation1022, 이후 Batch3–10 평가. 기존 Test 제외로 범위 제한.'),
        6: ('시간순 확장 및 재지정', 'Train1–3/1–6, Validation7–8, 탐색9–10. 모델 A는 Train1–6.'),
        7: ('미래 Batch 실패 분석', 'Batch7–10의 저장3모델 예측·조건부 특징 이동 확인.'),
        8: ('3개 확장 창과 특징·결합', '1–3→6,1–6→7,1–7→8; 9–10 재사용. Fold 겹침·비중첩 선택 편향.'),
        9: ('시기·가스 가중치 및 확장', '같은3Fold, Train1–6/1–7 별도 비교. Model B는 기본 balanced Train1–7.'),
    }
    registry = {2: 'model_comparison', 5: 'model_improvement', 6: 'temporal_expansion',
                8: 'temporal_robustness', 9: 'temporal_weighting'}
    rows = []
    for stage, (purpose, roles) in descriptions.items():
        fits = len(json.loads((ROOT / 'outputs' / registry[stage] / 'fit_records.json').read_text(encoding='utf-8'))) if stage in registry else 0
        rows.append(dict(stage=stage, purpose=purpose, classifier_fits=fits, historical_roles=roles))
    return pd.DataFrame(rows)


# 최신 검사 상태를 포함한 보고서와 요약 작성
def build_report(experiment, test_status):
    metrics = pd.read_csv(OUT / 'evaluation_metrics.csv', dtype={'scope': str})
    classes = pd.read_csv(OUT / 'class_metrics.csv', dtype={'scope': str})
    summary = pd.read_csv(OUT / 'model_comparison_summary.csv').set_index('model')
    pairs = pd.read_csv(OUT / 'paired_correctness.csv')
    transitions = pd.read_csv(OUT / 'prediction_transitions.csv')
    intervals = pd.read_csv(OUT / 'conditional_bootstrap_intervals.csv', dtype={'scope': str})
    wilson = pd.read_csv(OUT / 'recall_wilson_intervals.csv', dtype={'scope': str})
    replay = pd.read_csv(OUT / 'historical_prediction_replay.csv')
    metric_replay = pd.read_csv(OUT / 'historical_metric_replay.csv')
    history = history_table()
    history.to_csv(OUT / 'historical_experiment_timeline.csv', index=False, encoding='utf-8')
    role_counts = pd.read_csv(OUT / 'predictions_comparison.csv').groupby(['batch', 'gas']).size().rename('n').reset_index()
    role_counts['gas_name'] = role_counts.gas.map(GASES)
    role_counts['role'] = np.where(role_counts.batch == 8, '이미 사용한 개발 자료', '반복 관찰한 탐색 평가')
    role_counts.to_csv(OUT / 'batch_class_support.csv', index=False, encoding='utf-8')
    delta_equal = 100 * (summary.loc['B', 'equal_batch9_10_macro_f1'] - summary.loc['A', 'equal_batch9_10_macro_f1'])
    scope8 = metrics[metrics.scope == '8'].set_index('model')
    difference8 = 100 * (scope8.loc['B', 'macro_f1'] - scope8.loc['A', 'macro_f1'])
    pooled_classes = classes[classes.scope == 'pooled_9_10']
    deltas = []
    for scope in ['8', '9', '10', 'pooled_9_10']:
        for gas in GASES:
            a = classes[(classes.model == 'A') & (classes.scope == scope) & (classes.gas_id == gas)].iloc[0]
            b = classes[(classes.model == 'B') & (classes.scope == scope) & (classes.gas_id == gas)].iloc[0]
            deltas.append(dict(scope=scope, gas=GASES[gas], support=int(a.support),
                               correct_A=int(a.correct_n), correct_B=int(b.correct_n),
                               recall_A=a.recall, recall_B=b.recall, recall_delta_pp=100 * (b.recall - a.recall),
                               f1_A=a.f1, f1_B=b.f1, f1_delta_pp=100 * (b.f1 - a.f1)))
    deltas = pd.DataFrame(deltas)
    deltas.to_csv(OUT / 'class_performance_changes.csv', index=False, encoding='utf-8')
    test_text = ('전체 테스트 실행 전. 확정 결과는 test_results.xml 및 최종 검증 기록 참조.' if test_status is None else
                 f'전체 {test_status["passed"]}개 통과, 기존 {test_status["failed"]}개 실패. '
                 f'신규 {test_status["new_tests"]}개 모두 통과. 신규 실패 {test_status["new_failures"]}개.')
    sections = []

    def section(title, body):
        sections.append(f'<section><h2>{title}</h2>{body}</section>')

    section('1. 연구 배경 및 목적',
            '<p>가중치·특징·모델을 바꾸지 않고 기존 기준 SVM(A)과 Train1–7 확장 SVM(B)의 '
            '일반화 근거를 검토한다. 좋은 점수와 실패·불확실성을 같은 기준으로 제시한다.</p>'
            '<div class="warning"><b>새 독립 Test 없음.</b> 현재 프로젝트와 설정된 원본 경로에서 '
            '독립적으로 확보된 새로운 측정 자료가 확인되지 않았다. 독립 최종 성능을 측정했다고 '
            '주장하지 않는다. 공식 주 후보는 계속 모델 A이며 B는 고정된 확장 비교 모델이다.</div>')
    section('2. 데이터셋과 평가 자료의 역할',
            '<p>UCI Gas Sensor Array Drift Dataset의 기존13,910행·128특징·6종·10Batch를 '
            '읽었다. 원본은 복사·수정하지 않았다. 개별 측정 시각·농도·환경·세션 정보가 없어 '
            'Batch 번호를 실제 경과 시간으로 변환하지 않았다.</p>' + table(role_counts) +
            '<p>Batch8(294개)은 개발·선정 과정에 사용됐다. Batch9(470개)·10(3600개)은 '
            '이미 여러 단계에서 반복 확인한 탐색 평가 자료다. 세 Batch 모두 두 고정 모델의 '
            '전처리 Fit에는 들어가지 않지만 연구 전체에서 독립적인 새 자료는 아니다. '
            '저장소와 설정된 원본 경로 밖의 자료 존재 여부까지 확인한 것은 아니다.</p>')
    section('3. 기존 1–9단계 결과와 재현성', table(history) +
            '<p>원래 저장 모델을 재사용해 과거 예측과 지표를 대조했다. 분류기·전처리 재학습은 없다. '
            '1단계는 원본의 파일 지문·표본·클래스 검증으로 확인하고, 분류기를 학습한 단계와 '
            '기존 예측을 재사용한 진단 단계는 원래 예측을 모델로 다시 계산해 확인했다.</p>' + table(replay) +
            f'<p>확인된 과거 예측 비교 행 {int(replay.rows.sum()):,}개, 지표 스칼라 '
            f'{int(metric_replay.scalars_checked.sum()):,}개. 이 행 수는 같은 표본의 단계별 중복 비교를 '
            '포함하며 고유 평가 표본 수가 아니다. 상세는 historical_prediction_replay.csv와 '
            'historical_metric_replay.csv에 있다. 기존3건 테스트 실패는 재현 불일치와 별도 기록한다.</p>')
    section('4. 10단계 검증 설계와 고정 모델', table(pd.read_csv(OUT / 'model_audit.csv')) +
            '<p>A는6단계 B_SVM_balanced, Train1–6(5933개). B는9단계 기본 balanced '
            'Train1–7(9546개). 모두128입력·median imputer·StandardScaler·RBF SVM C1·gamma=scale을 '
            '유지한다. 저장된 스케일러 평균·분산·표본 수, 정답1–6 매핑과 원래 모델 해시를 확인했다. '
            'Train과 Batch8–10의 행·정확 특징 중복은0건이다.</p>'
            '<p>새 독립 자료0개, 신규 분류기 Fit0회, 전처리 Fit0회. 평가 전에 모델 경로·해시·'
            '부트스트랩2000회·seed42·계산법을 experiment_config.json에 고정했다. '
            'C·gamma·가중치·특징·임계값·후보를 결과에 맞춰 바꾸지 않았다.</p>')
    section('5. 모델 A/B 비교', table(summary.reset_index()) +
            f'<p><b>관찰:</b> Batch9–10 동일 가중 Macro F1은 '
            f'{100 * summary.loc["A", "equal_batch9_10_macro_f1"]:.2f}%→'
            f'{100 * summary.loc["B", "equal_batch9_10_macro_f1"]:.2f}%({delta_equal:+.2f}pp). '
            f'합산은 {100 * summary.loc["A", "pooled_macro_f1"]:.2f}%→'
            f'{100 * summary.loc["B", "pooled_macro_f1"]:.2f}%. '
            '합산은 큰 Batch10의 영향을 더 받는다. 표의 지표는0–1 범위, 그래프는% 단위다.</p>'
            '<p><b>해석:</b> 확장 학습이 이 관측 자료에서는 유망하지만 독립적인 새 시기의 '
            '일반화 효과를 확정한 것은 아니다.</p>')
    section('6. Batch별 성능과 표본 수',
            graph('batch_macro_f1', 'Batch9·10은 B가 높지만 개발 Batch8은 A가 높다. 숫자8→9→10 순서를 고정하고 막대 높이를 CSV와 자동 대조했다.') +
            table(metrics) + graph('class_recall_heatmap', '셀은 Recall와 정답/실제 표본 수다. Batch8 Toluene18개, Batch9 Toluene101개의 작은 지지도를 함께 확인해야 한다.') +
            graph('performance_changes', '관찰된 Batch 변동이 줄어도 새로운 Batch의 안정성을 보장하지 않는다. 개선과 손실이 가스별로 다르다.'))
    focus = deltas[(deltas.gas.isin(['Toluene', 'Acetaldehyde'])) & (deltas.scope.isin(['9', '10']))]
    loss = deltas[deltas.recall_delta_pp < 0]
    section('7. 가스별 실패·개선·악화',
            graph('focus_correct_errors', 'Batch9 Toluene은 A0/101, B1/101이다. 0%가 사라졌다는 사실만으로 실패가 해결됐다고 볼 수 없다. Acetaldehyde 개선도 다른 가스 손실과 함께 평가한다.') +
            table(focus) + table(pairs[pairs.gas_id.isin([4, 6])]) +
            '<p>Batch9 Toluene의 B 예측은 Acetaldehyde96개·Ethanol4개·Toluene1개다. '
            '같은 Batch의 Acetaldehyde Recall은74/75(98.67%)로 높아졌지만 Precision은74/174(42.53%)였다. '
            '이는 높은 Recall과 다른 가스의 오분류 유입이 함께 발생한 사례다.</p>' +
            '<h3>확장으로 Recall이 낮아진 가스</h3>' + table(loss) +
            '<h3>전체 가스의 합산 변화</h3>' + table(deltas[deltas.scope == 'pooled_9_10']) +
            '<h3>두 집중 가스의 예측 변화 조합</h3>' + table(transitions[transitions.gas_id.isin([4, 6])]) +
            '<p>예측 클래스 번호는1=Ethanol,2=Ethylene,3=Ammonia,4=Acetaldehyde,5=Acetone,6=Toluene. '
            'A만 맞힌 표본과 B만 맞힌 표본을 같은 실제 표본에서 비교했다. 오분류 조합만으로 '
            '두 가스의 화학적 유사성을 단정하지 않는다. Recall과 F1의 변화 방향이 다를 수도 있다.</p>')
    section('8. 모델별 Confusion Matrix',
            graph('confusion_model_A', '모델 A의 Batch8·9·10. 셀 첫 줄은 개수, 괄호는 실제 가스 행 support로 나눈 비율이다. CSV에는 원래 개수와 행 비율을 모두 보존했다.') +
            graph('confusion_model_B', '모델 B에 같은 정규화·색상 범위·축을 사용했다. 가스별 정답 수와 주요 오분류 방향을 같은 조건에서 비교한다.') +
            '<p>행은 실제 가스, 열은 예측 가스다. 행 정규화 비율이며 전체 표본 또는 예측 열 기준의 '
            '정밀도가 아니다. 모든 셀 표시값을 confusion_matrices.csv와 자동 대조했다.</p>')
    ci = intervals[intervals.metric == 'macro_f1']
    focus_wilson = wilson[wilson.gas_id.isin([4, 6])][
        ['model', 'scope', 'gas', 'support', 'correct_n', 'recall', 'wilson_lower', 'wilson_upper']]
    section('9. 통계적 불확실성',
            '<div class="warning">아래95% 구간은 관측된 자료 내부의 조건부 재추출 요약이다. '
            '독립적인 미래 Batch 일반화의 신뢰구간이 아니며 통계적 유의성이나 현장 성능을 보장하지 않는다.</div>'
            '<p>Batch×실제 가스별 표본 수를 고정하고 같은 표본의 A/B 예측 쌍을 함께 '
            '복원추출했다. joint prediction 셀의 다항추출은 해당 층의 행 재추출과 동일하다. '
            '2000회, seed42,2.5/97.5 백분위 구간을 사용했다. Batch를 독립 추출하거나 '
            '시간 블록을 재추출하지 않았다. 개별 측정 시각·세션이 없어 시간 의존성은 보정하지 못했다.</p>' +
            table(ci) + table(focus_wilson) +
            '<p>Recall의 Wilson 구간은 이항 독립 표본 가정의 참고치다. 상관된 측정이면 '
            '명목95% 보장에 맞지 않을 수 있다. 경험적 정답0개에서는 부트스트랩 구간이0으로 '
            '퇴화할 수 있어 Wilson 참고 구간도 병기했다. 어느 구간도 새 시기의 실패율 상한을 뜻하지 않는다.</p>'
            '<p>계산 정의 참고: <a href="https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm">NIST Wilson 비율 구간</a>, '
            '<a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html">SciPy paired·percentile bootstrap 설명</a>. '
            '이번 구현은 층화된 고정 예측의 다항추출이며 SciPy 기본 BCa를 실행했다고 주장하지 않는다.</p>')
    section('10. 센서 분포와 모델 신뢰성의 한계',
            graph('sensor_distribution_6', '7단계에서 진단용으로 정한 Toluene 특징을 그림에만 재사용했다. 공통 모델 A Train 스케일러로 변환했으며 새 Fit·입력 특징 변경은 없다.') +
            graph('sensor_distribution_4', 'Acetaldehyde 역시 Train 범위와 Batch별 분포 차이가 보이지만 농도·환경·센서 변화의 원인을 분리할 수 없다. 점을 제거하지 않고 계산에 유지했다.') +
            '<p>그림의 상자는 IQR, 중앙선은 중앙값, 수염은1.5×IQR, 점은 수염 밖 값이다. '
            '선정 특징은 이미 미래를 본 후의 진단 목록이므로 새로운 예측 근거의 독립 검증이 아니다. '
            '원래7단계128개 특징의 조건부 Wasserstein 결과를 참고하되 분포 이동의 크기만으로 '
            '성능이 단조롭게 바뀌거나 센서 고장·노화가 원인이라고 해석하지 않는다.</p>'
            '<p>Train1–7은 Toluene546→1114개, Acetaldehyde484→1228개로 늘고 시기·클래스 구성도 '
            '함께 바뀐다. 분포 이동은 관찰, 드리프트·농도·환경의 인과 기여는 미확인이다. '
            '닫힌6클래스 자료의 성능만으로 미지 가스·혼합 가스·실제 현장 적용 가능성을 주장할 수 없다.</p>' +
            '<p>' + html.escape(test_text) + '</p><p>기존3건은 과거 소스 SHA, 누락 임시 파일 후보, '
            '7단계 전체 모델 목록 고정 검사 충돌이다. 기존 테스트·해시 기준은 수정하지 않는다. '
            '원본·기존 파일·모델의 해시는 run_manifest.json과 최종 검증 파일에 기록한다.</p>')
    conclusions = [
        dict(question='확장 학습이 평균 Macro F1을 높였는가?', answer=f'관찰9–10 동일 가중 평균 {delta_equal:+.2f}pp. 개발Batch8은 {difference8:+.2f}pp로 하락.'),
        dict(question='개선된 가스는?', answer='합산 Toluene Recall46.22→67.76%, Acetaldehyde18.67→60.59%. 가스별 F1·Recall 표 참고.'),
        dict(question='여전히 실패하는 가스는?', answer='B의 Batch9 Toluene1/101(0.99%), Batch10 Acetone197/600(32.83%).'),
        dict(question='안정성 개선이 일관적인가?', answer='아님. 관찰 변동은 줄었지만 Batch8 Macro F1·Ethanol 등 Recall 손실과 특정 가스 실패가 남음.'),
        dict(question='데이터 양 증가만의 효과인가?', answer='아님. 시기·클래스 구성·농도 가능성·기본 클래스 가중치가 함께 달라짐.'),
        dict(question='독립 평가 없이 B를 최종 선정할 수 있는가?', answer='불가. 현재 공식 주 후보 A 유지, B는 확장 비교 모델.'),
        dict(question='현장 적용 성능을 주장할 수 있는가?', answer='불가. 새 시기·환경·농도·세션의 독립 검증과 운영 기준이 없음.'),
    ]
    pd.DataFrame(conclusions).to_csv(OUT / 'conclusions.csv', index=False, encoding='utf-8')
    section('11. 최종 결론', table(pd.DataFrame(conclusions)) +
            '<p>이번 단계는 독립 평가의 부재를 확인하고 기존 결과를 엄격히 재현한 신뢰성 평가다. '
            'Model B의 탐색적 개선은 보존하되 독립 최종 성능으로 승격하지 않는다. '
            '공식 주 후보·하이퍼파라미터·가중치·전처리·선정 규칙은 유지한다.</p>')
    section('12. 향후 독립 검증에 필요한 데이터',
            '<p>현재 자료 이후의 새로운 시기에 수집한6종 가스 자료가 필요하다. '
            '가스별 농도 범위·온습도·측정 환경·센서 개체와 교정 이력·측정 시각·세션 ID·'
            '참조 측정값을 기록하고 여러 시기와 세션에서 반복 확보해야 한다. '
            '가스·농도·환경·시기의 대표성을 확보하며 단순히 기존 행을 다시 나누지 않는다.</p>'
            '<p>수집 전 모델 버전·전처리·분류 대상·Macro F1·최소 클래스 Recall·허용 오류·'
            'Batch 가중 방식과 실패 처리 기준을 고정한다. 독립 평가 정답은 개발에 공개하지 않고 '
            '평가 시점에 한 번 사용한다. 필요한 표본 수·새 Batch 수는 허용 오류와 세션 상관을 '
            '고려한 설계로 결정해야 하며 임의의 수로 성능을 보장하지 않는다. '
            '새 자료가 없으면 최종 일반화 판단과 실제 현장 배포 주장을 유보한다.</p>')
    document = '<!doctype html><html lang="ko"><meta charset="utf-8"><title>시간순 일반화 검증과 모델 신뢰성</title>'
    document += '<style>body{font:16px/1.7 "Malgun Gothic",sans-serif;max-width:1500px;margin:25px auto;padding:20px}'
    document += 'section{overflow-x:auto;margin:38px 0}table{border-collapse:collapse;font-size:12px}'
    document += 'td,th{border:1px solid #bbc8d0;padding:6px}img{max-width:100%}h1,h2{color:#173a58}'
    document += '.warning{background:#fff3d9;border-left:5px solid #bd7f14;padding:16px}figcaption{color:#3d5363}</style>'
    document += '<h1>10단계 · 시간순 일반화 검증 및 모델 신뢰성 평가</h1>' + ''.join(sections) + '</html>'
    (ROOT / 'reports/temporal_generalization_validation_report.html').write_text(document, encoding='utf-8')
    summary_text = '# 10단계 시간순 일반화 검증 요약\n\n'
    summary_text += '**새 독립 Test 없음. 독립 최종 성능을 측정하지 않았음. 공식 주 후보 Model A 유지.**\n\n'
    summary_text += '신규 모델 학습·전처리 Fit·튜닝·가중치·특징·임계값 변경0회. 저장된 A/B만 비교.\n\n'
    summary_text += '## A/B 관찰 결과\n\n```text\n' + summary.reset_index().to_string(index=False) + '\n```\n\n'
    summary_text += '```text\n' + metrics.to_string(index=False) + '\n```\n\n'
    for row in conclusions:
        summary_text += f'- {row["question"]} {row["answer"]}\n'
    summary_text += '\n## 불확실성과 검사\n\n'
    summary_text += 'Batch×실제 가스 내부의 paired2000회·seed42·백분위95% 조건부 구간. '
    summary_text += '시간·세션 의존성 미보정이므로 미래 일반화의 신뢰구간이 아님.\n\n'
    summary_text += test_text + '\n\n'
    summary_text += '## 주요 그래프\n\n'
    for name in ['batch_macro_f1', 'class_recall_heatmap', 'confusion_model_A', 'confusion_model_B',
                 'focus_correct_errors', 'performance_changes', 'sensor_distribution_6', 'sensor_distribution_4']:
        summary_text += f'- outputs/temporal_generalization_validation/{name}.png\n'
    summary_text += '\n## 재현\n\n```text\n'
    summary_text += '.venv\\Scripts\\python.exe -B -X utf8 -m src.temporal_generalization_validation\n'
    summary_text += '.venv\\Scripts\\python.exe -B -X utf8 -m pytest -q -p no:cacheprovider '
    summary_text += '--junitxml=outputs/temporal_generalization_validation/test_results.xml\n'
    summary_text += '.venv\\Scripts\\python.exe -B -X utf8 -m src.temporal_generalization_validation --finalize\n```\n\n'
    summary_text += '1–9단계 보존 복제본에서10단계 출력이 없는 상태로 실행. 기존 경로가 있으면 중단. '
    summary_text += '기존 결과 삭제·덮어쓰기 없음. Git Commit·Push 없음.\n'
    (ROOT / 'reports/temporal_generalization_validation_summary.md').write_text(summary_text, encoding='utf-8')
    limitations = '''# 10단계 신뢰성·독립 평가의 한계

1. 저장소와 설정된 원본 경로에 확인된 새 독립 데이터가 없음. 기기 전체 또는 외부 기관의 데이터 부재를 단정한 것은 아님.
2. Batch8은 개발·선정에 사용했고9–10은 여러 단계에서 관찰했으므로 세 Batch 모두 독립 최종 Test가 아님.
3. 과거 랜덤 분할은 모든 시기의 일부를 Train에 사용했음. 원래 Test를 이름만 바꾸거나 재분할해 독립성을 복원할 수 없음.
4. Train1–6/1–7의 시기·표본 수·클래스 구성·기본 클래스 승수가 함께 달라져 데이터 양 하나의 인과 효과를 추정할 수 없음.
5. Toluene Batch9의1/101은 사실상 큰 실패로 남음. Batch8 Toluene18개 등 작은 지지도에 주의.
6. paired 층화 부트스트랩2000회·seed42는 고정된 예측의 관측 집합 내부 재추출 요약. 실제 시간 블록·세션을 추출하지 않아 미래 Batch 일반화의 신뢰구간이 아님.
7. Wilson95% Recall 구간도 이항 독립 가정의 참고치. 측정 간 상관이 있으면 명목 포함률을 보장하지 못함. 경험적0%의 bootstrap 퇴화와 미래 오류 확률을 구분해야 함.
8. 3개 관찰 Batch 또는10개 원래 Batch를 대규모 독립 반복으로 간주하지 않음. Batch 변동 SD는 장기 운영 안정성의 확정 증거가 아님.
9. 원본에 개별 timestamp·농도·온습도·환경·세션·센서 교정 정보가 없어 드리프트·농도·환경의 효과를 분리할 수 없음.
10. 기존7단계 진단 특징 그림은 이미 미래를 본 후의 목록을 시각화에만 사용. 이번 모델의 입력 선택·전처리 Fit·튜닝에는 유입되지 않음.
11. 정확 특징 중복0건은 근접 반복 측정이나 같은 세션 의존성이 없다는 증명이 아님.
12. 한글 폰트·숫자 Batch 순서·그림 표시값은 CSV와 자동 대조했음. 기존1–9단계 그래프·코드·해시 기록은 수정하지 않음.
13. 현재6종 단일 가스 자료의 지표만으로 미지 가스·혼합 가스·현장 안전성·운영 적용 가능성을 주장할 수 없음.
14. Model A를 공식 주 후보로 유지하며 Model B는 확장 비교 모델. 독립 평가 없이 최종 모델로 확정하지 않음.

## 독립 검증 자료와 절차
새 시기·여러 세션에서6종 가스와 농도·환경 조건을 대표하도록 자료를 확보할 것.
측정 시각·세션 ID·센서 ID·농도·온습도·교정 이력·참조값을 기록할 것.
수집 전에 모델 버전·전처리·성능/최소Recall/허용오류·Batch 가중·판정 기준을 고정하고 정답을 개발 과정에서 차단할 것.
클러스터 의존성을 고려한 표본 설계를 수행하고 독립 평가 정답으로 추가 튜닝하지 않을 것.

계산 정의 참고: [NIST Wilson 구간](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm),
[SciPy paired bootstrap](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html).
'''
    (ROOT / 'reports/temporal_generalization_limitations.md').write_text(limitations, encoding='utf-8')
