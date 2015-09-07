import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

import urllib
import urlparse

MANUFACTURERS = ["Pololu"]
CORRECT = {"GemFan": "Gemfan"}
MANUFACTURERS.extend(CORRECT.keys())
QUANTITY = {" 8 pack": 8}
class LizardRCSpider(CrawlSpider):
    name = "lizardrc"
    allowed_domains = ["lizard-rc.se"]
    start_urls = ["http://lizard-rc.se"]

    rules = (
        Rule(LinkExtractor(restrict_css=["#menu-wrap", ".pagination", ".categories_box"])),

        Rule(LinkExtractor(restrict_css=".ajax_block_product"), callback='parse_item'),
    )

    def parse_item(self, response):
      item = Part()
      item["site"] = self.name
      item["url"] = response.url
      product_name = response.css("#pb-left-column h1")
      if not product_name:
          return
      item["name"] = product_name[0].xpath("text()").extract()[0].strip()

      price = response.css("#our_price_display")
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
