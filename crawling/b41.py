from bs4 import BeautifulSoup
import requests 
import pandas as pd


response = requests.get("https://www.google.com")

html = response.text
soup = BeautifulSoup(html, "html.parser")

logo = soup.select_one("naW5gc mL3MVc DYz2A").text
subtitle = soup.select_one(".acUsEb.Qi40Vc.CoM3Df").text

print(logo, subtitle)

