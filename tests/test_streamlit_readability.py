# 한글 요약 표와 원본 값·다운로드 보존 검증
from copy import deepcopy

import pandas as pd
import pytest

from src.webapp.service import analyze, read_upload, downloads
from src.webapp.ui import prediction_table, pattern_table
from tests.test_streamlit_integration import synthetic, csv_bytes, make_app, models


@pytest.mark.parametrize('n', [99, 100, 101, 200])
@pytest.mark.parametrize('labels', [False, True])
def test_display_tables_preserve_outputs(models, n, labels):
    result = analyze(read_upload(csv_bytes(synthetic(n, labels))), models)
    before = deepcopy(result)
    exports = downloads(result)
    table = prediction_table(result)
    assert list(table.columns) == (['측정 번호', 'AI 예측 가스', '실제 가스', '예측 결과']
                                   if labels else ['측정 번호', 'AI 예측 가스'])
    assert list(table['측정 번호']) == list(range(1, n + 1))
    names = {1: '에탄올', 2: '에틸렌', 3: '암모니아', 4: '아세트알데하이드', 5: '아세톤', 6: '톨루엔'}
    assert table['AI 예측 가스'].tolist() == result['rows'].predicted_gas_id.map(names).tolist()
    if labels:
        assert table['실제 가스'].tolist() == result['rows'].gas.map(names).tolist()
        assert table['예측 결과'].eq('일치').tolist() == result['rows'].gas.eq(result['rows'].predicted_gas_id).tolist()
    if n >= 100:
        pattern = pattern_table(result)
        pd.testing.assert_series_equal(pattern['패턴 차이 점수'], result['windows'].score, check_names=False)
        assert pattern['결과'].eq('기준과 다른 패턴').tolist() == result['windows'].alert.tolist()
    for key in ['rows', 'windows', 'counts']:
        pd.testing.assert_frame_equal(result[key], before[key])
    assert downloads(result) == exports


def test_invalid_window_is_not_normal(models):
    frame = synthetic(200)
    frame.loc[:99, 'f001'] = float('nan')
    result = analyze(read_upload(csv_bytes(frame)), models)
    table = pattern_table(result)
    assert table.iloc[0]['결과'] == '평가 불가'
    assert pd.isna(table.iloc[0]['패턴 차이 점수'])


@pytest.mark.parametrize('labels', [False, True])
def test_real_ui_summary_and_raw_access(labels):
    app = make_app()
    app.file_uploader[0].set_value(('readability.csv', csv_bytes(synthetic(200, labels)), 'text/csv')).run()
    app.button(key='analyze').click().run()
    app.radio(key='page').set_value('상세 분석').run()
    assert not app.exception
    tables = [item.value for item in app.dataframe]
    expected = prediction_table(app.session_state['analysis'])
    pd.testing.assert_frame_equal(tables[0], expected)
    raw = next(table for table in tables if 'f128' in table)
    assert len(raw.columns) == 129 and '測定' not in str(raw.columns)
    assert [c for c in raw if c.startswith('f')] == [f'f{i:03}' for i in range(1, 129)]
    app.number_input[0].set_value(200).run()
    raw = next(item.value for item in app.dataframe if 'f128' in item.value)
    assert raw['측정 번호'].tolist() == [200]
    next(widget for widget in app.radio if widget.label == "원본 표시 범위").set_value('전체 측정값').run()
    raw = next(item.value for item in app.dataframe if 'f128' in item.value)
    assert len(raw) == 200
    assert len(app.download_button) == 3
    assert not app.exception
