# 등록 데이터셋 선택·명시적 후보 학습·검토 결과 표시
# 운영 모델 승인·교체 버튼은 제공하지 않음

import hashlib
import json

import altair as alt
import pandas as pd
import streamlit as st

from ..data import GASES
from ..webapp.data_preparation import LOCAL_ROOT
from .candidates import STORE, list_candidates, read_candidate, train_candidate
from .datasets import list_datasets, load_training_data

DATA_STORAGE = LOCAL_ROOT
CANDIDATE_STORAGE = STORE


# 다른 데이터셋의 검사·결과가 화면에 남지 않도록 초기화
def reset_candidate_state(state, token):
    if state.get('candidate_selection_token') == token:
        return False
    for key in ['candidate_check', 'candidate_receipt', 'candidate_contract',
                'candidate_history', 'candidate_roc_gas']:
        state.pop(key, None)
    state['candidate_selection_token'] = token
    return True


# 지표 변화와 평가의 한계를 함께 표시
def render_result(item):
    meta = item['metadata']
    st.subheader('기존 모델과 후보 비교')
    if meta['synthetic_only']:
        st.warning('합성 기능 검증용 결과입니다. 실제 센서 성능 개선을 검증하지 않았습니다.')
    official, candidate = meta['metrics']['official'], meta['metrics']['candidate']
    a, b, c = st.columns(3)
    a.metric('기존 Macro F1', f"{official['macro_f1']:.2%}")
    b.metric('후보 Macro F1', f"{candidate['macro_f1']:.2%}",
             f"{100 * meta['review']['macro_f1_delta']:+.2f}%p")
    c.metric('동일 검증 표본', f"{meta['validation_rows']:,}개")
    st.write(meta['review']['observed_outcome'])
    st.info(meta['review']['assessment'] + ' · 자동 승인·교체하지 않습니다.')
    for reason in meta['review']['assessment_reasons']:
        st.caption(reason)
    drops = meta['review']['severe_recall_drop_gases']
    if drops:
        st.warning('Recall이5%p 초과 하락한 가스: ' + ', '.join(drops))
    st.caption('5%p는 손실을 눈에 띄게 알리는 진단 기준이며20-C 승인 기준이 아닙니다.')
    st.dataframe(item['metrics'].rename(columns={
        'model': '모델', 'accuracy': 'Accuracy', 'macro_f1': 'Macro F1',
        'weighted_f1': 'Weighted F1', 'rows': '검증 표본 수'}),
        hide_index=True, width='stretch')
    st.subheader('가스별 Recall·Precision·F1·표본 수')
    st.dataframe(item['class_changes'].rename(columns={
        'gas': '가스', 'support': '정답 표본 수', 'official_recall': '기존 Recall',
        'candidate_recall': '후보 Recall', 'recall_delta': 'Recall 차이',
        'official_f1': '기존 F1', 'candidate_f1': '후보 F1'}),
        hide_index=True, width='stretch')
    for name, label in [('official', '기존 Model A'), ('candidate', '후보 SVM')]:
        sub = item['confusion'][item['confusion'].model.eq(name)]
        matrix = sub.pivot(index='actual_gas', columns='predicted_gas', values='n')
        matrix = matrix.rename(index=GASES, columns=GASES)
        st.write(label + ' Confusion Matrix · 행: 실제 / 열: 예측')
        st.dataframe(matrix, width='stretch')
    with st.expander('보조 ROC/AUC · 확률이 아닌 결정점수'):
        st.caption('클래스별 One-vs-Rest 순위 평가입니다. Macro F1·Recall을 대체하거나 예측 임계값을 바꾸지 않습니다.')
        st.dataframe(item['roc_auc'], hide_index=True, width='stretch')
        curves = item['roc_points']
        if not curves.empty:
            gas = st.selectbox('ROC를 확인할 가스', list(GASES),
                               format_func=lambda value: GASES[value], key='candidate_roc_gas')
            sub = curves[curves.gas_id.eq(gas)]
            chart = alt.Chart(sub).mark_line().encode(
                x=alt.X('fpr:Q', title='False Positive Rate', scale=alt.Scale(domain=[0, 1])),
                y=alt.Y('tpr:Q', title='True Positive Rate', scale=alt.Scale(domain=[0, 1])),
                color=alt.Color('model:N', title='모델'), tooltip=['model:N', 'fpr:Q', 'tpr:Q'],
            ).properties(title=GASES[gas] + ' · 신규Validation OvR ROC', height=320)
            st.altair_chart(chart, width='stretch')
    with st.expander('후보 저장·전처리·학습 정보'):
        st.write('후보ID: ' + meta['candidate_id'])
        st.write('생성 시각(UTC): ' + meta['created_at_utc'])
        st.write('데이터셋ID: ' + meta['dataset_id'])
        st.write('후보 경로: ' + str(item['directory'] / 'model.joblib'))
        st.write('평가 경로: ' + str(item['directory']))
        st.code(meta['candidate_model_sha256'])
        st.json(meta)
    st.download_button('후보 비교표 CSV 다운로드',
                       item['class_changes'].to_csv(index=False).encode('utf-8-sig'),
                       file_name='candidate_class_comparison.csv', mime='text/csv',
                       key='candidate_comparison_download', on_click='ignore')


