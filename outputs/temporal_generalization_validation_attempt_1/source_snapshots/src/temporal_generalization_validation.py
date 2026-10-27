# 고정된 두 SVM의 재현성·시기별 성능·조건부 불확실성 검증
# 독립 평가 자료 유무 확인 및 기존 원본·모델·산출물 보존

import argparse
import importlib.metadata
import json
import logging
from pathlib import Path
from statistics import NormalDist
import xml.etree.ElementTree as ET

import joblib
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from .data import ROOT, FEATURES, GASES, load_dataset, read_config
from .temporal_expansion import measured_scores, sha, now, write_json

OUT = ROOT / 'outputs/temporal_generalization_validation'
BOOTSTRAP_REPEATS = 2000
SEED = 42


# 표와 입력 파일 목록 저장
def save(name, rows):
    data = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    data.to_csv(OUT / f'{name}.csv', index=False, encoding='utf-8')
    return data


def inventory_data(config):
    rows = []
    suffixes = {'.dat', '.csv', '.tsv', '.parquet', '.xlsx', '.xls', '.npy', '.npz', '.arff', '.h5', '.feather'}
    for path in ROOT.rglob('*'):
        relative = path.relative_to(ROOT)
        if any(part in ['.git', '.venv', '__pycache__'] for part in relative.parts):
            continue
        if path.is_file() and path.suffix.lower() in suffixes:
            derived = relative.parts[0] == 'outputs'
            rows.append(dict(path=str(path), location='project', bytes=path.stat().st_size,
                             role='historical_derived_output' if derived else 'unverified_candidate',
                             confirmed_independent=False))
    for path in sorted(Path(config['data_dir']).rglob('*')):
        if path.is_file():
            rows.append(dict(path=str(path), location='configured_original_directory', bytes=path.stat().st_size,
                             role='known_original_batch' if path.name in [f'batch{i}.dat' for i in range(1, 11)]
                             else 'unverified_candidate', confirmed_independent=False))
    return save('data_inventory', rows)


# 각 표본의 과거 학습·검증·평가 노출 역할 정리
def exposure_audit(frame):
    exposure = frame[['row_id', 'batch', 'gas']].copy()
    old = pd.read_csv(ROOT / 'outputs/model_comparison/split_assignments.csv')
    for experiment in ['A_random', 'B_early', 'B_history']:
        mapping = old[old.experiment == experiment].set_index('row_id').partition
        exposure['stage2_' + experiment] = exposure.row_id.map(mapping)
    stage5 = pd.read_csv(ROOT / 'outputs/model_improvement/split_assignments.csv').set_index('row_id')
    exposure['stage5_role'] = exposure.row_id.map(stage5.partition)
    exposure['stage1_eda_observed'] = True
    exposure['stage6_role'] = np.select([frame.batch <= 6, frame.batch <= 8],
                                       ['train_condition_B', 'validation'], default='exploratory_evaluation')
    for fold, (end, target) in {'A': (3, 6), 'B': (6, 7), 'C': (7, 8)}.items():
        exposure['stage8_9_fold_' + fold] = np.select(
            [frame.batch <= end, frame.batch == target, frame.batch >= 9],
            ['train', 'validation', 'exploratory_evaluation'], default='not_in_fold')
    exposure['model_A_role'] = np.where(frame.batch <= 6, 'train', 'outside_fit_previously_observed')
    exposure['model_B_role'] = np.where(frame.batch <= 7, 'train', 'outside_fit_previously_observed')
    exposure['confirmed_new_independent'] = False
    save('historical_row_exposure', exposure)


