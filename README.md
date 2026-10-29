# Gas Sensor Drift Classification

128개 센서 특징으로6종 가스를 분류하고, 시간에 따른 일반화 한계와 입력 분포 변화를 연구하는 Python/scikit-learn 프로젝트다. 연구 과정과 기존 결과는 대표 Notebook, 실행 기능은 Python 모듈, 기능 검증은 tests로 분리한다.

## 문제와 데이터

UCI Gas Sensor Array Drift Dataset 224의13,910행·10 Batch·6가스·128특징을 사용한다. 클래스는 Ethanol, Ethylene, Ammonia, Acetaldehyde, Acetone, Toluene이다. 원본 출처는 UCI, DOI:10.24432/C5RP6W다.

원본은 config.json의 data_dir에서 읽으며 복사·이동하지 않는다. 센서16개×특징8개 매핑은 src/data.py의 feature_label 정의를 사용한다. Batch는 순서 정보이며 실제 측정 시각·농도·환경 정보로 확대 해석하지 않는다.

## 연구와 기준 모델

랜덤 분할과 과거→미래 Batch 평가를 구분한다. 공식 기준 모델은 Train Batch1~6의5,933행으로 학습한 SimpleImputer→StandardScaler→RBF SVM이다. 6단계에서는 Validation7~8의 Batch별 Macro F1 동일 가중 평균으로 후보를 고정했다. 이후 가중치·학습 시기 구성·특징 선택·비선형 변환·앙상블·HGB·소량 라벨 적응을 검토했지만 모든 가스의 일관된 미래 개선을 확보했다고 주장하지 않는다.

Batch9~10과 과거 Validation은 반복 사용한 회고적 자료이며 독립 최종 Test가 아니다. Toluene과 Acetaldehyde의 시기별 실패·성능 상충, 클래스 support 차이가 남아 있다. 분포 변화만으로 센서 노후화·장비 고장·오분류 원인을 확정하지 않는다.

## 폴더와 역할

```text
gas_sensor_drift.ipynb       대표 연구 Notebook,11개 섹션
app_streamlit.py            웹앱 진입점
src/data.py                원본 엄격 파싱·검증
src/analysis.py            분할·중복·클래스 구성 공통 검사
src/research.py            Notebook 공통 조회·시각화
src/*.py                   기존 연구 계산·학습 보조 함수와 모델 재로딩 클래스
src/drift_detection/       고정 RFF-MMD² 감지기·공통 계산
src/drift_detection_sensitivity/  창 구성·가스 구성 진단 계산
src/webapp/                CSV 검증·추론·감지·사용자 화면·20-A 등록
src/retraining/            20-B 후보 재학습·동일 Validation 평가·불변 저장
src/model_management/      20-C 수동 승인·운영 포인터·버전·롤백
tests/                     기능·누수·예측·수치·Notebook 회귀 검사
outputs/                   기존 핵심 실험 CSV·JSON·압축 예측 기록
research/                  연구 조건·해석 이관 근거와 유지 결과 지문
models/                    공식·연구 모델과 메타데이터 (Git 제외)
data/                      등록 데이터·운영 매니페스트 (Git 제외)
sample_data/               입력 형식 확인용 예제
maintenance/cleanup21/     로컬 정리 목록·삭제 사유·검증 기록 (Git 제외)
```

보고서 생성·포장·검토 전용 코드는 제거했다. 옛 실험의 보고서 생성·지문 동결·덮어쓰기를 함께 수행하던 일괄 CLI도 제거했다. 같은 경로의 공통 계산·모델 클래스는 보존하므로 기존 모델 재로딩과 조건별 계산에 재사용할 수 있다. 파일명 변경을 위한 일괄 이동은 하지 않았다. HTML 보고서 생성 기능은 제공하지 않는다. Streamlit 화면의 HTML/CSS와 Notebook 자체 표 출력은 유지한다.

## 설치와 로컬 준비

