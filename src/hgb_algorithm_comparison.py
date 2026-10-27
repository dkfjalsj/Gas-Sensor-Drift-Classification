# 동일한 과거 학습 행에서 SVM과 HGB 단독 모델 비교
# 사전 계획·Train 전처리·가스별 보호 기준 및 기존 파일 보존 검사

import argparse
import inspect
import json
import logging
import platform
import time
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.utils.class_weight import compute_sample_weight
from threadpoolctl import threadpool_limits

from .data import ROOT, FEATURES, GASES, load_dataset, read_config
from .temporal_expansion import now, sha
from .temporal_svm_ensemble import audit_model
from .nonlinear_feature_transformation import score_predictions, row_digest, digest, build_pipeline

OUT = ROOT/'outputs/hgb_algorithm_comparison'
MODEL_DIR = ROOT/'models/hgb_algorithm_comparison'
REPORTS = [f'hgb_algorithm_comparison_{suffix}' for suffix in
           ['report.html', 'summary.md', 'limitations.md']]
FOLDS = {'A': (3, 6), 'B': (6, 7), 'C': (7, 8)}
CAUTION = ('과거 Fold는 반복 사용한 개발 검증 자료이며 독립 Test가 아님. '
           '학습 구간이 겹치는 Fold를 독립 반복 표본으로 취급하지 않음. '
           'Batch 9~10 신규 평가 없음. 공식 Model A 유지.')
HGB_PARAMS = dict(loss='log_loss', learning_rate=.1, max_iter=100, max_leaf_nodes=31,
                  max_depth=None, min_samples_leaf=20, l2_regularization=0., max_features=1.,
                  max_bins=255, categorical_features=None, monotonic_cst=None,
                  interaction_cst=None, warm_start=False, early_stopping=False,
                  scoring='loss', validation_fraction=None, n_iter_no_change=10, tol=1e-7,
                  verbose=0, random_state=42, class_weight='balanced')


# NumPy 자료형도 손실 없이 JSON 기록
def write(name, value):
    def convert(item):
        if isinstance(item, np.generic):
            return item.item()
        if isinstance(item, np.ndarray):
            return item.tolist()
        if isinstance(item, Path):
            return str(item)
        raise TypeError(type(item).__name__)
    (OUT/name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False,
                                     default=convert), encoding='utf-8')


def save(name, rows):
    table = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    table.to_csv(OUT/f'{name}.csv', index=False, encoding='utf-8')
    return table


# 기존 파일 전체의 바이트 지문 수집
def snapshot():
    result = {}
    for folder in ['src', 'tests', 'outputs', 'reports', 'models']:
        for path in (ROOT/folder).rglob('*'):
            if (not path.is_file() or '__pycache__' in path.parts or OUT in path.parents or
                    MODEL_DIR in path.parents or
                    (path.parent == ROOT/'reports' and path.name in REPORTS)):
                continue
            result[str(path.relative_to(ROOT))] = sha(path)
    for name in ['README.md', 'config.json', 'training_config.json', '.gitignore',
                 'requirements.txt', 'requirements-lock.txt']:
        result[name] = sha(ROOT/name)
    return result


# 동일한 학습·검증 행과 시간순·정확 중복 검사
def splits(frame):
    assert frame.batch.max() <= 8
    fingerprints = pd.util.hash_pandas_object(frame[FEATURES], index=False)
    assignments, supports = [], []
    for fold, (end, batch) in FOLDS.items():
        train, validation = frame[frame.batch <= end], frame[frame.batch == batch]
        assert train.batch.max() < batch
        assert set(train.row_id).isdisjoint(validation.row_id)
        assert set(fingerprints.loc[train.index]).isdisjoint(fingerprints.loc[validation.index])
        assert set(train.gas) == set(GASES)
        for part, sub in [('train', train), ('validation', validation)]:
            assignments.extend(dict(fold=fold, partition=part, row_id=r.row_id,
                                    batch=int(r.batch), gas_id=int(r.gas)) for r in sub.itertuples())
            supports.extend(dict(fold=fold, partition=part, gas_id=g, gas=GASES[g],
                                 n=int((sub.gas == g).sum())) for g in GASES)
    return pd.DataFrame(assignments), pd.DataFrame(supports)


