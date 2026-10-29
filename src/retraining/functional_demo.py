# 기존5933행과 합성 신규 정답 자료로 실제API 전체 흐름 확인
# 합성Validation 점수는 실제 센서 성능 개선 근거가 아님

import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from ..data import ROOT, GASES
from ..webapp import dataset_registry
from .candidates import train_candidate, json_bytes
from .preservation import verify

OUT = ROOT / 'outputs/retraining_candidates'


def main():
    from tests.test_retraining_candidates import synthetic_source, payload

    data_store = OUT / 'synthetic_dataset_store'
    model_store = OUT / 'synthetic_candidate_store'
    frame, sessions = synthetic_source()
    manifest, _ = dataset_registry.register_dataset(
        payload(frame), payload(sessions), 'synthetic_functional_only.csv',
        'synthetic_functional_test_only', 'known_generator_labels_not_AI',
        True, True, storage=data_store,
    )
    before = {path.name: path.read_bytes() for path in (data_store / 'datasets' / manifest['dataset_id']).iterdir()}
    item = train_candidate(manifest['dataset_id'], feature_contract_confirmed=True,
                           dataset_storage=data_store, candidate_storage=model_store,
                           synthetic_only=True)
    directory = data_store / 'datasets' / manifest['dataset_id']
    assert before == {path.name: path.read_bytes() for path in directory.iterdir()}
    figure_dir = OUT / 'functional_demo'
    figure_dir.mkdir(exist_ok=True)
    classes = item['class_metrics']
    fig, ax = plt.subplots(figsize=(11, 4.8))
    x = np.arange(6)
    for offset, label in [(-0.18, 'official'), (0.18, 'candidate')]:
        sub = classes[classes.model.eq(label)]
        ax.bar(x + offset, sub.recall, width=0.36, label=label)
    ax.set(xticks=x, xticklabels=list(GASES.values()), ylim=(0, 1.05),
           xlabel='Known synthetic label', ylabel='Recall',
           title='Synthetic functional validation only | 60 rows, 10 per class')
    ax.tick_params(axis='x', rotation=20)
    ax.legend(title='Model')
    fig.tight_layout()
    fig.savefig(figure_dir / 'synthetic_recall_comparison.png', dpi=180)
    plt.close(fig)
    fig, axes = plt.subplots(2, 3, figsize=(14, 8.5))
    curves = item['roc_points']
    for ax, gas in zip(axes.ravel(), GASES):
        for label in ['official', 'candidate']:
            sub = curves[curves.gas_id.eq(gas) & curves.model.eq(label)]
            ax.plot(sub.fpr, sub.tpr, label=label)
        ax.plot([0, 1], [0, 1], '--', color='grey', label='reference')
        ax.set(title=GASES[gas] + ' | synthetic OvR ROC',
               xlabel='False Positive Rate', ylabel='True Positive Rate',
               xlim=(0, 1), ylim=(0, 1))
        ax.legend(fontsize=8)
    fig.suptitle('Decision scores, not probabilities | synthetic functional check only')
    fig.tight_layout()
    fig.savefig(figure_dir / 'synthetic_ovr_roc.png', dpi=180)
    plt.close(fig)
    result = dict(synthetic_new_data_only=True, real_new_sensor_data_used=False,
                  base_real_uci_rows=5933, new_synthetic_train_rows=60,
                  synthetic_validation_rows=60, validation_support_per_gas=10,
                  dataset_id=manifest['dataset_id'], candidate_id=item['metadata']['candidate_id'],
                  candidate_directory=str(item['directory']),
                  metrics=item['metadata']['metrics'], review=item['metadata']['review'],
                  immutable_dataset_unchanged=True, prediction_reload_exact=True,
                  original_files=verify(), production_datasets_registered=0,
                  official_model_replaced=False)
    (OUT / 'functional_validation.json').write_bytes(json_bytes(result))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
