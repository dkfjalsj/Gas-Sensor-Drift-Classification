# 4단계 신규 테스트의 검사 오류 수정 기록

수정 범위는 이번에 추가한 tests/test_toluene.py뿐이다. 기존 test_models.py, test_diagnostics.py, test_validation.py와 과거 해시 기준은 수정하지 않았다.

1. 겹침 지표는 확률 합산이므로 부동소수점 표현에서 1보다 약 2e-16 클 수 있다. [0,1] 검사에 1e-12의 수치 허용오차만 추가했다. Wasserstein 값을 원본에서 독립 재계산하는 검사는 유지했다. 실제 거리나 분석 결과는 변경하지 않았다.
2. 새 학습·모델 저장 금지 검사가 AST 해시 계산용 ast.dump까지 모델 저장으로 잘못 판단했다. Fit/fit_transform 금지는 유지하고 저장 검사는 joblib.dump에 적용하도록 바로잡았다. 진단 코드에는 Fit이나 joblib.dump가 없다.

첫 4단계 결과와 테스트 로그는 outputs/toluene_analysis_attempt_1/에 보존하고, 동일 분석을 다시 실행해 최종 결과를 outputs/toluene_analysis/에 생성했다. 기존 단계의 산출물은 덮어쓰지 않는다.

별도 기존 실패: 과거 소스 SHA-256 불일치와 현재 없는 ~$ 이름의 파일 참조. 이를 통과시키기 위해 기존 테스트나 과거 기록을 수정하지 않았다.
