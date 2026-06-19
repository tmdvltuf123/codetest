import os
from pathlib import Path
import re

import pandas as pd
import requests


BASE_DIR = Path(__file__).resolve().parent
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TARGET_COUNT = 100

TMDB_DISCOVER_URL = "https://api.themoviedb.org/3/discover/movie"
TMDB_GENRE_URL = "https://api.themoviedb.org/3/genre/movie/list"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
TITLE_PATTERN = re.compile(r"^[A-Za-z0-9가-힣\s\-:,.!?\'\"()&/]+$")


def load_tmdb_api_key():
    api_key = os.getenv("TMDB_API_KEY")
    if api_key:
        return api_key

    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return None

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() == "TMDB_API_KEY":
            return value.strip().strip('"').strip("'")

    return None


def get_genre_map(language="ko-KR"):
    params = {
        "api_key": TMDB_API_KEY,
        "language": language,
    }
    response = requests.get(TMDB_GENRE_URL, params=params, timeout=20)
    response.raise_for_status()

    genre_map = {}
    for genre in response.json().get("genres", []):
        genre_id = genre.get("id")
        if genre_id is not None:
            genre_map[genre_id] = genre.get("name", "기타")
    return genre_map


def get_tmdb_movies(target_count=TARGET_COUNT, language="ko-KR"):
    if not TMDB_API_KEY:
        raise ValueError("TMDB_API_KEY 환경변수를 설정해주세요.")

    genre_map = get_genre_map(language=language)
    all_movies = []
    seen_ids = set()
    page = 1

    while len(all_movies) < target_count and page <= 500:
        params = {
            "api_key": TMDB_API_KEY,
            "language": language,
            "sort_by": "popularity.desc",
            "include_adult": "false",
            "include_video": "false",
            "page": page,
        }

        response = requests.get(TMDB_DISCOVER_URL, params=params, timeout=20)
        response.raise_for_status()
        results = response.json().get("results", [])

        if not results:
            break

        for item in results:
            movie_id = item.get("id")
            if movie_id in seen_ids:
                continue

            title = item.get("title") or "제목 없음"
            if not TITLE_PATTERN.match(title):
                continue

            seen_ids.add(movie_id)

            release_date = str(item.get("release_date") or "")
            year = int(release_date[:4]) if len(release_date) >= 4 and release_date[:4].isdigit() else 0

            genre_names = [genre_map.get(genre_id, "기타") for genre_id in item.get("genre_ids", [])]
            genre = ", ".join(genre_names) if genre_names else "기타"

            vote_average = float(item.get("vote_average") or 0)
            popularity = float(item.get("popularity") or 0)
            poster_path = item.get("poster_path") or ""
            poster_url = f"{TMDB_IMAGE_BASE_URL}{poster_path}" if poster_path else ""
            overview = str(item.get("overview") or "").strip()

            all_movies.append(
                {
                    "title": title,
                    "genre": genre,
                    "year": year,
                    "score": round(vote_average, 1),
                    "salesPoint": int(popularity * 1000),
                    "posterUrl": poster_url,
                    "overview": overview,
                }
            )
        
        page += 1

    return pd.DataFrame(all_movies)


def main():
    global TMDB_API_KEY

    TMDB_API_KEY = load_tmdb_api_key()
    if not TMDB_API_KEY:
        raise ValueError(
            "TMDB_API_KEY가 없습니다. PowerShell에서 $env:TMDB_API_KEY='키값' 설정 또는 .env 파일에 TMDB_API_KEY=키값을 추가해주세요."
        )

    df = get_tmdb_movies()
    output_path = BASE_DIR / "movie_data.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"--- 영화 데이터 수집 완료: {output_path} ---")


if __name__ == "__main__":
    main()