from __future__ import annotations

import os
import math
from urllib.parse import quote
from datetime import datetime, timedelta, timezone
from pathlib import Path

import folium
import requests
import streamlit as st
from dotenv import load_dotenv
from streamlit_folium import st_folium
from world import CITY_PRESETS, search_cities, city_label, city_key, currency_codes, currency_name, open_places, place_card, safe_url


APP_DIR = Path(__file__).resolve().parent
load_dotenv(APP_DIR.parent / ".env")
load_dotenv(APP_DIR / ".env", override=False)

KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY") or os.getenv("KAKAO_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY", "").strip()
DEFAULT_LOCATION = {"lat": 37.5665, "lon": 126.9780}  # 서울시청

st.set_page_config(page_title="NEARBY · 세계 도시 여행", page_icon="🌍", layout="wide")


@st.cache_data(ttl=300, show_spinner=False)
def search_places(query: str, latitude: float, longitude: float, radius: int) -> list[dict]:
    response = requests.get(
        "https://dapi.kakao.com/v2/local/search/keyword.json",
        headers={"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"},
        params={
            "query": query,
            "x": longitude,
            "y": latitude,
            "radius": radius,
            "sort": "distance",
            "size": 15,
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json().get("documents", [])



@st.cache_data(ttl=300, show_spinner=False)
def check_kakao_connection(api_key: str) -> tuple[str, str]:
    if not api_key or not api_key.strip():
        return "info", "키 미설정 · .env에 KAKAO_REST_API_KEY를 설정해 주세요."
    try:
        response = requests.get(
            "https://dapi.kakao.com/v2/local/search/keyword.json",
            headers={"Authorization": f"KakaoAK {api_key}"},
            params={"query": "서울시청", "size": 1},
            timeout=5,
        )
        if response.status_code == 200:
            payload = response.json()
            if isinstance(payload, dict) and isinstance(payload.get("documents"), list):
                return "success", "연결됨 · 카카오 장소 검색 API를 사용할 수 있어요."
            return "warning", "확인 실패 · API 응답 형식이 올바르지 않아요."
        if response.status_code in (401, 403):
            return "error", "인증 실패 · REST API 키와 카카오 로컬 API 사용 권한을 확인해 주세요."
        if response.status_code == 429:
            return "warning", "호출 한도 초과 · 잠시 후 다시 확인해 주세요."
        return "warning", f"연결 확인 실패 · HTTP {response.status_code}"
    except requests.Timeout:
        return "warning", "연결 시간 초과 · 잠시 후 다시 확인해 주세요."
    except requests.RequestException:
        return "warning", "연결 실패 · 네트워크 상태를 확인해 주세요."
    except ValueError:
        return "warning", "확인 실패 · API 응답을 읽을 수 없어요."


def render_api_status() -> None:
    with st.container(border=True):
        st.markdown("**카카오 API 연결 상태**")
        api_key = KAKAO_REST_API_KEY or ""
        if st.button("다시 확인", key="refresh_kakao_status", use_container_width=True):
            check_kakao_connection.clear(api_key)
        with st.spinner("API 연결 확인 중..."):
            level, message = check_kakao_connection(api_key)
        getattr(st, level)(message)
        st.caption("실제 장소 검색 요청으로 확인하며, 결과는 최대 5분간 유지됩니다.")

def make_map(latitude: float, longitude: float, places: list[dict]) -> folium.Map:
    map_view = folium.Map(location=[latitude, longitude], zoom_start=15, control_scale=True)
    folium.Marker(
        [latitude, longitude],
        tooltip="도시 중심",
        popup="선택한 도시의 중심 위치",
        icon=folium.Icon(color="red", icon="user"),
    ).add_to(map_view)

    for place in places:
        place_lat, place_lon = float(place["y"]), float(place["x"])
        name = escape(place.get("place_name", "장소"))
        address = escape(place.get("road_address_name") or place.get("address_name", ""))
        popup = folium.Popup(
            f'<b>{name}</b><br>{address}<br><a href="{escape(safe_url(place.get("place_url", "#")), quote=True)}" target="_blank" rel="noopener noreferrer">지도에서 보기</a>',
            max_width=320,
        )
        folium.Marker(
            [place_lat, place_lon],
            tooltip=name,
            popup=popup,
            icon=folium.Icon(color="blue", icon="info-sign"),
        ).add_to(map_view)
    return map_view


CURRENCIES = {
    "USD": "미국 달러", "EUR": "유로", "JPY": "일본 엔", "CNY": "중국 위안",
    "GBP": "영국 파운드", "CHF": "스위스 프랑", "CAD": "캐나다 달러", "AUD": "호주 달러",
}


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_exchange_rates(api_key: str) -> dict:
    # Only successful responses are cached; never display URLs containing credentials.
    response = requests.get(
        f"https://v6.exchangerate-api.com/v6/{quote(api_key, safe='')}/latest/USD",
        timeout=10,
    )
    if response.status_code in (401, 403):
        raise ValueError("환율 API 키와 계정 활성화 상태를 확인해 주세요.")
    if response.status_code == 429:
        raise ValueError("환율 API 호출 한도를 초과했습니다.")
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("환율 응답 형식이 올바르지 않습니다.")
    if payload.get("result") != "success":
        messages = {
            "invalid-key": "EXCHANGE_API_KEY가 유효하지 않습니다. ExchangeRate-API 키인지 확인해 주세요.",
            "inactive-account": "환율 API 계정의 이메일 인증을 완료해 주세요.",
            "quota-reached": "환율 API 호출 한도를 초과했습니다.",
        }
        raise ValueError(messages.get(payload.get("error-type"), "환율 제공사에서 데이터를 받지 못했습니다."))
    rates = payload.get("conversion_rates")
    if payload.get("base_code") != "USD" or not isinstance(rates, dict):
        raise ValueError("환율 기준 통화 또는 데이터가 올바르지 않습니다.")
    if any(isinstance(rates.get(code), bool) or not isinstance(rates.get(code), (int, float))
           or not math.isfinite(rates[code]) or rates[code] <= 0
           for code in ["KRW", *CURRENCIES]):
        raise ValueError("일부 통화의 환율이 누락되었거나 올바르지 않습니다.")
    updated = payload.get("time_last_update_unix")
    if isinstance(updated, bool) or not isinstance(updated, (int, float)) or not math.isfinite(updated):
        raise ValueError("환율 갱신 시각이 올바르지 않습니다.")
    try:
        timestamp = datetime.fromtimestamp(updated, timezone(timedelta(hours=9)))
    except (ValueError, OverflowError, OSError):
        raise ValueError("환율 갱신 시각이 올바르지 않습니다.") from None
    return {"rates": rates, "updated": timestamp.strftime("%Y-%m-%d %H:%M")}


def render_exchange_rates() -> None:
    st.markdown('<div class="eyebrow">NEARBY · TRAVEL ESSENTIALS</div>'
                '<div class="card-heading exchange-heading"><strong>💱 주요 환율</strong>'
                '<span class="pill">🇰🇷 원화 기준</span></div>', unsafe_allow_html=True)
    st.caption("외화 기준 원화 환율 · 엔화는 100엔, 나머지는 1단위 기준입니다.")
    if not EXCHANGE_API_KEY:
        st.info("상위 폴더의 .env에 EXCHANGE_API_KEY를 설정하세요. (ExchangeRate-API)")
        return
    try:
        payload = fetch_exchange_rates(EXCHANGE_API_KEY)
    except requests.RequestException:
        st.warning("환율 서비스에 연결하지 못했습니다. 잠시 후 다시 시도해 주세요.")
        return
    except ValueError as exc:
        st.warning(str(exc))
        return
    rates = payload["rates"]
    local_codes = currency_codes(st.session_state.selected_city)
    st.markdown(f"**{escape(city_label(st.session_state.selected_city))} · 현지 환율**")
    for code in local_codes:
        rate = rates.get(code)
        if not isinstance(rate, (int, float)) or isinstance(rate, bool) or not math.isfinite(rate) or rate <= 0:
            st.info(f"{code} 환율은 현재 제공되지 않습니다.")
            continue
        unit = 100 if code == "JPY" else 1
        st.metric(f"{currency_name(code)} · {unit} {code}", f"{rates['KRW'] / rate * unit:,.2f} 원")
    if not local_codes:
        st.info("이 지역의 현지 통화 정보가 없습니다.")
    icons = {"USD": "🗽", "EUR": "🏛️", "JPY": "🌸", "CNY": "🐼",
             "GBP": "🫖", "CHF": "🏔️", "CAD": "🍁", "AUD": "🦘", "KRW": "🇰🇷"}
    cards = []
    for code, name in CURRENCIES.items():
        unit = 100 if code == "JPY" else 1
        value = rates["KRW"] / rates[code] * unit
        cards.append(f'<article class="exchange-tile"><div class="exchange-tile-top">'
                     f'<span class="exchange-icon" aria-hidden="true">{icons[code]}</span>'
                     f'<span class="exchange-code">{code}</span></div>'
                     f'<div class="exchange-name">{name}</div>'
                     f'<div class="exchange-value">{value:,.2f}<span> 원</span></div>'
                     f'<div class="exchange-unit">{unit} {code} 기준</div></article>')
    st.markdown('<div class="exchange-grid">' + ''.join(cards) + '</div>', unsafe_allow_html=True)
    st.caption(f"제공사 갱신: {payload['updated']} (한국 시간) · 조회 결과는 1시간 동안 캐시됩니다.")
    with st.expander("🧮 환율 계산기"):
        labels = {"KRW": "대한민국 원", **CURRENCIES, **{code: currency_name(code) for code in local_codes if code in rates}}
        for code in labels:
            icons.setdefault(code, "💱")
        selection = city_key(st.session_state.selected_city)
        if st.session_state.get("exchange_city") != selection:
            st.session_state.exchange_city = selection
            st.session_state.exchange_source = next((c for c in local_codes if c in labels), "USD")
            st.session_state.exchange_target = "KRW"
        left, right = st.columns(2)
        source = left.selectbox("보내는 통화", list(labels), index=None,
                                format_func=lambda code: f"{icons[code]} {labels[code]} ({code})", key="exchange_source")
        target = right.selectbox("받는 통화", list(labels), index=None,
                                 format_func=lambda code: f"{icons[code]} {labels[code]} ({code})", key="exchange_target")
        amount = st.number_input("환산 금액 (선택한 통화 1단위 기준)", min_value=0.0, max_value=1e12,
                                 value=100.0, step=10.0, key="exchange_amount")
        converted = amount / rates[source] * rates[target]
        st.markdown(f'<div class="exchange-converted"><span>💸 환산 결과</span>'
                    f'<strong>{converted:,.2f} {target}</strong>'
                    f'<small>{amount:,.2f} {source} → {labels[target]}</small></div>',
                    unsafe_allow_html=True)
    st.caption("참고용 환율이며 은행의 현찰·송금 환율 및 수수료는 다를 수 있습니다. "
               "제공: [ExchangeRate-API](https://www.exchangerate-api.com/)")


def weather_emoji(code: int, icon: str = "") -> str:
    if 200 <= code < 300:
        return "⛈️"
    if 300 <= code < 600:
        return "🌧️"
    if 600 <= code < 700:
        return "❄️"
    if 700 <= code < 800:
        return "🌫️"
    if code == 800:
        return "🌙" if icon.endswith("n") else "☀️"
    return "🌤️" if code == 801 else "☁️"


def clothing_advice(temp: float, code: int, wind: float = 0, pop: float = 0) -> str:
    outfits = [(28, "👕 반팔, 반바지, 통기성이 좋은 옷"), (23, "👕 반팔, 얇은 셔츠, 면바지"),
               (20, "👔 긴팔 티셔츠, 얇은 가디건"), (17, "🧥 가디건, 맨투맨, 긴바지"),
               (12, "🧥 재킷, 니트, 가벼운 겉옷"), (9, "🧥 트렌치코트, 도톰한 니트"),
               (5, "🧥 코트, 보온 내의")]
    tips = [next((outfit for threshold, outfit in outfits if temp >= threshold), "🧣 패딩, 목도리, 장갑, 보온 내의")]
    if 200 <= code < 600 or pop >= 0.4:
        tips.append("☔ 우산과 방수 신발을 챙기세요.")
    if 600 <= code < 700:
        tips.append("🥾 눈길에는 미끄럼 방지 신발을 신으세요.")
    if wind >= 7:
        tips.append("🌬️ 바람이 강하니 바람막이를 챙기세요.")
    if temp >= 23 and code in (800, 801):
        tips.append("🧢 모자와 선크림을 챙기세요.")
    return " · ".join(tips)


@st.cache_data(ttl=600, show_spinner=False)
def fetch_weather(endpoint: str, latitude: float, longitude: float, api_key: str) -> dict:
    params = {"lat": latitude, "lon": longitude, "appid": api_key, "units": "metric", "lang": "kr"}
    if endpoint == "3.0/onecall":
        params["exclude"] = "minutely,hourly,alerts"
    response = requests.get(f"https://api.openweathermap.org/data/{endpoint}", params=params, timeout=10)
    # Never expose request URLs containing the API key in error messages.
    if response.status_code != 200:
        return {"_error": response.status_code}
    return response.json()


def forecast_days(payload: dict, daily: bool) -> list[dict]:
    offset = payload.get("timezone_offset", 0) if daily else payload.get("city", {}).get("timezone", 0)
    tz = timezone(timedelta(seconds=offset))
    if daily:
        return [dict(day, date=datetime.fromtimestamp(day["dt"], tz).date()) for day in payload.get("daily", [])[:7]]
    groups = {}
    for item in payload.get("list", []):
        local = datetime.fromtimestamp(item["dt"], tz)
        groups.setdefault(local.date(), []).append((local, item))
    result = []
    for date, entries in sorted(groups.items()):
        representative = min(entries, key=lambda pair: abs(pair[0].hour - 12))[1]
        result.append({"date": date, "weather": representative["weather"],
                       "temp": {"min": min(x["main"]["temp_min"] for _, x in entries),
                                "max": max(x["main"]["temp_max"] for _, x in entries)},
                       "feels_like": {"day": representative["main"]["feels_like"]},
                       "wind_speed": max(x.get("wind", {}).get("speed", 0) for _, x in entries),
                       "pop": max(x.get("pop", 0) for _, x in entries)})
    return result


def weather_error(status: int) -> None:
    if status in (401, 403):
        st.warning("날씨 API 키의 활성화 상태와 이용 권한을 확인해 주세요.")
    elif status == 429:
        st.warning("날씨 API 호출 한도를 초과했습니다. 잠시 후 다시 시도해 주세요.")
    else:
        st.warning(f"날씨 정보를 가져오지 못했습니다. 잠시 후 다시 시도해 주세요. (HTTP {status})")


def render_weather(latitude: float, longitude: float) -> None:
    location_label = escape(city_label(st.session_state.selected_city))
    st.markdown('<div id="weather" class="eyebrow">NEARBY · DAILY WEATHER</div>'
                '<div class="card-heading weather-heading"><strong>오늘, 가볍게 나가볼까요?</strong>'
                f'<span class="pill">📍 {location_label}</span></div>', unsafe_allow_html=True)
    st.caption("선택한 도시의 날씨와 현지 날짜 기준 예보입니다.")
    if not OPENWEATHER_API_KEY:
        st.info("상위 폴더의 .env에 OPENWEATHER_API_KEY를 설정하면 날씨가 표시됩니다.")
        return
    latitude, longitude = round(latitude, 3), round(longitude, 3)
    today_tab, week_tab = st.tabs(["🌞 오늘의 날씨 · 추천 옷", "📅 일주일간의 날씨"])
    with today_tab:
        try:
            current = fetch_weather("2.5/weather", latitude, longitude, OPENWEATHER_API_KEY)
            if "_error" in current:
                weather_error(current["_error"])
            else:
                condition, main = current["weather"][0], current["main"]
                wind = current.get("wind", {}).get("speed", 0)
                description = escape(condition["description"])
                advice = escape(clothing_advice(main["feels_like"], condition["id"], wind))
                st.markdown(
                    '<div class="weather-now"><div class="weather-summary">'
                    f'<span class="weather-symbol" aria-hidden="true">{weather_emoji(condition["id"], condition.get("icon", ""))}</span>'
                    f'<div><div class="weather-description">{description}</div>'
                    f'<div class="weather-temperature">{main["temp"]:.1f}<span>°C</span></div></div></div>'
                    '<div class="weather-stats">'
                    f'<div><span>체감온도</span><strong>{main["feels_like"]:.1f}°</strong></div>'
                    f'<div><span>습도</span><strong>{main["humidity"]}%</strong></div>'
                    f'<div><span>풍속</span><strong>{wind:.1f}<small> m/s</small></strong></div>'
                    '</div></div>'
                    '<div class="weather-outfit"><span>👕 오늘의 추천 옷차림</span>'
                    f'<p>{advice}</p></div>', unsafe_allow_html=True)
                st.caption("체감온도 기준 추천 · 추위와 더위에 대한 민감도에 맞게 조절하세요.")
                tz = timezone(timedelta(seconds=current.get("timezone", 0)))
                observed = datetime.fromtimestamp(current["dt"], tz).strftime("%m/%d %H:%M")
                st.caption(f"관측 시각: {observed} (현지 시간) · 날씨 데이터는 10분간 캐시됩니다.")
        except (requests.RequestException, ValueError, KeyError, TypeError, IndexError):
            st.warning("현재 날씨를 불러올 수 없습니다. 잠시 후 다시 시도해 주세요.")
    with week_tab:
        try:
            payload = fetch_weather("3.0/onecall", latitude, longitude, OPENWEATHER_API_KEY)
            daily = True
            if payload.get("_error") in (401, 403):
                st.info("7일 예보에는 OpenWeather One Call 3.0 이용 권한이 필요합니다. 현재 키로 제공되는 5일 / 3시간 예보를 대신 표시합니다.")
                payload = fetch_weather("2.5/forecast", latitude, longitude, OPENWEATHER_API_KEY)
                daily = False
            if "_error" in payload:
                weather_error(payload["_error"])
            else:
                days = forecast_days(payload, daily)
                if not days:
                    st.info("현재 제공되는 예보가 없습니다.")
                if not daily:
                    st.caption("최저·최고 기온과 강수확률은 제공된 3시간 예보의 최솟값·최댓값입니다. 첫날과 마지막 날은 일부 시간대만 포함될 수 있습니다.")
                cards = []
                for day in days:
                    condition = day["weather"][0]
                    date = day["date"]
                    advice = escape(clothing_advice(day["feels_like"]["day"], condition["id"],
                                                    day.get("wind_speed", 0), day.get("pop", 0)))
                    cards.append(
                        f'<article class="weather-day"><strong>{date:%m/%d} ({"월화수목금토일"[date.weekday()]})</strong>'
                        f'<div class="weather-day-symbol" aria-hidden="true">{weather_emoji(condition["id"])}</div>'
                        f'<div>{escape(condition["description"])}</div>'
                        f'<p><span class="weather-low">{day["temp"]["min"]:.0f}°</span> / '
                        f'<strong>{day["temp"]["max"]:.0f}°</strong></p>'
                        f'<small>강수확률 {day.get("pop", 0):.0%}</small>'
                        f'<p class="weather-day-advice">{advice}</p></article>')
                st.markdown('<div class="weather-grid">' + ''.join(cards) + '</div>', unsafe_allow_html=True)
                st.caption("날짜별 옷차림은 낮 체감온도 기준입니다.")
        except (requests.RequestException, ValueError, KeyError, TypeError, IndexError):
            st.warning("예보를 불러올 수 없습니다. 잠시 후 다시 시도해 주세요.")
    st.caption("날씨 제공: [OpenWeather](https://openweathermap.org/)")


st.markdown("""
<style>
.stApp {background:#faf8f2;color:#252a26}
[data-testid="stHeader"] {background:transparent}
.block-container {max-width:1600px;padding:3rem 2rem}
h1,h2,h3 {color:#202521;letter-spacing:-.04em}
h1 {font-size:clamp(2rem,3.1vw,3.1rem)!important;font-weight:800!important}
.st-key-nav,.st-key-map_card,.st-key-panel,.st-key-recommendations {background:#fffefa;border:1px solid #eeeae2;border-radius:28px;padding:22px;box-shadow:0 8px 30px #333d2910}
.st-key-recommendations h3 {color:#294b3b}
.st-key-nav {padding:16px 8px;text-align:center}
.st-key-nav nav {display:flex;flex-direction:column;align-items:center;gap:22px}
.brand {background:#294b3b;color:white;border-radius:16px;padding:12px;font-weight:800}
.st-key-nav a {display:flex;align-items:center;justify-content:center;width:44px;height:44px;border-radius:16px;color:#45614e}
.st-key-nav a:hover,.st-key-nav a:first-of-type {background:#def0e5}
.st-key-nav svg {width:23px;height:23px;fill:none;stroke:currentColor;stroke-width:1.7}
.trip-intro {display:flex;align-items:center;justify-content:space-between;gap:20px;background:linear-gradient(120deg,#e2f0e7,#f3f3e6);border:1px solid #dce7d9;border-radius:24px;padding:24px 28px;margin:18px 0 20px}
.trip-label {font-size:12px;font-weight:600;color:#526b58}
.trip-intro h2 {font-size:clamp(22px,2.3vw,30px);color:#294b3b;margin:6px 0;padding:0;overflow-wrap:anywhere}
.trip-intro p {font-size:14px;color:#526356;margin:0;line-height:1.7}
.trip-link {flex-shrink:0;color:#294b3b!important;background:#fffefa;border:1px solid #dce7d9;border-radius:24px;padding:10px 16px;font-size:13px;font-weight:600;text-decoration:none!important}
.trip-link:hover {background:#f1f7ed}
@media(max-width:600px) {.trip-intro {align-items:flex-start;flex-direction:column;padding:20px;gap:16px}}
.eyebrow {color:#65816e;font-size:12px;letter-spacing:.17em;font-weight:700;margin-bottom:12px}
.st-key-categories button {border:0;border-radius:24px;min-height:48px;color:#26382c}
.st-key-categories [data-testid="stColumn"]:nth-child(1) button {background:#def0e5}
.st-key-categories [data-testid="stColumn"]:nth-child(2) button {background:#fae3e6}
.st-key-categories [data-testid="stColumn"]:nth-child(3) button {background:#eee5f8}
.st-key-categories [data-testid="stColumn"]:nth-child(4) button {background:#ffead7}
.st-key-categories button:hover {box-shadow:inset 0 0 0 2px #78927e}
button[kind="primary"] {background:#294b3b;color:white;border:0;border-radius:15px}
[data-testid="stForm"] {border:0;padding:0}
[data-testid="stTextInput"] input {background:#f6f5ef;color:#252a26}
.st-key-map_card iframe {border-radius:20px}
.card-heading {display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:12px}
.card-heading strong {font-size:20px}
.pill {background:#e4f1e7;color:#3c654b;border-radius:20px;padding:7px 12px;font-size:12px;white-space:nowrap}
.result {border-radius:20px;padding:18px;margin-bottom:12px}
.result:nth-child(4n+1) {background:#e2f0e7}
.result:nth-child(4n+2) {background:#f9e5e7}
.result:nth-child(4n+3) {background:#eee6f7}
.result:nth-child(4n+4) {background:#ffead8}
.result strong {font-size:16px;color:#26322b}
.result p {font-size:13px;color:#58625b;margin:8px 0;line-height:1.6}
.result a {font-size:12px;font-weight:600;color:#304d3d;text-decoration:none}
.empty {background:#f5f3ec;border-radius:20px;padding:32px 20px;text-align:center;color:#69716b}
.st-key-exchange_card {background:#fffefa;border:1px solid #eeeae2;border-radius:28px;padding:24px;box-shadow:0 8px 30px #333d2910}
.exchange-heading {flex-wrap:wrap;margin-bottom:6px}
.exchange-heading strong {font-size:24px;letter-spacing:-.04em;color:#294b3b}
.exchange-grid {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:12px 0 16px}
.exchange-tile {border-radius:20px;padding:18px;min-width:0;color:#26382c}
.exchange-tile:nth-child(4n+1) {background:#e2f0e7}
.exchange-tile:nth-child(4n+2) {background:#f9e5e7}
.exchange-tile:nth-child(4n+3) {background:#eee6f7}
.exchange-tile:nth-child(4n+4) {background:#ffead8}
.exchange-tile-top {display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:14px}
.exchange-icon {display:flex;align-items:center;justify-content:center;width:40px;height:40px;border-radius:14px;background:#fffefa99;font-size:24px}
.exchange-code {font-size:11px;font-weight:700;letter-spacing:.08em;color:#4d6053}
.exchange-name {font-size:13px;font-weight:600}
.exchange-value {font-size:clamp(18px,1.8vw,26px);font-weight:800;letter-spacing:-.04em;line-height:1.5;overflow-wrap:anywhere;font-variant-numeric:tabular-nums}
.exchange-value span {font-size:12px;font-weight:500}
.exchange-unit {font-size:11px;color:#58625b;margin-top:4px}
.st-key-exchange_card [data-testid="stExpander"] {background:#f6f5ef;border-radius:18px;overflow:hidden}
.st-key-exchange_card [data-testid="stExpander"] details {border-color:#e5e8de;border-radius:18px}
.exchange-converted {display:flex;flex-direction:column;gap:6px;background:#e2f0e7;color:#294b3b;border-radius:18px;padding:20px;margin-top:12px;overflow-wrap:anywhere}
.exchange-converted span,.exchange-converted small {font-size:13px}
.exchange-converted strong {font-size:clamp(22px,3vw,32px);font-variant-numeric:tabular-nums}
@media(max-width:1100px) {.exchange-grid {grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:480px) {.st-key-exchange_card {padding:16px}.exchange-grid {gap:8px}.exchange-tile {padding:12px}}
@media(max-width:340px) {.exchange-grid {grid-template-columns:1fr}}

.st-key-weather_card {background:#fffefa;border:1px solid #eeeae2;border-radius:28px;padding:22px;box-shadow:0 8px 30px #333d2910}
.weather-heading {flex-wrap:wrap;margin-bottom:4px}
.weather-heading strong {font-size:24px;letter-spacing:-.04em;color:#294b3b}
.st-key-weather_card [data-baseweb="tab-list"] {gap:10px}
.st-key-weather_card [data-baseweb="tab"] {background:#f3f2eb;color:#526356;border-radius:14px;padding:8px 14px;height:auto}
.st-key-weather_card [data-baseweb="tab"][aria-selected="true"] {background:#fffefa;color:#294b3b;font-weight:700}
.st-key-weather_card [data-baseweb="tab-highlight"] {background:#52775e}
.weather-now {display:flex;align-items:center;justify-content:space-between;gap:20px;background:#e2f0e7;border-radius:20px;padding:20px;margin-top:12px}
.weather-summary {display:flex;align-items:center;gap:16px}
.weather-symbol {font-size:56px;line-height:1}
.weather-description {font-size:14px;color:#45614e}
.weather-temperature {font-size:48px;font-weight:800;letter-spacing:-.05em;line-height:1.2;color:#294b3b;font-variant-numeric:tabular-nums}
.weather-temperature span {font-size:22px;margin-left:6px;font-weight:500}
.weather-stats {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}
.weather-stats div {display:flex;flex-direction:column;gap:8px}
.weather-stats span {font-size:12px;color:#526356}
.weather-stats strong {font-size:20px;white-space:nowrap;color:#294b3b}
.weather-stats small {font-size:12px;font-weight:500}
.weather-outfit {background:#ffead8;border-radius:18px;padding:14px 18px;margin:12px 0}
.weather-outfit span {font-size:12px;font-weight:700;color:#70513a}
.weather-outfit p {font-size:14px;line-height:1.6;margin:6px 0 0;color:#4d4338}
.weather-grid {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:12px 0}
.weather-day {background:#e2f0e7;border-radius:20px;padding:16px;color:#26382c;font-size:13px;overflow-wrap:anywhere}
.weather-day:nth-child(4n+2) {background:#f9e5e7}
.weather-day:nth-child(4n+3) {background:#eee6f7}
.weather-day:nth-child(4n+4) {background:#ffead8}
.weather-day-symbol {font-size:36px;margin:10px 0}
.weather-day p {margin:8px 0}
.weather-low {color:#456d89}
.weather-day .weather-day-advice {font-size:12px;line-height:1.6;color:#58625b;margin-top:12px}
@media(max-width:1100px) {.weather-now {flex-wrap:wrap}.weather-stats {width:100%}.weather-grid {grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:480px) {.st-key-weather_card {padding:16px}.weather-heading strong {font-size:21px}.weather-now {padding:16px}.weather-temperature {font-size:42px}.weather-stats {gap:10px}.weather-day {padding:12px}}
@media(max-width:340px) {.weather-grid {grid-template-columns:1fr}}

a:focus-visible {outline:3px solid #52775e;outline-offset:3px}
@media(max-width:900px) {
.block-container {padding:1.5rem 1rem}
[data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] .st-key-nav) {flex-wrap:wrap}
[data-testid="stColumn"]:has(.st-key-nav) {order:3;flex:1 1 100%!important;width:100%!important}
[data-testid="stColumn"]:has(.st-key-main) {order:1;flex:1 1 100%!important;width:100%!important}
[data-testid="stColumn"]:has(.st-key-panel) {order:2;flex:1 1 100%!important;width:100%!important}
.st-key-nav nav {flex-direction:row;justify-content:space-around;gap:8px}
.st-key-categories [data-testid="stHorizontalBlock"] {flex-wrap:wrap;gap:8px}
.st-key-categories [data-testid="stColumn"] {flex:1 1 40%!important;min-width:40%!important}
.st-key-map_card,.st-key-panel {padding:16px}
.st-key-map_card iframe {height:440px!important}
}
</style>
""", unsafe_allow_html=True)

from html import escape

st.session_state.setdefault("selected_city", dict(CITY_PRESETS[0]))
st.session_state.setdefault("city_candidates", [])
selected_city = st.session_state.selected_city
latitude, longitude = selected_city["latitude"], selected_city["longitude"]
has_location = False


def select_city(city):
    st.session_state.selected_city = dict(city)
    st.session_state.places = []
    st.session_state.search_context = None
    st.session_state.search_message = ""
    st.session_state.search_term = ""
    st.session_state.city_candidates = []


def nearby_places(term, radius):
    if st.session_state.selected_city["country_code"] == "KR":
        if not KAKAO_REST_API_KEY:
            raise ValueError("국내 장소 검색에 필요한 카카오 API 키가 설정되지 않았습니다.")
        return search_places(term, latitude, longitude, radius)
    if term not in ("카페", "맛집", "편의점", "약국"):
        raise ValueError("해외 장소는 카페·맛집·편의점·약국 카테고리로 검색해 주세요.")
    return open_places(latitude, longitude, radius, term)

for key, value in {"places": [], "search_term": "", "search_radius": 2000,
                   "search_context": None, "search_message": ""}.items():
    st.session_state.setdefault(key, value)


def run_search(term: str, radius: int) -> None:
    st.session_state.search_message = ""
    if not term.strip():
        st.session_state.search_message = "검색어를 입력해 주세요."
        return
    st.session_state.places = []
    st.session_state.search_context = None
    try:
        st.session_state.places = nearby_places(term.strip(), radius)
        st.session_state.search_context = (latitude, longitude, term.strip(), radius)
        if not st.session_state.places:
            st.session_state.search_message = "검색 결과가 없습니다. 검색어나 반경을 바꿔 보세요."
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        st.session_state.search_message = f"검색에 실패했습니다. API 키와 권한을 확인해 주세요. (HTTP {status})"
    except requests.RequestException:
        st.session_state.search_message = "검색 서비스에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요."
    except ValueError as exc:
        st.session_state.search_message = str(exc)


context = st.session_state.search_context
if context and context[:2] != (latitude, longitude):
    run_search(context[2], context[3])

nav_col, main_col, panel_col = st.columns([0.65, 6, 2.7], gap="large")
with nav_col:
    with st.container(key="nav"):
        st.markdown('''<nav aria-label="대시보드 탐색"><div class="brand">N.</div>
<a href="#explore" aria-label="주변 탐색" title="주변 탐색"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="m16 8-3 5-5 3 3-5Z"/></svg></a>
<a href="#map-view" aria-label="지도" title="지도"><svg viewBox="0 0 24 24"><path d="m3 5 6-2 6 2 6-2v16l-6 2-6-2-6 2Zm6-2v16m6-14v16"/></svg></a>
<a href="#search-results" aria-label="검색 결과" title="검색 결과"><svg viewBox="0 0 24 24"><circle cx="10" cy="10" r="6"/><path d="m15 15 6 6"/></svg></a>
<a href="#weather" aria-label="날씨" title="날씨"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path d="M12 1v3m0 16v3M1 12h3m16 0h3M4 4l2 2m12 12 2 2M4 20l2-2M18 6l2-2"/></svg></a></nav>''', unsafe_allow_html=True)

with main_col:
    with st.container(key="main"):
        st.markdown('<div id="explore" class="eyebrow">NEARBY · YOUR LITTLE CITY GUIDE</div>', unsafe_allow_html=True)
        st.title("낯선 도시에서, 나다운 하루")
        st.caption("커피 한 잔부터 오늘의 날씨까지, 여행에 필요한 정보를 한곳에서 만나보세요.")
        st.markdown(
            '<section class="trip-intro" aria-label="선택한 여행지">'
            '<div><span class="trip-label">지금 둘러보는 여행지</span>'
            f'<h2>{escape(city_label(selected_city))}</h2>'
            '<p>도시를 고르고, 마음에 드는 장소를 찾아 가볍게 떠나보세요.</p></div>'
            '<a class="trip-link" href="#map-view">여행 지도 보기 ↗</a></section>',
            unsafe_allow_html=True)
        st.caption("어떤 곳을 찾으세요? 카테고리를 누르면 주변 장소가 지도에 표시돼요.")
        with st.container(key="categories"):
            for col, label, icon in zip(st.columns(4), ["카페", "맛집", "편의점", "약국"],
                                       [":material/local_cafe:", ":material/restaurant:", ":material/storefront:", ":material/local_pharmacy:"]):
                if col.button(label, icon=icon, use_container_width=True):
                    st.session_state.search_term = label
                    run_search(label, st.session_state.search_radius)
        map_slot = st.empty()
        with st.container(key="recommendations"):
            st.markdown('<div class="eyebrow">NEARBY · LOCAL FINDS</div>', unsafe_allow_html=True)
            st.subheader("여행 중 쉬어갈 곳, 든든한 한 끼")
            st.caption("선택한 도시 중심에서 가까운 장소를 추천해요. 평점 순위가 아닌 거리순이며, 방문 전 영업 여부를 확인해 주세요.")
            for recommendation_col, category, heading in zip(st.columns(2), ["카페", "맛집"], ["☕ 추천 카페", "🍽️ 추천 맛집"]):
                with recommendation_col:
                    st.markdown(f"### {heading}")
                    try:
                        recommendations = nearby_places(category, st.session_state.search_radius)
                        if recommendations:
                            st.markdown('<div>' + ''.join(place_card(p, i) for i, p in enumerate(recommendations[:3], 1)) + '</div>', unsafe_allow_html=True)
                        else:
                            st.info("이 반경에 등록된 장소가 없습니다. 검색 반경을 넓혀 보세요.")
                    except (requests.RequestException, ValueError, KeyError, TypeError):
                        st.info("추천 장소를 불러오지 못했습니다. API 설정을 확인하거나 잠시 후 다시 시도해 주세요.")
            st.caption("장소 제공: Kakao Local (한국) · © OpenStreetMap contributors (해외)")
        with st.container(key="weather_card"):
            render_weather(latitude, longitude)
        with st.container(key="exchange_card"):
            render_exchange_rates()

with panel_col:
    with st.container(key="panel"):
        st.markdown("### 이번엔 어디로 떠날까요?")
        with st.form("city_search"):
            city_query = st.text_input("도시 검색", placeholder="도시 이름을 입력하세요", key="city_query")
            city_submitted = st.form_submit_button("도시 찾아보기", use_container_width=True, type="primary")
        st.caption("예: 도쿄, 파리, 런던, 뉴욕, 상파울로 등")
        for row in (CITY_PRESETS[1:4], CITY_PRESETS[4:] + CITY_PRESETS[:1]):
            for col, city in zip(st.columns(3), row):
                col.button(city["name"], key=f"city_{city['country_code']}", on_click=select_city, args=(city,), use_container_width=True)
        if city_submitted:
            try:
                with st.spinner("도시를 찾고 있어요..."):
                    candidates = search_cities(city_query)
                st.session_state.city_candidates = candidates
                if len(candidates) == 1:
                    select_city(candidates[0])
                    st.rerun()
                if not candidates:
                    st.info("도시를 찾지 못했어요. 영문 이름으로도 검색해 보세요.")
            except (requests.RequestException, ValueError, KeyError):
                st.session_state.city_candidates = []
                st.warning("도시 검색에 연결하지 못했습니다. 아래 예시 도시를 선택하거나 다시 시도해 주세요.")
        for candidate in st.session_state.city_candidates:
            st.button(city_label(candidate), key=f"select_{city_key(candidate)}", on_click=select_city, args=(candidate,), use_container_width=True)
        st.divider()
        st.caption("취향에 맞는 장소를 가까운 순서로")
        with st.form("place_search"):
            query = st.text_input("검색어", key="search_term", placeholder="장소 이름이나 키워드를 입력하세요")
            radius = st.select_slider("검색 반경", options=[500, 1000, 2000, 5000, 10000],
                                      key="search_radius", format_func=lambda x: f"{x / 1000:g} km")
            submitted = st.form_submit_button("주변 장소 검색", use_container_width=True, type="primary")
        if submitted:
            with st.spinner("가까운 장소를 찾고 있어요..."):
                run_search(query, radius)
            st.rerun()
        if st.session_state.search_message:
            st.warning(st.session_state.search_message)
        elif selected_city["country_code"] == "KR" and not KAKAO_REST_API_KEY:
            st.info("장소 검색은 .env의 KAKAO_REST_API_KEY 설정 후 사용할 수 있습니다.")
        if selected_city["country_code"] == "KR":
            with st.expander("장소 서비스 연결 상태"):
                render_api_status()
        else:
            st.caption("해외 지도·장소: OpenStreetMap · 카테고리 검색 지원")
        places = st.session_state.places
        st.markdown(f'<div id="search-results" class="card-heading"><strong>검색 결과</strong><span class="pill">{len(places)}곳</span></div>', unsafe_allow_html=True)
        context = st.session_state.search_context
        if context:
            st.caption(f"{context[2]} · 반경 {context[3]:,} m · 가까운 순")
        if places:
            cards = []
            for index, place in enumerate(places, 1):
                name = escape(place.get("place_name", "장소"))
                address = escape(place.get("road_address_name") or place.get("address_name") or "주소 정보 없음")
                category = escape(place.get("category_name", "").split(" > ")[-1])
                phone = escape(place.get("phone", ""))
                distance = place.get("distance", "")
                distance_text = f"{int(distance):,} m" if str(distance).isdigit() else ""
                url = place.get("place_url", "")
                if not url.startswith(("https://", "http://")):
                    url = "https://map.kakao.com"
                cards.append(place_card(place, index))
            st.markdown('<div>' + ''.join(cards) + '</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty">여행의 첫 장소를 찾아보세요<br><small>카페·맛집 카테고리를 누르거나<br>궁금한 장소를 검색해 보세요.</small></div>', unsafe_allow_html=True)

with map_slot.container():
    with st.container(key="map_card"):
        location_label = escape(city_label(selected_city))
        st.markdown(f'<div id="map-view" class="card-heading"><strong>여행지 한눈에 보기</strong><span class="pill">◎ {location_label}</span></div>', unsafe_allow_html=True)
        st.caption("선택한 도시 중심과 주변 장소를 함께 확인하세요.")
        st_folium(make_map(latitude, longitude, st.session_state.places), height=600,
                  use_container_width=True, returned_objects=[])
        st.caption("빨간 마커 · 도시 중심　 /　 파란 마커 · 검색한 장소")
