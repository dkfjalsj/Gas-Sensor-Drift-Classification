# 공식 Model A로 로컬 운영 매니페스트 최초 생성
# 이미 초기화한 경우 기존 버전·이력 유지

from .registry import ModelRegistry


if __name__ == '__main__':
    print(ModelRegistry().initialize()['active'])
