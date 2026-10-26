# Gas Sensor Drift Classification

UCI Gas Sensor Array Drift Dataset의 128개 센서 특징으로 6종 가스 분류를 연구하는 Python/scikit-learn 프로젝트다.
초기 Batch 학습 이후 일반화 성능과 센서 특징 분포 변화의 관계를 살펴본다.
센서 드리프트가 성능 저하의 유일한 원인이라고 가정하지 않는다.

현재 단계는 데이터 검증, EDA, 평가 설계다. **분류 모델 학습·튜닝·최종 모델 선정은 수행하지 않았다.**

## 데이터 출처

- [UCI Dataset 224](https://archive.ics.uci.edu/dataset/224/gas+sensor+array+drift+dataset)
- Vergara, A. (2012). DOI: [10.24432/C5RP6W](https://doi.org/10.24432/C5RP6W).
- 원본: `D:/dataset/gas+sensor+array+drift+dataset/batch1.dat` … `batch10.dat`.
- 원본은 외부 위치에서 읽기만 한다. 프로젝트에 복사·이동·수정하지 않는다.
- 클래스: 1 Ethanol, 2 Ethylene, 3 Ammonia, 4 Acetaldehyde, 5 Acetone, 6 Toluene.
- 농도 열이 있는 UCI 270 확장판과 구분한다. 실제 표본수와 통계는 보고서에서 확인한다.
- UCI 설명의 과거 연구 전용 문구와 현재 CC BY 4.0 메타데이터가 병존함을 기록한다.

## 폴더 구조

```text
src/                       엄격한 데이터 로더와 EDA 코드
tests/                     파서·실제 데이터·분할·산출물 검증
reports/eda_report.html    그림을 내장한 독립형 한국어 보고서
reports/evaluation_design.md  향후 공정한 모델 비교 설계
outputs/figures/           제목·축 이름이 있는 PNG 9개
outputs/*.csv             기술통계·분포 변화·분할 진단·표본 메타데이터
outputs/*.json            검증 요약·실행 환경·분할 진단
config.json               원본 경로·시드·기대 차원
requirements.txt          호환 버전 범위
requirements-lock.txt     검증한 가상환경의 정확한 설치 버전
.gitignore                원본·가상환경·캐시·비밀정보 제외
.venv/                    로컬 가상환경 (Git 제외)
```

## 실행 (PowerShell, Python 3.12)

```powershell
Set-Location D:\Gas-Sensor-Drift-Classification
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m src.analysis
.\.venv\Scripts\python.exe -m pytest -q
```

다른 원본 경로는 `config.json`의 `data_dir`을 변경하거나 `--config 경로`로 지정한다.
상대 경로는 설정 파일 기준으로 해석된다. 코드는 UTF-8로 읽고 쓴다.
보고서는 브라우저에서 `reports/eda_report.html`을 열면 외부 네트워크 없이 볼 수 있다.
그래프의 가스명·축은 영문으로 표시하여 OS별 한글 폰트 의존성을 줄였다.
재실행은 기존 분석 산출물을 덮어쓰지만 원본은 읽기 전용으로 처리한다.

## 검증 및 분석 원칙

각 행에 정확히 128개 특징 토큰이 존재하는지 확인한다. 생략된 특징을 0으로 채우지 않는다.
오류는 파일명·행 번호와 함께 종료한다. 파일 누락은 inventory에 남기고 중단한다.
NaN/Inf는 검증 결과에 기록한 후 EDA를 중단한다. 가스·Batch 메타데이터와 행 순서를 보존한다.
IQR 표시는 이상치 가능성 진단이며 자동 삭제 기준이 아니다. 모든 특징의 min/max/분위수는 CSV에 저장한다.
정확 중복과 상충 레이블, Batch 간 중복을 검사하고 모든 설계 분할의 누수 위험을 기록한다.
행 번호를 timestamp로 간주하지 않으며 정확한 날짜·경과 시간은 만들지 않는다.

PCA와 StandardScaler는 탐색에만 전체 자료로 Fit한다. 해당 객체를 저장하거나 모델 평가에 재사용하지 않는다.
모델 평가 시 전처리는 Pipeline 안에서 각 Train/Fold에만 Fit해야 한다.
모델 설계는 `reports/evaluation_design.md`와 보고서 9장을 참조한다.
분할 manifest의 row_id와 feature_group은 재현을 위한 메타데이터이며 원본 특징값을 포함하지 않는다.
`distribution_checks.csv`의 KS/BH는 탐색용이며 원인 판정이나 모델 성능 검증이 아니다.
실행 전후 SHA-256 일치를 확인하지만 로컬 배포본과 UCI 최신 배포본의 동일성은 인증하지 않는다.

## Git / SourceTree

로컬 기본 브랜치는 `main`이다. Commit·Push·remote 연결은 하지 않았다.
SourceTree에서 기존 로컬 저장소로 이 폴더를 추가한 후 사용자가 GitHub 원격을 연결한다.

Git에 올릴 파일: 코드, 테스트, README, config(공개 가능한 데이터 경로), 의존성 목록,
집계 CSV/JSON, PNG 그래프, HTML 보고서, 평가 설계. 산출물은 재생성 가능하지만 현재 분석의 검토를 위해 포함한다.
공유 전 config 및 run_manifest에 포함된 로컬 데이터 경로의 공개 범위를 검토할 수 있다.

Git에서 제외할 파일: `.venv/`, `__pycache__/`, `.pytest_cache/`, `.env*`, 원본 `.dat`,
데이터 디렉터리, 압축 파일, 임시 캐시, 모델 바이너리.
Git 점검 내역은 `reports/git_audit.txt`에 저장한다. 파일을 stage하지 않고 dry-run으로 포함 후보를 검토했다.
