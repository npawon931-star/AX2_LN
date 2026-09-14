# 카카오 REST API 장소 검색 지도

카카오 로컬 REST API로 장소를 검색하고 좌표를 Streamlit 기본 지도에 표시합니다.
카카오 지도 배경을 임베드하는 JavaScript SDK는 사용하지 않습니다.
검색 결과 표의 링크를 누르면 카카오맵에서 해당 장소를 열 수 있습니다.

## 실행

```powershell
cd C:\Users\user\AX2_LN\day06
python -m pip install -r requirements.txt
python -m streamlit run day06-1.py
```

http://localhost:8501 에 접속하여 검색 버튼을 누르세요.
장소명이나 `강남역 카페` 같은 검색어를 입력하면 최대 15곳을 표시합니다.

## 키 설정

`.env`에 `KAKAO_REST_API_KEY=발급받은_REST_API_키`를 설정하세요.
기존에 잘못 명명된 KAKAO_JAVASCRIPT_KEY 변수는 REST API용 이름으로 변경했습니다.
키 값은 서버에서 인증 헤더로만 사용합니다. 키 변경 후에는 앱을 재시작하세요.
이 방식에는 JavaScript 키나 JavaScript SDK 도메인 등록이 필요하지 않습니다.

`basic_map.html`은 이전 Folium 예제 결과물이며 현재 앱에서 사용하지 않습니다.

공식 문서: https://developers.kakao.com/docs/latest/ko/local/dev-guide#search-by-keyword
