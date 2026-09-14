import streamlit as st
from src.components import render_sidebar, render_country_info
from src.data import COUNTRY_DATA

# 페이지 기본 설정
st.set_page_config(
    page_title="국가별 여행 정보 서비스",
    page_icon="✈️",
    layout="wide"
)

def main():
    # 사이드바 렌더링 및 선택된 국가 가져오기
    selected_country = render_sidebar()
    
    # 선택된 국가의 데이터 가져오기
    country_info = COUNTRY_DATA.get(selected_country)
    
    if country_info:
        render_country_info(selected_country, country_info)

if __name__ == "__main__":
    main()