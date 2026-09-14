# 실행: python -m streamlit run day06-1.py
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from dotenv import load_dotenv
import streamlit as st


load_dotenv(Path(__file__).with_name(".env"))


def search_places(query, api_key):
    """카카오 로컬 REST API에서 최대 15개의 장소를 가져옵니다."""
    params = urlencode({"query": query, "size": 15})
    request = Request(
        f"https://dapi.kakao.com/v2/local/search/keyword.json?{params}",
        headers={"Authorization": f"KakaoAK {api_key}"},
    )
    try:
        with urlopen(request, timeout=10) as response:
            payload = json.load(response)
    except HTTPError as exc:
        messages = {
            400: "검색 요청을 처리할 수 없습니다. 검색어를 확인해 주세요.",
            401: "인증에 실패했습니다. .env의 REST API 키를 확인해 주세요.",
            403: "API 사용 권한이 없습니다. 카카오 개발자 콘솔에서 키와 서비스 권한을 확인해 주세요.",
            429: "API 호출 한도를 초과했습니다. 잠시 후 다시 시도해 주세요.",
        }
        raise RuntimeError(messages.get(exc.code, f"카카오 API 오류가 발생했습니다. (HTTP {exc.code})")) from None
    except (URLError, TimeoutError, OSError):
        raise RuntimeError("카카오 API에 연결하지 못했습니다. 네트워크를 확인하고 다시 시도해 주세요.") from None
    except (ValueError, UnicodeError):
        raise RuntimeError("카카오 API 응답을 읽지 못했습니다. 잠시 후 다시 시도해 주세요.") from None

    try:
        return [
            {
                "name": place["place_name"],
                "lat": float(place["y"]),
                "lng": float(place["x"]),
                "address": place.get("road_address_name") or place.get("address_name", ""),
                "phone": place.get("phone", ""),
                "url": place["place_url"],
            }
            for place in payload["documents"]
        ]
    except (KeyError, TypeError, ValueError):
        raise RuntimeError("카카오 API 응답 형식이 올바르지 않습니다.") from None


def main():
    st.set_page_config(page_title="카카오 장소 검색 지도", page_icon="🗺️", layout="wide")
    st.title("카카오 장소 검색 지도")
    st.caption("카카오 REST API로 검색한 장소를 Streamlit 지도에 표시합니다.")

    api_key = os.getenv("KAKAO_REST_API_KEY", "").strip()
    if not api_key or api_key == "your_kakao_rest_api_key":
        st.warning(".env에 KAKAO_REST_API_KEY를 설정한 후 앱을 재시작해 주세요.")
        return

    with st.form("place_search"):
        query = st.text_input("장소 검색", value="경복궁", placeholder="예: 강남역 카페")
        submitted = st.form_submit_button("검색")

    if submitted:
        st.session_state.pop("places", None)
        if not query.strip():
            st.warning("검색어를 입력해 주세요.")
            return
        try:
            with st.spinner("장소를 검색하고 있습니다..."):
                st.session_state["places"] = search_places(query.strip(), api_key)
        except RuntimeError as exc:
            st.error(str(exc))
            return

    places = st.session_state.get("places")
    if places is None:
        st.info("장소명이나 지역과 업종을 입력하고 검색 버튼을 눌러 주세요.")
    elif not places:
        st.info("검색 결과가 없습니다. 다른 검색어를 입력해 주세요.")
    else:
        st.caption(f"검색 결과 {len(places)}곳 (최대 15곳)")
        st.map(places, latitude="lat", longitude="lng")
        st.dataframe(
            places,
            hide_index=True,
            column_order=["name", "address", "phone", "url"],
            column_config={
                "name": "장소",
                "address": "주소",
                "phone": "전화번호",
                "url": st.column_config.LinkColumn("카카오맵", display_text="장소 보기"),
            },
        )


if __name__ == "__main__":
    main()
