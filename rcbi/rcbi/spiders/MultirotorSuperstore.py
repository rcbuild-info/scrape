import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

MANUFACTURERS = ["Cobra", "Dinogy", "SkyRC", "DYS", "HQProp", "iPower", "Tattu", "GemFan", "SunnySky", "Emax", "ZTW", "MS", "FrSky", "RCTimer", "TBS", "VAS", "DTF UHF", "Pololu", "ImmersionRC", "Hovership", "FatShark", "Hawkeye", "Brotronics", "Argonaut", "3DR", "Tarot", "SkyZone", "Shendrones", "Revolectrix", "Flying Cinema", "Airbot", "Circular Wireless"]
CORRECT = {"GemFan": "Gemfan", "SunnySky": "Sunnysky", "Emax": "EMAX", "MS": "MultirotorSuperstore", "TBS": "Team BlackSheep", "VAS": "Video Aerial Systems", "3DR": "3DRobotics", "SkyZone": "Skyzone", "ShenDrones": "Shendrones"}
NEW_PREFIX = {}
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
      item["url"] = response.url
      product_name = response.css(".product-name")
      if not product_name:
          return
      item["name"] = product_name[0].xpath("//h1/text()").extract()[0]

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
