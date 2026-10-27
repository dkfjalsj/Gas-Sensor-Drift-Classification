# 14단계 테스트 결과 분류 및 계산된 관찰 결과 보고서 반영
# 신규 학습 없이 저장된 표·모델의 설정만 확인

import html
import json
import xml.etree.ElementTree as ET

import joblib
import numpy as np
import pandas as pd

from .data import ROOT, GASES
from .temporal_expansion import now, sha, write_json
from .nonlinear_feature_transformation import OUT, REPORT_NAMES, render, verify_preservation


# 테스트 실패를 과거 실패와 신규 실패로 구분
def test_summary():
    old_path = ROOT / 'outputs/gas_specific_temporal_balancing/test_results.xml'
    old_tree = ET.parse(old_path)
    old_failures = {(case.attrib.get('classname'), case.attrib.get('name'))
                    for case in old_tree.iter('testcase')
                    if case.find('failure') is not None or case.find('error') is not None}
    cases = list(ET.parse(OUT/'test_results.xml').iter('testcase'))
    failures = []
    for case in cases:
        problem = case.find('failure')
        if problem is None:
            problem = case.find('error')
        if problem is not None:
            key = (case.attrib.get('classname'), case.attrib.get('name'))
            failures.append(dict(classname=key[0], name=key[1],
                                 historical=key in old_failures,
                                 message=problem.attrib.get('message', '')[:1200]))
    new_cases = [c for c in cases if 'test_nonlinear_feature_transformation' in c.attrib.get('classname', '')]
    summary = dict(total=len(cases), passed=sum(c.find('failure') is None and
                   c.find('error') is None and c.find('skipped') is None for c in cases),
                   failed=len(failures), skipped=sum(c.find('skipped') is not None for c in cases),
                   historical_failures=sum(f['historical'] for f in failures),
                   new_failures=sum(not f['historical'] for f in failures),
                   new_test_cases=len(new_cases), new_test_passed=sum(c.find('failure') is None and
                   c.find('error') is None for c in new_cases), failures=failures,
                   historical_failure_reference=str(old_path.relative_to(ROOT)))
    write_json(OUT/'test_summary.json', summary)
    return summary


