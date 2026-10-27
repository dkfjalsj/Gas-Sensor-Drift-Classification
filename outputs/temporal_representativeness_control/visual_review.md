# 그래프 최종 검토

Recall 히트맵 범례를 아래로 옮겨 제목 겹침 해소. 학습·모델·예측·지표·조건 변경 없음. 표시 수치 CSV가 완전히 같은지 대조. 초기 마감 기록·보고서·그래프는visual_review_before/에 보존.

전체 재현 시 기본 분석·테스트·finalize 후 다음을 실행:
python -B -X utf8 -m src.representativeness_visual_review --prepare
python -B -X utf8 -m pytest -q -p no:cacheprovider --junitxml=outputs/temporal_representativeness_control/test_results.xml
python -B -X utf8 -m src.representativeness_visual_review --finalize
