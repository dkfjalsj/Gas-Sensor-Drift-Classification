# Word 보고서용 연구 자료집

Batch9–10은 독립 Test가 아닌 반복 사용한 회고적 평가 자료임. PNG는 실제 기존 그림의 원래 픽셀을 그대로 보존함. 이미지 추출본은 원본 파일과 DPI·크기가 다를 수 있어 동일 그림의 원본 고해상도 파일을 우선 사용할 수 있음. 표는 원본 소수 자릿수·평가 조건을 유지함.

외부 ZIP의 원본 근거 경로는 출처 식별자이며 프로젝트 파일이 없어도 HTML·PNG·표를 열 수 있음. 소스 코드·모델·행별 예측은 이 배포 자료집에 포함하지 않음. 전체128×128 상관행렬은 저장되어 있지 않으며 11단계 동일 센서8특징 상관 그림을 명확한 범위로 제공함.


## png/1_batch_counts.png

- 자료 제목: batch_counts
- 실험 목적: 1단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 가스·Batch 구성은 불균형이며 Batch3–5에 Toluene이 없음. 값 변화와 센서 드리프트의 인과관계는 별도 문제임.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/figures/batch_counts.png`
- 파일 지문 SHA-256: `e9650a58fd29103b223e1dae7052371e530337bb1de8f077f27bcaad257730d4`

## png/1_batch_gas_trends.png

- 자료 제목: batch_gas_trends
- 실험 목적: 1단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 가스·Batch 구성은 불균형이며 Batch3–5에 Toluene이 없음. 값 변화와 센서 드리프트의 인과관계는 별도 문제임.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/figures/batch_gas_trends.png`
- 파일 지문 SHA-256: `df3daa03448133711d403176eca210d8b29a0646757adb329e4507a155b9ed9a`

## png/1_batch_shift.png

- 자료 제목: batch_shift
- 실험 목적: 1단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 가스·Batch 구성은 불균형이며 Batch3–5에 Toluene이 없음. 값 변화와 센서 드리프트의 인과관계는 별도 문제임.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/figures/batch_shift.png`
- 파일 지문 SHA-256: `d6d3ece253520fd6a040cb60f0d87b70ffe669479e9d07c0cd810cf39f3ebe16`

## png/1_class_counts.png

- 자료 제목: class_counts
- 실험 목적: 1단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 가스·Batch 구성은 불균형이며 Batch3–5에 Toluene이 없음. 값 변화와 센서 드리프트의 인과관계는 별도 문제임.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/figures/class_counts.png`
- 파일 지문 SHA-256: `1ae71cada54c247dbbb101e25664badeef984e860e6858530b4604a6c6e988a3`

## png/1_conditional_shift.png

- 자료 제목: conditional_shift
- 실험 목적: 1단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 가스·Batch 구성은 불균형이며 Batch3–5에 Toluene이 없음. 값 변화와 센서 드리프트의 인과관계는 별도 문제임.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/figures/conditional_shift.png`
- 파일 지문 SHA-256: `f66c3b56a874c42dbd937a083281cc573634875b22ba76916c22d2fb04abd777`

## png/1_feature_distributions.png

- 자료 제목: feature_distributions
- 실험 목적: 1단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 가스·Batch 구성은 불균형이며 Batch3–5에 Toluene이 없음. 값 변화와 센서 드리프트의 인과관계는 별도 문제임.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/figures/feature_distributions.png`
- 파일 지문 SHA-256: `0fffbe182d6739c1cab142fd970087cc990508dad3971bb346f34ae5b2077c14`

## png/1_gas_response.png

- 자료 제목: gas_response
- 실험 목적: 1단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 가스·Batch 구성은 불균형이며 Batch3–5에 Toluene이 없음. 값 변화와 센서 드리프트의 인과관계는 별도 문제임.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/figures/gas_response.png`
- 파일 지문 SHA-256: `fdb7b49228b3289be3485e8aa76f34ef0220e3f293d7f573bcc7404b7ec415b7`

## png/1_pca.png

- 자료 제목: pca
- 실험 목적: 1단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 가스·Batch 구성은 불균형이며 Batch3–5에 Toluene이 없음. 값 변화와 센서 드리프트의 인과관계는 별도 문제임.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/figures/pca.png`
- 파일 지문 SHA-256: `946a2973440b33ff5fe75ed3d5dc8bf1e2d94db55300283149e82dd9024643af`

## png/1_pca_variance.png

- 자료 제목: pca_variance
- 실험 목적: 1단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 가스·Batch 구성은 불균형이며 Batch3–5에 Toluene이 없음. 값 변화와 센서 드리프트의 인과관계는 별도 문제임.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/figures/pca_variance.png`
- 파일 지문 SHA-256: `d59ae026ca32c12f260503bbf45c5425aacd8bbe7cf0c33aad8fea3c43ee1056`

## tables/1_batch_class_counts.csv

- 자료 제목: batch_class_counts
- 실험 목적: 1단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 가스·Batch 구성은 불균형이며 Batch3–5에 Toluene이 없음. 값 변화와 센서 드리프트의 인과관계는 별도 문제임.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/batch_class_counts.csv`
- 파일 지문 SHA-256: `ea1e5369071d328f327b298e82e9a0cd96107c351aff82332647fadea7dc08ac`

## tables/1_batch_gas_feature_summary.csv

- 자료 제목: batch_gas_feature_summary
- 실험 목적: 1단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 가스·Batch 구성은 불균형이며 Batch3–5에 Toluene이 없음. 값 변화와 센서 드리프트의 인과관계는 별도 문제임.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/batch_gas_feature_summary.csv`
- 파일 지문 SHA-256: `a9201be6925e8dddab2bead9ad00b09239af637444cdf326990d7de98af53e45`

## tables/1_batch_standardized_mean_shift.csv

- 자료 제목: batch_standardized_mean_shift
- 실험 목적: 1단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 가스·Batch 구성은 불균형이며 Batch3–5에 Toluene이 없음. 값 변화와 센서 드리프트의 인과관계는 별도 문제임.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/batch_standardized_mean_shift.csv`
- 파일 지문 SHA-256: `f7d2a6dfe6a3c9f223618de66ce59facea0ac5bba1fb798fb98aa1cff013b5de`

## tables/1_class_conditional_shift.csv

- 자료 제목: class_conditional_shift
- 실험 목적: 1단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 가스·Batch 구성은 불균형이며 Batch3–5에 Toluene이 없음. 값 변화와 센서 드리프트의 인과관계는 별도 문제임.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/class_conditional_shift.csv`
- 파일 지문 SHA-256: `672438ffb3d29cad3bcac28040dee4f7fb7f191c25050eff5f8fad6f174cbfc2`

## tables/1_distribution_checks.csv

- 자료 제목: distribution_checks
- 실험 목적: 1단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 가스·Batch 구성은 불균형이며 Batch3–5에 Toluene이 없음. 값 변화와 센서 드리프트의 인과관계는 별도 문제임.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/distribution_checks.csv`
- 파일 지문 SHA-256: `5fbef6cfb21f7ef3cac36da01a749639d63e95e06f817e63f914ffdc6f22badf`

## tables/1_duplicate_rows.csv

- 자료 제목: duplicate_rows
- 실험 목적: 1단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 가스·Batch 구성은 불균형이며 Batch3–5에 Toluene이 없음. 값 변화와 센서 드리프트의 인과관계는 별도 문제임.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/duplicate_rows.csv`
- 파일 지문 SHA-256: `43d71697100e546195ac53b56493b17cae6641165646423223ed5d425cb4dc05`

## tables/1_feature_summary.csv

- 자료 제목: feature_summary
- 실험 목적: 1단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 가스·Batch 구성은 불균형이며 Batch3–5에 Toluene이 없음. 값 변화와 센서 드리프트의 인과관계는 별도 문제임.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/feature_summary.csv`
- 파일 지문 SHA-256: `27e1eb6a5fb24e523aece859d67bfe52405f776680a335411c7e5cd40c4e8304`

## tables/1_file_inventory.csv

- 자료 제목: file_inventory
- 실험 목적: 1단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 가스·Batch 구성은 불균형이며 Batch3–5에 Toluene이 없음. 값 변화와 센서 드리프트의 인과관계는 별도 문제임.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/file_inventory.csv`
- 파일 지문 SHA-256: `a32645a2925e4c48606b45b3d2854bc2e6a4ce8377f93684ff45ce24d21e0b90`

## tables/1_file_validation.csv

- 자료 제목: file_validation
- 실험 목적: 1단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 가스·Batch 구성은 불균형이며 Batch3–5에 Toluene이 없음. 값 변화와 센서 드리프트의 인과관계는 별도 문제임.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/file_validation.csv`
- 파일 지문 SHA-256: `e7ddcf6e3178292a0b6a6c08186e68f94cff5331c61ef4b7032c3cf01499be70`

## tables/1_label_order_runs.csv

- 자료 제목: label_order_runs
- 실험 목적: 1단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 가스·Batch 구성은 불균형이며 Batch3–5에 Toluene이 없음. 값 변화와 센서 드리프트의 인과관계는 별도 문제임.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/label_order_runs.csv`
- 파일 지문 SHA-256: `5756626768839254b81e90952e7c92da5a9c8eac8b8ac2d4bea670bce8af64a3`

## tables/1_pca_explained_variance.csv

- 자료 제목: pca_explained_variance
- 실험 목적: 1단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 가스·Batch 구성은 불균형이며 Batch3–5에 Toluene이 없음. 값 변화와 센서 드리프트의 인과관계는 별도 문제임.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/pca_explained_variance.csv`
- 파일 지문 SHA-256: `19dee5011545a98df43bf5ed95fcad4f0db7a5a6ce7a8514fa68e6009e228371`

## png/2_batch_A_random.png

- 자료 제목: batch_A_random
- 실험 목적: 2단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_comparison/figures/batch_A_random.png`
- 파일 지문 SHA-256: `82e2943663c398ede157b08e67cc1b0e1c7b3f0ffe806aebf8939b418a11e57b`

## png/2_batch_B_early.png

- 자료 제목: batch_B_early
- 실험 목적: 2단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_comparison/figures/batch_B_early.png`
- 파일 지문 SHA-256: `0ccb32068158481d70ab5c0938810af12d5838dd7efadc9b4bff86eba3de7f74`

## png/2_batch_B_history.png

- 자료 제목: batch_B_history
- 실험 목적: 2단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_comparison/figures/batch_B_history.png`
- 파일 지문 SHA-256: `5da50fc8031de2a2d18d2689a203a6203fbcb20730b841498c3a14ed536526ad`

## png/2_cm_A_random_test.png

- 자료 제목: cm_A_random_test
- 실험 목적: 2단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_comparison/figures/cm_A_random_test.png`
- 파일 지문 SHA-256: `aff47ee8d830cebd8aab6e20d4939e44c60943a8f4c43ff74ac765054a8630cd`

## png/2_cm_A_random_validation.png

- 자료 제목: cm_A_random_validation
- 실험 목적: 2단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_comparison/figures/cm_A_random_validation.png`
- 파일 지문 SHA-256: `1e659f8f9d1d4b48b53c03120ba32784fd330b7430f7b230a14ab7d70eba134c`

## png/2_cm_B_early_test.png

- 자료 제목: cm_B_early_test
- 실험 목적: 2단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_comparison/figures/cm_B_early_test.png`
- 파일 지문 SHA-256: `6527e2585187b29f644af9222ed7ac4f0cefa1c4ac6b944685e628fb6ed4e967`

## png/2_cm_B_early_validation.png

- 자료 제목: cm_B_early_validation
- 실험 목적: 2단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_comparison/figures/cm_B_early_validation.png`
- 파일 지문 SHA-256: `6a9c00049630616a33e491ff2be0f131bad61309d71bc11c436a005fb8935790`

## png/2_cm_B_history_test.png

- 자료 제목: cm_B_history_test
- 실험 목적: 2단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_comparison/figures/cm_B_history_test.png`
- 파일 지문 SHA-256: `926da61e6b967a2290f5aca6cf1efdcc312c4d945e5d039d7ac42bc79093b32f`

## png/2_cm_B_history_validation.png

- 자료 제목: cm_B_history_validation
- 실험 목적: 2단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_comparison/figures/cm_B_history_validation.png`
- 파일 지문 SHA-256: `c3a53a89686cb864146d768268158b2bbbecb565e1f751d51522a8e3d7c78e27`

## png/2_pooled_comparison.png

- 자료 제목: pooled_comparison
- 실험 목적: 2단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_comparison/figures/pooled_comparison.png`
- 파일 지문 SHA-256: `65256214f82e71e5581f18e7dfdcbf30c6b18ba5d2f6f7996c23e58948e9898d`

## png/2_stability.png

- 자료 제목: stability
- 실험 목적: 2단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_comparison/figures/stability.png`
- 파일 지문 SHA-256: `285eafb95f8df21e8cf3a8f021bd200b7665965b105c2e96ad09f7dceecc6077`

## tables/2_batch_stability.csv

- 자료 제목: batch_stability
- 실험 목적: 2단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_comparison/batch_stability.csv`
- 파일 지문 SHA-256: `3d9aa4f69eb17b9ad3bc0e858db70497e72be0ee76e2149d23cc8fe7e8873332`

## tables/2_confusion_matrices.csv

- 자료 제목: confusion_matrices
- 실험 목적: 2단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_comparison/confusion_matrices.csv`
- 파일 지문 SHA-256: `fa437bed17d237bf3a2392dbefa4a8699a3ce791f3ac3655bcec9b7100857415`

## tables/2_metrics.csv

- 자료 제목: metrics
- 실험 목적: 2단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_comparison/metrics.csv`
- 파일 지문 SHA-256: `3defd8f730f1f25cc81ea68191a3f1c261f49bce04758ff48bd3311a71f7b3ba`

## tables/2_per_class_metrics.csv

- 자료 제목: per_class_metrics
- 실험 목적: 2단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_comparison/per_class_metrics.csv`
- 파일 지문 SHA-256: `31b94eb843373897661df82f6a02eed29e960c1f44c54a97709de7d20c298e96`

## tables/2_random_batch_gap.csv

- 자료 제목: random_batch_gap
- 실험 목적: 2단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_comparison/random_batch_gap.csv`
- 파일 지문 SHA-256: `1692198d67925057de20cf7ca7a366a333f1d68ac890f4d4ee6dca81febc1f2f`

## tables/2_source_validation.csv

- 자료 제목: source_validation
- 실험 목적: 2단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_comparison/source_validation.csv`
- 파일 지문 SHA-256: `d2c30b2e1b9f543d29d018de38d32f53b45b0bad409fb2d4d0e0ce74f9351509`

## png/3_batch_performance.png

- 자료 제목: batch_performance
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/figures/batch_performance.png`
- 파일 지문 SHA-256: `6cb7d1521bab732705ed3ac5f2120680b2749b2eedbd205bc77bed2fbe23bb66`

## png/3_cm_LogisticRegression.png

- 자료 제목: cm_LogisticRegression
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/figures/cm_LogisticRegression.png`
- 파일 지문 SHA-256: `cbaf6f8f5386d60f3fc4d6b66b827a02cbe8a628bc49dc872c86f7fd0531104f`

## png/3_cm_RandomForest.png

- 자료 제목: cm_RandomForest
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/figures/cm_RandomForest.png`
- 파일 지문 SHA-256: `c31890237d80dd5cf7b070756be4fa8e73bf7257ae98f4256df932655d1d055b`

## png/3_cm_SVM_RBF.png

- 자료 제목: cm_SVM_RBF
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/figures/cm_SVM_RBF.png`
- 파일 지문 SHA-256: `bae0dacd036a561d25f5b7c99ef8103d01361270597e8c2f800a4fa886bf3644`

## png/3_feature_medians.png

- 자료 제목: feature_medians
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/figures/feature_medians.png`
- 파일 지문 SHA-256: `9934627c2d96c414b8b2d2cdadfa61a4aa9c5686c53a62a4c1b680e221da0f06`

## png/3_gas_recall.png

- 자료 제목: gas_recall
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/figures/gas_recall.png`
- 파일 지문 SHA-256: `9b4924bd82777896e8e3cee11ab7e2376a9e1848bd6a94446e0d78bef55c7056`

## png/3_lr_coefficients.png

- 자료 제목: lr_coefficients
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/figures/lr_coefficients.png`
- 파일 지문 SHA-256: `e2df7588860752ea78d68193a53d0ff082fbe2dbdbdda600b7f124eac60e93a8`

## png/3_pca_same_gas.png

- 자료 제목: pca_same_gas
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/figures/pca_same_gas.png`
- 파일 지문 SHA-256: `94bb07fa260c0d72d4d2934d94bff013dff5ade51ba42417609f4c5db395ac27`

## png/3_rf_importance.png

- 자료 제목: rf_importance
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/figures/rf_importance.png`
- 파일 지문 SHA-256: `0d6d1730e6700405db83c57c06de30a5d1536f8df0d4ba55f1d3ecb2f485b866`

## png/3_shift_error_association.png

- 자료 제목: shift_error_association
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/figures/shift_error_association.png`
- 파일 지문 SHA-256: `b70b15cb4d31b3fbbd701a7141ce1528833f8fa610687d1b5925432ad6aeddfc`

## png/3_svm_sensitivity.png

- 자료 제목: svm_sensitivity
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/figures/svm_sensitivity.png`
- 파일 지문 SHA-256: `0856e813a28791eb37251984ef0b9c14b3139097c55eb1df38fc8b467d58dfb8`

## png/3_wasserstein.png

- 자료 제목: wasserstein
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/figures/wasserstein.png`
- 파일 지문 SHA-256: `61ae5044736c84c1032d54168371655f77a6eefe5f4529d5ea81b586cc7d0eaa`

## tables/3_batch_associations.csv

- 자료 제목: batch_associations
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/batch_associations.csv`
- 파일 지문 SHA-256: `99e738217f16136c34f86b1dd23d77a1b61b098f063630c001d10bfdcd8d69d3`

## tables/3_batch_shift.csv

- 자료 제목: batch_shift
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/batch_shift.csv`
- 파일 지문 SHA-256: `e59d453d256963d27fac61613548cad129c1c68a776f17121f17043e1990cf2c`

## tables/3_confusion_matrices.csv

- 자료 제목: confusion_matrices
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/confusion_matrices.csv`
- 파일 지문 SHA-256: `9479da4507e0cd383e8266f8432e38caa84cb8287dac921a32dfaf7501a81eeb`

## tables/3_correlated_feature_pairs.csv

- 자료 제목: correlated_feature_pairs
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/correlated_feature_pairs.csv`
- 파일 지문 SHA-256: `4565671d6bbd0ecb247aaf81c64fa1acf9e1f6c13a91e294a0e0bce5a1de6aa8`

## tables/3_costs.csv

- 자료 제목: costs
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/costs.csv`
- 파일 지문 SHA-256: `86cf15daa5166e6550503e069d88e0c35415e0742ce3280d3f191e4550322712`

## tables/3_error_pairs.csv

- 자료 제목: error_pairs
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/error_pairs.csv`
- 파일 지문 SHA-256: `0b51e82e11b9a13be1b2b6712812a793192cf1cdbd82ef534b18651dce9baee2`

## tables/3_feature_associations.csv

- 자료 제목: feature_associations
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/feature_associations.csv`
- 파일 지문 SHA-256: `64134a5360c2b5185eb7f41a242b267bb058af31398cc71e9e1887f390ec97bf`

## tables/3_feature_stats.csv

- 자료 제목: feature_stats
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/feature_stats.csv`
- 파일 지문 SHA-256: `dba1476d9d142dde87285ba5564df3f34462e5df9655f35615fe6e8416a4166c`

## tables/3_gas_associations.csv

- 자료 제목: gas_associations
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/gas_associations.csv`
- 파일 지문 SHA-256: `feb12a71f1139479c7f6ec7d1de153cdcd4c8535f1573d69ca3eb7548ed04390`

## tables/3_gas_errors.csv

- 자료 제목: gas_errors
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/gas_errors.csv`
- 파일 지문 SHA-256: `4431bacda15f588c84f4c9fa0fd036b97dddc79c3fc3fd5c69a6b0bdedcbbf9a`

## tables/3_gas_shift.csv

- 자료 제목: gas_shift
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/gas_shift.csv`
- 파일 지문 SHA-256: `423e2e7cf60b9755d21d30a45a031c5dc39ab1b31e4b3b323f04dd1e26bc96bb`

## tables/3_lr_coefficients.csv

- 자료 제목: lr_coefficients
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/lr_coefficients.csv`
- 파일 지문 SHA-256: `d82dfa8eadf3e8587f9b6292b7f6ea271e84400d5b313cf4de45bf85c3bf76ad`

## tables/3_metrics.csv

- 자료 제목: metrics
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/metrics.csv`
- 파일 지문 SHA-256: `89ba99909d06b719f6308df93d5bd6a2ff3ca1323569f6f8b563eb1a0c3d6698`

## tables/3_pca_variance.csv

- 자료 제목: pca_variance
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/pca_variance.csv`
- 파일 지문 SHA-256: `e77c06204618ccb9d7787eb9216ffe68e37db1cf9a40b261f488ee2f53a18f4d`

## tables/3_rf_importance.csv

- 자료 제목: rf_importance
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/rf_importance.csv`
- 파일 지문 SHA-256: `9f62d7ce861bdbeab2081a850686da6c09c3ade5fa2443761b96ace95d96a38e`

## tables/3_selection_evidence.csv

- 자료 제목: selection_evidence
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/selection_evidence.csv`
- 파일 지문 SHA-256: `fa6ab4ee7f35b6c455d7ad70ee28a3f12bbf4f920d55ecc3d813ad460d73077e`

## tables/3_svm_sensitivity.csv

- 자료 제목: svm_sensitivity
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/svm_sensitivity.csv`
- 파일 지문 SHA-256: `54a8bf06f9dcd56e5bfb67c9d24293d8247c1a67132d216ce074d4f304b471b9`

## tables/3_train_scores.csv

- 자료 제목: train_scores
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/train_scores.csv`
- 파일 지문 SHA-256: `49c729ce78bc924be0a7673cee505f9e58a82a24e4cb3e1374a04323d267684e`

## tables/3_wasserstein.csv

- 자료 제목: wasserstein
- 실험 목적: 3단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_diagnostics/wasserstein.csv`
- 파일 지문 SHA-256: `10a29bc807742163101f9c7c25fa78cc54a5bc03e8ce0d1102d172f461a4fd28`

## png/4_batch_recall.png

- 자료 제목: batch_recall
- 실험 목적: 4단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_analysis/figures/batch_recall.png`
- 파일 지문 SHA-256: `93a2760fdb408ceaaa420a166eb2d53a3ff6005e786d59306c9c07b5731523de`

## png/4_centroid_diagnostic.png

- 자료 제목: centroid_diagnostic
- 실험 목적: 4단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_analysis/figures/centroid_diagnostic.png`
- 파일 지문 SHA-256: `b8530ded4e63043e14294af66f58416ff2eb47ba88e0a83f538d245e3ad0678f`

## png/4_class_counts.png

- 자료 제목: class_counts
- 실험 목적: 4단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_analysis/figures/class_counts.png`
- 파일 지문 SHA-256: `4321ab3a1b6a59f1a0deedd3a7c538f2d80c7a1865615b34554848886983fb12`

## png/4_distribution_profiles.png

- 자료 제목: distribution_profiles
- 실험 목적: 4단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_analysis/figures/distribution_profiles.png`
- 파일 지문 SHA-256: `ff23408fa8a21d95e6bf04adecc40779d29991ec9e25e09dc8f8d1d9962fe9be`

## png/4_existing_pca.png

