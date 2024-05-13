import os
import re
import redis
import random
from dotenv import load_dotenv
from bs4 import BeautifulSoup as bs
from playwright.sync_api import sync_playwright
from playwright_stealth.stealth import stealth_sync
from concurrent.futures import ThreadPoolExecutor


def extract_ids(string):
    """
    Extract product ID and push to Redis

    Parameters:
    ----------
    string: -> str: page content
    ----------

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
def extract_product_id():
    """
    Load through all pages and push product links to Redis

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

        while True:
            tag = redisClient.lpop('tags').decode('utf-8')

            if tag:
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
                            print(f"Retry {tag}?page={page_num} \t {len(ids)}")
                            break
            else:
                print('No more tags')
                break


def parallel_worker(num_workers):
    """
    Create num_workers to work in parallel

    Parameters:
    ----------
    num_workers: int -> number of workers
    ----------

    Return: None
    """
    print(f'Starting up {num_workers} workers...')
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        for _ in range(num_workers):
            executor.submit(extract_product_id)

# Driver code
if __name__ == "__main__":
    load_dotenv()    
    parallel_worker(2)
