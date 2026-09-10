# raw_trade_data.csv 파일 활용
# HS 코드 85로 시작하는 (반도체류) 
# + 국가명 미국 또는 베트남 + 수출금액 0 보다 큰 수(실제 수출 실적이 있는) 행만
# 다중 조건으로 필터링 한 뒤, 수출금액 상위 10건을 화면에 보여주고 report.csv fh wjwkd
# streamlit 사용 streamlit run day 04-01.py

# 지금 github 시도 중
# github 실험 중
# 너무 어려워 ㅠㅠ
# 이거를 수정해야해

import streamlit as st
import pandas as pd
import os

# 페이지 설정
st.set_page_config(
    page_title="반도체 수출 실적 분석",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ 반도체 (HS Code 85) 미국/베트남 수출 실적 분석")
st.markdown("""
**raw_trade_data.csv** 파일을 활용하여 아래 조건으로 필터링한 후, 수출금액 상위 10건의 데이터를 분석합니다.
- **필터링 조건**:
  - **품목 (HS Code)**: 85로 시작하는 반도체 관련 품목
  - **대상 국가**: 미국 또는 베트남
  - **수출 실적**: 수출금액이 0보다 큰 실제 수출 실적이 있는 행
""")

# CSV 파일 경로 설정 (절대경로 및 상대경로 지원)
csv_paths = [
    r"C:\Users\user\AX2_LN\day04\raw_trade_data.csv",
    r"../day04/raw_trade_data.csv",
    r"day04/raw_trade_data.csv"
]

csv_path = None
for path in csv_paths:
    if os.path.exists(path):
        csv_path = path
        break

if csv_path is None:
    st.error("데이터 파일(raw_trade_data.csv)을 찾을 수 없습니다. 경로를 확인해주세요.")
else:
    # 데이터 불러오기
    try:
        df = pd.read_csv(csv_path)
        
        # 1. HS 코드 85로 시작
        cond_hs = df['hs_code'].astype(str).str.startswith('85')
        # 2. 국가명 미국 또는 베트남
        cond_country = df['국가명'].isin(['미국', '베트남'])
        # 3. 수출금액 > 0
        cond_amount = df['수출금액'] > 0
        
        # 필터링 적용
        filtered_df = df[cond_hs & cond_country & cond_amount]
        
        # 수출금액 상위 10건 정렬
        top_10 = filtered_df.sort_values(by='수출금액', ascending=False).head(10)
        
        # report.csv 파일로 자동 저장 (Excel 호환을 위해 utf-8-sig 사용)
        report_filename = "report.csv"
        top_10.to_csv(report_filename, index=False, encoding="utf-8-sig")
        
        # 주요 지표 표시
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("전체 데이터 수", f"{len(df):,} 건")
        with col2:
            st.metric("조건 만족 데이터 수", f"{len(filtered_df):,} 건")
        with col3:
            st.metric("상위 10건 총 수출금액", f"${top_10['수출금액'].sum():,} (USD)")
            
        st.subheader("🏆 수출금액 상위 10건")
        
        # 데이터프레임 표시
        st.dataframe(top_10.style.format({
            '수출금액': '{:,.0f}',
            '중량': '{:,.2f}'
        }), width='stretch')
        
        # 저장 알림 및 다운로드 버튼
        st.success(f"💾 상위 10건의 데이터를 **{report_filename}** 파일로 자동 저장 완료했습니다.")
        
        # 웹 브라우저 다운로드 버튼도 제공
        csv_data = top_10.to_csv(index=False, encoding="utf-8-sig").encode('utf-8-sig')
        st.download_button(
            label="📥 CSV 파일 직접 다운로드",
            data=csv_data,
            file_name="report.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(f"데이터를 처리하는 중 오류가 발생했습니다: {e}")
