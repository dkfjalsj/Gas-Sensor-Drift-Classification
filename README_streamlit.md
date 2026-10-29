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


## 19.5단계 사용자 화면
데이터 분석 → 분석 결과 → 상세 분석의 세 영역으로 구성합니다.
CSV 선택 후 분석 시작을 누르면 결과 화면으로 이동합니다.
정답 평가와 기술 정보 및 CSV 다운로드는 상세 분석에서 확인합니다.


## 20-A 모델 관리 · 데이터 준비
모델 관리 화면에서 신규 실제 정답 CSV(f001~f128, gas)와 별도 세션 CSV(input_row, session_id, measured_at)를 등록합니다.
측정 시각은 시간대가 있는 실제 ISO 8601 값이어야 합니다. 출처와 실제 정답 확인 방식을 기록합니다.
최신 한 세션은 Validation, 나머지 과거 세션은 Train으로 고정합니다. 각 분할에 6가스가 모두 필요합니다.
기존 Model A 학습 자료와의 일치·근접 표본, 시기 겹침, 세션 부족, 출처 미확인은 준비를 보류합니다.
품질 경고는 관리자가 확인해야 합니다. 등록 자료는 Git 제외 경로 data/retraining/에 불변 버전으로 저장합니다.
20-A 등록 자체는 학습하지 않습니다. 20-B/20-C 영역에서 명시적 후보 학습·수동 승인·복구를 제공합니다.

## 20-B/20-C 후보 학습과 운영 모델 관리

로컬 포트폴리오용 프로토타입이며 로그인·관리자 인증을 제공하지 않습니다. 외부 공개 운영용 인증 시스템이 아닙니다.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-streamlit.txt
.\.venv\Scripts\python.exe -B -m src.model_management.initialize
.\.venv\Scripts\python.exe -B -m streamlit run app_streamlit.py
```

모델 바이너리와 원본 데이터는 Git에 포함하지 않습니다. 실행 전 검증된 공식 SVM
`models/temporal_expansion/B_SVM_balanced.joblib`과 감지기
`models/drift_detection/rff_mmd_v1.joblib`을 기존 로컬 위치에 준비해야 합니다.
공식 SVM SHA는 `1d6b20c94d1580d799e05ab5a9ce746bdb272d74f70ec2ff964011fffecfde32`,
감지기 SHA는 `de47661f66c69cdc7553f73acf1df9b721f65771d0301fe69a7a326f814fa4c5`입니다.
재학습은 config.json의 원본 경로, 기존 Batch1~6 원본과 추적된 분할 근거도 필요합니다.
초기화는 Model A만 지정하며, 이미 존재하는 운영 매니페스트와 이력은 유지합니다.

모델 관리에서20-A 등록 자료를 선택하고 재검사·입력 특징 호환성 확인 후 후보 학습을 실행합니다.
Train은 공식5,933행+신규 Train이며 전처리도 이 자료에서만 학습합니다.
후보는 models/retraining_candidates/에 별도 불변 저장하고 자동 적용하지 않습니다.

20-C에서 출처·실제 정답·검증 세션 독립성의 확인 근거를 입력하고, 동일한 신규 Validation에서
현재 운영 모델과 후보를 다시 비교합니다. 후보 Macro F1 비하락, 무결성·분리 검사,
명시적 변경 확인을 모두 통과해야 적용할 수 있습니다. 합성 후보는 실제 운영에 적용할 수 없습니다.
확인 근거는 인증된 외부 검증이 아닌 로컬 사용자 선언이며 독립 최종 성능을 보장하지 않습니다.

운영 정보는 Git 제외 경로 data/model_registry/registry.json에 저장합니다.
기존 모델 파일을 덮어쓰지 않고 포인터와 이력을 하나의 원자적 파일 교체로 함께 갱신합니다.
모델 변경 후 새 분석은 새 버전 캐시를 사용하며, 기존 분석 결과·CSV는 당시 모델 버전을 유지합니다.
이전 적용 이력에서 대상을 선택하고 확인하면 롤백도 새로운 이벤트로 기록됩니다.
손상된 매니페스트나 남아 있는 잠금은 자동 삭제하지 않습니다. 로컬 보관본과 원인 확인이 필요합니다.

```powershell
.\.venv\Scripts\python.exe -B -m pytest tests/test_retraining_candidates.py tests/test_model_approval.py -q -p no:cacheprovider
```

테스트도 검증된 공식 모델·감지기와 로컬 원본을 필요로 합니다. 합성 자료·후보는 임시 폴더에서 생성합니다.
과거 파일 보존 검사는 로컬 보존 스냅샷이 있어야 수행할 수 있으며, 없으면 해당 검사만 미실행으로 표시합니다.
과거 연구 테스트에는 알려진 보존 기준 충돌이 있어 전체 결과를 구분해야 합니다.

새 reports/, outputs/retraining_candidates/, outputs/model_approval/, data/, models/는 Git 제외입니다.
기존에 추적 중인 연구 근거·보고서는 의존성을 보존하기 위해 유지하며 이번 변경에서 추적 해제하지 않습니다.
합성 기능 검사 점수를 실제 센서 성능 개선으로 해석하지 않습니다.
