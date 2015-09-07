import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

import urllib
import urlparse

MANUFACTURERS = ["Gemfan", "ZTW", "T-Motor", "Surveilzone", "FrSky", "HQProp", "Cobra", "DYS", "Feiyu Tech"]
CORRECT = {"Sunny Sky": "Sunnysky", "Frsky" : "FrSky", "Emax": "EMAX", "Feetech": "FEETECH"}
MANUFACTURERS.extend(CORRECT.keys())
NEW_PREFIX = {}
QUANTITY = {" Set (2CCW + 2CW)": 4,
            " Set (2CW + 2CCW)": 4,
            " Value Pack - 6 Set (2CCW + 2CW)": 24,
            " Value Pack - 12 Set (2CCW + 2CW)": 48,
            " Value Pack - 25 Set (2CCW + 2CW)": 100}
class BoltRCSpider(CrawlSpider):
    name = "boltrc"
    allowed_domains = ["boltrc.com"]
    start_urls = ["http://boltrc.com"]

    rules = (
        Rule(LinkExtractor(restrict_css=["#menu", ".pagination .links"])),

        Rule(LinkExtractor(restrict_css=".name"), callback='parse_item'),
    )

    def parse_item(self, response):
      item = Part()
      item["site"] = self.name
      product_name = response.css(".product_main_right h3")
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

      price = response.css(".price-tax")
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
