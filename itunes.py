from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

BASE_DIR = Path(__file__).resolve().parent
ITUNES_SEARCH_URL = "https://itunes.apple.com/search"

SEARCH_TERMS = [
    ("KPOP", "kpop"),
    ("발라드", "korean ballad"),
    ("힙합", "korean hiphop"),
    ("록", "korean rock"),
    ("인디", "korean indie"),
]

TARGET_LIMIT = 30
TARGET_COUNTRY = "KR"


def get_itunes_music_data():
    all_tracks = []

    for genre_name, search_term in SEARCH_TERMS:

        params = {
            "term": search_term,
            "media": "music",
            "entity": "song",
            "limit": TARGET_LIMIT,
            "country": TARGET_COUNTRY,
            "lang": "ko_kr",
        }

        response = requests.get(
            ITUNES_SEARCH_URL,
            params=params,
            timeout=20
        )

        response.raise_for_status()
        results = response.json().get("results", [])

        for item in results:

            release_date = str(item.get("releaseDate", ""))
            year = None

            if release_date:
                try:
                    year = datetime.fromisoformat(
                        release_date.replace("Z", "+00:00")
                    ).year
                except ValueError:
                    year = None

            all_tracks.append(
                {
                    "title": item.get("trackName") or "",
                    "artist": item.get("artistName") or "",

                    # 기존 primaryGenreName 대신 직접 지정
                    "genre": genre_name,

                    "year": year,
                    "salesPoint": item.get("trackPrice")
                    or item.get("collectionPrice")
                    or 0,

                    "category": "music",
                    "country": item.get("country") or "",
                    "currency": item.get("currency") or "",
                    "previewUrl": item.get("previewUrl") or "",
                    "artworkUrl": item.get("artworkUrl100") or "",
                    "trackViewUrl": item.get("trackViewUrl") or "",
                }
            )

    return all_tracks


def save_csv(rows):
    output_path = BASE_DIR / "music_data.csv"

    df = pd.DataFrame(rows)

    df.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )


rows = get_itunes_music_data()
save_csv(rows)

print("--- 음악 데이터 수집 완료 ---")
print(f"--- 저장 건수: {len(rows)} ---")