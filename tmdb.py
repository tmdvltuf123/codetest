import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

import requests

url = "https://api.themoviedb.org/3/movie/popular"

headers = {
    "accept": "application/json",
    "Authorization": "Bearer " + TMDB_API_KEY
}

response = requests.get(url, headers=headers)

print(response.text)