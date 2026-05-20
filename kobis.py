import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time
import os

load_dotenv()
KOBIS_API_KEY = os.getenv("KOBIS_API_KEY")

# 1. 영화별 상세 정보(감독, 장르)를 가져오는 함수
def get_movie_detail(movie_cd):
    url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieInfo.json"
    params = {"key": KOBIS_API_KEY, "movieCd": movie_cd}
    try:
        res = requests.get(url, params=params).json()
        info = res['movieInfoResult']['movieInfo']
        
        directors = info.get('directors', [])
        director = directors[0]['peopleNm'] if directors else "감독 정보 없음"
        
        genres = info.get('genres', [])
        genre = genres[0]['genreNm'] if genres else "기타"
        
        return director, genre
    except:
        return "정보 없음", "기타"

# 2. 메인 수집 함수
def get_kobis_movies():
    target_dt = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {"key": KOBIS_API_KEY, "targetDt": target_dt}
    
    response = requests.get(url, params=params)
    data = response.json()
    
    # 서버 응답 검증
    if 'boxOfficeResult' not in data:
        print("에러 발생! 서버 응답:")
        print(data)
        return pd.DataFrame()
        
    items = data['boxOfficeResult']['dailyBoxOfficeList']
    
    all_movies = []
    for item in items:
        director, genre = get_movie_detail(item['movieCd'])
        
        all_movies.append({
            "title": item['movieNm'],
            "artist": director,
            "year": int(item.get("openDt", "2000-01-01")[:4]),
            "score": float(item['audiAcc']) / 100000,
            "category": "movie",
            "genre": genre,
            "popularity_score": float(item['audiAcc']) / 10000,
            "salesPoint": float(item['salesAcc']) / 1000000
        })
        time.sleep(0.2)
        print(f"수집 완료: {item['movieNm']}")
        
    return pd.DataFrame(all_movies)

# 실행
df = get_kobis_movies()
if not df.empty:
    df.to_csv("movie_data.csv", index=False, encoding='utf-8-sig')
    print("--- movie_data.csv 저장 완료! ---")
else:
    print("--- 수집된 데이터가 없어 파일을 만들지 못했습니다. ---")