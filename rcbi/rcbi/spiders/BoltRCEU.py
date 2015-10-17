import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

import urllib
import urlparse

MANUFACTURERS = ["FrSky", "T-Motor", "ZTW", "Gemfan", "Surveilzone"]
CORRECT = {"SunnySky": "Sunnysky", "Cobra-": "Cobra", "HQP": "HQProp", "Frsky": "FrSky"}
MANUFACTURERS.extend(CORRECT.keys())
NEW_PREFIX = {}
QUANTITY = {" (2 Pcs)": 2}
class BoltRCEUSpider(CrawlSpider):
  name = "boltrceu"
  allowed_domains = ["boltrc.eu"]
  start_urls = ["http://boltrc.eu/nl/en/"]

  rules = (
    Rule(LinkExtractor(restrict_css=["#block_top_menu", ".subcategory-image", ".pagination"])),
    Rule(LinkExtractor(restrict_css="[itemprop=\"name\"]"), callback='parse_item'),
  )

  def parse_item(self, response):
    item = Part()
    item["site"] = self.name
    product_name = response.css("[itemprop=\"name\"]")
    if not product_name:
      return
    item["name"] = product_name[0].xpath("text()").extract_first().strip()

    sku = response.css("[itemprop=\"sku\"]::text")
    if sku:
      item["sku"] = sku.extract_first().strip()

    variant = {}
    item["variants"] = [variant]
    variant["url"] = response.url

    price = response.css("[itemprop=\"price\"]::text")
    if price:
      variant["price"] = price.extract_first().strip()

    for quantity in QUANTITY:
      if quantity in item["name"]:
        variant["quantity"] = QUANTITY[quantity]
        item["name"] = item["name"].replace(quantity, "")

    availability = response.css("#availability_value")
    if availability:
      availability = availability.css("::text").extract_first()
      if availability == None or availability.strip() == "":
        variant["stock_state"] = "in_stock"
      else:
        variant["stock_state"] = "out_of_stock"

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