- 자료 제목: existing_pca
- 실험 목적: 4단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_analysis/figures/existing_pca.png`
- 파일 지문 SHA-256: `549886571dab3b1c34f1066e6dce8f82f426c68ca77926981fb96e166f737451`

## png/4_feature_boxes.png

- 자료 제목: feature_boxes
- 실험 목적: 4단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_analysis/figures/feature_boxes.png`
- 파일 지문 SHA-256: `49ba3df31a6c99585a39494a1cd256a22d8bb4dfe52069588475613451e3bc46`

## png/4_partition_recall.png

- 자료 제목: partition_recall
- 실험 목적: 4단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_analysis/figures/partition_recall.png`
- 파일 지문 SHA-256: `406cc86641ac4f320fd36178b36fa543fdd7c878ca8cec9018e03206e8a86be3`

## png/4_toluene_confusion.png

- 자료 제목: toluene_confusion
- 실험 목적: 4단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_analysis/figures/toluene_confusion.png`
- 파일 지문 SHA-256: `b3d6f0ad06601af180076a3f567148b34e5ae4a8c4930088f1bca6e4a13dbdb8`

## tables/4_batch_class_counts.csv

- 자료 제목: batch_class_counts
- 실험 목적: 4단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_analysis/batch_class_counts.csv`
- 파일 지문 SHA-256: `ea1e5369071d328f327b298e82e9a0cd96107c351aff82332647fadea7dc08ac`

## tables/4_centroid_distances.csv

- 자료 제목: centroid_distances
- 실험 목적: 4단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_analysis/centroid_distances.csv`
- 파일 지문 SHA-256: `54a932b893f0f0dd008f503adc03c22b7e7fed8a80b1f908518060613f016418`

## tables/4_consensus.csv

- 자료 제목: consensus
- 실험 목적: 4단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_analysis/consensus.csv`
- 파일 지문 SHA-256: `2343f70e42430cb973f537b68047b548355fdb24d0d72126dfa412a5037d963b`

## tables/4_exploratory_protocol.csv

- 자료 제목: exploratory_protocol
- 실험 목적: 4단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_analysis/exploratory_protocol.csv`
- 파일 지문 SHA-256: `d755d3c2cfd94f9aa02d0821b38cc7ade087d0667ddf32c8996d6fffc3adab32`

## tables/4_feature_distances.csv

- 자료 제목: feature_distances
- 실험 목적: 4단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_analysis/feature_distances.csv`
- 파일 지문 SHA-256: `eb96ae2e635d3bef0ab57b300f953f6c2feb298ec27e312002fae8ce7ee031de`

## tables/4_feature_stats.csv

- 자료 제목: feature_stats
- 실험 목적: 4단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_analysis/feature_stats.csv`
- 파일 지문 SHA-256: `dba1476d9d142dde87285ba5564df3f34462e5df9655f35615fe6e8416a4166c`

## tables/4_gas_profiles.csv

- 자료 제목: gas_profiles
- 실험 목적: 4단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_analysis/gas_profiles.csv`
- 파일 지문 SHA-256: `feaba3d922f11ca3cb82ac0533c753f5a5a4f7b043050d1c69e7b98244332d99`

## tables/4_historical_hash_audit.csv

- 자료 제목: historical_hash_audit
- 실험 목적: 4단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_analysis/historical_hash_audit.csv`
- 파일 지문 SHA-256: `c7d5030bb2eca157ce82447d4b1198744677f5adfed97340d11139ee43bf0970`

## tables/4_model_audit.csv

- 자료 제목: model_audit
- 실험 목적: 4단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_analysis/model_audit.csv`
- 파일 지문 SHA-256: `e334dfdc70ba61d1da6f65bd32b1e433fabe88b514cba4168d49cf7b97a37d7f`

## tables/4_model_scores.csv

- 자료 제목: model_scores
- 실험 목적: 4단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_analysis/model_scores.csv`
- 파일 지문 SHA-256: `a5e133c1d87a78ebef3b0b5a2fbbb991fae00a52b1e91c1d23081643e911a35e`

## tables/4_partition_counts.csv

- 자료 제목: partition_counts
- 실험 목적: 4단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_analysis/partition_counts.csv`
- 파일 지문 SHA-256: `82d7a73aeb012c80cefbc3e56a2157d6c0e648a24b453fdcebfdfc160f0f135e`

## tables/4_source_ast_audit.csv

- 자료 제목: source_ast_audit
- 실험 목적: 4단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_analysis/source_ast_audit.csv`
- 파일 지문 SHA-256: `d6433ec0aeab829055a508769da0cbdcae9149286f7b1c244947ac1ffdcffadd`

## tables/4_toluene_confusion.csv

- 자료 제목: toluene_confusion
- 실험 목적: 4단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_analysis/toluene_confusion.csv`
- 파일 지문 SHA-256: `5e65a52bedaca03d5bc18da5b478d6c451880b744c1570486be8dacd7add65ff`

## tables/4_toluene_metrics.csv

- 자료 제목: toluene_metrics
- 실험 목적: 4단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 전체 13,910행의 EDA 또는 초기 랜덤/시간순 실험. 각 원본 표의 experiment·partition·scope·support 구분 필수. EDA 전체자료 변환기는 평가에 재사용하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_analysis/toluene_metrics.csv`
- 파일 지문 SHA-256: `d65af1cd3f7843ba3338ffeb7a567acef5c6a495510bd7f57f0c7a1b7d01e327`

## png/5_candidate_batches.png

- 자료 제목: candidate_batches
- 실험 목적: 5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 기존 Test를 제외한 제한된 과거 개발 표본. 6단계 이후 확장 실험과 학습 범위가 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_improvement/figures/candidate_batches.png`
- 파일 지문 SHA-256: `84df8657c7a1adb64b8d9cbdc60bd9bc810a7b5c4ea7a26803fea0dd1aecc6c0`

## png/5_candidate_confusion.png

- 자료 제목: candidate_confusion
- 실험 목적: 5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 기존 Test를 제외한 제한된 과거 개발 표본. 6단계 이후 확장 실험과 학습 범위가 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_improvement/figures/candidate_confusion.png`
- 파일 지문 SHA-256: `4cf87521d8a5d21ae2b5de3a59b44027c319e70dc2786b9b1a095b75818d5a64`

## png/5_candidate_generalization.png

- 자료 제목: candidate_generalization
- 실험 목적: 5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 기존 Test를 제외한 제한된 과거 개발 표본. 6단계 이후 확장 실험과 학습 범위가 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_improvement/figures/candidate_generalization.png`
- 파일 지문 SHA-256: `02b7cee727cef3aa5b4dd9bc7387c9eb36d196f28a4a9a390950597816f82a93`

## png/5_frozen_expansion.png

- 자료 제목: frozen_expansion
- 실험 목적: 5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 기존 Test를 제외한 제한된 과거 개발 표본. 6단계 이후 확장 실험과 학습 범위가 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_improvement/figures/frozen_expansion.png`
- 파일 지문 SHA-256: `5af6d7f6027605d7ca27015a6ba9fc4242a4088af89a719a85db7d251e9ae2cb`

## png/5_validation_trials.png

- 자료 제목: validation_trials
- 실험 목적: 5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 기존 Test를 제외한 제한된 과거 개발 표본. 6단계 이후 확장 실험과 학습 범위가 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_improvement/figures/validation_trials.png`
- 파일 지문 SHA-256: `3ee675f13577adecf5d3c7d2962ab51b254458da2655e3878ec0ea9b9ed3f93c`

## tables/5_baseline_reproduction.csv

- 자료 제목: baseline_reproduction
- 실험 목적: 5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 기존 Test를 제외한 제한된 과거 개발 표본. 6단계 이후 확장 실험과 학습 범위가 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_improvement/baseline_reproduction.csv`
- 파일 지문 SHA-256: `711fafa453fcf35d4eaea031b78237f49c03f7882fbbf55261bc93162a550e78`

## tables/5_confusion_matrices.csv

- 자료 제목: confusion_matrices
- 실험 목적: 5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 기존 Test를 제외한 제한된 과거 개발 표본. 6단계 이후 확장 실험과 학습 범위가 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_improvement/confusion_matrices.csv`
- 파일 지문 SHA-256: `57031fe9577ed42a4b1c2af00ff34312604ea01e81d22b891cf987da5043ed1a`

## tables/5_cost_summary.csv

- 자료 제목: cost_summary
- 실험 목적: 5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 기존 Test를 제외한 제한된 과거 개발 표본. 6단계 이후 확장 실험과 학습 범위가 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_improvement/cost_summary.csv`
- 파일 지문 SHA-256: `dc68b79914d09ececfe641e53dff16be558b2ceba6c25b02264aff0bf8959943`

## tables/5_frozen_baseline_metrics.csv

- 자료 제목: frozen_baseline_metrics
- 실험 목적: 5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 기존 Test를 제외한 제한된 과거 개발 표본. 6단계 이후 확장 실험과 학습 범위가 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_improvement/frozen_baseline_metrics.csv`
- 파일 지문 SHA-256: `c4745e35e7a60b28b11ba0f70ca6dcaf15209bdaeb08b2fddc1c9b5ef921160c`

## tables/5_improvement_deltas.csv

- 자료 제목: improvement_deltas
- 실험 목적: 5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 기존 Test를 제외한 제한된 과거 개발 표본. 6단계 이후 확장 실험과 학습 범위가 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_improvement/improvement_deltas.csv`
- 파일 지문 SHA-256: `8a9a13c6883383591005fde674451c756af4dcf965ab37dddd4b04838f1bce74`

## tables/5_metrics.csv

- 자료 제목: metrics
- 실험 목적: 5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 기존 Test를 제외한 제한된 과거 개발 표본. 6단계 이후 확장 실험과 학습 범위가 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_improvement/metrics.csv`
- 파일 지문 SHA-256: `94b5f0e97d49e4a432e82e9bcfafec074eda143b38efd54b878017687aad71c9`

## tables/5_per_class_metrics.csv

- 자료 제목: per_class_metrics
- 실험 목적: 5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 기존 Test를 제외한 제한된 과거 개발 표본. 6단계 이후 확장 실험과 학습 범위가 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_improvement/per_class_metrics.csv`
- 파일 지문 SHA-256: `3082995b3a496e7756c008a97504996328c842caff2e38ab3a6e0907550d2103`

## tables/5_split_class_counts.csv

- 자료 제목: split_class_counts
- 실험 목적: 5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 기존 Test를 제외한 제한된 과거 개발 표본. 6단계 이후 확장 실험과 학습 범위가 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_improvement/split_class_counts.csv`
- 파일 지문 SHA-256: `9e2d073e608e1fc78cad83a7ae49fc6a47ab56482b3dd9124abfabb343bc9d48`

## tables/5_test_batch_stability.csv

- 자료 제목: test_batch_stability
- 실험 목적: 5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 기존 Test를 제외한 제한된 과거 개발 표본. 6단계 이후 확장 실험과 학습 범위가 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_improvement/test_batch_stability.csv`
- 파일 지문 SHA-256: `029b5a594a00298273e8204c5ad154c446cec7ac5d21e4c5ec158f4f7b6ce281`

## tables/5_validation_metrics.csv

- 자료 제목: validation_metrics
- 실험 목적: 5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 기존 Test를 제외한 제한된 과거 개발 표본. 6단계 이후 확장 실험과 학습 범위가 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/model_improvement/validation_metrics.csv`
- 파일 지문 SHA-256: `92b088d07cfefa7dfebc35988a54a3b7c62655c2c217f9069fa9ce384a47509f`

## png/6_candidate_batch_scores.png

- 자료 제목: candidate_batch_scores
- 실험 목적: 6단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Validation 동일 Batch 가중 Macro F1 0.897000. 9–10은 동일 가중0.602705, pooled0.558657로 구분함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_expansion/candidate_batch_scores.png`
- 파일 지문 SHA-256: `6b421813030d09ba1ce37dc8f08bb93bd2539b88e37cc40a24edd4741282770d`

## png/6_confusion_evaluation.png

- 자료 제목: confusion_evaluation
- 실험 목적: 6단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Validation 동일 Batch 가중 Macro F1 0.897000. 9–10은 동일 가중0.602705, pooled0.558657로 구분함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_expansion/confusion_evaluation.png`
- 파일 지문 SHA-256: `57b7c70e5a46815375be42144e2be5e9d6bf834c33a027689dd88f9264aa0086`

## png/6_confusion_validation.png

- 자료 제목: confusion_validation
- 실험 목적: 6단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Validation 동일 Batch 가중 Macro F1 0.897000. 9–10은 동일 가중0.602705, pooled0.558657로 구분함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_expansion/confusion_validation.png`
- 파일 지문 SHA-256: `b9d33985601a1ba83b2f7f4d762919f0e3afc3fcd192fcc28a51672898b2cbe8`

## png/6_training_range_comparison.png

- 자료 제목: training_range_comparison
- 실험 목적: 6단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Validation 동일 Batch 가중 Macro F1 0.897000. 9–10은 동일 가중0.602705, pooled0.558657로 구분함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_expansion/training_range_comparison.png`
- 파일 지문 SHA-256: `b327b78d693f094c56280f0640525d9918aff7872ed4e3df10ea7d4434ec8d60`

## png/6_training_range_comparison_01_a0ff7d.png

- 자료 제목: training_range_comparison
- 실험 목적: 6단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Validation 동일 Batch 가중 Macro F1 0.897000. 9–10은 동일 가중0.602705, pooled0.558657로 구분함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `reports/temporal_expansion_report.html#image-1`
- 파일 지문 SHA-256: `a0ff7de4932417a9ca04775220fa3c281b8c5bf16c936c90c0c778f3a3ae6354`

## png/6_candidate_batch_scores_02_973e05.png

- 자료 제목: candidate_batch_scores
- 실험 목적: 6단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Validation 동일 Batch 가중 Macro F1 0.897000. 9–10은 동일 가중0.602705, pooled0.558657로 구분함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `reports/temporal_expansion_report.html#image-2`
- 파일 지문 SHA-256: `973e051ae33b705086c01595cd8fbde2f83a928a0805865da05461ea134d44ff`

## png/6_confusion_validation_03_b5707f.png

- 자료 제목: confusion_validation
- 실험 목적: 6단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Validation 동일 Batch 가중 Macro F1 0.897000. 9–10은 동일 가중0.602705, pooled0.558657로 구분함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `reports/temporal_expansion_report.html#image-3`
- 파일 지문 SHA-256: `b5707f6aba26fb66935a85a5b8ee35ae2c903301e542149238513a23f8cb56de`

## png/6_confusion_evaluation_04_7e9e20.png

- 자료 제목: confusion_evaluation
- 실험 목적: 6단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Validation 동일 Batch 가중 Macro F1 0.897000. 9–10은 동일 가중0.602705, pooled0.558657로 구분함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `reports/temporal_expansion_report.html#image-4`
- 파일 지문 SHA-256: `7e9e2090c5b6e7fc793b7733ba483a2670f3a7c80dfaaa271e4daf3b1a86c624`

## tables/6_batch_class_counts.csv

- 자료 제목: batch_class_counts
- 실험 목적: 6단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Validation 동일 Batch 가중 Macro F1 0.897000. 9–10은 동일 가중0.602705, pooled0.558657로 구분함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_expansion/batch_class_counts.csv`
- 파일 지문 SHA-256: `d4671ce9a65deb88e56df3427cb6d22f82e498cbaf00006dbedc8c01417949b4`

## tables/6_confusion_matrices.csv

- 자료 제목: confusion_matrices
- 실험 목적: 6단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Validation 동일 Batch 가중 Macro F1 0.897000. 9–10은 동일 가중0.602705, pooled0.558657로 구분함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_expansion/confusion_matrices.csv`
- 파일 지문 SHA-256: `1ba8e1e52afef2cd3a6d477f30cc06c0277bbf6c52ebebddad0604f9dfdb1854`

## tables/6_expansion_deltas.csv

- 자료 제목: expansion_deltas
- 실험 목적: 6단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Validation 동일 Batch 가중 Macro F1 0.897000. 9–10은 동일 가중0.602705, pooled0.558657로 구분함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_expansion/expansion_deltas.csv`
- 파일 지문 SHA-256: `066ee2f01c874c8a7570eeb4643fc0af903546fce16be4499615c7bfce74f796`

## tables/6_improvement_deltas.csv

- 자료 제목: improvement_deltas
- 실험 목적: 6단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Validation 동일 Batch 가중 Macro F1 0.897000. 9–10은 동일 가중0.602705, pooled0.558657로 구분함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_expansion/improvement_deltas.csv`
- 파일 지문 SHA-256: `d7d3b0612269135ad262bce91110fa61761572b55557311795d39fa89346fac0`

## tables/6_metrics.csv

- 자료 제목: metrics
- 실험 목적: 6단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Validation 동일 Batch 가중 Macro F1 0.897000. 9–10은 동일 가중0.602705, pooled0.558657로 구분함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_expansion/metrics.csv`
- 파일 지문 SHA-256: `59dade7a829bbf4bd70e62a9b84161e3b1eb144ba5bc578ba279d10d2cb6e517`

## tables/6_per_class_metrics.csv

- 자료 제목: per_class_metrics
- 실험 목적: 6단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Validation 동일 Batch 가중 Macro F1 0.897000. 9–10은 동일 가중0.602705, pooled0.558657로 구분함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_expansion/per_class_metrics.csv`
- 파일 지문 SHA-256: `54e04563a114b140727409c91d1d5292b5df050873d7426298b7013f46ce0f5d`

## tables/6_summary_metrics.csv

- 자료 제목: summary_metrics
- 실험 목적: 6단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Validation 동일 Batch 가중 Macro F1 0.897000. 9–10은 동일 가중0.602705, pooled0.558657로 구분함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_expansion/summary_metrics.csv`
- 파일 지문 SHA-256: `e0575e7480e1fc32d3f1b1eb11f916f579a6a2ad1e7a787a0528169894396258`

## tables/6_validation_metrics.csv

- 자료 제목: validation_metrics
- 실험 목적: 6단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Validation 동일 Batch 가중 Macro F1 0.897000. 9–10은 동일 가중0.602705, pooled0.558657로 구분함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_expansion/validation_metrics.csv`
- 파일 지문 SHA-256: `3efeed1f7865c78eb0706fad0a7ae9d62221bb59fc853e03c783e883d9b4bc7e`

## png/7_batch_confusion_matrices.png

- 자료 제목: batch_confusion_matrices
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_failure_diagnostics/batch_confusion_matrices.png`
- 파일 지문 SHA-256: `463b66806be76f69c463a298b8455b4735c1985ba1d9ef5f0961a2977e215ebe`

## png/7_batch_performance.png

- 자료 제목: batch_performance
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_failure_diagnostics/batch_performance.png`
- 파일 지문 SHA-256: `84afb5f2b467fd2ff5c371fff715d004a7717471ddb88c0b4df01a8779a62a8a`

## png/7_conditional_feature_shift.png

- 자료 제목: conditional_feature_shift
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_failure_diagnostics/conditional_feature_shift.png`
- 파일 지문 SHA-256: `c5e0731a76d3e9bc9de383041b758f21be31784229c1dab29ca2d2f43403b7b3`

## png/7_focus_Acetaldehyde_distribution.png

- 자료 제목: focus_Acetaldehyde_distribution
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_failure_diagnostics/focus_Acetaldehyde_distribution.png`
- 파일 지문 SHA-256: `b3c30444599b01a241c4f986a63d8979d4bd4741dbb272951170e6a1bbf29df8`

## png/7_focus_Toluene_distribution.png

- 자료 제목: focus_Toluene_distribution
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_failure_diagnostics/focus_Toluene_distribution.png`
- 파일 지문 SHA-256: `5df627b7b329fe278f6434c583429a8735d689314837dd49fa98e537a77fe8a1`

## png/7_batch_performance_01_911e4b.png

- 자료 제목: batch_performance
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `reports/temporal_failure_diagnostic_report.html#image-1`
- 파일 지문 SHA-256: `911e4bfc6d557d3b75d32424da9afa8e41e161f55ef42ec181a6f28b3273c26c`

## png/7_batch_confusion_matrices_02_2585c4.png

- 자료 제목: batch_confusion_matrices
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `reports/temporal_failure_diagnostic_report.html#image-2`
- 파일 지문 SHA-256: `2585c49cb1d16b38b4e9f3fe32ff2f18748d953989c0ae091834103ba12ae0c5`

## png/7_conditional_feature_shift_03_7d9db6.png

- 자료 제목: conditional_feature_shift
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `reports/temporal_failure_diagnostic_report.html#image-3`
- 파일 지문 SHA-256: `7d9db6f11d2389b0cad0585790b2c6da488219fdd01f839ffbcaddf34aa54766`

## png/7_focus_Toluene_distribution_04_1e3cf6.png

- 자료 제목: focus_Toluene_distribution
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `reports/temporal_failure_diagnostic_report.html#image-4`
- 파일 지문 SHA-256: `1e3cf6600273bda91b34020d28898a7701f46023c468e8fdb9ffb16b32d1cc3e`

## png/7_focus_Acetaldehyde_distribution_05_0cb817.png

- 자료 제목: focus_Acetaldehyde_distribution
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `reports/temporal_failure_diagnostic_report.html#image-5`
- 파일 지문 SHA-256: `0cb817b3816e3a985e879ba1e656fd5d53a0255fa919c1b4705f77c3c0cfb713`

## tables/7_batch_class_counts.csv

- 자료 제목: batch_class_counts
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_failure_diagnostics/batch_class_counts.csv`
- 파일 지문 SHA-256: `d4671ce9a65deb88e56df3427cb6d22f82e498cbaf00006dbedc8c01417949b4`

## tables/7_batch_metrics.csv

- 자료 제목: batch_metrics
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_failure_diagnostics/batch_metrics.csv`
- 파일 지문 SHA-256: `3f647847fd1c00218f2416fe5c6b8a7d26fa1c0674427d386d3db287eb56f705`

## tables/7_class_metrics.csv

- 자료 제목: class_metrics
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_failure_diagnostics/class_metrics.csv`
- 파일 지문 SHA-256: `0cb6b1945dbf22edfd4a54654699ae4821df4d16896205849ced8d2ead907076`

## tables/7_confusion_counts.csv

- 자료 제목: confusion_counts
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_failure_diagnostics/confusion_counts.csv`
- 파일 지문 SHA-256: `d67c151b8ca02a7423828d04e182b765fa49ff4e3d2642230454f0f5433e7513`

## tables/7_correctness_patterns.csv

- 자료 제목: correctness_patterns
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_failure_diagnostics/correctness_patterns.csv`
- 파일 지문 SHA-256: `0a17b7ce37eb8a5c6888bc8616d367ddd560f48471a59b77275c975214ab7689`

## tables/7_extreme_response_summary.csv

- 자료 제목: extreme_response_summary
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_failure_diagnostics/extreme_response_summary.csv`
- 파일 지문 SHA-256: `de5ec39e31266495b83b126209e3b8fe2c3aedabda214c5558aea6d0ab4b7fc6`

## tables/7_feature_shifts.csv

- 자료 제목: feature_shifts
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_failure_diagnostics/feature_shifts.csv`
- 파일 지문 SHA-256: `6eac4fb5becf824d74434c0544fb90c422a67ec166701de72231f31238e6b1b3`

## tables/7_feature_summary.csv

- 자료 제목: feature_summary
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_failure_diagnostics/feature_summary.csv`
- 파일 지문 SHA-256: `188046ac7636368a2322635785c3b98395723c858ae2214c2615cb31d618fd43`

## tables/7_hypothesis_evidence.csv

- 자료 제목: hypothesis_evidence
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_failure_diagnostics/hypothesis_evidence.csv`
- 파일 지문 SHA-256: `828ca816c40da36052e21f42088ae584856cbf88f3adb0b51914cd9236a1c892`

## tables/7_improvement_priorities.csv

- 자료 제목: improvement_priorities
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_failure_diagnostics/improvement_priorities.csv`
- 파일 지문 SHA-256: `e007690daddaa94d8098c6f92677e60ceafbc5969a6f733e1b0f19f76a06be4c`

