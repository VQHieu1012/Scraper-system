import redis
from playwright.sync_api import sync_playwright
from playwright_stealth.stealth import stealth_sync
import requests
import re
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup as bs
import random
import os
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

    Return: list of product ids
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

    ids = list(set(ids))
    return ids


# Use playwright to render javascript 
def extract_product_id(tags):
    """
    Load through all pages and push product links to Redis

    tags: list of tag links

    Return: None
    """
    
    CHROMIUM_ARGS = [
        '--disable-blink-features=AutomationControlled',
        "--disable-images"
    ]
    redisClient = redis.from_url(os.getenv('redis_url_connection'))

    with sync_playwright() as p:
        
        browser = p.chromium.launch(channel='chrome', headless=False, slow_mo=200, args=CHROMIUM_ARGS, ignore_default_args=['--enable-automation'])
        page = browser.new_page()
        
        stealth_sync(page)

        for tag in tags:
            page_num = 1
            retry = True
            while True:
                page.goto(tag + '?page=' + str(page_num))
                
                page.wait_for_timeout(600)

                # Sometime we need to scroll down to render JS
                page.evaluate(f"window.scrollTo(0, 1500);")
                page.wait_for_timeout(random.randint(1500, 2000))
                # ---------------------------------

                ids = extract_ids(page.content())

                print(f"{tag}?page={page_num} \t {len(ids)}")

                if len(ids) != 0:
                    for id in ids:
                        redisClient.lpush('tiki_queue:start_urls', f"https://tiki.vn/api/v2/products/{id}")    
                    page_num += 1
                    retry = True
                else:
                    if retry:
                        retry = False
                        continue
                    else:
                        print(f"Finish {tag}?page={page_num} \t {len(ids)}")
                        break

def distribute_elements(lst, l):
    """
    Distribute tags to 'number of workers' list with approximate elements

    lst: list       -> list of tags need to be distributed
    l: int          -> number of workers

    Return: a list of lists with approximate elements
    """
    n = len(lst)
    min_size = n // l
    remainder = n % l
    
    result = []
    start_index = 0
    
    for i in range(l):
        end_index = start_index + min_size + (1 if i < remainder else 0)
        result.append(lst[start_index:end_index])
        start_index = end_index
        
    return result

def parallel_worker(num_workers, tags):
    """
    Create num_workers to work in parallel

    num_workers: int -> number of workers
    tags: list       -> list of tag links

    Return: None
    """
    all_tags = distribute_elements(tags, num_workers)
    print(all_tags)
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        executor.map(extract_product_id, all_tags)


# Driver code
if __name__ == "__main__":
    load_dotenv()    
    
    tags = get_tags()
    print(tags[:2])

    parallel_worker(2, tags[:2])


    

