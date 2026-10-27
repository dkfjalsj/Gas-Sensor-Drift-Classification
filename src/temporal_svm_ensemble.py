# 시기별 SVM 오류 상호 보완성 진단 및 조건부 결합
# 사전 계획 고정·동일 표본 평가·기존 파일 보존 검사

import argparse
import hashlib
import importlib.metadata
import json
import logging
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from threadpoolctl import threadpool_limits

from .data import ROOT, FEATURES, GASES, load_dataset, read_config
from .temporal_expansion import now, sha, write_json
from .temporal_representativeness_control import budgets, sample_rows
from .nonlinear_feature_transformation import score_predictions, row_digest, digest

OUT = ROOT / 'outputs/temporal_svm_ensemble'
MODEL_DIR = ROOT / 'models/temporal_svm_ensemble'
REPORTS = ['temporal_svm_ensemble_report.html', 'temporal_svm_ensemble_summary.md',
           'temporal_svm_ensemble_limitations.md']
FOLDS = {'A': (3, 6), 'B': (6, 7), 'C': (7, 8)}
EXPERTS = ['full', 'recent', 'spread']
CAUTION = ('새 독립 Test 없음. 과거 Fold는 반복 사용된 개발 검증 자료이며 학습 구간이 겹침. '
           'Batch 9~10 신규 평가 없음. 공식 Model A 유지.')
ORACLE_NOTE = ('정답을 알고 전문가를 선택한 가상 상한이며 실제 배포 가능한 모델이 아님. '
               'Accuracy·가스 Recall은 선택형 상한. Macro F1은 공동 오답에서 full 예측을 '
               '유지한 고정 Oracle의 점수이며 모든 오답 배치를 최적화한 수학적 상한은 아님.')


def save(name, rows):
    table = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    table.to_csv(OUT/f'{name}.csv', index=False, encoding='utf-8')
    return table


# 기존 정식 산출물·모델·코드의 지문 수집
def snapshot():
    files = {}
    for folder in ['src', 'tests', 'reports', 'models', 'outputs']:
        for path in (ROOT/folder).rglob('*'):
            if (not path.is_file() or '__pycache__' in path.parts or OUT in path.parents or
                    MODEL_DIR in path.parents or
                    (path.parent == ROOT/'reports' and path.name in REPORTS)):
                continue
            files[str(path.relative_to(ROOT))] = sha(path)
    for name in ['README.md', 'config.json', 'training_config.json', '.gitignore',
                 'requirements.txt', 'requirements-lock.txt']:
        files[name] = sha(ROOT/name)
    return files


# 예측 결과와 무관하게 고정 시기별 학습 행 선정
def expert_rows(frame, end, expert):
    if expert == 'full':
        return frame.index[frame.batch <= end].to_numpy()
    return sample_rows(frame, end, expert, budgets(frame)['mid'], 42)


# 이전 단계의 정확한 모델·행 기록 조회
def source_record(fold, expert):
    if expert == 'full':
        records = pd.read_csv(ROOT/'outputs/nonlinear_feature_transformation/model_registry.csv')
        row = records[(records.fold == fold) & (records.method == 'baseline')].iloc[0]
    else:
        records = pd.read_csv(ROOT/'outputs/temporal_representativeness_control/fit_records.csv')
        row = records[(records.fold == fold) & (records.setting == f'{expert}_mid') &
                      (records.seed == 42)].iloc[0]
    return dict(path=row.path, sha256=row.sha256)


