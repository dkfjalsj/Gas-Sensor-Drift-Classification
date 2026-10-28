# 로컬 관리자용 정답 데이터 검사·세션 분리·등록 화면
# 모델 학습·승인·교체 기능은 제공하지 않음

import hashlib
import json

import altair as alt
import pandas as pd
import streamlit as st

from ..data import GASES
from .data_preparation import inspect_candidate, load_training_reference
from .dataset_registry import identity, register_dataset, check_reservations, LOCAL_ROOT

NAMES = ["에탄올", "에틸렌", "암모니아", "아세트알데하이드", "아세톤", "톨루엔"]


# 입력 변경 시 이전 검사와 등록 결과 폐기
def reset_preparation(state, token):
    if state.get("preparation_token") != token:
        state.pop("preparation_check", None)
        state.pop("preparation_receipt", None)
        state.pop("preparation_accepted", None)
        state["preparation_token"] = token
        return True
    return False


# 일반 분석과 별도 업로드·상태로 데이터 준비
def render_management():
    st.info("로컬 관리자용 데이터 준비 화면입니다. 사용자 인증은 제공하지 않습니다. 이번 단계에서는 재학습하지 않습니다.")
    st.caption("데이터 업로드 → 품질 검사 → 구성 확인 → 세션별 분리 → 불변 버전 저장")
    upload = st.file_uploader("신규 실제 정답 CSV", type=["csv"], key="preparation_csv", max_upload_size=20)
    session_file = st.file_uploader("행별 세션 정보 CSV", type=["csv"], key="preparation_sessions", max_upload_size=20)
    payload = upload.getvalue() if upload else None
    session_payload = session_file.getvalue() if session_file else None
    file_token = hashlib.sha256((payload or b"") + (session_payload or b"")).hexdigest()
    if st.session_state.get("preparation_file_token") != file_token:
        st.session_state.pop("preparation_confirmed", None)
        st.session_state["preparation_file_token"] = file_token
    with st.expander("등록 파일 형식 안내"):
        st.write("센서 CSV: f001~f128, gas 필수. gas는 1~6 실제 정답입니다. AI 예측값을 정답으로 등록하지 마세요.")
        st.write("세션 CSV: input_row, session_id, measured_at. 모든 측정 번호에 세션과 시간대가 있는 실제 시각이 필요합니다.")
        st.code("input_row,session_id,measured_at\n1,session_01,2026-10-28T09:00:00+09:00")
        st.caption("시각 예시는 형식 안내입니다. 실제 수집 시각을 입력하세요. 한 세션·시기 누락·기간 겹침이면 준비를 보류합니다.")
    source = st.text_input("데이터 출처", key="preparation_source", placeholder="측정 장비·기관·실험 식별 정보")
    method = st.text_input("실제 정답 확인 방식", key="preparation_truth", placeholder="기준 가스 시험·별도 검증 기록 등")
    confirmed = st.checkbox("AI 예측이 아닌 실제 시험·별도 확인으로 확보한 정답임을 확인합니다.", key="preparation_confirmed")
    payload = upload.getvalue() if upload else None
    session_payload = session_file.getvalue() if session_file else None
    token = hashlib.sha256(json.dumps({"file": hashlib.sha256(payload or b"").hexdigest(),
                                      "sessions": hashlib.sha256(session_payload or b"").hexdigest(),
                                      "source": source, "method": method, "confirmed": confirmed,
                                      "filename": upload.name if upload else None},
                                     sort_keys=True).encode()).hexdigest()
    reset_preparation(st.session_state, token)
    if st.button("데이터 품질 검사", key="preparation_inspect", disabled=payload is None, type="primary"):
        with st.spinner("입력과 기존 학습 자료의 중복 확인 중…"):
            try:
                reference = load_training_reference()
                reference_problem = None
            except (OSError, ValueError, KeyError) as exc:
                reference, reference_problem = None, str(exc)
            check = inspect_candidate(payload, session_payload, source, method, confirmed, reference)
            if reference_problem:
                check.holds.append("기존 학습 자료 확인 실패: " + reference_problem)
            if check.ready:
                try:
                    check.holds.extend(check_reservations(check, identity(payload, session_payload, source, method)[0], source))
                except (OSError, ValueError, KeyError) as exc:
                    check.holds.append("이전 데이터 등록 이력을 확인할 수 없습니다: " + str(exc))
            st.session_state["preparation_check"] = check
    check = st.session_state.get("preparation_check")
    if check is None:
        st.write("실제 정답과 세션 정보를 준비한 뒤 품질 검사를 눌러 주세요.")
        return
    if check.errors:
        st.error("데이터 검증 실패")
        for message in check.errors:
            st.error(message)
    elif check.warnings:
        st.warning("품질 경고 존재 · 관리자 확인 필요")
    else:
        st.success("데이터 형식·품질 검사 통과")
    for warning in check.warnings:
        st.warning(warning)
    for hold in check.holds:
        st.info("분리 조건 미충족 · " + hold)
    if check.summary:
        summary = check.summary
        st.subheader("데이터 구성 확인")
        st.write(f"총 {summary['rows']:,}개의 측정값을 검사했습니다. 실제 정답 열이 포함되어 있습니다.")
        a, b = st.columns(2)
        a.metric("결측 특징값", f"{summary['missing_cells']:,}개", help=f"전체 특징값 중 {summary['missing_fraction']:.3%}")
        b.metric("중복 추가 행", f"{summary['duplicate_extra']:,}개")
        counts = pd.DataFrame({"가스": NAMES, "표본 수": [summary['gas_counts'][str(g)] for g in GASES]})
        counts["비율"] = counts["표본 수"] / summary["rows"]
        st.altair_chart(alt.Chart(counts).mark_bar(color="#167c91").encode(
            x=alt.X("표본 수:Q", title="측정 샘플 수"),
            y=alt.Y("가스:N", title=None, sort=NAMES, axis=alt.Axis(labelLimit=0)),
            tooltip=["가스:N", "표본 수:Q", alt.Tooltip("비율:Q", format=".1%")],
        ).properties(height=260), width="stretch")
        st.dataframe(counts, hide_index=True, width="stretch")
        if "sessions" in summary:
            st.write("등록된 수집 세션과 실제 측정 기간")
            st.dataframe(pd.DataFrame(summary["sessions"]).rename(columns={
                "session_id": "세션", "min": "첫 측정 시각 (UTC)", "max": "마지막 측정 시각 (UTC)"}),
                hide_index=True, width="stretch")
        if check.assignments is not None:
            st.subheader("학습·검증 고정 계획")
            st.write("최신 한 세션을 검증용, 나머지 과거 세션을 학습용으로 고정합니다. 비율을 임의로 바꾸지 않습니다.")
            table = check.assignments.groupby(["partition", "session_id", "gas"]).size().rename("표본 수").reset_index()
            st.dataframe(table.rename(columns={"partition": "분리", "session_id": "세션", "gas": "가스 ID"}),
                         hide_index=True, width="stretch")
        with st.expander("품질·중복 검사 기술 정보"):
            st.json(summary)
            st.caption("정확 수치와 유효숫자 12자리 근접 검사를 수행합니다. 반올림·가공·미신고 출처의 모든 중복을 증명할 수는 없습니다.")
    accepted = st.checkbox("품질 경고와 출처 확인의 한계를 검토했습니다.", key="preparation_accepted")
    allowed = check.ready and (not check.warnings or accepted)
    if st.button("고정 분리 데이터셋 저장", key="preparation_save", disabled=not allowed):
        try:
            manifest, created = register_dataset(payload, session_payload, upload.name, source, method,
                                                  confirmed, accepted, storage=LOCAL_ROOT)
            st.session_state["preparation_receipt"] = manifest
            st.success("데이터 준비 완료" if created else "동일한 불변 데이터셋이 이미 등록되어 있습니다.")
        except (OSError, ValueError, KeyError) as exc:
            st.error("저장 보류: " + str(exc))
    receipt = st.session_state.get("preparation_receipt")
    if receipt:
        st.success("데이터 준비 완료 · 재학습은 수행하지 않았습니다.")
        st.write("데이터셋 버전: " + receipt["dataset_id"])
        st.write(receipt["partition_rows"])
        st.caption("원본·세션·분리 행 목록·Train/Validation CSV와 지문을 로컬에 저장했습니다. 독립 최종 Test는 아닙니다.")
    elif check.ready:
        st.info("분리 조건 확인 완료 · 경고 확인 후 저장해야 준비가 완료됩니다.")
    with st.expander("후속 단계와 사용 범위"):
        st.write("20-B는 저장된 Train에서만 전처리와 후보 모델을 학습해야 합니다. Validation은 개발용으로 예약되며 최종 Test가 아닙니다.")
        st.caption("원본 데이터와 출처는 Git 제외 경로에 저장합니다. 외부에 공개하려면 별도 인증·접근 제어가 필요합니다.")
