# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Part(scrapy.Item):
    name = scrapy.Field()
    site = scrapy.Field()
    manufacturer = scrapy.Field()
    sku = scrapy.Field()
    weight = scrapy.Field()
    # url, price, quantity, stock, description, location, timestamp
    variants = scrapy.Field()
