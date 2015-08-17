# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Part(scrapy.Item):
    url = scrapy.Field()
    name = scrapy.Field()
    site = scrapy.Field()
    manufacturer = scrapy.Field()
    weight = scrapy.Field()
    price = scrapy.Field()
