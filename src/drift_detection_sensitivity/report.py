# 창 구성·가스 비율 통제 결과와 한계를 별도 보고서로 정리
# 원본 감지 점수·임계값·모델 변경 없음

import base64
import html
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..data import ROOT
from .experiment import OUT, CAUTION, REPORTS, SEEDS, THRESHOLD, test_summary, write


# 저장된 표만 읽어 비교 그래프·해석 생성
def render():
    summary = pd.read_csv(OUT / "condition_summary.csv")
    variation = pd.read_csv(OUT / "seed_variability.csv")
    old = pd.read_csv(OUT / "existing_window_analysis.csv")
    associations = pd.read_csv(OUT / "existing_associations.csv")
    available = pd.read_csv(OUT / "controlled_availability.csv")
    quota = pd.read_csv(OUT / "controlled_quota.csv")
    windows = pd.read_csv(OUT / "window_scores.csv")
    plt.rcParams.update({"font.family": "Malgun Gothic", "axes.unicode_minus": False, "figure.dpi": 130})
    figures = []
    meta = (f"고정 임계값={THRESHOLD:.8g} · 창100행 · 시드42~46\n"
            "원본 B7 36창(3,600행), B8 2창(200행) · 구성통제 비교당 B7 14창, B8 1창/출처/시드")

    def finish(name, title, fig):
        fig.suptitle(title + "\n" + meta, fontsize=10)
        fig.tight_layout(rect=[0, 0, 1, .86])
        path = OUT / f"{name}.png"
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        figures.append(dict(name=name, title=title, path=str(path.relative_to(ROOT))))

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, column, label in zip(axes, ["mixture_tv", "gas_classes", "error_rate"],
                                ["기준 대비 가스 비율 TV", "창 내 가스 종류 수", "창 내 분류 오류율"]):
        for part, group in old.groupby("partition"):
            ax.scatter(group[column], group.score, label=f"{part} {len(group)}창", alpha=.65)
        ax.axhline(THRESHOLD, color="red", linestyle="--")
        ax.set(xlabel=label, ylabel="기존 MMD² 점수")
        ax.legend(fontsize=8)
    finish("existing_relationships", "A: 저장된38개 창의 구성·점수·오류 관계 (사후 분석)", fig)
    methods = ["original", "shuffle_all", "shuffle_fixed_rows"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, batch in zip(axes, [7, 8]):
        data = [summary[(summary.target == batch) & (summary.method == m)].mean_score.to_numpy() for m in methods]
        means = [float(d.mean()) for d in data]
        sd = [float(d.std(ddof=1)) if len(d) > 1 else 0 for d in data]
        ax.bar(range(3), means, yerr=sd, capsize=4, color=["#999999", "#4587a6", "#6e9c63"])
        ax.axhline(THRESHOLD, color="red", linestyle="--")
        ax.set(xticks=range(3), xticklabels=["원본", "전체 재배열", "기존 평가 행 재배열"],
               xlabel=f"Batch{batch} 창 구성 방식", ylabel="창 MMD² 평균 (오차막대:시드 SD)")
    finish("window_method_means", "B: 창 구성 방식별 평균 점수 (시드 변동은 독립 환경 반복 아님)", fig)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, batch in zip(axes, [7, 8]):
        for method in ["shuffle_all", "shuffle_fixed_rows"]:
            sub = summary[(summary.target == batch) & (summary.method == method)].sort_values("seed")
            ax.plot(sub.seed, sub.mean_score, marker="o", label=method)
        original = summary[(summary.target == batch) & (summary.method == "original")].mean_score.iloc[0]
        ax.axhline(original, linestyle=":", color="gray", label="원본 평균")
        ax.axhline(THRESHOLD, linestyle="--", color="red", label="고정 임계값")
        ax.set(xticks=SEEDS, xlabel=f"Batch{batch} 재배열 시드", ylabel="창 MMD² 평균")
        ax.legend(fontsize=8)
    finish("seed_stability", "C: 모든 사전 지정 시드의 재배열 결과", fig)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, batch in zip(axes, [7, 8]):
        labels, values = [], []
        for method, source in [("original", "target"), ("shuffle_all", "target"),
                               ("shuffle_fixed_rows", "target"), ("composition_controlled", "internal"),
                               ("composition_controlled", "target")]:
            sub = summary[(summary.target == batch) & (summary.method == method) & (summary.source == source)]
            labels.append(method.replace("composition_controlled", "통제") + "\n" + source)
            values.append(sub.alert_rate.mean() * 100)
        ax.bar(range(len(labels)), values, color="#4587a6")
        ax.set(xticks=range(len(labels)), xticklabels=labels, xlabel=f"Batch{batch} 비교 조건", ylabel="경고율 (%)", ylim=(0, 110))
        ax.tick_params(axis="x", rotation=20, labelsize=7)
    finish("warning_rates", "조건별 경고율: 시드 평균 (원본은 단일 구성)", fig)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, batch in zip(axes, [7, 8]):
        control = summary[(summary.target == batch) & (summary.method == "composition_controlled")]
        for source, group in control.groupby("source"):
            ax.plot(group.seed, group.mean_score, marker="o", label=f"{source}, 창{int(group.windows.iloc[0])}/시드")
        ax.axhline(THRESHOLD, color="red", linestyle="--")
        ax.set(xlabel=f"Batch{batch} 비교 시드", ylabel="동일 가스 할당량 창의 MMD² 평균", xticks=SEEDS)
        ax.legend(fontsize=8)
    finish("composition_control", "B3: 라벨 기반 가스 비율 통제 (운영 평가 아님)", fig)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, batch in zip(axes, [7, 8]):
        sub = summary[(summary.target == batch) & summary.method.isin(["original", "shuffle_fixed_rows"])].copy()
        labels = ["원본" if r.method == "original" else str(r.seed) for r in sub.itertuples()]
        ax.bar(labels, sub.global_mean_distance_squared, label="고정 전체 평균 차이")
        ax.bar(labels, sub.between_window_variation, bottom=sub.global_mean_distance_squared,
               label="창 평균 간 변동")
        ax.set(xlabel=f"Batch{batch} 동일 평가 행 재배열", ylabel="평균 MMD² 분해 (합=창 점수 평균)")
        ax.legend(fontsize=8)
    finish("score_decomposition", "같은 평가 행에서도 창 구성에 따라 달라지는 점수 항", fig)
    fig, ax = plt.subplots(figsize=(11, 5))
    for (method, batch, source), group in summary.groupby(["method", "target", "source"]):
        ax.scatter(group.mean_tv, group.mean_score, label=f"{method}/B{batch}/{source}", alpha=.65)
    ax.set(xlabel="조건별 평균 가스 비율 TV", ylabel="조건별 평균 MMD²")
    ax.legend(fontsize=6, bbox_to_anchor=(1, 1))
    finish("composition_score_comparison", "통제 전후 가스 비율 차이와 점수 (반복 자료·비인과 비교)", fig)
    save_path = OUT / "graph_manifest.csv"
    pd.DataFrame(figures).to_csv(save_path, index=False, encoding="utf-8")

    notes = [CAUTION,
        "A 분석은 기존38개 창의 저장 점수·경고·오류율을 그대로 재사용함. "
        "가스 비율 차이는 TV=0.5Σ|p_window−p_reference|로 계산함.",
        "B2 전체 재배열은 원본 잔여 행 일부가 평가에 들어가고 다른 행이 제외될 수 있음. "
        "따라서 순서만의 효과라고 해석하지 않음. 보조 조건은 기존 평가3,600/200행과 "
        "제외13/94행을 고정해 창 구성 변화만 비교함.",
        "구성 통제는 정답 라벨로 창을 만드는 사후 진단이며 감지기에 라벨을 전달하지 않음. "
        "Reference 비율의100행 할당량은 " + ", ".join(f"{r.gas}:{r.quota}" for r in quota.itertuples()) + "임.",
        "같은 출처·시드·비교 안에서는 복제 없이 추출함. 시드 간 및 서로 다른 비교에서는 "
        "같은 원본 행이 재사용될 수 있으므로 독립 반복이나 신뢰구간으로 취급하지 않음.",
        "구성 통제의 내부 비교 자료는 기존 INTERNAL 평가 풀임. Reference와 임계값 산정 풀의 "
        "행은 통제 평가 창에 포함하지 않았음. 내부 풀은 여러 과거 Batch 혼합이며 대상 창은 "
        "각 Batch 내부에서만 구성함.",
        "전체 평균 RFF 차이와 창 간 변동의 합은 창 평균 MMD²와 같음. 동일 행 조건의 재배열은 "
        "전체 평균 차이를 유지하면서 창 간 변동을 바꿀 수 있음. 전체 평균 차이에100행 임계값을 "
        "직접 적용하지 않았음.",
        "경고 점수·구성·오류의 상관은 기술 통계이며 시기·농도·환경의 독립 효과를 구분하지 못함. "
        "상관이 약해도 가스 구성 영향이 없다는 증거가 아님. 높은 점수도 분류 실패의 보장은 아님.",
        "웹앱에서는 '설정된 참조와 다른 센서 측정 분포'로 표시해야 함. 드리프트 발생 확률·장비 "
        "고장·예상 정확도로 표시하지 말 것. 입력100행의 가스 구성과 배열에 민감할 수 있고, "
        "경고가 없어도 분류 정확도를 보장하지 않음을 안내할 필요가 있음.",
        "19단계 통합이나 기존 경고 문구·감지기 수정은 이번에 수행하지 않음. 실제 운영 전 "
        "입력 창 수집 규칙과 기준 가스 구성의 적합성을 정하고 별도 신규 자료로 검증 필요함. "
        "현재 결과로 임계값·창 크기·최적 시드를 재선정하지 않았음.",
        "시험 제한: 과거 전체 데이터 테스트의 Batch9~10 원본 읽기와 기존 산출물 쓰기를 "
        "감사 훅으로 차단함. 제한으로 건너뛴 검사는 통과가 아니며 상세 기록은 test_summary.json과 "
        "test_access_blocks.json 참조. 이번 보존 검사는 원본1~8만 재검증하며9~10은 열지 않았음.",
    ]
    comparisons = []
    for batch in [7, 8]:
        base = summary[(summary.target == batch) & (summary.method == "original")].iloc[0]
        for method in ["shuffle_all", "shuffle_fixed_rows", "composition_controlled"]:
            current = summary[(summary.target == batch) & (summary.method == method) & (summary.source == "target")]
            if current.empty:
                continue
            mean = float(current.mean_score.mean())
            comparisons.append(dict(target=batch, method=method, original_mean=base.mean_score,
                mean_score=mean, mean_delta=mean - base.mean_score,
                relative_mean_change=(mean / base.mean_score - 1),
                original_alert_rate=base.alert_rate, mean_alert_rate=float(current.alert_rate.mean())))
    pd.DataFrame(comparisons).to_csv(OUT / "method_deltas.csv", index=False, encoding="utf-8")
    for row in available.itertuples():
        notes.append(f"구성 통제 B{row.target}: 대상 최대{row.target_capacity}창, "
            f"내부 최대{row.internal_capacity}창, 출처마다{row.selected_windows_per_source}창 "
            f"({row.selected_rows}행) 사용. 대상 미선택{row.target_unselected}행, 내부 미선택{row.internal_unselected}행. "
            "특히1창 조건은 평가 불확실성이 큼.")
    for row in comparisons:
        notes.append(f"계산값 B{row['target']} {row['method']}: 평균 점수{row['mean_score']:.6g}, "
            f"원본 대비{row['relative_mean_change'] * 100:+.2f}%, 시드 평균 경고율{row['mean_alert_rate'] * 100:.2f}%.")
    for row in associations.itertuples():
        if row.scope == "pooled_7_8":
            notes.append(f"기존38창 사후 Spearman: score vs {row.variable}={row.spearman:.3f}. 인과·예측력 주장 없음.")
    tests = test_summary()
    complete = bool(available.available.all()) and len(available) == 2 and len(summary) == 42
    conclusion = ("A — 감지기 민감도와 교란 요인 정량 설명" if complete and tests.get("new_failures") == 0
                  and tests.get("new_tests", 0) == tests.get("new_passed", -1) else "테스트 완료 전 잠정 결과")
    notes.insert(1, "최종 판정: " + conclusion + ". 실제 드리프트 감지 정확도나 원인의 독립 분리 성공을 뜻하지 않음.")
    write("research_conclusion.json", dict(conclusion=conclusion, conditions_complete=complete,
        drift_accuracy_validated=False, causal_effect_identified=False, webapp_modified=False))
    text = "# 18.5단계 가스 구성·창 구성 민감도 진단\n\n" + "\n\n".join("- " + n for n in notes)
    text += "\n\n## 조건별 결과\n\n```text\n" + summary.to_string(index=False) + "\n```\n"
    text += "\n## 시드 변동\n\n```text\n" + variation.to_string(index=False) + "\n```\n"
    text += "\n## 전체 테스트\n\n```json\n" + json.dumps(tests, ensure_ascii=False, indent=2) + "\n```\n"
    (ROOT / "reports" / REPORTS[1]).write_text(text, encoding="utf-8")
    sections = []

    def section(title, content):
        sections.append("<h2>" + html.escape(title) + "</h2>" + content)

    section("1. 목적·고정 계획", "<p>" + CAUTION + "</p><pre>" + html.escape(
        (OUT / "protocol.md").read_text(encoding="utf-8")) + "</pre>")
    section("2. A: 기존 경고와 가스 구성·오류", old.to_html(index=False) + associations.to_html(index=False))
    section("3. B: 창 구성 방식 비교", pd.DataFrame(comparisons).to_html(index=False) + summary.to_html(index=False))
    section("4. B3: 구성 통제와 표본 한계", quota.to_html(index=False) + available.to_html(index=False) +
        pd.read_csv(OUT / "controlled_support.csv").to_html(index=False))
    section("5. C: 모든 시드의 변동성", variation.to_html(index=False) + pd.read_csv(OUT / "paired_row_checks.csv").to_html(index=False))
    section("6. 비교 그래프", "".join("<figure><img alt='" + html.escape(fig["title"]) +
        "' src='data:image/png;base64," + base64.b64encode((ROOT / fig["path"]).read_bytes()).decode("ascii") +
        "'><figcaption>" + html.escape(fig["title"]) + "</figcaption></figure>" for fig in figures))
    section("7. 관찰·해석·웹앱 전 검토 사항", "<ul>" + "".join("<li>" + html.escape(n) + "</li>" for n in notes) + "</ul>")
    section("8. 테스트·접근 제한·보존", "<pre>" + html.escape(json.dumps(tests, ensure_ascii=False, indent=2)) +
        "</pre><p>기존 모델·보고서·해시 기록 수정 없음. 원본9~10은 보존 해시 검사에서도 열지 않음. "
        "신규 모델 저장·재학습·19단계 통합·Commit·Push 없음.</p>")
    document = ("<!doctype html><html lang='ko'><meta charset='utf-8'><title>18.5단계 감지 민감도 진단</title>"
        "<style>body{font-family:Malgun Gothic,sans-serif;color:#172536;margin:32px}h2{margin-top:32px}"
        "table{border-collapse:collapse;display:block;overflow:auto;font-size:12px}td,th{border:1px solid #bbc;padding:6px}"
        "pre{white-space:pre-wrap;overflow-wrap:anywhere}img{max-width:100%;height:auto}</style>"
        "<body><h1>고정 감지기의 가스 구성·창 구성 민감도 진단</h1>" + "".join(sections) + "</body></html>")
    (ROOT / "reports" / REPORTS[0]).write_text(document, encoding="utf-8")
