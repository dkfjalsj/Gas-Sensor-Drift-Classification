# 개별 연구 원문 지문 보관본

manifest.json의 원래 경로·원문 SHA·압축 SHA를 통해 각 파일을 복구할 수 있음.
원본 CSV·모델·연구 코드는 원래 위치에 별도로 보존하며 이 보관본이나 ZIP 하나로 대체하지 않음.
기존 문서 해시를 직접 읽는 테스트는 다음 명령으로 실행함.

```powershell
.\.venv\Scripts\python.exe -B -X utf8 -m src.research_maintenance.publication_verify
```

이 명령은 필요한 옛 HTML·Markdown을 원래 위치에 일시 복원하고 SHA를 검증한 상태에서 기존 테스트를 그대로 실행함.
종료 후 이번 실행이 복원한 동일 바이트 문서만 제거함. 과거 테스트나 해시를 무조건 통과시키도록 변경하지 않음.
개별 원문이 필요하면 publication_archive.archived_bytes(row)로 지문 검증한 바이트를 얻어 별도 작업 폴더에 저장할 수 있음.
검증 보류 상태에서는 원래 문서가 아직 남아 있을 수 있으며 실제 삭제 이력은 outputs/report_publication/deletion_log.json으로 구분함.
