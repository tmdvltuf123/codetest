import requests
import pandas as pd

url = "https://rss.applemarketingtools.com/api/v2/kr/music/most-played/10/songs.json"
response = requests.get(url)

if response.status_code != 200 :
 return "데이터를 가져오는 데 실패했습니다."  