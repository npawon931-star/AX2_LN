# OpenAI + Streamlit: 대화 기록을 기억하지 않는 단발성 질문/답변 앱
# 실행: streamlit run day05-2.py

import streamlit as st
from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError, APIStatusError

st.set_page_config(page_title="나의 첫 번째 챗봇", page_icon="🤖", layout="centered")

st.markdown("""
<style>
.stMainBlockContainer {max-width: 850px; padding-top: 3rem;}
.hero {
    padding: 2rem; margin-bottom: 1.5rem; border-radius: 24px;
    background: linear-gradient(120deg, #182848, #4b3f8f); color: white;
    box-shadow: 0 12px 32px rgba(40, 40, 90, .15);
}
.hero .eyebrow {font-size: .8rem; letter-spacing: .18em; color: #c7d2fe;}
.hero h1 {color: white; font-size: 2rem; padding: .5rem 0;}
.hero p {color: #e0e7ff; margin-bottom: 0;}
div[data-testid="stForm"] {border-radius: 18px; padding: 1.5rem;}
div[data-testid="stMetric"] {
    border: 1px solid rgba(128, 128, 128, .25);
    border-radius: 16px; padding: 1rem;
}
div[data-testid="stFormSubmitButton"] button {
    border-radius: 12px; min-height: 3rem;
    background: #5b4fc7; color: white; border: none;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ 설정")
    st.caption("API 키를 입력하고 모델을 선택해 주세요.")
    api_key = st.text_input(
        "OpenAI API Key", type="password",
        help="sk-로 시작하는 OpenAI API 키를 입력하세요.",
    ).strip()
    model = st.selectbox(
        "모델 선택", ["gpt-4o-mini", "gpt-4o", "gpt-4.1", "gpt-4.1-mini"],
    )
    st.markdown("[API 키 발급 받기 ↗](https://platform.openai.com/api-keys)")
    st.divider()
    st.markdown("**이렇게 사용하세요**")
    st.caption("① API 키 입력 → ② 질문 작성 → ③ 답변 확인")
    st.info("각 질문은 독립적으로 처리되며, 이전 대화는 기억하지 않아요.")

st.markdown("""
<div class="hero">
    <div class="eyebrow">YOUR PERSONAL AI ASSISTANT</div>
    <h1>나의 첫 번째 챗봇</h1>
    <p>궁금한 순간, 편하게 물어보세요.<br>친절한 AI가 질문에 답해 드릴게요.</p>
</div>
""", unsafe_allow_html=True)

with st.form("question_form"):
    st.subheader("무엇이 궁금하신가요?")
    question = st.text_area(
        "질문을 입력하세요", placeholder="예) 파이썬의 리스트와 튜플 차이를 쉽게 설명해 줘.",
        height=130,
    )
    submitted = st.form_submit_button("질문하기 ✨", use_container_width=True)

if submitted:
    if not api_key:
        st.error("OpenAI API Key를 입력하세요.")
    elif not question.strip():
        st.error("질문을 입력하세요.")
    else:
        try:
            with st.spinner("답변을 생각하는 중..."):
                # 자동 재시도 없이, 제출한 질문에 대해 한 번만 요청합니다.
                with OpenAI(api_key=api_key, max_retries=0, timeout=60.0) as client:
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "당신은 친절한 한국어 답변가입니다. "
                                    "모든 답변을 반드시 '주인님'으로 시작하고 "
                                    "정중하고 이해하기 쉽게 설명하세요."
                                ),
                            },
                            {"role": "user", "content": question.strip()},
                        ],
                    )

            st.subheader("💬 답변")
            if response.choices:
                message = response.choices[0].message
                answer = (message.content or message.refusal or "").strip()
                if answer:
                    if not answer.startswith("주인님"):
                        answer = "주인님, " + answer
                    with st.container(border=True):
                        st.markdown(answer)
                else:
                    st.warning("답변 내용이 비어 있습니다. 질문을 바꿔 다시 시도해 주세요.")
                if response.choices[0].finish_reason == "length":
                    st.warning("답변이 길이 제한으로 중단되었습니다. 질문 범위를 줄여 주세요.")
            else:
                st.warning("답변을 받지 못했습니다. 다시 시도해 주세요.")

            st.divider()
            st.subheader("📊 이번 질문의 토큰 사용량")
            if response.usage is not None:
                input_col, output_col, total_col = st.columns(3)
                input_col.metric("입력 토큰", f"{response.usage.prompt_tokens:,}")
                output_col.metric("출력 토큰", f"{response.usage.completion_tokens:,}")
                total_col.metric("총 토큰 수", f"{response.usage.total_tokens:,}")
                st.caption("입력 토큰에는 답변 지침도 포함됩니다. 실제 비용은 모델과 입력·출력 토큰 단가에 따라 달라집니다.")
            else:
                st.caption("이번 응답에는 토큰 사용량 정보가 제공되지 않았습니다.")
        except AuthenticationError:
            st.error("API 키 인증에 실패했습니다. 입력한 키를 확인해 주세요.")
        except RateLimitError:
            st.error("요청 한도 또는 사용 가능한 크레딧을 초과했습니다. 사용량과 결제 설정을 확인해 주세요.")
        except APIConnectionError:
            st.error("OpenAI 서버에 연결하지 못했거나 응답 시간이 초과되었습니다. 잠시 후 다시 시도해 주세요.")
        except APIStatusError as exc:
            st.error(f"API 요청 중 오류가 발생했습니다 (상태 코드: {exc.status_code}). 모델 접근 권한과 서비스 상태를 확인해 주세요.")
        except Exception:
            st.error("답변 처리 중 예상하지 못한 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.")
else:
    st.caption("✦ 질문을 입력하면 이곳에 답변과 토큰 사용량이 표시됩니다.")