import streamlit as st


st.set_page_config(page_title="세계 여행 포털", page_icon="🌏")

home_page = st.Page("view/home.py", title= "홈", icon="🏠", default=True)
usa = st.Page("view/USA.py", title= "미국", icon="🇺🇸")
china = st.Page("view/china.py", title="중국", icon="🇨🇳")
japan = st.Page("view/japan.py", title="일본", icon="🇯🇵")
russia = st.Page("view/russia.py", title="러시아", icon="🇷🇺")

# 네비게이션 메뉴기동(사이바 메뉴가 자동으로 생김)

pg = st.navigation([home_page, usa, china, japan, russia])
pg.run()
