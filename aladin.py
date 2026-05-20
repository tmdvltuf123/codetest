import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv

load_dotenv()
ALADIN_OPEN_API_KEY = os.getenv("ALADIN_OPEN_API_KEY")

genre_targets = {
    '소설': '1',
    '경제/경영': '170',
    '인문': '656', 
    '사회': '798',
    '과학': '987',
    'IT/컴퓨터': '351',
    '자기계발': '336'
}

def get_balanced_bestseller():
    all_books = []
    url = "https://www.aladin.co.kr/ttb/api/ItemList.aspx"
    
    for genre_name, cid in genre_targets.items():
        params = {
            "ttbkey": ALADIN_OPEN_API_KEY,
            "QueryType": "BestSeller",
            "SearchTarget": "Book",
            "CategoryId": cid,
            "MaxResults": 28,
            "start": 1,
            "output": "js",
            "Version": "20131101"
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        items = data.get("item", [])
        
        for item in items:
            all_books.append({
                "title": item.get("title"),
                "artist": item.get("author"),
                "year": int(item.get("pubDate", "2000")[:4]),
                
                "score": item.get("customerReviewRank", 0) / 2 if item.get("customerReviewRank", 0) > 5 else item.get("customerReviewRank", 0),
                "category": "book",
                "genre": genre_name,
                "salesPoint": item.get("salesPoint", 0) # 판매지수 추가!
            })
        time.sleep(1) 
        
    return pd.DataFrame(all_books)


df = get_balanced_bestseller()
df.to_csv("book_data.csv", index=False, encoding='utf-8-sig')
print("--- 데이터 수집 및 판매지수 포함 저장 완료 ---")