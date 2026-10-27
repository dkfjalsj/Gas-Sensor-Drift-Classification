
## 계산 결과와 해석


- 로그 변환 평균 Macro F1 80.03% (기준 대비 +0.32%p). 사전 +0.5%p 기준 미달. 모든 보호 기준을 통과한 후보 없음.

- Fold별 개선 방향 불일치: 두 변환 모두 Batch 8에서 상승했으나 Batch 7에서 하락. Batch 8 Toluene support 18개의 작은 평가를 전체 일반화 개선으로 확대 해석하지 않음.

- Fold A Batch 6 Toluene은 세 조건 모두 Recall 0%. 분류 실패 완화 목표 미달.

- 로그 변환은 Toluene의 평균 Precision·F1을 높였지만 Recall은 하락. Acetaldehyde의 평균 Precision·Recall·F1은 모두 하락. 동시 균형 개선 근거 없음.

- 다른 네 가스 평균 F1 변화: 로그 +0.31%p, Yeo–Johnson -1.31%p. 평균 보호 기준 내이지만 개별 가스 손실은 아래 표에 공개.

- 오분류 방향도 상충: Fold A Toluene→Acetaldehyde는 기준416→로그441→Yeo–Johnson430개. Fold B Acetaldehyde→Toluene는67→10→8개로 줄었지만 Acetaldehyde Recall도 하락. 특정 오분류 방향 감소가 전체 정분류 증가를 뜻하지 않음.

- Yeo–Johnson은 평균 Macro F1이 하락하고 Toluene 평균 Recall 손실이 5%p를 초과함. 일부 가스·Fold 향상이 있어 규칙상 B(부분 개선)이나 기준보다 우수한 후보라는 뜻은 아님.

- 해석: 이 두 비선형 변환만으로 시기 변화에 따른 가스 경계 문제를 해결하지 못함. 모든 특징 변환이 무효이거나 센서 드리프트가 유일 원인이라는 결론은 아님.

- 다음 연구는 신규 실험 전 사전 계획을 별도로 고정하고 시기별 모델의 과거 오류 상호 보완성을 검토할 수 있음. 이번 결과를 보고 변환식·보호 기준을 변경하지 않음.


```text
fold            A     B     C  mean
method                             
baseline    61.99 89.69 87.44 79.71
signed_log  63.23 83.48 93.38 80.03
yeo_johnson 60.28 80.03 94.77 78.36
```


```text
     method          gas  precision_delta_pp  recall_delta_pp  f1_delta_pp
 signed_log      Ethanol               +5.25            -2.40        +1.66
 signed_log     Ethylene               -1.06            +4.20        +1.61
 signed_log      Ammonia               -5.41            +1.11        -1.99
 signed_log Acetaldehyde               -0.62            -3.76        -4.30
 signed_log      Acetone               -2.92            +3.21        -0.05
 signed_log      Toluene              +11.80            -1.61        +4.99
yeo_johnson      Ethanol               +3.88            -2.66        +0.81
yeo_johnson     Ethylene               -1.23            +3.28        +1.00
yeo_johnson      Ammonia              -14.50            +2.78        -5.84
yeo_johnson Acetaldehyde               -0.47            -4.97        -5.45
yeo_johnson      Acetone               -4.37            +3.10        -1.21
yeo_johnson      Toluene              +13.78            -6.54        +2.60
```


전체 테스트 146개 통과 / 5개 실패. 기존 실패 5개, 신규 실패 0개. 신규 검사 17/17 통과.


기존 실패: 과거 소스 SHA 불일치, 과거 임시 파일 후보 부재, 승인된 신규 모델 추가와 과거 전역 모델 목록 고정 검사 3건 충돌. 과거 테스트·기준·기록 미수정.


기준 모델 항등 선택 단계 제거 후 feature-name 경고 발생 가능. 원래 예측과 전체 일치 확인. 설치된 scikit-learn의 probability 인자 폐기 예정 경고는 설정 유지에 따른 경고이며 학습 오류 아님.


재실행: 새 빈 결과 경로에서 freeze → run → 전체 pytest → closeout 순서. 기존 경로가 있으면 학습 명령은 덮어쓰기를 거부함. 모델 로딩 시 프로젝트 루트에서 src 모듈 사용.