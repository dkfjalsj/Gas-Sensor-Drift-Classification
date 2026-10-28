# 추론 서비스와 분리한 Streamlit 산업형 분석 화면
# 업로드별 메모리 상태만 유지하며 학습·모델 교체 기능 없음

import hashlib

import altair as alt
import pandas as pd
import streamlit as st

from .service import (
    MODEL_PATH, DETECTOR_PATH, FEATURES, GASES, THRESHOLD, WARNING, NORMAL,
    InputError, load_models, read_upload, analyze, downloads, reset_on_upload_change,
)

PAGES = ["프로젝트 대시보드", "센서 데이터 업로드", "가스 분류 결과",
         "분포 변화 감지", "통합 분석 결과", "결과 다운로드"]


# 파일 버전이 바뀌면 캐시를 다시 확인하고 모델만 공유
@st.cache_resource(show_spinner="검증된 모델을 불러오는 중입니다…")
def cached_models(model_signature, detector_signature):
    return load_models()


# 정적 화면 스타일 적용
def style():
    st.markdown("""<style>
    .stApp {background:#f4f7fb;color:#17283b}
    [data-testid="stSidebar"] {background:#102336}
    [data-testid="stSidebar"] * {color:#e9f1f8}
    [data-testid="stSidebar"] button *,[data-testid="stSidebar"] input {color:#17283b}
    [data-testid="stFileUploaderDropzone"] * {color:#17283b!important}
    [data-testid="stSidebar"] button[kind="primary"] {background:#117c8b;border-color:#117c8b}
    [data-testid="stSidebar"] button[kind="primary"] * {color:white!important}
    .block-container {padding-top:2rem;max-width:1450px}
    h1,h2,h3 {letter-spacing:-.035em}
    [data-testid="stMetric"] {background:white;border:1px solid #dce5ef;border-radius:12px;padding:16px}
    [data-testid="stMetricLabel"] {color:#52677d}
    [data-testid="stMetricValue"] {font-size:28px!important}
    [data-testid="stMetricLabel"] p {white-space:normal!important;overflow:visible!important}
    .hero {background:#102b42;color:white;border-radius:16px;padding:28px 30px;margin-bottom:24px}
    .hero h1 {color:white;font-size:30px;margin:8px 0}
    .hero p {color:#c3d5e7;margin:4px 0}
    .eyebrow {font-size:12px;letter-spacing:2px;color:#63d8ca}
    div[data-testid="stAlert"] {border-radius:10px}
    @media (max-width:1100px) {
      .st-key-result_metrics [data-testid="stHorizontalBlock"],
      .st-key-dashboard_metrics [data-testid="stHorizontalBlock"] {display:grid;grid-template-columns:repeat(2,minmax(0,1fr))}
      .st-key-result_metrics [data-testid="stColumn"],
      .st-key-dashboard_metrics [data-testid="stColumn"] {width:auto!important;min-width:0}
      .st-key-integrated_charts [data-testid="stHorizontalBlock"] {display:grid;grid-template-columns:1fr}
      .st-key-integrated_charts [data-testid="stColumn"] {width:auto!important;min-width:0}
    }
    @media (max-width:650px) {
      .st-key-result_metrics [data-testid="stHorizontalBlock"],
      .st-key-dashboard_metrics [data-testid="stHorizontalBlock"] {grid-template-columns:1fr}
    }
    </style>""", unsafe_allow_html=True)


# 공통 분석 요약 카드
def result_metrics(result):
    summary = result["summary"]
    with st.container(key="result_metrics"):
        a, b, c, d = st.columns(4)
        a.metric("분류한 측정값", f"{summary['input_rows']:,}행")
        b.metric("예측된 가스", f"{summary['predicted_classes']}종")
        c.metric("유효한 감지 창", f"{summary['valid_windows']}개")
        d.metric("분포 경고 창", f"{summary['alert_windows']}개")


# 예측된 가스의 개수 시각화
def gas_chart(result):
    chart = alt.Chart(result["counts"]).mark_bar(color="#167c91", cornerRadiusTopLeft=4,
        cornerRadiusTopRight=4).encode(
        x=alt.X("gas:N", title="예측 가스", sort=list(GASES.values())),
        y=alt.Y("n:Q", title="측정값 수"),
        tooltip=[alt.Tooltip("gas:N", title="가스"), alt.Tooltip("n:Q", title="개수"),
                 alt.Tooltip("proportion:Q", title="예측 비율", format=".1%")],
    ).properties(height=280, title="가스별 예측 분포")
    st.altair_chart(chart, width="stretch")


