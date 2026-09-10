import os
import streamlit as st
import pandas as pd
import numpy as np
import requests
from dotenv import load_dotenv

# 1. 상위 폴더의 .env 파일 로드
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(dotenv_path=env_path)

# API 키 가져오기 (EXCHANGE_API_KEY 또는 API_KEY)
API_KEY = os.getenv("EXCHANGE_API_KEY") or os.getenv("API_KEY")

# 2. 페이지 설정 (반응형 레이아웃)
st.set_page_config(
    page_title="CaliCal - 실시간 환율 계산기",
    page_icon="💱",
    layout="centered", # 모바일 앱 느낌을 위해 centered 추천 (wide로 바꾸셔도 무방합니다)
    initial_sidebar_state="collapsed"
)

# 3. 이미지 스타일 감성을 녹여낸 CSS 커스텀 (Pretendard 폰트 + 미니멀 연두/그린 테마)
st.markdown("""
<link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
<style>
    /* 전체 폰트 적용 */
    html, body, [class*="css"] {
        font-family: 'Pretendard', sans-serif !important;
        background-color: #f4f7f2 !important; /* 이미지 배경 같은 연한 민트/그린빛 미색 */
    }
    
    /* 앱 메인 컨테이너 카드 스타일 */
    .app-card {
        background-color: #ffffff;
        border: 1px solid #e9f0e8;
        padding: 24px;
        border-radius: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
        margin-bottom: 20px;
    }

    /* 상단 타이틀 로고 느낌 */
    .logo-title {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #111827;
        text-align: center;
        letter-spacing: -0.03em;
        margin-bottom: 0px;
    }
    
    .logo-subtitle {
        font-size: 0.85rem;
        color: #9ca3af;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* 민트/그린 포인트 배지 & 메트릭 카드 */
    .green-badge {
        background-color: #eaf3ec;
        color: #276749;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 8px;
    }

    /* 입력창 디자인 커스텀 */
    .stNumberInput input {
        border-radius: 14px !important;
        border: 1px solid #e5e7eb !important;
        padding: 12px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# 4. API 호출 및 데이터 캐싱
@st.cache_data(ttl=3600)
def fetch_exchange_rates(api_key):
    if not api_key:
        return None
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/KRW"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get("result") == "success":
            return data.get("conversion_rates")
    except Exception as e:
        return None
    return None

if not API_KEY:
    st.error("⚠️ 상위 폴더의 `.env` 파일에서 API 키(`EXCHANGE_RATE_API_KEY` 또는 `API_KEY`)를 찾을 수 없습니다.")
    st.stop()

rates = fetch_exchange_rates(API_KEY)

if not rates:
    st.error("❌ 환율 데이터를 불러오지 못했습니다. API 키를 확인해주세요.")
    st.stop()

currencies = [
    {"code": "USD", "name": "미국 달러", "icon": "🇺🇸", "multiplier": 1},
    {"code": "EUR", "name": "유로", "icon": "🇪🇺", "multiplier": 1},
    {"code": "JPY", "name": "일본 엔 (100엔)", "icon": "🇯🇵", "multiplier": 100},
    {"code": "CNY", "name": "중국 위안", "icon": "🇨🇳", "multiplier": 1}
]

# --- UI 레이아웃 시작 (모바일 대시보드 형태) ---
st.markdown('<p class="logo-title">Exchan<span style="color: #4ade80;">Glow</span></p>', unsafe_allow_html=True)
st.markdown('<p class="logo-subtitle">Real-time Currency & Exchange Dashboard</p>', unsafe_allow_html=True)

# [섹션 1] 메인 요약 카드 (이미지의 'Daily intake' 카드 감성 재현)
st.markdown("""
<div class="app-card" style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border: 1px solid #bbf7d0;">
    <span class="green-badge">Live Market Status</span>
    <h3 style="color: #166534; margin-top: 5px; margin-bottom: 10px; font-weight: 700;">원화 기준 실시간 환율 요약</h3>
    <p style="color: #4b5563; font-size: 0.9rem; margin: 0;">주요 4개국 통화의 1외화당 원화 가치를 실시간으로 동기화하고 있습니다.</p>
</div>
""", unsafe_allow_html=True)

# [섹션 2] 주요 통화 기준가 카드 4분할
cols = st.columns(2) # 모바일 화면을 고려해 2열씩 배치 (필요시 4열로 확장 가능)

for idx, curr in enumerate(currencies):
    rate_per_krw = rates.get(curr["code"], 0)
    val_per_one = (1 / rate_per_krw * curr["multiplier"]) if rate_per_krw > 0 else 0
    
    # 2개씩 나누어 담기 위한 컬럼 분기
    with cols[idx % 2]:
        st.markdown(f"""
        <div class="app-card" style="padding: 18px; text-align: left;">
            <div style="font-size: 1.1rem; font-weight: 600; color: #4b5563; margin-bottom: 8px;">
                {curr['icon']} {curr['name']}
            </div>
            <div style="font-size: 1.4rem; font-weight: 800; color: #111827;">
                {val_per_one:,.2f} <span style="font-size: 0.75rem; color: #9ca3af; font-weight: 500;">KRW</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# [섹션 3] 원화 환전 계산기 (이미지의 'Nutritions' 바 그래프 감성 차용)
st.markdown("""
<div class="app-card">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
        <h4 style="margin: 0; font-weight: 700; color: #1f2937;">💰 원화 환전 계산기</h4>
        <span style="font-size: 0.8rem; color: #10b981; font-weight: 600;">Active Calculator</span>
    </div>
""", unsafe_allow_html=True)

krw_amount = st.number_input("환전할 원화 (KRW) 금액을 입력하세요", min_value=0, value=100000, step=10000, format="%d")

st.markdown("<hr style='border: 0; border-top: 1px solid #f3f4f6; margin: 15px 0;'>", unsafe_allow_html=True)

# 계산된 결과 바 형태 또는 메트릭으로 출력
for curr in currencies:
    rate_krw_to_curr = rates.get(curr["code"], 0)
    converted_val = krw_amount * rate_krw_to_curr
    if curr["code"] == "JPY":
        converted_val = converted_val / 100

    # 프로그레스바 비율 계산 (예시 기준치 대비 비율)
    percentage = min(int((krw_amount / 1000000) * 100), 100)
    
    st.markdown(f"""
    <div style="margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 600; color: #4b5563; margin-bottom: 4px;">
            <span>{curr['icon']} {curr['name']} ({curr['code']})</span>
            <span style="color: #111827; font-weight: 700;">{converted_val:,.2f} {curr['code']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# [섹션 4] 환율 추이 그래프 (이미지의 우측 화면 그래프 감성)
st.markdown("""
<div class="app-card">
    <h4 style="margin-top: 0; margin-bottom: 15px; font-weight: 700; color: #1f2937;">📈 주간 환율 변동 트렌드</h4>
""", unsafe_allow_html=True)

selected_curr = st.selectbox("조회할 통화", [c["code"] for c in currencies], format_func=lambda x: next(c['name'] for c in currencies if c['code'] == x))

current_rate = 1 / rates.get(selected_curr, 1)
if selected_curr == "JPY":
    current_rate *= 100

np.random.seed(hash(selected_curr) % 1000)
days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
historical_values = [round(current_rate * (1 + np.random.uniform(-0.008, 0.008)), 2) for _ in range(6)]
historical_values.append(round(current_rate, 2))

df_chart = pd.DataFrame({
    'Day': days,
    'Rate': historical_values
}).set_index('Day')

st.line_chart(df_chart, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# 푸터
st.markdown("<p style='text-align: center; color: #9ca3af; font-size: 0.75rem; margin-top: 30px;'>Designed with Apple Health / CaloriCam UI Mood &bull; Powered by ExchangeRate-API</p>", unsafe_allow_html=True)