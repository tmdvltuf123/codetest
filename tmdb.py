import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

# 장르 ID 매핑 (TMDB 기본 장르)
GENRE_MAP = {
    28: "액션", 12: "모험", 16: "애니메이션", 35: "코미디", 80: "범죄", 
    18: "드라마", 10751: "가족", 14: "판타지", 27: "공포", 10402: "음악", 
    9648: "미스터리", 10749: "로맨스", 878: "SF", 53: "스릴러", 37: "서부"
}

def get_director(movie_id):
    """영화 상세 API를 호출하여 감독 이름을 가져오는 함수"""
    url = f"{BASE_URL}/movie/{movie_id}/credits"
    params = {"api_key": TMDB_API_KEY, "language": "ko-KR"}
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        for crew in data.get("crew", []):
            if crew.get("job") == "Director":
                return crew.get("name")
    except Exception as e:
        print(f"감독 정보 조회 실패: {e}")
    return "감독 정보 없음"

def get_popular_movies():
    all_movies = []
    url = f"{BASE_URL}/movie/popular"
    params = {"api_key": TMDB_API_KEY, "language": "ko-KR", "page": 1}
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"영화 목록 호출 실패: {response.status_code}")
        return pd.DataFrame()

    movies = response.json().get("results", [])
    
    print(f"🎬 {len(movies)}개의 영화 데이터 수집을 시작합니다...")
    
    for movie in movies:
        movie_id = movie.get("id")
        
        # 1. 감독 정보 가져오기
        director = get_director(movie_id)
        
        # 2. 첫 번째 장르 ID를 장르명으로 변환
        genre_ids = movie.get("genre_ids", [])
        genre_name = GENRE_MAP.get(genre_ids[0], "기타") if genre_ids else "기타"
        
        all_movies.append({
            "title": movie.get("title"),
            "artist": director,
            "year": int(movie.get("release_date", "2000-01-01")[:4]),
            "score": movie.get("vote_average", 0),
            "category": "movie",
            "genre": genre_name,
            "salesPoint": int(movie.get("popularity", 0) * 100) # 인기도 기반 판매지수
        })
        time.sleep(0.5) # API 호출 제한 방지
        
    return pd.DataFrame(all_movies)

# 실행 및 저장
if __name__ == "__main__":
    df = get_popular_movies()
    if not df.empty:
        df.to_csv("movie_data.csv", index=False, encoding='utf-8-sig')
        print("--- ✅ movie_data.csv 파일 생성 완료! ---")
    else:
        print("--- ❌ 수집된 데이터가 없습니다. ---")