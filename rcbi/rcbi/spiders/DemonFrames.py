# -*- coding: utf-8 -*-
import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

import urllib
import urlparse

MANUFACTURERS = []
CORRECT = {"DEMON": "Demon Frames"}
MANUFACTURERS.extend(CORRECT.keys())
QUANTITY = {u"PACK OF 10 – ": 10}
STOCK_STATE_MAP = {"http://schema.org/InStock": "in_stock",
                   "http://schema.org/OutOfStock": "out_of_stock"}
class DemonFramesSpider(CrawlSpider):
  name = "demonframes"
  allowed_domains = ["demonframes.com"]
  start_urls = ["http://demonframes.com"]

  rules = (
      Rule(LinkExtractor(restrict_css=["#primary-nav", ".page-numbers"])),
      Rule(LinkExtractor(restrict_css=".product", deny=".*add-to-cart.*"), callback='parse_item'),
  )

  def parse_item(self, response):
    item = Part()
    item["site"] = self.name
    product_name = response.css("[itemprop='name']")
    if not product_name:
      return
    item["name"] = product_name[0].xpath("text()").extract()[0].strip()

    variant = {}
    item["variants"] = [variant]
    variant["url"] = response.url

    price = response.css("[itemprop=\"price\"]::attr(content)")
    if price:
      variant["price"] = "${:.2f}".format(float(price.extract_first()))

    for quantity in QUANTITY:
      if quantity in item["name"]:
        variant["quantity"] = QUANTITY[quantity]
        item["name"] = item["name"].replace(quantity, "").strip()

    availability = response.css("[itemprop=\"availability\"]::attr(href)").extract_first()
    if availability:
      variant["stock_state"] = STOCK_STATE_MAP[availability]
      text = response.css("p.stock::text")
      if text:
        variant["stock_text"] = text.extract_first()

    for m in MANUFACTURERS:
      if item["name"].startswith(m):
        item["name"] = item["name"][len(m):].strip("- ")
        item["manufacturer"] = m
        break
      elif item["name"].endswith(m):
        item["name"] = item["name"][:-len(m)].strip("- ")
        item["manufacturer"] = m
        break
    if "manufacturer" in item:
      m = item["manufacturer"]
      if m in CORRECT:
        item["manufacturer"] = CORRECT[m]
    return item
