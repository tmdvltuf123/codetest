import requests
import os
import pandas as pd
import time  
from dotenv import load_dotenv

load_dotenv()
ALADIN_OPEN_API_KEY = os.getenv("ALADIN_OPEN_API_KEY")

def get_aladin_bestseller():
    url = "https://www.aladin.co.kr/ttb/api/ItemList.aspx"
    book_list = []
    
    
    for i in range(3):
        start_index = (i * 100) + 1
        params = {
            "ttbkey": ALADIN_OPEN_API_KEY,
            "QueryType": "BestSeller",
            "SearchTarget": "Book",
            "MaxResults": 100,  
            "start": start_index, 
            "output": "js",
            "Version": "20131101"
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
       
        for item in data.get("item", []):
            book_list.append({
                "title": item.get("title"),
                "artist": item.get("author"),
                "year": item.get("pubDate", "")[:4],
                "score": item.get("customerReviewRank"),
                "category": "book",
                "keywords": ""
            })
        
        
        time.sleep(0.5)
    
    return pd.DataFrame(book_list)


df_books = get_aladin_bestseller()
df_books.to_csv("book_data.csv", index=False, encoding='utf-8-sig')
print(f"--- 총 {len(df_books)}개의 데이터를 성공적으로 저장했습니다! ---")
print(df_books.head()) 