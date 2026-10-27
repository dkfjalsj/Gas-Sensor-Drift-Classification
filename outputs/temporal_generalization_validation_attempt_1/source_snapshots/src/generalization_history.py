# 1–9단계 저장 예측·지표와 모델 파일의 재현 여부 검사
# 기존 모델 재사용 및 원본 기록 변경 없는 감사

import json

import joblib
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from .data import ROOT, FEATURES
from .temporal_expansion import measured_scores, sha


# 같은 모델·표본의 중복 예측을 줄이는 읽기 전용 감사
def audit_history(frame, out):
    indexed = frame.set_index('row_id')
    loaded, cached, checks, metric_checks = {}, {}, [], []
    root = ROOT / 'outputs'
    legacy = json.loads((root / 'model_comparison/fit_records.json').read_text(encoding='utf-8'))
    legacy_map = {(r['experiment'], r['model']): (ROOT / r['model_file'], r['sha256']) for r in legacy}

    def replay(folder, filename, keys, mapping):
        source = root / folder / filename
        data = pd.read_csv(source)
        count = 0
        for key, group in data.groupby(keys, sort=False):
            key = key if isinstance(key, tuple) else (key,)
            path, expected = mapping(key)
            if sha(path) != expected:
                raise ValueError(f'Historical model hash mismatch: {path}')
            path_key = str(path)
            if path_key not in loaded:
                loaded[path_key] = joblib.load(path)
                cached[path_key] = {}
            memo = cached[path_key]
            missing = [row for row in group.row_id.unique() if row not in memo]
            if missing:
                with threadpool_limits(limits=2):
                    pred = loaded[path_key].predict(indexed.loc[missing, FEATURES])
                memo.update(zip(missing, map(int, pred)))
            actual = group.row_id.map(memo).to_numpy()
            np.testing.assert_array_equal(actual, group.y_pred)
            np.testing.assert_array_equal(group.y_true, indexed.loc[group.row_id, 'gas'])
            np.testing.assert_array_equal(group.batch, indexed.loc[group.row_id, 'batch'])
            count += len(group)
        checks.append(dict(source=str(source.relative_to(ROOT)), rows=count, groups=data.groupby(keys).ngroups,
                           predictions_exact=True, labels_exact=True, model_hashes_match=True))
        print('Historical replay:', folder, filename, count, flush=True)
        return data

    def compare_metrics(folder, filename, data, keys, kind='standard'):
        old = pd.read_csv(root / folder / filename)
        for _, row in old.iterrows():
            sub = data
            for key in keys:
                if key == 'fold' and str(row[key]) in ['pooled', '9', '10']:
                    continue
                sub = sub[sub[key].astype(str) == str(row[key])]
            if 'scope' in row.index:
                if row.scope == 'batch':
                    sub = sub[sub.batch == row.batch]
                elif row.scope == 'common_6_10':
                    sub = sub[sub.batch.between(6, 10)]
            elif 'fold' in row.index and str(row.fold) in ['9', '10']:
                sub = sub[sub.batch == int(row.fold)]
            if sub.empty:
                raise ValueError(f'No predictions for historical metric: {folder} {row.to_dict()}')
            values, classes, _ = measured_scores(sub.y_true, sub.y_pred)
            tol = next(c for c in classes if c['gas_id'] == 6)
            values.update(total_n=len(sub), toluene_n=tol['support'],
                          correct_toluene=int(((sub.y_true == 6) & (sub.y_pred == 6)).sum()),
                          toluene_precision=tol['precision'], predicted_toluene_n=tol['predicted_count'],
                          other_five_macro_f1=float(np.mean([c['f1'] for c in classes
                                                            if c['gas_id'] != 6 and c['support'] > 0])))
            n_checked, maximum = 0, 0.0
            for name, actual in values.items():
                if name not in row.index or not isinstance(actual, (int, float, np.number)) or pd.isna(row[name]):
                    continue
                delta = abs(float(actual) - float(row[name]))
                if delta > 1e-12:
                    raise AssertionError(f'Historical metric mismatch: {folder}/{filename} {name} {delta}')
                n_checked += 1
                maximum = max(maximum, delta)
            metric_checks.append(dict(source=f'outputs/{folder}/{filename}',
                                      group=str({k: str(row[k]) for k in keys}),
                                      scope=str(row.get('scope', row.get('fold', 'pooled'))),
                                      scalars_checked=n_checked, max_absolute_error=maximum, match=True))

    # 원래9개 모델의 전체 Train·Validation·Test 예측부터 확인
    data4 = replay('toluene_analysis', 'predictions.csv', ['experiment', 'model'], lambda key: legacy_map[key])
    compare_metrics('toluene_analysis', 'toluene_metrics.csv', data4, ['experiment', 'model', 'partition'])
    for folder in ['model_comparison', 'model_diagnostics']:
        data = replay(folder, 'predictions.csv', ['experiment', 'model'], lambda key: legacy_map[key])
        compare_metrics(folder, 'metrics.csv', data, ['experiment', 'model', 'partition'])
    for folder in ['model_improvement', 'temporal_expansion']:
        records = json.loads((root / folder / 'fit_records.json').read_text(encoding='utf-8'))
        mapping = {(r['trial_id'],): (ROOT / r['model_file'], r.get('model_sha256', r.get('sha256'))) for r in records}
        data = replay(folder, 'predictions.csv.gz', ['trial_id'], lambda key, m=mapping: m[key])
        compare_metrics(folder, 'metrics.csv', data, ['trial_id', 'partition'])

    # 7단계 세 대표 모델의 가로형 예측도 원래 모델로 대조
    wide = pd.read_csv(root / 'temporal_failure_diagnostics/row_predictions.csv')
    choice6 = json.loads((root / 'temporal_expansion/selection_frozen.json').read_text(encoding='utf-8'))
    for short, trial in [('LR', 'B_LR_tune_C0p1'), ('RF', 'B_RF_balanced'), ('SVM', 'B_SVM_balanced')]:
        meta = choice6['selected_models'][trial]
        model = joblib.load(ROOT / meta['path'])
        assert sha(ROOT / meta['path']) == meta['sha256']
        with threadpool_limits(limits=2):
            actual = model.predict(indexed.loc[wide.row_id, FEATURES])
        np.testing.assert_array_equal(actual, wide[short])
    checks.append(dict(source='outputs/temporal_failure_diagnostics/row_predictions.csv', rows=len(wide) * 3,
                       groups=3, predictions_exact=True, labels_exact=True, model_hashes_match=True))

    # Fold별 모델과 동결 이후 평가 모델의 기록 확인
    for folder in ['temporal_robustness', 'temporal_weighting']:
        model_dir = ROOT / 'models' / folder
        records = json.loads((root / folder / 'fit_records.json').read_text(encoding='utf-8'))
        reference_hashes = {r['model_file']: r['sha256'] for r in records}
        if folder == 'temporal_robustness':
            prior = json.loads((root / 'temporal_weighting/run_manifest.json').read_text(encoding='utf-8'))
            reference_hashes.update({path: value for path, value in prior['before'].items()
                                     if path.startswith('models\\temporal_robustness\\')})
        def fold_mapping(key):
            path = model_dir / str(key[1]) / f'{key[0]}.joblib'
            return path, reference_hashes[str(path.relative_to(ROOT))]
        mapping = fold_mapping
        data = replay(folder, 'fold_predictions.csv.gz', ['config_id', 'fold'], mapping)
        compare_metrics(folder, 'fold_metrics.csv', data, ['config_id', 'fold'])
        if folder == 'temporal_weighting':
            ranges = replay(folder, 'range_batch8_predictions.csv.gz', ['config_id', 'fold'],
                            lambda key: fold_mapping((key[0], 'B' if str(key[1]) == '6' else 'C')))
            compare_metrics(folder, 'range_batch8_metrics.csv', ranges, ['config_id', 'fold'])
        registry = pd.read_csv(root / folder / ('evaluation_model_hashes.csv' if folder == 'temporal_robustness'
                                               else 'evaluation_models.csv'))
        id_col, path_col = ('config_id', 'model_file') if folder == 'temporal_robustness' else ('model_id', 'path')
        mapping = {(r[id_col],): (ROOT / r[path_col], r['sha256']) for r in registry.to_dict('records')}
        data = replay(folder, 'evaluation_predictions.csv.gz', ['config_id'], lambda key, m=mapping: m[key])
        compare_metrics(folder, 'evaluation_metrics.csv', data, ['config_id', 'fold'])
    pd.DataFrame(checks).to_csv(out / 'historical_prediction_replay.csv', index=False, encoding='utf-8')
    pd.DataFrame(metric_checks).to_csv(out / 'historical_metric_replay.csv', index=False, encoding='utf-8')
    return checks, metric_checks
