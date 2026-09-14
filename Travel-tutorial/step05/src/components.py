import streamlit as st
import os

def render_sidebar():
    st.sidebar.title("✈️ 국가 여행 가이드")
    st.sidebar.markdown("---")
    choice = st.sidebar.radio(
        "이동할 국가를 선택하세요:",
        ["대한민국 (홈)", "중국", "일본", "미국", "러시아"]
    )
    return choice

def render_country_info(name, info):
    st.title(f"📍 {name}")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("국가 주요 정보")
        st.write(f"**수도:** {info['capital']}")
        st.write(f"**공용어:** {info['language']}")
        st.write(f"**통화:** {info['currency']}")
        st.info(info['description'])
        
        # 여행 사이트 링크 버튼
        st.markdown(f"### 🔗 공식 여행 사이트")
        st.markdown(f"설명에 맞는 여행 정보를 확인하려면 아래 링크를 방문하세요:")
        st.link_button(f"👉 {info['site_name']}로 이동하기", info['travel_site'])

    with col2:
        img_path = os.path.join("assets", "images", info['image_name'])
        if os.path.exists(img_path):
            st.image(img_path, caption=f"{name} 풍경", width="stretch")
        else:
            st.warning(f"⚠️ 이미지를 찾을 수 없습니다: `{img_path}`\n\n해당 경로에 이미지를 넣어주세요.")