import requests
import pandas as pd
import os
import time
from dotenv import load_dotenv

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")


genre_targets = {
    '액션': '28',
    '드라마': '18',
    '코미디': '35',
    '스릴러': '53', 
    '로맨스': '10749', 
    'SF': '878', 
    '애니메이션': '16'
}

def get_tmdb_movies():
    all_movies = []
    base_url = "https://api.themoviedb.org/3/discover/movie"
    headers = {"Authorization": f"Bearer {TMDB_API_KEY}"}
    
    print("데이터 수집을 시작합니다. 잠시만 기다려주세요...")
    
    for genre_name, genre_id in genre_targets.items():
        # 페이지를 1로 설정 (페이지를 늘리면 더 많은 영화 수집 가능)
        params = {
            "language": "ko-KR", 
            "with_genres": genre_id, 
            "sort_by": "popularity.desc",
            "page": 1 
        }
        
        response = requests.get(base_url, headers=headers, params=params)
        movies = response.json().get("results", [])
        
        print(f"[{genre_name}] 수집 중 ({len(movies)}개)...")
        
        for movie in movies:
            movie_id = movie.get("id")
            detail_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
            detail_params = {"language": "ko-KR", "append_to_response": "credits"}
            
            detail = requests.get(detail_url, headers=headers, params=detail_params).json()
            
            directors = [c['name'] for c in detail.get('credits', {}).get('crew', []) if c['job'] == 'Director']
            director = directors[0] if directors else "감독 정보 없음"
            
            all_movies.append({
                "title": movie.get("title"),
                "artist": director,
                "year": int(movie.get("release_date", "2000-01-01")[:4]),
                "score": movie.get("vote_average", 0),
                "category": "movie",
                "genre": genre_name,
                "salesPoint": movie.get("popularity", 0)
            })
          
            time.sleep(0.1) 
            
    return pd.DataFrame(all_movies)

if __name__ == "__main__":
    df = get_tmdb_movies()
    df.to_csv("movie_data.csv", index=False, encoding='utf-8-sig')
    print("\n--- [완료] movie_data.csv가 생성되었습니다 ---")