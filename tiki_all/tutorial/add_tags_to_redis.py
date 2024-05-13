import redis
import os
import requests
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv


def get_tags():
    """
    Load all tag product links in tiki

    Return: list of tag links
    """
    cookies = {
        'TOKENS': '{%22access_token%22:%22tYnAkieDWjgsyPu8om1Fr9fI2RzJSlZB%22}',
        '_trackity': '247696e2-ac38-c299-7cf4-9333ee075cd5',
        'tiki_client_id': '',
        'delivery_zone': 'Vk4wMzQwMjQwMTM=',
    }

    headers = {
        'authority': 'tiki.vn',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'referer': 'https://tiki.vn/dien-thoai-may-tinh-bang/c1789',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Opera";v="106"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0',
        'x-guest-token': 'tYnAkieDWjgsyPu8om1Fr9fI2RzJSlZB',
    }

    # Create redis connection
    redisClient = redis.from_url(os.getenv('redis_url_connection'))

    # Create request session
    s = requests.Session()
    r = s.get('https://tiki.vn/dien-thoai-may-tinh-bang/c1789',  cookies=cookies, headers=headers)

    soup = bs(r.text, 'html.parser') 

    danh_muc = soup.find('div', class_ = 'styles__StyledColumns-sc-17y817k-2 gteCFh')
    p_tag =danh_muc.findAll('p')
    all_a_tag = []
    for p in p_tag:
        all_a_tag.extend(p.findAll('a'))
    links = [i.get('href') for i in all_a_tag]
    
    # Push to redis
    for link in links:
        if 'https://tiki.vn/search' not in link:
            redisClient.lpush('tags', link)

    print('Successfully push tags to Redis')

# Driver code
if __name__ == "__main__":
    load_dotenv()    
    get_tags()