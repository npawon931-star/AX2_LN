# 📂 무역직무 MBTI: Confidential Trade Profile

"나의 무역 DNA는 어떤 직무에 최적화되어 있을까?"  
감각적인 기밀 문서(Case File) 콘셉트와 꺾은선 그래프 분석을 결합한 인터랙티브 무역·상사 직무 성향 테스트입니다.

---

## 🚀 Key Features (주요 기능)

1. **4가지 파트별 20문항 진단**
   - **Part 1 (기본 성향):** 평소 태도와 의사결정 스타일 파악 (1점 가중치)
   - **Part 2 (실무 상황 대처):** 바이어 미팅, 선적 지연, 단가 협상 등 리얼 무역 상황 (3점 가중치)
   - **Part 3 (스펙 및 역량):** 선호하는 툴, 외국어 소통 방식, 자격증 성향 (3점 가중치)
   - **Part 4 (커리어 가치관):** 직장 선택 기준 및 최종 목표 (5점 타이브레이커 가중치)
2. **5대 역량 축 선 그래프 분석**
   - 외향·소통 / 시장·전략 / 실행·조율 / 분석·소싱 / 법규·꼼꼼 5개 축을 바탕으로 유저의 성향을 꺾은선 그래프로 시각화
3. **사건 파일(Case File) 인덱스 탭 디자인**
   - 톤다운된 파스텔 및 버건디 계열의 펠트·폴더 탭 UI 콘셉트 적용
   - 직무별 맞춤형 추천 기업 및 핵심 자격증(Good/Bad 팁) 제공

---

## 🛠️ Tech Stack

- **Framework:** Python, Streamlit
- **Data Handling:** Pandas, NumPy
- **Visualization:** Matplotlib / Plotly (선 그래프 구현용)

---

## 📁 Project Structure

```text
trade-mbti-app/
├── assets/             # 폰트 및 이미지 아이콘
├── data/               # 문항 데이터 및 직무별 페르소나 정의 (json/csv)
├── app.py              # Streamlit 메인 실행 파일
├── logic.py            # 20문항 차등 가중치 채점 및 그래프 데이터 변환 로직
└── README.md