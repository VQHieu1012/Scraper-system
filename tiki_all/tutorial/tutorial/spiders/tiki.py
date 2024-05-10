from typing import Iterable
from scrapy_redis.spiders import RedisSpider
from scrapy import FormRequest, version_info as scrapy_version
import re
import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(r"D:\Distributed-scraper\tiki_all\tutorial\tutorial\\")

from pipelines import TutorialPipeline

import json
from scrapy_redis.utils import bytes_to_str, is_dict, TextColor
from tutorial.items import TikiItem
import logging


# Uncomment this to write log file
# logging.basicConfig(
#     filename="log.txt",
#     format="%(asctime)s %(levelname)s: %(message)s",
#     level=logging.DEBUG, encoding='utf-8'
# )


class TikiSpider(RedisSpider):

    name = "tiki"
    allowed_domains = ["tiki.vn"]
    #start_urls = ["https://tiki.vn/api/v2/products/{id}"]


    redis_key = 'tiki_queue:start_urls'
    redis_batch_size = 5
    max_idle_time = 10 * 60

    cookies = {
        'TOKENS': '{%22access_token%22:%22tYnAkieDWjgsyPu8om1Fr9fI2RzJSlZB%22}',
        '_trackity': '247696e2-ac38-c299-7cf4-9333ee075cd5',
        'tiki_client_id': '',
        'delivery_zone': 'Vk4wMzQwMjQwMTM=',
        'TKSESSID': '853c35ae6468ea8abe5fe4d2bdd51005',
        'OTZ': '7419709_28_28__28_',
        'recaptcha-ca-e': 'AVGAUYwgqZkjAcdZ2hkUC-azMzSEIxybwWPfMDSQZxbjGykMQnLe_bD5hT7jyvc0StTMjVwGW-IeM86V1rZhTWnuOy4YFR3h2op2HM3M5UbDjZatnxNmp8uMXBaRPHbWezAlh2L7DQ:U=f57440da40000000',
    }
    

    def make_request_from_data(self, data):
        formatted_data = bytes_to_str(data, self.redis_encoding)

        if is_dict(formatted_data):
            parameter = json.loads(formatted_data)
        else:
            self.logger.warning(f"{TextColor.WARNING} Please use JSON data format. \
                Detail information, please check https://github.com/rmax/scrapy-redis#features{TextColor.ENDC}")
            r = FormRequest(formatted_data, dont_filter=True, cookies=self.cookies)
            return r

        if parameter.get('url', None) is None:
            self.logger.warning(f"{TextColor.WARNING}The data from Redis has no url key in push data{TextColor.ENDC}")
            return []

        url = parameter.pop("url")
        method = parameter.pop("method").upper() if "method" in parameter else "GET"
        metadata = parameter.pop("meta") if "meta" in parameter else {}

        return FormRequest(url, dont_filter=True, method=method, formdata=parameter, meta=metadata)

    
    def parse(self, response):
        self.myPipeline = TutorialPipeline
        
        if response.body == None or response.body == '':
            print('I got a null or empty string value for data in a file')
            
        else:
            data = json.loads(response.body)

            id = data.get("id")
            name = data.get("name")
            url = data.get("short_url")
            rate = float(data.get("rating_average", 0))
            sold = int(data.get("all_time_quantity_sold", 0))
            price = int(data.get("price", 0))
            day_ago_created = float(data.get("day_ago_created", 0))

            hierarchy = data.get("breadcrumbs")
            if len(hierarchy) > 4 and hierarchy[4]["category_id"] == 0:
                main_category = hierarchy[3]["name"]
                sub_category = hierarchy[2]["name"]
            elif len(hierarchy) > 3 and hierarchy[3]["category_id"] == 0:
                main_category = hierarchy[2]["name"]
                sub_category = hierarchy[1]["name"]
            elif len(hierarchy) > 2 and hierarchy[2]["category_id"] == 0:
                main_category = hierarchy[1]["name"]
                sub_category = hierarchy[0]["name"]
            elif hierarchy[1]["category_id"] == 0:
                main_category = hierarchy[0]["name"]
                sub_category = None
            else:
                main_category = None
                sub_category = None

            short_desc = data.get("short_description", "")
            desc = (
                re.sub(r"<[^>]*>", "", data.get("description", ""))
                .replace("\n", " ")
                .replace("\xa0", " ")
            )

            tiki_item = TikiItem()

            tiki_item["Product_id"] = id
            tiki_item["Name"] = name
            tiki_item["Rating"] = rate
            tiki_item["Sold_nbr"] = sold
            tiki_item["Price"] = price
            tiki_item["Main_category"] = main_category
            tiki_item["Sub_category"] = sub_category
            tiki_item["Day_ago_created"] = day_ago_created
            tiki_item["URL"] = url
            tiki_item["Short_description"] = short_desc
            tiki_item["Description"] = desc

            yield tiki_item

