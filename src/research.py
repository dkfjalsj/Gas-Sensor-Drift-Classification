# 대표 Notebook의 자료 확인·기존 결과 조회·공통 시각화
# 저장된 연구 점수를 변경하거나 운영 모델을 교체하지 않음

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from .data import ROOT, FEATURES, GASES, read_config, load_dataset


def study_data():
    frame, files = load_dataset(read_config())
    if len(frame) != 13910 or len(FEATURES) != 128 or set(frame.gas) != set(GASES):
        raise ValueError('기존 연구 자료 구성과 다름')
    return frame, files


# 출력 경로는 기존 CSV·JSON 연구 근거로 제한
def result_path(relative):
    path = ROOT / 'outputs' / relative
    if not path.resolve().is_relative_to((ROOT / 'outputs').resolve()):
        raise ValueError('연구 결과 폴더 밖 경로 금지')
    if not path.is_file():
        raise FileNotFoundError('필수 연구 근거 없음: ' + relative)
    return path


def result_table(relative):
    return pd.read_csv(result_path(relative))


def result_json(relative):
    return json.loads(result_path(relative).read_text(encoding='utf-8'))


def bar_values(values, title, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(10, 4))
    values.plot.bar(ax=ax)
    ax.set(title=title, xlabel=xlabel, ylabel=ylabel)
    fig.tight_layout()
    return fig


# 센서별8개 특징의 상관만 표시하며 전체128개 행렬로 해석하지 않음
def sensor_correlation(frame, sensor=1):
    if not 1 <= sensor <= 16:
        raise ValueError('센서 번호는1~16')
    columns = FEATURES[(sensor - 1) * 8:sensor * 8]
    correlation = frame[columns].corr()
    fig, ax = plt.subplots(figsize=(7, 6))
    image = ax.imshow(correlation, vmin=-1, vmax=1, cmap='coolwarm')
    ax.set(xticks=range(8), xticklabels=columns, yticks=range(8), yticklabels=columns,
           title=f'Sensor {sensor}: correlation of 8 features',
           xlabel='Feature', ylabel='Feature')
    fig.colorbar(image, ax=ax, label='Pearson correlation')
    fig.tight_layout()
    return fig


# 전체 자료의 탐색용 변환이며 학습 파이프라인에 전달하지 않음
def exploratory_pca(frame):
    scaled = StandardScaler().fit_transform(frame[FEATURES])
    pca = PCA(n_components=2, random_state=42)
    coordinates = pca.fit_transform(scaled)
    ids = np.random.default_rng(42).choice(len(frame), min(5000, len(frame)), replace=False)
    fig, ax = plt.subplots(figsize=(9, 6))
    scatter = ax.scatter(coordinates[ids, 0], coordinates[ids, 1],
                         c=frame.batch.iloc[ids], cmap='tab10', s=8, alpha=.4)
    ax.set(title='Exploratory PCA by batch (5,000 sampled points)',
           xlabel='Principal component 1', ylabel='Principal component 2')
    fig.colorbar(scatter, ax=ax, label='Batch number')
    fig.tight_layout()
    return fig, pca.explained_variance_ratio_


# 기존 기록의 지표 정의와 분할을 그대로 유지한 표
def comparison_table():
    table = result_table('model_comparison/metrics.csv')
    return table[(table.partition == 'test') & (table.scope == 'pooled')][[
        'experiment', 'model', 'n', 'accuracy', 'macro_precision', 'macro_recall',
        'macro_f1', 'macro_f1_fixed6', 'weighted_f1']].reset_index(drop=True)


def stored_confusion(experiment='A_random', model='SVM_RBF'):
    table = result_table('model_comparison/confusion_matrices.csv')
    rows = table[(table.experiment == experiment) & (table.model == model)
                 & (table.partition == 'test') & (table.scope == 'pooled')]
    if rows.empty:
        raise ValueError('해당 조건의 기존 혼동행렬 없음')
    matrix = rows.pivot(index='true_class', columns='predicted_class', values='count')
    fig, ax = plt.subplots(figsize=(7, 6))
    image = ax.imshow(matrix, cmap='Blues')
    for i in range(6):
        for j in range(6):
            ax.text(j, i, str(matrix.iloc[i, j]), ha='center', va='center')
    ax.set(xticks=range(6), xticklabels=list(GASES.values()),
           yticks=range(6), yticklabels=list(GASES.values()),
           title=f'{experiment} | {model} | recorded Test',
           xlabel='Predicted gas', ylabel='Actual gas')
    ax.tick_params(axis='x', rotation=45)
    fig.colorbar(image, ax=ax, label='Sample count')
    fig.tight_layout()
    return fig
