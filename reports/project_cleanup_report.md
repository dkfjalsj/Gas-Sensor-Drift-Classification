# 프로젝트 최종 자료집 제작·정리 보고

## 완료 범위와 판정

자료집·보관·기능 검증 완료. Git Stage·Commit·Push는 검증 결과를 확인한 뒤 실행하며 실제 결과는 최종 응답과 Git 이력으로 확인할 수 있음.
기존 연구를 다시 학습하거나 평가하지 않았음. 원본 .dat10개·모델325개·공식 임계값·100행 창 유지.

## 결과물

- [독립 최종 HTML](Gas_Sensor_Drift_Final_Report.html):25절 목차, 단계별 원문 전체, 표와 삽입 이미지360개. 60,473,279바이트.
- [Word 자료집 설명](report_materials/materials_guide.md):PNG193개·CSV334개의 제목·목적·데이터 조건·결과·해석·한계·출처·지문 기록.
- ZIP:`Gas_Sensor_Report_Materials.zip`, 65,034,780바이트. 이미 .gitignore의 `*.zip` 규칙으로 제외되며 대용량 중복 배포본이므로 강제 추가하지 않음.
- [근거 자료 목록](research_evidence_index.md), [정리 원문 보관·복원 안내](research_archive/README.md).

## 검증

- 프로젝트 밖 새 폴더에서 ZIP CRC·전체 자료 지문·PNG 해독·CSV UTF-8·한글·HTML 단독성 검증 통과.
- 사용자가 ZIP을 직접 풀어 HTML 한글·그래프·표가 정상 표시됨을 확인함. 브라우저 도구는 file://가 보안 정책으로 차단되어 직접 렌더 검사를 수행하지 않았고 우회하지 않았음.
- HTML 내 외부 이미지·CSS·스크립트 의존0건. 전체 자료 SHA 일치.
- 원본 CSV는 소수 자릿수와 원문 바이트 유지.20-A JSON을 펼친 CSV1개는 원문 값을 JSON 문자열로 보존한 변환이며 신규 연구 수치 아님.
- 상관 히트맵은 기존11단계 센서 내8×8 범위임. 전체128×128 상관행렬은 저장돼 있지 않아 있다고 주장하지 않음.
- 신규 모델 Fit·튜닝·Batch9–10 재평가0회. 성능 값을 유리하게 다시 계산하지 않았음.
- 기존 원본 .dat10/10 지문 일치, 모델325/325 지문 일치. 공식 Model A와 감지기 바이트·임계값 유지.

## 실제 정리 이력

옛 HTML·중복 Markdown·캐시 84개를 개별 gzip으로 지문 검증 보관 후 원래 위치에서 삭제함.
복구 방법:manifest.json의 원래 경로와 압축 파일을 찾아 publication_archive.archived_bytes(row)로 압축·원문 지문을 검증한 바이트를 별도 폴더에 저장함.
연구를 ZIP 하나로 대체하지 않았음. CSV·그래프 원본·분할·예측·설정·모델·코드는 프로젝트에 별도 보존함.

사용자가 화면 확인을 위해 ZIP을 프로젝트 안에 푼 사본530개는 ZIP과 모든 바이트 일치를 확인한 뒤 프로젝트 밖에 그대로 보존 이동함.
위치:`C:/Users/human-20/Documents/ChatGPT/ML 프로젝트 2/user_verified_report_materials_20261028/`.
사용자 확인 사본은 삭제하지 않았으며 원래 ZIP과 reports/report_materials도 유지함.

## 전체 테스트 및 초기 충돌

- 최종 전체 248개 통과 / 기존 실패2개 / 제한 skip90개 / error0개. 신규 실패0개.
- 이전 기준240통과/2기존실패/90skip 대비 신규 자료집 검사8개 추가.
- 기존 실패는 과거 임시 파일 부재와 과거 고정 모델 목록 충돌. 과거 해시·모델·테스트 기준을 바꾸어 통과시키지 않았음.
- 과거 직접 경로 검사는 옛 보고서와 캐시 원문84개를 SHA 검증하여 일시 복원한 실제 파일로 실행함. 검사 뒤 동일 바이트의 이번 복원본만 제거함. 일반 pytest를 그대로 실행하면 옛 경로 검사에서 실패할 수 있으므로 아래 명령 사용.

