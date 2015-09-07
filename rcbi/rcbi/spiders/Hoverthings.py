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
      item["url"] = response.url
      product_name = response.css(".product-name span")
      if not product_name:
          return
      item["name"] = product_name[0].xpath("text()").extract()[0].strip()

      price = response.css(".price")
      if price:
        item["price"] = price.xpath("text()").extract()[0].strip()

      for quantity in QUANTITY:
        if quantity in item["name"]:
          item["quantity"] = QUANTITY[quantity]
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