# 저장 파이프라인의 Train 통계·설정·지원 벡터 검증
def audit_model(model, train, end):
    assert train.batch.max() <= end and len(train) == len(set(train.row_id))
    assert list(model.named_steps) == ['imputer', 'scaler', 'classifier']
    imputer, scaler, classifier = (model[n] for n in ['imputer', 'scaler', 'classifier'])
    assert imputer.strategy == 'median' and isinstance(scaler, StandardScaler)
    np.testing.assert_array_equal(imputer.feature_names_in_, FEATURES)
    np.testing.assert_allclose(imputer.statistics_, train[FEATURES].median())
    filled = imputer.transform(train[FEATURES])
    assert filled.shape == (len(train), 128)
    assert scaler.n_samples_seen_ == len(train)
    np.testing.assert_allclose(scaler.mean_, filled.mean(axis=0), atol=1e-10)
    np.testing.assert_allclose(scaler.var_, filled.var(axis=0), rtol=1e-9)
    assert isinstance(classifier, SVC)
    for key, value in dict(kernel='rbf', C=1., gamma='scale', class_weight='balanced',
                           random_state=42, decision_function_shape='ovr',
                           break_ties=False).items():
        assert classifier.get_params()[key] == value
    # 1.9의 기본 문자열도 확률 계산 비활성 상태임
    assert classifier.probability in [False, 'deprecated']
    assert not hasattr(classifier, 'predict_proba')
    np.testing.assert_array_equal(classifier.classes_, list(GASES))
    np.testing.assert_allclose(classifier.class_weight_,
                               len(train)/(6*train.gas.value_counts().sort_index()))
    transformed = scaler.transform(filled)
    np.testing.assert_allclose(classifier.support_vectors_, transformed[classifier.support_],
                               rtol=1e-8, atol=1e-9)
    return dict(train_n=len(train), train_max_batch=int(train.batch.max()),
                row_sha256=row_digest(train.row_id), input_sha256=digest(train[FEATURES]),
                scaler_n=int(scaler.n_samples_seen_), actual_gamma=float(classifier._gamma),
                train_only=True, feature_count=128, class_order='1,2,3,4,5,6')


