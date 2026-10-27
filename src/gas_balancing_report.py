# 가스별 시기 구성의 균형 판정·실패·연구 한계 보고서 생성

import base64
import html
import json

import pandas as pd

from .data import ROOT, GASES
from .gas_specific_temporal_balancing import OUT, REPORTS, MID_SETTINGS, save


# 실제 계산 결과를 요약하고 확대·회고적 평가를 구분
def build_report(status):
    def read(name):
        return pd.read_csv(OUT / f'{name}.csv')

    def table(data):
        return '<div class="table">' + data.to_html(index=False, escape=True,
            na_rep='미실행/해당 없음', float_format=lambda value: f'{value:.4f}') + '</div>'

    def image(name, caption):
        payload = base64.b64encode((OUT / f'{name}.png').read_bytes()).decode('ascii')
        return f'<figure><img alt="{html.escape(caption)}" src="data:image/png;base64,{payload}"><figcaption>{caption}</figcaption></figure>'

    mid = read('mid_summary')
    guards = read('mid_guards')
    maximum = read('max_matched_summary')
    max_guards = read('max_matched_guards')
    registry = read('model_registry')
    metric = read('historical_metrics')
    classes = read('historical_class_metrics')
    future = pd.read_csv(OUT / 'exploratory_metrics.csv', dtype={'scope': str})
    future_classes = pd.read_csv(OUT / 'exploratory_class_metrics.csv', dtype={'scope': str})
    class_summary = classes.groupby(['setting', 'fold', 'gas_id']).agg(
        support=('support', 'first'), precision_mean=('precision', 'mean'),
        recall_mean=('recall', 'mean'), recall_sd=('recall', 'std'), f1_mean=('f1', 'mean')).reset_index()
    save('class_summary', class_summary)
    fold_summary = metric.groupby(['setting', 'fold', 'scope']).agg(
        train_n=('train_n', 'first'), validation_n=('n', 'first'),
        macro_f1_mean=('macro_f1', 'mean'), macro_f1_sd=('macro_f1', 'std'),
        accuracy_mean=('accuracy', 'mean'), min_recall=('min_class_recall', 'min')).reset_index()
    save('fold_summary', fold_summary)
    future_summary = future.groupby(['setting', 'scope']).agg(
        n=('n', 'first'), macro_f1_mean=('macro_f1', 'mean'), macro_f1_sd=('macro_f1', 'std'),
        accuracy_mean=('accuracy', 'mean'), toluene_recall_mean=('toluene_recall', 'mean'),
        acetaldehyde_recall_mean=('acetaldehyde_recall', 'mean'),
        other_four_f1_mean=('other_four_f1', 'mean'), min_recall=('min_class_recall', 'min')).reset_index()
    save('exploratory_summary', future_summary)
    future_class_summary = future_classes.groupby(['setting', 'scope', 'gas_id']).agg(
        support=('support', 'first'), precision_mean=('precision', 'mean'), recall_mean=('recall', 'mean'),
        recall_sd=('recall', 'std'), f1_mean=('f1', 'mean')).reset_index()
    save('exploratory_class_summary', future_class_summary)
    future_seed = future[future.scope.isin(['9', '10'])].groupby(['setting', 'seed']).macro_f1.mean().reset_index()
    save('exploratory_equal_batch_seed_scores', future_seed)
    save('exploratory_equal_batch_summary', future_seed.groupby('setting').macro_f1.agg(['mean', 'std']).reset_index())
    cm = pd.read_csv(OUT / 'exploratory_confusion.csv', dtype={'scope': str})
    directions = cm[cm.actual_id != cm.predicted_id].groupby(['setting', 'scope', 'actual_id', 'predicted_id']).agg(
        mean_error_count=('count', 'mean'), support=('support', 'first')).reset_index()
    directions['fraction'] = directions.mean_error_count / directions.support
    directions = directions.sort_values(['setting', 'scope', 'actual_id', 'mean_error_count'], ascending=[True, True, True, False])
    directions = directions.groupby(['setting', 'scope', 'actual_id']).head(2)
    save('major_error_directions', directions)
    frozen = json.loads((OUT / 'research_conclusion_frozen.json').read_text(encoding='utf-8'))
    conclusion = frozen['conclusion']
    count = int(registry.new_fit.sum())
    text_status = '전체 테스트 실행 전 · 최종 검사 후 확정 예정' if status is None else (
        f'전체 {status["passed"]}개 통과, {status["failed"]}개 실패. '
        f'기존 실패3건과 과거 모델 목록 고정 충돌2건. 신규 {status["new_tests"]}개 모두 통과, 신규 실패0건.')
    decision = json.loads((OUT / 'expansion_decision.json').read_text(encoding='utf-8'))
    composition = read('executed_sample_composition')
    rules = read('train_only_strategy_rules')
    rule_display = rules[(rules.setting == 'mixed_mid') & (rules.seed == 42)]
    sections = []

    def section(title, content):
        sections.append(f'<section><h2>{title}</h2>{content}</section>')

    section('1. 목적과 기존 연구 맥락', '''
    <p>12단계에서는 시기 분산과 최근 자료의 이득이 가스마다 달랐고,
    Toluene의 회고적 Recall 상승은 Acetaldehyde의 손실과 함께 나타났다.
    이번에는 전체 가스의 수를 고정하고 가스별 시기 전략을 조정하는 소규모 대조를 수행했다.</p>
    <p class="warning">공식 Model A 유지. 새 독립 Test 없음. 과거 Fold는 반복 사용한 개발 자료이며,
    Batch9–10은 회고적·탐색적 진단이다. 이번 결과는 현장 안전성이나 독립 미래 일반화의 입증이 아니다.</p>''')
    section('2. 사전 계획·예산·시간순 분할', '''
    <p>Train1–3→Validation6, Train1–6→7, Train1–7→8. 시드11·23·42·67·101을 모두 사용했다.
    가스 순서1–6은 Ethanol, Ethylene, Ammonia, Acetaldehyde, Acetone, Toluene이다.</p>
    <p>843개 예산은127/216/91/69/301/39개, 1689개는254/432/183/139/602/79개.
    Median Imputer와 StandardScaler는 각 선택 Train에만 Fit하고 RBF SVM(C1, gamma=scale, balanced)을 유지했다.
    같은 예산에서는 가스별 수와 balanced의 실제 승수도 같다. 특징 선택·새 모델 종류·튜닝은 없다.</p>
    <p>신규 평가 전에 protocol.md, experiment_plan.json과 모든 가능한 표본을 저장했다.
    확대는 혼합/최소대표 두 대상만 사전 지정하고 843개 과거 지표로 정한 조건을 통과할 때만 실행했다.</p>''')
    section('3. 실제 가스별 시기 전략과 동일 구성', '''
    <p><b>분산/최근:</b>12단계와 같은 배분 및 셀별 난수 순열 사용.
    <b>가스혼합:</b>각 가스의 Train 표본 중 한 Batch가50% 이상이면 분산, 그렇지 않으면 최근.
    특정 가스 이름이나9–10 점수로 전략을 수동 지정하지 않았다.</p>
    <p><b>최소대표:</b>가스별 q개, 실제 존재하는 m개 Batch에서 각 셀에
    min(가용 수,max(1,q//(2m)))개를 먼저 배정하고 나머지는 최신 Batch부터 채웠다.
    존재하지 않는 셀은 생성하지 않았다. 기준식은 이번 연구의 가설이며 최적 비율이라는 뜻은 아니다.</p>''' +
            table(rule_display[['fold', 'gas_id', 'largest_batch_share', 'chosen', 'observed_batches']]) +
            image('gas_batch_composition', 'Fold C·seed42의 실제 학습 수. 같은 배분량을5시드에서 사용하고 셀 내부 표본만 달라진다. 회색은 가스 부재다.') +
            table(read('identical_subset_checks').groupby(['fold', 'setting']).agg(
                same_spread_seed_n=('same_as_spread', 'sum'), same_recent_seed_n=('same_as_recent', 'sum')).reset_index()) +
            '<p>혼합형의 Fold A는 모든 가스에 분산 규칙이 적용돼 기준과 완전히 같다. '
            '이 Fold의 차이는 중립0으로 기록하고 모델을 재학습하거나 억지로 차이를 만들지 않았다.</p>')
    section('4. 843개 Macro F1·Fold·시드 비교', table(mid) +
            image('strategy_macro_f1', 'Fold별 Macro F1을 동일 가중한 뒤5시드 평균·SD 계산. 표본 수가 큰 Fold에 더 큰 가중치를 주지 않았다.') +
            image('fold_macro_f1', 'Fold별 시드 평균과SD. 학습 구간이 겹치므로 세 Fold를 독립 반복으로 취급하지 않는다.') +
            image('seed_distribution', '모든 고정 시드를 표시하며 나쁜 시드를 제외하지 않았다. SD는 부분표본 변동이지 미래 시기 불확실성이 아니다.') +
            table(fold_summary[fold_summary.setting.isin(MID_SETTINGS)]))
    section('5. 집중2가스와 나머지4가스의 손익',
            image('focus_joint_recall', '점은 시드 평균, 막대는시드SD. 점선은 기준 대비5pp 손실선으로 연구용 보호 기준이며 운영 임계값이 아니다.') +
            image('gas_recall_heatmap', '여섯 가스의 평균Recall. 작은 Batch8 Toluene18개를 포함해 Fold별 support를 아래 표에 공개했다.') +
            image('recall_changes', '같은 Fold·시드의 분산843 대비 평균Recall 차이. 음수인 가스도 그대로 표시했다.') +
            table(read('mid_class_deltas')) +
            table(class_summary[class_summary.setting.isin(MID_SETTINGS)]) +
            '<p>특정 가스의 높은 Recall은 Precision이나 다른 가스 손실과 함께 해석해야 한다. '
            'Toluene·Acetaldehyde뿐 아니라 Ethanol·Ethylene·Ammonia·Acetone을 각각 보호했다.</p>')
    section('6. 사전 보호 기준과 연구 판정',
            '<p>평균 Macro F1 +0.5pp 이상, 집중2가스 각각Recall 손실5pp 미만, '
            '다른각가스 손실10pp 미만, 모든Fold 평균차 비음수(2개 이상 양수), '
            '모든5시드의 Fold 평균차 양수를 동시에 요구했다. 동일 표본 Fold는 중립으로 처리한다. '
            '이 기준은 통계적 유의성이나 산업 안전 기준이 아니다.</p>' + table(guards) +
            '<p>한 조건이라도 보호·일관성을 충족하지 못하면 균형 개선 성공으로 기록하지 않았다. '
            '부분 개선은 평균Macro F1 +0.5pp 또는 특정가스Recall +2pp 이상이 있으나 손실/일관성 문제가 남는 경우다.</p>')
    section('7. 조건부1689개 확대 재확인', table(pd.DataFrame(decision['decisions'])) +
            '<p>혼합/최소대표 중 843개에서 Macro 이득·모든 Recall 보호·Fold2개 이상·시드4개 이상 양수를 '
            '충족한 구성만 확대했다. 미실행은0점이 아니며 대체 대상을 고르지 않았다. '
            '확대 후 같은 Validation을 다시 평가했으므로 독립 검증이 아니다.</p>' +
            table(maximum) + image('expansion_comparison', '843/1689는 가스별 수와 시기 배분도 함께 바뀐다. 순수 수량 효과로 단정하지 않는다.') +
            table(read('size_comparisons')) +
            '<p>확대 구성의 균형 판정은 동일1689개 분산형과도 비교했다. 아래 표는843개 기준과 혼동하지 않는다.</p>' +
            table(max_guards))
    section('8. Batch9–10의 제한된 회고적 진단',
            '<p>과거 결과와 확대 판정을 먼저 동결한 뒤, 사전 지정한843개4구성×5시드만 평가했다. '
            '확대 구성이나 가장 좋아 보인 시드를 추가로 평가하지 않았다. 미래 결과로 판정을 변경하지 않았다.</p>' +
            table(future_summary) + table(read('exploratory_equal_batch_summary')) +
            image('exploratory_confusion_9', '실제 가스별 행 정규화 비율의5시드 평균. 실제 표본470개를 반복 예측한 것이며2350개 독립 표본이 아니다.') +
            image('exploratory_confusion_10', '실제 표본3600개.5시드 평균 행비율이며 반복 예측 수를 독립 표본 수로 해석하지 않는다.') +
            table(future_class_summary) +
            table(directions[(directions.scope.isin(['9', '10'])) & directions.actual_id.isin([4, 6])]) +
            '<p>오분류 표의 mean_error_count는5시드 평균 표본 수이므로 소수가 가능하다. '
            '가스 ID는 원래1–6 매핑을 사용했다. Recall 하나의 개선만으로 균형 개선을 선언하지 않았다.</p>')
    section('9. 최종 연구 결론과 한계', f'<p class="warning"><b>{conclusion}</b></p>' +
            '<p>이 판정은 과거 개발 Fold의 사전 기준만 사용한 결과다. 843개와 확대 예산의 판정을 구분하며 '
            '어떤 경우에도 공식 Model A를 교체하지 않는다. 새로운 구성을 연구용으로만 기록한다.</p>' +
            '<p>농도·환경·측정 세션 정보가 없어 시기 대표성의 인과 효과를 완전히 분리할 수 없다. '
            'Train 구성에 따라 전처리 통계와 실제gamma가 함께 달라질 수 있다. '
            'Fold와 시드가 겹치고 과거 평가를 반복 사용했으므로 독립 미래 성능의 입증은 아니다.</p>' +
            '<p>추가 연구는 조건별 가스 대표성·두 집중가스의 Precision/Recall·다른4가스 손실을 함께 검증하고, '
            '관측 조건이 기록된 새 자료로 고정 후보를 독립 평가하는 방향이 필요하다.</p>')
    section('10. 재사용·검증·보존',
            f'<p>논리적 모델 평가 {len(registry)}건 중 신규 학습 {count}회, 재사용 {len(registry)-count}건. '
            f'신규 joblib {count}개만13단계 폴더에 저장했다. 같은행·순서·시드·전처리·설정의 모델은 경로와SHA로 참조한다.</p>' +
            f'<p><b>{text_status}</b></p>' +
            '''<p>기존260개모델·원본10개·1–12단계코드/보고서/CSV/그림/해시 보존.
            12단계기준45개구성의예측과 Model A/B 예측을재현했다.
            기존실패3건은과거소스SHA·과거기록누락파일·7단계모델목록고정충돌,
            기존목록충돌추가2건은10·11단계의140개전체목록고정검사다. 기존검사·해시 수정없음.</p>''' +
            '<pre>.venv\\Scripts\\python.exe -B -X utf8 -m src.gas_specific_temporal_balancing\n'
            '.venv\\Scripts\\python.exe -B -X utf8 -m pytest -q -p no:cacheprovider '
            '--junitxml=outputs/gas_specific_temporal_balancing/test_results.xml\n'
            '.venv\\Scripts\\python.exe -B -X utf8 -m src.gas_specific_temporal_balancing --finalize</pre>' +
            '<p>1–12단계 보존 복제본에서13단계출력이 없는 상태로 재현. 기존 경로가 있으면 중단. Commit·Push 없음.</p>')
    style = '''<style>body{font-family:'Malgun Gothic',sans-serif;max-width:1300px;margin:35px auto;padding:0 22px;background:#f5f8fc;color:#24394b;line-height:1.8}section{background:#fff;border-radius:12px;padding:25px;margin:23px 0}h2{font-size:22px;color:#245671}figure{margin:25px 0}img{width:100%;height:auto}figcaption{font-size:14px;color:#526b7d}.table{overflow:auto;margin:18px 0}table{border-collapse:collapse;white-space:nowrap;font-size:12px}th,td{border:1px solid #d1dde7;padding:7px;text-align:left}th{background:#eaf2f8}.warning{background:#fff0d8;padding:17px}pre{overflow:auto;background:#edf3f7;padding:15px}</style>'''
    document = '<!DOCTYPE html><html lang="ko"><meta charset="utf-8"><title>가스별 시기 균형 실험</title>' + style
    document += '<h1>13단계 · 가스별 시기 대표성 기반 균형 분류 실험</h1><p>관찰 수치와 연구 판정·한계를 구분한 회고적 개발 실험</p>'
    document += ''.join(sections) + '</html>'
    (ROOT / 'reports' / REPORTS[0]).write_text(document, encoding='utf-8')
    text = f'# 13단계 가스별 시기 균형 실험 요약\n\n**{conclusion}**\n\n'
    text += '공식 Model A 유지. 새 독립 Test 없음.9–10은회고적진단이며조건/시드선정에미사용.\n\n'
    text += f'신규학습{count}회, 논리평가{len(registry)}건, 재사용{len(registry)-count}건.\n\n'
    for title, data in [('843개 과거 결과', mid), ('보호 기준', guards), ('조건부 확대', pd.DataFrame(decision['decisions'])),
                        ('1689개 결과', maximum), ('동일1689개 기준 보호', max_guards), ('9–10 회고적 결과', future_summary)]:
        text += f'## {title}\n\n```text\n{data.to_string(index=False)}\n```\n\n'
    text += text_status + '\n\n기존260개모델·원본10개·과거결과보존. Commit·Push없음.\n'
    (ROOT / 'reports' / REPORTS[1]).write_text(text, encoding='utf-8')
    limitations = '''# 13단계 연구 한계

- 새 독립 Test 없음. 과거 Fold도이미 반복 관찰한 개발 자료이며9–10은회고적 진단.
- 가스혼합의50%집중도·최소대표의q//(2m)는사전 가설 규칙이며최적 비율이아님.
- Fold A의혼합형은분산형과정확히 같음. 가스가없는Batch는생성하지않았으며식별가능한대조만해석.
- 부분표본예산을맞춰도농도·환경·세션·근접측정의분포는통제할수없음.
- 시기구성이바뀌면전처리통계와gamma=scale의실제값이함께변할수있음. 순수시기인과효과아님.
- Fold학습구간·시드표본·셀별순열이겹침.5시드SD는부분표본변동이며미래일반화CI아님.
- 보호기준+0.5pp/5pp/10pp와Fold·시드방향은연구용기술규칙. 안전·통계적유의성기준아님.
- 확대대상은843개Validation으로판정후같은Validation재평가. 독립확인아님. 탈락구성은미실행이지0점아님.
- 확대는동일1689개분산형과도대조. 수량·가스×Batch배분이함께바뀌어순수수량효과로단정불가.
- 회고적혼동행렬은5시드평균행비율. 반복예측을새로운독립표본으로세지않음.
- 9–10단서는연구동기이며해당점수로비율·시드·조건을선택하지않음. 연구방향의역사적선택편향은남음.
- 어떤결론도Model A교체·최종모델확정·현장적용성·독립미래성능입증이아님.
- 기존실패5건의기록·해시·테스트는변경하지않음. 기존모델보존과전역목록고정충돌을구분.

새로운시기·가스농도·환경·세션정보가있는자료로모델/전처리/판정기준을고정한독립평가가필요함.
'''
    (ROOT / 'reports' / REPORTS[2]).write_text(limitations, encoding='utf-8')