# 기존 수치에서 변화와 해석을 구분하여 요약
def main():
    tests = test_summary()
    render()
    summary = pd.read_csv(OUT/'summary.csv').set_index('method')
    metrics = pd.read_csv(OUT/'fold_metrics.csv')
    classes = pd.read_csv(OUT/'class_metrics.csv')
    means = pd.read_csv(OUT/'mean_class_metrics.csv').set_index(['method', 'gas'])
    stats = pd.read_csv(OUT/'preprocessing_statistics.csv')
    registry = pd.read_csv(OUT/'model_registry.csv').fillna('')
    actual_settings = []
    for row in registry.itertuples():
        model = joblib.load(ROOT/row.path)
        actual_settings.append(dict(fold=row.fold, method=row.method,
                                    path=row.path, sha256=sha(ROOT/row.path),
                                    steps=[(name, type(step).__name__) for name, step in model.steps],
                                    classifier_params=model['classifier'].get_params(),
                                    actual_gamma=float(model['classifier']._gamma),
                                    train_n=int(model['scaler'].n_samples_seen_),
                                    classes=model['classifier'].classes_.tolist(),
                                    original_fit_seconds=float(row.historical_fit_seconds)))
    write_json(OUT/'actual_settings.json', actual_settings)
    delta = []
    for method in ['signed_log', 'yeo_johnson']:
        for gas in GASES.values():
            row = dict(method=method, gas=gas)
            for metric in ['precision', 'recall', 'f1']:
                row[f'{metric}_delta_pp'] = 100*(means.loc[(method, gas), metric] -
                                                means.loc[('baseline', gas), metric])
            delta.append(row)
    delta = pd.DataFrame(delta)
    delta.to_csv(OUT/'mean_gas_deltas.csv', index=False, encoding='utf-8')
    fold_table = metrics.pivot(index='method', columns='fold', values='macro_f1').mul(100)
    fold_table['mean'] = fold_table.mean(axis=1)
    lines = ['\n## 계산 결과와 해석\n',
             f'- 로그 변환 평균 Macro F1 {summary.loc["signed_log", "mean_macro_f1"]*100:.2f}% '
             f'(기준 대비 {summary.loc["signed_log", "macro_delta"]*100:+.2f}%p). '
             '사전 +0.5%p 기준 미달. 모든 보호 기준을 통과한 후보 없음.',
             '- Fold별 개선 방향 불일치: 두 변환 모두 Batch 8에서 상승했으나 Batch 7에서 하락. '
             'Batch 8 Toluene support 18개의 작은 평가를 전체 일반화 개선으로 확대 해석하지 않음.',
             '- Fold A Batch 6 Toluene은 세 조건 모두 Recall 0%. 분류 실패 완화 목표 미달.',
             '- 로그 변환은 Toluene의 평균 Precision·F1을 높였지만 Recall은 하락. '
             'Acetaldehyde의 평균 Precision·Recall·F1은 모두 하락. 동시 균형 개선 근거 없음.',
             f'- 다른 네 가스 평균 F1 변화: 로그 {100*(summary.loc["signed_log", "other_four_f1"]-summary.loc["baseline", "other_four_f1"]):+.2f}%p, '
             f'Yeo–Johnson {100*(summary.loc["yeo_johnson", "other_four_f1"]-summary.loc["baseline", "other_four_f1"]):+.2f}%p. '
             '평균 보호 기준 내이지만 개별 가스 손실은 아래 표에 공개.',
             '- 오분류 방향도 상충: Fold A Toluene→Acetaldehyde는 기준416→로그441→Yeo–Johnson430개. '
             'Fold B Acetaldehyde→Toluene는67→10→8개로 줄었지만 Acetaldehyde Recall도 하락. '
             '특정 오분류 방향 감소가 전체 정분류 증가를 뜻하지 않음.',
             '- Yeo–Johnson은 평균 Macro F1이 하락하고 Toluene 평균 Recall 손실이 5%p를 초과함. '
             '일부 가스·Fold 향상이 있어 규칙상 B(부분 개선)이나 기준보다 우수한 후보라는 뜻은 아님.',
             '- 해석: 이 두 비선형 변환만으로 시기 변화에 따른 가스 경계 문제를 해결하지 못함. '
             '모든 특징 변환이 무효이거나 센서 드리프트가 유일 원인이라는 결론은 아님.',
             '- 다음 연구는 신규 실험 전 사전 계획을 별도로 고정하고 시기별 모델의 과거 오류 '
             '상호 보완성을 검토할 수 있음. 이번 결과를 보고 변환식·보호 기준을 변경하지 않음.',
             '\n```text\n'+fold_table.to_string(float_format=lambda v:f'{v:.2f}')+'\n```',
             '\n```text\n'+delta.to_string(index=False, float_format=lambda v:f'{v:+.2f}')+'\n```',
             f'\n전체 테스트 {tests["passed"]}개 통과 / {tests["failed"]}개 실패. '
             f'기존 실패 {tests["historical_failures"]}개, 신규 실패 {tests["new_failures"]}개. '
             f'신규 검사 {tests["new_test_passed"]}/{tests["new_test_cases"]} 통과.',
             '\n기존 실패: 과거 소스 SHA 불일치, 과거 임시 파일 후보 부재, 승인된 신규 모델 추가와 '
             '과거 전역 모델 목록 고정 검사 3건 충돌. 과거 테스트·기준·기록 미수정.',
             '\n기준 모델 항등 선택 단계 제거 후 feature-name 경고 발생 가능. 원래 예측과 전체 일치 확인. '
             '설치된 scikit-learn의 probability 인자 폐기 예정 경고는 설정 유지에 따른 경고이며 학습 오류 아님.',
             '\n재실행: 새 빈 결과 경로에서 freeze → run → 전체 pytest → closeout 순서. '
             '기존 경로가 있으면 학습 명령은 덮어쓰기를 거부함. 모델 로딩 시 프로젝트 루트에서 src 모듈 사용.']
    observation = '\n\n'.join(lines)
    (OUT/'calculated_observations.md').write_text(observation, encoding='utf-8')
    summary_path = ROOT/'reports'/REPORT_NAMES[1]
    summary_path.write_text(summary_path.read_text(encoding='utf-8') + observation, encoding='utf-8')
    report_path = ROOT/'reports'/REPORT_NAMES[0]
    section = ('<h2>11. 계산 결과와 해석의 구분</h2><pre>'+html.escape(observation)+
               '</pre><h3>Fold별 Macro F1 (%)</h3>'+fold_table.to_html(float_format=lambda v:f'{v:.2f}')+
               '<h3>6종 가스 지표 증감 (%p)</h3>'+delta.to_html(index=False, float_format=lambda v:f'{v:+.2f}')+
               '<p>수치 안정성 처리 기록: '+html.escape(str(stats.transform_status.value_counts().to_dict()))+'</p>')
    report_path.write_text(report_path.read_text(encoding='utf-8').replace('</body>', section+'</body>'), encoding='utf-8')
    verification = verify_preservation()
    verification.update(completed_at=now(), test_summary=tests,
                        baseline_models_reused=3, new_classifier_fits=6,
                        source_ast_preserved='Existing source bytes unchanged implies same parsed AST',
                        graph_review='Recall heatmap and Train distributions visually inspected; Korean labels readable')
    write_json(OUT/'final_verification.json', verification)
    print(json.dumps(tests, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