# 지원 기능·기존 SVM 호환성을 학습 전에 검사
def preflight(frame):
    classifier = HistGradientBoostingClassifier(**HGB_PARAMS)
    classifier._validate_params()
    assert classifier.__sklearn_tags__().input_tags.allow_nan
    old = pd.read_csv(ROOT/'outputs/nonlinear_feature_transformation/model_registry.csv')
    results = []
    for fold, (end, _) in FOLDS.items():
        row = old[(old.fold == fold) & (old.method == 'baseline')].iloc[0]
        train = frame[frame.batch <= end]
        try:
            assert sha(ROOT/row.path) == row.sha256
            model = joblib.load(ROOT/row.path)
            check = audit_model(model, train, end)
            results.append(dict(fold=fold, can_reuse=True, path=row.path,
                                sha256=row.sha256, reason='', **check))
        except (ValueError, AssertionError, FileNotFoundError) as exc:
            results.append(dict(fold=fold, can_reuse=False, path=row.path,
                                sha256=row.sha256, reason=repr(exc), train_n=len(train),
                                row_sha256=row_digest(train.row_id)))
    return results


# 결과 확인 전에 두 조건과 보호 기준 고정
def freeze():
    if OUT.exists() or MODEL_DIR.exists() or any((ROOT/'reports'/n).exists() for n in REPORTS):
        raise FileExistsError('Stage16 output exists; no overwrite')
    frame, raw = load_dataset(read_config())
    frame = frame[frame.batch <= 8].copy()
    assignments, supports = splits(frame)
    checked = preflight(frame)
    before = snapshot()
    OUT.mkdir()
    save('split_assignments', assignments)
    save('fold_support', supports)
    write('svm_preflight.json', checked)
    write('preservation_before.json', dict(files=before, raw={r.file:r.sha256 for r in raw.itertuples()}))
    import sklearn
    plan = dict(
        stage=16, frozen_at=now(), folds=FOLDS, models=['SVM', 'HGB'],
        hypothesis='Full Train rows fixed; test whether a different decision-boundary family '
                   'improves temporal six-gas balance. Do not assume HGB superiority.',
        hgb_parameters=HGB_PARAMS,
        parameter_reason='User-proposed standard defaults. No validation-derived selection. '
                         'early_stopping=False and validation_fraction=None prevent internal random '
                         'validation. categorical_features=None because all128 sensor features numeric.',
        preprocessing=dict(SVM='Median Imputer -> StandardScaler -> fixed RBF SVC',
                           HGB='Median Imputer keep_empty_features=True -> HGB; no scaling'),
        missing_policy='HGB native NaN supported, but median imputation fixed for both conditions. '
                       'No imputation-policy comparison. Train-only medians; all128 columns kept.',
        imbalance='HGB class_weight=balanced supported. Fit receives no sample_weight and no validation '
                  'arrays. Effective per-row weight n_train/(6*n_train_gas), Train labels only. '
                  'Same frequency formula as SVM, different loss/optimization; not identical correction effect.',
        metrics='Accuracy, MacroF1 across true-present gases, WeightedF1, per-gas P/R/F1/support/'
                'prediction counts, minimum supported recall, zero recall count, confusion/errors, fit/predict time',
        aggregation='Equal-weight arithmetic mean of3 Fold MacroF1. Per-gas means over supported '
                    'Folds only, unsupported truth=>P/R/F1 NA not zero; other-four F1 equal gas/Fold '
                    'mean of1,2,3,5. Pooled metrics separate; Fold SD descriptive ddof0.',
        protection=dict(macro_gain_min=.005, per_gas_mean_recall_loss_max=.05,
                        other_four_f1_loss_max=.02, zero_recall_increase_max=0, no_new_zero=True,
                        inclusive=True, tolerance=1e-12),
        conclusion='A iff all protection guards. Else B iff mean MacroF1 gain>1e-12 OR any Fold '
                   'MacroF1 gain>1e-12 OR any gas equal-Fold mean F1 gain>1e-12. Else C. '
                   'Isolated precision/recall gain without any F1 gain does not alone imply B.',
        budget=dict(model_evaluations=6, maximum_new_HGB_fits=3,
                    maximum_fallback_SVM_fits=3, expected_reused_SVM=3),
        stop='Only2 fixed conditions. No tuning/new seeds/feature selection/sampling/ensembles. '
             'Fit error aborts condition and records failure; do not retry with different parameters. '
             'Leakage/preservation failure aborts experiment. No future evaluation.',
        complementary_errors='Saved predictions only: both correct, SVM-only, HGB-only, both wrong, '
                             'prediction disagreement; no Oracle or ensemble evaluation.',
        limitation=CAUTION, causal_limit='Different suitable preprocessing and model objectives; '
                                       'not an isolated causal effect of algorithm alone.',
        independent_test=False, future_batches_evaluated=[],
        feature_order=FEATURES, gas_mapping=GASES,
        split_sha256=sha(OUT/'split_assignments.csv'),
        svm_preflight_sha256=sha(OUT/'svm_preflight.json'),
        environment=dict(python=platform.python_version(), sklearn=sklearn.__version__,
                         hgb_signature=str(inspect.signature(HistGradientBoostingClassifier)),
                         hgb_fit_signature=str(inspect.signature(HistGradientBoostingClassifier.fit)),
                         hgb_native_nan=True, hgb_class_weight=True))
    write('experiment_plan.json', plan)
    (OUT/'protocol.md').write_text('# 16단계 사전 고정 계획\n\n'+CAUTION+'\n\n```json\n'+
                                  json.dumps(plan, ensure_ascii=False, indent=2)+'\n```', encoding='utf-8')
    write('plan_lock.json', dict(plan_sha256=sha(OUT/'experiment_plan.json'),
                                protocol_sha256=sha(OUT/'protocol.md')))
    print('Stage16 plan frozen; SVM compatibility checked; no classifier fits yet', flush=True)