# 사전 계획·전문가 구성·실행 게이트 고정
def freeze():
    if OUT.exists() or MODEL_DIR.exists() or any((ROOT/'reports'/n).exists() for n in REPORTS):
        raise FileExistsError('Stage15 output already exists')
    frame, raw = load_dataset(read_config())
    frame = frame[frame.batch <= 8].copy()
    before = snapshot()
    planned, experts, supports = [], [], []
    hashes = pd.util.hash_pandas_object(frame[FEATURES], index=False)
    for fold, (end, batch) in FOLDS.items():
        validation = frame[frame.batch == batch]
        seen = set()
        for expert in EXPERTS:
            train = frame.loc[expert_rows(frame, end, expert)]
            signature = row_digest(train.row_id)
            included = signature not in seen
            seen.add(signature)
            assert set(train.gas) == set(GASES)
            assert train.batch.max() < batch
            assert set(train.row_id).isdisjoint(validation.row_id)
            assert set(hashes.loc[train.index]).isdisjoint(hashes.loc[validation.index])
            source = source_record(fold, expert)
            experts.append(dict(fold=fold, expert=expert, included=included,
                                exclusion='' if included else 'identical ordered Train rows',
                                train_n=len(train), train_min=int(train.batch.min()),
                                train_max=int(train.batch.max()), validation_batch=batch,
                                row_sha256=signature, input_sha256=digest(train[FEATURES]), **source))
            for part, sub in [('train', train), ('validation', validation)]:
                planned.extend(dict(fold=fold, expert=expert, partition=part, row_id=r.row_id,
                                    batch=int(r.batch), gas_id=int(r.gas)) for r in sub.itertuples())
                supports.extend(dict(fold=fold, expert=expert, partition=part, batch=int(b),
                                     gas_id=g, n=int(((sub.batch == b) & (sub.gas == g)).sum()))
                                for b in sorted(sub.batch.unique()) for g in GASES)
    OUT.mkdir()
    save('planned_rows', planned)
    save('expert_plan', experts)
    save('class_batch_support', supports)
    plan = dict(
        stage=15, frozen_at=now(), folds=FOLDS, experts=EXPERTS, seed=42,
        selection='full: all Train; recent/spread: Stage12 mid843, fixed default seed42. '
                  'Recent descending gas-Batch fill; spread capacity-capped round-robin. '
                  'No ranking of models/seeds by past or current scores.',
        confounding='recent versus spread has matched 843 rows and gas counts. '
                    'full versus subset also changes sample amount/class proportions/balanced penalties '
                    'and fitted preprocessing; cannot attribute solely to temporal composition.',
        exclusion='Only identical ordered Train hashes removed before validation; otherwise no '
                  'removal based on prediction or correctness. Degenerate identical predictions reported.',
        baseline='full expert in same Fold; no ModelB trained through7 in Validation7',
        candidates=['hard_equal', 'rank_equal'],
        hard='Equal one vote per included expert. Tie: full predicted class if tied, else lowest gas id.',
        rank='Validate SVC OVR n×6 finite scores/classes1..6. Per expert descending stable '
             'rank -> points5..0; sum equally. Tie: full expert class rank, then lowest gas id. '
             'Never average raw scores/probabilities. Rank candidate skipped if any mapping/score audit fails.',
        oracle='If any expert predicts true label, return truth; otherwise full prediction. '
               'Accuracy/Recall selection upper bound, MacroF1 fixed-fallback diagnostic not globally '
               'optimized F1 bound. Never usable as deployed prediction or combination tuning.',
        gate=dict(nonidentical_predictions='any Fold disagreement count>0',
                  partial_correct='any Fold count(0<correct_experts<expert_count)>0',
                  macro='mean_Fold(oracle MacroF1)-max_expert(mean_Fold MacroF1)>=.01',
                  focus='For Tol or Ac: mean_Fold oracleRecall minus maximum single-expert '
                        'mean_Fold Recall>=.02 AND sum_Fold(any_correct & full_wrong & true_gas)>=10',
                  provenance='every expert past-only and imputer/scaler/support-vector audit passes',
                  threshold_inclusive=True, tolerance=1e-12, all_required=True),
        protection=dict(macro_gain_min=.005, per_gas_mean_recall_loss_max=.05,
                        other_four_mean_f1_loss_max=.02, zero_pairs_increase_max=0,
                        no_new_zero=True, inclusive=True, tolerance=1e-12),
        aggregation='equal Fold means; per-gas means only positive-support Folds; other-four F1 '
                    'equal gas/Fold means for1,2,3,5; missing truth metrics NA not zero; '
                    'pooled metrics separately labelled; Fold SD descriptive only',
        budget=dict(max_expert_evaluations=9, max_new_svc_fits=9, max_ensemble_evaluations=6,
                    oracle_diagnostic_evaluations=3, no_ensemble_classifier_fit=True),
        reuse='Match source sha, reconstructed Stage12/14 ordered rows, feature values/raw sha, '
              'median/scaler/class weights/support vectors; reloaded predictions match old records. '
              'If provenance audit fails, train same predeclared expert once on planned rows, log reason.',
        stop='Gate failure => no ensemble; no added expert/rule/weight/seed. Leakage, raw-hash '
             'or preservation failure => abort. Rank format failure => skip rank only.',
        conclusion='Gate fail C. Otherwise A iff ensemble all protection guards; B iff any ensemble '
                   'positive mean MacroF1 or class P/R/F1 change but guards fail; C otherwise. '
                   'Compare best single expert separately; no automatic official model replacement.',
        tie='If multiple all-guard candidates, higher mean MacroF1, within1e-12 fewer zeros then '
            'higher minimum recall then hard_equal. No validation-optimized weights.',
        independent_test=False, future_batches_evaluated=[], warning=CAUTION,
        existing_model_choice_bias='Stage12 models have already been examined in prior research. '
                                   'Default seed/rule freezing does not erase historical selection bias.',
        plan_rows_sha256=sha(OUT/'planned_rows.csv'), expert_plan_sha256=sha(OUT/'expert_plan.csv'),
        versions={k: importlib.metadata.version(k) for k in ['numpy', 'pandas', 'scikit-learn', 'joblib']})
    write_json(OUT/'experiment_plan.json', plan)
    write_json(OUT/'preservation_before.json', dict(files=before,
               raw={r.file:r.sha256 for r in raw.itertuples()}))
    (OUT/'protocol.md').write_text('# 15단계 사전 고정 계획\n\n'+CAUTION+'\n\n'+ORACLE_NOTE+
                                  '\n\n```json\n'+json.dumps(plan, ensure_ascii=False, indent=2)+'\n```', encoding='utf-8')
    write_json(OUT/'plan_lock.json', dict(plan_sha256=sha(OUT/'experiment_plan.json'),
                                        protocol_sha256=sha(OUT/'protocol.md')))
    print('Stage15 protocol frozen; no predictions yet', flush=True)


