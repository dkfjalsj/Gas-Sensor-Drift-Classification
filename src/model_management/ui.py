# 로컬 사용자 확인·동일 검증 비교·수동 적용·이전 버전 복구 화면
# 로그인·인증된 관리자 표시나 자동 승인 기능은 제공하지 않음

import json

import pandas as pd
import streamlit as st

from ..data import GASES
from ..retraining.candidates import list_candidates
from .registry import ModelRegistry
from .runtime import load_bundle

MANAGER_FACTORY = ModelRegistry


# 기존 분석 결과는 지우지 않고 승인 화면의 오래된 확인만 초기화
def reset_review(state, token):
    if state.get('approval_scope') != token:
        for key in ['approval_review', 'approval_confirm']:
            state.pop(key, None)
        state['approval_scope'] = token


def render_comparison(review):
    st.dataframe(pd.DataFrame([
        dict(model='현재 운영 모델', **review['current'][0]),
        dict(model='후보 모델', **review['candidate'][0]),
    ])[['model', 'accuracy', 'macro_f1', 'weighted_f1', 'rows']],
        hide_index=True, width='stretch')
    st.dataframe(review['changes'], hide_index=True, width='stretch')
    drops = review['changes'].query('recall_delta < 0').gas.tolist()
    if drops:
        st.warning('Recall이 하락한 가스: ' + ', '.join(drops))
    for label, key in [('현재 운영 모델', 'current'), ('후보 모델', 'candidate')]:
        st.write(label + ' · 혼동행렬 (행: 실제 / 열: 예측)')
        st.dataframe(pd.DataFrame(review[key][2], index=list(GASES.values()),
                                  columns=list(GASES.values())), width='stretch')
    for reason in review['reasons']:
        st.warning(reason)
    if review['eligible']:
        st.info('단순 승인 조건 충족 · 독립 최종 성능 검증이나 운영 안전성 인증은 아닙니다.')


