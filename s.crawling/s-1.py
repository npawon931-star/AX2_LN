import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def crawl_naver_stock_page():
    print("🚀 신형 네이버페이 증권 페이지 접속 중 (Selenium)...")
    
    # 크롬 옵션 설정 (필요시 headless 추가 가능)
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") # 브라우저 창을 띄우지 않고 하려면 주석 해제
    
    # WebDriver 자동 세팅 및 실행
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # 사용자가 지정하신 신형 페이지 접속
        url = "https://stock.naver.com/domestic/stock/005930/price"
        driver.get(url)
        
        # 페이지가 완전히 로딩되고 자바스크립트가 표를 그릴 때까지 대기 (여유 있게 3~5초)
        print("⏳ 데이터 로딩 대기 중...")
        time.sleep(4)
        
        # 해당 페이지의 테이블 태그 또는 데이터 영역 찾기
        # 신형 페이지의 표 구조를 파악하여 데이터를 수집합니다.
        tables = driver.find_elements(By.TAG_NAME, "table")
        
        if not tables:
            print("❌ 페이지에서 테이블을 찾지 못했습니다.")
            return

        # 페이지에 있는 테이블 중 일별 시세에 해당하는 요소를 pandas로 읽어오기 위해 HTML 소스 파싱
        # 또는 셀레니움으로 직접 표의 <tr>, <td>를 파싱합니다.
        print("📊 테이블 데이터를 추출하는 중...")
        
        # 첫 번째 테이블 또는 일별 시세 표 타겟팅
        target_table = tables[0] 
        html_content = target_table.get_attribute('outerHTML')
        
        # pandas로 HTML 테이블 변환
        df_list = pd.read_html(html_content)
        df = df_list[0]
        
        # 엑셀로 저장
        file_name = "삼성전자_신형페이지_일별시세.xlsx"
        df.to_excel(file_name, index=False, sheet_name='시세_데이터')
        
        print(f"✨ 크롤링 완료! '{file_name}' 파일로 저장되었습니다.")
        
    except Exception as e:
        print(f"❌ 크롤링 중 오류 발생: {e}")
        
    finally:
        # 브라우저 종료
        driver.quit()

if __name__ == "__main__":
    crawl_naver_stock_page()