# 고정 임계값과 창별 점수를 별도 표시
def drift_chart(result):
    table = result["windows"]
    valid = table[table.score.notna()]
    if valid.empty:
        st.info("표시할 유효 감지 점수가 없습니다.")
        return
    base = alt.Chart(valid).encode(
        x=alt.X("window:Q", title="창 번호 (입력 행 순서)", axis=alt.Axis(tickMinStep=1)),
        y=alt.Y("score:Q", title="RFF-MMD² 점수", scale=alt.Scale(zero=True)),
        tooltip=[alt.Tooltip("window:Q", title="창"), alt.Tooltip("start_position:Q", title="시작 행"),
                 alt.Tooltip("end_position:Q", title="끝 행"),
                 alt.Tooltip("score:Q", title="MMD²", format=".7f"), alt.Tooltip("status:N", title="상태")],
    )
    line = base.mark_line(color="#167c91", point=True)
    alerts = base.transform_filter(alt.datum.alert == True).mark_point(color="#d77330", size=100)
    rule = alt.Chart(pd.DataFrame({"threshold": [THRESHOLD]})).mark_rule(
        color="#c43d49", strokeDash=[6, 4]).encode(
        y="threshold:Q", tooltip=[alt.Tooltip("threshold:Q", title="고정 임계값", format=".12f")])
    st.altair_chart((line + alerts + rule).properties(height=280, title="창별 분포 변화 점수 · 빨간 점선은 고정 임계값"), width="stretch")


# 사용자 해석과 평가 불가 사유 안내
def drift_notice(result):
    drift = result["drift"]
    if drift["status"] == "분포 변화 감지":
        st.warning(WARNING)
    elif drift["status"] == "평가 불가":
        st.info("분포 변화 평가 불가: " + drift.get("reason", "유효한100행 창이 없습니다."))
        st.caption("가스 분류는 별도로 수행됐습니다. 100행 미만 입력도 행별 예측은 가능합니다.")
    else:
        st.info(NORMAL)
    if drift.get("invalid_windows", 0):
        st.warning(f"{drift['invalid_windows']}개 창은 평가할 수 없습니다. 창별 이유를 확인해 주세요.")
    st.caption("MMD²는 분포 차이의 점수이며 확률이나 예상 정확도가 아닙니다. "
               "창은 입력 순서의100개 측정값이며 실제 시간 길이를 뜻하지 않습니다.")


# 정답이 있을 때만 별도 평가 영역 표시
def optional_evaluation(result):
    evaluation = result["evaluation"]
    if evaluation is None:
        st.info("정답 gas 열이 없어 실제 Accuracy·Macro F1을 계산하지 않았습니다.")
        return
    st.subheader("업로드 정답에 대한 별도 평가")
    st.caption("사용자가 제공한 정답과 이번 예측의 비교입니다. 독립 Test나 새로운 연구 성능 검증이 아닙니다.")
    a, b = st.columns(2)
    a.metric("Accuracy · 업로드 정답 기준", f"{evaluation['accuracy']:.2%}")
    b.metric(f"Macro F1 · 정답의{evaluation['supported_classes']}종", f"{evaluation['macro_f1']:.2%}")
    if evaluation["supported_classes"] < 6:
        st.warning("정답에 일부 가스가 없습니다. 이 Macro F1을6종 전체 성능으로 해석하지 마세요.")
    matrix = evaluation["confusion"].rename_axis("실제 가스").reset_index().melt(
        id_vars="실제 가스", var_name="예측 가스", value_name="개수")
    heat = alt.Chart(matrix).encode(
        x=alt.X("예측 가스:N", sort=list(GASES.values())),
        y=alt.Y("실제 가스:N", sort=list(GASES.values())),
        tooltip=["실제 가스:N", "예측 가스:N", "개수:Q"])
    st.altair_chart((heat.mark_rect().encode(color=alt.Color("개수:Q", scale=alt.Scale(scheme="blues"))) +
                    heat.mark_text(color="#17283b").encode(text="개수:Q")).properties(height=300, title="Confusion Matrix"), width="stretch")
    st.dataframe(evaluation["per_class"], hide_index=True, width="stretch")


