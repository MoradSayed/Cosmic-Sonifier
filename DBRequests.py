import requests


api_url = 'https://images-api.nasa.gov/search'

def fetch_images(page=1, searchkeyword='space', result_queue=None):
    try:
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        response = requests.get(f'{api_url}?q={searchkeyword}&page={page}&media_type=image&keywords=space,star,galaxy,supernova', headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()["collection"]["items"] # list of images with respective metadata
        result_queue.put(data)
    except requests.exceptions.RequestException as error:
        print(error)
        result_queue.put(None)

