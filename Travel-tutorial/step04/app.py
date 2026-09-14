import streamlit as st


st.set_page_config(page_title="세계 여행 포털", page_icon="🌏", layout="wide")

home_page = st.Page("view/home.py", title= "홈", icon="🏠", default=True)
usa_page = st.Page("view/USA.py", title= "미국", icon="🇺🇸")
china_page = st.Page("view/china.py", title="중국", icon="🇨🇳")
japan_page = st.Page("view/japan.py", title="일본", icon="🇯🇵")
russia_page = st.Page("view/russia.py", title="러시아", icon="🇷🇺")
pg = st.navigation([home_page, usa_page, china_page, japan_page, russia_page ])
pg.run()