# 모델 정보와 연구 한계를 한 곳에 표시
def model_notes():
    with st.expander("모델 정보와 검증 범위", expanded=False):
        st.write("분류: 공식 Model A · B_SVM_balanced · SVM(RBF), Batch1–6 학습")
        st.write("분포 감지: rff_mmd_v1 · RFF512차원 · 고정 참조·고정100행 창")
        st.code(f"고정 임계값: {THRESHOLD}")
        st.write("18.5단계에서 Batch7–8은 비교 조건의 대상 창 모두 경고됐으며, "
                 "Batch7은 같은 평가 행의 재배열만으로 평균 점수가 약59.66% 낮아졌습니다. "
                 "점수와 분류 오류율의 일관된 양의 관계는 확인되지 않았습니다.")
        st.write("가스 구성·평가 창 구성·측정 조건의 영향을 구분해야 합니다. "
                 "실제 물리적 센서 드리프트 탐지 정확도는 검증되지 않았습니다. "
                 "과거 Batch9–10도 반복 사용한 회고적 자료이며 독립 Test가 아닙니다.")
        st.caption("예측 신뢰 확률은 제공하지 않습니다. 이 앱은 추론 전용이며 재학습·모델 자동 교체 기능이 없습니다.")


# 업로드별 상태 관리 및 여섯 화면 연결
def main():
    st.set_page_config(page_title="Gas Sensor Intelligence", page_icon="◈", layout="wide")
    style()
    with st.sidebar:
        st.markdown("### GAS SENSOR\nINTELLIGENCE")
        st.caption("가스 분류 · 측정 분포 확인")
        page = st.radio("분석 화면", PAGES, key="page")
        st.divider()
        upload = st.file_uploader("센서 데이터 CSV", type=["csv"], key="sensor_csv", max_upload_size=20,
            help="f001~f128 필수, gas 정답은 선택. UTF-8 CSV,20MB·20,000행 이하.")
        payload = upload.getvalue() if upload is not None else None
        digest = hashlib.sha256(payload).hexdigest() if payload is not None else None
        reset_on_upload_change(st.session_state, digest)
        submitted = st.button("분석 실행", key="analyze", type="primary", disabled=upload is None, width="stretch")
        st.caption("업로드는 분석 세션 메모리에서만 처리합니다. 파일을 바꾸면 이전 분석 결과를 비웁니다.")
    st.markdown("<div class='hero'><span class='eyebrow'>SENSOR ANALYTICS / RESEARCH PROTOTYPE</span>"
                "<h1>가스 분류 및 측정 분포 분석</h1><p>가스 예측과 분포 변화를 구분해 확인하는 추론 전용 대시보드</p></div>", unsafe_allow_html=True)
    try:
        signature = tuple((p.stat().st_mtime_ns, p.stat().st_size) for p in [MODEL_PATH, DETECTOR_PATH])
        models = cached_models(*signature)
    except (OSError, RuntimeError, ValueError) as exc:
        st.error("모델을 사용할 수 없습니다: " + str(exc))
        return
    if submitted:
        st.session_state.pop("analysis", None)
        try:
            with st.spinner("입력을 확인하고 저장 모델로 분석 중입니다…"):
                data = read_upload(payload)
                st.session_state["analysis"] = analyze(data, models)
                st.session_state.pop("analysis_error", None)
        except InputError as exc:
            st.session_state["analysis_error"] = str(exc)
        except (ValueError, RuntimeError, OverflowError) as exc:
            st.session_state["analysis_error"] = "분석을 완료하지 못했습니다. 센서 수치 범위와 입력 형식을 확인해 주세요."
    if "analysis_error" in st.session_state:
        st.error(st.session_state["analysis_error"])
    result = st.session_state.get("analysis")
    st.subheader(page)
    if page == PAGES[0]:
        with st.container(key="dashboard_metrics"):
            a, b, c, d = st.columns(4)
            a.metric("공식 분류 모델", "Model A")
            b.metric("분류 대상", "6종 가스")
            c.metric("입력 특징", "128개")
            d.metric("분포 감지 단위", "100행")
        left, right = st.columns(2)
        with left:
            st.markdown("#### 가스 종류 예측")
            st.write("검증된 저장 SVM이 각 측정값을6종 가스 중 하나로 분류합니다. 정답 없이 예측할 수 있습니다.")
            st.success("공식 Model A · 로딩 완료 · 추론 전용")
        with right:
            st.markdown("#### 기준 분포와 비교")
            st.write("고정 RFF-MMD² 감지기가100개 측정값의 분포를 기존 참조와 비교합니다. 가스 정답은 사용하지 않습니다.")
            st.info("분포 감지기 · 로딩 완료 · 고정 임계값")
        st.markdown("#### 사용 순서")
        st.write("① 왼쪽에서 CSV 업로드 → ② 분석 실행 → ③ 각 결과 화면 확인 → ④ CSV 다운로드")
    elif page == PAGES[1]:
        st.write("필수 열은 f001~f128입니다. 선택적 gas 정답은1~6 정수로 입력하며 별도 평가에만 사용합니다.")
        st.caption("가스 매핑:1 Ethanol ·2 Ethylene ·3 Ammonia ·4 Acetaldehyde ·5 Acetone ·6 Toluene")
        st.info("열 순서만 다르면 이름으로 재정렬합니다. 알 수 없는 열·중복 열·비수치·무한대·전체 결측은 거부합니다. "
                "일부 결측값은 각 저장 파이프라인의 기존 학습 중앙값으로 처리하며 자동 재학습하지 않습니다.")
        if payload is None:
            st.write("왼쪽 업로드 영역에서 파일을 선택해 주세요.")
        else:
            try:
                preview = read_upload(payload)
                st.success(f"입력 검증 완료 · {len(preview.features):,}행 · 정답 {'있음' if preview.truth is not None else '없음'}")
                st.caption(f"결측 특징값 {preview.missing_cells}개 · 특징 순서 재정렬 {'수행' if preview.reordered else '불필요'}")
                st.dataframe(preview.features.head(8), width="stretch")
                if result is None:
                    st.write("입력 확인 후 왼쪽의 분석 실행을 눌러 주세요.")
            except InputError as exc:
                st.error(str(exc))
    elif result is None:
        st.info("CSV를 업로드하고 분석 실행을 누르면 이 화면에 결과가 표시됩니다.")
    elif page == PAGES[2]:
        result_metrics(result)
        gas_chart(result)
        st.dataframe(result["counts"], hide_index=True, width="stretch")
        selected = st.number_input("확인할 입력 행", min_value=1, max_value=len(result["rows"]), value=1, step=1)
        st.dataframe(result["rows"].iloc[[int(selected) - 1]], hide_index=True, width="stretch")
        with st.expander("전체 행별 예측 결과"):
            st.dataframe(result["rows"], hide_index=True, width="stretch")
        optional_evaluation(result)
    elif page == PAGES[3]:
        drift_notice(result)
        result_metrics(result)
        summary = result["summary"]
        a, b, c = st.columns(3)
        a.metric("경고율 · 유효 창 기준", "평가 불가" if summary["alert_rate"] is None else f"{summary['alert_rate']:.1%}")
        b.metric("제외 잔여 행", f"{summary['excluded_tail_rows']}행")
        c.metric("고정 임계값", f"{THRESHOLD:.8f}")
        st.caption(f"고정 임계값 전체 값: {THRESHOLD} · 평가 불가 창 {summary['invalid_windows']}개")
        drift_chart(result)
        st.dataframe(result["windows"], hide_index=True, width="stretch")
    elif page == PAGES[4]:
        result_metrics(result)
        drift_notice(result)
        with st.container(key="integrated_charts"):
            a, b = st.columns(2)
            with a:
                gas_chart(result)
            with b:
                drift_chart(result)
        st.write("분포 경고가 가스 예측을 자동으로 무효화하지 않습니다. 필요시 기준 가스 측정과 모델 재검증을 검토해 주세요.")
        st.caption("가스 분류와 분포 변화 감지는 서로 다른 기능입니다. 라벨 제공 여부가 감지 점수나 예측값을 바꾸지 않습니다.")
    elif page == PAGES[5]:
        st.write("파일에는 모델 버전·지문·입력 파일 지문과 분석 조건이 포함됩니다. 행 번호는 업로드 순서를 유지합니다.")
        for name, data in downloads(result).items():
            st.download_button({"gas_classification.csv": "행별 가스 분류 CSV", "distribution_windows.csv": "창별 분포 변화 CSV",
                                "analysis_summary.csv": "분석 요약 CSV"}[name], data=data, file_name=name,
                               mime="text/csv", key="download_" + name, on_click="ignore", width="stretch")
        st.caption("100행 미만이면 창별 CSV는 제목 행만 포함하며, 평가 불가 이유는 분석 요약 CSV에 기록됩니다.")
        st.dataframe(pd.DataFrame([result["summary"]]), hide_index=True, width="stretch")
    model_notes()
    st.divider()
    st.caption("연구용 프로토타입 · 실제 센서 고장·물리적 드리프트 원인을 확정하지 않음 · 관리자 재학습·자동 모델 교체 미구현")


if __name__ == "__main__":
    main()
