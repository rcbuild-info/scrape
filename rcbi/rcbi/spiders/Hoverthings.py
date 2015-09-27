import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

import urllib
import urlparse

MANUFACTURERS = ["Gemfan"]
CORRECT = {"HQ Prop": "HQProp"}
MANUFACTURERS.extend(CORRECT.keys())
QUANTITY = {}
STOCK_STATE_MAP = {"http://schema.org/InStock": "in_stock",
                   "http://schema.org/OutOfStock": "out_of_stock"}
class HoverthingsSpider(CrawlSpider):
    name = "hoverthings"
    allowed_domains = ["hoverthings.com"]
    start_urls = ["http://hoverthings.com"]

    rules = (
        Rule(LinkExtractor(restrict_css=[".nav-primary", ".pages"])),

        Rule(LinkExtractor(restrict_css=".product-name"), callback='parse_item'),
    )

    def parse_item(self, response):
      item = Part()
      item["site"] = self.name
      product_name = response.css(".product-name span")
      if not product_name:
          return
      item["name"] = product_name[0].css("::text").extract_first().strip()

      variant = {}
      variant["timestamp"] = response.headers["Date"]
      item["variants"] = [variant]
      variant["url"] = response.url

      price = response.css("[itemprop=\"price\"]::text")
      if price:
        variant["price"] = price.extract_first().strip()

      availability = response.css("[itemprop=\"availability\"]::attr(href)")
      if availability:
        text = availability.extract_first().strip()
        if text in STOCK_STATE_MAP:
          variant["stock_state"] = STOCK_STATE_MAP[text]
        else:
          print(text)

      for quantity in QUANTITY:
        if quantity in item["name"]:
          variant["quantity"] = QUANTITY[quantity]
          item["name"] = item["name"].replace(quantity, "")

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
