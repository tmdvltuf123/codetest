import requests
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
ALADIN_OPEN_API_KEY = os.getenv("ALADIN_OPEN_API_KEY")

def get_aladin_bestseller():
    url = "https://www.aladin.co.kr/ttb/api/ItemList.aspx"
    params = {
        "ttbkey": ALADIN_OPEN_API_KEY,
        "QueryType": "BestSeller",
        "SearchTarget": "Book",
        "MaxResults": 10, 
        "output": "js",
        "Version": "20131101"
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    book_list = []
    for item in data.get("item", []):
       
        book_list.append({
            "title": item.get("title"),
            "artist": item.get("author"),
            "year": item.get("pubDate", "")[:4], 
            "score": item.get("customerReviewRank"),
            "category": "book",
            "keywords": "" #
        })
    
    return pd.DataFrame(book_list)


df_books = get_aladin_bestseller()
df_books.to_csv("book_data.csv", index=False, encoding='utf-8-sig')
print(df_books)