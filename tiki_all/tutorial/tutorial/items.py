# Define here the models for your scraped items
#
# See documentation in=
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TutorialItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class TikiItem(scrapy.Item):
    Product_id = scrapy.Field()
    Name = scrapy.Field()
    Rating = scrapy.Field()
    Sold_nbr = scrapy.Field()
    Price = scrapy.Field()
    Main_category = scrapy.Field()
    Sub_category = scrapy.Field()
    Day_ago_created = scrapy.Field()
    URL = scrapy.Field()
    Short_description = scrapy.Field()
    Description = scrapy.Field()