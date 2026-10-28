# 실제 서버 다운로드 응답과 합성 업로드 결과의 일치 확인
# 브라우저 파일 저장 이벤트와 HTTP 응답 검증 범위 구분

import hashlib
import io
import json
import urllib.request

import pandas as pd
from streamlit.runtime.memory_media_file_storage import _calculate_file_id, get_extension_for_mimetype

from .audit import OUT
from .service import load_models, read_upload, analyze, downloads


def main():
    payload = (OUT / "fixtures/ui_200_labels.csv").read_bytes()
    expected = downloads(analyze(read_upload(payload), load_models()))
    directory = OUT / "browser_downloads"
    directory.mkdir(exist_ok=True)
    records = []
    for filename, data in expected.items():
        file_id = _calculate_file_id(data, "text/csv", filename)
        url = "http://127.0.0.1:8501/media/" + file_id + get_extension_for_mimetype("text/csv")
        with urllib.request.urlopen(url, timeout=15) as response:
            content = response.read()
            assert response.status == 200 and content == data
            table = pd.read_csv(io.BytesIO(content))
            records.append(dict(file=filename, http_status=response.status, bytes=len(content), rows=len(table),
                                exact_payload_match=True, sha256=hashlib.sha256(content).hexdigest(),
                                content_disposition=response.headers.get("Content-Disposition")))
        (directory / filename).write_bytes(content)
    (OUT / "download_http_verification.json").write_text(json.dumps({
        "synthetic_functional_data_only": True, "files": records,
        "browser_download_button_clicked": True,
        "browser_download_completion_event_captured": False,
        "server_csv_responses_verified": True,
        "limitation": "IAB download event timed out; local browser save dialog/completion not verified",
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(records)


if __name__ == "__main__":
    main()
