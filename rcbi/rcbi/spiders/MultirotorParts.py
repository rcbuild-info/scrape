import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

MANUFACTURERS = ["Blackout", "Cobra", "HQProp", "ImmersionRC", "Pololu", "T-Motor", "FrSky", "Gemfan", "Diatone", "DYS", "ZTW"]
CORRECT = {}
NEW_PREFIX = {}
QUANTITY = {"set of 4 ": 4, "set 8 pcs ": 8, " (4x cw en 4x ccw)": 8, " (2 cw and 2 ccw)": 4, "set of 2 ": 2, " (1 cw and 1 ccw)": 2, " (1 cw an 1 ccw)": 2, " (1 cw and 1ccw)": 2}
STRIP_PREFIX=["4 "]
class MultirotorPartsSpider(CrawlSpider):
    name = "multirotorparts"
    allowed_domains = ["multirotorparts.com"]
    start_urls = ["https://www.multirotorparts.com/"]

    rules = (
        Rule(LinkExtractor(restrict_css=["#vertnav", ".pages"])),

        Rule(LinkExtractor(restrict_css=".product-name"), callback='parse_item'),
    )

    def parse_item(self, response):
      item = Part()
      item["site"] = self.name
      item["url"] = response.url
      product_name = response.css(".product-name h1")
      if not product_name:
          return
      item["name"] = product_name[0].xpath("text()").extract()[0].strip()

      for prefix in STRIP_PREFIX:
        if item["name"].startswith(prefix):
          item["name"] = item["name"][len(prefix):]
          break

      price = response.css(".special-price .price")
      if price:
        item["price"] = price.xpath("text()").extract()[0].strip()
      else:
        price = response.css(".regular-price .price")
        if price:
          item["price"] = price.xpath("text()").extract()[0].strip()

      for quantity in QUANTITY:
        if quantity in item["name"]:
          item["quantity"] = 4
          item["name"] = item["name"].replace(quantity, "")

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
      return item
