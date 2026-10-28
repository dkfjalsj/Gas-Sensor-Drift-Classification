# 옛 문서 보관본의 지문 확인과 기존 테스트용 일시 복원
# 과거 해시·테스트를 변경하지 않고 원문 검사 조건 유지

from contextlib import contextmanager
import gzip
import json
from pathlib import Path

from ..data import ROOT
from .publication import ARCHIVE, OUT, checked_path, sha


# 압축 파일과 복원할 원문의 지문을 모두 확인
def archived_bytes(row):
    path = checked_path(row['archive'])
    payload = path.read_bytes()
    if sha(payload) != row['compressed_sha256']:
        raise ValueError('압축 보관본 지문 불일치: ' + row['path'])
    restored = gzip.decompress(payload)
    if sha(restored) != row['sha256'] or len(restored) != row['bytes']:
        raise ValueError('원문 지문 불일치: ' + row['path'])
    return restored


def records():
    path = ARCHIVE / 'manifest.json'
    lock = json.loads((OUT / 'archive_lock.json').read_text(encoding='utf-8'))
    if sha(path.read_bytes()) != lock['sha256']:
        raise ValueError('보관 목록 지문 불일치')
    return json.loads(path.read_text(encoding='utf-8'))


# 직접 경로를 읽는 옛 테스트에 실제 원문 파일을 일시 제공
@contextmanager
def legacy_test_documents():
    created = []
    try:
        for row in records():
            path = checked_path(row['path'])
            payload = archived_bytes(row)
            if path.exists():
                if sha(path.read_bytes()) != row['sha256']:
                    raise ValueError('기존 문서 덮어쓰기 금지: ' + row['path'])
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as stream:
                stream.write(payload)
            created.append(row)
        yield [row['path'] for row in created]
    finally:
        # 이번 실행에서 만든 동일 바이트의 문서만 제거
        for row in reversed(created):
            path = checked_path(row['path'])
            if sha(path.read_bytes()) != row['sha256']:
                raise ValueError('테스트 중 달라진 문서는 삭제하지 않음: ' + row['path'])
            path.unlink()
