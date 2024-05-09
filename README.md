# Distributed-Scraper

## Introduction
In this repository, we create a Distributed scraper system to scrape product details in Tiki. 

We apply Multiprocessing, Distributed system with Scrapy and Redis to optimize scraping time, CPU, and memory usage.

## Workflow
The first thing we need to do is extract all tags for products on Tki. Then we need to loop through all pages and get the product IDs. Once we have product IDs, we will use Scrapy to scrape product data.
Basically, this is how we work:

![alt text](https://github.com/VQHieu1012/Distributed-Scraper/blob/main/workflow.png)

## System design
`Extract tags` - this step is pretty fast and we don't need to optimize it. 

`Loop through all pages to get all product IDs` - the most time-consuming -> we need to concurrent this task using Multiprocessing.

`Get product data` - time-consuming -> we need to scrape huge amounts of products but this step is easy to create distributed instances.

![alt text](https://github.com/VQHieu1012/Distributed-Scraper/blob/main/system.png)

All components can be deployed in different machines or VMWare. We recommend you modify code by applying `Celery` in the system for better performance, scalability, and flexibility.
