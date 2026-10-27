# 저장된 계산값으로 17단계 해석과 최종 검사 결과 정리
# 추가 예측·학습 없이 보고서만 갱신

import html

import pandas as pd

from .data import ROOT
from .temporal_calibration import OUT, now, verify, write
from .temporal_calibration_report import render, test_summary


# 기존 결과 표를 바탕으로 효과와 한계 정리
def main():
    render()
    summary = pd.read_csv(OUT / "ratio_summary.csv").set_index("rate")
    classes = pd.read_csv(OUT / "mean_class_metrics.csv")
    notes = []
    for rate in [0, 5, 10, 20]:
        row = summary.loc[rate]
        notes.append(
            f"계산값: {rate}% 교정의 평균 Macro F1은 "
            f"{row.mean_macro_f1 * 100:.2f}%, 같은 평가 행의 기준 대비 "
            f"{row.mean_macro_delta * 100:+.2f}%p임."
        )
    for gas_id in [4, 6]:
        sub = classes[classes.gas_id == gas_id].set_index("rate")
        values = " → ".join(
            f"{rate}% 교정: {sub.loc[rate, 'recall'] * 100:.2f}%"
            for rate in [0, 5, 10, 20]
        )
        notes.append(f"계산값: {sub.iloc[0].gas}의 Fold·시드 평균 Recall은 {values}임.")
    notes.extend([
        "계산값: Fold A의 Toluene 평가 표본은 시드마다 233개임. "
        "기준 정분류는 모두 0개, 각 교정 비율에서 시드11은 233개, "
        "시드23·42는 각각 232개임. Toluene→Acetaldehyde 오분류는 "
        "기준 209·208·202개에서 각 교정 비율 모두 0개로 감소함.",
        "계산값: 나머지 네 가스의 평균 F1은 기준 대비 5%에서 +2.16%p, "
        "10%에서 +3.46%p, 20%에서 +3.77%p임. 신규 Recall 0 조합은 없음.",
        "해석: 가장 큰 회복은 0→5%에서 나타남. 평균 Macro F1의 추가 증가는 "
        "5→10%에서 약1.69%p, 10→20%에서 약0.66%p로 작아짐. "
        "Acetaldehyde Recall과 Ethanol F1 등 일부 지표는 20%가 10%보다 낮아 "
        "모든 클래스 지표의 단조 개선을 뜻하지 않음.",
        "계산값·한계: 과거 유지 진단은 Fold A의 Batch4–5, 358개·5종만 가능함. "
        "평균 Macro F1은 기준94.25%, 5%·10% 교정94.79%, 20% 교정94.71%임. "
        "해당 자료에 Toluene이 없어 그 가스의 과거 유지 성능은 검증 불가함. "
        "Fold B/C에는 적합한 과거 미학습 평가 집합이 없어 유지 성능 결론을 내리지 않음.",
        "연구 결론: 5%·10%·20%는 각각 사전 보호·일관성 기준을 충족하여 A로 판정함. "
        "세 비율 중 공식 채택 비율을 선정한 결과가 아님. 공식 Model A 유지함.",
        "연구 한계: 같은 Batch에서 확보한 정답 일부가 도움이 된다는 근거임. "
        "미관찰 다음 Batch에서도 효과가 유지되거나 센서 드리프트의 독립 효과가 "
        "확인됐다는 증거는 아님. 물리적 센서 교정으로 해석하지 않음.",
        "검증 조건: 전체 Batch 정답을 이용한 층화 표본 구성이며 실제 배포에서 "
        "같은 6종 구성의 라벨을 같은 비용으로 확보할 수 있다는 보장은 없음. "
        "Batch 내 시각 정보가 없어 교정이 평가보다 실제로 선행했다는 주장도 불가함.",
    ])
    text = "\n\n## 계산 결과와 해석 구분\n\n" + "\n\n".join(
        "- " + note for note in notes
    ) + "\n"
    summary_path = ROOT / "reports/temporal_calibration_summary.md"
    summary_path.write_text(summary_path.read_text(encoding="utf-8") + text, encoding="utf-8")
    report_path = ROOT / "reports/temporal_calibration_report.html"
    block = "<h2>12. 핵심 계산값과 해석</h2><ul>" + "".join(
        "<li>" + html.escape(note) + "</li>" for note in notes
    ) + "</ul>"
    report_path.write_text(
        report_path.read_text(encoding="utf-8").replace("</body>", block + "</body>"),
        encoding="utf-8",
    )
    checks = verify()
    model_n = len(list((ROOT / "models/temporal_calibration").glob("*.joblib")))
    assert model_n == 27
    tests = test_summary()
    assert tests["new_failures"] == 0
    write("final_verification.json", {
        **checks,
        "new_adaptive_models": model_n,
        "reused_unique_baseline_models": 3,
        "future_batches_evaluated": [],
        "official_model_unchanged": True,
        "visual_review": ["mean_macro_by_rate.png", "toluene_correct.png"],
        "tests": tests,
        "closed_at": now(),
    })
    print({**checks, "new_models": model_n, "tests": tests})


if __name__ == "__main__":
    main()
