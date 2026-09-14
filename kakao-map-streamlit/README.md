# 내 주변 카카오 지도 검색

브라우저에서 현재 위치를 받아, 카카오 Local REST API로 주변 장소를 검색하는 Streamlit 앱입니다.

## 실행

프로젝트 상위 폴더의 `.env`에 카카오 REST API 키를 넣습니다.

```env
KAKAO_REST_API_KEY=발급받은_REST_API_키
OPENWEATHER_API_KEY=발급받은_OPENWEATHER_API_키
```

의존성을 설치하고 실행합니다.

```bash
pip install -r requirements.txt
streamlit run app.py
```

브라우저가 위치 권한을 요청하면 **허용**을 선택하세요. 권한을 허용하기 전이나 위치를 가져오지 못한 경우에는 서울시청이 기본 위치로 표시됩니다.

## 카카오 설정

Kakao Developers에서 애플리케이션을 만든 뒤 앱 키의 **REST API 키**를 사용하세요. 이 앱은 카카오 지도 JavaScript SDK가 아니라 Local REST API를 호출하므로 JavaScript 키가 아닌 REST API 키가 필요합니다.


## 날씨와 추천 옷차림

상위 폴더의 `.env`에 `OPENWEATHER_API_KEY`를 설정하세요. 오늘 날씨, 체감온도, 습도, 풍속, 날씨 이모티콘과 기온·비·눈·바람에 맞는 옷차림을 표시합니다.

일주일 탭은 One Call 3.0의 오늘부터 7일 예보를 표시합니다. 별도 이용 권한이 없는 키(HTTP 401/403)는 기본 5일 / 3시간 예보로 전환합니다. 이 경우 실제 제공된 날짜만 표시하며 최저·최고 기온과 강수확률은 제공된 시간대의 최솟값·최댓값입니다. 첫날과 마지막 날은 일부 시간대만 포함될 수 있습니다.

응답은 10분간 캐시됩니다. 날씨 키 누락이나 API 오류가 있어도 지도 검색은 계속 이용할 수 있습니다. 자동으로 유료 구독을 신청하지 않습니다.

API 안내: https://openweathermap.org/one-call-transfer · https://openweathermap.org/forecast5
## 주요 환율

상위 폴더의 `.env`에 `EXCHANGE_API_KEY`를 설정하세요. 연동 제공사는 [ExchangeRate-API](https://www.exchangerate-api.com/docs/standard-requests)이며 다른 서비스의 키는 호환되지 않습니다.
달러·유로·엔·위안 등 8개 통화의 원화 환율과 통화 간 계산기를 제공합니다. 엔화 카드는 100엔, 나머지는 1단위 기준이며 계산기는 1단위 금액을 입력합니다.
갱신 시각은 한국 시간으로 표시합니다. 성공 응답은 1시간 캐시하며 오류 시에도 지도와 날씨는 이용할 수 있습니다. 은행의 실제 환전 금액과 다를 수 있습니다.