# 동일 표본의 정답·오답 일치와 가상 Oracle 계산
def complement(y, predictions):
    y, predictions = np.asarray(y), np.asarray(predictions)
    if predictions.ndim != 2 or predictions.shape[0] != len(y):
        raise ValueError('n rows by experts required')
    if not np.isin(predictions, list(GASES)).all():
        raise ValueError('Invalid gas mapping')
    correct = predictions == y[:, None]
    count = correct.sum(axis=1)
    disagreement = np.any(predictions != predictions[:, [0]], axis=1)
    oracle = np.where(count > 0, y, predictions[:, 0])
    return pd.DataFrame(dict(y_true=y, correct_experts=count,
                             all_correct=count == predictions.shape[1],
                             some_correct=(count > 0) & (count < predictions.shape[1]),
                             all_wrong=count == 0, disagreement=disagreement,
                             identical_wrong=(~disagreement) & (count == 0),
                             oracle_pred=oracle, full_pred=predictions[:, 0],
                             oracle_rescue=(count > 0) & ~correct[:, 0])), correct


# 다수결 또는 모델 내부 클래스 순위만 결합
def combine(predictions, scores=None, mode='hard_equal'):
    predictions = np.asarray(predictions)
    if predictions.ndim != 2 or predictions.shape[1] < 1 or not np.isin(predictions, list(GASES)).all():
        raise ValueError('Invalid expert predictions')
    if mode == 'hard_equal':
        totals = np.column_stack([(predictions == g).sum(axis=1) for g in GASES])
        primary = totals == totals.max(axis=1, keepdims=True)
        secondary = np.zeros_like(totals)
        secondary[np.arange(len(predictions)), predictions[:, 0]-1] = 1
    elif mode == 'rank_equal':
        scores = np.asarray(scores)
        if scores.shape != (predictions.shape[1], len(predictions), 6) or not np.isfinite(scores).all():
            raise ValueError('Finite experts×rows×6 OVR scores required')
        order = np.argsort(-scores, axis=2, kind='stable')
        points = np.empty_like(scores, dtype=int)
        np.put_along_axis(points, order, np.broadcast_to(np.arange(5, -1, -1), scores.shape), axis=2)
        totals = points.sum(axis=0)
        primary = totals == totals.max(axis=1, keepdims=True)
        secondary = points[0]
    else:
        raise ValueError('Unplanned ensemble mode')
    return np.argmax(np.where(primary, secondary, -1), axis=1) + 1


# 전체 Fold 기준 진단 게이트 재현
def gate_decision(metrics, classes, samples, provenance=True):
    experts = metrics[metrics.role == 'expert']
    best = experts.groupby('model').macro_f1.mean().max()
    oracle = metrics[metrics.model == 'oracle'].macro_f1.mean()
    means = classes.groupby(['model', 'gas_id']).recall.mean()
    focus = []
    for gas in [6, 4]:
        best_recall = max(means.loc[(expert, gas)] for expert in experts.model.unique())
        gain = means.loc[('oracle', gas)]-best_recall
        rescued = int(samples[samples.y_true == gas].oracle_rescue.sum())
        focus.append(dict(gas_id=gas, recall_gain=float(gain), rescued=rescued,
                          passes=bool(gain >= .02-1e-12 and rescued >= 10)))
    checks = dict(nonidentical=bool(samples.disagreement.any()),
                  partial_correct=bool(samples.some_correct.any()),
                  macro_gain=bool(oracle-best >= .01-1e-12),
                  focus_room=any(r['passes'] for r in focus), provenance=bool(provenance))
    return dict(checks=checks, passed=all(checks.values()), oracle_mean_macro_f1=float(oracle),
                best_expert_mean_macro_f1=float(best), oracle_macro_gain=float(oracle-best),
                focus=focus, decided_at=now(), oracle_warning=ORACLE_NOTE)


