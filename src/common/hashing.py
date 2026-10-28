# 원본 바이트의 SHA-256 지문 계산
# 데이터 정리나 전처리 없이 입력 그대로 식별

import hashlib


# 파일·업로드의 바이트 지문 반환
def sha256_bytes(payload):
    return hashlib.sha256(payload).hexdigest()
