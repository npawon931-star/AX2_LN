"""Global city and place providers. All coordinates use WGS84."""
from __future__ import annotations

import math
from datetime import datetime
from html import escape
from zoneinfo import ZoneInfo
from urllib.parse import urlsplit

import requests
import streamlit as st
from babel.numbers import get_territory_currencies, get_currency_name

# Instant, offline-capable starting points; other cities use live geocoding.
CITY_PRESETS = [
    dict(name="서울", country="대한민국", country_code="KR", latitude=37.5665, longitude=126.978, timezone="Asia/Seoul"),
    dict(name="도쿄", country="일본", country_code="JP", latitude=35.6762, longitude=139.6503, timezone="Asia/Tokyo"),
    dict(name="파리", country="프랑스", country_code="FR", latitude=48.8566, longitude=2.3522, timezone="Europe/Paris"),
    dict(name="런던", country="영국", country_code="GB", latitude=51.5074, longitude=-0.1278, timezone="Europe/London"),
    dict(name="뉴욕", country="미국", country_code="US", latitude=40.7128, longitude=-74.006, timezone="America/New_York"),
    dict(name="상파울로", country="브라질", country_code="BR", latitude=-23.5505, longitude=-46.6333, timezone="America/Sao_Paulo"),
]
ALIASES = dict(zip(["seoul", "tokyo", "paris", "london", "new york", "sao paulo", "são paulo"],
                   [0, 1, 2, 3, 4, 5, 5]))
CATEGORIES = {"카페": ("amenity", "cafe"), "맛집": ("amenity", "restaurant"),
              "편의점": ("shop", "convenience"), "약국": ("amenity", "pharmacy")}
HEADERS = {"User-Agent": "NearbyCityExplorer/1.0 (Streamlit travel dashboard)"}


def city_key(city):
    return f"{city['country_code']}:{city['latitude']:.5f}:{city['longitude']:.5f}"


def city_label(city):
    return " · ".join(dict.fromkeys(x for x in [city["name"], city.get("admin1"), city.get("country")] if x))


def local_time(city):
    try:
        return datetime.now(ZoneInfo(city["timezone"])).strftime("%m.%d ? %H:%M")
    except (KeyError, ValueError):
        return "?? ?? ?? ?"


def currency_codes(city):
    return get_territory_currencies(city["country_code"])


def currency_name(code):
    return get_currency_name(code, locale="ko")


def safe_url(url):
    try:
        parts = urlsplit(str(url))
        return str(url) if parts.scheme in ("https", "http") and parts.netloc else "#"
    except ValueError:
        return "#"


@st.cache_data(ttl=86400, show_spinner=False)
def search_cities(query):
    query = query.strip()
    if len(query) < 2:
        return []
    presets = [dict(c) for c in CITY_PRESETS if c["name"] == query]
    if query.casefold() in ALIASES:
        presets = [dict(CITY_PRESETS[ALIASES[query.casefold()]])]
    if presets:
        return presets
    response = requests.get("https://geocoding-api.open-meteo.com/v1/search",
                            params={"name": query, "count": 15, "language": "ko"},
                            headers=HEADERS, timeout=10)
    response.raise_for_status()
    results = presets[:]
    for city in response.json().get("results", []):
        if not city.get("country_code") or not city.get("feature_code", "").startswith("PPL"):
            continue
        lat, lon = float(city["latitude"]), float(city["longitude"])
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            continue
        if any(c["country_code"] == city["country_code"] and distance_m(lat, lon, c["latitude"], c["longitude"]) < 15000 for c in results):
            continue
        results.append(city)
    return results


def distance_m(lat, lon, other_lat, other_lon):
    a, b = math.radians(lat), math.radians(other_lat)
    dlat, dlon = b - a, math.radians(other_lon - lon)
    h = math.sin(dlat / 2) ** 2 + math.cos(a) * math.cos(b) * math.sin(dlon / 2) ** 2
    return round(6371000 * 2 * math.asin(min(1, math.sqrt(h))))


@st.cache_data(ttl=1800, show_spinner=False)
def open_places(lat, lon, radius, category):
    tag, value = CATEGORIES[category]
    query = f'[out:json][timeout:20];nwr["{tag}"="{value}"]["name"](around:{int(radius)},{float(lat)},{float(lon)});out center tags;'
    response = requests.post("https://overpass-api.de/api/interpreter", data={"data": query},
                             headers=HEADERS, timeout=28)
    response.raise_for_status()
    payload = response.json()
    if payload.get("remark"):
        raise ValueError("장소 서버가 혼잡합니다. 잠시 후 다시 시도해 주세요.")
    places = []
    for item in payload.get("elements", []):
        tags = item.get("tags", {})
        center = item.get("center", item)
        if "lat" not in center or "lon" not in center:
            continue
        distance = distance_m(lat, lon, center["lat"], center["lon"])
        if distance > radius:
            continue
        address = " ".join(tags.get(k, "") for k in ["addr:city", "addr:street", "addr:housenumber"]).strip()
        places.append(dict(id=f"osm-{item['type']}-{item['id']}", x=center["lon"], y=center["lat"],
                           place_name=tags.get("name:ko") or tags.get("name", "이름 없는 장소"),
                           address_name=address or "주소 정보 없음 · 지도에서 위치 확인",
                           category_name=category, distance=str(distance),
                           phone=tags.get("phone") or tags.get("contact:phone", ""),
                           opening_hours=tags.get("opening_hours", ""),
                           place_url=f"https://www.openstreetmap.org/{item['type']}/{item['id']}"))
    places.sort(key=lambda p: (int(p["distance"]), p["place_name"]))
    return places[:15]


def place_card(place, index=1):
    name = escape(place.get("place_name", "장소"))
    address = escape(place.get("road_address_name") or place.get("address_name") or "주소 정보 없음")
    category = escape(place.get("category_name", "").split(" > ")[-1])
    distance = str(place.get("distance", ""))
    distance = f"{int(distance):,} m" if distance.isdigit() else ""
    phone = escape(place.get("phone", ""))
    hours = escape(place.get("opening_hours", ""))
    url = escape(safe_url(place.get("place_url", "")), quote=True)
    return (f'<article class="result"><div class="card-heading"><strong>{index:02d} · {name}</strong>'
            f'<span class="pill">{distance}</span></div><p>{category}<br>{address}'
            + (f"<br>{phone}" if phone else "") + (f"<br>등록된 영업시간: {hours}" if hours else "")
            + f'</p><a href="{url}" target="_blank" rel="noopener noreferrer">지도에서 자세히 보기 ↗</a></article>')


@st.cache_data(ttl=600, show_spinner=False)
def open_weather(lat, lon):
    response = requests.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude": lat, "longitude": lon, "timezone": "auto", "wind_speed_unit": "ms",
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "forecast_days": 7}, timeout=10)
    response.raise_for_status()
    return response.json()


def wmo_condition(code):
    if code == 0:
        return "??", "??", 800
    if code in (1, 2, 3):
        return "??", "??", 803
    if code in (45, 48):
        return "???", "??", 741
    if code in (71, 73, 75, 77, 85, 86):
        return "??", "?", 601
    if code in (95, 96, 99):
        return "??", "??", 211
    return "???", "?", 501