# 기준 대비 보호 조건 및 단독 최고 대비 추가 가치 계산
def summarize(metrics, classes):
    baseline = classes[classes.model == 'full'].set_index(['fold', 'gas_id'])
    best_single = metrics[metrics.role == 'expert'].groupby('model').macro_f1.mean().max()
    rows = []
    for name, sub in metrics.groupby('model', sort=False):
        gas = classes[classes.model == name].set_index(['fold', 'gas_id'])
        paired = gas[['precision', 'recall', 'f1']].join(
            baseline[['precision', 'recall', 'f1']], rsuffix='_base')
        mean_delta = (paired.recall-paired.recall_base).groupby('gas_id').mean()
        other = paired[paired.index.get_level_values('gas_id').isin([1, 2, 3, 5])]
        delta = sub.macro_f1.mean()-metrics[metrics.model == 'full'].macro_f1.mean()
        zero = int(gas.recall.eq(0).sum())
        new_zero = int((paired.recall.eq(0) & (paired.recall_base > 0)).sum())
        guards = dict(macro_guard=bool(delta >= .005-1e-12),
                      gas_recall_guard=bool((mean_delta >= -.05-1e-12).all()),
                      other_guard=bool((other.f1-other.f1_base).mean() >= -.02-1e-12),
                      zero_guard=zero <= int(baseline.recall.eq(0).sum()), new_zero_guard=new_zero == 0)
        positive = delta > 1e-12 or bool(((paired[['precision', 'recall', 'f1']].to_numpy()-
                    paired[['precision_base', 'recall_base', 'f1_base']].to_numpy()) > 1e-12).any())
        role = sub.role.iloc[0]
        status = ('A' if all(guards.values()) else ('B' if positive else 'C')) if role == 'ensemble' else role
        rows.append(dict(model=name, role=role, mean_macro_f1=sub.macro_f1.mean(),
                         mean_accuracy=sub.accuracy.mean(), mean_weighted_f1=sub.weighted_f1.mean(),
                         fold_sd=sub.macro_f1.std(ddof=0), macro_delta=delta,
                         above_best_single=sub.macro_f1.mean()-best_single,
                         mean_toluene_recall=gas.xs(6, level='gas_id').recall.mean(),
                         mean_acetaldehyde_recall=gas.xs(4, level='gas_id').recall.mean(),
                         min_recall=gas.recall.min(), zero_pairs=zero, new_zero_pairs=new_zero,
                         other_four_f1=other.f1.mean(), worst_fold_delta=float((sub.set_index('fold').macro_f1-
                         metrics[metrics.model == 'full'].set_index('fold').macro_f1).min()),
                         **guards, balanced_success=role == 'ensemble' and all(guards.values()), conclusion=status))
    return pd.DataFrame(rows)


# 원본·기존 파일·사전 규칙 보존 검사
def verify():
    before = json.loads((OUT/'preservation_before.json').read_text(encoding='utf-8'))
    allowed = {'src\\temporal_svm_ensemble.py', 'tests\\test_temporal_svm_ensemble.py'}
    expected_files = dict(before['files'])
    repaired_names = set()
    for repair_path in sorted(OUT.glob('technical_repair*.json')):
        repairs = json.loads(repair_path.read_text(encoding='utf-8'))['files']
        assert set(repairs).issubset(allowed), 'Only new Stage15 implementation repairs allowed'
        for name, change in repairs.items():
            assert change['before'] == expected_files[name]
            expected_files[name] = change['after']
            repaired_names.add(name)
    rows = []
    for n, s in before['files'].items():
        expected = expected_files[n]
        rows.append(dict(kind='stage15_technical_repair' if n in repaired_names else 'existing',
                         path=n, frozen_original=s, expected=expected, actual=sha(ROOT/n)))
    raw_dir = Path(read_config()['data_dir'])
    rows.extend(dict(kind='raw', path=n, frozen_original=s, expected=s, actual=sha(raw_dir/n)) for n, s in before['raw'].items())
    checks = save('preservation_audit', rows)
    assert checks.expected.eq(checks.actual).all(), 'Preservation failure'
    lock = json.loads((OUT/'plan_lock.json').read_text(encoding='utf-8'))
    assert sha(OUT/'experiment_plan.json') == lock['plan_sha256']
    assert sha(OUT/'protocol.md') == lock['protocol_sha256']
    plan = json.loads((OUT/'experiment_plan.json').read_text(encoding='utf-8'))
    assert sha(OUT/'planned_rows.csv') == plan['plan_rows_sha256']
    assert sha(OUT/'expert_plan.csv') == plan['expert_plan_sha256']
    return dict(raw_files=len(before['raw']), existing_files=len(before['files']),
                existing_models=sum(n.endswith('.joblib') for n in before['files']),
                all_preserved=True, frozen_plan_unchanged=True)


