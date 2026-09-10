# 날씨 API 실습
# OpenWeatherMap 현재 날씨 API로 특정 도시의 날씨를 가져와 출력한다
# 사전준비 OpenWeatherMap회원 가입 후 API 발급
# pip install request python-dotenv
#.env 파일을 생성하고 이곳에 OPENWEATHER_API_KEY=발급받은_API_키
#.env.example OPENWEATHER_API_KEY=your_key
#.env.example 받아서 .env로 이름바꾸고 자기 API를 채운다

import os
import requests
import streamlit as st
from dotenv import load_dotenv, find_dotenv
import pandas as pd
import altair as alt

# 1. 로컬 환경(.env) 로드 시도 (실패해도 에러 나지 않도록 예외 처리)
try:
    load_dotenv(find_dotenv())
except Exception:
    pass

# 2. 로컬(.env) 또는 Streamlit Cloud(st.secrets)에서 안전하게 API 키 가져오기
API_KEY = os.getenv("OPENWEATHER_API_KEY") or st.secrets.get("OPENWEATHER_API_KEY", "")
EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY") or st.secrets.get("EXCHANGE_API_KEY", "")

# 페이지 설정 (와이드 모드)
st.set_page_config(
    page_title="파스텔 날씨 및 환율 스튜디오",
    page_icon="🌿",
    layout="wide"
)

# 🎨 Pretendard 글꼴 및 프리미엄 파스텔 디자인 시스템 CSS
st.markdown("""
<link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
<style>
    .stApp {
        background-color: #f4f6f9;
        font-family: 'Pretendard Variable', Pretendard, -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
    }
    
    /* 상단 헤더 네비게이션 바 */
    .top-nav {
        background-color: #ffffff;
        border-radius: 24px;
        padding: 24px 36px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        margin-bottom: 24px;
    }

    /* 공통 카드 스타일 */
    .card-lavender {
        background-color: #eae6f3;
        border-radius: 28px;
        padding: 32px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.02);
        margin-bottom: 24px;
        color: #2d3748;
    }

    .card-sage {
        background-color: #e0eae4;
        border-radius: 28px;
        padding: 32px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.02);
        margin-bottom: 24px;
        color: #2d3748;
    }

    .card-peach {
        background-color: #fce8e6;
        border-radius: 28px;
        padding: 32px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.02);
        margin-bottom: 24px;
        color: #2d3748;
    }

    .card-white {
        background-color: #ffffff;
        border-radius: 28px;
        padding: 32px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.03);
        margin-bottom: 24px;
        color: #2d3748;
    }

    /* 반응형 미디어쿼리 */
    @media (max-width: 768px) {
        .top-nav {
            padding: 16px 20px;
            flex-direction: column;
            gap: 12px;
            text-align: center;
        }
        .card-lavender, .card-sage, .card-peach, .card-white {
            padding: 20px;
            border-radius: 20px;
        }
    }
</style>
""", unsafe_allow_html=True)

# 상단 헤더 영역
st.markdown("""
<div class="top-nav">
    <div style="font-weight: 800; font-size: 2.2rem; color: #1a202c; display: flex; align-items: center; gap: 14px; letter-spacing: -0.5px;">
        <span style="font-size: 2.4rem;">🌿</span> 날씨 & 환율 스튜디오
    </div>
    <div style="background-color: #1a202c; color: white; padding: 10px 24px; border-radius: 22px; font-size: 0.9rem; font-weight: 600; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
        도움말
    </div>
</div>
""", unsafe_allow_html=True)

if not API_KEY:
    st.error("⚠️ 상위 폴더의 `.env` 파일에서 `OPENWEATHER_API_KEY`를 확인해주세요!")
