import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

import copy
import os
import urlparse
import urllib

MANUFACTURERS = ["Cobra", "Dinogy", "SkyRC", "DYS", "HQProp", "iPower", "Tattu", "GemFan", "SunnySky", "Emax", "ZTW", "MS", "FrSky", "RCTimer", "TBS", "VAS", "DTF UHF", "Pololu", "ImmersionRC", "Hovership", "FatShark", "Hawkeye", "Brotronics", "Argonaut", "3DR", "Tarot", "SkyZone", "Shendrones", "Revolectrix", "Flying Cinema", "Airbot", "Circular Wireless"]
CORRECT = {"GemFan": "Gemfan", "SunnySky": "Sunnysky", "Emax": "EMAX", "MS": "MultirotorSuperstore", "TBS": "Team BlackSheep", "VAS": "Video Aerial Systems", "3DR": "3DRobotics", "SkyZone": "Skyzone", "ShenDrones": "Shendrones"}
NEW_PREFIX = {}
STOCK_STATE_MAP = {"backordered": "backordered",
                   "expected-on": "out_of_stock",
                   "http://schema.org/InStock": "in_stock",
                   "http://schema.org/OutOfStock": "out_of_stock"}
class MultirotorSuperstoreSpider(CrawlSpider):
    name = "multirotorsuperstore"
    allowed_domains = ["multirotorsuperstore.com"]
    start_urls = ["http://www.multirotorsuperstore.com/"]

    rules = (
        Rule(LinkExtractor(restrict_css=[".submenu", ".pages"])),

        Rule(LinkExtractor(restrict_css=".category-products"), callback='parse_item'),
    )

    def parse_item(self, response):
      item = Part()
      item["site"] = self.name
      product_name = response.css(".product-name")
      if not product_name:
          return
      item["name"] = product_name[0].xpath("//h1/text()").extract()[0]

      variant = {}
      variant["timestamp"] = response.headers["Date"]
      if "Last-Modified" in response.headers:
        variant["timestamp"] = response.headers["Last-Modified"]
      item["variants"] = [variant]

      parsed = urlparse.urlparse(response.url)
      filename = "/" + os.path.basename(parsed[2])
      variant["url"] = urlparse.urlunparse((parsed[0], parsed[1], filename,
                                            parsed[3], parsed[4], parsed[5]))

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

      superproduct = response.css("#super-product-table")
      if not superproduct:
        availability = response.css("[itemprop=\"availability\"]::attr(href)")
        if availability and availability.extract_first() in STOCK_STATE_MAP:
          variant["stock_state"] = STOCK_STATE_MAP[availability.extract_first()]
          variant["stock_text"] = response.css(".availability>span::text").extract_first().strip()
        elif availability:
          print(availability)

        price = response.css(".product-essential .regular-price .price::text")
        if price:
          special = response.css(".product-essential .special-price .price::text")
          if special:
            variant["price"] = special.extract_first().strip()
          else:
            variant["price"] = price.extract_first().strip()
      else:
        subproducts = superproduct.css("tbody>tr")
        first = True
        in_stock = response.css(".product-essential .in-stock")
        if not in_stock:
          variant["stock_state"] = "out_of_stock"
        for subproduct in subproducts:
          cols = subproduct.css("td")
          if first:
            first = False
          else:
            variant = copy.deepcopy(variant)
            item["variants"].append(variant)

          variant["description"] = cols[0].css("::text").extract_first().strip()

          if in_stock:
            quantity_field = cols[2].css("input")
            if quantity_field:
              variant["stock_state"] = "in_stock"
            else:
              variant["stock_state"] = "out_of_stock"

          # Do price last so we can copy for tiered pricing.
          price = cols[1].css(".regular-price .price::text")
          if price:
            variant["price"] = price.extract_first().strip()

          # TODO(tannewt): Support tiered pricing.
      return item