## tables/7_lr_svm_error_group_features.csv

- 자료 제목: lr_svm_error_group_features
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_failure_diagnostics/lr_svm_error_group_features.csv`
- 파일 지문 SHA-256: `fd401cb33e00071fd2110cd802ea7ebe1c888592ef61412512c7a491aa07421d`

## tables/7_model_agreement.csv

- 자료 제목: model_agreement
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_failure_diagnostics/model_agreement.csv`
- 파일 지문 SHA-256: `12d921eba5b43eee96cf6fc9fbca374fdcf1a8b4ea162157c0fa049581201b56`

## tables/7_model_feature_dependence.csv

- 자료 제목: model_feature_dependence
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_failure_diagnostics/model_feature_dependence.csv`
- 파일 지문 SHA-256: `8c74a1e573a9afdc7049d8706ab9a31c45fe65a4be81583f7a9a61bf3ea177ee`

## tables/7_nearest_train_gas_counts.csv

- 자료 제목: nearest_train_gas_counts
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_failure_diagnostics/nearest_train_gas_counts.csv`
- 파일 지문 SHA-256: `d615d57b1b0d569ef3ccc383fddc6ba97fdda1698373201aa16590944cf1ac0b`

## tables/7_pairwise_agreement.csv

- 자료 제목: pairwise_agreement
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_failure_diagnostics/pairwise_agreement.csv`
- 파일 지문 SHA-256: `b643ffaf7f79f954b674a324c08a7a596d410e27ab9cb21059a6250b3fddefd1`

## tables/7_proximity_summary.csv

- 자료 제목: proximity_summary
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_failure_diagnostics/proximity_summary.csv`
- 파일 지문 SHA-256: `a6978950a371d5aaa8902ce444883a42dbfccc96d2a294d4dd8973ba3fd8ba8d`

## tables/7_replay_checks.csv

- 자료 제목: replay_checks
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_failure_diagnostics/replay_checks.csv`
- 파일 지문 SHA-256: `f7b6ec6825de46d93b329fbd81e4e7fb278255c5df1a8bc1e16e873e976ff3ee`

## tables/7_sample_proximity.csv

- 자료 제목: sample_proximity
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_failure_diagnostics/sample_proximity.csv`
- 파일 지문 SHA-256: `f79e148df57b96dc13a6e5d0125f85661ebddeb7649c65d91e224d22b8d55d4e`

## tables/7_selected_feature_correlations.csv

- 자료 제목: selected_feature_correlations
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_failure_diagnostics/selected_feature_correlations.csv`
- 파일 지문 SHA-256: `c83c5e0ab5344e7e9a89a31ce3abf31fa22529f3d70d14c685af8b60dfe34105`

## tables/7_selected_plot_features.csv

- 자료 제목: selected_plot_features
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_failure_diagnostics/selected_plot_features.csv`
- 파일 지문 SHA-256: `5d11fa29b2714c64e58963ccac01eda9c821fb06e74d96a7a5509d4e5d58e909`

## tables/7_shift_and_performance.csv

- 자료 제목: shift_and_performance
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_failure_diagnostics/shift_and_performance.csv`
- 파일 지문 SHA-256: `41c7488932b75faf9e350854a0b5fdcf50a284b1a247fc9ee84ad2e77541e928`

## tables/7_top_misclassifications.csv

- 자료 제목: top_misclassifications
- 실험 목적: 7단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Model A Batch9 Toluene 0/101, Batch10 Acetaldehyde Recall0.14. 합산 결과가 Batch별 실패를 숨길 수 있음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_failure_diagnostics/top_misclassifications.csv`
- 파일 지문 SHA-256: `813d6df8f86fc7876dd17ba121b9d133021ae7378cd0b3ad1e73b4a9c595158a`

## png/8_candidate_baseline_confusion.png

- 자료 제목: candidate_baseline_confusion
- 실험 목적: 8단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_robustness/candidate_baseline_confusion.png`
- 파일 지문 SHA-256: `3972f041e10ad4ea454fc13a2182a18cc405df3228084a1cccd43dbc710a3304`

## png/8_cv_configuration_comparison.png

- 자료 제목: cv_configuration_comparison
- 실험 목적: 8단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_robustness/cv_configuration_comparison.png`
- 파일 지문 SHA-256: `3907e84ae3510d6a5ec6ea2580c8c9b338a59b951e17c649e747b2f257fda294`

## png/8_exploratory_batch_scores.png

- 자료 제목: exploratory_batch_scores
- 실험 목적: 8단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_robustness/exploratory_batch_scores.png`
- 파일 지문 SHA-256: `744ee0c9c63947e2e7bfd1ef2c023496de709e376880962b9e07397d7d4cc983`

## png/8_feature_selection_effect.png

- 자료 제목: feature_selection_effect
- 실험 목적: 8단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_robustness/feature_selection_effect.png`
- 파일 지문 SHA-256: `b0159ab66dea2e9e749b40bc89a458c5e8cf8602b95c0d72296b7d137e96be3a`

## png/8_feature_selection_effect_01_552afe.png

- 자료 제목: feature_selection_effect
- 실험 목적: 8단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `reports/temporal_robustness_improvement_report.html#image-1`
- 파일 지문 SHA-256: `552afed7d207d1d756b439e0100b8145f62b6e144b5ab1de2d6f84a13bd3d14b`

## png/8_cv_configuration_comparison_02_1b9824.png

- 자료 제목: cv_configuration_comparison
- 실험 목적: 8단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `reports/temporal_robustness_improvement_report.html#image-2`
- 파일 지문 SHA-256: `1b98243917345de3e2b97ae93da698ca9a1566afcda5200528dd83ac7424f434`

## png/8_exploratory_batch_scores_03_324163.png

- 자료 제목: exploratory_batch_scores
- 실험 목적: 8단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `reports/temporal_robustness_improvement_report.html#image-3`
- 파일 지문 SHA-256: `324163a675dce49d1afafe9b812b929e1462c3d1c9d561b99d3edd4b91a18d6a`

## png/8_candidate_baseline_confusion_04_0fc9d3.png

- 자료 제목: candidate_baseline_confusion
- 실험 목적: 8단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `reports/temporal_robustness_improvement_report.html#image-4`
- 파일 지문 SHA-256: `0fc9d3585d92d70753ca06448fa2c279db53b9cc8f2dc36738ab68cfdd516d95`

## tables/8_cv_summary.csv

- 자료 제목: cv_summary
- 실험 목적: 8단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_robustness/cv_summary.csv`
- 파일 지문 SHA-256: `39eba31eb1effdaf9ad663634710cabcd1d9bb4783c47f5fcb5d77f4eed078f9`

## tables/8_evaluation_class_metrics.csv

- 자료 제목: evaluation_class_metrics
- 실험 목적: 8단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_robustness/evaluation_class_metrics.csv`
- 파일 지문 SHA-256: `4dc4836916c8afa19974c0aa8ad34dbf70af7aeb7d7f1404daf29e22abff715d`

## tables/8_evaluation_confusion.csv

- 자료 제목: evaluation_confusion
- 실험 목적: 8단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_robustness/evaluation_confusion.csv`
- 파일 지문 SHA-256: `d72927243a46f71633a8a48c6dc86d3e0bdb6a090115f1509cd5024816f63528`

## tables/8_evaluation_metrics.csv

- 자료 제목: evaluation_metrics
- 실험 목적: 8단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_robustness/evaluation_metrics.csv`
- 파일 지문 SHA-256: `257a54a8e90be87b113efd71d6c36293c0342335168050aa49f89268b40faa89`

## tables/8_evaluation_model_hashes.csv

- 자료 제목: evaluation_model_hashes
- 실험 목적: 8단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_robustness/evaluation_model_hashes.csv`
- 파일 지문 SHA-256: `2310c2aa3dfc24e950a70675f2974547e13474580fe7b3a99af7fe2e91613aa7`

## tables/8_evaluation_summary.csv

- 자료 제목: evaluation_summary
- 실험 목적: 8단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_robustness/evaluation_summary.csv`
- 파일 지문 SHA-256: `56a247f76e60c5e36657614f50cdf4540418a06a621f9ad597c21fff4cb496a0`

## tables/8_evaluation_times.csv

- 자료 제목: evaluation_times
- 실험 목적: 8단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_robustness/evaluation_times.csv`
- 파일 지문 SHA-256: `2bfb9fd07633dd5ab259ced12d2ba9d2daf208715216d0123053bb7ae92a1f15`

## tables/8_feature_effects.csv

- 자료 제목: feature_effects
- 실험 목적: 8단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_robustness/feature_effects.csv`
- 파일 지문 SHA-256: `e89d77910f6edb44961898af177a275c909b608088bcafd8f6b7b7617c615229`

## tables/8_feature_selection_details.csv

- 자료 제목: feature_selection_details
- 실험 목적: 8단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_robustness/feature_selection_details.csv`
- 파일 지문 SHA-256: `18ce09eb082917c6e349b28c3f06e2c72ab9fd808ff0d72c3714961aa4bcce77`

## tables/8_fold_class_metrics.csv

- 자료 제목: fold_class_metrics
- 실험 목적: 8단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_robustness/fold_class_metrics.csv`
- 파일 지문 SHA-256: `99198dd031d945b821e0f9ea240d6e27701bc0c9c3ca43e8cfa42ae0f6b835bd`

## tables/8_fold_confusion.csv

- 자료 제목: fold_confusion
- 실험 목적: 8단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_robustness/fold_confusion.csv`
- 파일 지문 SHA-256: `244d4c3ac8e434f5718902bed862807b1255d8740f1a46d28b793d14610a1e9d`

## tables/8_fold_metrics.csv

- 자료 제목: fold_metrics
- 실험 목적: 8단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_robustness/fold_metrics.csv`
- 파일 지문 SHA-256: `cdd19b168d867995bd617829cc2217a22ed904d37bb27f38a5ca37d01f36066f`

## tables/8_fold_support.csv

- 자료 제목: fold_support
- 실험 목적: 8단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_robustness/fold_support.csv`
- 파일 지문 SHA-256: `45aec77e069bac8caf21f2651b8488f2359a4554e3033d0f1131a4391eff39c2`

## tables/8_zero_recall_fold_classes.csv

- 자료 제목: zero_recall_fold_classes
- 실험 목적: 8단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_robustness/zero_recall_fold_classes.csv`
- 파일 지문 SHA-256: `a1f4fef9ee870c4900b6ed6e6160bea27b3c1d36649d544fca85ad1a71869ca3`

## png/9_cv_weighting_comparison.png

- 자료 제목: cv_weighting_comparison
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_weighting/cv_weighting_comparison.png`
- 파일 지문 SHA-256: `7491fe736217ddf7c16d06880705372ff8a45700fcfd16cea092084043754ff0`

## png/9_effective_weights_by_batch.png

- 자료 제목: effective_weights_by_batch
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_weighting/effective_weights_by_batch.png`
- 파일 지문 SHA-256: `02a50f362d0641134671a62894a77a6a1bf94070a16cb00887a633222af30388`

## png/9_evaluation_range_comparison.png

- 자료 제목: evaluation_range_comparison
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_weighting/evaluation_range_comparison.png`
- 파일 지문 SHA-256: `1da272f986b43c2e0296943c10e37a1309873635a4df73103a87f96f00774282`

## png/9_evaluation_range_comparison_before_order_fix.png

- 자료 제목: evaluation_range_comparison_before_order_fix
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_weighting/evaluation_range_comparison_before_order_fix.png`
- 파일 지문 SHA-256: `acc2693d09f6da12fd2863093b2805c15d840fddd03a259676014826328e8ccb`

## png/9_range_expansion_batch8.png

- 자료 제목: range_expansion_batch8
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_weighting/range_expansion_batch8.png`
- 파일 지문 SHA-256: `a5eb8ad9391dbc0652a69d56b62329988e0ca722f5c2c6359abff9b27f6e8a78`

## png/9_weighting_confusion_matrices.png

- 자료 제목: weighting_confusion_matrices
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_weighting/weighting_confusion_matrices.png`
- 파일 지문 SHA-256: `3cb32fb3067848695a4211bd02e4398ca55c430a2e527c9421797a3d71a812cd`

## png/9_effective_weights_by_batch_01_5e78ed.png

- 자료 제목: effective_weights_by_batch
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `reports/temporal_weighting_report.html#image-1`
- 파일 지문 SHA-256: `5e78edf8f5eb6bb544b024ca7253d8d32bf1a4b21f374214b5491489276f1305`

## png/9_cv_weighting_comparison_02_26ef9b.png

- 자료 제목: cv_weighting_comparison
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `reports/temporal_weighting_report.html#image-2`
- 파일 지문 SHA-256: `26ef9b2cec94a1d2c1a16b3ae9242f08ca93c731984a2ee8eb29f76e1d2bedfb`

## png/9_range_expansion_batch8_03_3f9bfa.png

- 자료 제목: range_expansion_batch8
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `reports/temporal_weighting_report.html#image-3`
- 파일 지문 SHA-256: `3f9bfa45fafb8eb6a2c176068e0c893ff5fe3839732e8cab24f17abcc4e4c92a`

## png/9_evaluation_range_comparison_04_8912ff.png

- 자료 제목: evaluation_range_comparison
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `reports/temporal_weighting_report.html#image-4`
- 파일 지문 SHA-256: `8912ffab927495acdf937303c78137d0186d2d5202aae856e15bc92c325239fa`

## png/9_weighting_confusion_matrices_05_1da958.png

- 자료 제목: weighting_confusion_matrices
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `reports/temporal_weighting_report.html#image-5`
- 파일 지문 SHA-256: `1da95890588863de8df4387b3272e0f3ca8bf849e70c5197394031d24b0c7ef4`

## tables/9_baseline_range_effects.csv

- 자료 제목: baseline_range_effects
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_weighting/baseline_range_effects.csv`
- 파일 지문 SHA-256: `218289707cdbfa0e34511e12f3add792a451533bb299cca6d1eaac6c1347b3cd`

## tables/9_class_sample_equivalence_control.csv

- 자료 제목: class_sample_equivalence_control
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_weighting/class_sample_equivalence_control.csv`
- 파일 지문 SHA-256: `d4b425897f70c85028091a74998d4bb2bb4cfd82cf2354a700071cc5cd1adc17`

## tables/9_cv_summary.csv

- 자료 제목: cv_summary
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_weighting/cv_summary.csv`
- 파일 지문 SHA-256: `6a0f7e2a8ac1031d3c2f1c8625faaf553e24a5b2dc7c68b26913448f7a1c0502`

## tables/9_equivalence_evaluation.csv

- 자료 제목: equivalence_evaluation
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_weighting/equivalence_evaluation.csv`
- 파일 지문 SHA-256: `32f601212a08e920b74a346fd72e68c49162d0cf3c840bb19a7d99eef4c9ab9c`

## tables/9_evaluation_classes.csv

- 자료 제목: evaluation_classes
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_weighting/evaluation_classes.csv`
- 파일 지문 SHA-256: `c365baa30e46f38c8ae56a38cece2f130d90fa50ee0a52dca85c5814f64d9c30`

## tables/9_evaluation_confusion.csv

- 자료 제목: evaluation_confusion
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_weighting/evaluation_confusion.csv`
- 파일 지문 SHA-256: `cec1894bda28dbd30dacccc87e24c33013e2748631abd4db6d14a213570a1ed7`

## tables/9_evaluation_metrics.csv

- 자료 제목: evaluation_metrics
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_weighting/evaluation_metrics.csv`
- 파일 지문 SHA-256: `3c1157c6fa2892c0ef379d909fcf1e9e8f93ecb3415a30717facc09e1febe722`

## tables/9_evaluation_models.csv

- 자료 제목: evaluation_models
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_weighting/evaluation_models.csv`
- 파일 지문 SHA-256: `efe1b26f78fbc793cc619a42f26f3219b2477a1722d4afb60f8bac54b162a330`

## tables/9_evaluation_summary.csv

- 자료 제목: evaluation_summary
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_weighting/evaluation_summary.csv`
- 파일 지문 SHA-256: `ee870e908227cd92cc5c883d7b2215d890a06bf07c768a83f86a47a75dbdd058`

## tables/9_evaluation_times.csv

- 자료 제목: evaluation_times
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_weighting/evaluation_times.csv`
- 파일 지문 SHA-256: `2e443baeebfe933449cf2af973ea25df0fff576db94525d0d0994486b8c3c2bb`

## tables/9_fold_class_metrics.csv

- 자료 제목: fold_class_metrics
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_weighting/fold_class_metrics.csv`
- 파일 지문 SHA-256: `c93e4bac0ab6946f6907911d2a49ed47d6ca80501c36d53a89424bb6447074a0`

## tables/9_fold_confusion.csv

- 자료 제목: fold_confusion
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_weighting/fold_confusion.csv`
- 파일 지문 SHA-256: `6c8a35fab208fe2731c3c24b263fa27c0ac6c05d0908e0912ee1863cc079de89`

## tables/9_fold_metrics.csv

- 자료 제목: fold_metrics
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_weighting/fold_metrics.csv`
- 파일 지문 SHA-256: `0baf439dd0cf869ae9c7ac6ceabd27c70ee75d4b92d79a2f3cb5e7a735d39735`

## tables/9_fold_support.csv

- 자료 제목: fold_support
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_weighting/fold_support.csv`
- 파일 지문 SHA-256: `45aec77e069bac8caf21f2651b8488f2359a4554e3033d0f1131a4391eff39c2`

## tables/9_guard_checks.csv

- 자료 제목: guard_checks
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_weighting/guard_checks.csv`
- 파일 지문 SHA-256: `be71709411466945494f7b903ae3339bb159e04095ec1399104b131ae1e727b5`

## tables/9_range_batch8_classes.csv

- 자료 제목: range_batch8_classes
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_weighting/range_batch8_classes.csv`
- 파일 지문 SHA-256: `55f92ee43855601e86efe4e7ae6490da5fbb60f3ae98658ce7542c65199c40b3`

## tables/9_range_batch8_metrics.csv

- 자료 제목: range_batch8_metrics
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_weighting/range_batch8_metrics.csv`
- 파일 지문 SHA-256: `28ca5d8f9b753ba9848db367bc11c25c5081fd828e3f59744235ab7093deab46`

## tables/9_training_range_class_support.csv

- 자료 제목: training_range_class_support
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_weighting/training_range_class_support.csv`
- 파일 지문 SHA-256: `611e848459598f4c99f61bfab8a53c3b2e8fb6aeec8a077f57bffec548bfbbf0`

## tables/9_weight_effects_within_range.csv

- 자료 제목: weight_effects_within_range
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_weighting/weight_effects_within_range.csv`
- 파일 지문 SHA-256: `2b58edddf7f2f34eb48a24097d83a9c74643245c0311cabf376111ce655e0145`

## tables/9_weight_group_summary.csv

- 자료 제목: weight_group_summary
- 실험 목적: 9단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_weighting/weight_group_summary.csv`
- 파일 지문 SHA-256: `4345c07f064339d0751549929144ec4c15dc51700075a23e8702fa0e48c806a1`

## png/10_batch_macro_f1.png

- 자료 제목: batch_macro_f1
- 실험 목적: 10단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 확장 Model B의 9–10 동일 가중 Macro F1 0.700451이나 개발 구간·특정 가스 손실이 남아 Model A를 유지함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_generalization_validation/batch_macro_f1.png`
- 파일 지문 SHA-256: `308b8305740076abd3df8c780e17077796d3083e644ade31ebc5eae9258657c2`

## png/10_class_recall_heatmap.png

- 자료 제목: class_recall_heatmap
- 실험 목적: 10단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 확장 Model B의 9–10 동일 가중 Macro F1 0.700451이나 개발 구간·특정 가스 손실이 남아 Model A를 유지함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_generalization_validation/class_recall_heatmap.png`
- 파일 지문 SHA-256: `6afcdd23a1364c4d645e884c8ed33795ecb96d0e014537325c9b931254ae45b5`

## png/10_confusion_model_A.png

- 자료 제목: confusion_model_A
- 실험 목적: 10단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 확장 Model B의 9–10 동일 가중 Macro F1 0.700451이나 개발 구간·특정 가스 손실이 남아 Model A를 유지함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_generalization_validation/confusion_model_A.png`
- 파일 지문 SHA-256: `0f429fbf511a452497f446dc6e71a97cf18a5dfb3f6755ca4655a5954ae62bcc`

## png/10_confusion_model_B.png

- 자료 제목: confusion_model_B
- 실험 목적: 10단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 확장 Model B의 9–10 동일 가중 Macro F1 0.700451이나 개발 구간·특정 가스 손실이 남아 Model A를 유지함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_generalization_validation/confusion_model_B.png`
- 파일 지문 SHA-256: `eb50bb02d3cfe9ff1ab7b306afba6a67f97fe1b18a6a97bfc349459a1deec0c2`

## png/10_focus_correct_errors.png

- 자료 제목: focus_correct_errors
- 실험 목적: 10단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 확장 Model B의 9–10 동일 가중 Macro F1 0.700451이나 개발 구간·특정 가스 손실이 남아 Model A를 유지함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_generalization_validation/focus_correct_errors.png`
- 파일 지문 SHA-256: `155cdea665f3383d3b956715152087db1c6d8d85bdb7903b86c6fc789744f6bb`

## png/10_performance_changes.png

- 자료 제목: performance_changes
- 실험 목적: 10단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 확장 Model B의 9–10 동일 가중 Macro F1 0.700451이나 개발 구간·특정 가스 손실이 남아 Model A를 유지함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_generalization_validation/performance_changes.png`
- 파일 지문 SHA-256: `eaa448854f26e7dc7949e4df4e0cee0831867c279107218a0f8477135d26fe76`

## png/10_sensor_distribution_4.png

- 자료 제목: sensor_distribution_4
- 실험 목적: 10단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 확장 Model B의 9–10 동일 가중 Macro F1 0.700451이나 개발 구간·특정 가스 손실이 남아 Model A를 유지함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_generalization_validation/sensor_distribution_4.png`
- 파일 지문 SHA-256: `40bdf743a94ed3a3508dcb74aa0d54ee62e6530c86faee7115358b8ca163feb2`

## png/10_sensor_distribution_6.png

- 자료 제목: sensor_distribution_6
- 실험 목적: 10단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 확장 Model B의 9–10 동일 가중 Macro F1 0.700451이나 개발 구간·특정 가스 손실이 남아 Model A를 유지함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_generalization_validation/sensor_distribution_6.png`
- 파일 지문 SHA-256: `4af4886f5e3abebe46ad131f48e332bbed75243431829fc4dbee9c8f474051f5`

## tables/10_batch_class_support.csv

- 자료 제목: batch_class_support
- 실험 목적: 10단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 확장 Model B의 9–10 동일 가중 Macro F1 0.700451이나 개발 구간·특정 가스 손실이 남아 Model A를 유지함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_generalization_validation/batch_class_support.csv`
- 파일 지문 SHA-256: `626220d1da69702d0b11ddd37cf23beac179ddf8f316d8d112eb41f325efa78a`

## tables/10_class_metrics.csv

- 자료 제목: class_metrics
- 실험 목적: 10단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 확장 Model B의 9–10 동일 가중 Macro F1 0.700451이나 개발 구간·특정 가스 손실이 남아 Model A를 유지함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_generalization_validation/class_metrics.csv`
- 파일 지문 SHA-256: `7304e666d5afce35c482cde85cfb96e76c07ba858134e959616d37f1cf1b75f1`

## tables/10_class_performance_changes.csv

