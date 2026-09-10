# 💱 실시간 환율 계산기 (KRW Based Currency Calculator)

원화(KRW)를 기준으로 주요 4개국 통화(**달러 USD, 유로 EUR, 엔화 JPY, 위안화 CNY**)의 실시간 환율 정보와 과거 추이 그래프를 제공하고, 원화 입력 시 각 통화별 환산 금액을 실시간으로 계산해주는 웹 기반 환율 계산기 프로젝트입니다.

---

## 🚀 주요 기능 (Features)

1. **실시간 환율 조회 및 기준가 표시**
   - `ExchangeRate-API`(무료 플랜)를 활용하여 최신 환율 데이터를 실시간으로 가져옵니다.
   - 1외화당 원화(KRW) 가치 및 1,000원당 엔화 등의 직관적인 환율 기준가를 상단 카드 형태로 제공합니다.
   - 포함 통화: 
     - 🇺🇸 미국 달러 (USD)
     - 🇪🇺 유로 (EUR)
     - 🇯🇵 일본 엔 (JPY - 100엔 기준 표시 지원)
     - 🇨🇳 중국 위안 (CNY)

2. **과거 환율 추이 그래프 (Historical Trends)**
   - 최근 30일간 주요 통화의 원화 대비 환율 변동 추이를 직관적인 인터랙티브 라인 차트(`Chart.js` / `Plotly`)로 시각화합니다.
   - 환율의 변동성을 한눈에 파악할 수 있습니다.

3. **원화 기준 실시간 환율 계산기**
   - 사용자가 원화(KRW) 금액을 입력하면, 최신 환율을 반영하여 각 통화(`USD`, `EUR`, `JPY`, `CNY`)로 환전했을 때의 금액을 실시간으로 계산해 줍니다.
   - 반대로 특정 통화 금액 입력 시 원화로 얼마인지 역계산하는 기능도 확장 가능합니다.

---

## 🛠️ 기술 스택 (Tech Stack)

- **Frontend**: HTML5, CSS3 (Tailwind CSS), JavaScript (Vanilla JS)
- **Visualization**: Chart.js (또는 Plotly.js)
- **API**: ExchangeRate-API (`https://v6.exchangerate-api.com/v6/{API_KEY}/latest/KRW` 또는 `USD`)

---

## 📂 프로젝트 구조 (Project Structure)

```text
currency-calculator/
├── README.md             # 프로젝트 소개 및 사용 설명서
├── index.html            # 메인 사용자 인터페이스 (HTML + Tailwind)
├── style.css             # 추가 스타일링 및 반응형 디자인
├── app.js                # API 연동, 실시간 환율 계산 및 차트 렌더링 로직
└── config.js             # API 키 설정 파일 (git ignore 권장)
```

---

## ⚙️ 시작하기 (Getting Started)

### 1. API 키 발급 받기
1. [ExchangeRate-API 공식 홈페이지](https://www.exchangerate-api.com/)에 접속하여 무료 계정을 생성합니다.
2. 발급받은 무료 API Key를 확인합니다.

### 2. 프로젝트 설정
1. 본 레포지토리를 클론하거나 다운로드합니다.
2. `config.js` 파일에 발급받은 API 키를 입력합니다.
   ```javascript
   const API_KEY = "YOUR_EXCHANGERATE_API_KEY";
   ```

### 3. 실행 방법
- 별도의 백엔드 서버 없이 `index.html` 파일을 웹 브라우저로 열거나, VS Code의 **Live Server** 확장 프로그램을 사용하여 실행할 수 있습니다.
