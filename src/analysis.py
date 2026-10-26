"""Run python -m src.analysis. Only exploratory PCA is fitted; no classifier is imported."""
import argparse
import base64
import hashlib
import html
import importlib.metadata
import json
import logging
from datetime import datetime
from pathlib import Path
import platform
import sys
from zoneinfo import ZoneInfo

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp, wasserstein_distance
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split, StratifiedGroupKFold
from sklearn.preprocessing import StandardScaler

from .data import ROOT, FEATURES, GASES, feature_label, read_config, load_dataset, duplicate_summary

SELECTED = [1, 2, 3, 6, 9, 17, 65, 121]
EXPECTED_COUNTS = [445, 1244, 1586, 161, 197, 2300, 3613, 294, 470, 3600]

def table(frame, index=True):
    return frame.to_html(index=index, border=0, float_format=lambda x: f'{x:,.4g}', escape=True)

def audit_split(frame, train, test, name, groups):
    left, right = frame.iloc[train], frame.iloc[test]
    overlap = set(groups.iloc[train]) & set(groups.iloc[test])
    return dict(name=name, train_n=len(left), test_n=len(right),
                train_batches=sorted(map(int, left.batch.unique())),
                test_batches=sorted(map(int, right.batch.unique())),
                missing_train=sorted(set(GASES)-set(map(int, left.gas.unique()))),
                missing_test=sorted(set(GASES)-set(map(int, right.gas.unique()))),
                row_overlap=len(set(train) & set(test)), duplicate_feature_groups=len(overlap),
                test_rows_matching_train=int(groups.iloc[test].isin(overlap).sum()),
                train_class_counts={str(g): int((left.gas == g).sum()) for g in GASES},
                test_class_counts={str(g): int((right.gas == g).sum()) for g in GASES})

def build_split_audits(frame, groups, seed):
    indices = np.arange(len(frame))
    train, test = train_test_split(indices, test_size=.2, stratify=frame.gas, random_state=seed)
    audits = [audit_split(frame, train, test, 'A_stratified_random_80_20', groups)]
    assignments = pd.DataFrame({'row_id': frame.row_id, 'feature_group': groups,
                                'random_split': np.where(np.isin(indices, test), 'test', 'train')})
    if audits[0]['duplicate_feature_groups']:
        splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)
        train, test = next(splitter.split(indices, frame.gas, groups))
        audits.append(audit_split(frame, train, test, 'A_group_safe_approx_80_20', groups))
        assignments['group_safe_split'] = np.where(np.isin(indices, test), 'test', 'train')
    for end in (1, 3):
        for target in range(end+1, 11):
            train = indices[frame.batch <= end]
            test = indices[frame.batch == target]
            audits.append(audit_split(frame, train, test, f'B_fixed_1-{end}_to_{target}', groups))
    for end in range(2, 10):
        train = indices[frame.batch <= end]
        test = indices[frame.batch == end+1]
        audits.append(audit_split(frame, train, test, f'B_expanding_1-{end}_to_{end+1}', groups))
    return audits, assignments

