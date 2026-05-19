import requests

music_item_list_url = "https://itunes.apple.com/search"


music_item_list_params = {
    "term": "아이유",          
    "country": "KR",        
    "media": "music",       
    "limit": 10,             
    "lang": "ko_kr"          #
}

response = requests.get(url=music_item_list_url, params=music_item_list_params)
print(response.text)