- 자료 제목: class_performance_changes
- 실험 목적: 10단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 확장 Model B의 9–10 동일 가중 Macro F1 0.700451이나 개발 구간·특정 가스 손실이 남아 Model A를 유지함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_generalization_validation/class_performance_changes.csv`
- 파일 지문 SHA-256: `5e2645c812ac67e6f80e3b1618ffdfdf609340c08a0e143ca6ae5521eab100e6`

## tables/10_conclusions.csv

- 자료 제목: conclusions
- 실험 목적: 10단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 확장 Model B의 9–10 동일 가중 Macro F1 0.700451이나 개발 구간·특정 가스 손실이 남아 Model A를 유지함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_generalization_validation/conclusions.csv`
- 파일 지문 SHA-256: `9378b56a077c236bd56ae43af55f758228bdff5760c3d4736d6732142e80bb19`

## tables/10_conditional_bootstrap_intervals.csv

- 자료 제목: conditional_bootstrap_intervals
- 실험 목적: 10단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 확장 Model B의 9–10 동일 가중 Macro F1 0.700451이나 개발 구간·특정 가스 손실이 남아 Model A를 유지함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_generalization_validation/conditional_bootstrap_intervals.csv`
- 파일 지문 SHA-256: `b720731d0d7d3f1dc0a3e5958eda89565463835bea74b420ac0a5e3c82439e9c`

## tables/10_conditional_class_intervals.csv

- 자료 제목: conditional_class_intervals
- 실험 목적: 10단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 확장 Model B의 9–10 동일 가중 Macro F1 0.700451이나 개발 구간·특정 가스 손실이 남아 Model A를 유지함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_generalization_validation/conditional_class_intervals.csv`
- 파일 지문 SHA-256: `86fd6874472ceb5108ed4df1180b6c1d6e2c808c3217db251f62dd30212a6775`

## tables/10_confusion_matrices.csv

- 자료 제목: confusion_matrices
- 실험 목적: 10단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 확장 Model B의 9–10 동일 가중 Macro F1 0.700451이나 개발 구간·특정 가스 손실이 남아 Model A를 유지함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_generalization_validation/confusion_matrices.csv`
- 파일 지문 SHA-256: `fce732ae2d0c592ee6f7622299258dab4f61c18354ffdb430c22538fca356fab`

## tables/10_data_inventory.csv

- 자료 제목: data_inventory
- 실험 목적: 10단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 확장 Model B의 9–10 동일 가중 Macro F1 0.700451이나 개발 구간·특정 가스 손실이 남아 Model A를 유지함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_generalization_validation/data_inventory.csv`
- 파일 지문 SHA-256: `62909032fa05450fa61f77f40a1943e023e70dd4613b49212ee5363f81f59895`

## tables/10_evaluation_metrics.csv

- 자료 제목: evaluation_metrics
- 실험 목적: 10단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 확장 Model B의 9–10 동일 가중 Macro F1 0.700451이나 개발 구간·특정 가스 손실이 남아 Model A를 유지함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_generalization_validation/evaluation_metrics.csv`
- 파일 지문 SHA-256: `379cee75babf76bd5f16a2c3f5483a0465d9d5da69b0a710eeb33658a9c72e02`

## tables/10_graph_metadata.csv

- 자료 제목: graph_metadata
- 실험 목적: 10단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 확장 Model B의 9–10 동일 가중 Macro F1 0.700451이나 개발 구간·특정 가스 손실이 남아 Model A를 유지함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_generalization_validation/graph_metadata.csv`
- 파일 지문 SHA-256: `93fa226ec0cb2447522bb72dfbace5dc71c6dfe4a2fca8f80376f2365729f08e`

## tables/10_graph_value_checks.csv

- 자료 제목: graph_value_checks
- 실험 목적: 10단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 확장 Model B의 9–10 동일 가중 Macro F1 0.700451이나 개발 구간·특정 가스 손실이 남아 Model A를 유지함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_generalization_validation/graph_value_checks.csv`
- 파일 지문 SHA-256: `a320eaf0ed4f92466135901ad888a32d44cb625e1d06d2bb302b66c432b2d299`

## tables/10_historical_experiment_timeline.csv

- 자료 제목: historical_experiment_timeline
- 실험 목적: 10단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 확장 Model B의 9–10 동일 가중 Macro F1 0.700451이나 개발 구간·특정 가스 손실이 남아 Model A를 유지함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_generalization_validation/historical_experiment_timeline.csv`
- 파일 지문 SHA-256: `bfa82a353614662fc57bd5cba8168735aaab995a2936b17a402f660318e7877e`

## tables/10_historical_metric_replay.csv

- 자료 제목: historical_metric_replay
- 실험 목적: 10단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 확장 Model B의 9–10 동일 가중 Macro F1 0.700451이나 개발 구간·특정 가스 손실이 남아 Model A를 유지함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_generalization_validation/historical_metric_replay.csv`
- 파일 지문 SHA-256: `16457ce0a47d41f4ce4c38ad6585684381a8dae7669d62584fb224f5fac27935`

## tables/10_model_audit.csv

- 자료 제목: model_audit
- 실험 목적: 10단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 확장 Model B의 9–10 동일 가중 Macro F1 0.700451이나 개발 구간·특정 가스 손실이 남아 Model A를 유지함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_generalization_validation/model_audit.csv`
- 파일 지문 SHA-256: `84b227e5e9928ea4fb14c316d2011b76cf3f06fa233ebfdfb739bc40b601ac53`

## tables/10_model_comparison_summary.csv

- 자료 제목: model_comparison_summary
- 실험 목적: 10단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 확장 Model B의 9–10 동일 가중 Macro F1 0.700451이나 개발 구간·특정 가스 손실이 남아 Model A를 유지함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_generalization_validation/model_comparison_summary.csv`
- 파일 지문 SHA-256: `06e4d50a51ae7e2cd5ce151bbb125289c36fabd273c0bbcb758cec2908ac711f`

## tables/10_paired_correctness.csv

- 자료 제목: paired_correctness
- 실험 목적: 10단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 확장 Model B의 9–10 동일 가중 Macro F1 0.700451이나 개발 구간·특정 가스 손실이 남아 Model A를 유지함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_generalization_validation/paired_correctness.csv`
- 파일 지문 SHA-256: `105d2db82f214277d441880821903907b03e3d8eac943a24a7c948ff0a0fb371`

## tables/10_recall_wilson_intervals.csv

- 자료 제목: recall_wilson_intervals
- 실험 목적: 10단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 확장 Model B의 9–10 동일 가중 Macro F1 0.700451이나 개발 구간·특정 가스 손실이 남아 Model A를 유지함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_generalization_validation/recall_wilson_intervals.csv`
- 파일 지문 SHA-256: `61b327cca5c3d4ffb377f37f8904a1998a9ecb76689541d7cf36d5f9bbbf4f00`

## tables/10_sensor_plot_statistics.csv

- 자료 제목: sensor_plot_statistics
- 실험 목적: 10단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 확장 Model B의 9–10 동일 가중 Macro F1 0.700451이나 개발 구간·특정 가스 손실이 남아 Model A를 유지함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_generalization_validation/sensor_plot_statistics.csv`
- 파일 지문 SHA-256: `66f95779fe53e354c5740f027d9a333144edd83c3307dc45cc0f139791d611b4`

## png/11_batch9_subgroups.png

- 자료 제목: batch9_subgroups
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/batch9_subgroups.png`
- 파일 지문 SHA-256: `eba9eddf8e00d80eed3a065644f5007c63cff24c471d7944e7e9ae5d28f94c8f`

## png/11_decision_score_comparison.png

- 자료 제목: decision_score_comparison
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/decision_score_comparison.png`
- 파일 지문 SHA-256: `f3c64db977da625b38eab04f5d78d10f315523bc4b8220db1077d0661275d436`

## png/11_nearest_train_batch.png

- 자료 제목: nearest_train_batch
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/nearest_train_batch.png`
- 파일 지문 SHA-256: `eae03e16d1492e449525c69b066555753341875331eb75b77b034d44a7abb460`

## png/11_nearest_train_gas.png

- 자료 제목: nearest_train_gas
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/nearest_train_gas.png`
- 파일 지문 SHA-256: `917a24bdfe95c2b63daa8fbcf830875bb3143fb073952ad0c57902a2871678a7`

## png/11_pca_feature_space.png

- 자료 제목: pca_feature_space
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/pca_feature_space.png`
- 파일 지문 SHA-256: `7f6a241d47a73761dfa59693ebe1d26a339897e807673f8bfeffde1ae626bcb3`

## png/11_prediction_change_crosstab.png

- 자료 제목: prediction_change_crosstab
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/prediction_change_crosstab.png`
- 파일 지문 SHA-256: `651f70f0293b304e5bcc1db3e04c9c0d76afd0fdb455fb33fee41d0457b1b397`

## png/11_sensor_correlations.png

- 자료 제목: sensor_correlations
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/sensor_correlations.png`
- 파일 지문 SHA-256: `79523a3c4f1f6451cd8a8a1455e634607282140c5f1ea086b7aef044faf672b7`

## png/11_sensor_joint_profiles.png

- 자료 제목: sensor_joint_profiles
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/sensor_joint_profiles.png`
- 파일 지문 SHA-256: `58d21654cd4e059cb408291cc7bf796f87916fa8328b200c80c8095ee2081520`

## png/11_sensor_shift_heatmap.png

- 자료 제목: sensor_shift_heatmap
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/sensor_shift_heatmap.png`
- 파일 지문 SHA-256: `41bf35c4735e49feaa43b99b78656f9d495c208738ef2af162e41158f0c53588`

## png/11_toluene_prediction_distribution.png

- 자료 제목: toluene_prediction_distribution
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/toluene_prediction_distribution.png`
- 파일 지문 SHA-256: `884f2805746ee74e3a3719605646bcf9cc5f23531e79f2101c8dbe4f6d230b0c`

## tables/11_batch9_cluster_summary.csv

- 자료 제목: batch9_cluster_summary
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/batch9_cluster_summary.csv`
- 파일 지문 SHA-256: `e9cc8007ebd68c7969e4709177f6021a450d795ec7565ccf65b1d84cd983905b`

## tables/11_batch9_linkage.csv

- 자료 제목: batch9_linkage
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/batch9_linkage.csv`
- 파일 지문 SHA-256: `a7365c2a69d5a9e27cbe87ef3a611241320623cf7fdc6974e86568a48f32f77e`

## tables/11_batch9_pairwise_distances.csv

- 자료 제목: batch9_pairwise_distances
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/batch9_pairwise_distances.csv`
- 파일 지문 SHA-256: `2e5e1fe4ed0c5f58ca96f25f44e7bf7f6d661afc4b01fdcfd17002464b5dcc03`

## tables/11_batch9_subgroups.csv

- 자료 제목: batch9_subgroups
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/batch9_subgroups.csv`
- 파일 지문 SHA-256: `b04d1f8d31a1f49fda54b9e664485feb2210cc3b7c4f98be4b0dcc8b420cce28`

## tables/11_batch_class_support.csv

- 자료 제목: batch_class_support
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/batch_class_support.csv`
- 파일 지문 SHA-256: `d4671ce9a65deb88e56df3427cb6d22f82e498cbaf00006dbedc8c01417949b4`

## tables/11_class_weights.csv

- 자료 제목: class_weights
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/class_weights.csv`
- 파일 지문 SHA-256: `452e937ccdc430bb409b26452056566c4d3e022a962d08fe31806dddfb59945e`

## tables/11_decision_scores.csv

- 자료 제목: decision_scores
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/decision_scores.csv`
- 파일 지문 SHA-256: `8087db56641a1db48a51507165b613b4250e538a08c92cc59a9aa5cfad554148`

## tables/11_decision_summary.csv

- 자료 제목: decision_summary
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/decision_summary.csv`
- 파일 지문 SHA-256: `5cff5a7ac3b9aadcf81e606c5e51c5a96b9c5822f359f8a829d3042ce571894d`

## tables/11_feature_distribution_shift.csv

- 자료 제목: feature_distribution_shift
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/feature_distribution_shift.csv`
- 파일 지문 SHA-256: `14e788483f8ff734b956482d1e5693232ace9cfb720b593fca322ffaa5b319f3`

## tables/11_feature_statistics.csv

- 자료 제목: feature_statistics
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/feature_statistics.csv`
- 파일 지문 SHA-256: `41357a009663e96cc59eea86f00420eda20dd909f53f7022b5f04c190df61a4f`

## tables/11_graph_metadata.csv

- 자료 제목: graph_metadata
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/graph_metadata.csv`
- 파일 지문 SHA-256: `59734160fa0ecbef5ca8629ec19be0e43a3118353f3e1336be45f76a58babc82`

## tables/11_graph_value_checks.csv

- 자료 제목: graph_value_checks
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/graph_value_checks.csv`
- 파일 지문 SHA-256: `7f66da49f467abba04e4f6605730a2e85b53e7d768ff2d109f971438c41143a6`

## tables/11_hypothesis_evidence.csv

- 자료 제목: hypothesis_evidence
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/hypothesis_evidence.csv`
- 파일 지문 SHA-256: `a1e016eb45fe9a9fa3114e63a78544d4df0044aa17bc805d6b20415203c3c57f`

## tables/11_model_audit.csv

- 자료 제목: model_audit
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/model_audit.csv`
- 파일 지문 SHA-256: `78b6a9a9f8d624de99545fc5fe7e5faeb903a20a070735cb4f4c1217f22c088d`

## tables/11_nearest_batch_counts.csv

- 자료 제목: nearest_batch_counts
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/nearest_batch_counts.csv`
- 파일 지문 SHA-256: `ffdd50dc2db0097a706e28b98f4a61f0b4769a522cd68f03f9c495b3fcd3c677`

## tables/11_nearest_gas_counts.csv

- 자료 제목: nearest_gas_counts
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/nearest_gas_counts.csv`
- 파일 지문 SHA-256: `a1e33ee7c50d392af0d04c2e807cdec59eabdeb12e5a37421a06ec41e2afb6b2`

## tables/11_nearest_neighbors.csv

- 자료 제목: nearest_neighbors
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/nearest_neighbors.csv`
- 파일 지문 SHA-256: `7de55589ddb4418c6d9dd96fa0c99b511fff2a99b793852f2767679c5e31b9a8`

## tables/11_neighbor_summary.csv

- 자료 제목: neighbor_summary
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/neighbor_summary.csv`
- 파일 지문 SHA-256: `26d629326cc9820fb37f33ea0c02a197465595655dc09385fd058d8875b91a52`

## tables/11_pair_geometry.csv

- 자료 제목: pair_geometry
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/pair_geometry.csv`
- 파일 지문 SHA-256: `ca0c58e0675cbc80e170fe30be4b64889471418d1d3c6db597826142c2916e20`

## tables/11_pca_components.csv

- 자료 제목: pca_components
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/pca_components.csv`
- 파일 지문 SHA-256: `251cfa3ff48b8559585c6534e7e6dbec2d23c9a6d349742a80f07a5bfcb3ee3a`

## tables/11_sensor_correlation_changes.csv

- 자료 제목: sensor_correlation_changes
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/sensor_correlation_changes.csv`
- 파일 지문 SHA-256: `a55371d44aa93752bb59f3ef7cf6627f31b8c4a7e322efebbcedb80ad6e500d5`

## tables/11_sensor_correlations.csv

- 자료 제목: sensor_correlations
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/sensor_correlations.csv`
- 파일 지문 SHA-256: `06fd82b3c8f6ff0fffab3d42176d1e7613c5e1434de2c6200342ed82ff13a9df`

## tables/11_sensor_distribution_shift.csv

- 자료 제목: sensor_distribution_shift
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/sensor_distribution_shift.csv`
- 파일 지문 SHA-256: `73cf5cea471e112166fce95c4dab632cb0e5d46a1eaca45385060d7a38d3c22e`

## tables/11_sensor_feature_mapping.csv

- 자료 제목: sensor_feature_mapping
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/sensor_feature_mapping.csv`
- 파일 지문 SHA-256: `8e59c9f63325b60ee9f32ace47bc093dc1ff025393288cd1bc55025d32fbf2c6`

## tables/11_sensor_gas_contrasts.csv

- 자료 제목: sensor_gas_contrasts
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/sensor_gas_contrasts.csv`
- 파일 지문 SHA-256: `316b6df7bae0b8bb286fc9c3e61e0e1b54567ec8a7c9469b5f7fd6bbb4968e8f`

## tables/11_sensor_plot_selection.csv

- 자료 제목: sensor_plot_selection
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/sensor_plot_selection.csv`
- 파일 지문 SHA-256: `6358afca351ec3bfffc9340bc6ec6643e295d683575fa20d4064f1175004be29`

## tables/11_stage7_distance_replay.csv

- 자료 제목: stage7_distance_replay
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/stage7_distance_replay.csv`
- 파일 지문 SHA-256: `cf0cc598593eca183039602428a6d7172924009c3ad92d1662579f77f1543704`

## tables/11_top5_gas_counts.csv

- 자료 제목: top5_gas_counts
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/top5_gas_counts.csv`
- 파일 지문 SHA-256: `2eac051b5bf8eee69511c61b2d33762fc2b8c9a1a9aab3e9ffe670c914e34737`

## tables/11_top5_neighbors.csv

- 자료 제목: top5_neighbors
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/top5_neighbors.csv`
- 파일 지문 SHA-256: `9d0eaa3dc44300626c83b9e1ddeba58e3d376132031479d6d1bbcd00d8258170`

## tables/11_train_class_recall.csv

- 자료 제목: train_class_recall
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/train_class_recall.csv`
- 파일 지문 SHA-256: `f06e45811fa6e4831e09b4a707f8fb4c23b69c594cb375490c9077c46bfed86f`

## tables/11_train_scores_A.csv

- 자료 제목: train_scores_A
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/train_scores_A.csv`
- 파일 지문 SHA-256: `a3a2284cfca9eed0aff612065a790d0a1d0dbd3ba5fdbd03700d7f20d080aeb7`

## tables/11_train_scores_B.csv

- 자료 제목: train_scores_B
- 실험 목적: 11단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Model A Train1–6/Validation7–8; 확장 Model B Train1–7. 9–10은 반복 관찰한 회고적 자료. 모델별 학습 범위·표의 분모 확인 필수.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/toluene_failure_deep_diagnostic/train_scores_B.csv`
- 파일 지문 SHA-256: `cd228d00497d95fb0fe02a3ed014661e6ecb0dbab954823bed70f7bf26fc68ab`

## png/12_batch_macro_f1.png

- 자료 제목: batch_macro_f1
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/batch_macro_f1.png`
- 파일 지문 SHA-256: `02bd2941f0c7701476c202b0ac6c5ee0077aea1ffc05470714a0842777393fc2`

## png/12_class_recall_heatmap.png

- 자료 제목: class_recall_heatmap
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/class_recall_heatmap.png`
- 파일 지문 SHA-256: `bef35eb1de9e544374187b60f33f8f76c294927dee310c32a0575e74aa025a6c`

## png/12_composition_macro_f1.png

- 자료 제목: composition_macro_f1
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/composition_macro_f1.png`
- 파일 지문 SHA-256: `b3d4e0607d403018cb93a3dfccd11da5846a4b28d13a07dc4704cc0b5ee03216`

## png/12_exploratory_macro_f1.png

- 자료 제목: exploratory_macro_f1
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/exploratory_macro_f1.png`
- 파일 지문 SHA-256: `ec270961c66f750683e22a9a11adb082f7ca8ed94100ebb964f1876242e7a416`

## png/12_focus_recall.png

- 자료 제목: focus_recall
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/focus_recall.png`
- 파일 지문 SHA-256: `68f587467542d72e7e100a48e49552d71b0d117deb09075c3a1aba85c0280b1a`

## png/12_preprocessing_weight_controls.png

- 자료 제목: preprocessing_weight_controls
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/preprocessing_weight_controls.png`
- 파일 지문 SHA-256: `57b40cf9e368133873bda18a81f9f922ea70db521a050bc4e6fb623644adc662`

## png/12_sample_size_effect.png

- 자료 제목: sample_size_effect
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/sample_size_effect.png`
- 파일 지문 SHA-256: `b950183090630af257061a75e3ebb8a901861d098a90702be413f7b5863fe052`

## png/12_seed_distributions.png

- 자료 제목: seed_distributions
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/seed_distributions.png`
- 파일 지문 SHA-256: `a2f93d71342ecfd397e70d168b9d44ae898e46349cf0cf8bf885f7e4ab022910`

## png/12_training_composition.png

- 자료 제목: training_composition
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/training_composition.png`
- 파일 지문 SHA-256: `370cc6b4aedfd9ed908c2c5d9be9315ced3515444d769f775f575bdac291349e`

## png/12_class_recall_heatmap_c6d3d74a.png

- 자료 제목: class_recall_heatmap
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/visual_review_before/class_recall_heatmap.png`
- 파일 지문 SHA-256: `c6d3d74a2ed732597fcab82f5b06256c1685d9d8c94087a02afda7b72a58f101`

## tables/12_batch_class_support.csv

- 자료 제목: batch_class_support
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/batch_class_support.csv`
- 파일 지문 SHA-256: `d4671ce9a65deb88e56df3427cb6d22f82e498cbaf00006dbedc8c01417949b4`

## tables/12_class_summary.csv

- 자료 제목: class_summary
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/class_summary.csv`
- 파일 지문 SHA-256: `22b0cf44f992b62698180dcbd67a3ca0dd5239cc1b17b7eb60572b5421929fab`

## tables/12_class_weights.csv

- 자료 제목: class_weights
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/class_weights.csv`
- 파일 지문 SHA-256: `041b9cbbf80e6027122da3df618d41ff3a12d2d0feb0508f5ecf46b8ad976c77`

## tables/12_effect_summary.csv

- 자료 제목: effect_summary
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/effect_summary.csv`
- 파일 지문 SHA-256: `7808b125a108ab82a3e3e31d338344517552f2b8f0fc2b337c87711023290cdb`

## tables/12_exploratory_class_metrics.csv

- 자료 제목: exploratory_class_metrics
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/exploratory_class_metrics.csv`
- 파일 지문 SHA-256: `d827f807e37fb66eac55ca272e58473bf197aa111348e15101ce04ee1f408209`

## tables/12_exploratory_class_summary.csv

- 자료 제목: exploratory_class_summary
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/exploratory_class_summary.csv`
- 파일 지문 SHA-256: `75e626dd7de9c43260375d21169e8941fe5719630da834d82abae296143079ed`

## tables/12_exploratory_confusion.csv

- 자료 제목: exploratory_confusion
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/exploratory_confusion.csv`
- 파일 지문 SHA-256: `0a09a5ba1941f647b9e387bf8fe5605e422009ab949e930ba16a90b365ab76c9`

## tables/12_exploratory_metrics.csv

- 자료 제목: exploratory_metrics
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/exploratory_metrics.csv`
- 파일 지문 SHA-256: `86a1bae0746cb4e3e8950a4767dfef309b878e155ebe1f79dd297ccd51b4566f`

## tables/12_exploratory_seed_summary.csv

- 자료 제목: exploratory_seed_summary
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/exploratory_seed_summary.csv`
- 파일 지문 SHA-256: `929a113fe6bca6db6f319c25649064f07c6021f40fb4c1bc9ef8ea5a61d111fd`

## tables/12_exploratory_summary.csv

- 자료 제목: exploratory_summary
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/exploratory_summary.csv`
- 파일 지문 SHA-256: `81c31caf271cfb2ff0b9bf223fe7375eb57a11789d5302a4a4dc5889d84d2242`

## tables/12_fit_records.csv