Python3.12 환경에서 검증했다.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-streamlit.txt
.\.venv\Scripts\python.exe -m pip install -r requirements-notebook.txt
```

원본 경로를 config.json에서 확인하고, 아래 두 검증된 로컬 파일을 준비한다. 모델·원본은 저장소에 포함하지 않으므로 코드만 내려받아 즉시 모델을 재구성할 수 있는 배포본은 아니다.

- models/temporal_expansion/B_SVM_balanced.joblib
  - SHA-256: 1d6b20c94d1580d799e05ab5a9ce746bdb272d74f70ec2ff964011fffecfde32
- models/drift_detection/rff_mmd_v1.joblib
  - SHA-256: de47661f66c69cdc7553f73acf1df9b721f65771d0301fe69a7a326f814fa4c5

기존 연구 모델325개는 재현·재로딩 검증을 위해 로컬에 보존했다. 서비스 실행에는 위 두 모델이 필요하며, 연구 전체 모델 재검사에는 나머지 로컬 모델도 필요하다.

## Notebook

Jupyter를 지원하는 편집기에서 프로젝트 .venv 커널을 선택하고 루트의 gas_sensor_drift.ipynb를 순서대로 실행한다. 경로 기준은 프로젝트 루트다. 코드 셀은 외부 자료 확인, EDA·PCA, 저장 결과 표시·그래프, 기존 예측 소량 재현, 운영 정보 조회를 수행한다. 기본 실행 경로에서는 분류 모델의 신규 학습·튜닝·승인·운영 교체를 호출하지 않는다. 선택 재학습 예시는 RUN_BASELINE_REPLAY=False로 제공하며 이번 정리에서는 실행하지 않았다.

기존 실험 지표는 outputs의 원본 CSV를 그대로 읽는다. 삭제한 보고서에만 있던 조건·해석은 research/experiment_conditions.json에 원문 SHA와 함께 이관했다. 과거 전체 학습 실험을 이번 정리에서 재실행한 것으로 표현하지 않는다. 필요한 환경·자료가 없으면 명시적으로 오류를 내며 결과를 만들어내지 않는다.

## Streamlit 실행

```powershell
.\.venv\Scripts\python.exe -B -m src.model_management.initialize
.\.venv\Scripts\python.exe -B -m streamlit run app_streamlit.py --server.address 127.0.0.1
```

초기화는 처음에 Model A를 지정하며 기존 운영 매니페스트가 있으면 그대로 유지한다. 운영 매니페스트는 data/model_registry/registry.json이다. CSV 업로드의 필수 입력은 f001~f128이며 gas 정답은 선택적이다. 가스 분류,100행 단위 분포 변화 감지, 상세 결과,3종 CSV 다운로드와 모델 관리를 제공한다.

고정 감지기의 임계값은0.00825701197565701이다. 가스 구성과 창 구성도 점수에 영향을 준다. 높은 MMD²를 높은 오류율이나 실제 센서 고장으로 해석하지 않는다.

## 20-A~20-C 모델 관리

20-A에서 실제 정답·출처·수집 세션·측정 시각을 확인하고 최신 세션 Validation과 이전 세션 Train을 불변 등록한다. 기존 Train 및 과거 Validation과의 중복·누수를 검사한다.

20-B는 기존5,933행+신규 Train에서만 전처리와 같은 SVM을 학습하고 동일 신규 Validation에서 비교한다. 후보 파일은 별도로 저장하며 자동 적용하지 않는다.

20-C는 실제 출처·정답·검증 독립성의 수동 확인 근거, 무결성·분리 검사, 동일 Validation의 Macro F1 비하락과 명시적 확인이 있어야 적용한다. 파일을 덮어쓰지 않고 운영 포인터와 누적 이력을 원자적으로 갱신하며 이전 모델로 복구할 수 있다. 새 분석은 새 버전 캐시를 사용하고 기존 분석은 당시 모델 버전을 유지한다.

로그인·인증이 없는 로컬 프로토타입이다. 확인 근거는 외부 검증이 아닌 사용자 선언이며 확인 불가능하면 적용하지 않아야 한다. 합성 후보는 실제 운영 적용을 차단한다. 합성 Train60/Validation60의 Macro F1100%는 기능 검사 결과로, 실제 신규 센서 성능 개선은 아직 검증하지 않았다.

## 테스트

```powershell
.\.venv\Scripts\python.exe -B -m pytest tests -q -p no:cacheprovider
```

공식 모델·감지기·로컬 원본과 유지된 outputs를 준비해야 한다. 후보 학습·승인·롤백 검사는 임시 디렉터리에서 합성 자료를 생성해 수행하며 실제 운영 상태를 변경하지 않는다. Notebook 구조·기존 지표·유지 결과 지문·예측 재현도 검사한다.

21단계에서 폐기된 보고서·그림·옛 전체 파일 목록 검사는 제거하고 핵심 기능·수치·누수 검증으로 범위를 재편했다. 과거303개 통과/기존2실패/84미실행/11해시충돌과 새 검사 개수를 직접 비교해 품질 향상으로 해석하지 않는다. 과거 실패 기준을 새 해시로 갱신한 것이 아니며, 폐기한 검사는 maintenance/cleanup21/retired_tests.json에 기록했다.

## Git와 한계

21단계 변경은 로컬 검토용으로 남기며 Commit·Push하지 않는다. 모델·실측 데이터·로컬 정리 로그·캐시는 제외한다. 연구 핵심 CSV·JSON과 대표 Notebook·소스·테스트는 다음 검토 대상이다. 삭제된 추적 파일도 Git 변경 목록에 남으므로 다음 Git 반영은 별도 검토가 필요하다.