# 표본별 두 단독 모델의 오류 비교
def error_agreement(y, svm, hgb):
    y, svm, hgb = np.asarray(y), np.asarray(svm), np.asarray(hgb)
    if y.shape != svm.shape or y.shape != hgb.shape:
        raise ValueError('Same ordered validation rows required')
    a, b = svm == y, hgb == y
    return pd.DataFrame(dict(y_true=y, svm_pred=svm, hgb_pred=hgb,
                             both_correct=a & b, svm_only=a & ~b, hgb_only=~a & b,
                             both_wrong=~a & ~b, disagreement=svm != hgb))


# 평균·가스·Recall0 보호 기준 판정
def judge(metrics, classes):
    baseline = classes[classes.model == 'SVM'].set_index(['fold', 'gas_id'])
    treatment = classes[classes.model == 'HGB'].set_index(['fold', 'gas_id'])
    paired = treatment[['precision', 'recall', 'f1']].join(
        baseline[['precision', 'recall', 'f1']], rsuffix='_svm')
    gas_delta = (paired.recall-paired.recall_svm).groupby('gas_id').mean()
    f1_delta = (paired.f1-paired.f1_svm).groupby('gas_id').mean()
    other = paired[paired.index.get_level_values('gas_id').isin([1, 2, 3, 5])]
    fold_delta = (metrics[metrics.model == 'HGB'].set_index('fold').macro_f1-
                  metrics[metrics.model == 'SVM'].set_index('fold').macro_f1)
    gain = float(fold_delta.mean())
    checks = dict(complete=len(metrics) == 6 and len(paired) == 18,
                  macro_guard=gain >= .005-1e-12,
                  gas_recall_guard=bool((gas_delta >= -.05-1e-12).all()),
                  other_four_guard=float((other.f1-other.f1_svm).mean()) >= -.02-1e-12,
                  zero_count_guard=int(treatment.recall.eq(0).sum()) <= int(baseline.recall.eq(0).sum()),
                  no_new_zero_guard=not bool((paired.recall.eq(0) & (paired.recall_svm > 0)).any()))
    positive = gain > 1e-12 or bool((fold_delta > 1e-12).any()) or bool((f1_delta > 1e-12).any())
    category = 'A' if all(checks.values()) else ('B' if positive else 'C')
    return dict(checks=checks, all_passed=all(checks.values()), conclusion=category,
                mean_macro_delta=gain, fold_deltas={k:float(v) for k, v in fold_delta.items()},
                mean_gas_recall_delta={int(k):float(v) for k, v in gas_delta.items()},
                mean_gas_f1_delta={int(k):float(v) for k, v in f1_delta.items()},
                other_four_f1_delta=float((other.f1-other.f1_svm).mean()),
                new_zero_pairs=int((paired.recall.eq(0) & (paired.recall_svm > 0)).sum()),
                official_model='Model A unchanged', future_batches_evaluated=[])


