# Distributed-Scraper

## Introduction
In this repository, we create a Distributed scraper system to scrape product details in Tiki. 

We apply Multiprocessing, Distributed system with Scrapy and Redis to optimize scraping time, and also make it easy to scale your scraper.

## Workflow
The first thing we need to do is extract all tags for products on Tki. Then we need to loop through all pages and get the product IDs. Once we have product IDs, we will use Scrapy to scrape product data.
Basically, this is how we work:

![alt text](https://github.com/VQHieu1012/Distributed-Scraper/blob/main/workflow.png)

## System design
`Extract tags` - this step is pretty fast and we don't need to optimize it. 

`Loop through all pages to get all product IDs` - the most time-consuming -> we need to concurrent this task using Multiprocessing.

`Get product data` - time-consuming -> we need to scrape huge amounts of products but this step is easy to create distributed instances.

![alt text](https://github.com/VQHieu1012/Distributed-Scraper/blob/main/system.png)

## How to run
* Clone this code repository
* Install requirements
* You can modify scraper logic for your own purpose
* We set `max_idle_time = 10 * 60` in scraper. If there is no URL in Redis, our scraper will wait for `10 * 60 s` before it auto shuts down
* You can run `add_urls_to_redis.py` (default: 2 workers) and activate your scrapers (Multiple Scrapy Instance) simultaneously (because our scrapers will wait for `10 * 60 s` before shuts down), this makes the scraping process less time-consuming
* All scraped data is stored in Redis

Note: if you run all these processes on your local machine, make sure your machine is good enough to handle it, if not, it can lead to `playwright._impl._errors.Error: Page crashed`. We recommend you run all processes simultaneously but on different machines for better performance.

All components can be deployed in different machines or VMWare. We recommend you modify code by applying `Celery` in the system for better performance, scalability, and flexibility.