# 저장 전문가 진단 후 게이트 통과 시에만 결합 평가
def run(resume=False):
    if (OUT/'started.json').exists() and not resume:
        raise FileExistsError('Run already started; no overwrite')
    if resume:
        assert (OUT/'technical_repair.json').exists()
        assert not (OUT/'diagnostic_gate.json').exists() and not (OUT/'predictions.csv').exists()
        assert not (OUT/'resumed.json').exists()
    verify()
    write_json(OUT/('resumed.json' if resume else 'started.json'), dict(started_at=now()))
    logging.basicConfig(filename=OUT/'execution_log.txt', level=logging.INFO, encoding='utf-8')
    frame, raw = load_dataset(read_config())
    frame = frame[frame.batch <= 8].copy()
    old_manifest = json.loads((ROOT/'outputs/temporal_representativeness_control/run_manifest.json').read_text(encoding='utf-8'))
    assert {r.file:r.sha256 for r in raw.itertuples()} == old_manifest['raw_hashes']
    planned = pd.read_csv(OUT/'expert_plan.csv').fillna('')
    old_assignments = pd.read_csv(ROOT/'outputs/temporal_representativeness_control/sample_assignments.csv')
    old_predictions = pd.read_csv(ROOT/'outputs/temporal_representativeness_control/historical_predictions.csv')
    metrics, classes, matrices, predictions, audit, per_sample, pair_rows = [], [], [], [], [], [], []
    caches = {}

    def record(name, fold, role, validation, predicted, seconds=0.):
        score, gas, cm = score_predictions(validation.gas, predicted)
        metrics.append(dict(model=name, fold=fold, batch=FOLDS[fold][1], role=role,
                            predict_seconds=seconds, **score))
        classes.extend(gas.assign(model=name, fold=fold, batch=FOLDS[fold][1], role=role).to_dict('records'))
        matrices.extend(dict(model=name, fold=fold, true_gas=g, predicted_gas=h, n=int(cm[g-1, h-1]))
                        for g in GASES for h in GASES)
        predictions.extend(dict(model=name, fold=fold, row_id=r, batch=FOLDS[fold][1],
                                y_true=int(y), y_pred=int(p)) for r, y, p in
                           zip(validation.row_id, validation.gas, predicted))

    with threadpool_limits(limits=1):
        for fold, (end, batch) in FOLDS.items():
            validation = frame[frame.batch == batch]
            pred_list, scores, names = [], [], []
            for expert in EXPERTS:
                item = planned[(planned.fold == fold) & (planned.expert == expert)].iloc[0]
                if not item.included:
                    continue
                train = frame.loc[expert_rows(frame, end, expert)]
                assert item.row_sha256 == row_digest(train.row_id)
                assert item.input_sha256 == digest(train[FEATURES])
                if expert != 'full':
                    previous = old_assignments[(old_assignments.fold == fold) &
                        (old_assignments.setting == f'{expert}_mid') & (old_assignments.seed == 42)]
                    assert previous.row_id.tolist() == train.row_id.tolist()
                fit_seconds, new_fit, reuse_error = 0., False, ''
                try:
                    assert sha(ROOT/item.path) == item.sha256
                    model = joblib.load(ROOT/item.path)
                    check = audit_model(model, train, end)
                except (AssertionError, FileNotFoundError, ValueError) as exc:
                    # 같은 사전 전문가만 한 번 재학습하며 후보 추가 없음
                    reuse_error = repr(exc)
                    model = Pipeline([('imputer', SimpleImputer(strategy='median', keep_empty_features=True)),
                                      ('scaler', StandardScaler()),
                                      ('classifier', SVC(C=1., gamma='scale', class_weight='balanced', probability=False,
                                                         random_state=42, cache_size=512))])
                    tick = time.perf_counter()
                    model.fit(train[FEATURES], train.gas)
                    fit_seconds = time.perf_counter()-tick
                    check = audit_model(model, train, end)
                    MODEL_DIR.mkdir(exist_ok=True)
                    path = MODEL_DIR/f'{fold}_{expert}.joblib'
                    joblib.dump(model, path)
                    new_fit = True
                tick = time.perf_counter()
                predicted = model.predict(validation[FEATURES])
                seconds = time.perf_counter()-tick
                if expert == 'full':
                    old = pd.read_csv(ROOT/'outputs/nonlinear_feature_transformation/predictions.csv')
                    old = old[(old.fold == fold) & (old.method == 'baseline')]
                else:
                    old = old_predictions[(old_predictions.fold == fold) &
                        (old_predictions.setting == f'{expert}_mid') & (old_predictions.seed == 42)]
                if not new_fit:
                    np.testing.assert_array_equal(predicted, old.set_index('row_id').loc[validation.row_id, 'y_pred'])
                path = path if new_fit else ROOT/item.path
                reloaded = joblib.load(path)
                np.testing.assert_array_equal(predicted, reloaded.predict(validation[FEATURES]))
                raw_scores = model.decision_function(validation[FEATURES])
                valid_rank = raw_scores.shape == (len(validation), 6) and np.isfinite(raw_scores).all()
                audit.append(dict(fold=fold, expert=expert, **check, new_fit=new_fit,
                                  fit_seconds=fit_seconds, reuse_error=reuse_error,
                                  model_path=str(path.relative_to(ROOT)), sha256=sha(path),
                                  validation_rows_sha256=row_digest(validation.row_id), rank_valid=bool(valid_rank),
                                  rank_argmax_predict_disagreement=int((raw_scores.argmax(axis=1)+1 != predicted).sum()),
                                  predictions_reproduced=True))
                record(expert, fold, 'expert', validation, predicted, seconds)
                names.append(expert)
                pred_list.append(predicted)
                scores.append(raw_scores)
                print(f'{fold} {expert}: Train={len(train)}, reused={not new_fit}', flush=True)
                logging.info('%s %s train=%s new_fit=%s', fold, expert, len(train), new_fit)
            stacked = np.column_stack(pred_list)
            sample, correct = complement(validation.gas, stacked)
            sample['fold'], sample['batch'], sample['row_id'] = fold, batch, validation.row_id.to_numpy()
            for i, name in enumerate(names):
                sample[f'{name}_pred'] = stacked[:, i]
                sample[f'{name}_correct'] = correct[:, i]
                sample[f'{name}_only_correct'] = correct[:, i] & (correct.sum(axis=1) == 1)
            per_sample.extend(sample.to_dict('records'))
            for i, left in enumerate(names):
                for j in range(i+1, len(names)):
                    right = names[j]
                    for gas_id in [0, *GASES]:
                        mask = np.ones(len(validation), dtype=bool) if gas_id == 0 else validation.gas.to_numpy() == gas_id
                        pair_rows.append(dict(fold=fold, left=left, right=right, gas_id=gas_id,
                            n=int(mask.sum()), agreement=int(((stacked[:, i] == stacked[:, j]) & mask).sum()),
                            both_correct=int((correct[:, i] & correct[:, j] & mask).sum()),
                            left_only=int((correct[:, i] & ~correct[:, j] & mask).sum()),
                            right_only=int((~correct[:, i] & correct[:, j] & mask).sum()),
                            both_wrong=int((~correct[:, i] & ~correct[:, j] & mask).sum())))
            record('oracle', fold, 'oracle', validation, sample.oracle_pred)
            caches[fold] = (validation, stacked, np.stack(scores))
        metric_table, class_table = pd.DataFrame(metrics), pd.DataFrame(classes)
        samples = save('sample_complementarity', per_sample)
        save('pairwise_complementarity', pair_rows)
        save('expert_audit', audit)
        gate = gate_decision(metric_table, class_table, samples, all(a['train_only'] for a in audit))
        write_json(OUT/'diagnostic_gate.json', gate)
        # 게이트 기록 이후에만 고정된 두 결합 후보 실행
        statuses = []
        for mode in ['hard_equal', 'rank_equal']:
            execute = gate['passed'] and (mode != 'rank_equal' or all(a['rank_valid'] for a in audit))
            statuses.append(dict(candidate=mode, executed=execute,
                                 reason='gate passed and input valid' if execute else
                                 ('diagnostic gate failed' if not gate['passed'] else 'invalid rank inputs')))
            if execute:
                for fold, (validation, stacked, score) in caches.items():
                    tick = time.perf_counter()
                    combined = combine(stacked, score, mode)
                    record(mode, fold, 'ensemble', validation, combined, time.perf_counter()-tick)
        save('ensemble_execution', statuses)
    metric_table = save('fold_metrics', metrics)
    class_table = save('class_metrics', classes)
    save('confusion', matrices)
    prediction_table = save('predictions', predictions)
    save('ensemble_metrics', metric_table[metric_table.role == 'ensemble'])
    summary = save('summary', summarize(metric_table, class_table))
    pooled = []
    for model, sub in prediction_table.groupby('model'):
        score, _, _ = score_predictions(sub.y_true, sub.y_pred)
        pooled.append(dict(model=model, scope='pooled repeated-development Folds', **score))
    save('pooled_metrics', pooled)
    category = 'C' if not gate['passed'] else ('A' if summary.balanced_success.any() else
                ('B' if ((summary.role == 'ensemble') & summary.conclusion.eq('B')).any() else 'C'))
    aborted_fits = (json.loads((OUT/'technical_repair.json').read_text(encoding='utf-8'))
                    .get('aborted_classifier_fits', 0)) if (OUT/'technical_repair.json').exists() else 0
    write_json(OUT/'conclusion_frozen.json', dict(conclusion=category, frozen_at=now(),
               gate_passed=gate['passed'], new_svc_fits=sum(a['new_fit'] for a in audit)+aborted_fits,
               new_expert_fits=sum(a['new_fit'] for a in audit), aborted_technical_fits=aborted_fits,
               reused_models=sum(not a['new_fit'] for a in audit),
               expert_evaluations=len(audit), ensemble_evaluations=sum(s['executed'] for s in statuses)*3,
               future_batches_evaluated=[], official_model='Model A unchanged'))
    finalize()
    print(json.dumps(gate, ensure_ascii=False, indent=2), flush=True)
    print(summary.to_string(index=False), flush=True)