# 기존 파일·원본·고정 계획 검사
def verify():
    before = json.loads((OUT/'preservation_before.json').read_text(encoding='utf-8'))
    rows = [dict(kind='existing', path=n, expected=s, actual=sha(ROOT/n)) for n, s in before['files'].items()]
    raw_dir = Path(read_config()['data_dir'])
    rows.extend(dict(kind='raw', path=n, expected=s, actual=sha(raw_dir/n)) for n, s in before['raw'].items())
    audit = save('preservation_audit', rows)
    assert audit.expected.eq(audit.actual).all(), 'Existing file changed'
    plan = json.loads((OUT/'experiment_plan.json').read_text(encoding='utf-8'))
    lock = json.loads((OUT/'plan_lock.json').read_text(encoding='utf-8'))
    assert sha(OUT/'experiment_plan.json') == lock['plan_sha256']
    assert sha(OUT/'protocol.md') == lock['protocol_sha256']
    assert sha(OUT/'split_assignments.csv') == plan['split_sha256']
    assert sha(OUT/'svm_preflight.json') == plan['svm_preflight_sha256']
    return dict(all_preserved=True, plan_unchanged=True, raw_files=len(before['raw']),
                existing_models=sum(n.endswith('.joblib') for n in before['files']),
                existing_files=len(before['files']))