def render_candidates():
    st.button('등록 데이터셋 목록 새로고침', key='candidate_refresh')
    st.subheader('후보 모델 학습·비교 (20-B)')
    st.caption('20-A 등록 데이터만 사용합니다. 공식 모델과 감지기는 유지하며 후보를 자동 승인·교체하지 않습니다.')
    try:
        rows = list_datasets(DATA_STORAGE)
    except OSError as exc:
        st.error('데이터셋 저장소 확인 실패: ' + str(exc))
        return
    if not rows:
        st.info('등록된 실제 신규 데이터셋이 없습니다. 아래20-A에서 데이터 검증·고정 분리를 먼저 완료해 주세요.')
        st.button('후보 모델 학습 시작', key='candidate_train', disabled=True)
        return
    lookup = {row['dataset_id']: row for row in rows}
    dataset_id = st.selectbox('준비된 데이터셋', list(lookup), key='candidate_dataset')
    row = lookup[dataset_id]
    if row['error']:
        reset_candidate_state(st.session_state, dataset_id + ':invalid')
        st.error('무결성 확인 실패: ' + row['error'])
        st.button('후보 모델 학습 시작', key='candidate_train', disabled=True)
        return
    manifest = row['manifest']
    token = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    reset_candidate_state(st.session_state, token)
    st.write('데이터셋ID: ' + dataset_id)
    st.write('출처: ' + manifest['provenance']['source'])
    st.write('실제 정답 확인 방식: ' + manifest['provenance']['truth_method'])
    st.write(manifest['partition_rows'])
    st.dataframe(pd.DataFrame(manifest['quality']['sessions']), hide_index=True, width='stretch')
    support = pd.DataFrame({part: manifest['quality'][part + '_counts'] for part in ['train', 'validation']})
    support.index = [GASES[int(value)] for value in support.index]
    st.dataframe(support, width='stretch')
    if st.button('재학습 조건 다시 검사', key='candidate_validate'):
        try:
            with st.spinner('원본·분리·세션·기존5933행 중복 재검증 중…'):
                check = load_training_data(dataset_id, DATA_STORAGE)
            st.session_state['candidate_check'] = check.manifest_sha
            st.success('원본 지문과 시간순 분리 조건 재검증 통과')
        except (OSError, ValueError, KeyError) as exc:
            st.session_state.pop('candidate_check', None)
            st.error('재학습 보류: ' + str(exc))
    compatible = st.checkbox('128개 특징의 정의·순서·측정 단위가 기존 공식 학습 자료와 같음을 별도로 확인했습니다.',
                             key='candidate_contract')
    st.caption('이 확인은 소프트웨어의 단위 검증이나 물리적 독립성 증명이 아닙니다. 다르면 학습하지 마세요.')
    busy = st.session_state.get('candidate_busy', False)
    allowed = bool(st.session_state.get('candidate_check')) and compatible and not busy
    if st.button('후보 모델 학습 시작', key='candidate_train', disabled=not allowed, type='primary'):
        st.session_state['candidate_busy'] = True
        status = st.empty()
        try:
            with st.spinner('고정 설정으로 후보 하나를 학습·검증 중…'):
                item = train_candidate(dataset_id, feature_contract_confirmed=True,
                                       dataset_storage=DATA_STORAGE, candidate_storage=CANDIDATE_STORAGE,
                                       progress=status.info)
            st.session_state['candidate_receipt'] = item['metadata']['candidate_id']
            st.success('동일 요청의 기존 후보를 재사용했습니다.' if item['reused'] else '후보 저장 완료 · 공식 모델은 유지합니다.')
        except Exception as exc:
            st.error('후보 학습·저장 실패: ' + str(exc))
        finally:
            st.session_state['candidate_busy'] = False
            status.empty()
    try:
        saved = list_candidates(CANDIDATE_STORAGE, dataset_id)
        valid = [item for item in saved if 'error' not in item]
        for item in saved:
            if 'error' in item:
                st.error('후보 이력 확인 실패: ' + item['error'])
        if valid:
            choices = {item['metadata']['candidate_id']: item for item in valid}
            selected = st.selectbox('저장된 후보 이력', list(choices), key='candidate_history')
            render_result(choices[selected])
    except (OSError, ValueError, KeyError) as exc:
        st.error('후보 결과 확인 실패: ' + str(exc))
    st.divider()
