# 사전 계획과 실제 통제 결과·교란 한계를 구분한 보고서 생성

import base64
import html
import json

import pandas as pd

from .data import ROOT
from .temporal_representativeness_control import OUT, REPORTS, save


# 새 보고서와 요약·한계 문서 생성
def build_report(status):
    def read(name):
        return pd.read_csv(OUT / f'{name}.csv')

    def table(data):
        return '<div class="table">' + data.to_html(index=False, escape=True,
               float_format=lambda value: f'{value:.4f}') + '</div>'

    def image(name, caption):
        data = base64.b64encode((OUT / f'{name}.png').read_bytes()).decode('ascii')
        return f'<figure><img alt="{html.escape(caption)}" src="data:image/png;base64,{data}"><figcaption>{caption}</figcaption></figure>'

    plan = json.loads((OUT / 'experiment_plan.json').read_text(encoding='utf-8'))
    summary = read('historical_summary')
    effects = read('effect_summary')
    folds = read('fold_summary')
    classes = read('class_summary')
    future = pd.read_csv(OUT / 'exploratory_metrics.csv', dtype={'scope': str})
    future_seed = future[future.scope.isin(['9', '10'])].groupby(['setting', 'seed']).agg(
        equal_batch_macro_f1=('macro_f1', 'mean'), worst_recall=('min_class_recall', 'min'),
        zero_pairs=('zero_recall_classes', 'sum')).reset_index()
    pooled = future[future.scope == 'pooled'][['setting', 'seed', 'macro_f1', 'accuracy',
           'toluene_recall', 'acetaldehyde_recall', 'min_class_recall', 'other_four_f1']]
    future_seed = future_seed.merge(pooled, on=['setting', 'seed'], validate='one_to_one')
    save('exploratory_seed_summary', future_seed)
    future_summary = future_seed.groupby('setting').agg(
        equal_batch_macro_f1_mean=('equal_batch_macro_f1', 'mean'),
        equal_batch_macro_f1_sd=('equal_batch_macro_f1', 'std'),
        pooled_macro_f1_mean=('macro_f1', 'mean'), accuracy_mean=('accuracy', 'mean'),
        pooled_toluene_recall_mean=('toluene_recall', 'mean'),
        pooled_acetaldehyde_recall_mean=('acetaldehyde_recall', 'mean'),
        worst_recall=('worst_recall', 'min'), zero_pairs_mean=('zero_pairs', 'mean'),
        other_four_f1_mean=('other_four_f1', 'mean')).reset_index()
    save('exploratory_summary', future_summary)
    future_classes = read('exploratory_class_metrics').groupby(['setting', 'scope', 'gas_id']).agg(
        support=('support', 'first'), precision_mean=('precision', 'mean'), recall_mean=('recall', 'mean'),
        recall_sd=('recall', 'std'), f1_mean=('f1', 'mean')).reset_index()
    save('exploratory_class_summary', future_classes)
    text_status = '전체 테스트 실행 전 · 최종 검사 후 확정' if status is None else (
        f'전체 {status["passed"]}개 통과 / {status["failed"]}개 실패. '
        f'기존 실패3건 + 승인된 신규 모델 추가와 과거 목록 고정 충돌2건. '
        f'신규 {status["new_tests"]}개 검사 모두 통과, 신규 코드 검사 실패0건.')
    effects_index = effects.set_index('comparison')

    def effect_text(name):
        row = effects_index.loc[name]
        return (f'{row.mean_delta * 100:+.2f}pp (시드차이 SD {row.seed_sd_delta * 100:.2f}pp), '
                f'양수인 Fold {int(row.positive_fold_n)}/3·시드 {int(row.positive_seed_n)}/5, '
                f'사전 기술적 일관성 기준 {"충족" if row.consistent_descriptive else "미충족"}, '
                f'가스 성능 보호 경고 {"있음" if row.protection_flag else "없음"}')

    findings = [
        ('동일 표본 수에서 분산형이 초기형보다 일관되게 우수했는가?', effect_text('spread_vs_early')),
        ('최근 중심형이 더 좋은 경우가 있었는가?', effect_text('recent_vs_spread') + ' (분산형 대비). Fold별 수치는 표에 모두 공개.'),
        ('표본 수 증가가 도움이 됐는가?', '419→843: ' + effect_text('size_mid_vs_small') + '; 843→1689: ' + effect_text('size_max_vs_mid')),
        ('시기와 표본 수 중 어느 효과가 큰가?', '이 사전 예산 범위의 대응 차이 크기만 비교 가능. '
         '배분된 가스×Batch 수와 정보 다양성도 바뀌므로 일반적인 인과 효과 순위를 정할 수 없음.'),
        ('클래스 가중치·전처리가 영향을 줬는가?', '동일벌점: ' + effect_text('unit_vs_balanced') + '; 고정통계: ' + effect_text('anchor_vs_native')),
        ('Toluene 실패에 단서가 추가됐는가?', 'Fold A의 Toluene은 초기1–2에만79개 있고3–5에는 없음. '
         '가중치만 같아도 가스별 시기 범위가 달라질 수 없다는 제약이 남음. '
         '회고적9–10 표의 Toluene과Acetaldehyde 손익을 함께 확인할 것.'),
        ('모든 가스에서 일관된 효과인가?', 'paired_class_effects.csv 및 보호 경고로 확인. 평균 상승만으로 성공 선언하지 않음.'),
        ('무엇을 분리하지 못했는가?', '농도·환경·세션·근접 반복 측정, 전처리 대비 자동gamma 변화, '
         '공통anchor의 추가 무정답 정보, 표본 증가에 따른Batch배분/범위 변화는 분리하지 못함.'),
    ]
    save('interpretation_findings', [dict(question=q, answer=a) for q, a in findings])
    sections = []

    def section(title, content):
        sections.append(f'<section><h2>{title}</h2>{content}</section>')

    section('1. 목적·기존 결과·평가 지위', '''
    <p>1–11단계와 원본·140개 기존 모델 보존. 11단계의 Toluene 혼동 관찰을 출발점으로
    학습 수와 가스별 구성을 맞춘 시기 구성 대조 수행. 최고 점수 탐색이나 모델 교체가 목적이 아님.</p>
    <p class="warning">새 독립 Test 없음. Fold6·7·8도 기존 개발 자료를 재사용하며,
    Batch9–10은 회고적·탐색적 진단. 공식 주 후보 Model A 유지. 조건·시드 사후 선정 없음.</p>''')
    budget_table = pd.DataFrame([dict(budget=level, total=sum(values.values()), **{f'gas{g}': n for g, n in values.items()})
                                for level, values in plan['budgets'].items()])
    section('2. 사전 고정 설계·실제 표본 예산',
            '''<p>Fold A Train1–3→6, B1–6→7, C1–7→8. 시드11/23/42/67/101.
            초기풀Batch1–2의 가스별 수254/432/183/139/602/79를 기준으로25·50·100% 내림.
            최대1689는 엄격한 초기풀 제약 내 최대이며 전체 자료 최대가 아님.</p>''' + table(budget_table) +
            '''<p>초기:1–2에서 오래된Batch부터 채움. 분산:가스가 존재하는 과거Batch를 용량 제한 균등 순환 배분.
            최근:최신Batch부터 채움. 가스×Batch마다 고정 순열의 앞부분을 사용하고 분산 예산은 포함 관계.
            A대조843개는 세 구성·모든Fold에서 동일한 가스별 수를 정확히 유지.
            작은/큰 예산 간 가스비율은 내림으로 소폭 다름.</p>''' +
            table(read('batch_class_support').pivot(index='batch', columns='gas', values='n').reindex(columns=range(1, 7)).fillna(0).astype(int).reset_index()) +
            '''<p><b>제약:</b>Toluene은Batch3–5에 없음. Fold A의 분산은Toluene에서1–2만 사용할 수 있음.
            초기집중형 최대 예산은모든1689개를 사용하므로 같은 조건의 시드 차이가 없어질 수 있음.
            구성 차이가 없는 가스·예산을 인위적으로 다르다고 주장하지 않음.</p>''' +
            image('training_composition', 'Fold C, seed42의 가스×Batch 표본 수. 배분량은 시드와 무관하며 행 선택만 달라짐. 전체Fold·시드 기록은CSV.'))
    section('3. 동일 표본 수에서의 시기 구성 비교',
            table(summary[summary.setting.isin(['early_mid', 'spread_mid', 'recent_mid'])]) +
            image('composition_macro_f1', '843개·동일 가스 수·동일SVM 정책. 막대는Fold6/7/8 동일 가중 평균을5시드 평균한 값, 오차는부분표본 SD.') +
            '<p><b>관찰:</b>분산 대 초기 ' + effect_text('spread_vs_early') +
            '. 최근 대 분산 ' + effect_text('recent_vs_spread') +
            '''. <b>해석:</b>동일 표본/가스 예산 내 구성 비교이며 전처리는 각 선택 Train에서 재추정됨.
            시기별 관측 조건을 무작위 배정한 인과 실험은 아님.</p>''')
    section('4. 동일 분산 정책 내 표본 수 증가',
            image('sample_size_effect', '419→843→1689개. 가스별비율 근사 유지, 균등순환 정책과셀별순열 고정. 시기 구성의 미세 변화도 남음.') +
            '<p><b>관찰:</b>419→843 ' + effect_text('size_mid_vs_small') +
            '; 843→1689 ' + effect_text('size_max_vs_mid') +
            '. <b>한계:</b>표본이 늘면 추가로표현되는 가스×Batch 조건도 달라지므로 순수한 수량 효과로 단정하지 않음.</p>')
    section('5. 시간순Fold와 시드 변동성', table(folds) +
            image('batch_macro_f1', '숫자순 평가Batch6→7→8. 같은 시드라도Fold 학습구간이 겹쳐 독립 반복 아님.') +
            image('seed_distributions', '고정5시드를 빠짐없이 표시. 변동은부분표본 선택에 관한 것이며 새 시기의일반화 신뢰구간 아님.') +
            '''<p>과거평가 합산 지표는historical_pooled_metrics.csv에 별도 저장.
            Fold 동일 가중 지표와 큰Batch가 더영향을 받는 합산 지표를 구분함.
            정식 독립 반복·유의확률을 확보한 실험이 아니므로 통계적 우월성 미확인.</p>''')
    section('6. 가스별 균형·Toluene·Acetaldehyde',
            image('class_recall_heatmap', '가스별Recall은각Fold·시드의 평균. 최소Recall·0Recall 조합·기타4종F1도CSV/표에서 보고.') +
            image('focus_recall', 'Toluene과Acetaldehyde의Batch별support와5시드 변동. 작은 표본으로효과를 과장하지 않음.') +
            table(read('paired_class_effects')) +
            table(classes[classes.setting.isin(['early_mid', 'spread_mid', 'recent_mid']) & classes.gas_id.isin([1, 4, 5, 6])]) +
            '<p>어느한가스의 이득만으로 성공 판정하지 않음. 평균Recall5pp 초과손실·기타4종평균F1 2pp 초과손실·0Recall조합 증가를 보호 경고로 표시.</p>')
    section('7. 전처리·클래스 가중치 대조',
            '''<p>분산843개 동일 행에서 native/공통anchor × balanced/고정unit의2×2 대조.
            native는선택Train만imputer/scaler Fit. anchor는모든Fold보다 과거인Batch1–2 전체1689개로Fit한 통계를공유.
            anchor조건은선택분류기Train 외 과거 무정답 정보가추가되므로 총정보예산 통제로 해석하지 않음.</p>''' +
            image('preprocessing_weight_controls', '기본과고정통계는gamma=scale 정책유지. 실제gamma는Train 변환분산에따라 달라질 수있음. 고정unit은모든가스벌점1.0.') +
            table(effects[effects.comparison.isin(['unit_vs_balanced', 'anchor_vs_native', 'anchor_unit_vs_native_unit'])]) +
            '''<p>A대조에서는가스별수가같으므로balanced의실제승수도동일함. sample_weight없음.
            C의전처리대조는스케일변화와자동gamma변화를함께포함하며 분리된순수효과아님.
            기존A/B통계·class_weight·gamma는reference_*.csv에추출했으며 저장모델은변경하지않음.</p>''')
    section('8. 사전 지정한 Batch9–10 회고적 진단',
            '''<p>과거지표와해석을historical_findings_frozen.json으로먼저고정.
            Fold C의초기843/분산843/최근843/분산1689 각5시드20모델만재사용.
            미래점수로조건·시드·전처리를다시고르지않음. A/B는학습량이다른비통제참조로별도표시.</p>''' +
            table(future_summary) + image('exploratory_macro_f1', '실선은신규통제구성, 점선은기존A/B비통제참조. 독립최종Test아님.') +
            table(future_classes[future_classes.gas_id.isin([1, 4, 5, 6])]) +
            '<p>가스별Recall은Batch별과합산을모두기록. 이평가에서상승하거나하락해도Model A지위를바꾸지않음.</p>')
    section('9. 대응 효과·일관성·8가지 연구 질문', table(effects) +
            ''.join(f'<p><b>{html.escape(q)}</b><br>{html.escape(a)}</p>' for q, a in findings) +
            '''<p>사전기술기준은효과의방향·실용적크기를요약하는규칙이며통계적유의성검정이아님.
            Fold학습영역과시드표본이겹치므로15개결과를독립반복으로취급하지않음.</p>''')
    section('10. 검증·보존·다음 단계', f'<p><b>{text_status}</b></p>' +
            '''<p>120개신규SVM은전용경로에저장. 기존140개모델·원본10개·1–11단계코드/보고서/해시불변.
            전처리Train-only와anchor의추가과거참조를명시적으로구분. 시간순·행/정확특징중복·예산·시드·예측재현·CSV그림값검사.</p>
            <p>기존실패3건은소스과거SHA/누락된과거기록파일/7단계모델목록고정충돌.
            추가2건은10·11단계의전체모델목록140개고정검사와이번승인된120개추가충돌이며기존모델변경아님.
            기존검사/해시수정이나누락파일생성없음.</p>
            <p>다음단계는이번사후최고설정을채택하는대신, 시기대표성·농도/환경정보를가진새자료확보와사전운영기준에따른고정모델평가.
            추가학습은작은통제대조로제한하고실패가스와대표성공백을함께검증할것.</p>''' +
            '<pre>.venv\\Scripts\\python.exe -B -X utf8 -m src.temporal_representativeness_control\n'
            '.venv\\Scripts\\python.exe -B -X utf8 -m pytest -q -p no:cacheprovider '
            '--junitxml=outputs/temporal_representativeness_control/test_results.xml\n'
            '.venv\\Scripts\\python.exe -B -X utf8 -m src.temporal_representativeness_control --finalize</pre>' +
            '<p>1–11단계 보존 복제본에서12단계출력이없는상태로재현. 기존경로가있으면중단. Commit·Push없음.</p>')
    style = '''<style>body{font-family:'Malgun Gothic',sans-serif;max-width:1300px;margin:35px auto;padding:0 22px;color:#233447;line-height:1.8;background:#f6f9fc}section{background:#fff;border-radius:12px;margin:24px 0;padding:25px}h2{color:#24516b;font-size:22px}img{width:100%;height:auto}figure{margin:24px 0}figcaption{font-size:14px;color:#526579}.table{overflow:auto;margin:20px 0}table{border-collapse:collapse;font-size:12px;white-space:nowrap}td,th{border:1px solid #d1dce6;padding:7px;text-align:left}th{background:#e8f1f8}.warning{background:#fff1d8;padding:16px}pre{overflow:auto;background:#eef3f7;padding:16px}</style>'''
    document = '<!DOCTYPE html><html lang="ko"><meta charset="utf-8"><title>시간순 대표성 통제 실험</title>' + style
    document += '<h1>12단계 · 학습 데이터 시기별 대표성 통제 실험</h1><p>사전 고정120회학습 · 5시드 · 3개과거Fold · 모델선정변경없음</p>'
    document += ''.join(sections) + '</html>'
    (ROOT / 'reports' / REPORTS[0]).write_text(document, encoding='utf-8')
    summary_text = '# 12단계 시기별 대표성 통제 실험 요약\n\n'
    summary_text += 'Model A 유지. 새 독립 Test 없음. 8조건×3Fold×5시드=120 SVM 학습. 신규모델120개.\n\n'
    summary_text += '가스별 예산과총수:\n\n' + budget_table.to_string(index=False) + '\n\n'
    for q, a in findings:
        summary_text += f'- {q} {a}\n'
    summary_text += '\n과거 결과:\n\n' + summary.to_string(index=False)
    summary_text += '\n\n미래 회고적 진단(후보선정에미사용):\n\n' + future_summary.to_string(index=False)
    summary_text += '\n\n' + text_status + '\n\n기존원본10개·모델140개·과거기록보존. Commit·Push없음.\n'
    (ROOT / 'reports' / REPORTS[1]).write_text(summary_text, encoding='utf-8')
    limitations = '''# 12단계 통제 실험의 한계

1. 새 독립 Test 없음. 과거Fold도이미관찰한개발자료이며9–10은회고적진단.
2. 초기집중형은Batch1–2로제한. 최대1689는이설계의공통상한이며전체데이터최대아님.
3. 작은/중간/큰예산의내림으로가스비율과balanced승수가조금달라짐.
4. 분산은동일한용량제한정책이지만예산증가에따라가스×Batch배분과표현조건이달라짐. 순수수량효과아님.
5. Fold A Toluene은1–2에만존재. 시간다양성대조를모든가스에동일하게구현할수없음.
6. 공통anchor는선택분류기표본외의Batch1–2통계정보를추가이용. 미래누수는아니지만총정보예산통제와구분.
7. anchor전처리에서는gamma=scale의수치도달라질수있어스케일러단독효과로해석불가.
8. 고정unit은기존balanced와유효벌점이다름. 기존A/B를고친것이아니며튜닝아님.
9. 5시드는부분표본변동만측정. Fold·시드가겹치고독립반복아님. 효과검정p값/미래CI미제시.
10. 기술적일관성기준+0.5pp·Fold3개양수·시드4/5양수는유의성검정이나운영기준아님.
11. 농도·환경·측정세션·근접반복의정보부족으로시기구성의인과효과완전분리불가.
12. 기존A/B는각5933/9546개학습으로신규부분표본모델과학습량이다름. 비통제참조만가능.
13. 9–10평가에서사후최고조건/시드선정하지않음. 공식Model A유지. 현장적용성미입증.
14. 신규모델추가로과거전체모델목록고정검사2개충돌예상. 과거파일/해시변경과구분해공개.

재현은1–11단계보존복제본에서12단계출력이없는상태로수행. 과거검사/해시기록수정금지.
'''
    (ROOT / 'reports' / REPORTS[2]).write_text(limitations, encoding='utf-8')