# 평가 전에 모델과 계산 방법 고정
def freeze_config(frame, config):
    reports = ['temporal_generalization_validation_report.html',
               'temporal_generalization_validation_summary.md', 'temporal_generalization_limitations.md']
    if OUT.exists() or any((ROOT / 'reports' / name).exists() for name in reports):
        raise FileExistsError('Stage10 outputs already exist')
    old6 = json.loads((ROOT / 'outputs/temporal_expansion/selection_frozen.json').read_text(encoding='utf-8'))
    old9 = json.loads((ROOT / 'outputs/temporal_weighting/selection_frozen.json').read_text(encoding='utf-8'))
    assert old9['selected_scheme'] == 'class_balanced'
    models = {
        'A': dict(**old6['selected_models']['B_SVM_balanced'], train_end=6, official_main_candidate=True),
        'B': dict(**old9['selected_models']['7'], train_end=7, official_main_candidate=False),
    }
    for meta in models.values():
        if sha(ROOT / meta['path']) != meta['sha256']:
            raise ValueError('Frozen historical model hash mismatch')
    OUT.mkdir(parents=True)
    inventory = inventory_data(config)
    experiment = dict(
        frozen_at_seoul=now(), models=models, new_model_fits=0, preprocessing_fits=0,
        evaluation_batches=[8, 9, 10], batch8_role='previously used development data',
        batch9_10_role='repeated historical exploratory evaluation',
        confirmed_independent_rows=0, independent_final_performance_measured=False,
        independence_search_scope=[str(ROOT), config['data_dir']],
        unknown_data_candidates=int((inventory.role == 'unverified_candidate').sum()),
        seed=SEED, bootstrap_repeats=BOOTSTRAP_REPEATS, confidence_level=.95,
        bootstrap='Paired row bootstrap within each Batch x true-gas stratum. Equivalent '
        'multinomial draws of joint (prediction_A,prediction_B) cell counts preserve pairing. '
        'No Batch or chronological-block resampling; 2.5/97.5 percentile intervals. '
        'Conditional descriptive sampling uncertainty, not independent future generalization CI.',
        wilson='95% Wilson score interval for class recall under binomial independence; '
        'temporal/session dependence may invalidate nominal coverage.',
        sensors='Reuse stage7 diagnostic top features for visualization only. All transforms '
        'use frozen Model A Train scaler; no fit or model feature changes.',
        selection_policy='Model A remains official main candidate; Model B remains fixed expansion comparison. '
        'No retuning, reselection, thresholds or model weighting changes.',
        cm_normalization='CSV retains counts; plots use row fractions: actual gas support denominator.',
    )
    write_json(OUT / 'experiment_config.json', experiment)
    return experiment


# 저장 모델의 Train 통계와 입력·클래스 매핑 확인
def evaluate_models(frame, experiment):
    future = frame[frame.batch >= 8].copy().reset_index(drop=True)
    wide = future[['row_id', 'batch', 'gas']].copy()
    metrics, classes, matrices, audit = [], [], [], []
    loaded = {}
    for name, meta in experiment['models'].items():
        model = joblib.load(ROOT / meta['path'])
        loaded[name] = model
        train = frame[frame.batch <= meta['train_end']]
        assert list(model.feature_names_in_) == FEATURES
        np.testing.assert_array_equal(model.classes_, list(GASES))
        np.testing.assert_allclose(model.named_steps['imputer'].statistics_, train[FEATURES].median())
        scaler = model.named_steps['scaler']
        assert scaler.n_samples_seen_ == len(train)
        np.testing.assert_allclose(scaler.mean_, train[FEATURES].mean(), atol=1e-10)
        np.testing.assert_allclose(scaler.var_, train[FEATURES].var(ddof=0), rtol=1e-9)
        classifier = model.named_steps['classifier']
        assert classifier.C == 1 and classifier.gamma == 'scale' and classifier.kernel == 'rbf'
        assert classifier.class_weight == 'balanced'
        hashes = pd.util.hash_pandas_object(frame[FEATURES], index=False)
        assert set(hashes.loc[train.index]).isdisjoint(hashes.loc[frame.batch >= 8])
        assert set(train.row_id).isdisjoint(future.row_id)
        with threadpool_limits(limits=2):
            wide['pred_' + name] = model.predict(future[FEATURES])
        audit.append(dict(model=name, path=meta['path'], sha256=sha(ROOT / meta['path']),
                          train_end=meta['train_end'], train_n=len(train), feature_count=128,
                          class_mapping_ok=True, train_preprocessing_ok=True,
                          row_overlap=0, exact_feature_overlap=0, params=json.dumps(classifier.get_params())))
        for scope in ['8', '9', '10', 'pooled_9_10']:
            sub = wide[wide.batch >= 9] if scope == 'pooled_9_10' else wide[wide.batch == int(scope)]
            score, per_class, cm = measured_scores(sub.gas, sub['pred_' + name])
            metrics.append(dict(model=name, scope=scope, **score))
            for i, row in enumerate(per_class):
                classes.append(dict(model=name, scope=scope, **row, correct_n=int(cm[i, i]),
                                    error_n=int(cm[i].sum() - cm[i, i])))
                for j, predicted_gas in enumerate(GASES):
                    matrices.append(dict(model=name, scope=scope, actual_id=row['gas_id'],
                                         predicted_id=predicted_gas, count=int(cm[i, j]), support=int(cm[i].sum()),
                                         row_fraction=float(cm[i, j] / cm[i].sum())))
    save('model_audit', audit)
    save('predictions_comparison', wide)
    save('evaluation_metrics', metrics)
    save('class_metrics', classes)
    save('confusion_matrices', matrices)
    model_summary = []
    for name in ['A', 'B']:
        group = pd.DataFrame(metrics)
        group = group[(group.model == name) & group.scope.isin(['9', '10'])]
        pooled = pd.DataFrame(metrics).query('model==@name and scope=="pooled_9_10"').iloc[0]
        all_three = pd.DataFrame(metrics).query('model==@name and scope in ["8","9","10"]')
        model_summary.append(dict(model=name, train_end=experiment['models'][name]['train_end'],
                                  equal_batch9_10_macro_f1=float(group.macro_f1.mean()),
                                  batch9_10_sd=float(group.macro_f1.std(ddof=0)),
                                  batch8_10_sd=float(all_three.macro_f1.std(ddof=0)),
                                  pooled_macro_f1=pooled.macro_f1, toluene_recall=pooled.toluene_recall,
                                  acetaldehyde_recall=pooled.acetaldehyde_recall,
                                  pooled_min_class_recall=pooled.min_class_recall,
                                  worst_batch_class_recall=float(group.min_class_recall.min()),
                                  other_four_f1=pooled.other_four_f1))
    save('model_comparison_summary', model_summary)
    return loaded, wide


