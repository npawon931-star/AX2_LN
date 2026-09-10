"""
에너지 소비량 데이터 필터링, 결측치 정리
energy consumption 4000 이상 필터링
building type로 필터링
energy_cleaned.csv로 저장
실행방법 : streamlit run day03-04.py
"""

import pandas as pd
import streamlit as st

st.title("에너지 소비량 데이터 필러링 & 결측치 정리")
st.caption("energy consumtion 4000 이상으로 필터링해보고, 결측치를 제거해 새 CSV로 저장합니다.")

CSV_PATH = "test_energy_data.csv"

try : 
    df = pd.read_csv(CSV_PATH)

except FileNotFoundError :
    st.error("❌에너지 소비량 파일을 찾을 수 없습니다.")

else : 
    st.metric("원본 데이터 행 개수", f"{len(df)}행")

    st.markdown("---")

    #energy 4000 이상 필터링
    st.subheader("1) 에너지 4000 이상 소비")

    over_4000 = df[df["Energy Consumption"]>=4000]
    st.write(f"에너지 4000 이상 소비량 : **{len(over_4000)}**")
    st.dataframe(over_4000[["Building Type", "Square Footage", "Number of Occupants", "Appliances Used", "Energy Consumption"]].head())

    st.markdown("---")

    #건물 종류 Residential, Commercial, Industrial 3컬럼 사용

    st.subheader("2) 건물 종류 필터링 결과")
    Residential_df = df[df["Building Type"] == "Residential"]
    Commercial_df = df[df["Building Type"] == "Commercial"]
    Industrial_df = df[df["Building Type"] == "Industrial"]
    col1, col2, col3 = st.columns(3)
    with col1 :
        st.metric("Residential 수", f"{len(Residential_df)}개")
    with col2 :
        st.metric("Commercial 수", f"{len(Commercial_df)}개")  
    with col3 :
        st.metric("Industrial 수", f"{len(Industrial_df)}개")

    st.markdown("---")

    # 두 조건을 동시에 만족하는 행
    st.subheader("3) Energy Consumption 4000 이상 & Industrial")
    over_4000_industrial = df[(df["Energy Consumption"]>=4000) & (df["Building Type"] == "Industrial")]
    st.write(f"Energy Consumption 4000 이상 & industrial: **{len(over_4000_industrial)}개**")

    st.markdown("---")

    # 건물 종류의 결측치(NaN) 확인 및 dropna 처리 
    st.subheader("4) Building Type 결측치 처리")
    missing_BT_count = df["Building Type"].isna().sum() #isna()는 결측치면 True 반환
    st.write(f"Building Type 열의 결측치 개수: **{missing_BT_count}개**")

    # subset=["Building Type"]: Building Type 열이 결측치인 행만 골라서 제거한다. 
    df_clean = df.dropna(subset=["Building Type"])
    col1, col2 = st.columns(2)
    with col1 :
        st.metric("제거 전", f"{len(df)}행")
    with col2 :
        st.metric("제거 후", f"{len(df_clean)}행")  


    # 정리된 데이터를 csv 파일로 저장
    output_path = "energy_cleaned.csv"
    df_clean.to_csv(output_path, index=False)
    st.success("파일을 저장했습니다")
    st.dataframe(df_clean.head(), use_container_width=True)