else:
    # 🔍 검색 영역
    st.markdown("<h4 style='font-weight: 700; color: #1a202c; margin-bottom: 12px;'>🔍 지역 및 단위 검색</h4>", unsafe_allow_html=True)
    
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        city = st.text_input("도시 영문 이름", value="Seoul", placeholder="예: Seoul, Tokyo, New York", label_visibility="collapsed")
    with col_s2:
        unit_option = st.radio("온도 단위", ["섭씨 (°C)", "화씨 (°F)"], horizontal=True, label_visibility="collapsed")

    units = "metric" if "섭씨" in unit_option else "imperial"
    unit_symbol = "°C" if units == "metric" else "°F"

    # API 호출 함수 (날씨)
    def get_weather_data(city_name):
        curr_url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&units={units}&lang=kr"
        fc_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={API_KEY}&units={units}&lang=kr"
        return requests.get(curr_url), requests.get(fc_url)

    # KRW 기준 환율 API 호출 함수
    def get_exchange_data():
        if not EXCHANGE_API_KEY:
            return None
        url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/KRW"
        res = requests.get(url)
        if res.status_code == 200:
            return res.json()
        return None

    res_curr, res_fc = get_weather_data(city)

    if res_curr.status_code != 200:
        st.error("❌ 도시를 찾을 수 없습니다. 올바른 영문 도시명(예: Seoul,KR)을 입력해주세요.")
    else:
        c_data = res_curr.json()
        city_name = c_data["name"]
        country = c_data["sys"]["country"]
        
        temp = c_data["main"]["temp"]
        feels_like = c_data["main"]["feels_like"]
        humidity = c_data["main"]["humidity"]
        wind_speed = c_data["wind"]["speed"]
        desc = c_data["weather"][0]["description"]
        icon = c_data["weather"][0]["icon"]

        exchange_data = get_exchange_data()

        # 온도별 옷차림 추천 로직
        if temp >= 28:
            outfit = "민소매, 반팔, 반바지, 원피스, 린넨 소재"
        elif temp >= 23:
            outfit = "반팔, 얇은 셔츠, 반바지, 면바지"
        elif temp >= 20:
            outfit = "긴팔 티셔츠, 얇은 가디건, 셔츠, 슬랙스"
        elif temp >= 17:
            outfit = "니트, 가디건, 맨투맨, 청바지, 자켓"
        elif temp >= 12:
            outfit = "자켓, 야상, 얇은 코트, 청바지"
        elif temp >= 6:
            outfit = "트렌치코트, 자켓, 니트, 기모 바지"
        else:
            outfit = "패딩, 두꺼운 코트, 목도리, 기모 안감"

        st.markdown("<br>", unsafe_allow_html=True)

        # 반응형 2단 컬럼
        col1, col2 = st.columns(2, gap="medium")

        with col1:
            # 1. 라벤더 톤 카드 (현재 날씨)
            st.markdown(f"""
            <div class="card-lavender">
                <h3 style="margin-top:0; font-weight:700; color:#2d3748;">실시간 날씨 요약</h3>
                <p style="color: #4a5568; font-size: 0.95rem; margin-bottom: 20px;"><b>{city_name}, {country}</b>의 현재 기상 상태입니다.</p>
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
                    <div>
                        <h1 style="font-size: 3.2rem; margin: 0; font-weight: 800; color:#1a202c;">{temp}{unit_symbol}</h1>
                        <p style="font-weight: 600; color: #5b46f4; margin-top: 8px; font-size: 1.15rem;">{desc}</p>
                    </div>
                    <img src="https://openweathermap.org/img/wn/{icon}@4x.png" width="110">
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 2. 피치 톤 카드 (원화 기준 주요 통화 환율 정보)
            if exchange_data and "conversion_rates" in exchange_data:
                rates = exchange_data["conversion_rates"]
                try:
                    usd_to_krw = 1 / rates.get("USD", 1)
                    eur_to_krw = 1 / rates.get("EUR", 1)
                    jpy_to_krw = (1 / rates.get("JPY", 1)) * 100
                    cny_to_krw = 1 / rates.get("CNY", 1)
                except ZeroDivisionError:
                    usd_to_krw = eur_to_krw = jpy_to_krw = cny_to_krw = 0

                st.markdown(f"""
                <div class="card-peach">
                    <h3 style="margin-top:0; font-weight:700; color:#2d3748;">💱 주요 통화 환율 (원화 기준)</h3>
                    <p style="color: #4a5568; font-size: 0.9rem; margin-bottom: 16px;">한국 원화(KRW) 대비 실시간 주요 외화 시세입니다.</p>
                    <div style="display: flex; gap: 10px; text-align: center; flex-wrap: wrap;">
                        <div style="background: #ffffff; padding: 12px; border-radius: 16px; flex: 1; min-width: 70px; border: 1px solid #f2d3d0;">
                            <span style="color: #718096; font-size: 0.75rem; font-weight: 500;">미국 달러(USD)</span>
                            <p style="margin: 4px 0 0 0; color: #1a202c; font-size: 0.95rem; font-weight: 700;">{usd_to_krw:,.1f}원</p>
                        </div>
                        <div style="background: #ffffff; padding: 12px; border-radius: 16px; flex: 1; min-width: 70px; border: 1px solid #f2d3d0;">
                            <span style="color: #718096; font-size: 0.75rem; font-weight: 500;">유럽 유로(EUR)</span>
                            <p style="margin: 4px 0 0 0; color: #1a202c; font-size: 0.95rem; font-weight: 700;">{eur_to_krw:,.1f}원</p>
                        </div>
                        <div style="background: #ffffff; padding: 12px; border-radius: 16px; flex: 1; min-width: 70px; border: 1px solid #f2d3d0;">
                            <span style="color: #718096; font-size: 0.75rem; font-weight: 500;">일본 엔(100엔)</span>
                            <p style="margin: 4px 0 0 0; color: #1a202c; font-size: 0.95rem; font-weight: 700;">{jpy_to_krw:,.1f}원</p>
                        </div>
                        <div style="background: #ffffff; padding: 12px; border-radius: 16px; flex: 1; min-width: 70px; border: 1px solid #f2d3d0;">
                            <span style="color: #718096; font-size: 0.75rem; font-weight: 500;">중국 위안(CNY)</span>
                            <p style="margin: 4px 0 0 0; color: #1a202c; font-size: 0.95rem; font-weight: 700;">{cny_to_krw:,.1f}원</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="card-peach">
                    <h3 style="margin-top:0; font-weight:700; color:#2d3748;">💱 실시간 환율 정보</h3>
                    <p style="color: #e53e3e; font-size: 0.9rem;">⚠️ `.env` 파일에 올바른 `EXCHANGE_API_KEY`를 설정해주세요.</p>
                </div>
                """, unsafe_allow_html=True)

            # 3. 세이지 그린 톤 카드 (스타일 가이드)
            st.markdown(f"""
            <div class="card-sage">
                <h3 style="margin-top:0; font-weight:700; color:#2d3748;">👗 오늘의 맞춤 스타일링 가이드</h3>
                <p style="color: #2d3748; font-size: 0.95rem; margin-top: 10px; line-height: 1.6;">
                    현재 기온 <b>{temp}{unit_symbol}</b> (체감 {feels_like}{unit_symbol})에 어울리는 추천 착장입니다:<br>
                    <span style="color: #2c4a3e; font-weight: 700;">👉 {outfit}</span>
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            # 4. 화이트 카드 (세부 기상 지표)
            st.markdown(f"""
            <div class="card-white">
                <h3 style="margin-top:0; font-weight:700; color:#2d3748;">상세 대기 지표</h3>
                <p style="color: #718096; font-size: 0.95rem;">주요 환경 매개변수 정보입니다.</p>
                <div style="display: flex; gap: 16px; margin-top: 24px; flex-wrap: wrap;">
                    <div style="background: #f8fafc; padding: 20px; border-radius: 20px; flex: 1; min-width: 90px; text-align: center; border: 1px solid #edf2f7;">
                        <span style="color: #718096; font-size: 0.85rem; font-weight: 500;">체감 온도</span>
                        <h3 style="margin: 8px 0 0 0; color: #1a202c; font-size: 1.25rem; font-weight: 700;">{feels_like}{unit_symbol}</h3>
                    </div>
                    <div style="background: #f8fafc; padding: 20px; border-radius: 20px; flex: 1; min-width: 90px; text-align: center; border: 1px solid #edf2f7;">
                        <span style="color: #718096; font-size: 0.85rem; font-weight: 500;">습도</span>
                        <h3 style="margin: 8px 0 0 0; color: #1a202c; font-size: 1.25rem; font-weight: 700;">{humidity}%</h3>
                    </div>
                    <div style="background: #f8fafc; padding: 20px; border-radius: 20px; flex: 1; min-width: 90px; text-align: center; border: 1px solid #edf2f7;">
                        <span style="color: #718096; font-size: 0.85rem; font-weight: 500;">풍속</span>
                        <h3 style="margin: 8px 0 0 0; color: #1a202c; font-size: 1.25rem; font-weight: 700;">{wind_speed} m/s</h3>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 5. 화이트 카드 (Altair 그라데이션 곡선 트렌드 그래프)
            if res_fc.status_code == 200:
                fc_list = res_fc.json()["list"]
                times, temps = [], []
                for item in fc_list[:10]:
                    times.append(item["dt_txt"][11:16])
                    temps.append(item["main"]["temp"])
                
                df_fc = pd.DataFrame({"시간": times, "온도": temps})
                
                st.markdown(f"""
                <div class="card-white" style="margin-bottom: 0;">
                    <h3 style="margin-top:0; font-weight:700; color:#2d3748;">시간대별 온도 트렌드</h3>
                    <p style="color: #718096; font-size: 0.95rem; margin-bottom: 15px;">향후 시간별 기온 변화 추이입니다.</p>
                </div>
                """, unsafe_allow_html=True)

                chart = alt.Chart(df_fc).mark_area(
                    line={"color": "#5b46f4", "strokeWidth": 3},
                    color=alt.Gradient(
                        gradient="linear",
                        stops=[
                            alt.GradientStop(color="rgba(91, 70, 244, 0.4)", offset=0),
                            alt.GradientStop(color="rgba(91, 70, 244, 0.0)", offset=1)
                        ],
                        x1=0, x2=0, y1=0, y2=1
                    ),
                    interpolate="monotone"
                ).encode(
                    x=alt.X("시간:O", title=None, axis=alt.Axis(labelAngle=0, labelColor="#4a5568", labelFont="Pretendard")),
                    y=alt.Y("온도:Q", title=None, scale=alt.Scale(zero=False), axis=alt.Axis(labelColor="#4a5568", labelFont="Pretendard")),
                    tooltip=["시간", "온도"]
                ).properties(
                    height=205
                ).configure_view(
                    strokeWidth=0
                ).configure_axis(
                    domain=False,
                    ticks=False,
                    gridColor="#edf2f7"
                )

                st.altair_chart(chart, use_container_width=True)