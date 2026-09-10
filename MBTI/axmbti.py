import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import urllib.request

# 1. 페이지 설정 및 커스텀 CSS (카드 박스 버튼 스타일 및 Pretendard 폰트 적용)
st.set_page_config(page_title="무역직무 MBTI: Confidential Trade Profile", page_icon="📂", layout="centered")

st.markdown("""
<style>
    @import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css");

    .stApp, body, p, span, div, h1, h2, h3, h4, h5, h6, label {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, 'Helvetica Neue', 'Segoe UI', 'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif !important;
    }

    .folder-tab {
        background-color: #C66B76;
        color: white;
        padding: 10px 20px;
        border-radius: 8px 8px 0 0;
        font-weight: bold;
        display: inline-block;
        font-size: 1.1rem;
        letter-spacing: 1px;
    }
    
    div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"] {
        background-color: #FFFFFF;
        border: 2px solid #C66B76;
        padding: 30px;
        border-radius: 0 12px 12px 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 30px;
    }

    /* 카드 박스 형태의 커스텀 버튼 스타일 */
    .stButton>button {
        border-radius: 12px !important;
        border: 1.5px solid #E5DCD0 !important;
        padding: 15px 20px !important;
        font-weight: 600 !important;
        width: 100% !important;
        text-align: left !important;
        transition: all 0.2s ease-in-out !important;
        background-color: #FDFBF7 !important;
        color: #2B2B2B !important;
        margin-bottom: 6px;
    }
    
    .stButton>button:hover {
        background-color: #F4EBE1 !important;
        border-color: #C66B76 !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. 클라우드 서버 환경 한글 폰트 강제 설정
@st.cache_resource
def setup_matplotlib_font():
    font_path = "NanumGothic.ttf"
    if not os.path.exists(font_path):
        try:
            url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
            urllib.request.urlretrieve(url, font_path)
        except Exception:
            pass
            
    if os.path.exists(font_path):
        try:
            fm.fontManager.add_font(font_path)
            prop = fm.FontProperties(fname=font_path)
            font_name = prop.get_name()
            plt.rcParams['font.family'] = font_name
        except Exception:
            pass
            
    plt.rcParams['axes.unicode_minus'] = False

setup_matplotlib_font()

# 3. 8개 직무 정의 및 상세 페르소나 데이터
JOB_DETAILS = {
    "해외영업/바이어관리": {
        "title": "🔥 판을 키우고 사람을 사로잡는 최전선의 전략가",
        "desc": "신규 시장 개척, 바이어 발굴 및 협상, 계약 체결을 주도하며 탁월한 설득력과 순발력으로 성과를 만들어냅니다.",
        "target": "종합상사(현대, LX, 포스코), 대기업·중견 제조사 해외영업부서",
        "weapon": "무역영어 1급, 국제무역사 1급, 최상위 어학(오픽 AL 등)",
        "caution": "서류 마감이나 반복적인 행정 정산 업무에서는 쉽게 지루함을 느낄 수 있습니다."
    },
    "해외마케팅/수출기획": {
        "title": "🎯 현지 트렌드를 꿰뚫어 보는 글로벌 브랜드 아키텍트",
        "desc": "현지 시장 데이터를 분석하고 디지털 마케팅 전략을 짜서 K-브랜드의 해외 진입 경로를 설계합니다.",
        "target": "글로벌 소비재/K-뷰티 브랜드(아모레, 실리콘투 등), 수출입 유통사",
        "weapon": "검색광고마케터, GA4, 국제무역사 1급, 트렌드 분석 역량",
        "caution": "직관적인 성과가 눈에 보이지 않는 장기 프로젝트 구간에서 피로감을 느낄 수 있습니다."
    },
    "물류/SCM": {
        "title": "⚙️ 공급망의 맥을 짚어 리스크를 통제하는 실행·조율가",
        "desc": "최적의 운송 경로를 짜고 물류 지연이나 돌발 변수에 맞서 비용과 시간을 혁신적으로 방어합니다.",
        "target": "글로벌 포워더(판토스, CJ대한통운), 대기업 SCM 총괄팀",
        "weapon": "물류관리사, 유통관리사 2급, CPIM",
        "caution": "예상치 못한 천재지변이나 선사 지연 등 통제 불가능한 변수 발생 시 스트레스가 큽니다."
    },
    "무역사무/오퍼상담": {
        "title": "📋 단 1건의 오탈자도 허용하지 않는 꼼꼼한 오퍼레이션 관리자",
        "desc": "L/C, B/L 등 복잡한 무역 서류를 완벽하게 검토하고 유관 부서와의 납기를 칼같이 조율합니다.",
        "target": "중견·중소 수출입 기업 관리부서, 외국계 오퍼상(Agent)",
        "weapon": "무역영어 1급, 국제무역사 1급, 재무/회계 기초 소양",
        "caution": "반복적인 서류 검토 작업 속에서 매너리즘이나 시야 협소에 빠지지 않도록 주의해야 합니다."
    },
    "글로벌 구매/수입MD": {
        "title": "🛒 전 세계를 뒤져 최적의 단가와 품질을 쥐어짜는 실속형 협상가",
        "desc": "우수 상품 및 원부자재 소싱처를 발굴하고, 공급사와의 팽팽한 단가 협상을 통해 마진을 극대화합니다.",
        "target": "대형 유통사(이마트, 쿠팡 등 글로벌 Sourcing 팀), 종합상사 수입부서",
        "weapon": "유통관리사 2급, 국제무역사 1급, CPSM(국제구매공인전문가)",
        "caution": "공급사의 무리한 납기 단가 요구 압박 속에서 품질과 원가 사이의 밸런스를 잡아야 합니다."
    },
    "통관/관세전문": {
        "title": "⚖️ 법적 테두리 안에서 단 1%의 리스크도 용납하지 않는 원칙주의자",
        "desc": "관세법, HS코드, FTA 원산지 결정기준을 정확히 다루며 기업의 세무·법적 리스크를 철저히 방어합니다.",
        "target": "관세법인 및 관세사무소, 대기업 관세·통관 전담 부서",
        "weapon": "관세사, 원산지관리사, 무역영어 1급",
        "caution": "법령 개정이나 까다로운 세관 심사 조항을 주기적으로 파고들어야 하는 끈기가 필수적입니다."
    },
    "해외사업기획/전략": {
        "title": "🌐 거시적 비즈니스를 설계하고 미래의 판을 짜는 비전가",
        "desc": "신사업 투자, 합작법인(JV) 설립, 해외 거점 확장 등 전사적 글로벌 전략과 로드맵을 기획합니다.",
        "target": "대기업 그룹사 전략기획실, 글로벌 컨설팅 펌, 해외 인프라 투자 기업",
        "weapon": "데이터분석 관련 자격증(ADsP 등), 경영사례 분석력, 최상위 어학",
        "caution": "실무 실행 단계보다 거시적 계획 단계에 치우쳐 현실과 이상 사이 괴리를 느낄 수 있습니다."
    },
    "해외영업관리/CS": {
        "title": "🤝 돌발 클레임을 부드럽게 녹여내는 든든한 소통 중재자",
        "desc": "수출입 과정에서 터지는 온갖 클레임과 이슈를 냉철하게 분석하고 바이어와의 관계를 매끄럽게 회복합니다.",
        "target": "글로벌 하드웨어 제조사, IT/전자제품 수출 기업의 고객지원/해외운영팀",
        "weapon": "무역영어 1급, 비즈니스 커뮤니케이션 자격, 높은 공감 및 협상력",
        "caution": "양측의 불만을 동시에 받아내는 감정 노동 강도가 높을 수 있으므로 멘탈 관리가 중요합니다."
    }
}

# 4. 20문항 데이터셋 정의 (파트별 분류)
QUESTIONS_BY_PART = {
    "Part 1: 기본 성향": [
        {"id": "q_0", "q": "Q1. 새로운 사람들을 만나거나 모임에 갔을 때, 나의 평소 모습은?", "a": "내가 먼저 주도적으로 대화를 이끌고 분위기를 띄우는 편이다.", "b": "상대방의 이야기를 경청하고 전체적인 분위기를 차분하게 조율하는 편이다.", "map_a": ["해외영업/바이어관리", "해외마케팅/수출기획", "해외사업기획/전략", "해외영업관리/CS"], "map_b": ["물류/SCM", "무역사무/오퍼상담", "글로벌 구매/수입MD", "통관/관세전문"], "weight": 1},
        {"id": "q_1", "q": "Q2. 친구들이나 동료들이 말하는 나의 가장 큰 장점은?", "a": "너는 일단 저지르고 보는 추진력이 있어! 실행력이 장이야.", "b": "너는 실수를 안 해서 믿고 맡길 수 있어. 엄청 꼼꼼해.", "map_a": ["해외영업/바이어관리", "해외사업기획/전략", "해외마케팅/수출기획"], "map_b": ["무역사무/오퍼상담", "통관/관세전문", "물류/SCM"], "weight": 1},
        {"id": "q_2", "q": "Q3. 여러 가지 일을 동시에 처리해야 하는 멀티태스킹 상황이 닥쳤을 때 나는?", "a": "직관과 순발력을 발휘해 눈앞에 닥친 중요한 일부터 빠르게 해치운다.", "b": "리스트를 꼼꼼하게 적고 우선순위를 철저히 계산한 뒤 하나씩 확실하게 끝낸다.", "map_a": ["해외영업/바이어관리", "해외영업관리/CS", "해외마케팅/수출기획"], "map_b": ["무역사무/오퍼상담", "통관/관세전문", "물류/SCM"], "weight": 1},
        {"id": "q_3", "q": "Q4. 모임이나 프로젝트에서 의견이 팽팽하게 갈릴 때, 나는 주로 어떤 역할을 맡는가?", "a": "내 주장을 명확하게 설득하고 판을 우리 쪽으로 유리하게 끌고 가려 한다.", "b": "양쪽의 입장을 객관적으로 중재하며 누구나 수용할 수 있는 합리적인 절충안을 찾는다.", "map_a": ["해외영업/바이어관리", "해외사업기획/전략", "글로벌 구매/수입MD"], "map_b": ["해외영업관리/CS", "무역사무/오퍼상담", "물류/SCM"], "weight": 1},
        {"id": "q_4", "q": "Q5. 공부를 하거나 새로운 과제를 맡았을 때 나를 더 흥분시키는 포인트는?", "a": "트렌드가 어떻게 변하고 있는지, 시장의 큰 그림과 새로운 기회를 발견하는 것.", "b": "복잡한 데이터를 뜯어보며 숨은 규칙이나 오차를 완벽하게 찾아내는 것.", "map_a": ["해외마케팅/수출기획", "해외사업기획/전략"], "map_b": ["무역사무/오퍼상담", "통관/관세전문", "물류/SCM"], "weight": 1}
    ],
    "Part 2: 실무 상황 대처": [
        {"id": "q_5", "q": "Q6. 해외 바이어와 첫 화상 미팅을 앞두고 있다. 나의 사전 준비 스타일은?", "a": "바이어의 현지 문화, 최근 비즈니스 이슈, 주요 관심사를 바삭하게 조사해 맞춤형 스크립트를 짠다.", "b": "핵심 제품 스펙과 가격 경쟁력, 예상되는 가격 협상 시나리오를 완벽하게 시뮬레이션한다.", "map_a": ["해외마케팅/수출기획", "해외사업기획/전략"], "map_b": ["해외영업/바이어관리", "글로벌 구매/수입MD"], "weight": 3},
        {"id": "q_6", "q": "Q7. 선적을 코앞에 둔 긴급 상황, 파트너사로부터 '선박 스케줄이 3일 지연되었다'는 연락이 왔다. 나의 첫 반응은?", "a": "즉시 대체 가능한 다른 선사나 운송 경로(항공 등)를 수배해 비용 대비 리스크를 최소화할 대안을 찾는다.", "b": "바이어에게 곧바로 상황을 투명하게 공유하고, 납기 지연에 따른 클레임이나 페널티 방어 대책을 세운다.", "map_a": ["물류/SCM"], "map_b": ["해외영업관리/CS"], "weight": 3},
        {"id": "q_7", "q": "Q8. 계약서 최종 검토 단계에서 내가 가장 집착하는 부분은?", "a": "인코텀즈(Incoterms) 조건과 결제 방식(L/C 등), 환율 변동 리스크가 우리에게 유리하게 설계되었는지 뜯어본다.", "b": "품목의 정확한 HS코드 매칭과 FTA 원산지 결정기준 충족 여부 등 세관 관련 법적 하자가 전혀 없는지 확인한다.", "map_a": ["무역사무/오퍼상담", "해외사업기획/전략"], "map_b": ["통관/관세전문"], "weight": 3},
        {"id": "q_8", "q": "Q9. 공급사와의 단가 협상 자리, 상대방이 턱없이 높은 가격을 부르며 꿈쩍도 하지 않는다. 나의 협상 전략은?", "a": "경쟁사 풀과 시장 시세 데이터를 근거로 조목조목 반박하며 팽팽하게 압박해 단가를 깎아낸다.", "b": "장기 계약 물량 보장이나 상호 윈윈할 수 있는 다른 조건을 제안해 부드럽게 합의점을 이끌어낸다.", "map_a": ["글로벌 구매/수입MD"], "map_b": ["해외영업/바이어관리"], "weight": 3},
        {"id": "q_9", "q": "Q10. 바이어나 협력사와 트러블(클레임)이 발생했을 때 나의 대처 방식은?", "a": "감정적으로 대응하지 않고 계약서와 팩트를 기반으로 원인을 칼같이 분석해 책임 소재를 명확히 가린다.", "b": "상대방의 불만을 적극적으로 공감하고 경청하며, 발 빠르게 보상안이나 대안을 제시해 관계를 회복한다.", "map_a": ["통관/관세전문", "무역사무/오퍼상담"],
        "map_b": ["해외영업관리/CS"], "weight": 3}
    ],
    "Part 3: 스펙 및 역량 성향": [
        {"id": "q_10", "q": "Q11. 내가 다루거나 자신 있어 하는(또는 배우고 싶은) 데이터·오피스 도구는?", "a": "엑셀 함수, 통계 툴 등을 활용해 복잡한 숫자를 다듬고 트렌드나 인사이트를 도출하는 것.", "b": "오피스 프로그램을 활용해 깔끔한 계약서 양식, 오퍼 시트, 인보이스, 무역 서류를 틀림없이 작성하는 것.", "map_a": ["해외마케팅/수출기획", "해외사업기획/전략", "물류/SCM"], "map_b": ["무역사무/오퍼상담", "통관/관세전문"], "weight": 3},
        {"id": "q_11", "q": "Q12. 나의 외국어 활용 능력이나 선호하는 소통 방식은?", "a": "언어 유창성이나 비즈니스 회화 능력을 살려 사람을 직접 대면하거나 대화로 설득하는 것.", "b": "비즈니스 이메일, 영문 계약서 조항, 관세 법령 등 서면 문서 위주의 정확한 커뮤니케이션.", "map_a": ["해외영업/바이어관리", "해외영업관리/CS"],
        "map_b": ["무역사무/오퍼상담", "통관/관세전문"], "weight": 3},
        {"id": "q_12", "q": "Q13. 내가 커리어를 쌓기 위해 가장 먼저 취득하고 싶거나, 내 무기라고 생각하는 자격증 분야는?", "a": "어학 성적이나 국제무역사, 유통관리사처럼 시장 흐름과 바이어 소통을 증명하는 자격증.", "b": "물류관리사, 관세사, 원산지관리사, CPIM처럼 특정 전문 법규나 공급망 프로세스를 파고드는 자격증.", "map_a": ["해외영업/바이어관리", "해외마케팅/수출기획", "글로벌 구매/수입MD"],
        "map_b": ["물류/SCM", "통관/관세전문", "무역사무/오퍼상담"],
        "weight": 3},
        {"id": "q_13", "q": "Q14. 대외활동이나 프로젝트, 팀플을 할 때 내가 주로 맡았던 역할은?", "a": "전체 프로젝트의 기획 방향을 잡고, 대외 발표나 외부 협력사 컨택을 주도하는 리더롤.", "b": "팀원들이 놓치는 세부적인 일정, 예산 계산, 서류 마감을 철저히 챙기는 서포트/관리롤.", "map_a": ["해외사업기획/전략", "해외영업/바이어관리"],
        "map_b": ["무역사무/오퍼상담", "물류/SCM"],
        "weight": 3},
        {"id": "q_14", "q": "Q15. 내가 생각하는 나의 '일잘러' 기준은 무엇인가?", "a": "누구도 생각하지 못한 새로운 기회를 포착해 성과를 폭발적으로 만들어내는 것.", "b": "단 한 건의 실수나 법적 리스크도 허용하지 않고 시스템을 완벽하게 굴러가게 만드는 것.", "map_a": ["해외영업/바이어관리", "해외마케팅/수출기획", "해외사업기획/전략"],
        "map_b": ["통관/관세전문", "무역사무/오퍼상담", "물류/SCM"],
        "weight": 3}
    ],
    "Part 4: 커리어 가치관": [
        {"id": "q_15", "q": "Q16. 내가 직장을 선택할 때 가장 타협할 수 없는 가치는 무엇인가?", "a": "회사의 폭발적인 성장 가능성과 내가 그 안에서 주도적으로 판을 키울 수 있는지 여부.", "b": "시스템이 체계적이고, 나의 전문성과 커리어가 확실한 스펙으로 쌓일 수 있는지 여부.", "map_a": ["해외사업기획/전략", "해외영업/바이어관리"],
        "map_b": ["통관/관세전문", "무역사무/오퍼상담"],
        "weight": 5},
        {"id": "q_16", "q": "Q17. 훗날 나의 커리어 목표가 '최고의 전문가'가 되는 것이라면, 내가 더 듣고 싶은 찬사는?", "a": "저 사람은 해외 바이어 마음을 사로잡고 계약을 따오는 데는 독보적이야!", "b": "저 사람을 거치면 공급망이나 통관·물류에서 단 1%의 리스크도 생기지 않아.", "map_a": ["해외영업/바이어관리", "해외마케팅/수출기획"],
        "map_b": ["물류/SCM", "통관/관세전문", "무역사무/오퍼상담"],
        "weight": 5},
        {"id": "q_17", "q": "Q18. 회사 생활을 하면서 가장 큰 보람이나 희열을 느끼는 순간은?", "a": "수많은 경쟁을 뚫고 내 손으로 직접 거대 계약을 성사시켰거나 새로운 시장을 열었을 때.", "b": "복잡하게 얽혀 있던 물류 지연이나 단가 협상, 서류 트러블을 완벽하게 해결해 프로세스를 정상화했을 때.", "map_a": ["해외영업/바이어관리", "해외사업기획/전략"],
        "map_b": ["물류/SCM", "통관/관세전문", "글로벌 구매/수입MD"],
        "weight": 5},
        {"id": "q_18", "q": "Q19. 내가 생각하는 '이상적인 비즈니스 파트너(상사나 거래처)'의 모습은?", "a": "새로운 아이디어를 과감하게 수용하고, 도전적인 목표를 향해 함께 속도를 내주는 리더.", "b": "지시사항이 명확하고, 리스크 관리 능력이 뛰어나며 실수를 용납하지 않는 꼼꼼한 실무형 리더.", "map_a": ["해외영업/바이어관리", "해외마케팅/수출기획", "해외사업기획/전략"],
        "map_b": ["무역사무/오퍼상담", "통관/관세전문", "물류/SCM"],
        "weight": 5},
        {"id": "q_19", "q": "Q20. 앞으로 무역·상사 업계에서 내가 펼치고 싶은 최종 꿈은?", "a": "글로벌 거점을 누비며 회사의 성장을 이끄는 글로벌 리더 및 사업가.", "b": "글로벌 공급망과 무역 생태계의 흐름을 꿰뚫고 있는 대체 불가능한 분야별 최고 스페셜리스트.",
        "map_a": ["해외사업기획/전략", "해외영업/바이어관리"],
        "map_b": ["통관/관세전문", "물류/SCM", "글로벌 구매/수입MD"],
        "weight": 5}
    ]
}

ALL_QUESTIONS = []
for part_name, q_list in QUESTIONS_BY_PART.items():
    for q in q_list:
        ALL_QUESTIONS.append(q)

if "step" not in st.session_state:
    st.session_state.step = "welcome"
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "current_part_idx" not in st.session_state:
    st.session_state.current_part_idx = 0

part_keys = list(QUESTIONS_BY_PART.keys())

# 5. 화면 분기 로직
if st.session_state.step == "welcome":
    st.markdown('<div class="folder-tab">📂 CONFIDENTIAL TRADE PROFILE</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown("""
            <h2 style="color: #C66B76; margin-top:0;">무역직무 MBTI 성향 테스트</h2>
            <p><b>"나의 무역 DNA는 어떤 직무에 최적화되어 있을까?"</b></p>
            <p>총 20개의 문항을 통해 당신의 성향, 실무 대처 능력, 커리어 가치관을 입체적으로 분석하고, 딱 맞는 무역·상사 직무와 <b>5대 역량 꺾은선 그래프</b>를 도출해 드립니다.</p>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="font-size: 0.9rem; color: #666;">• 소요 시간: 약 3분<br>• 결과: 맞춤형 직무 페르소나 + 추천 기업 및 필수 자격증 진단서</p>
        """, unsafe_allow_html=True)
        
        if st.button("진단 시작하기 🚀"):
            st.session_state.step = "survey"
            st.session_state.current_part_idx = 0
            st.rerun()

elif st.session_state.step == "survey":
    current_part_name = part_keys[st.session_state.current_part_idx]
    
    st.markdown(f'<div class="folder-tab">📝 {current_part_name.upper()}</div>', unsafe_allow_html=True)
    
    with st.container():
        answered_count = sum(1 for q in ALL_QUESTIONS if st.session_state.answers.get(q['id']) is not None)
        progress = answered_count / len(ALL_QUESTIONS)
        st.progress(progress)
        st.write(f"**전체 진행 상황:** {answered_count} / {len(ALL_QUESTIONS)} 문항 완료 ({current_part_name})")
        st.markdown("---")
        
        current_questions = QUESTIONS_BY_PART[current_part_name]
        
        for q in current_questions:
            st.markdown(f"**{q['q']}**")
            
            current_ans = st.session_state.answers.get(q['id'], None)
            
            prefix_a = "✅ " if current_ans == 'A' else "🤍 "
            if st.button(f"{prefix_a} [A형] {q['a']}", key=f"btn_{q['id']}_A"):
                st.session_state.answers[q['id']] = 'A'
                st.rerun()
                
            prefix_b = "✅ " if current_ans == 'B' else "🤍 "
            if st.button(f"{prefix_b} [B형] {q['b']}", key=f"btn_{q['id']}_B"):
                st.session_state.answers[q['id']] = 'B'
                st.rerun()
                
            st.markdown("<br>", unsafe_allow_html=True)
            
        col1, col2 = st.columns(2)
        with col1:
            if st.session_state.current_part_idx > 0:
                if st.button("⬅️ 이전 파트"):
                    st.session_state.current_part_idx -= 1
                    st.rerun()
        with col2:
            if st.session_state.current_part_idx < len(part_keys) - 1:
                if st.button("다음 파트 ➡️"):
                    st.session_state.current_part_idx += 1
                    st.rerun()
            else:
                if st.button("결과 분석서 확인하기 🔍"):
                    if answered_count < len(ALL_QUESTIONS):
                        st.warning("모든 문항을 선택해주세요!")
                    else:
                        st.session_state.step = "result"
                        st.rerun()

elif st.session_state.step == "result":
    job_scores = {job: 0 for job in JOB_DETAILS.keys()}
    axis_scores = {"외향·소통": 0, "시장·전략": 0, "실행·조율": 0, "분석·소싱": 0, "법규·꼼꼼": 0}
    
    for idx, q in enumerate(ALL_QUESTIONS):
        ans = st.session_state.answers.get(q['id'], "A")
        weight = q['weight']
        
        target_jobs = q['map_a'] if ans == 'A' else q['map_b']
        for j in target_jobs:
            if j in job_scores:
                job_scores[j] += weight
                
        if idx in [0, 2, 11, 16]:
            if ans == 'A': axis_scores["외향·소통"] += weight * 5
        if idx in [4, 5, 14]:
            if ans == 'A': axis_scores["시장·전략"] += weight * 5
        if idx in [1, 6]:
            if ans == 'A': axis_scores["실행·조율"] += weight * 5
        if idx in [3, 8, 10]:
            if ans == 'A': axis_scores["분석·소싱"] += weight * 5
        if idx in [7, 9, 12, 13, 17, 19]:
            if ans == 'B': axis_scores["법규·꼼꼼"] += weight * 5

    best_job = max(job_scores, key=job_scores.get)
    result_data = JOB_DETAILS[best_job]
    
    st.markdown(f'<div class="folder-tab">📂 RESULT: {best_job}</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown(f"""
            <h2 style="color: #C66B76; margin-top:0;">{result_data['title']}</h2>
            <p style="font-size: 1.1rem; line-height: 1.6;">{result_data['desc']}</p>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
        """, unsafe_allow_html=True)
        
        st.markdown("### **📊 5대 역량 스펙트럼 분석 그래프**")
        
        max_val = max(axis_scores.values()) if max(axis_scores.values()) > 0 else 1
        normalized_scores = {k: min(int((v / max_val) * 85) + 15, 100) for k, v in axis_scores.items()}
        
        for k in normalized_scores:
            if normalized_scores[k] < 20:
                normalized_scores[k] = 35

        fig, ax = plt.subplots(figsize=(8, 4.5))
        fig.patch.set_facecolor('#FFFFFF')
        ax.set_facecolor('#FDFBF7')
        
        categories = list(normalized_scores.keys())
        values = list(normalized_scores.values())
        x_pos = range(len(categories))
        
        # 명시적으로 폰트 프로퍼티 생성 및 적용
        font_path = "NanumGothic.ttf"
        font_prop = fm.FontProperties(fname=font_path) if os.path.exists(font_path) else None
        
        ax.plot(x_pos, values, marker='o', color='#5A2E34', linewidth=2.5, markersize=8)
        ax.fill_between(x_pos, values, color='#C66B76', alpha=0.15)
        
        ax.set_xticks(list(x_pos))
        ax.set_xticklabels(categories, fontsize=10, fontweight='bold', color='#2B2B2B', fontproperties=font_prop)
        ax.set_ylim(0, 110)
        ax.set_ylabel("숙련도 (Lv. Score)", fontsize=9, color='#666', fontproperties=font_prop)
        ax.grid(axis='y', linestyle='--', alpha=0.5, color='#ccc')
        
        for spine in ['top', 'right']:
            ax.spines[spine].set_visible(False)
        for spine in ['bottom', 'left']:
            ax.spines[spine].set_color('#C66B76')

        st.pyplot(fig)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div style="background-color: #F4F6F4; padding: 15px; border-radius: 8px; border-left: 4px solid #588157; height: 100%;">
                <h4 style="color: #588157; margin-top:0;">✅ 추천 기업 & 핵심 무기</h4>
                <p><b>타겟 기업:</b><br>{}</p>
                <p><b>추천 자격증:</b><br>{}</p>
            </div>
            """.format(result_data['target'], result_data['weapon']), unsafe_allow_html=True)
            
        with col2:
            st.markdown("""
            <div style="background-color: #FAF4F4; padding: 15px; border-radius: 8px; border-left: 4px solid #C66B76; height: 100%;">
                <h4 style="color: #C66B76; margin-top:0;">⚠️ 실무 주의 포인트</h4>
                <p>{}</p>
            </div>
            """.format(result_data['caution']), unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("테스트 다시하기 🔄"):
            st.session_state.answers = {}
            st.session_state.step = "welcome"
            st.session_state.current_part_idx = 0
            st.rerun()