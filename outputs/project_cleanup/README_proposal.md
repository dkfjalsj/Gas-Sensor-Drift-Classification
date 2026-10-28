# 가스 센서 드리프트 감지 및 분류 성능 보정 시스템

> Word 수행내역서 작성 중인 기존 README를 보존하기 위한 **교체 초안**임. 루트 README는 아직 변경하지 않았음. 실제 채택 시 프로젝트 루트로 옮긴 뒤 아래 상대 링크를 사용할 수 있음.

UCI Gas Sensor Array Drift Dataset으로 가스 6종을 분류하고, 참조 데이터와 입력 센서 특징의 분포 차이를 안내하는 머신러닝 연구 프로젝트입니다. 시간순 성능 저하를 분석하고 Streamlit 분석 화면과 신규 정답 데이터 검증·분리를 연결했습니다.

## 데이터와 연구 질문

- 데이터: [UCI Gas Sensor Array Drift Dataset](https://archive.ics.uci.edu/dataset/224/gas+sensor+array+drift+dataset), 13,910행·10개 Batch·16개 센서에서 추출한 128개 특징.
- 가스: Ethanol, Ethylene, Ammonia, Acetaldehyde, Acetone, Toluene.
- 원본 경로: `config.json`의 `data_dir`. 원본·모델·로컬 등록 데이터·가상환경·인증 정보는 Git에서 제외합니다.
- 질문: 같은 분포의 분류 정확도와 미래 Batch의 일반화는 얼마나 다른가? 어떤 가스와 시기에서 실패하는가? 분포 변화 안내와 소량의 새 정답 데이터가 운영 검토를 도울 수 있는가?

## 현재 구현

- LR·RF·RBF SVM 기준 비교와 시간순 반복 검증.
- 특징 선택, 학습 시기·가스별 구성, 가중치, 비선형 변환, 앙상블 및 HGB 비교 기록.
- 공식 사용 모델 Model A: `B_SVM_balanced` (Train Batch 1–6, 5,933행).
- 고정 RFF-MMD² 감지기: 100행 창, 임계값 `0.00825701197565701`.
- Streamlit: CSV 업로드, 6종 가스 예측, 분포 변화 안내, 선택적 정답 비교, 상세 표와 CSV 3종 다운로드.
- 20-A: 신규 정답·출처·세션·측정 시각 검증, 공식 Train 중복 검사, 최신 세션 Validation 분리, 불변 데이터셋 저장.

20-B 후보 학습과 20-C 승인·모델 교체·rollback은 미구현입니다. 현재 모델 관리 화면은 데이터를 준비하며 모델을 자동으로 재학습하거나 교체하지 않습니다.

## 주요 결과와 해석

Model A의 Validation Batch 7–8 동일 가중 Macro F1은 0.897000입니다. 반복 관찰한 Batch 9–10에서는 동일 가중 평균 0.602705, pooled Macro F1 0.558657입니다. Batch 9 Toluene Recall 0%, Batch 10 Acetaldehyde Recall 14%가 남아 있습니다. 두 집계는 서로 다른 계산입니다.

Model A는 보호 지표와 사전 검증 조건을 고려해 유지한 공식 사용 모델입니다. 독립적인 최종 성능을 확정한 모델이라는 뜻은 아닙니다. 17단계에서 새 시기의 일부 정답을 사용한 적응은 회복 가능성을 보였으나 새 시기 정답 없는 일반화와 직접 비교할 수 없습니다.

분포 변화 경고는 센서 고장이나 분류 실패의 확정이 아닙니다. 가스 구성과 창의 행 순서에도 영향을 받습니다. 실제 산업 안전 장치 또는 물리적 드리프트 탐지 정확도로 검증하지 않았습니다. 새로운 독립 Test와 농도·환경·세션 기록이 필요합니다.

## 구조

```text
app_streamlit.py               웹앱 진입점
src/data.py                    원본 형식·특징·가스 매핑
src/common/                    운영·연구 공통 도구
src/webapp/                    분석 UI·서비스·20-A 검증·저장
src/drift_detection/           고정 분포 변화 감지기
src/research_maintenance/      자료 조사·보고서 통합·보존 검사
src/*실험별 모듈                기존 연구 재현 진입점 유지
tests/                         데이터·실험·웹앱·보존 검사
reports/                       통합 보고서·과거 원문·근거 목록
outputs/                       실험 표·그림·분할·검증 기록
models/                        로컬 모델, Git 제외
data/retraining/               로컬 불변 등록 데이터, Git 제외
```

## 실행

PowerShell, Python 3.12 기준입니다. 모델 바이너리와 원본은 Git에 포함하지 않으므로 검증된 로컬 자산이 별도로 필요합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-streamlit-lock.txt
.\.venv\Scripts\python.exe -m streamlit run app_streamlit.py
```

일반 검증은 `python -m pytest`로 실행할 수 있으나 일부 과거 검사는 기존 산출물을 다시 쓰려고 합니다. 현재 자료 보존 중에는 다음 제한 실행을 사용합니다. 건너뛴 검사는 통과로 집계하지 않습니다.

```powershell
$env:OPENBLAS_NUM_THREADS='1'
$env:OMP_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
.\.venv\Scripts\python.exe -B -m pytest tests -q -p src.research_maintenance.testing_guard -p no:cacheprovider
```

최신 정리 검증은 240 통과, 기존 실패 2, 제한 skip 90입니다. 과거 임시 파일 부재와 고정 모델 목록 충돌을 기록했으며 해시 기준을 임의 수정하지 않았습니다.

## 연구 자료

- [상세 통합 연구 보고서](reports/Gas_Sensor_Drift_Final_Report.md)
- [그림을 포함한 통합 HTML](reports/Gas_Sensor_Drift_Final_Report.html)
- [연구 근거 자료 목록](reports/research_evidence_index.md)
- [정리·보존 및 보류 현황](reports/project_cleanup_report.md)
- [웹앱 세부 실행 안내](README_streamlit.md)

기존 자료는 Word 문서 반영을 확인할 때까지 삭제·이동하지 않습니다. Git Stage·Commit·Push도 보류합니다. 향후 Notebook은 공통 함수를 호출하는 방식으로 작성하고 과거 실험 결과 경로를 덮어쓰지 않아야 합니다.
