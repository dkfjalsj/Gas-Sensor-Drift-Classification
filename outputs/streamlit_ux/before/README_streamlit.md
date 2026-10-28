# 가스 분류·분포 변화 분석 웹앱

기존 연구 결과와 모델을 유지하는 로컬 Streamlit 추론 앱이다. 공식 Model A와 rff_mmd_v1만 사용하며 재학습·모델 교체 기능은 없다.

## 설치 및 실행

프로젝트 폴더 `D:\Gas-Sensor-Drift-Classification`에서 PowerShell로 실행한다.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-streamlit.txt -c constraints-streamlit.txt
.\.venv\Scripts\python.exe -B -m streamlit run app_streamlit.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false --server.fileWatcherType none --server.maxUploadSize 20
```

브라우저에서 http://127.0.0.1:8501 을 연다. 이미 해당 포트를 사용한다면 다른 포트를 지정한다. 기존 requirements.txt와 requirements-lock.txt는 수정하지 않았다. 추가 설치 환경의 고정 목록은 requirements-streamlit-lock.txt에 기록한다.

## 입력과 사용 순서

1. UTF-8 CSV를 업로드한다. 필수 열은 f001~f128이며 선택적 gas 열은 정수1~6이다.
2. 분석 실행을 누른다. 다른 이름의 추가 열·중복 열·빈 행·무한대·비수치·전체 결측은 거부한다.
3. 가스 분류·분포 변화·통합 결과 화면을 확인한다.
4. 결과 다운로드에서 행별 예측·창별 점수·분석 요약 CSV를 받는다.

20MB·20,000행 이하를 지원한다. 열 순서만 다르면 이름을 기준으로 재정렬하고 이를 표시한다. 일부 결측은 각 저장 파이프라인의 기존 중앙값으로 처리한다. 임의의 특징 삭제·값 보정·스케일러 재적합은 하지 않는다.

gas가 없으면 실제 정확도를 계산하지 않는다. gas가 있으면 예측·감지 입력에서 분리해 사용자 제공 정답에 대한 평가에만 사용한다. 정답이 일부 클래스만 포함하면 Macro F1의 대상 클래스 수를 함께 표시한다. 사용자 제공 정답의 진실성은 앱이 검증할 수 없다.

## 해석 제한

- 감지는 입력 순서대로100행씩 사용하며 마지막100행 미만을 제외한다. 시간 정보나 Batch 경계를 추정하지 않으므로 파일 자체를 하나의 평가 구간으로 준비해야 한다.
- 100행 미만도 가스 예측은 가능하지만 분포 평가는 불가하다. 창별 다운로드는 제목 행만 포함하고 이유는 요약 CSV에 남긴다.
- MMD²는 확률·예상 정확도가 아니다. 가스 구성과 창 구성이 점수에 영향을 줄 수 있다. 분포 경고가 분류 결과를 무효화하지 않는다.
- 18.5단계에서 같은 행의 재배열로 Batch7 평균 점수가 약59.66% 감소했고, 모든 대상 창 경고는 유지됐다. 실제 고장·물리적 드리프트 탐지 정확도는 검증하지 않았다.
- 업로드는 세션 메모리에서만 처리하며 앱이 디스크에 저장하지 않는다. 서버를 공유 환경에 공개하려면 인증·접근 제어·배포 환경의 로그 및 보관 정책을 별도 검토해야 한다. 현재는 localhost 연구용 실행만 검증한다.
- 캐시는 모델 객체에만 적용한다. 파일 내용이 달라지면 이전 분석 결과를 비우며 파일 제거 시에도 결과를 비운다.

## 화면 및 코드

6개 화면: 대시보드, 입력, 가스 분류, 분포 변화, 통합 결과, 다운로드.

- app_streamlit.py: 실행 진입점
- src/webapp/service.py: 입력·모델 로딩·예측·감지·CSV 변환
- src/webapp/ui.py: 화면·모델 캐싱·업로드 상태 관리
- tests/test_streamlit_integration.py: 서비스와 실제 Streamlit 위젯 흐름 검사
- outputs/streamlit_integration/: 실행·검증·보존 기록
- reports/streamlit_integration_report.md: 완료 보고서

향후 반자동 재학습은 별도 라벨 확보·후보 검증·관리자 승인·버전 관리 설계가 필요하다. 현재 화면에 미구현된 버튼이나 자동 보정 결과를 표시하지 않는다.