# 학습을 한 번씩 수행하고 저장 예측의 재현성 확인
def run():
    if (OUT/'started.json').exists():
        raise FileExistsError('Already started; no duplicate fitting')
    verify()
    write('started.json', dict(started_at=now()))
    logging.basicConfig(filename=OUT/'execution_log.txt', encoding='utf-8', level=logging.INFO)
    frame, _ = load_dataset(read_config())
    frame = frame[frame.batch <= 8].copy()
    assignments, _ = splits(frame)
    pd.testing.assert_frame_equal(assignments, pd.read_csv(OUT/'split_assignments.csv'))
    prechecked = json.loads((OUT/'svm_preflight.json').read_text(encoding='utf-8'))
    old_predictions = pd.read_csv(ROOT/'outputs/nonlinear_feature_transformation/predictions.csv')
    metrics, classes, predictions, confusion, registry, weights, audits, agreement = [], [], [], [], [], [], [], []
    svm_models = {}
    # 모든 SVM 호환성 검사를 HGB 학습 전에 재확인
    for entry in prechecked:
        fold = entry['fold']
        if entry['can_reuse']:
            assert sha(ROOT/entry['path']) == entry['sha256']
            svm = joblib.load(ROOT/entry['path'])
            audit_model(svm, frame[frame.batch <= FOLDS[fold][0]], FOLDS[fold][0])
            svm_models[fold] = svm
    with threadpool_limits(limits=1):
        for fold, (end, batch) in FOLDS.items():
            train, validation = frame[frame.batch <= end], frame[frame.batch == batch]
            pred = {}
            for name in ['SVM', 'HGB']:
                print(f'{fold} {name}: Train {len(train)} -> Batch{batch} {len(validation)}', flush=True)
                entry = next(r for r in prechecked if r['fold'] == fold)
                new_fit = name == 'HGB' or not entry['can_reuse']
                model = (svm_models[fold] if name == 'SVM' and not new_fit else
                         (build_pipeline('baseline') if name == 'SVM' else Pipeline([
                             ('imputer', SimpleImputer(strategy='median', keep_empty_features=True)),
                             ('classifier', HistGradientBoostingClassifier(**HGB_PARAMS))])))
                started, fit_seconds = now(), 0.
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter('always')
                    if new_fit:
                        # 외부 검증 자료·sample_weight 없이 Train만 전달
                        write(f'{fold}_{name}_fit_started.json', dict(started_at=started, train_n=len(train),
                              row_sha256=row_digest(train.row_id), input_sha256=digest(train[FEATURES])))
                        tick = time.perf_counter()
                        model.fit(train[FEATURES], train.gas)
                        fit_seconds = time.perf_counter()-tick
                    tick = time.perf_counter()
                    predicted = model.predict(validation[FEATURES])
                    predict_seconds = time.perf_counter()-tick
                if name == 'SVM' and not new_fit:
                    expected = old_predictions[(old_predictions.fold == fold) & (old_predictions.method == 'baseline')]
                    np.testing.assert_array_equal(predicted, expected.set_index('row_id').loc[validation.row_id, 'y_pred'])
                if name == 'HGB':
                    assert model['classifier'].get_params() == HGB_PARAMS
                    assert model['classifier'].n_iter_ == 100
                    assert not model['classifier'].do_early_stopping_
                    assert len(model['classifier'].validation_score_) == 0
                    model.training_input_sha256_ = digest(train[FEATURES])
                    model.training_row_ids_sha256_ = row_digest(train.row_id)
                    MODEL_DIR.mkdir(exist_ok=True)
                    path = MODEL_DIR/f'{fold}_HGB.joblib'
                    joblib.dump(model, path)
                    reloaded = joblib.load(path)
                else:
                    # SVM은 기존 파일을 덮어쓰거나 새 모델 폴더에 복사하지 않음
                    if new_fit:
                        fallback_dir = OUT/'svm_fallbacks'
                        fallback_dir.mkdir(exist_ok=True)
                        path = fallback_dir/f'{fold}_SVM.joblib'
                        joblib.dump(model, path)
                    else:
                        path = ROOT/entry['path']
                    reloaded = joblib.load(path)
                np.testing.assert_array_equal(predicted, reloaded.predict(validation[FEATURES]))
                np.testing.assert_array_equal(model['classifier'].classes_, list(GASES))
                np.testing.assert_array_equal(model['imputer'].feature_names_in_, FEATURES)
                np.testing.assert_allclose(model['imputer'].statistics_, train[FEATURES].median())
                assert model['imputer'].transform(train[FEATURES]).shape == (len(train), 128)
                effective = compute_sample_weight('balanced', train.gas)
                if name == 'HGB':
                    np.testing.assert_allclose(model['classifier']._finalize_sample_weight(None, train.gas.to_numpy()), effective)
                for g in GASES:
                    mask = train.gas.to_numpy() == g
                    weights.append(dict(fold=fold, model=name, gas_id=g, train_support=int(mask.sum()),
                                        class_weight=float(effective[mask][0]),
                                        sample_weight_sum=float(effective[mask].sum())))
                score, per_class, matrix = score_predictions(validation.gas, predicted)
                metrics.append(dict(fold=fold, batch=batch, model=name, fit_seconds=fit_seconds,
                                    predict_seconds=predict_seconds, **score))
                classes.extend(per_class.assign(fold=fold, batch=batch, model=name).to_dict('records'))
                confusion.extend(dict(fold=fold, batch=batch, model=name, true_gas=g,
                                      predicted_gas=h, n=int(matrix[g-1, h-1])) for g in GASES for h in GASES)
                predictions.extend(dict(fold=fold, batch=batch, model=name, row_id=r,
                                        y_true=int(y), y_pred=int(p)) for r, y, p in zip(validation.row_id, validation.gas, predicted))
                pred[name] = predicted
                audits.append(dict(fold=fold, model=name, train_n=len(train),
                                   train_row_sha256=row_digest(train.row_id), train_input_sha256=digest(train[FEATURES]),
                                   validation_row_sha256=row_digest(validation.row_id), feature_order_sha256=row_digest(FEATURES),
                                   class_order='1,2,3,4,5,6', train_only=True,
                                   external_validation_passed=False, sample_weight_passed=False,
                                   early_stopping=False if name == 'HGB' else None,
                                   n_iter=int(model['classifier'].n_iter_) if name == 'HGB' else None,
                                   actual_gamma=float(model['classifier']._gamma) if name == 'SVM' else None))
                registry.append(dict(fold=fold, model=name, path=str(path.relative_to(ROOT)), sha256=sha(path),
                                     new_fit=new_fit, saved_new_file=name == 'HGB', fit_started_at=started,
                                     fit_seconds=fit_seconds, parameters=model['classifier'].get_params(),
                                     warnings=[str(w.message) for w in caught]))
                logging.info('%s %s fit=%s predict=%s new_fit=%s', fold, name, fit_seconds, predict_seconds, new_fit)
            paired = error_agreement(validation.gas, pred['SVM'], pred['HGB'])
            paired['fold'], paired['batch'], paired['row_id'] = fold, batch, validation.row_id.to_numpy()
            agreement.extend(paired.to_dict('records'))
    for name, rows in [('fold_metrics', metrics), ('class_metrics', classes), ('predictions', predictions),
                       ('confusion', confusion), ('class_weights', weights), ('train_only_audit', audits),
                       ('error_agreement', agreement)]:
        save(name, rows)
    write('model_registry.json', registry)
    write('actual_settings.json', dict(models=registry, hgb_parameters=HGB_PARAMS,
          native_missing_supported=True, selected_missing_policy='Train-only median imputation',
          early_stopping=False, external_validation_arguments=[], ensemble_executed=False))
    metric_table, class_table = pd.DataFrame(metrics), pd.DataFrame(classes)
    conclusion = judge(metric_table, class_table)
    conclusion.update(frozen_at=now(), new_HGB_fits=3, reused_SVM=sum(not r['new_fit'] for r in registry if r['model'] == 'SVM'),
                      fallback_SVM_fits=sum(r['new_fit'] for r in registry if r['model'] == 'SVM'))
    write('conclusion_frozen.json', conclusion)
    directions = pd.DataFrame(confusion)
    save('error_directions', directions[directions.true_gas != directions.predicted_gas])
    from .hgb_algorithm_comparison_report import render
    render()
    write('final_verification.json', {**verify(), 'completed_at':now()})
    print(json.dumps(conclusion, ensure_ascii=False, default=lambda x:x.item() if isinstance(x, np.generic) else str(x)), flush=True)


# 새 조건 추가 없이 계획·실행·최종 보고서 갱신 분리
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['freeze', 'run', 'report'])
    action = parser.parse_args().action
    if action == 'freeze':
        freeze()
    elif action == 'run':
        run()
    else:
        from .hgb_algorithm_comparison_report import render
        render()
        write('final_verification.json', {**verify(), 'checked_at':now()})


if __name__ == '__main__':
    main()
