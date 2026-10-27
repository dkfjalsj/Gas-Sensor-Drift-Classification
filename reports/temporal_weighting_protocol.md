# 9단계 사전 실험 계획

## 고정 분할과 예산
SVM8개 가중치 설정 × Fold A/B/C =24회 분류기 Fit. LR 추가 실험 없음.
A Train1–3→Validation6, B Train1–6→Validation7, C Train1–7→Validation8.
실제 존재하는 가스·Batch만 사용. 합성·재표본화 없음. Train/Validation 클래스·중복 확인.
Fold A Train Toluene79개, Fold C Validation Toluene18개. Fold는 독립 반복 아님.
원본128특징, Train median imputer와 StandardScaler. 전처리는 무가중 Train Fit 유지.
SVM RBF C1,gamma=scale,seed42, 기존 나머지 설정 유지. 가중치만 분류기에 적용.

## 가중치 수식
N=Train크기, n_g=가스 수, n_gb=실재 가스·Batch 셀 수, m_g=가스가 존재하는 Train Batch 수.
c=N/(6*n_g), u=Train의 관찰 Batch 순서0..B-1을0..1로 변환. 실제 경과 시간이 아님.
r=clip(sqrt(n_g/(m_g*n_gb)),0.75,1.5). 모든 raw를 평균1로 정규화해 effective로 사용.
1. class_balanced: raw=c, class_weight=balanced, sample=None.
2. time_linear: raw=c*(1+u), class_weight=balanced, sample=(1+u)/mean(raw).
3. time_exp: raw=c*2**u, class_weight=balanced, sample=2**u/mean(raw).
4. time_recent: raw=c*t, 최근2개 Train Batch t=1.75, 나머지1, class_weight=balanced.
5. class_sample: raw=c, class_weight=None, sample=effective. 동일 유효 가중치의 대조.
6. gas_batch: raw=c*r, class_weight=None. 작은 셀의 완전 역빈도 보정 대신 제한된 제곱근 보정.
7. time_class_shrink: raw=sqrt(c)*(1+u), class_weight=None. 완화된 가스 균형과 시간 결합.
8. time_gas_batch: raw=c*r*sqrt(1+u), class_weight=None. 제한된 셀 보정·완만한 시간 결합.
class_weight의 실제 승수×sample_weight가 effective이며 C_i=C*effective로 기록.
class_sample은 baseline과의 동등성 대조이며 독립적인 새 개선 방법으로 부풀리지 않음.
시간 승수1..2, 셀 승수0.75..1.5. 특정 가스 우대 계수 없음. 모든 가중치 양수.
가스·Batch 보정은 정확히 셀 질량을 같게 만드는 방법이 아니며 작은 셀 과대 영향 방지가 목적.
행별 가중치·셀별 질량·최소최대·가중치 집중도(합w)^2/합w² 기록. 집중도는 독립 표본 수 추정 아님.

## 사전 선정과 보호 기준
기준 class_balanced에 비해 다음을 모두 만족해야 함.
- Fold 평균 Macro F1 하락 최대0.5pp, Toluene/Acetaldehyde 평균 Recall 각각 하락 최대3pp.
- 나머지4종 평균F1 하락 최대2pp, 각 가스 Fold평균F1 하락 최대5pp.
- 전체 최소Recall 하락 최대2pp, 각 Fold 최소Recall 하락 최대5pp.
- 기존에 없던 Recall0 Fold/가스 조합 추가 금지.
- 비기준 후보는0% 조합을 줄이거나 평균Macro F1을0.2pp 이상 높여야 함.
통과 후보가 없으면 원래6단계 SVM 유지. 기준은 항상 비교 집합에 유지.
유효 설정 최고평균의0.5pp 이내에서 적은0% 조합→높은최소Recall→높은
min(Toluene평균Recall,Acetaldehyde평균Recall)→높은합산Macro F1→낮은Fold SD→설정순서.
보호 수치는 사전 탐색 기준이며 통계적 유의성·운영 안전 기준이 아님. 평균만으로 우수 판정 금지.

## 학습 범위 비교와 평가
가중치 후보 선정은3Fold만 사용. 후보의 주 모델은Train1–6으로 기존SVM과 가중치 효과 비교.
같은 설정의Train1–7 모델은 별도 확장 비교이며 주 후보로 사후 교체하지 않음.
기본 설정Train1–6(B모델) vs1–7(C모델)을 공통미래Batch8에서 비교.
Batch8을 보고 학습 범위를 재선정하지 않음. Validation으로 이미 사용한18개 Toluene의 한계 명시.
후보와 모델SHA 고정 후에만9–10 평가. 모든8설정의Train6/7과 기존SVM·8단계Hard Voting 기록.
학습 범위가 다른 모델은 별도 표. 학습량·시기·클래스 구성 효과를 데이터 양 하나로 해석 금지.
과거 Test 재사용의 회고적·탐색적 평가이며 독립 최종Test 아님. 평가 기반 재선정·튜닝 금지.
기존1–8단계 파일·모델·원본·해시·테스트 보존. 기존실패3건은 별도 기록. Commit·Push 금지.
