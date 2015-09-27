import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

import copy
import re
import urllib
import urlparse

MANUFACTURERS = ["Pololu"]
CORRECT = {"GemFan": "Gemfan"}
MANUFACTURERS.extend(CORRECT.keys())
QUANTITY = {" 8 pack": 8}
COMBINATION_RE = re.compile("addCombination\([0-9]+, new Array\(([0-9\' ]+)\), ([0-9]+), .*\);")

ATTRIBUTE_RE = re.compile("tabInfos\['id_attribute'\] = ('[0-9]+');\s+tabInfos\['attribute'\] = '(\w+)';", re.UNICODE)
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
      product_name = response.css("#pb-left-column h1")
      if not product_name:
          return
      item["name"] = product_name[0].xpath("text()").extract()[0].strip()

      variant = {}
      variant["timestamp"] = response.headers["Date"]
      item["variants"] = []
      variant["url"] = response.url

      price = response.css("#our_price_display")
      if price:
        variant["price"] = price.xpath("text()").extract()[0].strip()

      for quantity in QUANTITY:
        if quantity in item["name"]:
          variant["quantity"] = QUANTITY[quantity]
          item["name"] = item["name"].replace(quantity, "")

      body = response.body_as_unicode()
      attr_map = {}
      for attr in ATTRIBUTE_RE.finditer(body):
        g = attr.groups()
        attr_map[g[0]] = g[1]
      if not attr_map:
        quantity = response.css("#quantityAvailable::text")
        if quantity:
          stock_quantity = int(quantity.extract_first().strip())
          if stock_quantity == 0:
            variant["stock_state"] = "out_of_stock"
          else:
            variant["stock_state"] = "in_stock"
            variant["stock_text"] = str(stock_quantity) + " items in stock"
        item["variants"].append(variant)
      else:
        for combo in COMBINATION_RE.finditer(body):
          g = combo.groups()
          if "," in g[0]:
            print(g)
            continue
          variant["description"] = attr_map[g[0]]
          stock_quantity = int(g[1])
          if stock_quantity == 0:
            variant["stock_state"] = "out_of_stock"
          else:
            variant["stock_state"] = "in_stock"
            variant["stock_text"] = str(stock_quantity) + " items in stock"
          item["variants"].append(variant)
          variant = copy.deepcopy(variant)

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