- 자료 제목: fit_records
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/fit_records.csv`
- 파일 지문 SHA-256: `75b3d2f589efdb37c7d11cfbc2650c773b4626ae6b7068d90737adbdfd57c6f8`

## tables/12_fold_summary.csv

- 자료 제목: fold_summary
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/fold_summary.csv`
- 파일 지문 SHA-256: `bc72b4669d20415863e88ea0c4f809ca147074d179792416988ee95d8c551029`

## tables/12_graph_metadata.csv

- 자료 제목: graph_metadata
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/graph_metadata.csv`
- 파일 지문 SHA-256: `5b9d19db8afa3fe23c48db21a64879daf95e6afa098419331dbfa05fbee9ec2a`

## tables/12_graph_value_checks.csv

- 자료 제목: graph_value_checks
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/graph_value_checks.csv`
- 파일 지문 SHA-256: `a181028f4ad1e9defd88a6e61455b72ccc78859d131c20f667fe9c9f8a383051`

## tables/12_historical_class_metrics.csv

- 자료 제목: historical_class_metrics
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/historical_class_metrics.csv`
- 파일 지문 SHA-256: `555223854ed3f418cf936360cbe8333566cac39562e389d77d50eacd92a52e6f`

## tables/12_historical_confusion.csv

- 자료 제목: historical_confusion
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/historical_confusion.csv`
- 파일 지문 SHA-256: `61260308caa075dbf2b5351a42f7b21c26d07c8d84b516a1f2a1277c20b310b2`

## tables/12_historical_metrics.csv

- 자료 제목: historical_metrics
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/historical_metrics.csv`
- 파일 지문 SHA-256: `64fef65978da835bbd613b8d9be2b3e3361d1585371eae44db6b15c5a5af83cb`

## tables/12_historical_pooled_class_metrics.csv

- 자료 제목: historical_pooled_class_metrics
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/historical_pooled_class_metrics.csv`
- 파일 지문 SHA-256: `e0c372fea8209f7d73918878aa6a88dbfb83c0c1d9aed592928729e0fea98a72`

## tables/12_historical_pooled_metrics.csv

- 자료 제목: historical_pooled_metrics
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/historical_pooled_metrics.csv`
- 파일 지문 SHA-256: `ccf825a9263655c7740e7f5ab5dae14513e1ddf398afe7ec8ecb61e40c4cf386`

## tables/12_historical_summary.csv

- 자료 제목: historical_summary
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/historical_summary.csv`
- 파일 지문 SHA-256: `11445674392ee8ad064816d832b760adc67395cb4ffe0954927e00da038815a5`

## tables/12_interpretation_findings.csv

- 자료 제목: interpretation_findings
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/interpretation_findings.csv`
- 파일 지문 SHA-256: `742a12ec8b1fa9ab466a7a803c73789399d7107b181c77dcf7015dfc7b572c8d`

## tables/12_paired_class_effects.csv

- 자료 제목: paired_class_effects
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/paired_class_effects.csv`
- 파일 지문 SHA-256: `e1902036503efd09bc43482e6cfa640a20b33992b5962a08c31eedc114fd6c08`

## tables/12_paired_effects.csv

- 자료 제목: paired_effects
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/paired_effects.csv`
- 파일 지문 SHA-256: `57c846470d3684fa91084ab60456e47f801975f6edb36a6c4e892a4333b5d682`

## tables/12_preprocessing_statistics.csv

- 자료 제목: preprocessing_statistics
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/preprocessing_statistics.csv`
- 파일 지문 SHA-256: `68ab2adbbbce270b4179ed20bd37f6c01b91d53f10f3afa2a1a7e39666887c20`

## tables/12_reference_class_weights.csv

- 자료 제목: reference_class_weights
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/reference_class_weights.csv`
- 파일 지문 SHA-256: `fd8caf1928bda41c813774608febb7057dd49e3abbc11664a0b70ac40352a95e`

## tables/12_reference_model_audit.csv

- 자료 제목: reference_model_audit
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/reference_model_audit.csv`
- 파일 지문 SHA-256: `4d42fe296b266211b7d0da1cb0dd716accf3fee9add5ffba0a805868170af4c4`

## tables/12_reference_model_metrics.csv

- 자료 제목: reference_model_metrics
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/reference_model_metrics.csv`
- 파일 지문 SHA-256: `ff926226601f169c7e555f70d44600581d601fe4eaca51f695f360728e1bebd6`

## tables/12_reference_preprocessing.csv

- 자료 제목: reference_preprocessing
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/reference_preprocessing.csv`
- 파일 지문 SHA-256: `fefaed9b43e3cace2ac051e76b0a667c79d4a0c92710eb5557ac6b81d9ca8276`

## tables/12_sample_composition.csv

- 자료 제목: sample_composition
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/sample_composition.csv`
- 파일 지문 SHA-256: `76ee2fc7d7ebdcd68bea424599e4802d75f43c802d8e8636bff4c42a1d4f9f07`

## tables/12_seed_summary.csv

- 자료 제목: seed_summary
- 실험 목적: 12단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_representativeness_control/seed_summary.csv`
- 파일 지문 SHA-256: `802a3798c7fbd5c36f553f7df99814d68f9fa07a02f63046c24072544927ca1f`

## png/13_expansion_comparison.png

- 자료 제목: expansion_comparison
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/expansion_comparison.png`
- 파일 지문 SHA-256: `27d29d59de17bb485f8bac355a3568531913404cc466fea94ff23cf20e628ede`

## png/13_exploratory_confusion_10.png

- 자료 제목: exploratory_confusion_10
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/exploratory_confusion_10.png`
- 파일 지문 SHA-256: `a207e5188b7becfa4e65fce0ac2d6c638329e72221a3ebe3801de8ec55ee3481`

## png/13_exploratory_confusion_9.png

- 자료 제목: exploratory_confusion_9
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/exploratory_confusion_9.png`
- 파일 지문 SHA-256: `ff1552a5ea6913d140d1f9c0847c32c285e0790adcff37da2ce60f678da3babb`

## png/13_focus_joint_recall.png

- 자료 제목: focus_joint_recall
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/focus_joint_recall.png`
- 파일 지문 SHA-256: `a181b6d65aa7b57e0062b32b5ccab0401d3b35c7bad29f7a0705b82973be10dd`

## png/13_fold_macro_f1.png

- 자료 제목: fold_macro_f1
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/fold_macro_f1.png`
- 파일 지문 SHA-256: `8ba47a3dbdc22f62ee2e1a10059751fc21abfee89adffab8bf2c4bf8b3fbb485`

## png/13_gas_batch_composition.png

- 자료 제목: gas_batch_composition
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/gas_batch_composition.png`
- 파일 지문 SHA-256: `074253a20834be246f4281c9b41dcfcfcc0c103db8997bd601cee481e5317a47`

## png/13_gas_recall_heatmap.png

- 자료 제목: gas_recall_heatmap
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/gas_recall_heatmap.png`
- 파일 지문 SHA-256: `92b39e3cc853584b579124900a6ffa2242ef79b9d3c55885850ecbc7f9e0ff4a`

## png/13_recall_changes.png

- 자료 제목: recall_changes
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/recall_changes.png`
- 파일 지문 SHA-256: `27492677a85909b0edaf096210de8565e4e2d70c143258385575e104e85e1672`

## png/13_seed_distribution.png

- 자료 제목: seed_distribution
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/seed_distribution.png`
- 파일 지문 SHA-256: `038077d086655063463266fe6cf3b7adb3aefdec84311baf0525120592fa1b6b`

## png/13_strategy_macro_f1.png

- 자료 제목: strategy_macro_f1
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/strategy_macro_f1.png`
- 파일 지문 SHA-256: `5f9f7ec0a8a0091738eb7ad843d0fcccf29d3c10d271762093616b66345527ad`

## png/13_exploratory_confusion_10_472cc12b.png

- 자료 제목: exploratory_confusion_10
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/visual_review_before/exploratory_confusion_10.png`
- 파일 지문 SHA-256: `472cc12bf4d588a87d52a66ef69f3d08c85f25156cb5aba048b2c41c6b19390d`

## png/13_exploratory_confusion_9_9182d796.png

- 자료 제목: exploratory_confusion_9
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/visual_review_before/exploratory_confusion_9.png`
- 파일 지문 SHA-256: `9182d7966dc9091c388e34a7fbbf7d187e25f2132553b3d32cfdc1cd9e1ae8f7`

## png/13_focus_joint_recall_aed55803.png

- 자료 제목: focus_joint_recall
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/visual_review_before/focus_joint_recall.png`
- 파일 지문 SHA-256: `aed55803c1ff419faa6644f464eb4eff64de818ab01aeff181c390eb894b3c53`

## png/13_gas_batch_composition_004b0851.png

- 자료 제목: gas_batch_composition
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/visual_review_before/gas_batch_composition.png`
- 파일 지문 SHA-256: `004b0851775a54fe22913203e075597a8313f98fa1658f576e29699e22850859`

## tables/13_all_class_deltas.csv

- 자료 제목: all_class_deltas
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/all_class_deltas.csv`
- 파일 지문 SHA-256: `f4516fe6a4eac46e0b6d5544b943e2ff4fb548b999f3eae94da811f5c7945792`

## tables/13_all_guards.csv

- 자료 제목: all_guards
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/all_guards.csv`
- 파일 지문 SHA-256: `30882fe637115378f4206ca216923ff76628138b65941d4d4140188c502f38b1`

## tables/13_all_paired_deltas.csv

- 자료 제목: all_paired_deltas
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/all_paired_deltas.csv`
- 파일 지문 SHA-256: `a22db5762a82e7e3a94ad55825dcbc10e5f6e44c1d65bda4a52f3873cf19778a`

## tables/13_all_seed_summary.csv

- 자료 제목: all_seed_summary
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/all_seed_summary.csv`
- 파일 지문 SHA-256: `c48152777044e80d3ff9a8848fb0bd93f474989f7922ce89f5214671d05eda79`

## tables/13_all_summary.csv

- 자료 제목: all_summary
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/all_summary.csv`
- 파일 지문 SHA-256: `a539a80d1e77e3c3a9ef6c86ace116b19215e6cc40ee53b784238ab6fdc896cb`

## tables/13_class_summary.csv

- 자료 제목: class_summary
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/class_summary.csv`
- 파일 지문 SHA-256: `48792729775006a2417c3fbd419decfecb031c0122f7766a9e0f5a1fefb09a48`

## tables/13_executed_sample_composition.csv

- 자료 제목: executed_sample_composition
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/executed_sample_composition.csv`
- 파일 지문 SHA-256: `8362b72f33eeb274f4d13ec985632c60409710f33a8a5d8d376028b37a568edf`

## tables/13_exploratory_class_metrics.csv

- 자료 제목: exploratory_class_metrics
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/exploratory_class_metrics.csv`
- 파일 지문 SHA-256: `847b3d1811bee3fb3363a96878a7d09d6cb52d6fc5001d7088859ff37ba1d7c5`

## tables/13_exploratory_class_summary.csv

- 자료 제목: exploratory_class_summary
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/exploratory_class_summary.csv`
- 파일 지문 SHA-256: `163c125999d8539c9bb4ba610b4ff808c9e81fc47bc77c40b1bb3a4815171756`

## tables/13_exploratory_confusion.csv

- 자료 제목: exploratory_confusion
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/exploratory_confusion.csv`
- 파일 지문 SHA-256: `e2e8b5e1ded53fb730cdbf744eff9fd8d350648b8efd6662d78b25f7ce38fed9`

## tables/13_exploratory_equal_batch_seed_scores.csv

- 자료 제목: exploratory_equal_batch_seed_scores
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/exploratory_equal_batch_seed_scores.csv`
- 파일 지문 SHA-256: `15ba40989d3f6be80a8b9bc10446e2edcd6a306e2eaa6a888f4f3842c6627e2d`

## tables/13_exploratory_equal_batch_summary.csv

- 자료 제목: exploratory_equal_batch_summary
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/exploratory_equal_batch_summary.csv`
- 파일 지문 SHA-256: `02ede0c9d82d7f5a1ca71564293661874a4e78cbaa6c9764187d3df895f01ae1`

## tables/13_exploratory_metrics.csv

- 자료 제목: exploratory_metrics
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/exploratory_metrics.csv`
- 파일 지문 SHA-256: `be12292579817574dfc442fccf3cef9b4da2b7c053d84c376887d74d16b8aa54`

## tables/13_exploratory_summary.csv

- 자료 제목: exploratory_summary
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/exploratory_summary.csv`
- 파일 지문 SHA-256: `10eb5e44954c431a1ef8648798e8037a8803d548abc0575ef5737e2a5e0c0e2f`

## tables/13_fold_summary.csv

- 자료 제목: fold_summary
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/fold_summary.csv`
- 파일 지문 SHA-256: `b623291b9dc3575df869640c5b479632e43cbda2220163705bab3f13d2fa3ab1`

## tables/13_graph_metadata.csv

- 자료 제목: graph_metadata
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/graph_metadata.csv`
- 파일 지문 SHA-256: `9ac044816bfc6d4a044f893c79156f384d5b023fab6cef85e016bd57cc61d5a1`

## tables/13_graph_value_checks.csv

- 자료 제목: graph_value_checks
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/graph_value_checks.csv`
- 파일 지문 SHA-256: `4c5a0050aef6bef76314b01308b2e20d37d9ab15c29db158a2d74b4d91efbd85`

## tables/13_historical_class_metrics.csv

- 자료 제목: historical_class_metrics
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/historical_class_metrics.csv`
- 파일 지문 SHA-256: `089f7bc6a29edaae00815508931959d4b637c77ee17a0e0bc6f74e17990feeb6`

## tables/13_historical_confusion.csv

- 자료 제목: historical_confusion
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/historical_confusion.csv`
- 파일 지문 SHA-256: `5d723a861f39947f7fbb1683db32f84c07ae93454d9c7b67890f19322552d02e`

## tables/13_historical_metrics.csv

- 자료 제목: historical_metrics
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/historical_metrics.csv`
- 파일 지문 SHA-256: `8b6b8bb1e6527790cf0863eea06945e588087a4a791b0053f4dc487b39c35529`

## tables/13_identical_subset_checks.csv

- 자료 제목: identical_subset_checks
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/identical_subset_checks.csv`
- 파일 지문 SHA-256: `0bf25e91252287f14377264827e6ae65d4b0b7dc5d70ae3349b894832f763f42`

## tables/13_major_error_directions.csv

- 자료 제목: major_error_directions
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/major_error_directions.csv`
- 파일 지문 SHA-256: `3ce301833a8381b6f1744ae6afb42dbf92648c7e0217547436e39cda873a8dda`

## tables/13_max_matched_class_deltas.csv

- 자료 제목: max_matched_class_deltas
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/max_matched_class_deltas.csv`
- 파일 지문 SHA-256: `c05845222f11f372bb1025506b6e5016505cba5ae1e33330aa5ac5c98543fb9a`

## tables/13_max_matched_guards.csv

- 자료 제목: max_matched_guards
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/max_matched_guards.csv`
- 파일 지문 SHA-256: `3fd63da3ef51fa63fef3ee4cb7daf4552c2cce766d757d97024d52d58ca69e93`

## tables/13_max_matched_paired_deltas.csv

- 자료 제목: max_matched_paired_deltas
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/max_matched_paired_deltas.csv`
- 파일 지문 SHA-256: `4b8f15146f334eff8286256e18c7c2b2f6aca26496f54edb7a0c6a572f519249`

## tables/13_max_matched_seed_summary.csv

- 자료 제목: max_matched_seed_summary
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/max_matched_seed_summary.csv`
- 파일 지문 SHA-256: `415224a137eee6105ceca431e4e476368d4d4972472438f47a2e9a4a4c6ca53c`

## tables/13_max_matched_summary.csv

- 자료 제목: max_matched_summary
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/max_matched_summary.csv`
- 파일 지문 SHA-256: `244dc9f86b18c96a9a0d1a39a6bb512adc29eb65bc555ddbd1e5c89435ff0352`

## tables/13_mid_class_deltas.csv

- 자료 제목: mid_class_deltas
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/mid_class_deltas.csv`
- 파일 지문 SHA-256: `48e4b6965aa309d0d3fce91a017bfa01fbb0822633828d508fe96bf44cc5a838`

## tables/13_mid_guards.csv

- 자료 제목: mid_guards
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/mid_guards.csv`
- 파일 지문 SHA-256: `ccfbd17bffb05b63a1a0e6f3e9505f81cd59fe8317b31029c691a4d8c475adb5`

## tables/13_mid_paired_deltas.csv

- 자료 제목: mid_paired_deltas
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/mid_paired_deltas.csv`
- 파일 지문 SHA-256: `1b90e410065e9705d1bd099d4e7910931581a927897eb8c952243545b7dde7e3`

## tables/13_mid_seed_summary.csv

- 자료 제목: mid_seed_summary
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/mid_seed_summary.csv`
- 파일 지문 SHA-256: `065798d597a5380878e3c51320aca18596e72dbbc3a2e2575940629a6c031b81`

## tables/13_mid_summary.csv

- 자료 제목: mid_summary
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/mid_summary.csv`
- 파일 지문 SHA-256: `af601a25e5264a21f5ee4d5a9c858b413e8eb7a5809b5f82d207381a060be6b0`

## tables/13_model_registry.csv

- 자료 제목: model_registry
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/model_registry.csv`
- 파일 지문 SHA-256: `15f0de9e3c6c9c3462d4616df93fd1fdb32511b750c25db285fb4d95b70d6fac`

## tables/13_planned_sample_composition.csv

- 자료 제목: planned_sample_composition
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/planned_sample_composition.csv`
- 파일 지문 SHA-256: `c6acc3ccd9e210553cb12aec383a04287c61ca7659c15803728235133b000758`

## tables/13_replay_checks.csv

- 자료 제목: replay_checks
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/replay_checks.csv`
- 파일 지문 SHA-256: `bf9adc890ca143cdd598f50a48c811afb5f78d5ea6f047c955503b1b5afa1ed1`

## tables/13_size_class_deltas.csv

- 자료 제목: size_class_deltas
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/size_class_deltas.csv`
- 파일 지문 SHA-256: `814836eb7dde502692b385e66f288cfd28573a7942a60f59f918c9e3956993e1`

## tables/13_size_comparisons.csv

- 자료 제목: size_comparisons
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/size_comparisons.csv`
- 파일 지문 SHA-256: `fd0c232e2f280758266facd992b244aed433d10ad441a97fbe111a2a6e804e56`

## tables/13_train_only_strategy_rules.csv

- 자료 제목: train_only_strategy_rules
- 실험 목적: 13단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 시기·가스별 구성 변경으로 Toluene–Acetaldehyde 간 상충이 나타났으며 균형 보호 조건을 만족하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/gas_specific_temporal_balancing/train_only_strategy_rules.csv`
- 파일 지문 SHA-256: `e8088575e38df13476201e3538e96e7e3a06b086cf9fc6ad0a7b043a33982b80`

## png/14_confusion_matrices.png

- 자료 제목: confusion_matrices
- 실험 목적: 14단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: signed-log 과거 Fold 평균0.800290 대 기준0.797082. 사전 개선 기준 미달이며 일관된 균형 개선을 확인하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/nonlinear_feature_transformation/confusion_matrices.png`
- 파일 지문 SHA-256: `7c9e69c1b8e6429bac84c0609a416570cdfac463c373b51d1a6223ae390df812`

## png/14_directional_errors.png

- 자료 제목: directional_errors
- 실험 목적: 14단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: signed-log 과거 Fold 평균0.800290 대 기준0.797082. 사전 개선 기준 미달이며 일관된 균형 개선을 확인하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/nonlinear_feature_transformation/directional_errors.png`
- 파일 지문 SHA-256: `2c2aefb9ae35c372b1a2215088c991d34e2fe3d10b649e865c758f3f64e7730f`

## png/14_focus_precision_recall_f1.png

- 자료 제목: focus_precision_recall_f1
- 실험 목적: 14단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: signed-log 과거 Fold 평균0.800290 대 기준0.797082. 사전 개선 기준 미달이며 일관된 균형 개선을 확인하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/nonlinear_feature_transformation/focus_precision_recall_f1.png`
- 파일 지문 SHA-256: `264de3d5af924c3346f9542dbc64013c34e0c5556c2259b55ab19d9199e769c0`

## png/14_fold_macro_f1.png

- 자료 제목: fold_macro_f1
- 실험 목적: 14단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: signed-log 과거 Fold 평균0.800290 대 기준0.797082. 사전 개선 기준 미달이며 일관된 균형 개선을 확인하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/nonlinear_feature_transformation/fold_macro_f1.png`
- 파일 지문 SHA-256: `dd8add1c707d76c0dc42a99457e53dbe1e8e1aa1b5e7f7791a7ba1aec64c02cc`

## png/14_mean_macro_f1.png

- 자료 제목: mean_macro_f1
- 실험 목적: 14단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: signed-log 과거 Fold 평균0.800290 대 기준0.797082. 사전 개선 기준 미달이며 일관된 균형 개선을 확인하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/nonlinear_feature_transformation/mean_macro_f1.png`
- 파일 지문 SHA-256: `780562193f09e97d0a8d411f088cc486cf45728e1a315df792cee09d1ade34ec`

## png/14_recall_delta.png

- 자료 제목: recall_delta
- 실험 목적: 14단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: signed-log 과거 Fold 평균0.800290 대 기준0.797082. 사전 개선 기준 미달이며 일관된 균형 개선을 확인하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/nonlinear_feature_transformation/recall_delta.png`
- 파일 지문 SHA-256: `0799319a0591b3ce7e64f04655f538c6a13ffb939e0bfab5d5e343991adb6ed3`

## png/14_recall_heatmap.png

- 자료 제목: recall_heatmap
- 실험 목적: 14단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: signed-log 과거 Fold 평균0.800290 대 기준0.797082. 사전 개선 기준 미달이며 일관된 균형 개선을 확인하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/nonlinear_feature_transformation/recall_heatmap.png`
- 파일 지문 SHA-256: `0a954c89d239ef9ef4c34acbed0cdeb66e22b343f4ee3dba6f075135df238acc`

## png/14_train_distributions.png

- 자료 제목: train_distributions
- 실험 목적: 14단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: signed-log 과거 Fold 평균0.800290 대 기준0.797082. 사전 개선 기준 미달이며 일관된 균형 개선을 확인하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/nonlinear_feature_transformation/train_distributions.png`
- 파일 지문 SHA-256: `6b5360db608f406e984a6089c615cf3feb9a5b670be7b7df4ed87b613e62102d`

## tables/14_class_metrics.csv

- 자료 제목: class_metrics
- 실험 목적: 14단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: signed-log 과거 Fold 평균0.800290 대 기준0.797082. 사전 개선 기준 미달이며 일관된 균형 개선을 확인하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/nonlinear_feature_transformation/class_metrics.csv`
- 파일 지문 SHA-256: `fa59d7bee4d6cd77b7c39aef3b1c78c5ad4642016a8d4218e410aaba8fde5167`

## tables/14_confusion.csv

- 자료 제목: confusion
- 실험 목적: 14단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: signed-log 과거 Fold 평균0.800290 대 기준0.797082. 사전 개선 기준 미달이며 일관된 균형 개선을 확인하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/nonlinear_feature_transformation/confusion.csv`
- 파일 지문 SHA-256: `4ca798a3588fabbae7f1a91e60c8b306456c22e690788d3282034b8153e927c6`

## tables/14_distribution_examples.csv

- 자료 제목: distribution_examples
- 실험 목적: 14단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: signed-log 과거 Fold 평균0.800290 대 기준0.797082. 사전 개선 기준 미달이며 일관된 균형 개선을 확인하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/nonlinear_feature_transformation/distribution_examples.csv`
- 파일 지문 SHA-256: `14efe42314657406b6c7525bf684c88ea64bc35a35e9391e144769456f4946d8`

## tables/14_fold_metrics.csv

- 자료 제목: fold_metrics
- 실험 목적: 14단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: signed-log 과거 Fold 평균0.800290 대 기준0.797082. 사전 개선 기준 미달이며 일관된 균형 개선을 확인하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/nonlinear_feature_transformation/fold_metrics.csv`
- 파일 지문 SHA-256: `e0f6438fa1ee773c59df228b4eb92fd53238f15361e6688f0939517d02262ba3`

