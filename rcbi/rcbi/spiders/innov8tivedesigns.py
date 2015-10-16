import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

import os.path
import urllib
import urlparse

MANUFACTURERS = ["APC", "Cobra", "Scorpion", "T-Motor"]
CORRECT = {"GemFan": "Gemfan"}
MANUFACTURERS.extend(CORRECT.keys())
NEW_PREFIX = {}
QUANTITY = {}
STOCK_STATE_MAP = {"in-stock": "in_stock",
                   "out-of-stock": "out_of_stock"}
class Innov8tiveDesignsSpider(CrawlSpider):
  name = "innov8tivedesigns"
  allowed_domains = ["innov8tivedesigns.com"]
  start_urls = ["http://innov8tivedesigns.com"]

  handle_httpstatus_list = [200, 500]

  custom_settings = {#"DOWNLOAD_DELAY": 2,
                     "RETRY_ENABLED": False}

  rules = (
    Rule(LinkExtractor(restrict_css=["#nav", ".pages"])),
    Rule(LinkExtractor(restrict_css=".product-grid"), callback='parse_item'),
  )

  def parse_item(self, response):
    item = Part()
    item["site"] = self.name
    product_name = response.css("#product-overview h1")
    if not product_name:
      return
    item["name"] = product_name[0].xpath("text()").extract()[0].strip()

    variant = {}
    item["variants"] = [variant]


    parsed = urlparse.urlparse(response.url)
    filename = "/" + os.path.basename(parsed[2])
    variant["url"] = urlparse.urlunparse((parsed[0], parsed[1], filename,
                                          parsed[3], parsed[4], parsed[5]))

    price = response.css(".regular-price .price")
    if price:
      variant["price"] = price.xpath("text()").extract()[0].split()[-1]

    for quantity in QUANTITY:
      if quantity in item["name"]:
        variant["quantity"] = QUANTITY[quantity]
        item["name"] = item["name"].replace(quantity, "")

    stock = response.css(".availability")
    if stock:
      stock_class = stock.css("::attr(class)").extract_first().split()[1]
      if stock_class in STOCK_STATE_MAP:
        variant["stock_state"] = STOCK_STATE_MAP[stock_class]
      else:
        print(stock_class)

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
      if m in NEW_PREFIX:
        item["name"] = NEW_PREFIX[m] + " " + item["name"]
      if m in CORRECT:
        item["manufacturer"] = CORRECT[m]
    return item