```powershell
.\.venv\Scripts\python.exe -B -X utf8 -m src.research_maintenance.publication_verify
```

- 최초 검사는 프로젝트 안의 사용자 ZIP 해제 사본으로 HTML 단일성 검사 충돌. 외부 보존 이동으로 해결.
- 정리 직후 검사는 예전 보존 목록이 캐시도 요구하여 충돌. 캐시 원문까지 일시 복원하도록 신규 검증 도구 보완. 기존 테스트 수정 없음.
- 초기 실패 기록은 outputs/report_publication/initial_validation_* 및 post_cleanup_attempt2_*에 보존.
- 기존 AppTest의 CSV 업로드·분류·MMD·정답 비교·100행 처리·다운로드·20-A 검증·시기 분리·불변 저장 검사 포함.
- 새 로컬8504 서버 기동·health200 및 실제 화면 확인은 outputs/report_publication/webapp_runtime.json에 별도 기록함.

## 코드 및 남겨둔 자료

실험 코드·보고서 생성 코드·리뷰·closeout·모델·원본 CSV·분할·실패 실험 근거는 재현·테스트 참조를 위해 유지함.
중복 코드라 하여 과거 진입점이나 pickle 모듈 경로를 삭제하지 않았음. 새 자료집·보관·복원 도구에 한글 주석을 작성함.
현재 데이터·학습·평가 API를 Notebook에서 호출할 수 있으나 기존 main의 출력 경로 덮어쓰기와 과거 자료 재사용을 주의해야 함.
이번 작업에서 Notebook·20-B·20-C는 구현하지 않음.

## 파일별 삭제·복구 위치

