import os
import streamlit as st
import pandas as pd
import numpy as np
import requests
from dotenv import load_dotenv

# 1. 상위 폴더의 .env 파일 로드 (ExchangeRate & OpenWeather 공용)
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(dotenv_path=env_path)

EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY") or os.getenv("API_KEY")
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# 2. 페이지 설정 (모바일 대시보드 무드)
st.set_page_config(
    page_title="Tripy - 스마트 맞춤 여행 플래너",
    page_icon="✈️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 3. Pretendard 폰트 및 모바일 감성 스타일링
st.markdown("""
<link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
<style>
    html, body, [class*="css"] {
        font-family: 'Pretendard', sans-serif !important;
        background-color: #f8fafc !important;
    }
    .app-card {
        background-color: #ffffff;
        border: 1px solid #f1f5f9;
        padding: 22px;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
        margin-bottom: 16px;
    }
    .logo-title {
        font-size: 2rem !important;
        font-weight: 800 !important;
        color: #0f172a;
        text-align: center;
        letter-spacing: -0.03em;
        margin-bottom: 0px;
    }
    .logo-subtitle {
        font-size: 0.85rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .badge {
        background-color: #eff6ff;
        color: #2563eb;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 6px;
    }
    .stNumberInput input, .stSelectbox select {
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
    }
</style>
""", unsafe_allow_html=True)

# 4. 데이터 캐싱 및 API 연동 함수
@st.cache_data(ttl=3600)
def fetch_exchange_rates(api_key):
    if not api_key:
        return None
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/KRW"
    try:
        res = requests.get(url)
        data = res.json()
        if data.get("result") == "success":
            return data.get("conversion_rates")
    except:
        return None
    return None

@st.cache_data(ttl=1800)
def fetch_weather(city, api_key):
    if not api_key:
        return None
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=kr"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            return res.json()
    except:
        return None
    return None

# 도시 데이터 매핑
destination_data = {
    "🇺🇸 미국": {"city": "New York", "city_kr": "뉴욕", "currency": "USD", "name": "미국 달러", "multiplier": 1},
    "🇯🇵 일본": {"city": "Tokyo", "city_kr": "도쿄", "currency": "JPY", "name": "일본 엔", "multiplier": 100},
    "🇪🇺 프랑스": {"city": "Paris", "city_kr": "파리", "currency": "EUR", "name": "유로", "multiplier": 1},
    "🇨🇳 중국": {"city": "Beijing", "city_kr": "베이징", "currency": "CNY", "name": "중국 위안", "multiplier": 1},
    "🇬🇧 영국": {"city": "London", "city_kr": "런던", "currency": "GBP", "name": "영국 파운드", "multiplier": 1},
    "🇻🇳 베트남": {"city": "Hanoi", "city_kr": "하노이", "currency": "VND", "name": "베트남 동", "multiplier": 1}
}

travel_tips_db = {
    "🇺🇸 미국": {
        "spots": ["Central Park (센트럴 파크)", "Times Square (타임스 스퀘어)", "The Met (메트로폴리탄 미술관)"],
        "etiquette": "팁 문화가 보편화되어 있습니다. 식당에서는 보통 15~20%의 팁을 지불하는 것이 매너입니다."
    },
    "🇯🇵 일본": {
        "spots": ["Senso-ji (센소지 사원)", "Shibuya Crossing (시부야 스크램블)", "Tokyo Skytree (도쿄 스카이트리)"],
        "etiquette": "대중교통이나 공공장소에서 통화하는 것은 실례가 될 수 있습니다. 에스컬레이터는 한쪽으로 서기를 지켜주세요."
    },
    "🇪🇺 프랑스": {
        "spots": ["Eiffel Tower (에펠탑)", "Louvre Museum (루브르 박물관)", "Montmartre (몽마르트르 언덕)"],
        "etiquette": "가게에 들어갈 때 '봉주르(Bonjour)'라고 먼저 인사하는 것이 현지 예절입니다."
    },
    "🇨🇳 중국": {
        "spots": ["Forbidden City (자금성)", "Great Wall (만리장성)", "The Bund (와이탄)"],
        "etiquette": "차(Tea) 문화를 존중하며, 잔이 비면 상대방이 채워주므로 가볍게 손가락을 톡톡 쳐서 감사를 표현합니다."
    },
    "🇬🇧 영국": {
        "spots": ["Big Ben (빅벤)", "British Museum (대영박물관)", "Tower Bridge (타워브리지)"],
        "etiquette": "줄 서기(Queuing) 질서가 매우 엄격합니다. 새치기는 절대 금물입니다."
    },
    "🇻🇳 베트남": {
        "spots": ["Hoan Kiem Lake (호안끼엠 호수)", "Old Quarter (하노이 구시가지)", "Temple of Literature (문묘)"],
        "etiquette": "사원 등 종교 시설 방문 시 민소매나 짧은 바지 등 노출이 심한 복장은 피해야 합니다."
    }
}

# --- 앱 UI 시작 ---
st.markdown('<p class="logo-title">Trave<span style="color: #2563eb;">ly</span></p>', unsafe_allow_html=True)
st.markdown('<p class="logo-subtitle">Smart Weather, Currency & Trip Assistant</p>', unsafe_allow_html=True)

st.markdown('<div class="app-card">', unsafe_allow_html=True)
selected_country = st.selectbox("✈️ 여행할 국가를 선택하세요", list(destination_data.keys()))
dest_info = destination_data[selected_country]
st.markdown('</div>', unsafe_allow_html=True)

# API 데이터 가져오기
exchange_rates = fetch_exchange_rates(EXCHANGE_API_KEY)
weather_data = fetch_weather(dest_info["city"], WEATHER_API_KEY)

# 실시간 날씨 및 스타일링 가이드 섹션
st.markdown(f"### 🌤️ {selected_country} ({dest_info['city_kr']}) 실시간 날씨 & 스타일링")

if weather_data:
    temp = weather_data["main"]["temp"]
    feels_like = weather_data["main"]["feels_like"]
    humidity = weather_data["main"]["humidity"]
    description = weather_data["weather"][0]["description"]
    wind_speed = weather_data["wind"]["speed"]
    
    if temp < 10:
        style_tip = "날씨가 쌀쌀합니다! 패딩, 코트, 목도리 등 따뜻한 겨울 외투를 꼭 챙기세요."
    elif 10 <= temp < 20:
        style_tip = "선선한 날씨입니다. 가디건, 자켓, 트렌치코트 레이어드룩을 추천해요."
    else:
        style_tip = "따뜻하거나 더운 날씨입니다. 통기성이 좋은 가벼운 옷차림과 자외선 차단제를 준비하세요."

    st.markdown(f"""
    <div class="app-card" style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border: 1px solid #bfdbfe;">
        <span class="badge">Live Weather</span>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
            <div>
                <h2 style="margin: 0; font-size: 2.2rem; color: #1e3a8a; font-weight: 800;">{temp:.1f}°C</h2>
                <p style="margin: 4px 0 0 0; color: #475569; font-weight: 600; text-transform: capitalize;">상태: {description} (체감 {feels_like:.1f}°C)</p>
            </div>
            <div style="text-align: right; color: #334155; font-size: 0.9rem;">
                <p style="margin: 2px 0;">💧 습도: <b>{humidity}%</b></p>
                <p style="margin: 2px 0;">💨 바람: <b>{wind_speed} m/s</b></p>
            </div>
        </div>
        <hr style="border: 0; border-top: 1px solid #cbd5e1; margin: 15px 0;">
        <p style="margin: 0; color: #1e293b; font-size: 0.9rem;">👗 <b>오늘의 맞춤 스타일링 가이드:</b> {style_tip}</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("⚠️ OpenWeather API 키를 확인해주세요. 날씨 정보를 불러오지 못했습니다.")

# 환율 정보 및 계산기 섹션
st.markdown("### 💱 실시간 환율 & 환전 계산기")
if exchange_rates:
    rate_krw_to_target = exchange_rates.get(dest_info["currency"], 0)
    val_per_one = (1 / rate_krw_to_target * dest_info["multiplier"]) if rate_krw_to_target > 0 else 0
    
    st.markdown(f"""
    <div class="app-card">
        <span style="font-size: 0.85rem; color: #64748b; font-weight: 600;">기준 환율 (1 {dest_info['currency']} 당)</span>
        <div style="font-size: 1.5rem; font-weight: 800; color: #0f172a; margin-top: 4px;">
            {val_per_one:,.2f} <span style="font-size: 0.8rem; color: #64748b; font-weight: 500;">KRW</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        krw_in = st.number_input("원화 (KRW) 금액 입력", min_value=0, value=100000, step=10000, format="%d")
    with col2:
        converted = krw_in * rate_krw_to_target
        st.metric(label=f"환전 예상 금액 ({dest_info['currency']})", value=f"{converted:,.2f} {dest_info['currency']}")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.warning("⚠️ 환율 API 키를 확인해주세요.")

# 여행지 추천 및 에티켓 섹션
st.markdown("### 🗺️ 추천 핫플레이스 & 현지 여행 에티켓")
current_tips = travel_tips_db[selected_country]

col_a, col_b = st.columns(2)
with col_a:
    st.markdown(f"""
    <div class="app-card" style="height: 100%;">
        <h4 style="margin-top: 0; color: #1e3a8a; font-weight: 700;">🌟 추천 여행지 TOP 3</h4>
        <ul style="padding-left: 20px; color: #334155; line-height: 1.8; margin-bottom: 0;">
            <li><b>{current_tips['spots'][0]}</b></li>
            <li><b>{current_tips['spots'][1]}</b></li>
            <li><b>{current_tips['spots'][2]}</b></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown(f"""
    <div class="app-card" style="height: 100%;">
        <h4 style="margin-top: 0; color: #b45309; font-weight: 700;">⚠️ 필수 문화 & 에티켓</h4>
        <p style="color: #334155; font-size: 0.9rem; line-height: 1.6; margin-bottom: 0;">
            {current_tips['etiquette']}
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.75rem;'>TraveLy App &bull; Powered by OpenWeatherMap & ExchangeRate-API</p>", unsafe_allow_html=True)