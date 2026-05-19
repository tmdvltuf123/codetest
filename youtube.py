import requests
import os
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

music_item_list_url = "https://www.googleapis.com/youtube/v3/videos"
music_item_list_params = {
    "key": YOUTUBE_API_KEY,
    "part": "snippet",               
    "chart": "mostPopular",          
    "videoCategoryId": "10",   
    "regionCode": "KR",      
    "maxResults": 10                 
}

response = requests.get(url=music_item_list_url, params=music_item_list_params)
print(response.text)