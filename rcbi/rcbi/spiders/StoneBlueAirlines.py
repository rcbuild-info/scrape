import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

import os
import urlparse
import urllib

MANUFACTURERS = ["Cobra", "DTF-UHF", "EMAX", "FatShark", "Foxeer", "FrSky", "Gemfan", "ImmersionRC", "XHover"]
CORRECT = {"Cobra Motor": "Cobra", "Emax": "EMAX", "HQ Prop": "HQProp", "HQ Prop Propellers": "HQProp", "HQ Direct Drive Propellers": "HQProp", "SunnySky": "Sunnysky", "TBS": "Team BlackSheep", "VAS": "Video Aerial Systems"}
MANUFACTURERS.extend(CORRECT.keys())
MANUFACTURERS.sort(key=len, reverse=True)
NEW_PREFIX = {}
QUANTITY = {}
STOCK_STATE_MAP = {"out-of-stock": "out_of_stock",
                   "in-stock": "in_stock"}
class StoneBlueAirlinesSpider(CrawlSpider):
  name = "stoneblueairlines"
  allowed_domains = ["www.stoneblueairlines.com"]
  start_urls = ["http://www.stoneblueairlines.com/"]

  rules = (
    Rule(LinkExtractor(restrict_css=["#nav", ".pages ol"])),
    Rule(LinkExtractor(restrict_css=[".product-name"]), callback='parse_item'),
  )

  def parse_item(self, response):
    item = Part()
    item["site"] = self.name
    product_name = response.css(".product-name h1::text")
    if not product_name:
      return
    item["name"] = product_name.extract_first().strip()

    for m in MANUFACTURERS:
      if item["name"].startswith(m):
        item["name"] = item["name"][len(m):].strip("- ")
        item["manufacturer"] = m
        break
    if "manufacturer" in item:
      m = item["manufacturer"]
      if m in NEW_PREFIX:
        item["name"] = NEW_PREFIX[m] + " " + item["name"]
      if m in CORRECT:
        item["manufacturer"] = CORRECT[m]

    variant = {}
    item["variants"] = [variant]

    parsed = urlparse.urlparse(response.url)
    filename = "/" + os.path.basename(parsed[2])
    variant["url"] = urlparse.urlunparse((parsed[0], parsed[1], filename,
                                          parsed[3], parsed[4], parsed[5]))

    price_box = response.css(".product-essential .price-box")
    if price_box:
      price = price_box.css(".special-price .price::text")
      if not price:
        price = price_box.css(".regular-price .price::text")
      if price:
        variant["price"] = price.extract_first().strip()

    for quantity in QUANTITY:
      if quantity in item["name"]:
        variant["quantity"] = QUANTITY[quantity]
        item["name"] = item["name"].replace(quantity, "")

    stock = response.css(".availability")
    if stock:
      stock_class = stock.css("::attr(class)").extract_first().strip().split()[-1]
      text = stock.css("span::text").extract()[-1].strip()
      variant["stock_text"] = text
      if stock_class in STOCK_STATE_MAP:
        variant["stock_state"] = STOCK_STATE_MAP[stock_class]
      else:
        print(stock_class)

    return item
