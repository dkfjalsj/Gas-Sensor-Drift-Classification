# Batch 번호의 숫자 순서로 탐색적 비교 그래프 표시 교정
# 기존 지표·모델·선정·해시 기록 보존 및 교정 이력 별도 저장

import base64
import io
import json
import re
import shutil

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

from .data import ROOT
from .temporal_expansion import sha, write_json, now

OUT = ROOT / 'outputs/temporal_weighting'


# 원본 그래프·보고서를 남긴 뒤 표시 순서만 교정
def run():
    if (OUT / 'plot_order_correction.json').exists():
        raise FileExistsError('Plot correction already exists')
    report = ROOT / 'reports/temporal_weighting_report.html'
    selection_doc = ROOT / 'reports/temporal_weighting_model_selection.md'
    plot = OUT / 'evaluation_range_comparison.png'
    decision_file = OUT / 'selection_frozen.json'
    selection_hash = sha(decision_file)
    decision = json.loads(decision_file.read_text(encoding='utf-8'))
    previous = json.loads((OUT / 'final_verification.json').read_text(encoding='utf-8'))
    assert sha(report) == previous['report_final_sha256']
    assert sha(selection_doc) == previous['selection_document_sha256']
    snapshots = {}
    for original, name in [
        (report, 'report_before_plot_order_fix.html'),
        (selection_doc, 'selection_before_plot_order_fix.md'),
        (plot, 'evaluation_range_comparison_before_order_fix.png'),
    ]:
        target = OUT / name
        shutil.copy2(original, target)
        snapshots[name] = sha(target)
    data = pd.read_csv(OUT / 'evaluation_metrics.csv', dtype={'fold': str})
    selected = decision['selected_scheme']
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    coordinates = []
    for ax, end in zip(axes, [6, 7]):
        names = list(dict.fromkeys(['stage6_SVM', f'train{end}_class_balanced', f'train{end}_{selected}']))
        for name in names:
            sub = data[(data.config_id == name) & (data.fold != 'pooled')].copy()
            sub['batch_numeric'] = sub.fold.astype(int)
            sub = sub.sort_values('batch_numeric')
            assert sub.batch_numeric.tolist() == [9, 10]
            ax.plot(sub.batch_numeric, sub.macro_f1, marker='o', label=name)
            for _, row in sub.iterrows():
                coordinates.append(dict(panel_train_end=end, model_id=name,
                                        batch=int(row.batch_numeric), macro_f1=float(row.macro_f1)))
        ax.set(title=f'Exploratory comparison: Train1-{end}', xlabel='Evaluation batch',
               ylabel='Macro F1', xticks=[9, 10], ylim=(0, 1))
        ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(plot, dpi=150)
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=110)
    plt.close(fig)
    replacement = '<img alt="evaluation_range_comparison" src="data:image/png;base64,'
    replacement += base64.b64encode(buffer.getvalue()).decode('ascii') + '">'
    original_doc = report.read_text(encoding='utf-8')
    pattern = r'<img alt="evaluation_range_comparison" src="data:image/png;base64,[^"]+">'
    corrected, count = re.subn(pattern, lambda match: replacement, original_doc)
    assert count == 1
    note = '<p>그래프 교정 이력: Batch 문자열을 숫자로 정렬해9·10의 표시 순서를 바로잡았다. '
    note += '지표·예측·후보는 변경하지 않았다. 교정 전 보고서·그래프와 해시 기록은 '
    note += '별도 보존했으며 plot_order_correction.json과 plot_coordinates.csv에서 확인 가능하다.</p>'
    report.write_text(corrected.replace('</html>', note + '</html>'), encoding='utf-8')
    with selection_doc.open('a', encoding='utf-8') as stream:
        stream.write('\n## 그래프 표시 교정 이력\n\n')
        stream.write('새9단계 비교 그래프에서 문자열 정렬로9·10의 표시 순서가 바뀐 문제를 숫자 정렬로 교정함. '
                     'CSV 수치·예측·학습·후보·가중치·기존1–8단계 결과는 변경 없음. '
                     '교정 전 보고서·선정문서·그래프 및 과거 해시 기록 보존.\n\n')
        stream.write('문서 보완 후 그래프 교정 실행: '
                     '`.venv\\Scripts\\python.exe -B -X utf8 -m src.temporal_weighting_plot_review`\n')
    pd.DataFrame(coordinates).to_csv(OUT / 'plot_coordinates.csv', index=False, encoding='utf-8')
    assert sha(decision_file) == selection_hash
    write_json(OUT / 'plot_order_correction.json', dict(
        corrected_at_seoul=now(), reason='Numeric batch order replaces lexicographic order in one new plot.',
        snapshots=snapshots, corrected_plot_sha256=sha(plot), report_current_sha256=sha(report),
        selection_document_current_sha256=sha(selection_doc), frozen_selection_sha256=selection_hash,
        correction_code_sha256=sha(ROOT / 'src/temporal_weighting_plot_review.py'),
        model_or_metric_changes=False, older_hash_records_modified=False,
    ))
    print('Numeric Batch9/10 plot order corrected; original report and graph snapshots preserved.')


if __name__ == '__main__':
    run()