# 같은 표본에서 바뀐 예측과 공통 실패 집계
def paired_changes(wide):
    rows, transitions = [], []
    for batch, group in wide.groupby('batch'):
        for gas in [0, *GASES]:
            sub = group if gas == 0 else group[group.gas == gas]
            a, b = sub.pred_A == sub.gas, sub.pred_B == sub.gas
            rows.append(dict(batch=int(batch), gas_id=gas, gas='전체' if not gas else GASES[gas], n=len(sub),
                             A_correct=int(a.sum()), B_correct=int(b.sum()), both_correct=int((a & b).sum()),
                             A_only_correct=int((a & ~b).sum()), B_only_correct=int((b & ~a).sum()),
                             both_wrong=int((~a & ~b).sum()), changed_prediction_n=int((sub.pred_A != sub.pred_B).sum()),
                             changed_prediction_rate=float((sub.pred_A != sub.pred_B).mean())))
        for (gas, a, b), n in group.groupby(['gas', 'pred_A', 'pred_B']).size().items():
            transitions.append(dict(batch=int(batch), gas_id=int(gas), prediction_A=int(a), prediction_B=int(b), n=int(n)))
    save('paired_correctness', rows)
    save('prediction_transitions', transitions)


# 혼동행렬 묶음에서 벡터화 지표 계산
def matrix_statistics(matrix):
    true = matrix.sum(axis=2)
    predicted = matrix.sum(axis=1)
    tp = np.diagonal(matrix, axis1=1, axis2=2)
    precision = np.divide(tp, predicted, out=np.zeros_like(tp, dtype=float), where=predicted != 0)
    recall = np.divide(tp, true, out=np.zeros_like(tp, dtype=float), where=true != 0)
    f1 = np.divide(2 * tp, true + predicted, out=np.zeros_like(tp, dtype=float), where=(true + predicted) != 0)
    return dict(accuracy=tp.sum(axis=1) / true.sum(axis=1), macro_precision=precision.mean(axis=1),
                macro_recall=recall.mean(axis=1), macro_f1=f1.mean(axis=1),
                weighted_f1=(f1 * true).sum(axis=1) / true.sum(axis=1)), dict(precision=precision, recall=recall, f1=f1)


def wilson_interval(correct, n):
    z = NormalDist().inv_cdf(.975)
    p = correct / n
    center = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, center - half), min(1.0, center + half)


