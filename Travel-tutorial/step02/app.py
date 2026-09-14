import streamlit as st

st.set_page_config(page_title="세계 여행 포털", page_icon="🌏")

# 사이드바
menu = st.sidebar.radio("메뉴", ["홈", "미국", "중국", "일본", "러시아"])

if menu == "홈":
    st.title("🇰🇷 대한민국")
    st.write("대한민국은 동아시아에 위치한 나라로, 한반도의 남쪽에 자리잡고 있습니다.")
    st.write("사이드바에서 나라를 선택하여 각 나라의 소개와 공식 관광 사이트를 확인해 보세요.")
elif menu == "미국":
    st.title("🇺🇸 미국")
    st.write("미국은 북아메리카에 위치한 나라로, 수도는 워싱턴 D.C.입니다.")
    st.write("뉴욕의 자유의 여신상, 그랜드 캐니언 등 다양한 도시 명소와 자연경관을 만날 수 있습니다.")
    st.link_button("미국 공식 관광 사이트 방문", "https://www.visittheusa.com/")
elif menu == "중국":
    st.title("🇨🇳 중국")
    st.write("중국은 동아시아에 위치한 나라로, 수도는 베이징입니다.")
    st.write("만리장성과 자금성 등 오랜 역사를 간직한 문화유산이 있습니다.")
    st.link_button("중국 공식 관광 사이트 방문", "https://www.travelchina.org.cn/en")
elif menu == "일본":
    st.title("🇯🇵 일본")
    st.write("일본은 동아시아에 위치한 섬나라로, 수도는 도쿄입니다.")
    st.write("후지산과 교토의 사찰 등 자연과 전통문화를 함께 즐길 수 있습니다.")
    st.link_button("일본 공식 관광 사이트 방문", "https://www.japan.travel/en/")
elif menu == "러시아":
    st.title("🇷🇺 러시아")
    st.write("러시아는 유럽 동부와 아시아 북부에 걸쳐 있는 나라로, 수도는 모스크바입니다.")
    st.write("모스크바의 붉은 광장과 바이칼 호수 등 다양한 명소가 있습니다.")
    st.link_button("러시아 공식 관광 사이트 방문", "https://discoverrussia.travel/")
