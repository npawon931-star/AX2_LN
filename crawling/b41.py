from bs4 import BeautifulSoup
import requests 
import pandas as pd
import openpyxl 

data = []

for i in range (1, 5): 
    response = requests.get(f"https://startcoding.pythonanywhere.com/basic?page={i}")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    items = soup.select(".product")

    # print(f"가져온 상품 개수: {len(items)}개 \n"+"-"*30) # 상품 개수 확인

    for item in items:
        category = item.select_one(".product-category").text # .strip()으로 공백 제거
        category_name = item.select_one(".product-name").text
        category_link = item.select_one(".product-name > a").attrs["href"] # ['href']로 수정
        price = item.select_one(".product-price").text.split("원")[0].replace(",","") #가격
        data.append([category, category_name, category_link, price])
        print(category, category_name, category_link, price)

df = pd.DataFrame(data, columns=["카테고리", "상품명", "상세페이지링크", "가격"])
df.to_excel("data.xlsx", index=False)