# Batch·가스 내부에서 같은 A/B 예측 쌍을 함께 재추출
def bootstrap_uncertainty(wide, repeats=BOOTSTRAP_REPEATS, seed=SEED):
    rng = np.random.default_rng(seed)
    draws, points = {}, {}
    for batch in [8, 9, 10]:
        draws[str(batch)] = {name: np.zeros((repeats, 6, 6), dtype=int) for name in ['A', 'B']}
        points[str(batch)] = {name: np.zeros((1, 6, 6), dtype=int) for name in ['A', 'B']}
        for gas in GASES:
            sub = wide[(wide.batch == batch) & (wide.gas == gas)]
            pair = np.zeros((6, 6), dtype=int)
            np.add.at(pair, (sub.pred_A.to_numpy() - 1, sub.pred_B.to_numpy() - 1), 1)
            sampled = rng.multinomial(len(sub), pair.ravel() / len(sub), size=repeats).reshape(repeats, 6, 6)
            draws[str(batch)]['A'][:, gas - 1] = sampled.sum(axis=2)
            draws[str(batch)]['B'][:, gas - 1] = sampled.sum(axis=1)
            points[str(batch)]['A'][0, gas - 1] = pair.sum(axis=1)
            points[str(batch)]['B'][0, gas - 1] = pair.sum(axis=0)
    for dictionary in [draws, points]:
        dictionary['pooled_9_10'] = {name: dictionary['9'][name] + dictionary['10'][name] for name in ['A', 'B']}
    interval_rows, class_rows, replicates = [], [], []
    metric_draws, metric_points = {}, {}
    for scope in draws:
        metric_draws[scope], metric_points[scope] = {}, {}
        class_draws, class_points = {}, {}
        for name in ['A', 'B']:
            metric_draws[scope][name], class_draws[name] = matrix_statistics(draws[scope][name])
            metric_points[scope][name], class_points[name] = matrix_statistics(points[scope][name])
        for name in ['A', 'B', 'B_minus_A']:
            for metric in ['precision', 'recall', 'f1']:
                sample = class_draws[name][metric] if name != 'B_minus_A' else class_draws['B'][metric] - class_draws['A'][metric]
                point = class_points[name][metric] if name != 'B_minus_A' else class_points['B'][metric] - class_points['A'][metric]
                lower, upper = np.quantile(sample, [.025, .975], axis=0)
                for j, gas in enumerate(GASES):
                    class_rows.append(dict(scope=scope, model=name, gas_id=gas, metric=metric,
                                           point=float(point[0, j]), lower=float(lower[j]), upper=float(upper[j])))
    metric_draws['equal_9_10'], metric_points['equal_9_10'] = {}, {}
    for name in ['A', 'B']:
        metric_draws['equal_9_10'][name] = {key: (metric_draws['9'][name][key] + metric_draws['10'][name][key]) / 2
                                          for key in metric_draws['9'][name]}
        metric_points['equal_9_10'][name] = {key: (metric_points['9'][name][key] + metric_points['10'][name][key]) / 2
                                           for key in metric_points['9'][name]}
    for scope in metric_draws:
        for metric in metric_draws[scope]['A']:
            for name in ['A', 'B', 'B_minus_A']:
                sample = metric_draws[scope][name][metric] if name != 'B_minus_A' else metric_draws[scope]['B'][metric] - metric_draws[scope]['A'][metric]
                point = metric_points[scope][name][metric] if name != 'B_minus_A' else metric_points[scope]['B'][metric] - metric_points[scope]['A'][metric]
                lower, upper = np.quantile(sample, [.025, .975])
                interval_rows.append(dict(scope=scope, model=name, metric=metric, point=float(point[0]),
                                          lower=float(lower), upper=float(upper), repeats=repeats, seed=seed))
        for i in range(repeats):
            replicates.append(dict(scope=scope, replicate=i, macro_f1_A=float(metric_draws[scope]['A']['macro_f1'][i]),
                                   macro_f1_B=float(metric_draws[scope]['B']['macro_f1'][i]),
                                   delta=float(metric_draws[scope]['B']['macro_f1'][i] - metric_draws[scope]['A']['macro_f1'][i])))
    return pd.DataFrame(interval_rows), pd.DataFrame(class_rows), pd.DataFrame(replicates)


