# Distributed-Scraper

## Introduction
In this repository, we create a Distributed scraper system. 
We apply Multiprocessing, Distributed system with Scrapy and Redis to optimize scraping time, CPU and memory usage.

## Workflow
First thing we need to do is extract all tags for products in web. Then we need to loop through all page product and get ID product. Once we get ID product, we will use scrapy to crape product data.
Basically this is how we work:

![alt text](https://github.com/VQHieu1012/Distributed-Scraper/blob/main/workflow.png)

## System design
`Extract tags` - this step is pretty fast and we don't need to optimize it. 

`Loop through all pages to get all product IDs` - the most time consuming -> we need to concurrent this task using Multiprocessing.

`Get product data` - time consuming -> we need to scrape huge amount of products but this step is easy to create distributed instance.

![alt text](https://github.com/VQHieu1012/Distributed-Scraper/blob/main/system.png)

All components can be deployed in different machine or VMWare. We recommend you to modify code by applying `Celery` in system for better performance, scalability and flexibility.
