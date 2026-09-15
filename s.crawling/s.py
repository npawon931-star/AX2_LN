import pandas as pd
import requests

def get_naver_stock_sise(code="005930", page=1):
    url = f"https://finance.naver.com/item/sise_day.naver?code={code}&page={page}"
    
    # 봇 차단 방지를 위한 브라우저 헤더 정보
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    df_list = pd.read_html(response.text, encoding='euc-kr')
    df = df_list[0]
    
    # 빈 행 제거
    df = df.dropna()
    return df

def save_stock_to_excel():
    print("🚀 삼성전자 일별 시세 크롤링을 시작합니다...")
    
    # 예시로 최근 5페이지(약 50영업일) 데이터를 가져옵니다. (원하는 만큼 페이지 수 조절 가능)
    max_page = 5
    dfs = []
    
    for p in range(1, max_page + 1):
        print(f"[{p}/{max_page}] 페이지 데이터 수집 중...")
        df_page = get_naver_stock_sise("005930", p)
        dfs.append(df_page)
        
    # 데이터 합치기
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # 결측치(날짜 없는 행 등) 제거
    combined_df = combined_df.dropna(subset=['날짜'])
    
    # 엑셀 파일명 지정
    file_name = "삼성전자_일별시세.xlsx"
    
    # to_excel을 이용해 엑셀 파일로 저장 (index=False는 불필요한 번호 열 제외)
    combined_df.to_excel(file_name, index=False, sheet_name='삼성전자_시세')
    
    print(f"✨ 크롤링 완료! '{file_name}' 파일로 저장되었습니다.")

if __name__ == "__main__":
    save_stock_to_excel()