import streamlit as st

st.title("🇺🇸 미국")
st.write("미국은 북아메리카에 위치한 나라로, 수도는 워싱턴 D.C.입니다. 활기찬 대도시부터 광활한 국립공원까지 다양한 풍경과 문화를 만날 수 있습니다.")

st.subheader("📍 대표 명소")
st.markdown("""
- **뉴욕 자유의 여신상**: 뉴욕을 대표하는 상징적인 명소입니다.
- **그랜드 캐니언**: 오랜 시간에 걸쳐 만들어진 거대한 협곡입니다.
- **샌프란시스코 금문교**: 샌프란시스코만 입구에 놓인 유명한 현수교입니다.
""")
st.subheader("🍽️ 대표 음식")
st.write("햄버거, 바비큐, 클램 차우더 등 지역마다 특색 있는 음식을 만날 수 있습니다.")
with st.expander("💬 알아두면 좋은 인사말"):
    st.write("Hello (헬로) — 안녕하세요.")
    st.write("Thank you (땡큐) — 감사합니다.")
st.link_button("미국 공식 관광 사이트 방문", "https://www.visittheusa.com/")
