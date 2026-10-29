# 로컬 웹앱 실행

최신 프로젝트 구조·설치·모델 준비·테스트는 [README.md](README.md)를 따른다.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-streamlit.txt
.\.venv\Scripts\python.exe -B -m src.model_management.initialize
.\.venv\Scripts\python.exe -B -m streamlit run app_streamlit.py --server.address 127.0.0.1
```

입력은 UTF-8 CSV의 f001~f128이며 gas는 선택적 실제 정답이다. 분류·고정 분포 감지·상세 보기·CSV 다운로드·20-A 등록·20-B 후보 학습·20-C 수동 승인과 롤백을 제공한다.

실제 운영은 Model A를 유지한다. 합성 후보는 운영 적용할 수 없고 신규 실제 센서 데이터 성능 개선은 미검증이다. 인증 없는 로컬 프로토타입이며 외부 공개 서비스용 권한 관리가 없다.
