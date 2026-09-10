# 인코딩 자동 감지 + 한글 폰트 막대 그래프
# 여러 인코딩("utf-8-sig", "cp949", "euc-kr")
# 내가 쓸 폰트 같은 경로에 있어야 함
# 객실 등급별 생존율 막대그래프 생성 후 그림으로 저장 chart.png
# 실행 streamlit run day03-05.py

#CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "common", "raw_trade_data")
#CSV_PATH = "..\common\Titanic.csv"

import os
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from matplotlib import font_manager

st.title("📊인코딩 자동감지 + 한글 폰트 막대 그래프 (Titanic 연습)")
st.caption("여러 인코딩을 순서대로 시도해서 파일을 읽고, 객실 등급별 생존율을 그래프로 그립니다.")

CSV_PATH = os.path.join(os.path.dirname(__file__), "titanic_cleaned.csv")
FONT_PATH = os.path.join(os.path.dirname(__file__), "GmarketSansTTFMedium.ttf")

import pandas as pd

def read_csv_with_auto_encoding(file_path, **kwargs):
    encodings = ["utf-8-sig", "cp949", "euc-kr"]
    
    for encoding in encodings:
        try:
            # kwargs를 통해 pd.read_csv의 다른 파라미터(예: sep, header 등)를 그대로 전달
            df = pd.read_csv(file_path, encoding=encoding, **kwargs)
            print(f"성공적으로 불러왔습니다. 사용된 인코딩: {encoding}")
            return df
        except UnicodeDecodeError:
            # 인코딩 에러가 발생하면 다음 인코딩으로 넘어감
            continue
        except Exception as e:
            # 인코딩 외의 다른 에러(예: 파일 없음 등)가 발생하면 즉시 중단
            print(f"파일을 읽는 중 에러가 발생했습니다: {e}")
            raise e
            
    # 모든 인코딩 시도가 실패했을 경우 에러 발생
    raise ValueError(f"지원하는 인코딩({encodings})으로 파일을 읽을 수 없습니다. 파일의 실제 인코딩을 확인해주세요.")



# 인코딩 자동 감지로 CSV 읽기
st.subheader("1) 인코딩 자동 감지")
df = read_csv_with_auto_encoding(CSV_PATH)

st.markdown("---")
# 객실등급(Pclass)별 생존율 집계
# Survived 사망0 / 생존1 등급별 평균을 내면
# 그대로가 등급의 생존 비율이 된다
# 10명 남 3 여자 7
# 1000 생존 300 300/1000 30%

pclass_survival_rate = df.groupby("Pclass")["Survived"].mean().sort_index()
st.dataframe( (pclass_survival_rate * 100).round(1).rename("생존율(%)") )

# df_df = st.dataframe( (pclass_survival_rate * 100).round(1).rename("생존율(%)") )
# st.write(df_df)

# 차트 그리기

st.markdown("---")
st.subheader("3) 객실등급별 생존율 막대그래프")
try : 
    # 폰트 파일이 없으면 FileNotFoundError가 발생
    font_prop = font_manager.FontProperties(fname=FONT_PATH)
    # matplotlib font_manager에 폰트를 등록
    font_manager.fontManager.addfont(FONT_PATH)
    
    # [추가할 부분] 등록한 폰트를 Matplotlib 전역 기본 폰트로 설정
    plt.rcParams['font.family'] = font_prop.get_name()
    plt.rcParams['axes.unicode_minus'] = False # 마이너스 폰트 깨짐 방지
    
    st.write("GmarketSansTTFMedium 폰트를 적용")
except FileNotFoundError:
    st.warning("GmarketSansTTFMedium 폰트 파일을 찾을 수가 없습니다.")
except FileNotFoundError:
    st.warning("GmarketSansTTFMedium 폰트 파일을 찾을 수가 없습니다.")

fig, ax = plt.subplots(figsize=(8,5))
(pclass_survival_rate * 100).plot(kind="bar", color= "#AFEEEE", ax=ax )
ax.set_title("객실 등급별 생존율")
ax.set_xlabel("객실등급(Pclass)")
ax.set_ylabel("생존율(%)")

st.pyplot(fig)
output_png = os.path.join(os.path.dirname(__file__), "chart.png")
fig.savefig(output_png)