## tables/14_fold_support.csv

- 자료 제목: fold_support
- 실험 목적: 14단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: signed-log 과거 Fold 평균0.800290 대 기준0.797082. 사전 개선 기준 미달이며 일관된 균형 개선을 확인하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/nonlinear_feature_transformation/fold_support.csv`
- 파일 지문 SHA-256: `64b9120101a80b3650166a54d7d17332793db1db4a70efa263b7ad54b4b9bf0c`

## tables/14_graph_manifest.csv

- 자료 제목: graph_manifest
- 실험 목적: 14단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: signed-log 과거 Fold 평균0.800290 대 기준0.797082. 사전 개선 기준 미달이며 일관된 균형 개선을 확인하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/nonlinear_feature_transformation/graph_manifest.csv`
- 파일 지문 SHA-256: `5b158f7dd3ed5f7a8e20ab6e3f6bdcc2822ea4b4d8151474d8aa89f0cab7c90e`

## tables/14_mean_class_metrics.csv

- 자료 제목: mean_class_metrics
- 실험 목적: 14단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: signed-log 과거 Fold 평균0.800290 대 기준0.797082. 사전 개선 기준 미달이며 일관된 균형 개선을 확인하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/nonlinear_feature_transformation/mean_class_metrics.csv`
- 파일 지문 SHA-256: `9de38d8993612702d5568f32a5a35277c466ceef7d60a3485c04f9bca27e9379`

## tables/14_mean_gas_deltas.csv

- 자료 제목: mean_gas_deltas
- 실험 목적: 14단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: signed-log 과거 Fold 평균0.800290 대 기준0.797082. 사전 개선 기준 미달이며 일관된 균형 개선을 확인하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/nonlinear_feature_transformation/mean_gas_deltas.csv`
- 파일 지문 SHA-256: `eab3aad8ae5ebef86e8ee507fe1861850a6309c974e8a4e999d02eb84ad0eeff`

## tables/14_model_registry.csv

- 자료 제목: model_registry
- 실험 목적: 14단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: signed-log 과거 Fold 평균0.800290 대 기준0.797082. 사전 개선 기준 미달이며 일관된 균형 개선을 확인하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/nonlinear_feature_transformation/model_registry.csv`
- 파일 지문 SHA-256: `bdaee39ade14a2616299864f90e4dd8add84452819f38171829a447bc44835a3`

## tables/14_preprocessing_statistics.csv

- 자료 제목: preprocessing_statistics
- 실험 목적: 14단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: signed-log 과거 Fold 평균0.800290 대 기준0.797082. 사전 개선 기준 미달이며 일관된 균형 개선을 확인하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/nonlinear_feature_transformation/preprocessing_statistics.csv`
- 파일 지문 SHA-256: `4b64f141c7952b5362b4c5778e65c20ce79ff3d1e0ebf2968603e7f0f492f022`

## tables/14_protection_checks.csv

- 자료 제목: protection_checks
- 실험 목적: 14단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: signed-log 과거 Fold 평균0.800290 대 기준0.797082. 사전 개선 기준 미달이며 일관된 균형 개선을 확인하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/nonlinear_feature_transformation/protection_checks.csv`
- 파일 지문 SHA-256: `4cd1dedb4859f314338d44641e11a14582d1a84215d326943ecbf5c90206b003`

## tables/14_summary.csv

- 자료 제목: summary
- 실험 목적: 14단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: signed-log 과거 Fold 평균0.800290 대 기준0.797082. 사전 개선 기준 미달이며 일관된 균형 개선을 확인하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/nonlinear_feature_transformation/summary.csv`
- 파일 지문 SHA-256: `59d96bff2e8908cec3248bf4c816a2a73b1a59be1ecd2ea413305ab144e0e249`

## tables/14_train_only_audit.csv

- 자료 제목: train_only_audit
- 실험 목적: 14단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: signed-log 과거 Fold 평균0.800290 대 기준0.797082. 사전 개선 기준 미달이며 일관된 균형 개선을 확인하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/nonlinear_feature_transformation/train_only_audit.csv`
- 파일 지문 SHA-256: `3fc09dcd490ad0d8b5350349be3fa62434aca49352173bc729da75b0cc4fe4ce`

## png/15_agreement_disagreement.png

- 자료 제목: agreement_disagreement
- 실험 목적: 15단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_svm_ensemble/agreement_disagreement.png`
- 파일 지문 SHA-256: `e850a820646fa76b67b9d7cae99d1795b6f9b7fa8e6d7f8b93914c5b6acaaafb`

## png/15_confusion_matrices.png

- 자료 제목: confusion_matrices
- 실험 목적: 15단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_svm_ensemble/confusion_matrices.png`
- 파일 지문 SHA-256: `d13666bf532c6493fc729612b437253d6d5d2e788755f5675d1aa63bed0220a2`

## png/15_directional_errors.png

- 자료 제목: directional_errors
- 실험 목적: 15단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_svm_ensemble/directional_errors.png`
- 파일 지문 SHA-256: `01581c2fe627b6226ded31603268ab36add1a8aa0734e64c571b0e9fdaa7279c`

## png/15_expert_mean_macro.png

- 자료 제목: expert_mean_macro
- 실험 목적: 15단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_svm_ensemble/expert_mean_macro.png`
- 파일 지문 SHA-256: `0a5df8ec09d6faa195651e9b7918c6b2e4d8dd9678d4351639b996985f566b34`

## png/15_focus_complementarity.png

- 자료 제목: focus_complementarity
- 실험 목적: 15단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_svm_ensemble/focus_complementarity.png`
- 파일 지문 SHA-256: `70f534650b4512b7c726c466745fb65eff10148b68e6314a37b7224f5ea1ac6b`

## png/15_fold_performance.png

- 자료 제목: fold_performance
- 실험 목적: 15단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_svm_ensemble/fold_performance.png`
- 파일 지문 SHA-256: `efb550519832641a505eb172589862e8ac7609e6d242fa50d4ee7e94b05f2cec`

## png/15_oracle_macro.png

- 자료 제목: oracle_macro
- 실험 목적: 15단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_svm_ensemble/oracle_macro.png`
- 파일 지문 SHA-256: `fa8b6f19be3c5e181b15579e56e4877e8112ee82dc6ed545865d4aab15a8ac6a`

## png/15_oracle_recall.png

- 자료 제목: oracle_recall
- 실험 목적: 15단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_svm_ensemble/oracle_recall.png`
- 파일 지문 SHA-256: `a9ec1ad2f7eb9a916d9502c997c1fb6622dab567ab8c062ab01e7841af2aef0e`

## png/15_partial_correct.png

- 자료 제목: partial_correct
- 실험 목적: 15단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_svm_ensemble/partial_correct.png`
- 파일 지문 SHA-256: `65c5c7850daeebdaa02322856f02bfc38919d223fcce23a896b341beccaa6ef4`

## png/15_recall_delta.png

- 자료 제목: recall_delta
- 실험 목적: 15단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_svm_ensemble/recall_delta.png`
- 파일 지문 SHA-256: `2e5ab256602dd6c771515653cf0cf32881cddbc0ba9f909ed1c312dc76cc10eb`

## png/15_recall_heatmap.png

- 자료 제목: recall_heatmap
- 실험 목적: 15단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_svm_ensemble/recall_heatmap.png`
- 파일 지문 SHA-256: `516f13212d88377693b5c8dc8c82b2b3391f97f3285efdd617ba3b0f87ac66a5`

## tables/15_class_batch_support.csv

- 자료 제목: class_batch_support
- 실험 목적: 15단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_svm_ensemble/class_batch_support.csv`
- 파일 지문 SHA-256: `3f5e11da20668161069a79f4384e378f1acebe807713daa1dc0180cd2a097d35`

## tables/15_class_metrics.csv

- 자료 제목: class_metrics
- 실험 목적: 15단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_svm_ensemble/class_metrics.csv`
- 파일 지문 SHA-256: `f8d6a9d6c05f596f61d4fa561e0e3081edbabcc8ac57cfe388ef8f359ef0d1d4`

## tables/15_complementarity_summary.csv

- 자료 제목: complementarity_summary
- 실험 목적: 15단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_svm_ensemble/complementarity_summary.csv`
- 파일 지문 SHA-256: `f4a537000a83c617f69d7fd42e800dd7883fbe7edbc826d434483d21a86fb65a`

## tables/15_confusion.csv

- 자료 제목: confusion
- 실험 목적: 15단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_svm_ensemble/confusion.csv`
- 파일 지문 SHA-256: `b49c67be5d454f990cb4612b6d9b617473c42c2e8228365d1e199117515940db`

## tables/15_ensemble_execution.csv

- 자료 제목: ensemble_execution
- 실험 목적: 15단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_svm_ensemble/ensemble_execution.csv`
- 파일 지문 SHA-256: `f946f61e0cea5edb03d13d44956d84eead1dffb411b3b33970a1e32195a47bdc`

## tables/15_ensemble_metrics.csv

- 자료 제목: ensemble_metrics
- 실험 목적: 15단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_svm_ensemble/ensemble_metrics.csv`
- 파일 지문 SHA-256: `f81776b1b5655dfff19aecae349cd2901fab7110a562efeee1716ad900d6514c`

## tables/15_expert_audit.csv

- 자료 제목: expert_audit
- 실험 목적: 15단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_svm_ensemble/expert_audit.csv`
- 파일 지문 SHA-256: `f0175e55afdf581165f4f789c07ec52343fd6a8dbd342cf4c66eac80b39adf5f`

## tables/15_expert_plan.csv

- 자료 제목: expert_plan
- 실험 목적: 15단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_svm_ensemble/expert_plan.csv`
- 파일 지문 SHA-256: `b1919c740055952b0a31ab766aab1f1088aec9d3005616ee9a6e3e91567c15db`

## tables/15_focus_complementarity.csv

- 자료 제목: focus_complementarity
- 실험 목적: 15단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_svm_ensemble/focus_complementarity.csv`
- 파일 지문 SHA-256: `8b9cd7f8aca27c7c2788dcb65b84e6c31903c84ad7f3475f0daa3ac1b8aacaa9`

## tables/15_fold_metrics.csv

- 자료 제목: fold_metrics
- 실험 목적: 15단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_svm_ensemble/fold_metrics.csv`
- 파일 지문 SHA-256: `a612fdcee890230f9ce5c6e811bac03e34631d14815179db4dc18cc9403ea8cf`

## tables/15_graph_manifest.csv

- 자료 제목: graph_manifest
- 실험 목적: 15단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_svm_ensemble/graph_manifest.csv`
- 파일 지문 SHA-256: `e69ba526fd15234195d7e34b4e7a1ff905c90401c31628b9b7a3bd88ee1a4ca8`

## tables/15_mean_class_metrics.csv

- 자료 제목: mean_class_metrics
- 실험 목적: 15단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_svm_ensemble/mean_class_metrics.csv`
- 파일 지문 SHA-256: `803bc9f1b2cefcd75fc4b4ee47114178a717dce137824f6865cc5273f59dcc4b`

## tables/15_pairwise_complementarity.csv

- 자료 제목: pairwise_complementarity
- 실험 목적: 15단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_svm_ensemble/pairwise_complementarity.csv`
- 파일 지문 SHA-256: `8cd21bc3cc7b8ff10e8ede4bfa756d2aec746cb1ab8c12775471bfb743272cb6`

## tables/15_planned_rows.csv

- 자료 제목: planned_rows
- 실험 목적: 15단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_svm_ensemble/planned_rows.csv`
- 파일 지문 SHA-256: `84b68f970dc7876fb998493558377346b5802d1e980482961ad4d12618dc77a2`

## tables/15_pooled_metrics.csv

- 자료 제목: pooled_metrics
- 실험 목적: 15단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_svm_ensemble/pooled_metrics.csv`
- 파일 지문 SHA-256: `f3649d47993554163dff391e9e80ee86b0aa21918eeddaeb1c761ad2e9d9e4bc`

## tables/15_sample_complementarity.csv

- 자료 제목: sample_complementarity
- 실험 목적: 15단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_svm_ensemble/sample_complementarity.csv`
- 파일 지문 SHA-256: `cce09aa0498bfd6cd55c6365ff9115db314b04dc5b0dec6822b17b32ecb406ff`

## tables/15_summary.csv

- 자료 제목: summary
- 실험 목적: 15단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: hard_equal 평균0.740510, 기준0.797082보다 낮음. Oracle은 구현 가능한 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_svm_ensemble/summary.csv`
- 파일 지문 SHA-256: `05d6146779bb9b7458ba0abe6257c96e1d8625fb7dd13c4ff9d4321873bad1f1`

## png/16_confusion_matrices.png

- 자료 제목: confusion_matrices
- 실험 목적: 16단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: HGB 평균0.660984 대 SVM0.797082. 이번 고정 비교에서 우수성 근거 부족.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/hgb_algorithm_comparison/confusion_matrices.png`
- 파일 지문 SHA-256: `fc8a636aedb90c6ca5ddf3fe2ae7ec3790bbf254fd41e5480bf5e852caa45acb`

## png/16_error_agreement.png

- 자료 제목: error_agreement
- 실험 목적: 16단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: HGB 평균0.660984 대 SVM0.797082. 이번 고정 비교에서 우수성 근거 부족.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/hgb_algorithm_comparison/error_agreement.png`
- 파일 지문 SHA-256: `a4407414cf844faba1b482c20638347ba0105c898fe45d1321f1678839aca7cf`

## png/16_focus_error_directions.png

- 자료 제목: focus_error_directions
- 실험 목적: 16단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: HGB 평균0.660984 대 SVM0.797082. 이번 고정 비교에서 우수성 근거 부족.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/hgb_algorithm_comparison/focus_error_directions.png`
- 파일 지문 SHA-256: `93947b02de0f0dc63d9b8bf7df9d8f5757ad89e607f8eb0574cbce6098b48f7f`

## png/16_focus_precision_recall_f1.png

- 자료 제목: focus_precision_recall_f1
- 실험 목적: 16단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: HGB 평균0.660984 대 SVM0.797082. 이번 고정 비교에서 우수성 근거 부족.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/hgb_algorithm_comparison/focus_precision_recall_f1.png`
- 파일 지문 SHA-256: `13332df5d9418f2aa701d20c224ac44636a1688cd88048bf212f2e06cb6127af`

## png/16_fold_macro_f1.png

- 자료 제목: fold_macro_f1
- 실험 목적: 16단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: HGB 평균0.660984 대 SVM0.797082. 이번 고정 비교에서 우수성 근거 부족.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/hgb_algorithm_comparison/fold_macro_f1.png`
- 파일 지문 SHA-256: `608d52c5d4919160721212dcd2bd9b9ad22afb977b498e02ca8d67d99551a846`

## png/16_mean_macro_f1.png

- 자료 제목: mean_macro_f1
- 실험 목적: 16단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: HGB 평균0.660984 대 SVM0.797082. 이번 고정 비교에서 우수성 근거 부족.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/hgb_algorithm_comparison/mean_macro_f1.png`
- 파일 지문 SHA-256: `5a7c05648cd87e839d75398084401982367aeff665d8d7d628ba6ec870ef47a4`

## png/16_recall_delta.png

- 자료 제목: recall_delta
- 실험 목적: 16단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: HGB 평균0.660984 대 SVM0.797082. 이번 고정 비교에서 우수성 근거 부족.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/hgb_algorithm_comparison/recall_delta.png`
- 파일 지문 SHA-256: `e3fd733a2c357245a7f9f86b59d8eb05d999645f2654d77f30156bf002f9d380`

## png/16_recall_heatmap.png

- 자료 제목: recall_heatmap
- 실험 목적: 16단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: HGB 평균0.660984 대 SVM0.797082. 이번 고정 비교에서 우수성 근거 부족.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/hgb_algorithm_comparison/recall_heatmap.png`
- 파일 지문 SHA-256: `d3695d0787a938b46e4f433abb2aca12647375570a2d6121866a4d3dee33d5a9`

## tables/16_class_delta_percentages.csv

- 자료 제목: class_delta_percentages
- 실험 목적: 16단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: HGB 평균0.660984 대 SVM0.797082. 이번 고정 비교에서 우수성 근거 부족.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/hgb_algorithm_comparison/class_delta_percentages.csv`
- 파일 지문 SHA-256: `32a788914ab1932195d17fac146ec3a12daf7263340c1e08bc6e04228eab53cb`

## tables/16_class_deltas.csv

- 자료 제목: class_deltas
- 실험 목적: 16단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: HGB 평균0.660984 대 SVM0.797082. 이번 고정 비교에서 우수성 근거 부족.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/hgb_algorithm_comparison/class_deltas.csv`
- 파일 지문 SHA-256: `10b9425a260bb127ebedc45494c0869bbc88822ec8d6ea788a5a1ffaa5e6acf4`

## tables/16_class_metrics.csv

- 자료 제목: class_metrics
- 실험 목적: 16단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: HGB 평균0.660984 대 SVM0.797082. 이번 고정 비교에서 우수성 근거 부족.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/hgb_algorithm_comparison/class_metrics.csv`
- 파일 지문 SHA-256: `4f34d55e6f51a357728dc3e876d0f45fc0b0d1abc450fcc22e778443fb12dd3c`

## tables/16_class_weights.csv

- 자료 제목: class_weights
- 실험 목적: 16단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: HGB 평균0.660984 대 SVM0.797082. 이번 고정 비교에서 우수성 근거 부족.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/hgb_algorithm_comparison/class_weights.csv`
- 파일 지문 SHA-256: `b7bc3b7fa400894651b363d3ee9a6e5263445f8eb716539e94c2f868854fde18`

## tables/16_confusion.csv

- 자료 제목: confusion
- 실험 목적: 16단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: HGB 평균0.660984 대 SVM0.797082. 이번 고정 비교에서 우수성 근거 부족.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/hgb_algorithm_comparison/confusion.csv`
- 파일 지문 SHA-256: `650ef026ab50b1d72e06f1919f56d9f4a81df297d2f65b0eb98b00dfc7a29ec6`

## tables/16_error_agreement.csv

- 자료 제목: error_agreement
- 실험 목적: 16단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: HGB 평균0.660984 대 SVM0.797082. 이번 고정 비교에서 우수성 근거 부족.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/hgb_algorithm_comparison/error_agreement.csv`
- 파일 지문 SHA-256: `e4883e50824c2aa307c923ccecbb6262d343a3a6276b3a5f180d44c78e0e3b51`

## tables/16_error_agreement_summary.csv

- 자료 제목: error_agreement_summary
- 실험 목적: 16단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: HGB 평균0.660984 대 SVM0.797082. 이번 고정 비교에서 우수성 근거 부족.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/hgb_algorithm_comparison/error_agreement_summary.csv`
- 파일 지문 SHA-256: `20314046e86103393e9a8cd1e127c728c0f4c4f6c6278c92d417b352ffe82303`

## tables/16_error_directions.csv

- 자료 제목: error_directions
- 실험 목적: 16단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: HGB 평균0.660984 대 SVM0.797082. 이번 고정 비교에서 우수성 근거 부족.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/hgb_algorithm_comparison/error_directions.csv`
- 파일 지문 SHA-256: `09ca9fd9f8b09178c9ec8c7a5843e1f40530da4cc3b779bcc1410358c0376601`

## tables/16_focus_error_agreement.csv

- 자료 제목: focus_error_agreement
- 실험 목적: 16단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: HGB 평균0.660984 대 SVM0.797082. 이번 고정 비교에서 우수성 근거 부족.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/hgb_algorithm_comparison/focus_error_agreement.csv`
- 파일 지문 SHA-256: `aabb15ee773767e5a7e39e849c8335eea29a052de3d0005ea74bfb18f45d1bf1`

## tables/16_focus_error_directions.csv

- 자료 제목: focus_error_directions
- 실험 목적: 16단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: HGB 평균0.660984 대 SVM0.797082. 이번 고정 비교에서 우수성 근거 부족.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/hgb_algorithm_comparison/focus_error_directions.csv`
- 파일 지문 SHA-256: `50a87ce0f7950e9f34ed3893026a25984822416d37186db4a7fc745e316b25d2`

## tables/16_fold_metrics.csv

- 자료 제목: fold_metrics
- 실험 목적: 16단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: HGB 평균0.660984 대 SVM0.797082. 이번 고정 비교에서 우수성 근거 부족.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/hgb_algorithm_comparison/fold_metrics.csv`
- 파일 지문 SHA-256: `c4685cb676f20438a61851d3e2dbda7d5ed9e9ae60af34b1cb2d2fa0336e8269`

## tables/16_fold_support.csv

- 자료 제목: fold_support
- 실험 목적: 16단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: HGB 평균0.660984 대 SVM0.797082. 이번 고정 비교에서 우수성 근거 부족.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/hgb_algorithm_comparison/fold_support.csv`
- 파일 지문 SHA-256: `1a82c40c88f4f305ec3ee9d715278a216f1a9f8434a45b0f7479f4b2b9e12be6`

## tables/16_graph_manifest.csv

- 자료 제목: graph_manifest
- 실험 목적: 16단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: HGB 평균0.660984 대 SVM0.797082. 이번 고정 비교에서 우수성 근거 부족.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/hgb_algorithm_comparison/graph_manifest.csv`
- 파일 지문 SHA-256: `27fc789f9404b0c15fa054765cc46fb8189cfb584717eedfed09e7ec9c6c0721`

## tables/16_mean_class_metrics.csv

- 자료 제목: mean_class_metrics
- 실험 목적: 16단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: HGB 평균0.660984 대 SVM0.797082. 이번 고정 비교에서 우수성 근거 부족.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/hgb_algorithm_comparison/mean_class_metrics.csv`
- 파일 지문 SHA-256: `6279f450fcdd4edff51a29cbbbc2c14b29a91c0a616cbd8a36ec897691a8dba7`

## tables/16_summary.csv

- 자료 제목: summary
- 실험 목적: 16단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: HGB 평균0.660984 대 SVM0.797082. 이번 고정 비교에서 우수성 근거 부족.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/hgb_algorithm_comparison/summary.csv`
- 파일 지문 SHA-256: `c24eb46db31febf2ae3a8aa28d6694c49bc0cc0011a2d439c589f12cb71a5512`

## tables/16_train_only_audit.csv

- 자료 제목: train_only_audit
- 실험 목적: 16단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 과거 Fold A Train1–3→6, B Train1–6→7, C Train1–7→8 중심. 겹치는 Train과 반복 사용한 검증 자료이며 독립 반복 표본이 아님. 가스별 시기·support·보호 기준 포함.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: HGB 평균0.660984 대 SVM0.797082. 이번 고정 비교에서 우수성 근거 부족.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/hgb_algorithm_comparison/train_only_audit.csv`
- 파일 지문 SHA-256: `a29a8baa0820e890cab5746db1adb5803b5caeaad24df91859fe7ae756fa88e8`

## png/17_acetaldehyde_metrics.png

- 자료 제목: acetaldehyde_metrics
- 실험 목적: 17단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 목표 Batch6/7/8의 평가50%를 먼저 고정한 뒤 별도5/10/20% 정답 Calibration으로 SVM 적응. 0%와 같은 평가 행 비교. 시드별 평가 집합이 겹치며 새 시기 무정답 일반화와 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 정답 적응 0/5/10/20% 평균 Macro F1=0.802428/0.922580/0.939445/0.946083. 같은 Batch 일부 정답 사용 조건이며 독립 Test 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_calibration/acetaldehyde_metrics.png`
- 파일 지문 SHA-256: `478ff7959abdc894f685948f3a9259f1886a7ebee30f4ad81dd52cf549403143`

