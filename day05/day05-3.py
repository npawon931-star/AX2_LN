# 대화 기록을 기억하는 멀티턴 챗봇(스트리밍 응답)
# st.session_state에 대화 기록을 저장해서, 이전 대화 맥락을 기억하는 챗봇
# st.chat_message / st.chat_input 같은 streamlit의 채팅 전용 위젯을 사용합니다.
# stream=True 옵션으로 답변이 실시간으로 타이핑되듯 출력됩니다.
# streamlit run day05-3.py

# 시스템 메시지를 사용자가 설정하도록
# 대화 기록 초기화 버튼

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

# 대화 기록과 스트리밍 응답을 처리합니다.
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_usage" not in st.session_state:
    st.session_state.last_usage = None

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
    system_message = st.text_area(
        "시스템 메시지",
        value="당신은 친절한 한국어 답변가입니다. 모든 답변을 반드시 '주인님'으로 시작하고 정중하고 이해하기 쉽게 설명하세요.",
        key="system_message", height=150,
        help="AI의 역할과 답변 방식을 설정합니다. 변경 내용은 다음 질문부터 적용됩니다.",
    )
    if st.button("대화 기록 초기화", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_usage = None
        st.rerun()
    st.markdown("[API 키 발급 받기 ↗](https://platform.openai.com/api-keys)")
    st.divider()
    st.markdown("**이렇게 사용하세요**")
    st.caption("① API 키 입력 → ② 질문 작성 → ③ 답변 확인")
    st.info("현재 세션의 이전 대화를 기억해요. 초기화 버튼을 누르면 새 대화를 시작합니다.")

st.markdown("""
<div class="hero">
    <div class="eyebrow">YOUR PERSONAL AI ASSISTANT</div>
    <h1>나의 첫 번째 챗봇</h1>
    <p>궁금한 순간, 편하게 물어보세요.<br>친절한 AI가 질문에 답해 드릴게요.</p>
</div>
""", unsafe_allow_html=True)

# 대화 기록과 스트리밍 응답을 처리합니다.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if not st.session_state.messages:
    st.caption("질문을 입력하면 대화를 시작합니다.")

question = st.chat_input("질문을 입력하세요")
if question:
    if not api_key:
        st.error("OpenAI API Key를 입력하세요.")
    elif not question.strip():
        st.error("질문을 입력하세요.")
    else:
        user_message = {"role": "user", "content": question.strip()}
        with st.chat_message("user"):
            st.markdown(user_message["content"])

        # 대화 기록과 스트리밍 응답을 처리합니다.
        messages = [*st.session_state.messages, user_message]
        if system_message.strip():
            messages.insert(0, {"role": "system", "content": system_message.strip()})
        st.session_state.last_usage = None
        try:
            with st.chat_message("assistant"):
                placeholder = st.empty()
                placeholder.markdown("답변을 생각하는 중...")
                answer = ""
                finish_reason = None
                usage = None
                with OpenAI(api_key=api_key, max_retries=0, timeout=60.0) as client:
                    with client.chat.completions.create(
                        model=model,
                        messages=messages,
                        stream=True,
                        stream_options={"include_usage": True},
                    ) as stream:
                        for chunk in stream:
                            if chunk.usage is not None:
                                usage = chunk.usage
                            # 대화 기록과 스트리밍 응답을 처리합니다.
                            if not chunk.choices:
                                continue
                            choice = chunk.choices[0]
                            if choice.finish_reason is not None:
                                finish_reason = choice.finish_reason
                            text = choice.delta.content or choice.delta.refusal or ""
                            if text:
                                answer += text
                                placeholder.markdown(answer + "▌")
                if answer.strip():
                    placeholder.markdown(answer)
                    # 대화 기록과 스트리밍 응답을 처리합니다.
                    st.session_state.messages.extend([
                        user_message, {"role": "assistant", "content": answer},
                    ])
                else:
                    placeholder.empty()
                    st.warning("답변 내용이 비어 있습니다. 다시 질문해 주세요.")
                if finish_reason == "length":
                    st.warning("답변이 길이 제한으로 중단되었습니다. 이어서 설명해 달라고 요청해 주세요.")
                st.session_state.last_usage = usage
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

if st.session_state.last_usage is not None:
    st.divider()
    st.subheader("📊 최근 질문의 토큰 사용량")
    usage = st.session_state.last_usage
    input_col, output_col, total_col = st.columns(3)
    input_col.metric("입력 토큰", f"{usage.prompt_tokens:,}")
    output_col.metric("출력 토큰", f"{usage.completion_tokens:,}")
    total_col.metric("총 토큰 수", f"{usage.total_tokens:,}")
    st.caption("입력 토큰에는 시스템 메시지와 이전 대화 기록도 포함됩니다.")