def run():
    before = {str(p.relative_to(ROOT)): sha(p) for directory in ['src', 'tests', 'models', 'reports', 'outputs']
              for p in (ROOT / directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    before.update({name: sha(ROOT / name) for name in ['config.json', 'training_config.json', 'README.md', 'requirements.txt', '.gitignore']})
    config = read_config()
    frame, source = load_dataset(config)
    raw = dict(zip(source.file, source.sha256))
    old = json.loads((ROOT / 'outputs/temporal_weighting/run_manifest.json').read_text(encoding='utf-8'))
    assert raw == old['raw_hashes']
    experiment = freeze_config(frame, config)
    experiment_hash = sha(OUT / 'experiment_config.json')
    exposure_audit(frame)
    started = now()
    loaded, wide = evaluate_models(frame, experiment)
    paired_changes(wide)
    print('Paired conditional bootstrap, 2000 repeats', flush=True)
    intervals, class_intervals, replicates = bootstrap_uncertainty(wide)
    save('conditional_bootstrap_intervals', intervals)
    save('conditional_class_intervals', class_intervals)
    replicates.to_csv(OUT / 'bootstrap_replicates.csv.gz', index=False, encoding='utf-8', compression='gzip')
    class_data = pd.read_csv(OUT / 'class_metrics.csv', dtype={'scope': str})
    wilson = []
    for row in class_data.to_dict('records'):
        low, high = wilson_interval(row['correct_n'], row['support'])
        wilson.append(dict(**row, wilson_lower=low, wilson_upper=high))
    save('recall_wilson_intervals', wilson)
    from .generalization_history import audit_history
    audit_history(frame, OUT)
    from .generalization_visuals import create_visuals
    create_visuals(frame, loaded['A'])
    from .generalization_report import build_report
    build_report(experiment, test_status=None)
    after = {name: sha(ROOT / name) for name in before}
    assert before == after
    assert all(sha(Path(config['data_dir']) / name) == value for name, value in raw.items())
    assert sha(OUT / 'experiment_config.json') == experiment_hash
    write_json(OUT / 'run_manifest.json', dict(
        completed_at_seoul=now(), evaluation_started_at_seoul=started,
        config_frozen_before_prediction=experiment['frozen_at_seoul'] <= started,
        before=before, after=after, raw_hashes=raw, experiment_sha256=experiment_hash,
        new_model_fits=0, preprocessing_fits=0, original_main_candidate='A',
        code_sha256={name: sha(ROOT / 'src' / name) for name in ['temporal_generalization_validation.py',
                     'generalization_history.py', 'generalization_visuals.py', 'generalization_report.py']},
        package_versions={name: importlib.metadata.version(name) for name in ['numpy', 'pandas', 'scikit-learn', 'matplotlib', 'joblib']},
    ))
    print(pd.read_csv(OUT / 'model_comparison_summary.csv').to_string(index=False), flush=True)


# 전체 검사 후 동일한 결과로 보고서의 테스트 항목만 확정
def finalize():
    if (OUT / 'final_verification.json').exists():
        raise FileExistsError('Stage10 final verification already exists')
    manifest = json.loads((OUT / 'run_manifest.json').read_text(encoding='utf-8'))
    for name, expected in manifest['before'].items():
        assert sha(ROOT / name) == expected
    cases = ET.parse(OUT / 'test_results.xml').getroot().findall('.//testcase')
    failed = [f"{case.get('classname')}::{case.get('name')}" for case in cases
              if case.find('failure') is not None or case.find('error') is not None]
    expected = {'tests.test_diagnostics::test_existing_results_and_models_unchanged',
                'tests.test_models::test_eda_and_sources_preserved_report_complete',
                'tests.test_temporal_failure_diagnostics::test_no_new_fit_calls_or_new_model_files'}
    assert set(failed) == expected
    new = [case for case in cases if case.get('classname', '').endswith('test_temporal_generalization_validation')]
    assert all(case.find('failure') is None and case.find('error') is None for case in new)
    passed = sum(case.find('failure') is None and case.find('error') is None and case.find('skipped') is None for case in cases)
    status = dict(passed=passed, failed=len(failed), failed_tests=failed, new_tests=len(new), new_failures=0)
    experiment = json.loads((OUT / 'experiment_config.json').read_text(encoding='utf-8'))
    from .generalization_report import build_report
    build_report(experiment, test_status=status)
    write_json(OUT / 'final_verification.json', dict(
        completed_at_seoul=now(), test_status=status, prior_files_unchanged=len(manifest['before']),
        raw_files_unchanged=10, new_model_fits=0, confirmed_independent_rows=0,
        final_model_selection_changed=False,
        final_report_sha256={name: sha(ROOT / 'reports' / name) for name in
                             ['temporal_generalization_validation_report.html',
                              'temporal_generalization_validation_summary.md', 'temporal_generalization_limitations.md']},
        graph_validation_sha256=sha(OUT / 'graph_value_checks.csv'),
    ))
    print('FINAL TESTS', status, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--finalize', action='store_true')
    args = parser.parse_args()
    try:
        finalize() if args.finalize else run()
    except Exception:
        logging.exception('Generalization validation failed')
        raise