## png/17_fold_macro_by_rate.png

- 자료 제목: fold_macro_by_rate
- 실험 목적: 17단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 목표 Batch6/7/8의 평가50%를 먼저 고정한 뒤 별도5/10/20% 정답 Calibration으로 SVM 적응. 0%와 같은 평가 행 비교. 시드별 평가 집합이 겹치며 새 시기 무정답 일반화와 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 정답 적응 0/5/10/20% 평균 Macro F1=0.802428/0.922580/0.939445/0.946083. 같은 Batch 일부 정답 사용 조건이며 독립 Test 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_calibration/fold_macro_by_rate.png`
- 파일 지문 SHA-256: `756136d9cd695ea6185a2789348b42f67cc9851a91a600396e95b26d8d280643`

## png/17_mean_macro_by_rate.png

- 자료 제목: mean_macro_by_rate
- 실험 목적: 17단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 목표 Batch6/7/8의 평가50%를 먼저 고정한 뒤 별도5/10/20% 정답 Calibration으로 SVM 적응. 0%와 같은 평가 행 비교. 시드별 평가 집합이 겹치며 새 시기 무정답 일반화와 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 정답 적응 0/5/10/20% 평균 Macro F1=0.802428/0.922580/0.939445/0.946083. 같은 Batch 일부 정답 사용 조건이며 독립 Test 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_calibration/mean_macro_by_rate.png`
- 파일 지문 SHA-256: `e1784c442e3070bfc6f93454d9011289558e6bdb516ce01ae65d61ae98c0d9ac`

## png/17_recall_delta.png

- 자료 제목: recall_delta
- 실험 목적: 17단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 목표 Batch6/7/8의 평가50%를 먼저 고정한 뒤 별도5/10/20% 정답 Calibration으로 SVM 적응. 0%와 같은 평가 행 비교. 시드별 평가 집합이 겹치며 새 시기 무정답 일반화와 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 정답 적응 0/5/10/20% 평균 Macro F1=0.802428/0.922580/0.939445/0.946083. 같은 Batch 일부 정답 사용 조건이며 독립 Test 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_calibration/recall_delta.png`
- 파일 지문 SHA-256: `32b162797b4b22ca7a6b6a9c2bed48304f84feb800b367dbf2ee5fea8de0dd4b`

## png/17_sample_count_effect.png

- 자료 제목: sample_count_effect
- 실험 목적: 17단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 목표 Batch6/7/8의 평가50%를 먼저 고정한 뒤 별도5/10/20% 정답 Calibration으로 SVM 적응. 0%와 같은 평가 행 비교. 시드별 평가 집합이 겹치며 새 시기 무정답 일반화와 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 정답 적응 0/5/10/20% 평균 Macro F1=0.802428/0.922580/0.939445/0.946083. 같은 Batch 일부 정답 사용 조건이며 독립 Test 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_calibration/sample_count_effect.png`
- 파일 지문 SHA-256: `673474a68135345f3714d59e82ae19ff646337f18504ef42839f7f23f46f334f`

## png/17_seed_variability.png

- 자료 제목: seed_variability
- 실험 목적: 17단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 목표 Batch6/7/8의 평가50%를 먼저 고정한 뒤 별도5/10/20% 정답 Calibration으로 SVM 적응. 0%와 같은 평가 행 비교. 시드별 평가 집합이 겹치며 새 시기 무정답 일반화와 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 정답 적응 0/5/10/20% 평균 Macro F1=0.802428/0.922580/0.939445/0.946083. 같은 Batch 일부 정답 사용 조건이며 독립 Test 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_calibration/seed_variability.png`
- 파일 지문 SHA-256: `a22c7b06f802df6a8a747a24fda590c9dcb4f893e5c22abbf4b3ccdcf9c3e45f`

## png/17_six_gas_f1.png

- 자료 제목: six_gas_f1
- 실험 목적: 17단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 목표 Batch6/7/8의 평가50%를 먼저 고정한 뒤 별도5/10/20% 정답 Calibration으로 SVM 적응. 0%와 같은 평가 행 비교. 시드별 평가 집합이 겹치며 새 시기 무정답 일반화와 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 정답 적응 0/5/10/20% 평균 Macro F1=0.802428/0.922580/0.939445/0.946083. 같은 Batch 일부 정답 사용 조건이며 독립 Test 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_calibration/six_gas_f1.png`
- 파일 지문 SHA-256: `5115cb6ee42a72d71f68f5f67097c356f02f408207cd728838e641b4369a8918`

## png/17_toluene_correct.png

- 자료 제목: toluene_correct
- 실험 목적: 17단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 목표 Batch6/7/8의 평가50%를 먼저 고정한 뒤 별도5/10/20% 정답 Calibration으로 SVM 적응. 0%와 같은 평가 행 비교. 시드별 평가 집합이 겹치며 새 시기 무정답 일반화와 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 정답 적응 0/5/10/20% 평균 Macro F1=0.802428/0.922580/0.939445/0.946083. 같은 Batch 일부 정답 사용 조건이며 독립 Test 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_calibration/toluene_correct.png`
- 파일 지문 SHA-256: `86d270cc6d8eeb929a96016355c0471415050965800b3f11a9e52cfbf544d069`

## png/17_toluene_to_acetaldehyde.png

- 자료 제목: toluene_to_acetaldehyde
- 실험 목적: 17단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 목표 Batch6/7/8의 평가50%를 먼저 고정한 뒤 별도5/10/20% 정답 Calibration으로 SVM 적응. 0%와 같은 평가 행 비교. 시드별 평가 집합이 겹치며 새 시기 무정답 일반화와 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 정답 적응 0/5/10/20% 평균 Macro F1=0.802428/0.922580/0.939445/0.946083. 같은 Batch 일부 정답 사용 조건이며 독립 Test 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_calibration/toluene_to_acetaldehyde.png`
- 파일 지문 SHA-256: `8c2aa7903f9b68157e8efde08cca8f8ce9fefabf47cb2ceefbcc8a63e1dfe8ee`

## tables/17_class_metrics.csv

- 자료 제목: class_metrics
- 실험 목적: 17단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 목표 Batch6/7/8의 평가50%를 먼저 고정한 뒤 별도5/10/20% 정답 Calibration으로 SVM 적응. 0%와 같은 평가 행 비교. 시드별 평가 집합이 겹치며 새 시기 무정답 일반화와 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 정답 적응 0/5/10/20% 평균 Macro F1=0.802428/0.922580/0.939445/0.946083. 같은 Batch 일부 정답 사용 조건이며 독립 Test 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_calibration/class_metrics.csv`
- 파일 지문 SHA-256: `d9c3287f1cba98c3bec34c299c35a444507aeeab3ab142d1ce631a3fc43f823d`

## tables/17_class_weights.csv

- 자료 제목: class_weights
- 실험 목적: 17단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 목표 Batch6/7/8의 평가50%를 먼저 고정한 뒤 별도5/10/20% 정답 Calibration으로 SVM 적응. 0%와 같은 평가 행 비교. 시드별 평가 집합이 겹치며 새 시기 무정답 일반화와 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 정답 적응 0/5/10/20% 평균 Macro F1=0.802428/0.922580/0.939445/0.946083. 같은 Batch 일부 정답 사용 조건이며 독립 Test 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_calibration/class_weights.csv`
- 파일 지문 SHA-256: `8dc043784543dfb198b7c6436a3a078f7769a6d359bb51663e42e9469d1e8195`

## tables/17_confusion.csv

- 자료 제목: confusion
- 실험 목적: 17단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 목표 Batch6/7/8의 평가50%를 먼저 고정한 뒤 별도5/10/20% 정답 Calibration으로 SVM 적응. 0%와 같은 평가 행 비교. 시드별 평가 집합이 겹치며 새 시기 무정답 일반화와 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 정답 적응 0/5/10/20% 평균 Macro F1=0.802428/0.922580/0.939445/0.946083. 같은 Batch 일부 정답 사용 조건이며 독립 Test 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_calibration/confusion.csv`
- 파일 지문 SHA-256: `1de92834a3851bf44d546cb9902c01698ddfe593788cb9ed0717615ee26975a3`

## tables/17_error_directions.csv

- 자료 제목: error_directions
- 실험 목적: 17단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 목표 Batch6/7/8의 평가50%를 먼저 고정한 뒤 별도5/10/20% 정답 Calibration으로 SVM 적응. 0%와 같은 평가 행 비교. 시드별 평가 집합이 겹치며 새 시기 무정답 일반화와 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 정답 적응 0/5/10/20% 평균 Macro F1=0.802428/0.922580/0.939445/0.946083. 같은 Batch 일부 정답 사용 조건이며 독립 Test 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_calibration/error_directions.csv`
- 파일 지문 SHA-256: `93cea2fcfecda3c565bebcf4995f494954e13de41f00f1fa47faa4243647c70c`

## tables/17_evaluation_metrics.csv

- 자료 제목: evaluation_metrics
- 실험 목적: 17단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 목표 Batch6/7/8의 평가50%를 먼저 고정한 뒤 별도5/10/20% 정답 Calibration으로 SVM 적응. 0%와 같은 평가 행 비교. 시드별 평가 집합이 겹치며 새 시기 무정답 일반화와 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 정답 적응 0/5/10/20% 평균 Macro F1=0.802428/0.922580/0.939445/0.946083. 같은 Batch 일부 정답 사용 조건이며 독립 Test 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_calibration/evaluation_metrics.csv`
- 파일 지문 SHA-256: `6b20905c74509fc4994c180bacd01323c765efa943d67a19fad54477a7b1a8b0`

## tables/17_focus_counts.csv

- 자료 제목: focus_counts
- 실험 목적: 17단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 목표 Batch6/7/8의 평가50%를 먼저 고정한 뒤 별도5/10/20% 정답 Calibration으로 SVM 적응. 0%와 같은 평가 행 비교. 시드별 평가 집합이 겹치며 새 시기 무정답 일반화와 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 정답 적응 0/5/10/20% 평균 Macro F1=0.802428/0.922580/0.939445/0.946083. 같은 Batch 일부 정답 사용 조건이며 독립 Test 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_calibration/focus_counts.csv`
- 파일 지문 SHA-256: `027e23127eccec2c77cf79c40dfec2e0cc84708ecfb9744de0356f677d9ce24d`

## tables/17_fold_summary.csv

- 자료 제목: fold_summary
- 실험 목적: 17단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 목표 Batch6/7/8의 평가50%를 먼저 고정한 뒤 별도5/10/20% 정답 Calibration으로 SVM 적응. 0%와 같은 평가 행 비교. 시드별 평가 집합이 겹치며 새 시기 무정답 일반화와 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 정답 적응 0/5/10/20% 평균 Macro F1=0.802428/0.922580/0.939445/0.946083. 같은 Batch 일부 정답 사용 조건이며 독립 Test 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_calibration/fold_summary.csv`
- 파일 지문 SHA-256: `4fb141bc39ce5b599c83eefea5993561874a4f014a7033884085235174b06182`

## tables/17_graph_manifest.csv

- 자료 제목: graph_manifest
- 실험 목적: 17단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 목표 Batch6/7/8의 평가50%를 먼저 고정한 뒤 별도5/10/20% 정답 Calibration으로 SVM 적응. 0%와 같은 평가 행 비교. 시드별 평가 집합이 겹치며 새 시기 무정답 일반화와 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 정답 적응 0/5/10/20% 평균 Macro F1=0.802428/0.922580/0.939445/0.946083. 같은 Batch 일부 정답 사용 조건이며 독립 Test 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_calibration/graph_manifest.csv`
- 파일 지문 SHA-256: `63195118d70519d81bea211fb01e36b9f7437eacbc96d365a0ebdf2eee057ca0`

## tables/17_mean_class_metrics.csv

- 자료 제목: mean_class_metrics
- 실험 목적: 17단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 목표 Batch6/7/8의 평가50%를 먼저 고정한 뒤 별도5/10/20% 정답 Calibration으로 SVM 적응. 0%와 같은 평가 행 비교. 시드별 평가 집합이 겹치며 새 시기 무정답 일반화와 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 정답 적응 0/5/10/20% 평균 Macro F1=0.802428/0.922580/0.939445/0.946083. 같은 Batch 일부 정답 사용 조건이며 독립 Test 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_calibration/mean_class_metrics.csv`
- 파일 지문 SHA-256: `e9108134d0f89ab66109e721c25ed0cfb7ebc6079d834e544688111747ee486a`

## tables/17_metrics.csv

- 자료 제목: metrics
- 실험 목적: 17단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 목표 Batch6/7/8의 평가50%를 먼저 고정한 뒤 별도5/10/20% 정답 Calibration으로 SVM 적응. 0%와 같은 평가 행 비교. 시드별 평가 집합이 겹치며 새 시기 무정답 일반화와 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 정답 적응 0/5/10/20% 평균 Macro F1=0.802428/0.922580/0.939445/0.946083. 같은 Batch 일부 정답 사용 조건이며 독립 Test 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_calibration/metrics.csv`
- 파일 지문 SHA-256: `8e147514b2d06c4c043f35ae96e65facd48a4a243824df9a604438f3a308378d`

## tables/17_overlap_checks.csv

- 자료 제목: overlap_checks
- 실험 목적: 17단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 목표 Batch6/7/8의 평가50%를 먼저 고정한 뒤 별도5/10/20% 정답 Calibration으로 SVM 적응. 0%와 같은 평가 행 비교. 시드별 평가 집합이 겹치며 새 시기 무정답 일반화와 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 정답 적응 0/5/10/20% 평균 Macro F1=0.802428/0.922580/0.939445/0.946083. 같은 Batch 일부 정답 사용 조건이며 독립 Test 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_calibration/overlap_checks.csv`
- 파일 지문 SHA-256: `d3f24b773f7d9ae04e5bf5bc92b4a0a1cf562d219e6973ba1baf94d46cd8b210`

## tables/17_ratio_summary.csv

- 자료 제목: ratio_summary
- 실험 목적: 17단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 목표 Batch6/7/8의 평가50%를 먼저 고정한 뒤 별도5/10/20% 정답 Calibration으로 SVM 적응. 0%와 같은 평가 행 비교. 시드별 평가 집합이 겹치며 새 시기 무정답 일반화와 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 정답 적응 0/5/10/20% 평균 Macro F1=0.802428/0.922580/0.939445/0.946083. 같은 Batch 일부 정답 사용 조건이며 독립 Test 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_calibration/ratio_summary.csv`
- 파일 지문 SHA-256: `66e73b01bfc0e1cc166e30feb0448f69708a00f152f8f827b8b15b7406a5def3`

## tables/17_regression_metrics.csv

- 자료 제목: regression_metrics
- 실험 목적: 17단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 목표 Batch6/7/8의 평가50%를 먼저 고정한 뒤 별도5/10/20% 정답 Calibration으로 SVM 적응. 0%와 같은 평가 행 비교. 시드별 평가 집합이 겹치며 새 시기 무정답 일반화와 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 정답 적응 0/5/10/20% 평균 Macro F1=0.802428/0.922580/0.939445/0.946083. 같은 Batch 일부 정답 사용 조건이며 독립 Test 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_calibration/regression_metrics.csv`
- 파일 지문 SHA-256: `4a9d85dd0a73b06626c3070bc1fd40cfdfb93c11c9bca55fd484eb5367c6b05a`

## tables/17_seed_summary.csv

- 자료 제목: seed_summary
- 실험 목적: 17단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 목표 Batch6/7/8의 평가50%를 먼저 고정한 뒤 별도5/10/20% 정답 Calibration으로 SVM 적응. 0%와 같은 평가 행 비교. 시드별 평가 집합이 겹치며 새 시기 무정답 일반화와 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 정답 적응 0/5/10/20% 평균 Macro F1=0.802428/0.922580/0.939445/0.946083. 같은 Batch 일부 정답 사용 조건이며 독립 Test 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_calibration/seed_summary.csv`
- 파일 지문 SHA-256: `05cdf48be2e96683dd80a0540c31c29757c6371d56a1befaf9bf26a777087c10`

## tables/17_split_support.csv

- 자료 제목: split_support
- 실험 목적: 17단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 목표 Batch6/7/8의 평가50%를 먼저 고정한 뒤 별도5/10/20% 정답 Calibration으로 SVM 적응. 0%와 같은 평가 행 비교. 시드별 평가 집합이 겹치며 새 시기 무정답 일반화와 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 정답 적응 0/5/10/20% 평균 Macro F1=0.802428/0.922580/0.939445/0.946083. 같은 Batch 일부 정답 사용 조건이며 독립 Test 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_calibration/split_support.csv`
- 파일 지문 SHA-256: `f7124c2c55ff0a7e3b5878914f18c21ef885d7421f8c0c8d9f43b7f138eddafb`

## tables/17_train_only_audit.csv

- 자료 제목: train_only_audit
- 실험 목적: 17단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 목표 Batch6/7/8의 평가50%를 먼저 고정한 뒤 별도5/10/20% 정답 Calibration으로 SVM 적응. 0%와 같은 평가 행 비교. 시드별 평가 집합이 겹치며 새 시기 무정답 일반화와 다름.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 정답 적응 0/5/10/20% 평균 Macro F1=0.802428/0.922580/0.939445/0.946083. 같은 Batch 일부 정답 사용 조건이며 독립 Test 성능이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/temporal_calibration/train_only_audit.csv`
- 파일 지문 SHA-256: `b4cecff34909f1b0ae342740a4a66e8376fd65329b47a8091bc56edf07bf450f`

## png/18_batch7_windows.png

- 자료 제목: batch7_windows
- 실험 목적: 18단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Batch7의36창·Batch8의2창 모두 경고. 이는 실제 고장·노화 또는 분류 실패 확정이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection/batch7_windows.png`
- 파일 지문 SHA-256: `d57c58676fb08e4419751f290eeab30d7f7110076a84759222ab288dfae142ce`

## png/18_batch8_windows.png

- 자료 제목: batch8_windows
- 실험 목적: 18단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Batch7의36창·Batch8의2창 모두 경고. 이는 실제 고장·노화 또는 분류 실패 확정이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection/batch8_windows.png`
- 파일 지문 SHA-256: `f4e337b847108ee53f95f4992ce90667e823d4f129f334547162ab473bb9fa7e`

## png/18_calibration_distribution.png

- 자료 제목: calibration_distribution
- 실험 목적: 18단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Batch7의36창·Batch8의2창 모두 경고. 이는 실제 고장·노화 또는 분류 실패 확정이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection/calibration_distribution.png`
- 파일 지문 SHA-256: `58720d403fd3577d0b20d3a6a053a197ec9b17745abfb3a143aec4626ce7d60d`

## png/18_gas_composition.png

- 자료 제목: gas_composition
- 실험 목적: 18단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Batch7의36창·Batch8의2창 모두 경고. 이는 실제 고장·노화 또는 분류 실패 확정이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection/gas_composition.png`
- 파일 지문 SHA-256: `980cb0030b524812480766911dc0f86bcdd24713067ce038b1f2d2c5e4b7cbe3`

## png/18_score_comparison.png

- 자료 제목: score_comparison
- 실험 목적: 18단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Batch7의36창·Batch8의2창 모두 경고. 이는 실제 고장·노화 또는 분류 실패 확정이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection/score_comparison.png`
- 파일 지문 SHA-256: `11c84224e80250ff9fe4a52d62032977f0219ca61417c940abd9b6496781ef89`

## png/18_unsupported_windows.png

- 자료 제목: unsupported_windows
- 실험 목적: 18단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Batch7의36창·Batch8의2창 모두 경고. 이는 실제 고장·노화 또는 분류 실패 확정이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection/unsupported_windows.png`
- 파일 지문 SHA-256: `8b013b8e5fb52117d9811bbc830ef330b4ee1099b6086ed53af0b3f9a28ca5f8`

## png/18_warning_classifier_error.png

- 자료 제목: warning_classifier_error
- 실험 목적: 18단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Batch7의36창·Batch8의2창 모두 경고. 이는 실제 고장·노화 또는 분류 실패 확정이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection/warning_classifier_error.png`
- 파일 지문 SHA-256: `8888090eabc6cd57e512100f917745e885fb48c3beaa6df406e9254dd6fff2a5`

## png/18_warning_rates.png

- 자료 제목: warning_rates
- 실험 목적: 18단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Batch7의36창·Batch8의2창 모두 경고. 이는 실제 고장·노화 또는 분류 실패 확정이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection/warning_rates.png`
- 파일 지문 SHA-256: `59b891a6d834230fdf6e89eeb875ca68f65571dd2a9536c5bcd0370960735ca2`

## tables/18_alert_runs.csv

- 자료 제목: alert_runs
- 실험 목적: 18단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Batch7의36창·Batch8의2창 모두 경고. 이는 실제 고장·노화 또는 분류 실패 확정이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection/alert_runs.csv`
- 파일 지문 SHA-256: `141351ef15b489a4dcebf0f0d3ee93f111e81e1fe8e5f86b02cf585fa6d75994`

## tables/18_associations.csv

- 자료 제목: associations
- 실험 목적: 18단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Batch7의36창·Batch8의2창 모두 경고. 이는 실제 고장·노화 또는 분류 실패 확정이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection/associations.csv`
- 파일 지문 SHA-256: `0c22c37122a65f9f26b12e6e2df4af00c697b9bc0c5d90c8f8d4eae92bebcb4c`

## tables/18_batch_class_counts.csv

- 자료 제목: batch_class_counts
- 실험 목적: 18단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Batch7의36창·Batch8의2창 모두 경고. 이는 실제 고장·노화 또는 분류 실패 확정이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection/batch_class_counts.csv`
- 파일 지문 SHA-256: `fc28dc9da73d768427332203cbdbf5d6276fac1abff34f0673e29cf9561668dd`

## tables/18_batch_classifier_metrics.csv

- 자료 제목: batch_classifier_metrics
- 실험 목적: 18단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Batch7의36창·Batch8의2창 모두 경고. 이는 실제 고장·노화 또는 분류 실패 확정이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection/batch_classifier_metrics.csv`
- 파일 지문 SHA-256: `6b11480a4c1a7fd9129c72c90e7fc32316c850010da911ddfdeba72b3d7a7c16`

## tables/18_class_classifier_metrics.csv

- 자료 제목: class_classifier_metrics
- 실험 목적: 18단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Batch7의36창·Batch8의2창 모두 경고. 이는 실제 고장·노화 또는 분류 실패 확정이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection/class_classifier_metrics.csv`
- 파일 지문 SHA-256: `74e08f3a2e0491392ad0ae0f2a0152d575c869c5a34a10292c1d58d26f094508`

## tables/18_gas_composition.csv

- 자료 제목: gas_composition
- 실험 목적: 18단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Batch7의36창·Batch8의2창 모두 경고. 이는 실제 고장·노화 또는 분류 실패 확정이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection/gas_composition.csv`
- 파일 지문 SHA-256: `c02ca5f9a9a525144497f7707c507e5b7429ff190b9a2498b94c14629d0acca9`

## tables/18_graph_manifest.csv

- 자료 제목: graph_manifest
- 실험 목적: 18단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Batch7의36창·Batch8의2창 모두 경고. 이는 실제 고장·노화 또는 분류 실패 확정이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection/graph_manifest.csv`
- 파일 지문 SHA-256: `e01bec62808b127a00455debfd6c3a6749bae2c5faa11593658eaae79e14197d`

## tables/18_input_audit.csv

- 자료 제목: input_audit
- 실험 목적: 18단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Batch7의36창·Batch8의2창 모두 경고. 이는 실제 고장·노화 또는 분류 실패 확정이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection/input_audit.csv`
- 파일 지문 SHA-256: `9500e135eb201422cf6c3daeb10153ea9d598105b44e924f28b3369dfd10109e`

