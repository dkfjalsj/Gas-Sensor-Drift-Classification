# 고정 점수의 해석과 최종 테스트·보존 결과 정리
# 추가 적합·점수 계산 없이 기존 CSV만 사용

import html
import json

import pandas as pd

from ..data import ROOT
from ..temporal_expansion import now
from .experiment import OUT, verify, test_summary, write
from .report import render


# 전체 테스트 완료 후 보고서 해석 보완
def main():
    render()
    windows = pd.read_csv(OUT / "window_error_analysis.csv")
    support = pd.read_csv(OUT / "window_gas_support.csv")
    counts = support.groupby(["partition", "window"]).n.apply(lambda x: int((x > 0).sum()))
    class_counts = counts.rename("gas_classes").reset_index()
    class_counts.to_csv(OUT / "window_class_counts.csv", index=False, encoding="utf-8")
    examples = windows[(windows.error_rate == 0) | (windows.error_rate >= .25)].copy()
    examples.to_csv(OUT / "score_error_counterexamples.csv", index=False, encoding="utf-8")
    notes = [
        "관찰: Batch7·8의38개 평가 창이 모두 경고됨. 따라서 대상 자료 안에서 경고와 "
        "비경고의 오류율을 비교할 비경고 집합은 없음. 비경고 오류율을0으로 채우거나 "
        "감지 민감도·특이도·정확도·ROC-AUC를 계산하지 않음.",
        "관찰: 참조 분포 내부 평가 경고율은1/14=7.14%임. 이는 무작위 pooled 기준 "
        "분포 내부의 관찰값이며 실제 정상 센서 오경고율이나5% 보장이 아님.",
        "관찰: Calibration·내부 평가의 모든100행 창에는6종이 존재함. 반면 Batch7은 "
        "36개 창 중30개가2종,2개가3종,4개가4종임. Batch8은2개 창에 각각2종·3종이 "
        "존재함. 전체 Batch의6종 비율만으로 창별 구성 차이를 설명하기 어려움.",
        "해석: pooled 참조와 파일 순서 창의 가스 구성 차이는 경고에 영향을 줄 수 있음. "
        "각 창의 total variation과 점수 사이 단순 상관이 작더라도 구성 영향이 없다고 "
        "결론 내릴 수 없음. 가스별 거리·농도·반응 변화와 비선형 상호작용을 분리하지 못함.",
        "반례: Batch8 창1은 점수0.305474로 임계값을 크게 초과하지만100개 모두 정분류됨. "
        "Batch7 창8은 더 낮은 점수0.057273에서도29개가 오분류됨. 이 경우도 임계값은 "
        "초과했으므로 비경고 실패 사례로 잘못 표현하지 않음.",
        "관찰·해석 구분:38개 창의 점수와 오류율의 Spearman은 약-0.292이며 설명용임. "
        "점수가 클수록 오류가 증가한다는 근거를 보이지 않았고, 음의 인과 효과나 "
        "미래 오류 예측력을 뜻하지 않음. 창의 가스 구성·Batch 영향이 남음.",
        "기술 결론 A의 범위: 라벨 없는 점수·고정 경고·저장 재현·입력 처리·분리 검사를 "
        "갖춘 백엔드 프로토타입 구축임. 모든 대상 창 경고로 인해 선택적인 운영 경보의 "
        "효용은 확인되지 않음. 물리적 드리프트 탐지 정확도나 실제 배포 신뢰성 인증 아님.",
        "다음 단계 제안: 감지 규칙을 현재 결과에 맞춰 바꾸지 말고, 가스 구성과 측정 조건을 "
        "통제한 별도 기준 자료 및 새 시기 자료를 수집해 검증. Streamlit 어댑터의 실제 "
        "실행·배포와 사용자 경고 이해도 검증도 별도 필요함.",
    ]
    text = "\n\n## 경고 해석에서 특히 주의할 결과\n\n" + "\n\n".join("- " + n for n in notes) + "\n"
    summary_path = ROOT / "reports/drift_detection_summary.md"
    summary_path.write_text(summary_path.read_text(encoding="utf-8") + text, encoding="utf-8")
    limits_path = ROOT / "reports/drift_detection_limitations.md"
    limits_path.write_text(limits_path.read_text(encoding="utf-8") + text, encoding="utf-8")
    report_path = ROOT / "reports/drift_detection_report.html"
    section = "<h2>11. 경고 해석의 핵심 반례와 한계</h2><ul>" + "".join(
        "<li>" + html.escape(n) + "</li>" for n in notes) + "</ul>"
    section += class_counts.to_html(index=False) + examples.to_html(index=False)
    report_path.write_text(report_path.read_text(encoding="utf-8").replace("</body>", section + "</body>"), encoding="utf-8")
    tests = test_summary()
    checks = verify()
    assert tests["new_failures"] == 0 and tests["new_passed"] == tests["new_tests"]
    metadata = json.loads((OUT / "detector_metadata.json").read_text(encoding="utf-8"))
    write("final_verification.json", {**checks, "tests": tests,
        "technical_conclusion": "A", "physical_drift_accuracy_verified": False,
        "web_app_executed": False, "threshold": metadata["threshold"],
        "new_detector_artifacts": 1, "visual_review": ["warning_rates.png", "batch7_windows.png", "warning_classifier_error.png"],
        "closed_at": now()})
    print({**checks, "tests": tests, "technical_conclusion": "A"})


if __name__ == "__main__":
    main()
