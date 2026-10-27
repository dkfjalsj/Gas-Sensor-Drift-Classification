# 고정 감지 결과와 사후 오류 분석을 표·그래프로 정리
# 임계값 변경 없이 기술적 성공과 연구 한계 구분

import base64
import html
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..data import ROOT
from .experiment import OUT, CAUTION, REPORT_NAMES, test_summary, write


# 저장 결과만으로 보고서와 그래프 생성
def render():
    summary = pd.read_csv(OUT / "partition_summary.csv").set_index("partition")
    windows = pd.read_csv(OUT / "windows.csv")
    composition = pd.read_csv(OUT / "gas_composition.csv")
    errors = pd.read_csv(OUT / "window_error_analysis.csv")
    comparisons = pd.read_csv(OUT / "warning_error_comparison.csv")
    association = pd.read_csv(OUT / "associations.csv")
    batch_metrics = pd.read_csv(OUT / "batch_classifier_metrics.csv")
    support = pd.read_csv(OUT / "window_gas_support.csv")
    metadata = json.loads((OUT / "detector_metadata.json").read_text(encoding="utf-8"))
    threshold = metadata["threshold"]
    plt.rcParams.update({"font.family": "Malgun Gothic", "axes.unicode_minus": False,
                         "figure.dpi": 130, "axes.titlesize": 11})
    figures = []
    info = (f"참조 n={metadata['reference_n']}, 창=100행, 임계값={threshold:.6g}\n"
            "Calibration14창·내부14창·Batch7 36창·Batch8 2창 (잔여 행 제외)")

    def finish(name, title, fig):
        fig.suptitle(title + "\n" + info, fontsize=11)
        fig.tight_layout(rect=[0, 0, 1, .88])
        path = OUT / f"{name}.png"
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        figures.append(dict(name=name, title=title, path=str(path.relative_to(ROOT))))

    fig, ax = plt.subplots(figsize=(10, 5))
    calibration = windows[windows.partition == "calibration"]
    ax.hist(calibration.score, bins=7, color="#4587a6", edgecolor="white")
    ax.axvline(threshold, color="#bf3b40", linestyle="--", label="95백분위수")
    ax.set(xlabel="RFF-MMD² 점수 (확률 아님)", ylabel="창 수")
    ax.legend()
    finish("calibration_distribution", "임계값 산정 자료의 점수 분포 (n=1,400 사용·83행 제외)", fig)
    for batch in [7, 8]:
        part = f"batch{batch}"
        sub = windows[windows.partition == part]
        fig, ax = plt.subplots(figsize=(11, 5))
        ax.plot(sub.window, sub.score, marker="o", label=f"Batch{batch} 점수")
        ax.axhline(threshold, color="#bf3b40", linestyle="--", label="고정 임계값")
        ax.set(xlabel="파일 행 순서 기반 창 번호 (실제 시간 아님)", ylabel="RFF-MMD² 점수")
        ax.legend()
        n = int(summary.loc[part, "input_rows"])
        dropped = int(summary.loc[part, "excluded_tail_rows"])
        finish(f"batch{batch}_windows", f"Batch{batch}: 입력{n}행·{len(sub)}창·잔여{dropped}행 제외", fig)
    fig, ax = plt.subplots(figsize=(10, 5))
    selected = summary.loc[["calibration", "internal", "batch7", "batch8"]]
    bars = ax.bar(selected.index, selected.alert_rate * 100,
                  color=["#999999", "#4587a6", "#da7747", "#6e9c63"])
    for bar, row in zip(bars, selected.itertuples()):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f"{int(row.alert_windows)}/{int(row.valid_windows)}창\nn={int(row.valid_windows) * 100}",
                ha="center", fontsize=9)
    ax.set(xlabel="자료 구분 (Calibration은 임계값 산정용)", ylabel="임계값 초과 창 비율 (%)", ylim=(0, 115))
    finish("warning_rates", "기준 분포 내부 경고율과 개발 Batch 경고율", fig)
    fig, ax = plt.subplots(figsize=(10, 5))
    parts = ["calibration", "internal", "batch7", "batch8"]
    ax.boxplot([windows[windows.partition == p].score for p in parts], tick_labels=parts)
    ax.axhline(threshold, color="#bf3b40", linestyle="--", label="고정 임계값")
    ax.set(xlabel="자료 구분", ylabel="RFF-MMD² 점수")
    ax.legend()
    finish("score_comparison", "자료별 점수 분포 (Batch8은2개 창)", fig)
    fig, ax = plt.subplots(figsize=(11, 5))
    mixture = composition.pivot(index="partition", columns="gas", values="proportion").loc[
        ["reference", "calibration", "internal", "batch7", "batch8"]]
    mixture.plot.bar(stacked=True, ax=ax, colormap="tab10", rot=0)
    ax.set(xlabel="자료 구분 (전체 입력 행 기준)", ylabel="가스 정답 비율 (사후 분석)")
    ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
    finish("gas_composition", "사후 확인한 가스 구성: Reference2966·Cal1483·내부1484·B7 3613·B8 294행", fig)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for part, sub in errors.groupby("partition"):
        axes[0].scatter(sub.score, sub.error_rate * 100, label=f"{part} {len(sub)}창", alpha=.75)
    axes[0].axvline(threshold, color="#bf3b40", linestyle="--")
    axes[0].set(xlabel="RFF-MMD² 점수", ylabel="창 내 분류 오류율 (%)")
    axes[0].legend()
    pooled = comparisons[comparisons.scope == "pooled_7_8"]
    names = [f"{'경고' if r.alert else '비경고'}\n{r.windows}창, n={r.rows}" for r in pooled.itertuples()]
    axes[1].bar(names, pooled.error_rate * 100, color="#4587a6")
    axes[1].set(xlabel="경고 상태 (사용된3,800행만)", ylabel="행 가중 분류 오류율 (%)")
    finish("warning_classifier_error", "고정 감지 점수와 저장된 공식 SVM 오류의 사후 관계", fig)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].bar(summary.index, summary.excluded_tail_rows, color="#999999")
    axes[0].set(xlabel="자료 구분", ylabel="100행 미만으로 제외된 행 수")
    axes[0].tick_params(axis="x", rotation=20)
    low = support.groupby(["partition", "window"]).n.apply(lambda x: int((x > 0).sum())).reset_index(name="classes")
    for part in parts:
        group = low[low.partition == part]
        axes[1].bar(part, int((group.classes < 6).sum()), label=part)
    axes[1].set(xlabel="자료 구분", ylabel="실제6종을 모두 포함하지 않는 창 수")
    finish("unsupported_windows", "입력 부족·클래스 support 한계 (유효하지 않은 창은 별도 표)", fig)
    pd.DataFrame(figures).to_csv(OUT / "graph_manifest.csv", index=False, encoding="utf-8")
    notes = [CAUTION,
        "관찰: 기준 후보 Batch1–6의5,933행을 라벨 없이 무작위 분리함. Reference2,966행, "
        "Calibration1,483행, 내부 평가1,484행. Reference에만 중앙값·평균·표준편차·커널 폭 적합.",
        f"계산값: sigma²={metadata['median_squared_distance']:.8g}, gamma={metadata['gamma']:.8g}, "
        f"고정 임계값={threshold:.8g}. Calibration14창의95백분위수이며 미래 경고율5% 보장 아님.",
        "한계: Calibration과 내부 평가는 여러 과거 Batch를 무작위로 섞은 pooled 분포의 창임. "
        "Batch7–8은 파일 순서의 창이므로 가스 비율·행 순서·측정 조건 차이가 함께 반영될 수 있음. "
        "기준 자체에도 시간 변화가 있고 무노화 정상 상태 정답은 없음.",
        "한계: 같은 Reference를 공유해 창별 점수가 통계적으로 의존함. Calibration14창과 "
        "내부14창은 적고, Batch8은 전체294행 중200행·2창만 평가하며94행을 제외함. "
        "Batch8 경고율 한 창의 변화는50%p임. 이 자료로 정밀한 오경고율이나 재현율을 추정하지 않음.",
        "관찰과 해석 구분: 가스 구성 비율과 분류 오류는 감지기·점수를 저장하고 해시로 잠근 뒤 "
        "정답과 기존 예측을 결합해 계산함. 정답으로 감지기·임계값을 수정하지 않았음. "
        "Window의 실제 클래스 수를 공개하고 창 Macro F1을6종 전체 성능처럼 해석하지 않음.",
        "연관성 한계: 경고·비경고 오류율은 가스 구성·Batch·측정 조건의 교란이 있음. "
        "Spearman은 설명용이며 독립 관측의 유의성이나 향후 오류 예측력을 주장하지 않음. "
        "Batch가2개뿐이므로 Batch 평균2점의 상관계수는 산출하지 않음.",
        "운영 해석: 경고는 기준 가스 측정·모델 재검증의 검토 신호임. 경고가 없어도 분류 정확도를 "
        "보장하지 않으며, 경고가 있어도 센서 고장·노후화·분류 실패를 확정하지 않음.",
        "메타데이터 한계: 현재 .dat에는 정답과128개 특징만 있음. Batch와 source_line은 파일에서 "
        "파생한 정보이며 정확한 측정 시각·농도·환경·개별 측정 센서 식별 정보가 없음. "
        "고정 특징 묶음의 센서 번호는 행별 장치 식별자나 물리적 원인 증거가 아님.",
        "구현 범위: CSV 서비스는128개 특징 이름을 확인하고 순서만 다르면 재정렬함. 추가 열·" 
        "중복 열·비수치·무한대·전체 결측은 평가 불가. 일부 결측만 Reference 중앙값으로 처리. "
        "실제 Streamlit은 설치·실행하지 않았고, 선택형 화면 어댑터와 백엔드 CSV 경계를 제공함.",
        "웹앱 실행: Streamlit을 별도 설치한 환경에서 프로젝트 루트의 "
        "python -m streamlit run src/drift_detection/streamlit_app.py 사용. "
        "실제 배포 검증·경고의 업무 적합성 검증은 다음 단계임.",
        "재실행: python -B -m src.drift_detection.experiment freeze → run → 전체pytest → report. "
        "freeze/run은 기존 경로 또는 실행 흔적이 있으면 거부하며 추가 실험 없이 report만 갱신 가능.",
        "다음 검증: 새 시기의 라벨 없는 입력으로 고정 감지기를 적용하고 별도 기준 가스·환경·" 
        "정답 자료를 독립 수집해 경고 해석과 운영 비용 검토. 가스 구성 통제 조건과 무통제 "
        "조건을 구분하고, 향후 임계값 버전 변경 시 새 독립 자료로 검증 필요.",
    ]
    for part, row in summary.iterrows():
        notes.append(f"계산값: {part}: {int(row.valid_windows)}창, 평균{row.mean_score:.6g}, "
                     f"중앙값{row.median_score:.6g}, 최대{row.max_score:.6g}, "
                     f"경고{int(row.alert_windows)}창({row.alert_rate * 100:.2f}%), "
                     f"잔여{int(row.excluded_tail_rows)}행 제외.")
    for row in comparisons[comparisons.scope == "pooled_7_8"].itertuples():
        notes.append(f"사후 계산값: {'경고' if row.alert else '비경고'} {row.windows}창 "
                     f"{row.rows}행 중 오류{row.errors}개({row.error_rate * 100:.2f}%). "
                     "경고가 오류를 일으켰거나 오류를 예측한다고 해석하지 않음.")
    tests = test_summary()
    conclusion = "A — 운영 가능한 감지 프로토타입" if tests.get("new_failures") == 0 else "테스트 완료 전 잠정 결과"
    notes.insert(1, "결론: " + conclusion + ". 기술적인 구축·검증 판정이며 실제 드리프트 탐지 정확도의 판정이 아님.")
    write("research_conclusion.json", dict(conclusion=conclusion,
        physical_drift_accuracy_verified=False, web_deployment_verified=False,
        independent_test=False, detector_version=metadata["version"]))
    limits = "# 18단계 연구 한계\n\n" + "\n\n".join("- " + note for note in notes if
        note.startswith(("한계", "연관성", "메타데이터", "구현 범위", "운영", "다음")) or note == CAUTION) + "\n"
    summary_text = ("# 18단계 비지도 분포 변화 감지\n\n" + "\n\n".join("- " + note for note in notes) +
        "\n\n## 상세 요약\n\n```text\n" + summary.to_string() +
        "\n```\n\n## 사후 분류 오류 비교\n\n```text\n" + comparisons.to_string(index=False) +
        "\n```\n\n## 전체 테스트\n\n```json\n" + json.dumps(tests, ensure_ascii=False, indent=2) + "\n```\n")
    (ROOT / "reports" / REPORT_NAMES[1]).write_text(summary_text, encoding="utf-8")
    (ROOT / "reports" / REPORT_NAMES[2]).write_text(limits, encoding="utf-8")
    sections = []

    def section(title, content):
        sections.append("<h2>" + html.escape(title) + "</h2>" + content)

    section("1. 목적·기존 연구와 달라진 점", "<p>16단계 HGB 평균 Macro F1 66.10%는 SVM보다 낮았으며, "
            "17단계는 새 시기 라벨을 추가해 개발 평균 Macro F1 80.24→92.26→93.94→94.61%로 회복됨. "
            "이번에는 분류 모델을 학습하지 않고 라벨 없는 분포 변화 경고 기능만 개발함.</p><p>" + CAUTION + "</p>")
    section("2. 분석 전 고정 계획", "<pre>" + html.escape((OUT / "protocol.md").read_text(encoding="utf-8")) + "</pre>")
    section("3. 기준 분리·입력·누수 검사", pd.read_csv(OUT / "overlap_checks.csv").to_html(index=False) +
            pd.read_csv(OUT / "input_audit.csv").to_html(index=False) + "<p>분할 ID는 split_assignments.csv 참조. "
            "참조와 Calibration·내부 평가 모두 서로 다른 행이며 정답 층화 없음.</p>")
    section("4. 감지기·임계값·경고 결과", "<pre>" + html.escape(json.dumps(metadata, ensure_ascii=False, indent=2)) +
            "</pre>" + summary.to_html() + pd.read_csv(OUT / "alert_runs.csv").to_html(index=False))
    section("5. Window별 감지 결과", windows.to_html(index=False))
    section("6. 가스 구성 및 support 사후 진단", composition.to_html(index=False) + support.to_html(index=False))
    section("7. 분류 성능과의 사후 관계", "<p>Batch 지표는 전체 입력 행, 창 오류율은 잔여 제외3,800행임. "
            "둘의 표본 수가 다름. 경고로 분류 실패를 예측한다는 결론 불가.</p>" +
            batch_metrics.to_html(index=False) + pd.read_csv(OUT / "class_classifier_metrics.csv").to_html(index=False) +
            comparisons.to_html(index=False) + association.to_html(index=False) + errors.to_html(index=False))
    section("8. 그래프", "".join("<figure><img alt='" + html.escape(fig["title"]) +
            "' src='data:image/png;base64," + base64.b64encode((ROOT / fig["path"]).read_bytes()).decode("ascii") +
            "'><figcaption>" + html.escape(fig["title"]) + "</figcaption></figure>" for fig in figures))
    section("9. 관찰·해석·운영 한계", "<ul>" + "".join("<li>" + html.escape(note) + "</li>" for note in notes) + "</ul>")
    section("10. 테스트·보존·재현", "<pre>" + html.escape(json.dumps(tests, ensure_ascii=False, indent=2)) +
            "</pre><p>기존5개 역사적 실패와 신규 실패 구분. 원본10개 및 기존324개 모델·기존 파일의 "
            "지문은 preservation_audit.csv 참조. 저장 후 창 점수 재로딩 일치. 기존 해시·테스트 수정 없음. Commit·Push 없음.</p>")
    document = ("<!doctype html><html lang='ko'><meta charset='utf-8'><title>18단계 비지도 분포 변화 감지</title>"
        "<style>body{font-family:Malgun Gothic,sans-serif;margin:32px;color:#172536}h2{margin-top:34px}"
        "table{border-collapse:collapse;display:block;overflow:auto;font-size:12px}td,th{border:1px solid #bbc;padding:6px}"
        "img{max-width:100%;height:auto}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style>"
        "<body><h1>비지도 센서 분포 변화 감지 및 경고</h1>" + "".join(sections) + "</body></html>")
    (ROOT / "reports" / REPORT_NAMES[0]).write_text(document, encoding="utf-8")
