import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

import urllib
import urlparse

MANUFACTURERS = ["HQProp", "Tattu", "T-Motor", "Lumenier", "ImmersionRC", "IBCrazy", "Gemfan", "Futaba", "FrSky", "Boscam", "DYS", "Turnigy", "DJI", "Tarot", "RotorX", "Pololu", "Lift RC", "Cobra", "APC Propellers", "Flytrex"]
CORRECT = {"Ztw": "ZTW", "SunnySky": "Sunnysky", "LRC": "Lift RC", "Fat Shark": "FatShark", "Dys": "DYS", "3DR": "3DRobotics", "APC Propeller": "APC Propellers", "Apc Propeller": "APC Propellers"}
MANUFACTURERS.extend(CORRECT.keys())
NEW_PREFIX = {}
QUANTITY = {"Pair ": 2}
class LiftRCSpider(CrawlSpider):
    name = "liftrc"
    allowed_domains = ["liftrc.com"]
    start_urls = ["http://liftrc.com"]

    rules = (
        Rule(LinkExtractor(restrict_css=[".sm_megamenu_menu", ".pages"])),

        Rule(LinkExtractor(restrict_css=".item-title"), callback='parse_item'),
    )

    def parse_item(self, response):
      item = Part()
      item["site"] = self.name
      product_name = response.css(".product-name")
      if not product_name:
          return
      item["name"] = product_name[0].xpath("text()").extract()[0].strip()

      parsed = urlparse.urlparse(response.url)
      qs = urlparse.parse_qs(parsed.query)
      qs.pop("path", None)
      # By default all values in qs will be a list and cause funky % encoding
      # in the resulting url. So, if the list is one value then we replace the
      # list with it.
      for k in qs:
          if len(qs[k]) == 1:
              qs[k] = qs[k][0]
      item["url"] = urlparse.urlunparse((parsed[0], parsed[1], parsed[2],
                                         parsed[3], urllib.urlencode(qs),
                                         parsed[5]))

      price = response.css("[itemprop='price']")
      if price:
        item["price"] = price.xpath("text()").extract()[0].split()[-1]

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
          if m in NEW_PREFIX:
            item["name"] = NEW_PREFIX[m] + " " + item["name"]
          if m in CORRECT:
            item["manufacturer"] = CORRECT[m]
      return item
