import redis
from playwright.sync_api import sync_playwright
from playwright_stealth.stealth import stealth_sync
import requests
import re
import multiprocessing
from bs4 import BeautifulSoup as bs
import random
import os
from dotenv import load_dotenv


def get_tags():
    """
    Load all tag product links in tiki
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

    s = requests.Session()
    r = s.get('https://tiki.vn/dien-thoai-may-tinh-bang/c1789',  cookies=cookies, headers=headers)
    soup = bs(r.text, 'html.parser') 
    danh_muc = soup.find('div', class_ = 'styles__StyledColumns-sc-17y817k-2 gteCFh')
    p_tag =danh_muc.findAll('p')
    all_a_tag = []
    for p in p_tag:
        all_a_tag.extend(p.findAll('a'))
    links = [i.get('href') for i in all_a_tag]
    return links

def extract_ids(string):
    """
    Extract product ID and push to Redis

    string: -> str: page content
    """
    ids = []
    soup = bs(string, 'html.parser')
    a_tags = soup.find_all('a', {'data-view-id': 'product_list_item'})
    for a in a_tags:
        id = a.get('data-view-content')
        pattern = r'"id":(\d+)'
        match = re.search(pattern, id)
        if match:
            id_value = match.group(1)
            ids.append(id_value)
        else:
            pass
    ids = list(set(ids))
    return ids

def block(route):
    """
    Block images and media file for better bandwidth
    """
    if route.request.resource_type in ["image", "media"]: # "stylesheet"
        route.abort()
    elif ".mp4" in route.request.url:
        route.abort()
    else:
        route.continue_()


# Use playwright to render javascript 
def extract_product_id(tags):
    
    CHROMIUM_ARGS = [
        '--disable-blink-features=AutomationControlled',
        "--disable-images"
    ]
    redisClient = redis.from_url(os.getenv('redis_url_connection'))

    with sync_playwright() as p:
        
        browser = p.firefox.launch(headless=False, slow_mo=200, args=CHROMIUM_ARGS, ignore_default_args=['--enable-automation'])
        page = browser.new_page()
        
        stealth_sync(page)
        page.route("**/*", block)  

        for tag in tags:
            page_num = 1
            while True:
                page.goto(tag + '?page=' + str(page_num))
                print(tag + '?page=' + str(page_num))
                page.wait_for_timeout(random.randint(1000, 1500))

                ids = extract_ids(page.content())
                for id in ids:
                    redisClient.lpush('tiki_queue:start_urls', f"https://tiki.vn/api/v2/products/{id}")    
                
                if page.locator('//div[@class="style__StyledNotFoundProductView-sc-1uz0b49-0 iSZIiE"]').is_visible():
                    print('Fnish')
                    break
                else: 
                    page_num += 1

def parallel_worker(workers, tags):
    tags_each_list = len(tags) // workers
    tags_1 = tags[:tags_each_list]
    tags_2 = tags[tags_each_list:]
    all_tags = [tags_1, tags_2]
    num_workers = 2

    # Apply extract_product_id for each tag và run using pool.map
    with multiprocessing.Pool(num_workers) as pool:
        pool.map(extract_product_id, all_tags)

   
if __name__ == "__main__":
    load_dotenv()    
    
    # Create a redis client
    tags = get_tags()
    print(tags[:5])
    
    parallel_worker(2, tags[:5])
    