# 계산 완료 표에서 JSON·보고서만 재생성
def finalize():
    assert (OUT/'conclusion_frozen.json').exists() and (OUT/'diagnostic_gate.json').exists()
    # CSV를 거쳐 NumPy 논릿값을 표준 JSON 자료형으로 변환
    audit = json.loads(pd.read_csv(OUT/'expert_audit.csv').fillna('').to_json(orient='records'))
    write_json(OUT/'actual_settings.json', dict(audit=audit, classes=GASES, feature_order=FEATURES,
               model_hyperparameters=dict(kernel='rbf', C=1., gamma='scale', class_weight='balanced',
                                          decision_function_shape='ovr', probability=False),
               method='No raw-score averaging, calibration, weight optimization or future evaluation'))
    from .temporal_svm_ensemble_report import render
    render()
    write_json(OUT/'final_verification.json', {**verify(), 'completed_at':now()})


# 실행 전 고정과 진단·결합 실행 분리
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['freeze', 'run', 'resume', 'report', 'finalize'])
    action = parser.parse_args().action
    if action == 'freeze':
        freeze()
    elif action == 'run':
        run()
    elif action == 'resume':
        run(resume=True)
    elif action == 'finalize':
        finalize()
    else:
        from .temporal_svm_ensemble_report import render
        render()
        write_json(OUT/'final_verification.json', {**verify(), 'checked_at':now()})


if __name__ == '__main__':
    main()
