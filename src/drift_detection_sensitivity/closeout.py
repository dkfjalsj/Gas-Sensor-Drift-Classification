# 저장 결과만으로 최종 해석·테스트·보존 기록 마무리
# 감지 점수 재계산이나 모델 적합 없음

import html
import json

import pandas as pd

from ..data import ROOT
from ..temporal_expansion import now
from .access_guard import install
from .experiment import OUT, test_summary, verify, write
from .report import render


# 완료된 실험의 해석과 제한 사항 반영
def main():
    install()
    render()
    notes = [
        "핵심 관찰: 원본·전체 재배열·평가 행 고정 재배열·가스 구성 통제의 대상 창 모두 "
        "경고율100%를 유지함. 이번 범위에서 경고 여부는 안정적이지만 점수 크기는 창 구성에 민감함.",
        "계산값: Batch7 원본 평균0.100152가 전체 재배열0.040685(-59.38%), 동일 평가 행 "
        "재배열0.040398(-59.66%)로 감소함. Batch8은0.228156에서 각각0.204938(-10.18%), "
        "0.209090(-8.36%)로 감소함. 전체 재배열은 제외 행도 달라질 수 있어 두 조건을 구분함.",
        "계산값: 전체 재배열5개 시드의 평균 점수 범위는 Batch7 0.040583~0.040922, "
        "Batch8 0.201160~0.208915임. 유리한 시드를 선택하지 않았으며 시드 SD는 독립 미래 "
        "환경의 불확실성 추정치가 아님.",
        "계산값: 동일 가스 할당량 창의 대상/내부 평균은 Batch7 0.028181/0.003155, "
        "Batch8 0.222819/0.002360임. 내부 출처의 시드 평균 경고율은 각각5.71%/0%, "
        "대상은 모두100%임. Batch7은 출처마다14창, Batch8은1창을 사용했으며 반복 시드의 "
        "표본이 겹칠 수 있어70개 또는5개의 독립 새 표본이라고 해석하지 않음.",
        "해석: 가스 구성·창 구성을 통제해도 대상과 내부 기준의 차이가 남음. 따라서 기존 "
        "100% 경고를 가스 구성만의 결과라고 설명할 수 없지만, 남은 차이가 물리적 센서 "
        "드리프트라고 확정할 수도 없음. 조건 통제는 선택 표본도 바꾸며 농도·환경·시기별 "
        "가스 내 반응 차이를 분리하지 못함.",
        "해석: 동일 평가 행 재배열에서 전체 평균 RFF 차이는 유지됐고 창 간 변동 항이 "
        "줄었음. 이 수학적 분해는 창 묶음에 대한 점수 민감도를 설명하며 드리프트의 "
        "인과 효과를 추정한 결과가 아님.",
        "사후 관계: 기존38창에서 점수와 가스 비율 TV·가스 종류 수의 Spearman은 모두 "
        "약0이며, 점수와 분류 오류율은 약-0.292임. 관찰 상관이 작다는 사실로 구성 영향을 "
        "배제하지 않음. 점수 크기를 분류 오류의 일관된 순위나 정확도 예측값으로 쓰는 "
        "근거도 확보하지 못함.",
        "웹앱 전 검토: '설정된 참조와 다른 측정 분포'라는 의미와 가스 구성·창 구성의 "
        "영향을 화면에 명시할 필요가 있음. 실제 고장 경보나 분류 성능 경보로 사용하려면 "
        "입력 창 수집 규칙과 운영 목적에 맞춘 별도 검증이 필요함. 이번에는 기존 코드·문구·"
        "임계값 수정 및19단계 통합을 하지 않았음.",
        "테스트 해석:143개 통과·2개 역사적 실패·89개 접근 제한 건너뜀. 신규15개 모두 통과. "
        "기존 실패5개 중2개는 그대로 재현됐고3개는 Batch9~10 접근이 필요한 검사여서 "
        "건너뜀. 건너뜀은 해결이나 통과가 아님. 실패2개는 과거 누락 임시 파일과 고정 모델 "
        "목록 검사임. 기존 기준이나 과거 해시 기록은 수정하지 않았음.",
        "보존 범위: 기존325개 모델과 기존 코드·산출물의 SHA-256이 유지됨. 원본1~8을 "
        "재검증했고9~10은 읽기 금지에 따라 해시 재검증도 하지 않았음. 테스트에서32번의 "
        "금지 원본 접근 시도를 파일 열기 전에 차단했고 이 제한이89개 건너뜀에 반영됨.",
    ]
    text = "\n\n## 최종 관찰과 해석\n\n" + "\n\n".join("- " + n for n in notes) + "\n"
    md = ROOT / "reports/drift_detection_sensitivity_report.md"
    md.write_text(md.read_text(encoding="utf-8") + text, encoding="utf-8")
    report = ROOT / "reports/drift_detection_sensitivity_report.html"
    section = "<h2>9. 최종 관찰·운영 해석·검증 범위</h2><ul>" + "".join(
        "<li>" + html.escape(note) + "</li>" for note in notes) + "</ul>"
    report.write_text(report.read_text(encoding="utf-8").replace("</body>", section + "</body>"), encoding="utf-8")
    tests = test_summary()
    assert tests["new_failures"] == 0 and tests["new_tests"] == tests["new_passed"] == 15
    checks = verify()
    conclusion = json.loads((OUT / "research_conclusion.json").read_text(encoding="utf-8"))
    assert conclusion["conclusion"].startswith("A")
    files = list(OUT.rglob("*")) + [md, report]
    files += list((ROOT / "src/drift_detection_sensitivity").glob("*.py"))
    files += [ROOT / "tests/test_drift_detection_sensitivity.py"]
    pd.DataFrame({"path": [str(p.relative_to(ROOT)) for p in files if p.is_file()]}).to_csv(
        OUT / "artifact_manifest.csv", index=False, encoding="utf-8")
    write("final_verification.json", {**checks, "tests": tests, "tests_pending": False,
        "conclusion": "A", "physical_drift_accuracy_validated": False,
        "webapp_integration_performed": False,
        "visual_review": ["window_method_means.png", "composition_control.png", "score_decomposition.png"],
        "closed_at": now()})
    print({**checks, "passed": tests["passed"], "failed": tests["failed"],
           "skipped": tests["skipped"], "new_passed": tests["new_passed"], "conclusion": "A"})


if __name__ == "__main__":
    main()
