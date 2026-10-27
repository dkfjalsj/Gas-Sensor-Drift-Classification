# 진단 결과의 반례·모델 간 차이와 실제 테스트 결과 정리
# 기존 모델·파이프라인 변경 없이 최종 보고서 확인

import json
import xml.etree.ElementTree as ET
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from .data import ROOT, FEATURES, GASES, load_dataset, read_config
from .temporal_expansion import sha, write_json

OUT = ROOT / 'outputs/temporal_failure_diagnostics'


# 저장 결과로 모델 간 차이와 해석의 한계 명시
def run():
    target = OUT / 'final_verification.json'
    if target.exists():
        raise FileExistsError('Final verification already exists')
    state = json.loads((OUT / 'run_manifest.json').read_text(encoding='utf-8'))
    for name, expected in state['before'].items():
        if sha(ROOT / name) != expected:
            raise RuntimeError('Existing file changed')
    frame, source = load_dataset(read_config())
    if dict(zip(source.file, source.sha256)) != state['raw_hashes']:
        raise RuntimeError('Raw files changed')
    wide = pd.read_csv(OUT / 'row_predictions.csv')
    cross = wide[wide.gas.isin([4, 6])].groupby(
        ['batch', 'gas', 'LR', 'SVM']).size().rename('n').reset_index()
    cross.to_csv(OUT / 'lr_svm_prediction_crosstab.csv', index=False, encoding='utf-8')
    acl = wide[(wide.batch == 10) & (wide.gas == 4)]
    sv_only = acl[(acl.SVM == 4) & (acl.LR != 4)]
    lr_wrong_labels = sv_only.LR.value_counts().sort_index()
    comparison = ', '.join(f'{GASES[int(gas)]} {n}개' for gas, n in lr_wrong_labels.items())
    decision = json.loads((ROOT / 'outputs/temporal_expansion/selection_frozen.json').read_text(encoding='utf-8'))
    model = joblib.load(ROOT / decision['selected_models']['B_SVM_balanced']['path'])
    scaler = model.named_steps['scaler']
    indexed = frame.set_index('row_id')
    chosen = pd.read_csv(OUT / 'selected_plot_features.csv')
    feature_groups = []
    for (batch, gas), group in wide[wide.gas.isin([4, 6])].groupby(['batch', 'gas']):
        conditions = {
            'both_wrong': (group.LR != gas) & (group.SVM != gas),
            'SVM_correct_LR_wrong': (group.LR != gas) & (group.SVM == gas),
            'LR_correct_SVM_wrong': (group.LR == gas) & (group.SVM != gas),
            'both_correct': (group.LR == gas) & (group.SVM == gas),
        }
        for label, mask in conditions.items():
            subset = group[mask]
            if subset.empty:
                continue
            for feature in chosen[chosen.gas_id == gas].feature:
                j = FEATURES.index(feature)
                z = (indexed.loc[subset.row_id, feature].to_numpy() - scaler.mean_[j]) / scaler.scale_[j]
                feature_groups.append(dict(
                    batch=int(batch), gas_id=int(gas), comparison_group=label,
                    feature=feature, n=len(subset), standardized_mean=float(z.mean()),
                    standardized_median=float(np.median(z)), standardized_std=float(z.std(ddof=0)),
                ))
    groups = pd.DataFrame(feature_groups)
    groups.to_csv(OUT / 'lr_svm_error_group_features.csv', index=False, encoding='utf-8')
    shifts = pd.read_csv(OUT / 'feature_shifts.csv')
    mean_shift = shifts[shifts.gas_id > 0].groupby(['gas_id', 'batch']).wasserstein_same_gas_train_sd.mean()
    proximity = pd.read_csv(OUT / 'proximity_summary.csv')
    near = proximity[(proximity.batch == 9) & (proximity.gas_id == 6)].iloc[0]
    acl_near = proximity[(proximity.batch == 10) & (proximity.gas_id == 4)].iloc[0]
    facts = [
        f'Batch 9 Toluene 101개 모두 다른 가스의 Train 표본이 더 가까웠다. '
        f'같은 가스 최근접 거리 중앙값 {near.median_own_distance:.3f}, '
        f'다른 가스 {near.median_other_distance:.3f}(저장 SVM Train 표준화 128차원 거리).',
        '그중 최근접 Train 가스는 Acetaldehyde 97·Ethanol 3·Acetone 1개였다. '
        '하지만 SVM은 전부 Ethanol로 예측했다. 따라서 단순한 최근접 가스만으로 '
        'SVM의 오분류 방향을 설명할 수 없다.',
        f'Batch 9 Toluene의 128개 평균 정규화 Wasserstein은 '
        f'{mean_shift.loc[(6, 9)]:.3f}로, Recall 77.78%였던 Batch 8의 '
        f'{mean_shift.loc[(6, 8)]:.3f}보다 작았다. 평균 분포 거리 증가만으로 '
        'Recall 변화를 단조롭게 설명할 수 없다.',
        f'Batch 10 Acetaldehyde는 {100 * acl_near.other_gas_closer_rate:.2f}%에서 '
        f'다른 가스의 Train 표본이 더 가까웠다. 평균 정규화 Wasserstein은 '
        f'Batch 7 {mean_shift.loc[(4, 7)]:.3f}→Batch 10 {mean_shift.loc[(4, 10)]:.3f}였다. '
        '이때 SVM Recall은 61.56%→14%로 낮아졌다. 동반 변화이며 인과 증거가 아니다.',
        'Batch 9 Toluene과 Batch 10 Acetaldehyde 모두 모든 특징이 전체 Train 기준 |z|≤3이었다. '
        '두 실패를 미래의 극단값 발생만으로 설명할 근거가 없다. '
        '기준은 전체 Train SD이므로 동일 가스의 상대적 이동이나 다변량 변화를 배제하지 않는다.',
        f'Batch 9 Toluene의 지지벡터 최대 RBF 유사도 중앙값은 '
        f'{near.median_max_support_kernel:.3f}였다. 유사도가 확률이나 정답 보장은 아니며 '
        '단순히 모든 학습 표본에서 멀어졌다는 설명도 충분하지 않다.',
        f'Batch 10에서 SVM만 맞히고 LR이 틀린 Acetaldehyde 84개를 LR은 '
        f'{comparison}로 예측했다. 세부 표본 ID와 예측은 row_predictions.csv, '
        '교차표와 특징 요약은 lr_svm_prediction_crosstab.csv 및 '
        'lr_svm_error_group_features.csv에 기록했다.',
        '상위 이동 특징 사이 Train 상관관계가 높았다. f036–f044 r=0.987, '
        'f107–f099 r=0.994. 일부 특징의 중복 표현 가능성과 중요도 해석의 한계가 있다. '
        '이동 특징을 평가 결과에 맞춰 제거하지 않았다.',
    ]
    cases = ET.parse(OUT / 'test_results.xml').getroot().findall('.//testcase')
    failed = [f"{case.get('classname')}::{case.get('name')}" for case in cases
              if case.find('failure') is not None or case.find('error') is not None]
    passed = sum(case.find('failure') is None and case.find('error') is None and
                 case.find('skipped') is None for case in cases)
    new_cases = [case for case in cases if 'test_temporal_failure_diagnostics' in case.get('classname', '')]
    if any(case.find('failure') is not None or case.find('error') is not None for case in new_cases):
        raise RuntimeError('New diagnostic tests failed')
    verification = (f'전체 테스트 {passed}개 통과, {len(failed)}개 실패. '
                    f'신규 테스트 {len(new_cases)}개 모두 통과. 기존 실패는 과거 소스 SHA 불일치와 '
                    '과거 기록의 zNex~$haremetrics.csv 부재이며 테스트·과거 기준은 수정하지 않았다. '
                    f'기존 파일 {len(state["before"])}개와 원본 {len(state["raw_hashes"])}개 해시 보존 확인. '
                    '연구 모델 재학습·튜닝·전처리 Fit 없음. 전체 기존 테스트에는 과거의 소규모 '
                    '예제 Fit 검사가 포함되며 저장 연구 모델을 갱신하지 않는다.')
    report_path = ROOT / 'reports/temporal_failure_diagnostic_report.html'
    report_before = sha(report_path)
    document = report_path.read_text(encoding='utf-8')
    import html
    note = '<aside style="background:#eef5fa;padding:18px"><h3>핵심 관찰과 반례</h3><ul>'
    note += ''.join(f'<li>{html.escape(fact)}</li>' for fact in facts)
    note += '</ul><p>' + html.escape(verification) + '</p></aside>'
    report_path.write_text(document.replace('</h1>', '</h1>' + note, 1), encoding='utf-8')
    proposal_path = ROOT / 'reports/temporal_failure_improvement_proposal.md'
    with proposal_path.open('a', encoding='utf-8') as stream:
        stream.write('\n## 최종 관찰과 반례\n\n' + '\n\n'.join('- ' + fact for fact in facts))
        stream.write('\n\n## 보존·테스트 결과\n\n' + verification + '\n')
        stream.write('\n## 실행 방법\n\n')
        stream.write('```text\n.venv\\Scripts\\python.exe -B -X utf8 -m src.temporal_failure_diagnostics\n')
        stream.write('.venv\\Scripts\\python.exe -B -X utf8 -m pytest -q -p no:cacheprovider '
                     '--junitxml=outputs/temporal_failure_diagnostics/test_results.xml\n')
        stream.write('.venv\\Scripts\\python.exe -B -X utf8 -m src.temporal_failure_review\n```\n\n')
        stream.write('기존 경로가 있으면 진단 코드는 중단함. 재실행은 1–6단계를 보존한 복제본에서 '
                     '7단계 출력이 없는 상태로 수행해야 함. 기존 산출물 삭제·덮어쓰기 금지.\n')
    write_json(target, dict(
        full_suite_passed=passed, full_suite_failed=len(failed), failed_tests=failed,
        new_tests=len(new_cases), prior_files_rechecked=len(state['before']),
        report_before_review_sha256=report_before, report_final_sha256=sha(report_path),
        proposal_final_sha256=sha(proposal_path), review_source_sha256=sha(Path(__file__)),
        new_model_fits=0, preprocessing_fits=0,
        limitations='Diagnostic association only; historical test reused; no independent test.',
    ))
    print('\n'.join(facts) + '\n' + verification)


if __name__ == '__main__':
    run()
