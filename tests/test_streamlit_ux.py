# 쉬운 결과 화면과 기존 CSV 바이트 유지 검증
import hashlib
import json

import pytest

from src.data import ROOT
from src.webapp.service import analyze, read_upload, downloads
from tests.test_streamlit_integration import synthetic, csv_bytes, make_app, models


@pytest.mark.parametrize('n', [99, 100, 101, 200])
@pytest.mark.parametrize('labels', [False, True])
def test_frozen_download_identity(models, n, labels):
    baseline = json.loads((ROOT / 'outputs/streamlit_ux/baseline_download_sha256.json').read_text())
    result = analyze(read_upload(csv_bytes(synthetic(n, labels))), models)
    assert {name: hashlib.sha256(value).hexdigest() for name, value in downloads(result).items()} == baseline[f'{n}_{labels}']


def test_simple_result_and_details():
    app = make_app()
    app.file_uploader[0].set_value(('test.csv', csv_bytes(synthetic(101, True)), 'text/csv')).run()
    assert any('101개의 센서 데이터가 준비' in item.value for item in app.success)
    app.button(key='analyze').click().run()
    assert app.radio(key='page').value == '분석 결과'
    assert not app.exception
    assert len(app.metric) == 3
    assert not app.dataframe
    assert not any('Accuracy' in item.label for item in app.metric)
    app.radio(key='page').set_value('상세 분석').run()
    assert len(app.download_button) == 3
    assert any('Accuracy' in item.label for item in app.metric)
    app.file_uploader[0].clear().run()
    assert 'analysis' not in app.session_state
    assert not app.exception


def test_unavailable_reason_for_invalid_windows():
    frame = synthetic(200)
    frame.loc[:99, 'f001'] = float('nan')
    frame.loc[100:, 'f002'] = float('nan')
    app = make_app()
    app.file_uploader[0].set_value(('missing.csv', csv_bytes(frame), 'text/csv')).run()
    app.button(key='analyze').click().run()
    assert not app.exception
    assert any('일부 값 때문에' in item.value for item in app.info)
    assert not any('더 필요' in item.value for item in app.info)
