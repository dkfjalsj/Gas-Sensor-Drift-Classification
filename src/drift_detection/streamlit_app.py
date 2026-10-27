# CSV 감지 서비스를 표시하는 선택형 Streamlit 화면
# 저장된 감지기만 사용하며 추가 적합 없음

from pathlib import Path

import pandas as pd

from src.drift_detection.detector import evaluate_csv, load_detector


# 라벨 없는128특징 CSV 업로드 및 경고 표시
def main():
    import streamlit as st

    st.set_page_config(page_title="센서 측정 분포 확인", layout="wide")
    st.title("센서 측정 분포 확인")
    st.caption("분포 변화는 센서 고장이나 가스 분류 성능 저하를 확정하지 않습니다.")
    st.write("f001~f128의 센서 특징만 포함한 CSV를 올려 주세요. "
             "최소100개 측정값이 필요하며, 마지막100개 미만은 제외합니다.")
    path = Path(__file__).resolve().parents[2] / "models/drift_detection/rff_mmd_v1.joblib"
    if not path.is_file():
        st.error("저장된 기준 감지기를 찾을 수 없습니다.")
        return
    source = st.file_uploader("센서 데이터 CSV", type=["csv"])
    if source is None:
        return
    result = evaluate_csv(load_detector(path), source)
    state = result["status"]
    display = st.warning if state == "분포 변화 감지" else st.info
    display(result["message"])
    if state == "평가 불가":
        st.caption(result.get("reason", "입력 자료를 확인해 주세요."))
        return
    st.write(f"평가 창 {result['valid_windows']}개 · "
             f"경고 {result['alert_windows']}개 · 제외 잔여 행 {result['excluded_tail_rows']}개")
    st.dataframe(pd.DataFrame(result["windows"]), hide_index=True)
    st.caption("점수는 분포 차이의 크기이며 정확도나 드리프트 발생 확률이 아닙니다.")


if __name__ == "__main__":
    main()
