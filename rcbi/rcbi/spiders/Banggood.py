import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

MANUFACTURERS = ["Walkera", "Eachine", "DYS", "FrSky", "EMAX", "Feiyu Tech", "Tarot", "Gemfan", "Flysky", "ZTW", "Diatone", "Sunnysky", "RCTimer", "Hobbywing", "Boscam", "ImmersionRC", "SkyRC", "Aomway", "Flycolor"]
CORRECT = {"SKYRC": "SkyRC", "Emax": "EMAX", "Skyzone": "SkyZone", "AOMWAY": "Aomway", "SunnySky": "Sunnysky", "GEMFAN": "Gemfan", "FlySky": "Flysky"}
MANUFACTURERS.extend(CORRECT.keys())
NEW_PREFIX = {}
STRIP_PREFIX = ["New Version ", "Original ", "2 Pairs "]
class BanggoodSpider(CrawlSpider):
    name = "banggood"
    allowed_domains = ["banggood.com"]
    start_urls = ["http://www.banggood.com/Wholesale-Multi-Rotor-Parts-c-2520.html",
                  "http://www.banggood.com/Wholesale-FPV-System--c-2734.html"]

    rules = (
        Rule(LinkExtractor(restrict_css=[".page_num"])),

        Rule(LinkExtractor(restrict_css=".title"), callback='parse_item'),
    )

    def parse_item(self, response):
      item = Part()
      item["site"] = self.name
      item["url"] = response.url
      product_name = response.css(".good_main h1")
      if not product_name:
          return
      item["name"] = product_name[0].xpath("text()").extract()[0].strip()

      for prefix in STRIP_PREFIX:
        if item["name"].startswith(prefix):
          item["name"] = item["name"][len(prefix):]
          break

      price = response.css(".price .now")
      if price:
        item["price"] = price.xpath("text()").extract()[0].strip()

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