## tables/18_overlap_checks.csv

- 자료 제목: overlap_checks
- 실험 목적: 18단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Batch7의36창·Batch8의2창 모두 경고. 이는 실제 고장·노화 또는 분류 실패 확정이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection/overlap_checks.csv`
- 파일 지문 SHA-256: `d410518191f826ccd641b556f94e13799fa253718e5ee2e71df251c1229420f6`

## tables/18_partition_summary.csv

- 자료 제목: partition_summary
- 실험 목적: 18단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Batch7의36창·Batch8의2창 모두 경고. 이는 실제 고장·노화 또는 분류 실패 확정이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection/partition_summary.csv`
- 파일 지문 SHA-256: `5223c9457fcfd5023c975df0dd8d442972b00ee1d038f986365f5ed9137f3903`

## tables/18_reload_checks.csv

- 자료 제목: reload_checks
- 실험 목적: 18단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Batch7의36창·Batch8의2창 모두 경고. 이는 실제 고장·노화 또는 분류 실패 확정이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection/reload_checks.csv`
- 파일 지문 SHA-256: `cc854d1d65011255f2772a0fd1894868fb266c2a3000c6b4fdb10f15b8d88008`

## tables/18_score_error_counterexamples.csv

- 자료 제목: score_error_counterexamples
- 실험 목적: 18단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Batch7의36창·Batch8의2창 모두 경고. 이는 실제 고장·노화 또는 분류 실패 확정이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection/score_error_counterexamples.csv`
- 파일 지문 SHA-256: `755f849da5ca79112e3f7f3762fafb7ff4253129d497c64e7a5f28d44075de6c`

## tables/18_warning_error_comparison.csv

- 자료 제목: warning_error_comparison
- 실험 목적: 18단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Batch7의36창·Batch8의2창 모두 경고. 이는 실제 고장·노화 또는 분류 실패 확정이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection/warning_error_comparison.csv`
- 파일 지문 SHA-256: `27f2791424ac092dccfc56863abf2cf3553c77e0e255d255432acbce50233243`

## tables/18_window_class_counts.csv

- 자료 제목: window_class_counts
- 실험 목적: 18단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Batch7의36창·Batch8의2창 모두 경고. 이는 실제 고장·노화 또는 분류 실패 확정이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection/window_class_counts.csv`
- 파일 지문 SHA-256: `280dc7bef93b8cc9362c4ef57a1ed45bc90106ca502a9f7efbb8b696d82b648d`

## tables/18_window_error_analysis.csv

- 자료 제목: window_error_analysis
- 실험 목적: 18단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Batch7의36창·Batch8의2창 모두 경고. 이는 실제 고장·노화 또는 분류 실패 확정이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection/window_error_analysis.csv`
- 파일 지문 SHA-256: `1070f1ee1adbbe1b74a79cf6ec6c9a8719d5cf894614edd32f11af13d59d00f0`

## tables/18_window_gas_support.csv

- 자료 제목: window_gas_support
- 실험 목적: 18단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Batch7의36창·Batch8의2창 모두 경고. 이는 실제 고장·노화 또는 분류 실패 확정이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection/window_gas_support.csv`
- 파일 지문 SHA-256: `cdad7f4572bed557ab2ba6f97595278cff5dc31824091eb4aecb070c2c210eda`

## tables/18_windows.csv

- 자료 제목: windows
- 실험 목적: 18단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: Batch7의36창·Batch8의2창 모두 경고. 이는 실제 고장·노화 또는 분류 실패 확정이 아님.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection/windows.csv`
- 파일 지문 SHA-256: `7e6780e5478e9d040abddcd0947fd161906d33687b237336c82f18772aac4d5c`

## png/18_5_composition_control.png

- 자료 제목: composition_control
- 실험 목적: 18.5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 같은 행의 재배열·가스 구성에 점수가 민감함. 경고율만으로 드리프트 탐지 정확도를 주장할 수 없음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection_sensitivity/composition_control.png`
- 파일 지문 SHA-256: `b7ef2d1732dc4c9384751da70638d7d32acc1449e0a52bfe71a6ef8bc2cf87c5`

## png/18_5_composition_score_comparison.png

- 자료 제목: composition_score_comparison
- 실험 목적: 18.5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 같은 행의 재배열·가스 구성에 점수가 민감함. 경고율만으로 드리프트 탐지 정확도를 주장할 수 없음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection_sensitivity/composition_score_comparison.png`
- 파일 지문 SHA-256: `ef7ab0138c69674b2788ecc85762c981fdf957374a2efa1a03b5f8782ca7b542`

## png/18_5_existing_relationships.png

- 자료 제목: existing_relationships
- 실험 목적: 18.5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 같은 행의 재배열·가스 구성에 점수가 민감함. 경고율만으로 드리프트 탐지 정확도를 주장할 수 없음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection_sensitivity/existing_relationships.png`
- 파일 지문 SHA-256: `1601694dab2a045d7cbf8b5b3aab66002b4f11ad0ed43b4354f2c6ebe00b24f5`

## png/18_5_score_decomposition.png

- 자료 제목: score_decomposition
- 실험 목적: 18.5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 같은 행의 재배열·가스 구성에 점수가 민감함. 경고율만으로 드리프트 탐지 정확도를 주장할 수 없음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection_sensitivity/score_decomposition.png`
- 파일 지문 SHA-256: `776b78cc988416b4388bc77e9635f309d563daf0009e921c205299eb064d2762`

## png/18_5_seed_stability.png

- 자료 제목: seed_stability
- 실험 목적: 18.5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 같은 행의 재배열·가스 구성에 점수가 민감함. 경고율만으로 드리프트 탐지 정확도를 주장할 수 없음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection_sensitivity/seed_stability.png`
- 파일 지문 SHA-256: `30a546c017a1ec89a805d73a6a8c4d8a78e5d5aa09df68203b86b0145f68ae19`

## png/18_5_warning_rates.png

- 자료 제목: warning_rates
- 실험 목적: 18.5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 같은 행의 재배열·가스 구성에 점수가 민감함. 경고율만으로 드리프트 탐지 정확도를 주장할 수 없음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection_sensitivity/warning_rates.png`
- 파일 지문 SHA-256: `be317722de83228b310a3fd2379d93b459f0af8eb35d87fe5894952fa389c37d`

## png/18_5_window_method_means.png

- 자료 제목: window_method_means
- 실험 목적: 18.5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 같은 행의 재배열·가스 구성에 점수가 민감함. 경고율만으로 드리프트 탐지 정확도를 주장할 수 없음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection_sensitivity/window_method_means.png`
- 파일 지문 SHA-256: `7ca8ad69693d5129ea96eac50416fb33cda06da5fb508babeb1b69349e49f1c6`

## tables/18_5_artifact_manifest.csv

- 자료 제목: artifact_manifest
- 실험 목적: 18.5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 같은 행의 재배열·가스 구성에 점수가 민감함. 경고율만으로 드리프트 탐지 정확도를 주장할 수 없음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection_sensitivity/artifact_manifest.csv`
- 파일 지문 SHA-256: `c32bcd5030dd16a70dc3d95f1fdc669c17e98deb1184e4f41db4d8def896243f`

## tables/18_5_condition_summary.csv

- 자료 제목: condition_summary
- 실험 목적: 18.5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 같은 행의 재배열·가스 구성에 점수가 민감함. 경고율만으로 드리프트 탐지 정확도를 주장할 수 없음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection_sensitivity/condition_summary.csv`
- 파일 지문 SHA-256: `1fae7b77ff150e572f74d6ef367fc5e0d476b4fa7873d3d64662dea9db6efe44`

## tables/18_5_controlled_availability.csv

- 자료 제목: controlled_availability
- 실험 목적: 18.5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 같은 행의 재배열·가스 구성에 점수가 민감함. 경고율만으로 드리프트 탐지 정확도를 주장할 수 없음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection_sensitivity/controlled_availability.csv`
- 파일 지문 SHA-256: `128c5cd27259d515ce118842a4b37ff773e49abf22415b9d08c91cd767ba1ff1`

## tables/18_5_controlled_quota.csv

- 자료 제목: controlled_quota
- 실험 목적: 18.5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 같은 행의 재배열·가스 구성에 점수가 민감함. 경고율만으로 드리프트 탐지 정확도를 주장할 수 없음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection_sensitivity/controlled_quota.csv`
- 파일 지문 SHA-256: `7b9db328bd6b098cfd8b77e336c5468dcc52f1fb4f3c859a9d2cc5108915b6e8`

## tables/18_5_controlled_support.csv

- 자료 제목: controlled_support
- 실험 목적: 18.5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 같은 행의 재배열·가스 구성에 점수가 민감함. 경고율만으로 드리프트 탐지 정확도를 주장할 수 없음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection_sensitivity/controlled_support.csv`
- 파일 지문 SHA-256: `3a4949987d38438df6c859f42381ddbed4d456fe5a68ec5179b20487c79fc82b`

## tables/18_5_existing_associations.csv

- 자료 제목: existing_associations
- 실험 목적: 18.5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 같은 행의 재배열·가스 구성에 점수가 민감함. 경고율만으로 드리프트 탐지 정확도를 주장할 수 없음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection_sensitivity/existing_associations.csv`
- 파일 지문 SHA-256: `91474dd15a71dc856f6ebd0159ef858516f1f2ae63891c2c816eb37c85b39746`

## tables/18_5_existing_window_analysis.csv

- 자료 제목: existing_window_analysis
- 실험 목적: 18.5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 같은 행의 재배열·가스 구성에 점수가 민감함. 경고율만으로 드리프트 탐지 정확도를 주장할 수 없음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection_sensitivity/existing_window_analysis.csv`
- 파일 지문 SHA-256: `d733ec0717cfce343e5832f82acddadbb69c046b501c4cc2f9af35b396dbbb27`

## tables/18_5_graph_manifest.csv

- 자료 제목: graph_manifest
- 실험 목적: 18.5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 같은 행의 재배열·가스 구성에 점수가 민감함. 경고율만으로 드리프트 탐지 정확도를 주장할 수 없음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection_sensitivity/graph_manifest.csv`
- 파일 지문 SHA-256: `6ff140b16bf5780bccc4aecd4495172585bdb75c3aac8bd8eeefd7308fd584f6`

## tables/18_5_method_deltas.csv

- 자료 제목: method_deltas
- 실험 목적: 18.5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 같은 행의 재배열·가스 구성에 점수가 민감함. 경고율만으로 드리프트 탐지 정확도를 주장할 수 없음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection_sensitivity/method_deltas.csv`
- 파일 지문 SHA-256: `db4e3aa6dc2252b41dad83e96eb766252e73a649a50c4af2ea0a46c551adc77f`

## tables/18_5_seed_variability.csv

- 자료 제목: seed_variability
- 실험 목적: 18.5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 같은 행의 재배열·가스 구성에 점수가 민감함. 경고율만으로 드리프트 탐지 정확도를 주장할 수 없음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection_sensitivity/seed_variability.csv`
- 파일 지문 SHA-256: `096b37ccded1cd180777ce0381009dc66bb2f667ccab51ad7e6fb4e1ae1e5985`

## tables/18_5_window_gas_composition.csv

- 자료 제목: window_gas_composition
- 실험 목적: 18.5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 같은 행의 재배열·가스 구성에 점수가 민감함. 경고율만으로 드리프트 탐지 정확도를 주장할 수 없음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection_sensitivity/window_gas_composition.csv`
- 파일 지문 SHA-256: `35b185099cb54e16048d8ff78aac259368dd935ff3611a1453ecbc3282f1f5b9`

## tables/18_5_window_scores.csv

- 자료 제목: window_scores
- 실험 목적: 18.5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: Reference2966/Calibration1483/내부1484 (Batch1–6). 고정 RFF512, 100행 창, 임계값0.00825701197565701. Batch7–8의 점수·경고·구성 민감도 사후 진단. 물리적 드리프트 정답 없음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 같은 행의 재배열·가스 구성에 점수가 민감함. 경고율만으로 드리프트 탐지 정확도를 주장할 수 없음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/drift_detection_sensitivity/window_scores.csv`
- 파일 지문 SHA-256: `56446046044cff4fdadcf97161b92258e1382cd819ddb139901c0840d70c8953`

## png/19_streamlit_integration.png

- 자료 제목: streamlit_integration
- 실험 목적: 19단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 고정 Model A와 감지기를 사용하는 웹앱·20-A 기능 검증. 합성 fixture는 기능 테스트용이며 실제 가스 분류 정확도나 현장 정답으로 취급하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/streamlit_integration/streamlit_integration.png`
- 파일 지문 SHA-256: `d4d5ed0f1a5265fb8aba9bd3c2722768b5b18ba1ac77dfe62f4d6c76662e8cc1`

## png/19_5_desktop_result.png

- 자료 제목: desktop_result
- 실험 목적: 19.5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 고정 Model A와 감지기를 사용하는 웹앱·20-A 기능 검증. 합성 fixture는 기능 테스트용이며 실제 가스 분류 정확도나 현장 정답으로 취급하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/streamlit_ux/desktop_result.png`
- 파일 지문 SHA-256: `ae079c07c1cd6287d436573e4f26cba799dcf25fb3a530d413edbffe5b10666a`

## png/19_5_mobile_final.png

- 자료 제목: mobile_final
- 실험 목적: 19.5단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 고정 Model A와 감지기를 사용하는 웹앱·20-A 기능 검증. 합성 fixture는 기능 테스트용이며 실제 가스 분류 정확도나 현장 정답으로 취급하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/streamlit_ux/mobile_final.png`
- 파일 지문 SHA-256: `ebfb15607b77616d0093e51204051ad50d27904463bd522ea100685afe6f3784`

## png/19_6_desktop_final_pattern.png

- 자료 제목: desktop_final_pattern
- 실험 목적: 19.6단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 고정 Model A와 감지기를 사용하는 웹앱·20-A 기능 검증. 합성 fixture는 기능 테스트용이며 실제 가스 분류 정확도나 현장 정답으로 취급하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/streamlit_ui_readability/screenshots/desktop_final_pattern.png`
- 파일 지문 SHA-256: `caf57052cde79a7f8de886a198722f2fcee6049bee3564683a498bfa88c3bfef`

## png/19_6_desktop_final_table.png

- 자료 제목: desktop_final_table
- 실험 목적: 19.6단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 고정 Model A와 감지기를 사용하는 웹앱·20-A 기능 검증. 합성 fixture는 기능 테스트용이며 실제 가스 분류 정확도나 현장 정답으로 취급하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/streamlit_ui_readability/screenshots/desktop_final_table.png`
- 파일 지문 SHA-256: `feb6921e20da9bb2e302f51aaccbe473b7e75b1ccadde93920fdf6c02ce75506`

## png/19_6_desktop_gas.png

- 자료 제목: desktop_gas
- 실험 목적: 19.6단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 고정 Model A와 감지기를 사용하는 웹앱·20-A 기능 검증. 합성 fixture는 기능 테스트용이며 실제 가스 분류 정확도나 현장 정답으로 취급하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/streamlit_ui_readability/screenshots/desktop_gas.png`
- 파일 지문 SHA-256: `7bab49b8ddeed24a4414b146ca3fbd6408b4c3d6aa67eeea6aeb90480256dd2a`

## png/19_6_desktop_pattern.png

- 자료 제목: desktop_pattern
- 실험 목적: 19.6단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 고정 Model A와 감지기를 사용하는 웹앱·20-A 기능 검증. 합성 fixture는 기능 테스트용이며 실제 가스 분류 정확도나 현장 정답으로 취급하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/streamlit_ui_readability/screenshots/desktop_pattern.png`
- 파일 지문 SHA-256: `62b57b308e2c48095bf0667d7cc552cfd214c2659c4a91cac73407293d707d6d`

## png/19_6_desktop_table.png

- 자료 제목: desktop_table
- 실험 목적: 19.6단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 고정 Model A와 감지기를 사용하는 웹앱·20-A 기능 검증. 합성 fixture는 기능 테스트용이며 실제 가스 분류 정확도나 현장 정답으로 취급하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/streamlit_ui_readability/screenshots/desktop_table.png`
- 파일 지문 SHA-256: `5ee0c28198cb7fb73828b7c45f58c527f7bb72418201dd6e65e2b8b54660e6f8`

## png/19_6_mobile_gas.png

- 자료 제목: mobile_gas
- 실험 목적: 19.6단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 고정 Model A와 감지기를 사용하는 웹앱·20-A 기능 검증. 합성 fixture는 기능 테스트용이며 실제 가스 분류 정확도나 현장 정답으로 취급하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/streamlit_ui_readability/screenshots/mobile_gas.png`
- 파일 지문 SHA-256: `3802a8dd038c17d4de1954c447755a64a7a6720ba82f23f60e1181cd39bafead`

## png/19_6_mobile_pattern.png

- 자료 제목: mobile_pattern
- 실험 목적: 19.6단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 고정 Model A와 감지기를 사용하는 웹앱·20-A 기능 검증. 합성 fixture는 기능 테스트용이며 실제 가스 분류 정확도나 현장 정답으로 취급하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/streamlit_ui_readability/screenshots/mobile_pattern.png`
- 파일 지문 SHA-256: `5dd30b77466f5f8add6bdab661d7f0b881f1d1c647f9e0213ccb41df22b4fa45`

## png/19_6_mobile_pattern_scrolled.png

- 자료 제목: mobile_pattern_scrolled
- 실험 목적: 19.6단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 고정 Model A와 감지기를 사용하는 웹앱·20-A 기능 검증. 합성 fixture는 기능 테스트용이며 실제 가스 분류 정확도나 현장 정답으로 취급하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/streamlit_ui_readability/screenshots/mobile_pattern_scrolled.png`
- 파일 지문 SHA-256: `d532f27c094698aeaac981e18a4310dfb13b78d7637ba535e5c89bf4964829d3`

## png/19_6_mobile_predictions.png

- 자료 제목: mobile_predictions
- 실험 목적: 19.6단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 고정 Model A와 감지기를 사용하는 웹앱·20-A 기능 검증. 합성 fixture는 기능 테스트용이며 실제 가스 분류 정확도나 현장 정답으로 취급하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/streamlit_ui_readability/screenshots/mobile_predictions.png`
- 파일 지문 SHA-256: `0eea7e726708a223c98690113dfe4d629f9be0cd270c5fde8140435c8acb6746`

## png/19_6_raw_f128.png

- 자료 제목: raw_f128
- 실험 목적: 19.6단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 고정 Model A와 감지기를 사용하는 웹앱·20-A 기능 검증. 합성 fixture는 기능 테스트용이며 실제 가스 분류 정확도나 현장 정답으로 취급하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/streamlit_ui_readability/screenshots/raw_f128.png`
- 파일 지문 SHA-256: `3e073c4810c9ff9567d39f6b21483060929e3e1cbdbf3e7d057b3b3830ade8d4`

## png/19_6_tablet_final_pattern.png

- 자료 제목: tablet_final_pattern
- 실험 목적: 19.6단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 고정 Model A와 감지기를 사용하는 웹앱·20-A 기능 검증. 합성 fixture는 기능 테스트용이며 실제 가스 분류 정확도나 현장 정답으로 취급하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/streamlit_ui_readability/screenshots/tablet_final_pattern.png`
- 파일 지문 SHA-256: `b4341be78c5814026abccad0dd98ce5646bc7001afd3e3823d4b878bc74f5a04`

## png/19_6_tablet_pattern.png

- 자료 제목: tablet_pattern
- 실험 목적: 19.6단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 고정 Model A와 감지기를 사용하는 웹앱·20-A 기능 검증. 합성 fixture는 기능 테스트용이며 실제 가스 분류 정확도나 현장 정답으로 취급하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 해당 단계 원문 표의 모델·Fold·클래스별 계산값을 그대로 제시함. 단일 그림의 순위로 공식 모델을 교체하지 않음.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/streamlit_ui_readability/screenshots/tablet_pattern.png`
- 파일 지문 SHA-256: `bfb2bad5641c63a5e43d1a3eac05b48e9e7330b202aa4dadacbaafbc36f09277`

## png/20_A_management_ready.png

- 자료 제목: management_ready
- 실험 목적: 20-A단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 고정 Model A와 감지기를 사용하는 웹앱·20-A 기능 검증. 합성 fixture는 기능 테스트용이며 실제 가스 분류 정확도나 현장 정답으로 취급하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 출처·정답·세션·시각·중복·6종 지원·과거 Validation 재사용 검사 후 불변 저장. 실제 데이터의 진위·물리적 독립성은 검증하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/retraining_data_preparation/screenshots/management_ready.png`
- 파일 지문 SHA-256: `1a1ff32ee75d8ee40ed3ee5b37c29286a7a7777fdb97785b8069ef52cf745da1`

## png/20_A_management_save_disabled.png

- 자료 제목: management_save_disabled
- 실험 목적: 20-A단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 고정 Model A와 감지기를 사용하는 웹앱·20-A 기능 검증. 합성 fixture는 기능 테스트용이며 실제 가스 분류 정확도나 현장 정답으로 취급하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 출처·정답·세션·시각·중복·6종 지원·과거 Validation 재사용 검사 후 불변 저장. 실제 데이터의 진위·물리적 독립성은 검증하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/retraining_data_preparation/screenshots/management_save_disabled.png`
- 파일 지문 SHA-256: `7f355243bbd4d5337c10789c7bb1811715ffe805830bcac0fed674534731e561`

## png/20_A_management_validation_blocked.png

- 자료 제목: management_validation_blocked
- 실험 목적: 20-A단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 고정 Model A와 감지기를 사용하는 웹앱·20-A 기능 검증. 합성 fixture는 기능 테스트용이며 실제 가스 분류 정확도나 현장 정답으로 취급하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 출처·정답·세션·시각·중복·6종 지원·과거 Validation 재사용 검사 후 불변 저장. 실제 데이터의 진위·물리적 독립성은 검증하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/retraining_data_preparation/screenshots/management_validation_blocked.png`
- 파일 지문 SHA-256: `da4dae1ba404e69853a755898f75f67d14c096104ea74d2aebe2d1db5364d47d`

## tables/20_A_saved_quality_record.csv

- 자료 제목: 저장된20-A 합성 기능 검증 기록
- 실험 목적: 20-A단계 기존 결과의 설명·비교·사후 진단.
- 데이터·학습/검증/평가 구간: 고정 Model A와 감지기를 사용하는 웹앱·20-A 기능 검증. 합성 fixture는 기능 테스트용이며 실제 가스 분류 정확도나 현장 정답으로 취급하지 않음.
- 사용 모델: 원문 조건과 각 CSV의 model/config/trial 열 기준. EDA는 분류 모델 없음, 감지는 고정 RFF-MMD², 웹앱 기능 검증은 공식 Model A 사용.
- 핵심 결과: 출처·정답·세션·시각·중복·6종 지원·과거 Validation 재사용 검사 후 불변 저장. 실제 데이터의 진위·물리적 독립성은 검증하지 못함.
- 결과 해석: 집계 방식·클래스 support·학습 범위가 같은 조건끼리 비교해야 함. 그림과 상세 표를 함께 사용할 것.
- 한계: 반복 관찰한 개발 자료이며 인과·독립 미래 성능 미입증. 가스 정답 사용 적응과 무정답 감지를 구분. 화면·검증 fixture는 연구 정확도 아님.
- 원본 근거: `outputs/retraining_data_preparation/synthetic_quality_record.json`
- 파일 지문 SHA-256: `fe181af2b08648677d7111bc1b3ac7085e81ff503769ec1d4f283ff44801a4bc`