def render_operations():
    st.subheader('운영 모델 승인·버전·복구 (20-C)')
    st.caption('로컬 포트폴리오용 수동 확인입니다. 승인자의 신원을 인증하지 않습니다.')
    manager = MANAGER_FACTORY()
    if manager.testing:
        st.warning('테스트 전용 임시 운영 환경 · 실제 운영 모델에 적용되지 않습니다.')
    try:
        state = manager.read()
    except Exception as exc:
        st.error('운영 매니페스트 확인 실패 · 자동 복구하지 않습니다: ' + str(exc))
        return
    active = state['active']
    st.write('현재 운영 모델: ' + active['model']['name'])
    st.write('버전: ' + active['version_id'])
    st.write('적용 시각 (UTC): ' + active['applied_at_utc'])
    st.code('모델 SHA-256: ' + active['model']['model_sha256'])
    st.caption('원본 Model A 여부: ' + str(active['model']['kind'] == 'official'))
    try:
        manager.validate_version(active)
    except Exception as exc:
        st.error('현재 모델 무결성 오류 · 새 분석은 차단됩니다. 정상 이력으로 복구하세요: ' + str(exc))

    st.markdown('#### 후보 선택과 승인')
    rows = list_candidates(manager.candidates)
    valid = []
    for row in rows:
        if 'error' in row:
            st.error('후보 확인 실패: ' + row['error'])
        else:
            valid.append(row)
    if not valid:
        st.info('승인할 등록 후보가 없습니다. 합성 기능 검증 후보는 운영 목록에 포함하지 않습니다.')
        st.button('후보 모델 승인 및 적용', key='approval_apply', disabled=True)
    else:
        lookup = {row['metadata']['candidate_id']: row['metadata'] for row in valid}
        st.dataframe(pd.DataFrame([
            dict(candidate_id=meta['candidate_id'], created_at_utc=meta['created_at_utc'],
                 dataset_id=meta['dataset_id'], status=meta['status'], synthetic_only=meta['synthetic_only'],
                 approval_status=('실운영 불가: 합성 후보' if meta['synthetic_only']
                                  else '동일 Validation·확인 근거 재검사 필요'),
                 validation_macro_f1=meta['metrics']['candidate']['macro_f1'])
            for meta in lookup.values()
        ]), hide_index=True, width='stretch')
        selected = st.selectbox('승인 검토 후보', list(lookup), key='approval_candidate')
        meta = lookup[selected]
        if meta['synthetic_only']:
            st.warning('합성 후보는 실제 운영에 적용할 수 없습니다.')
        st.caption('측정·정답·독립성을 확인할 수 없다면 적용하지 마세요. 입력 근거는 자기신고로 기록됩니다.')
        evidence, checks = {}, []
        for key, label in [('source', '실제 측정 데이터 출처'), ('truth', '실제 가스 정답 확인'),
                           ('independence', '검증 세션의 물리적 독립성 확인')]:
            checks.append(st.checkbox(label + ' 완료', key='approval_' + key + '_checked'))
            evidence[key] = st.text_input(label + ' 근거 (10자 이상)', key='approval_' + key)
        evidence = evidence if all(checks) else None
        reset_review(st.session_state, json.dumps([active, selected, evidence], sort_keys=True))
        if st.button('동일 Validation 승인 조건 검사', key='approval_validate'):
            try:
                with st.spinner('데이터셋·학습 분리·예측 재현·동일 Validation 비교 중…'):
                    st.session_state['approval_review'] = manager.review(selected, evidence)
            except Exception as exc:
                st.session_state.pop('approval_review', None)
                st.error('승인 보류: ' + str(exc))
        review = st.session_state.get('approval_review')
        if review:
            render_comparison(review)
        confirmed = st.checkbox(
            '현재 운영 모델을 선택한 후보 모델로 변경합니다. 기존 모델은 보존되며 이전 버전으로 복구할 수 있습니다.',
            key='approval_confirm')
        if st.button('후보 모델 승인 및 적용', key='approval_apply', type='primary',
                     disabled=not (review and review['eligible'] and confirmed)):
            try:
                manager.activate(selected, confirmed=confirmed, evidence=evidence,
                                 expected_version=active['version_id'], comparison_token=review['token'],
                                 preflight=lambda version: load_bundle(version, manager))
                st.session_state.pop('approval_review', None)
                st.rerun()
            except Exception as exc:
                st.error('적용 실패 · 운영 매니페스트 유지: ' + str(exc))

    st.markdown('#### 버전 이력과 이전 모델 복구')
    st.dataframe(pd.DataFrame([
        dict(version_id=event['version']['version_id'], action=event['action'],
             applied_at_utc=event['version']['applied_at_utc'],
             model=event['version']['model']['name'], sha256=event['version']['model']['model_sha256'],
             previous=event['previous_version_id'], candidate_id=event['version']['model']['candidate_id'],
             dataset_id=event['version']['model']['dataset_id'])
        for event in state['events']
    ]), hide_index=True, width='stretch')
    previous = {event['version']['version_id']: event['version'] for event in state['events']
                if event['version']['model'] != active['model']}
    if not previous:
        st.info('복구할 다른 모델의 적용 이력이 없습니다.')
        st.button('이전 모델로 복구', key='rollback_apply', disabled=True)
    else:
        target = st.selectbox('복구 가능한 이전 버전', list(previous), key='rollback_target')
        scope = active['version_id'] + ':' + target
        if st.session_state.get('rollback_scope') != scope:
            st.session_state.pop('rollback_confirm', None)
            st.session_state['rollback_scope'] = scope
        confirm = st.checkbox('선택한 이전 모델로 복구하고 복구 이력을 남깁니다.', key='rollback_confirm')
        if st.button('이전 모델로 복구', key='rollback_apply', disabled=not confirm):
            try:
                manager.rollback(target, confirmed=confirm, expected_version=active['version_id'],
                                 preflight=lambda version: load_bundle(version, manager))
                st.rerun()
            except Exception as exc:
                st.error('복구 실패 · 운영 매니페스트 유지: ' + str(exc))
    st.divider()