def run(config_path=None):
    config = read_config(config_path)
    out, reports = ROOT / 'outputs', ROOT / 'reports'
    out.mkdir(exist_ok=True)
    reports.mkdir(exist_ok=True)
    files_dir = out / 'figures'
    files_dir.mkdir(exist_ok=True)
    # Inventory is written even when parsing subsequently fails.
    inventory = []
    for batch in range(1, 11):
        path = Path(config['data_dir']) / f'batch{batch}.dat'
        inventory.append(dict(batch=batch, path=str(path), exists=path.is_file(),
                              bytes=path.stat().st_size if path.is_file() else None))
    pd.DataFrame(inventory).to_csv(out / 'file_inventory.csv', index=False, encoding='utf-8')
    frame, files = load_dataset(config)
    files.to_csv(out / 'file_validation.csv', index=False, encoding='utf-8')
    x = frame[FEATURES]
    groups, duplicates = duplicate_summary(frame)
    for b in range(1, 11):
        sub = frame[frame.batch == b]
        files.loc[files.batch == b, 'within_batch_duplicate_extra'] = int(sub.duplicated(FEATURES).sum())
    files.to_csv(out / 'file_validation.csv', index=False, encoding='utf-8')
    counts = pd.crosstab(frame.batch, frame.gas).reindex(index=range(1, 11), columns=GASES, fill_value=0)
    counts.columns = [GASES[c] for c in counts.columns]
    counts.to_csv(out / 'batch_class_counts.csv', encoding='utf-8')
    total = counts.sum()
    summary = dict(samples=len(frame), features=len(FEATURES), classes=sorted(map(int, frame.gas.unique())),
                   class_counts={GASES[g]: int((frame.gas == g).sum()) for g in GASES},
                   class_imbalance_ratio=float(total.max()/total.min()),
                   missing_nan=int(x.isna().sum().sum()), infinite=int(np.isinf(x.to_numpy()).sum()),
                   expected_total_matches=len(frame) == config['expected_samples'],
                   expected_batch_totals_match=counts.sum(axis=1).tolist() == EXPECTED_COUNTS,
                   **duplicates)
    (out / 'validation_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    if not np.isfinite(x.to_numpy()).all():
        raise ValueError('Non-finite input: validation saved; EDA stops instead of silently imputing')
    desc = x.describe(percentiles=[.01, .25, .5, .75, .99]).T
    q1, q3 = x.quantile(.25), x.quantile(.75)
    flag = (x.lt(q1-1.5*(q3-q1)) | x.gt(q3+1.5*(q3-q1)))
    desc['iqr_flag_count'] = flag.sum()
    desc['iqr_flag_rate'] = flag.mean()
    desc['zero_count'] = (x == 0).sum()
    desc['constant'] = x.nunique() == 1
    desc['sensor'] = [(i-1)//8+1 for i in range(1, 129)]
    desc['kind'] = [feature_label(i).split(': ', 1)[1] for i in range(1, 129)]
    desc.to_csv(out / 'feature_summary.csv', encoding='utf-8')
    frame.groupby(['batch','gas'])[FEATURES].agg(['mean','median','std','min','max']).to_csv(
        out / 'batch_gas_feature_summary.csv', encoding='utf-8')
    duplicate_rows = frame.loc[frame.duplicated(FEATURES, keep=False), ['row_id','batch','source_line','gas']].copy()
    duplicate_rows['feature_group'] = groups.loc[duplicate_rows.index]
    duplicate_rows.to_csv(out / 'duplicate_rows.csv', index=False, encoding='utf-8')
    audits, assignments = build_split_audits(frame, groups, config['random_state'])
    (out / 'split_audit.json').write_text(json.dumps(audits, indent=2), encoding='utf-8')
    assignments.to_csv(out / 'split_manifest.csv', index=False, encoding='utf-8')
    order_rows = []
    for b in range(1, 11):
        sub = frame[frame.batch == b]
        starts = np.r_[True, sub.gas.to_numpy()[1:] != sub.gas.to_numpy()[:-1]]
        for _, run in sub.groupby(np.cumsum(starts)):
            order_rows.append(dict(batch=b, gas=int(run.gas.iloc[0]), first_line=int(run.source_line.iloc[0]),
                                   last_line=int(run.source_line.iloc[-1]), rows=len(run)))
    pd.DataFrame(order_rows).to_csv(out / 'label_order_runs.csv', index=False, encoding='utf-8')
    plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':10, 'axes.grid':True,
                         'grid.alpha':.2, 'figure.dpi':120})
    figures = {}
    def save(fig, name, caption):
        fig.tight_layout()
        path = files_dir / f'{name}.png'
        fig.savefig(path, dpi=140, bbox_inches='tight')
        plt.close(fig)
        figures[name] = f'<figure><img alt="{html.escape(caption)}" src="data:image/png;base64,{base64.b64encode(path.read_bytes()).decode()}"><figcaption>{html.escape(caption)}</figcaption></figure>'

    fig, ax = plt.subplots(figsize=(9,4))
    bars = ax.bar(total.index, total.values, color=plt.cm.tab10(np.arange(6)))
    ax.bar_label(bars)
    ax.set(title='Gas class sample counts', xlabel='Gas class', ylabel='Number of samples')
    save(fig, 'class_counts', '관찰: 전체 가스별 표본 수. 클래스 순서는 공식 번호 1–6이다.')
    fig, axes = plt.subplots(1, 2, figsize=(14,5))
    counts.plot.bar(stacked=True, ax=axes[0], colormap='tab10')
    axes[0].set(title='Class counts by batch', xlabel='Batch (ordered category)', ylabel='Number of samples')
    (counts.div(counts.sum(axis=1), axis=0)*100).plot.bar(stacked=True, ax=axes[1], colormap='tab10', legend=False)
    axes[1].set(title='Class proportions by batch', xlabel='Batch (ordered category)', ylabel='Within-batch percentage (%)')
    axes[0].legend(fontsize=8)
    save(fig, 'batch_counts', '관찰: Batch 크기와 클래스 구성은 일정하지 않다. 번호 간 간격을 실제 시간 간격으로 해석하지 않는다.')
    fig, axes = plt.subplots(2,4,figsize=(16,8))
    for ax, i in zip(axes.flat, SELECTED):
        v = x[f'f{i:03d}']
        # Transform only the display coordinate, preserving sign and showing heavy tails.
        ax.hist(np.sign(v)*np.log10(1+np.abs(v)), bins=50, color='#357ca5')
        ax.set(title=feature_label(i), xlabel='sign(x) log10(1+abs(x)) [display]', ylabel='Number of samples')
    save(fig, 'feature_distributions', '사전 지정한 센서·특징을 표시했다. 전체 128개 특징의 원래 범위와 IQR 표시는 feature_summary.csv에 저장했다.')
    fig, axes = plt.subplots(2,2,figsize=(13,9))
    for ax, i in zip(axes.flat, [1,2,65,121]):
        ax.boxplot([frame.loc[frame.gas==g,f'f{i:03d}'] for g in GASES], tick_labels=list(GASES.values()), showfliers=False)
        ax.set_yscale('symlog', linthresh=1)
        ax.tick_params(axis='x', rotation=20)
        ax.set(title=feature_label(i)+' by gas', xlabel='Gas class', ylabel='Feature value (symlog; original units)')
    save(fig, 'gas_response', '상자는 IQR, 중앙선은 중앙값, 수염은 1.5×IQR 범위다. 극단점은 도표에서만 생략했으며 분석에서는 제거하지 않았다. 단위는 파일에 기재되지 않았다.')
    fig, axes = plt.subplots(2,2,figsize=(13,9))
    for ax, i in zip(axes.flat, [1,2,65,121]):
        for g, gas in GASES.items():
            med = frame[frame.gas==g].groupby('batch')[f'f{i:03d}'].median().reindex(range(1,11))
            ax.plot(range(1,11), med, marker='o', label=gas)
        ax.set_yscale('symlog', linthresh=1)
        ax.set(title=feature_label(i)+' median by batch and gas', xlabel='Batch (ordered category)', ylabel='Median feature value (symlog)', xticks=range(1,11))
    axes[0,0].legend(fontsize=7)
    save(fig, 'batch_gas_trends', '관찰: 동일 가스 안에서도 Batch별 반응 중앙값을 비교한다. 누락 클래스는 선을 끊으며 Batch 사이를 실제 경과 시간으로 보간하지 않는다.')
    base = frame.batch == 1
    base_mean, base_sd = x[base].mean(), x[base].std(ddof=0)
    usable = base_sd > 0
    shift = (frame.groupby('batch')[FEATURES].mean()-base_mean).div(base_sd.where(usable))
    shift.to_csv(out / 'batch_standardized_mean_shift.csv', encoding='utf-8')
    fig, ax = plt.subplots(figsize=(15,5))
    im = ax.imshow(shift, aspect='auto', cmap='coolwarm', vmin=-3, vmax=3)
    ax.set(title='Batch mean shift relative to batch 1 (color clipped at +/-3)', xlabel='Feature index (1..128)', ylabel='Batch (ordered category)',
           yticks=np.arange(10), yticklabels=range(1,11), xticks=np.arange(0,128,8), xticklabels=range(1,129,8))
    fig.colorbar(im, ax=ax, label='(Batch mean - batch 1 mean) / batch 1 SD')
    save(fig, 'batch_shift', '해석 주의: 전체 평균 차이에는 가스 구성 변화도 섞인다. 색상만 ±3에서 제한하며 실제 수치는 CSV에 보존한다.')
    conditional = pd.DataFrame(index=range(1,11), columns=list(GASES.values()), dtype=float)
    dist_rows = []
    for g, gas in GASES.items():
        reference = x[base & (frame.gas==g)]
        for b in range(1,11):
            target = x[(frame.batch==b) & (frame.gas==g)]
            if target.empty or reference.empty:
                continue
            conditional.loc[b, gas] = ((target.mean()-reference.mean()).abs()/base_sd.where(usable)).mean()
            if b == 1:
                continue
            for i in SELECTED:
                col = f'f{i:03d}'
                ks = ks_2samp(reference[col], target[col], method='asymp')
                dist_rows.append(dict(gas=gas,batch=b,feature=col,reference_n=len(reference),target_n=len(target),
                                      ks_statistic=float(ks.statistic),p_value=float(ks.pvalue),
                                      wasserstein_over_batch1_sd=float(wasserstein_distance(reference[col],target[col])/base_sd[col]) if usable[col] else None))
    distances = pd.DataFrame(dist_rows)
    # Benjamini-Hochberg across every selected-feature/gas/batch test, not per plot.
    order = np.argsort(distances.p_value.to_numpy())
    adjusted = np.minimum.accumulate((distances.p_value.to_numpy()[order]*len(order)/np.arange(1,len(order)+1))[::-1])[::-1]
    q = np.empty(len(order)); q[order] = np.minimum(adjusted,1)
    distances['q_bh'] = q
    distances.to_csv(out / 'distribution_checks.csv', index=False, encoding='utf-8')
    conditional.to_csv(out / 'class_conditional_shift.csv', encoding='utf-8')
    fig, ax = plt.subplots(figsize=(10,6))
    im = ax.imshow(np.ma.masked_invalid(conditional.to_numpy()), aspect='auto', cmap='viridis')
    ax.set(title='Within-gas mean shift relative to batch 1', xlabel='Gas class', ylabel='Batch (ordered category)',
           xticks=range(6), xticklabels=list(GASES.values()), yticks=range(10), yticklabels=range(1,11))
    fig.colorbar(im, ax=ax, label='Mean absolute shift / pooled batch 1 SD (128 features)')
    save(fig, 'conditional_shift', '관찰: 동일 가스별 평균 벡터 차이를 Batch 1의 전체 클래스 표준편차로 정규화했다. 빈 칸은 해당 클래스 없음. 이 지표는 분류 성능이나 드리프트 원인의 추정치가 아니다.')
    # EXPLORATORY ONLY. Neither estimator nor transformed values are persisted for evaluation.
    z = StandardScaler().fit_transform(x)
    pca = PCA(n_components=10, svd_solver='full')
    pcs = pca.fit_transform(z)
    variance = pd.DataFrame({'component':np.arange(1,11), 'explained_variance_ratio':pca.explained_variance_ratio_,
                             'cumulative_ratio':np.cumsum(pca.explained_variance_ratio_)})
    variance.to_csv(out / 'pca_explained_variance.csv', index=False, encoding='utf-8')
    fig, axes = plt.subplots(1,2,figsize=(14,6))
    for g, gas in GASES.items():
        mask = frame.gas == g
        axes[0].scatter(pcs[mask,0], pcs[mask,1], s=5, alpha=.35, label=gas, rasterized=True)
    axes[0].legend(markerscale=3, fontsize=8)
    dots = axes[1].scatter(pcs[:,0],pcs[:,1],c=frame.batch,cmap='viridis',s=5,alpha=.4,vmin=.5,vmax=10.5,rasterized=True)
    fig.colorbar(dots, ax=axes[1], label='Batch (ordered category)', ticks=range(1,11))
    for ax, title in zip(axes, ['PCA colored by gas (all samples)', 'PCA colored by batch (all samples)']):
        ax.set(title=title, xlabel=f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)',
               ylabel=f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)')
    save(fig, 'pca', '탐색 전용: 전체 자료에서 StandardScaler와 PCA를 Fit했다. 이 변환을 이후 Train/Test 평가에 재사용하면 누수가 발생한다. 점의 중첩과 2차원 투영은 분류 가능성을 확정하지 않는다.')
    fig, ax = plt.subplots(figsize=(8,4))
    ax.bar(variance.component, variance.explained_variance_ratio, label='Individual')
    ax.plot(variance.component, variance.cumulative_ratio, 'o-', label='Cumulative')
    ax.set(title='Exploratory PCA explained variance (first 10 components)', xlabel='Principal component', ylabel='Variance ratio', xticks=range(1,11))
    ax.legend()
    save(fig, 'pca_variance', 'StandardScaler 적용 후 PCA 설명분산. 차원 수 선택과 분류 성능 평가는 이번 단계에서 수행하지 않았다.')
    # Confirm immutable source bytes after all analysis.
    for record in files.to_dict('records'):
        current = hashlib.sha256((Path(config['data_dir'])/record['file']).read_bytes()).hexdigest()
        if current != record['sha256']:
            raise RuntimeError(f'Source file changed during run: {record["file"]}')
    manifest = dict(generated_at_seoul=datetime.now().astimezone().isoformat(), python=platform.python_version(),
                    config=config, packages={p:importlib.metadata.version(p) for p in ['numpy','pandas','scipy','scikit-learn','matplotlib','pytest']},
                    source_hashes_unchanged=True, classifiers_trained=False,
                    analysis_file_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out / 'run_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    plan = evaluation_plan(audits)
    (reports / 'evaluation_design.md').write_text(plan, encoding='utf-8')
    generate_report(frame, files, counts, desc, summary, conditional, distances, variance, figures, audits, manifest, plan)
    print(json.dumps({'summary':summary,'pca_first_two_ratio':float(variance.explained_variance_ratio.iloc[:2].sum()),
                      'conditional_shift_batch10':conditional.loc[10].to_dict(),
                      'report':str(reports/'eda_report.html')},ensure_ascii=False,indent=2))

def evaluation_plan(audits):
    return '''# 모델 비교 실험 설계 (미실행)

## 공통 데이터와 모델
입력은 f001–f128만 사용한다. gas는 타깃, batch/source_line/row_id는 메타데이터다.
Logistic Regression, Random Forest, SVM(RBF)을 같은 표본·레이블·분할·평가지표로 비교한다.
세 모델 모두 Pipeline(StandardScaler, estimator)을 기본 조건으로 정한다. Random Forest에도
동일한 스케일링 조건을 적용할 수 있다. 특징 선택·PCA·대체·이상치 처리·재표본화는 기본 실험에서 사용하지 않는다.
추후 필요하면 Train 내부의 각 Fold에서만 Fit하는 파이프라인 단계로 추가하고 공통 ablation으로 비교한다.
EDA 결과를 보고 유리한 특징·클래스를 사후 선택하지 않는다. 모델의 기본값과 버전, LR 반복 한도,
SVM 커널, RF seed를 실행 전 명시하며, 이번에는 분류기 생성·Fit·튜닝을 수행하지 않았다.

## A. Stratified Random Split
전체 자료에서 seed=42, Train 80%, Test 20% 계층 분할을 미리 기록했다.
모든 모델은 split_manifest.csv의 같은 행 목록을 사용한다. 정확 중복 특징이 양쪽에 걸치면
일반 분할은 누수 진단용으로만 남기고 StratifiedGroupKFold(5개 Fold)의 첫 Fold를 약 20% holdout으로 사용한다.
그룹 분할의 클래스별 수와 크기는 재확인한다. 같은 특징에 상충하는 레이블이 있으면 출처 확인 전 학습을 중단한다.
내부 검증은 Train 내부 5-fold StratifiedKFold(shuffle=True, random_state=42),
중복이 있으면 StratifiedGroupKFold로 대체한다. 가장 작은 클래스의 고유 그룹 수보다 Fold 수를 크게 잡지 않는다.
클래스당 그룹이 부족하면 Fold 수를 줄이고 사유를 보고한다. Test를 내부 검증이나 설정 결정에 사용하지 않는다.
표본의 독립성과 동일 분포 가정은 보장되지 않으므로 이 평가는 동일 수집 집합 내 기준 성능으로 해석한다.

## B. Batch 기반 시간순 분할
주 실험은 Batch 1만 Train으로 고정하고 Batch 2–10 각각을 Test로 평가한다.
보조 실험은 Batch 1–3으로 Train을 고정하고 Batch 4–10을 각각 평가한다.
적응에 따른 학습 자료 증가와 시간 변화의 혼동을 구분하기 위해,
확장 창 Train=Batch 1..k, Test=Batch k+1 (k=2..9)은 별도 보조 표로 보고한다.
Batch 번호의 순서만 사용하며 숫자 간격을 월 간격으로 사용하지 않는다.
학습 Batch가 하나인 주 실험은 Batch 간 시간순 내부 검증이 불가능하다.
이때 Train 안의 계층/그룹 검증은 보조 안정성 진단으로만 사용하며 시간 일반화 검증이라고 부르지 않는다.
여러 학습 Batch가 있는 경우 forward validation: Train=1..j, Validation=j+1을 사용하고
외부 Test보다 앞선 Batch만 포함한다. 클래스 누락 Fold를 명시하고 임의로 미래 표본을 보충하지 않는다.
Train에 없는 클래스가 Test에 있으면 알려진 6종 분류를 온전히 검증할 수 없으므로
해당 분할을 부적격으로 표시하고, 새 클래스 문제를 별도로 논의한다.
Test에 특정 클래스가 없으면 해당 클래스 recall/F1은 NA와 support=0으로 보고한다.
미래 Batch가 Train과 같은 특징 벡터를 포함하면 미래 Test에서 해당 중복을 제외한 결과를 주 결과로 삼고
원래 평가 수, 제외 수, 클래스 구성, 원본 중복 포함 결과를 민감도 분석으로 함께 보고한다.
배치 내부 행 순서로 시계열 Fold를 만들지 않는다. 동일 측정의 변형·근접 중복은 정확 중복 검사로 보장되지 않는다.

## 지표와 공정성
Accuracy, macro-F1, balanced accuracy(평가 Batch에 실제 존재하는 클래스의 평균 recall),
클래스별 precision/recall/F1/support와 고정 6×6 confusion matrix를 제공한다.
6종 모두 있는 Test는 6-class macro-F1을 주 지표로 사용한다.
누락 클래스가 있는 Test는 present-class macro-F1을 보고하고 그 클래스 집합을 명시한다.
고정 6-class zero-fill macro-F1을 보조 지표로 함께 표시하여 클래스 구성이 다른 Batch끼리의 단순 비교를 피한다.
분할별·모델별 paired 비교, 전체 표본 가중 집계와 Batch 동일 가중 집계를 구분한다.
소수 클래스 support와 클래스별 결과를 함께 해석하며 accuracy만으로 선정하지 않는다.
불확실성은 동일 Test 표본의 paired bootstrap을 고려하되 독립 표본 가정을 밝히고,
Batch 수가 적다는 한계와 연속 수집 의존성 때문에 신뢰구간을 과신하지 않는다.
class_weight/resampling, 특징 선택, 튜닝은 이번 범위 밖이며 추후 모든 모델에 동일한 검증 예산·원칙을 적용한다.
모든 scaler/selector/PCA는 매 Train/Fold에서 새로 Fit한다. EDA scaler/PCA는 저장하거나 재사용하지 않는다.
하이퍼파라미터 결정 전 Test 결과를 확인하지 않으며, 이번 EDA로 이미 전체 분포를 관찰했음을 기록한다.
완전히 독립적인 최종 확인에는 새 자료가 필요하다.

## 드리프트 해석
시간에 따른 성능 감소는 아직 확인하지 않았다. 향후 감소하더라도 센서 드리프트 외에
클래스 구성, 가스 농도, 실험 환경, 표본 수, 수집·전처리 변화가 원인일 수 있다.
같은 가스 내 특징 분포 변화와 Batch별 성능을 병렬로 비교하되 상관과 인과를 구분한다.
'''

def generate_report(frame, files, counts, desc, summary, conditional, distances, variance, figures, audits, manifest, plan):
    absent = [f'Batch {b}: {", ".join(counts.columns[counts.loc[b]==0])}' for b in counts.index if (counts.loc[b]==0).any()]
    extremes = desc.sort_values('iqr_flag_rate', ascending=False).head(10)
    selected = desc.loc[[f'f{i:03d}' for i in SELECTED], ['min','1%','50%','99%','max','iqr_flag_rate']]
    rows_flagged = int(((frame[FEATURES] < (desc['25%']-1.5*(desc['75%']-desc['25%']))) |
                        (frame[FEATURES] > (desc['75%']+1.5*(desc['75%']-desc['25%'])))).any(axis=1).sum())
    audit_table = pd.DataFrame([{k:v for k,v in a.items() if k not in ('train_class_counts','test_class_counts')} for a in audits])
    max_shift = conditional.loc[10].sort_values(ascending=False)
    sections = []
    def section(title, body):
        sections.append(f'<section><h2>{title}</h2>{body}</section>')
    section('1. 프로젝트 개요 및 기획의도', '''<p>Gas Sensor Drift Classification은 센서 특징만으로 6종 가스를 구분할 수 있는지,
초기 Batch에서 학습한 모델이 이후 Batch에 일반화하는지, 분포 변화와 성능 변화가 어떤 관계인지 검토하는 연구다.
이번 단계는 데이터 검증·EDA·평가 설계만 수행했다. 분류기를 학습하지 않았으므로 정확도나 성능 저하를 주장하지 않는다.</p>
<p><b>표기 원칙:</b> 관찰은 파일에서 계산한 사실, 공식 설명은 UCI 문서의 정보,
해석은 관찰에 대한 가능한 설명이다. 원인과 미확인 사항은 단정하지 않는다.</p>''')
    section('2. 데이터셋 출처 및 구성', f'''<p>공식 출처: <a href="{html.escape(manifest['config']['uci_url'])}">UCI Gas Sensor Array Drift Dataset (ID 224)</a>,
Vergara (2012), DOI <a href="https://doi.org/10.24432/C5RP6W">10.24432/C5RP6W</a>. 확인일: 2026-10-26.</p>
<p>공식 설명은 13,910개 측정, 16개 센서, 센서당 8개 특징, 6종 가스, 10개 Batch를 제시한다.
각 센서의 특징은 ΔR, 정규화 반응, 상승 및 하강 EMA(각 α=0.001, 0.01, 0.1)다.
클래스 번호는 1=Ethanol, 2=Ethylene, 3=Ammonia, 4=Acetaldehyde, 5=Acetone, 6=Toluene이다.</p>
<p>로컬 원본 경로: <code>{html.escape(manifest['config']['data_dir'])}</code>. 복사·이동 없이 읽었다.
각 행은 정수 label 뒤에 공백으로 분리한 index:value 128쌍이다. 헤더, 농도, 측정 timestamp 열이 없다.</p>
<p>공식 Batch/Month ID 대응은 1→1·2; 2→3·4·8·9·10; 3→11·12·13; 4→14·15; 5→16;
6→17·18·19·20; 7→21; 8→22·23; 9→24·30; 10→36이다.
이를 개별 표본의 날짜나 시간으로 변환하지 않았다. 공식 문서의 달력 기간과 “36 months” 표기 사이에는
해석상 불명확함이 있어 실제 날짜축을 생성하지 않았다.</p>
<p>미확인: 로컬 파일이 UCI 현재 배포본과 바이트 단위로 동일한지 확인하지 않았다.
UCI는 Batch10의 2013년 수정 이력을 기록한다. 로컬 SHA-256은 재현성과 변경 감지용이며 배포본 인증값이 아니다.
UCI 페이지의 과거 연구 전용 설명과 현재 CC BY 4.0 표시가 함께 존재한다는 출처상의 불일치도 기록한다.</p>''')
    section('3. 데이터 검증 결과', f'''<p class="fact">관찰: {summary['samples']:,}행 × {summary['features']}개 특징,
클래스 {summary['classes']}. UCI 표본 수 일치: {summary['expected_total_matches']};
참고 Batch별 표본 수 일치: {summary['expected_batch_totals_match']}.</p>
{table(files.drop(columns=['sha256','format','spaces','tabs']), False)}
<p>모든 행의 label과 특징 index 1..128의 개수·중복·정렬을 엄격히 검사했다.
생략된 특징을 0으로 채우지 않았다. 공백/탭 발생 횟수와 SHA-256은 file_validation.csv에 포함한다.</p>
<p>NaN/결측 {summary['missing_nan']}개, 무한대 {summary['infinite']}개.
정확 특징 중복의 추가 행 {summary['feature_duplicate_extra']}개, 중복 그룹에 속한 전체 행 {summary['feature_duplicate_rows']}개,
label+특징 중복 추가 행 {summary['labeled_duplicate_extra']}개, 상충 label 그룹 {summary['conflicting_label_groups']}개,
Batch 간 중복 그룹 {summary['cross_batch_duplicate_groups']}개.
정확 부동소수점 값 일치 기준이며 근접 중복이나 같은 실험의 반복 여부는 확인하지 못했다.</p>
<p>특징별 전역 1.5×IQR 경계 밖 표본을 탐색용으로 표시했다. 하나 이상 해당하는 행은 {rows_flagged:,}개이며,
상수 특징은 {int(desc.constant.sum())}개다. 클래스 혼합·농도·왜도에 의해 극단값이 생길 수 있어 자동 제거하지 않았다.</p>
{table(extremes[['min','50%','max','iqr_flag_count','iqr_flag_rate']])}
<p>행 순서는 source_line으로 보존했다. label_runs와 labels_nondecreasing은 저장된 클래스 순서의 속성이다.
행 번호를 측정 시각이나 Batch 내 시간 순서로 간주하지 않는다. label_order_runs.csv에서 클래스 연속 구간을 확인할 수 있다.</p>''')
    section('4. 가스별 클래스 분포', figures['class_counts']+f'''<p class="fact">관찰: 최대/최소 클래스 표본 비율 {summary['class_imbalance_ratio']:.3f}.
이 비율은 표본 수 불균형이며 실제 현장 가스 발생확률이 아니다.</p>{table(counts.sum().to_frame('samples'))}''')
    section('5. Batch별 데이터 분포', figures['batch_counts']+table(counts)+
            '<p class="fact">관찰: 클래스 누락 — '+html.escape('; '.join(absent) or '없음')+
            '</p><p>해석: Batch 간 클래스 비율이 달라 전체 특징 분포 차이와 accuracy가 클래스 구성의 영향을 받을 수 있다.</p>')
    section('6. 주요 센서 특징 분석', '''<p>대표 특징은 성능이나 유의확률로 선택하지 않고 센서와 특징 종류의 범위를 보도록 미리 지정했다.
전체 특징의 기술통계와 가스·Batch 조건부 요약은 CSV에 제공한다. 원시 센서 시계열이 아닌 추출 특징을 분석했다.</p>'''+
            table(selected)+figures['feature_distributions']+figures['gas_response']+
            '<p>해석: 가스별 반응 분포의 차이와 중첩은 분류 연구의 근거가 되지만, 이 그래프만으로 일반화 성능을 확정할 수 없다. 파일에 물리 단위가 없으므로 임의의 단위를 부여하지 않았다.</p>')
    section('7. PCA 시각화', f'''<p class="fact">관찰: 전체 자료 표준화 후 PC1+PC2 설명분산 비율은
{variance.explained_variance_ratio.iloc[:2].sum():.2%}다. PC1은 {variance.explained_variance_ratio.iloc[0]:.2%},
PC2는 {variance.explained_variance_ratio.iloc[1]:.2%}다. 첫 10개 성분만 계산했다.</p>'''+figures['pca']+figures['pca_variance']+
            '<p>해석: PCA는 분산 최대화 투영이며 클래스 분리나 인과관계의 검정이 아니다. 전체 EDA에 Fit한 객체와 변환 자료는 학습용으로 저장하지 않았다.</p>')
    section('8. 센서 드리프트 관련 탐색 결과', figures['batch_gas_trends']+figures['batch_shift']+figures['conditional_shift']+
            f'''<p class="fact">관찰: Batch 10과 Batch 1의 동일 가스 평균 차이(128개 특징의 절대 차이를 Batch 1 전체 SD로 나눈 평균)는
{'; '.join(f'{g}: {v:.3f}' for g,v in max_shift.items())}이다. 단위 없는 탐색 지표이며 임계값을 설정하지 않았다.</p>
<p>선택한 8개 특징에서 가스별 Batch 1 대비 KS 통계량, Wasserstein 거리와 전체 {len(distances)}회 비교의 BH 보정 q값을
distribution_checks.csv에 저장했다. q&lt;0.05 비교 수는 {int((distances.q_bh<.05).sum())}개다.
KS의 독립 표본 가정과 다중 비교, 클래스별 표본 수 차이를 고려해야 하며 이 수치만으로 센서 노화나 인과를 판정하지 않는다.</p>
<p><b>해석:</b> 같은 가스 안의 분포 변화는 클래스 비율 변화만으로 설명되지 않을 가능성을 보여 준다.
그러나 농도와 실험 환경 등의 메타데이터가 없으므로 센서 드리프트만의 효과로 분리할 수 없다.
조건부 shift도 가스별 농도 구성이 다르면 변할 수 있다. 미래 성능 저하 및 분포 변화와의 관계는 아직 미검증이다.</p>''')
    section('9. 머신러닝 모델 비교 실험 설계', '<p>자세한 실행 전 설계는 evaluation_design.md에 기록했다. 아래는 분할만 만든 진단 결과이며 모델 결과가 아니다.</p>'+
            table(audit_table, False)+'<pre>'+html.escape(plan)+'</pre>')
    section('10. 데이터의 한계 및 다음 단계', '''<p>한 수집 플랫폼의 추출 특징 자료이므로 새로운 장비·환경에서의 일반화는 미확인이다.
농도·환경·센서 관리·측정별 timestamp·반복 실험 식별자가 없어 원인 분리가 제한된다.
Batch는 불규칙한 측정 시기 구간이며 Batch 내부 저장 순서의 시간적 의미는 확인되지 않았다.
가스 누락 Batch, 클래스 불균형, 극단값, 소수 클래스의 작은 support를 평가에서 명시해야 한다.</p>
<p>다음 단계는 평가 설계를 확정하고 동일 분할의 Train 내부에만 전처리를 Fit하여 세 모델을 학습·비교하는 것이다.
그 후 Batch별 성능과 동일 가스의 분포 변화를 함께 분석하되, 드리프트가 유일한 저하 원인이라고 가정하지 않는다.
이번 산출물에는 모델 Fit·하이퍼파라미터 튜닝·최종 모델 선정·모델 성능 수치가 없다.</p>
<p>재현: 프로젝트 루트에서 <code>.venv\\Scripts\\python.exe -m src.analysis</code> 실행.
설정은 config.json, 실행 환경은 requirements-lock.txt와 outputs/run_manifest.json,
원본 지문은 outputs/file_validation.csv에 기록했다. 실행 전후 원본 SHA-256 일치를 확인했다.</p>''')
    document = '''<!doctype html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gas Sensor Drift Classification — EDA 보고서</title><style>
body{font-family:"Malgun Gothic",Arial,sans-serif;max-width:1240px;margin:35px auto;padding:0 24px;color:#1d2d40;line-height:1.7;background:#f7f9fc}
section{background:white;border:1px solid #dce3eb;padding:24px;margin:24px 0;border-radius:10px;overflow-x:auto}
h1,h2{color:#163e66}table{border-collapse:collapse;font-size:13px;white-space:nowrap;max-width:100%}
th,td{padding:7px 10px;border:1px solid #dce3eb;text-align:right}th{background:#edf3f9}figure{margin:24px 0}
img{max-width:100%;height:auto}figcaption{font-size:13px;color:#4d6072}pre{white-space:pre-wrap;font-family:inherit;font-size:14px}
code{background:#edf3f9;padding:2px 4px}.fact{border-left:4px solid #1e847b;padding-left:12px}a{color:#125b9a}</style></head><body>
<h1>Gas Sensor Drift Classification</h1><p>데이터 검증 · 탐색적 분석 · 모델 평가 설계 | 모델 학습 미실행</p>'''
    document += ''.join(sections) + '</body></html>'
    (ROOT/'reports'/'eda_report.html').write_text(document, encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=None)
    args = parser.parse_args()
    try:
        run(args.config)
    except (OSError, ValueError, RuntimeError, KeyError) as exc:
        logging.exception('Analysis failed: %s', exc)
        sys.exit(1)

if __name__ == '__main__':
    main()
