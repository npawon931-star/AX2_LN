# 나라별 여행 안내

대한민국이 기본 홈인 Streamlit 앱입니다. 사이드바에서 중국·일본·미국으로 전환하면 국가 정보, 대표 여행지, 여행 사이트 버튼이 표시됩니다.

## 실행

PowerShell에서 프로젝트 폴더로 이동한 뒤 실행하세요.

```powershell
cd C:\Users\user\AX2_LN\Travel-tutorial\step05
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## 폴더 구조

- app.py: 앱 실행 및 국가 선택 메뉴
- .streamlit/config.toml: Streamlit 테마 및 실행 설정
- assets/: 로고 등 공통 이미지와 정적 파일 보관
- src/data/countries.py: 국가 정보와 여행 사이트 링크
- src/components/country_view.py: 국가 상세 화면
- src/utils/images.py: 이미지 파일 탐색
- src/images/korea/: 대한민국 사진
- src/images/china/: 중국 사진
- src/images/japan/: 일본 사진
- src/images/usa/: 미국 사진

## 이미지 추가

국가별 폴더에 JPG, JPEG, PNG, WEBP 파일을 넣으세요.
cover.jpg 또는 cover.png처럼 파일 이름을 cover로 지정하면 대표 사진으로 먼저 표시합니다.
나머지 사진은 파일명 순서대로 갤러리에 표시됩니다.
사진이 없어도 앱을 실행할 수 있습니다. 사진을 추가한 뒤 화면을 새로고침하세요.
assets 폴더는 공통 자료 보관용이며 국가 사진은 src/images에서 불러옵니다.

## 여행 사이트

- [대한민국 구석구석](https://korean.visitkorea.or.kr/main/cr_main.do)
- [Travel China](https://www.travelchina.org.cn/en/channel/Travel_Guide)
- [Travel Japan](https://www.japan.travel/en/)
- [Visit the USA](https://www.visittheusa.com/)

링크 버튼은 새 탭으로 연결됩니다.