| 원래 경로 | 삭제 이유 | 검증 보관본 | 원문 SHA-256 |
|---|---|---|---|
| `.pytest_cache/.gitignore` | 재생성 가능한 캐시; 검증 보관본 유지 | `reports/research_archive/3ed731b65d06150c138e2dadb0be0697550888a6b47eb8c45ecc9adba8b8e9bd.gz` | `3ed731b65d06150c138e2dadb0be0697550888a6b47eb8c45ecc9adba8b8e9bd` |
| `.pytest_cache/CACHEDIR.TAG` | 재생성 가능한 캐시; 검증 보관본 유지 | `reports/research_archive/37dc88ef9a0abeddbe81053a6dd8fdfb13afb613045ea1eb4a5c815a74a3bde4.gz` | `37dc88ef9a0abeddbe81053a6dd8fdfb13afb613045ea1eb4a5c815a74a3bde4` |
| `.pytest_cache/README.md` | 재생성 가능한 캐시; 검증 보관본 유지 | `reports/research_archive/73fd6fccdd802c419a6b2d983d6c3173b7da97558ac4b589edec2dfe443db9ad.gz` | `73fd6fccdd802c419a6b2d983d6c3173b7da97558ac4b589edec2dfe443db9ad` |
| `.pytest_cache/v/cache/lastfailed` | 재생성 가능한 캐시; 검증 보관본 유지 | `reports/research_archive/5163ef0b43e7f3281fa2758022215b540d6c647cc0f3c93f5515ae9adb25caca.gz` | `5163ef0b43e7f3281fa2758022215b540d6c647cc0f3c93f5515ae9adb25caca` |
| `.pytest_cache/v/cache/nodeids` | 재생성 가능한 캐시; 검증 보관본 유지 | `reports/research_archive/1adc9f9b76527599f1c10388e7d9cfa9455ea0c9cb421b7cc50cfa4125b58920.gz` | `1adc9f9b76527599f1c10388e7d9cfa9455ea0c9cb421b7cc50cfa4125b58920` |
| `outputs/gas_specific_temporal_balancing/visual_review_before/gas_specific_temporal_balancing_report.html` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/57dbce8356d272af2230993b88bc53589c86d9427d8ae260c08043ec96db5b53.gz` | `57dbce8356d272af2230993b88bc53589c86d9427d8ae260c08043ec96db5b53` |
| `outputs/temporal_generalization_validation_attempt_1/report_snapshots/temporal_generalization_validation_report.html` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/307f420cc68d2ca4c5a6195b14e50047e01c51c328a4afea443e17cb45803811.gz` | `307f420cc68d2ca4c5a6195b14e50047e01c51c328a4afea443e17cb45803811` |
| `outputs/temporal_representativeness_control/visual_review_before/temporal_representativeness_control_report.html` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/1e2bf9e34bcf00c98b5b43624aeb4644ab4608578a8dd4f14cc2bb56d481731c.gz` | `1e2bf9e34bcf00c98b5b43624aeb4644ab4608578a8dd4f14cc2bb56d481731c` |
| `outputs/temporal_weighting/report_before_plot_order_fix.html` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/f09c2a6acbba53f5caa062fbd332f5ecfbba27e10f1e0bac52ffd50d8ca8c6e9.gz` | `f09c2a6acbba53f5caa062fbd332f5ecfbba27e10f1e0bac52ffd50d8ca8c6e9` |
| `outputs/toluene_analysis_attempt_1/toluene_failure_analysis.html` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/92dc4080bac0a4799960d5eee25d5965b705210d4f57bcc31fe1406d2dee6bb4.gz` | `92dc4080bac0a4799960d5eee25d5965b705210d4f57bcc31fe1406d2dee6bb4` |
| `outputs/toluene_failure_deep_diagnostic_first_review/review_report_snapshot/toluene_failure_deep_diagnostic_report.html` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/9d6274add660a41095a6002cf153b5ebe08bf549bac6d8afd11389fe246a98d0.gz` | `9d6274add660a41095a6002cf153b5ebe08bf549bac6d8afd11389fe246a98d0` |
| `reports/drift_detection_limitations.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/907e7c1fe53fa92d9866db996bee4124acef7963088b712a39ba876d054ca6b6.gz` | `907e7c1fe53fa92d9866db996bee4124acef7963088b712a39ba876d054ca6b6` |
| `reports/drift_detection_report.html` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/7402d86021ad5f2c40abbfc1e51160c18edcdd516c03183108656aa0888dda3f.gz` | `7402d86021ad5f2c40abbfc1e51160c18edcdd516c03183108656aa0888dda3f` |
| `reports/drift_detection_sensitivity_report.html` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/1cd6657fb597258f2b942aa49fcdb11e3cbd56ec1c24e03b2c6de4d6992a28d4.gz` | `1cd6657fb597258f2b942aa49fcdb11e3cbd56ec1c24e03b2c6de4d6992a28d4` |
| `reports/drift_detection_sensitivity_report.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/8aa0c25cf156605c7defe74f5c34887715f0b35ef235c196da199e1fdb209fe5.gz` | `8aa0c25cf156605c7defe74f5c34887715f0b35ef235c196da199e1fdb209fe5` |
| `reports/drift_detection_summary.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/3e3437c3a531512f2597ea4ed5eb107dde862a5c8f5bf3a2ad1756cc0d0dffde.gz` | `3e3437c3a531512f2597ea4ed5eb107dde862a5c8f5bf3a2ad1756cc0d0dffde` |
| `reports/eda_report.html` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/c6a7b1b4f38211169dd7111dd4349eb219d4a330030ec59d94e3077aac263bd9.gz` | `c6a7b1b4f38211169dd7111dd4349eb219d4a330030ec59d94e3077aac263bd9` |
| `reports/evaluation_design.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/df167c648596b3dfc62113c5846c59162e687b4596b2387ce29abbdfb6dbedbe.gz` | `df167c648596b3dfc62113c5846c59162e687b4596b2387ce29abbdfb6dbedbe` |
| `reports/Gas_Sensor_Drift_Final_Report.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/dc60a7ff0d074ee67117000f748dc3c4838e7e0d5315a06bab503163ab9581a4.gz` | `dc60a7ff0d074ee67117000f748dc3c4838e7e0d5315a06bab503163ab9581a4` |
| `reports/gas_specific_temporal_balancing_limitations.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/ba9da5fe572298c898e841eb7d551fa4a882d71dc73a0ad407bda7f7ccf9c933.gz` | `ba9da5fe572298c898e841eb7d551fa4a882d71dc73a0ad407bda7f7ccf9c933` |
| `reports/gas_specific_temporal_balancing_report.html` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/99e2358d9e1b31768391408d96559ea9d1b23aaa3cd29e31df80cdaa1be2f9ba.gz` | `99e2358d9e1b31768391408d96559ea9d1b23aaa3cd29e31df80cdaa1be2f9ba` |
| `reports/gas_specific_temporal_balancing_summary.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/c111f3fefd077934585a85389f8cc0017ca677d2452c370af730508e59ab5fc4.gz` | `c111f3fefd077934585a85389f8cc0017ca677d2452c370af730508e59ab5fc4` |
| `reports/hgb_algorithm_comparison_limitations.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/665ee36aa0fb8e2b31765f775879f52650c26c58edc0ab7dde21189c07ba2cf7.gz` | `665ee36aa0fb8e2b31765f775879f52650c26c58edc0ab7dde21189c07ba2cf7` |
| `reports/hgb_algorithm_comparison_report.html` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/a1996ee6a1c784cdf32155a367bf99a53b365b96eb2ca3d38a995190cf89bab3.gz` | `a1996ee6a1c784cdf32155a367bf99a53b365b96eb2ca3d38a995190cf89bab3` |
| `reports/hgb_algorithm_comparison_summary.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/92015cb1f35911cd67b3264fb982b34b983b1275a02334bb8eb6fe09dcab86f2.gz` | `92015cb1f35911cd67b3264fb982b34b983b1275a02334bb8eb6fe09dcab86f2` |
| `reports/model_comparison_report.html` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/123eabf6dc42d2234fdb2e6673321d38c748d6193c1d9556056ad756753c5514.gz` | `123eabf6dc42d2234fdb2e6673321d38c748d6193c1d9556056ad756753c5514` |
| `reports/model_diagnostic_report.html` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/ef6b9c2ea9a733d5e0a9d858e0a461c15603b2112fd0268dd299772282a9fc31.gz` | `ef6b9c2ea9a733d5e0a9d858e0a461c15603b2112fd0268dd299772282a9fc31` |
| `reports/model_improvement_protocol.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/836f1600b3a27d5f82f769105aeb62d48ecb3aa79b238dd0510d626891b92386.gz` | `836f1600b3a27d5f82f769105aeb62d48ecb3aa79b238dd0510d626891b92386` |
| `reports/model_improvement_report.html` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/3c0c202d85688ca5c1c1ff6bc7d86430bd5c1c5718bea46620f54b505d98ac82.gz` | `3c0c202d85688ca5c1c1ff6bc7d86430bd5c1c5718bea46620f54b505d98ac82` |
| `reports/model_selection_rationale.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/f3f399348f8df0e9e1f0a9c58b8156040f0784e60b70be815d7bf5443549cf3f.gz` | `f3f399348f8df0e9e1f0a9c58b8156040f0784e60b70be815d7bf5443549cf3f` |
| `reports/nonlinear_feature_transformation_limitations.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/b02fd224e44629ebc44ff1dfe24c2fcb39986a1d441c64bac3de19043010fc4b.gz` | `b02fd224e44629ebc44ff1dfe24c2fcb39986a1d441c64bac3de19043010fc4b` |
| `reports/nonlinear_feature_transformation_report.html` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/e1017a8229e747cd254241bb9acf619b3302fa67ddc21209c65aafc80b169d78.gz` | `e1017a8229e747cd254241bb9acf619b3302fa67ddc21209c65aafc80b169d78` |
| `reports/nonlinear_feature_transformation_summary.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/139edc9d73205c65d0f74e5a15ea1a1181863aa3c2605dd2ad1373fcc00c8e8f.gz` | `139edc9d73205c65d0f74e5a15ea1a1181863aa3c2605dd2ad1373fcc00c8e8f` |
| `reports/retraining_data_preparation_report.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/241333ea291cd0f1ec72eed48102af2c5718d5e7614fe41a512e1842f12b885e.gz` | `241333ea291cd0f1ec72eed48102af2c5718d5e7614fe41a512e1842f12b885e` |
| `reports/streamlit_integration_report.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/2ab8ebabae940e81507a66eeffea2d7fdf2a7c29fa754c0ee16e9e9349db4cd2.gz` | `2ab8ebabae940e81507a66eeffea2d7fdf2a7c29fa754c0ee16e9e9349db4cd2` |
| `reports/streamlit_ui_readability_report.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/7965ceb844b0b6608dbfb4984a8db9d6cda796bef44e52094a99f5064a124783.gz` | `7965ceb844b0b6608dbfb4984a8db9d6cda796bef44e52094a99f5064a124783` |
| `reports/streamlit_ux_improvement_report.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/1e430c85088eafa7441ec2933dcd05896e13b3480f633cb3c860d90c713c9256.gz` | `1e430c85088eafa7441ec2933dcd05896e13b3480f633cb3c860d90c713c9256` |
| `reports/temporal_calibration_limitations.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/f61bf1d6a813760e5b48b86014535d4b8b10f5fcbcda6c41bbcf5b41de860192.gz` | `f61bf1d6a813760e5b48b86014535d4b8b10f5fcbcda6c41bbcf5b41de860192` |
| `reports/temporal_calibration_report.html` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/be93a52e3d4eeab4bc59247a50d9134eec97956846ec429aff136dd1b92e5fd0.gz` | `be93a52e3d4eeab4bc59247a50d9134eec97956846ec429aff136dd1b92e5fd0` |
| `reports/temporal_calibration_summary.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/2c527d359f6b22a5a273baef113e247f4fcf77b1df3e4873f0f99e5674184a73.gz` | `2c527d359f6b22a5a273baef113e247f4fcf77b1df3e4873f0f99e5674184a73` |
| `reports/temporal_expansion_model_selection.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/bbe1cce0f0fcfbf94ed1d873af293680a9362f92942db2ba9f7ff58422a2a2d9.gz` | `bbe1cce0f0fcfbf94ed1d873af293680a9362f92942db2ba9f7ff58422a2a2d9` |
| `reports/temporal_expansion_protocol.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/6b77a2dd1af43a0371f5a5d24e8fa94877cc7b5e239cd3f22ab26f9832569624.gz` | `6b77a2dd1af43a0371f5a5d24e8fa94877cc7b5e239cd3f22ab26f9832569624` |
| `reports/temporal_expansion_report.html` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/71c992daf8630bc7c8b9d5122cef7ceee7eab301b72d695d29f93866df22ea29.gz` | `71c992daf8630bc7c8b9d5122cef7ceee7eab301b72d695d29f93866df22ea29` |
| `reports/temporal_expansion_verification.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/ac606a5fc8a03510deda23b08029ef13de1d4b91bd2738163fd84c778b769303.gz` | `ac606a5fc8a03510deda23b08029ef13de1d4b91bd2738163fd84c778b769303` |
| `reports/temporal_failure_diagnostic_report.html` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/4a965b811f3664ff93c190ad0ec76668ddd27430434ed16ba56e12b288a9305b.gz` | `4a965b811f3664ff93c190ad0ec76668ddd27430434ed16ba56e12b288a9305b` |
| `reports/temporal_failure_improvement_proposal.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/e6dbf36d0e74f31c741f6f05e2a1fe266759b7a24ec733275db4dedf29dd9aaa.gz` | `e6dbf36d0e74f31c741f6f05e2a1fe266759b7a24ec733275db4dedf29dd9aaa` |
| `reports/temporal_generalization_limitations.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/0b33e7b72faf9fe5c9a13b9ce4a4d334bdd18b56e3d250899012444b87129368.gz` | `0b33e7b72faf9fe5c9a13b9ce4a4d334bdd18b56e3d250899012444b87129368` |
| `reports/temporal_generalization_validation_report.html` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/dbcb6a59b1160b094121a25ea8836f070cc16ec7790c1ab6eaad0412ad754c37.gz` | `dbcb6a59b1160b094121a25ea8836f070cc16ec7790c1ab6eaad0412ad754c37` |
| `reports/temporal_generalization_validation_summary.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/e77e912fc53d135150ae30c2f3ecd51df755d080694d353017bd829d928e2837.gz` | `e77e912fc53d135150ae30c2f3ecd51df755d080694d353017bd829d928e2837` |
| `reports/temporal_representativeness_control_limitations.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/fdbd9a71b114683e16b3ec946f2550d81a33fff493b0a582992a58742540a5ad.gz` | `fdbd9a71b114683e16b3ec946f2550d81a33fff493b0a582992a58742540a5ad` |
| `reports/temporal_representativeness_control_report.html` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/3dbf69db27abd11bee69342052b4d28dfdec41436694b97b1d32decfad7902b1.gz` | `3dbf69db27abd11bee69342052b4d28dfdec41436694b97b1d32decfad7902b1` |
| `reports/temporal_representativeness_control_summary.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/1583cf25cf56a47f092dc61eaf2a55d0860857cb17ecfa8e7d4fdb75a6c8a6b6.gz` | `1583cf25cf56a47f092dc61eaf2a55d0860857cb17ecfa8e7d4fdb75a6c8a6b6` |
| `reports/temporal_robustness_improvement_report.html` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/152e25c3a28adb26f22b75a402e3163f811b2081190dbfbb10136ae3a580e78a.gz` | `152e25c3a28adb26f22b75a402e3163f811b2081190dbfbb10136ae3a580e78a` |
| `reports/temporal_robustness_model_selection.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/3ddc13f2f957d22e1589390a7b68af0a46142bb2f82a693d23934b98422a3e07.gz` | `3ddc13f2f957d22e1589390a7b68af0a46142bb2f82a693d23934b98422a3e07` |
| `reports/temporal_robustness_protocol.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/b3f164b6bfec007eaba64d6c66a111e86da41b5eddc4a5233a4a22149751d646.gz` | `b3f164b6bfec007eaba64d6c66a111e86da41b5eddc4a5233a4a22149751d646` |
| `reports/temporal_svm_ensemble_limitations.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/073f56354b17440aabf077af2a9e4f1f7a7c41605e84c4dcfd82b3b9308b5670.gz` | `073f56354b17440aabf077af2a9e4f1f7a7c41605e84c4dcfd82b3b9308b5670` |
| `reports/temporal_svm_ensemble_report.html` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/60e9f42c273df252ea7b59613fae6fac5ded071f9241fb118ec6e57910f3a5e6.gz` | `60e9f42c273df252ea7b59613fae6fac5ded071f9241fb118ec6e57910f3a5e6` |
| `reports/temporal_svm_ensemble_summary.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/2b33609cf4e76ae8f70973f9d38d6d605724b2ab7df7e037d49c75cf25291bed.gz` | `2b33609cf4e76ae8f70973f9d38d6d605724b2ab7df7e037d49c75cf25291bed` |
| `reports/temporal_weighting_final_verification.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/92510af362b733f29d91c46b660d1038174e87684198428063608ac5acae60c3.gz` | `92510af362b733f29d91c46b660d1038174e87684198428063608ac5acae60c3` |
| `reports/temporal_weighting_model_selection.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/a599ec943806cfb3b929bfd71c538f1968ce2260086b5241ee9a9dbac84964ab.gz` | `a599ec943806cfb3b929bfd71c538f1968ce2260086b5241ee9a9dbac84964ab` |
| `reports/temporal_weighting_protocol.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/1d0724a5f8c18a9b2835d725416499421b28ebf18498befd9ef270d622188991.gz` | `1d0724a5f8c18a9b2835d725416499421b28ebf18498befd9ef270d622188991` |
| `reports/temporal_weighting_report.html` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/6deeb84be841b3bd1f631c672dfe8fbb9881ea6bae23a5ccf1f5d247697bf60f.gz` | `6deeb84be841b3bd1f631c672dfe8fbb9881ea6bae23a5ccf1f5d247697bf60f` |
| `reports/toluene_failure_analysis.html` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/92dc4080bac0a4799960d5eee25d5965b705210d4f57bcc31fe1406d2dee6bb4.gz` | `92dc4080bac0a4799960d5eee25d5965b705210d4f57bcc31fe1406d2dee6bb4` |
| `reports/toluene_failure_deep_diagnostic_report.html` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/0fbd4e69758f5d74d691ddcd21b3992072a57748ed5a8b524c98ef5af9809ea1.gz` | `0fbd4e69758f5d74d691ddcd21b3992072a57748ed5a8b524c98ef5af9809ea1` |
| `reports/toluene_failure_deep_diagnostic_summary.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/81e67d98a9393965b5691f16d57178db41098f618e85fa30dcc861c47908441c.gz` | `81e67d98a9393965b5691f16d57178db41098f618e85fa30dcc861c47908441c` |
| `reports/toluene_failure_hypothesis_review.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/4483bd18e971873125e29935eceec809fc04d859799261a9b15caff56786d086.gz` | `4483bd18e971873125e29935eceec809fc04d859799261a9b15caff56786d086` |
| `reports/toluene_preservation_proposal.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/d2cf9639fae15b093627dd81a279d358f650c5a6bbe02cb97784a773ab24f943.gz` | `d2cf9639fae15b093627dd81a279d358f650c5a6bbe02cb97784a773ab24f943` |
| `reports/toluene_test_repair_note.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/12dd0d10dd2461bbb28a2dbb279b6d56cad505d46a1add787a09398e870218b5.gz` | `12dd0d10dd2461bbb28a2dbb279b6d56cad505d46a1add787a09398e870218b5` |
| `reports/training_protocol.md` | 통합된 옛 열람 문서의 지문 보관 | `reports/research_archive/2cd4bfbf656d9227f3cf96d1519962de8ea91e3a0f5ef7535ee1af789b7beda2.gz` | `2cd4bfbf656d9227f3cf96d1519962de8ea91e3a0f5ef7535ee1af789b7beda2` |
| `src/__pycache__/__init__.cpython-312.pyc` | 재생성 가능한 캐시; 검증 보관본 유지 | `reports/research_archive/13d04dde811b7c86a7b3b560878030aeb107a6120bb44784ca2db248f91e4112.gz` | `13d04dde811b7c86a7b3b560878030aeb107a6120bb44784ca2db248f91e4112` |
| `src/__pycache__/analysis.cpython-312.pyc` | 재생성 가능한 캐시; 검증 보관본 유지 | `reports/research_archive/701e7778df9822852a7b2e3fc16f81767f26086f6bcfc8fecfc97895e5d921f6.gz` | `701e7778df9822852a7b2e3fc16f81767f26086f6bcfc8fecfc97895e5d921f6` |
| `src/__pycache__/data.cpython-312.pyc` | 재생성 가능한 캐시; 검증 보관본 유지 | `reports/research_archive/69ecde5d003d435234664ccf7e339b985a3d862a0a8d35be21a55654dacacf70.gz` | `69ecde5d003d435234664ccf7e339b985a3d862a0a8d35be21a55654dacacf70` |
| `src/__pycache__/model_report.cpython-312.pyc` | 재생성 가능한 캐시; 검증 보관본 유지 | `reports/research_archive/394dcc0a509acfd703dcc84d04c1e9d3a9c320f2092e52025c306b7e112f3b19.gz` | `394dcc0a509acfd703dcc84d04c1e9d3a9c320f2092e52025c306b7e112f3b19` |
| `src/__pycache__/train_models.cpython-312.pyc` | 재생성 가능한 캐시; 검증 보관본 유지 | `reports/research_archive/181e9d4acf1338509a765353b38a19b837fafdb0eb639c2d00aa5047affc5805.gz` | `181e9d4acf1338509a765353b38a19b837fafdb0eb639c2d00aa5047affc5805` |
| `src/drift_detection/__pycache__/__init__.cpython-312.pyc` | 재생성 가능한 캐시; 검증 보관본 유지 | `reports/research_archive/5313201d130705a8da1ed3d30a87da42f7e36d583ac97fd5db092740d0066dd8.gz` | `5313201d130705a8da1ed3d30a87da42f7e36d583ac97fd5db092740d0066dd8` |
| `src/drift_detection/__pycache__/detector.cpython-312.pyc` | 재생성 가능한 캐시; 검증 보관본 유지 | `reports/research_archive/9a2da36d51e6801fe0bd5e493d612982403aa361cd73adc98f2dc19bd1f33304.gz` | `9a2da36d51e6801fe0bd5e493d612982403aa361cd73adc98f2dc19bd1f33304` |
| `src/webapp/__pycache__/__init__.cpython-312.pyc` | 재생성 가능한 캐시; 검증 보관본 유지 | `reports/research_archive/033dc9f99e0d90c0ffd0fc3238fe3a566ed6908a77f8b307be9d7ea72206b9f5.gz` | `033dc9f99e0d90c0ffd0fc3238fe3a566ed6908a77f8b307be9d7ea72206b9f5` |
| `src/webapp/__pycache__/data_preparation.cpython-312.pyc` | 재생성 가능한 캐시; 검증 보관본 유지 | `reports/research_archive/f5e091ae84af940711daf402fa10796d4645bcecfc7de87c54cb1039cb49a0b3.gz` | `f5e091ae84af940711daf402fa10796d4645bcecfc7de87c54cb1039cb49a0b3` |
| `src/webapp/__pycache__/dataset_registry.cpython-312.pyc` | 재생성 가능한 캐시; 검증 보관본 유지 | `reports/research_archive/609fe065059093834ae26024fa0499f4751adc94123bcd9becd69afe4330a5b3.gz` | `609fe065059093834ae26024fa0499f4751adc94123bcd9becd69afe4330a5b3` |
| `src/webapp/__pycache__/management_ui.cpython-312.pyc` | 재생성 가능한 캐시; 검증 보관본 유지 | `reports/research_archive/00975bf03c9efd14d4c0d951c32d36ba740f39f116e72acd2b51d9a78fe4a9c5.gz` | `00975bf03c9efd14d4c0d951c32d36ba740f39f116e72acd2b51d9a78fe4a9c5` |
| `src/webapp/__pycache__/service.cpython-312.pyc` | 재생성 가능한 캐시; 검증 보관본 유지 | `reports/research_archive/83f07e25ec27e433b0544965d196c96ab8107154a75ef689b95fe610603f413b.gz` | `83f07e25ec27e433b0544965d196c96ab8107154a75ef689b95fe610603f413b` |
| `src/webapp/__pycache__/ui.cpython-312.pyc` | 재생성 가능한 캐시; 검증 보관본 유지 | `reports/research_archive/4035d7827538fa8f3bbb455be10945ed25c8224e4b96cfa6632388878185d0ef.gz` | `4035d7827538fa8f3bbb455be10945ed25c8224e4b96cfa6632388878185d0ef` |
| `tests/__pycache__/test_models.cpython-312-pytest-9.1.1.pyc` | 재생성 가능한 캐시; 검증 보관본 유지 | `reports/research_archive/67078ebd0baf75a387faa34fab94a634ecbbee860bbf3ecde56555a55c27ddff.gz` | `67078ebd0baf75a387faa34fab94a634ecbbee860bbf3ecde56555a55c27ddff` |
| `tests/__pycache__/test_validation.cpython-312-pytest-9.1.1.pyc` | 재생성 가능한 캐시; 검증 보관본 유지 | `reports/research_archive/e891f12afeca1653db2ec3d3bbfeb7fe571ad3a88ed65394b0f8b921fbec7f3d.gz` | `e891f12afeca1653db2ec3d3bbfeb7fe571ad3a88ed65394b0f8b921fbec7f3d` |

## 전후 집계

집계 시점 2026-10-28T07:17:52.502259+00:00. 가상환경·Git 포함 20,671→21,239개, 1,114,534,618→1,268,277,216바이트. 연구 파일 1,605→2,173개, 440,374,270→594,116,868바이트. Word용PNG·CSV·개별원문보관·ZIP 추가 때문에 전체 용량은 증가함. 파일 수나 용량 감소로 연구 보존을 대체하지 않았음. 이 집계 이후 Git 객체·후속 검증 기록·이 문단 추가분은 별도임.

Git 바이트 보존: 새 자료집·지문·스냅샷·신규 코드에만 .gitattributes의 -text를 적용함. .gitignore 및 과거 해시 기록은 변경하지 않음. 원문 HTML·테스트 로그의 기존 정렬 공백은 보존하여 전체 diff --check에 공백 경고가 남을 수 있으며 Python 코드의 공백 검사는 별도로 수행함.
