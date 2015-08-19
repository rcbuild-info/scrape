import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

MANUFACTURERS = ["HQProp", "FrSky", "Hawkeye", "Eachine", "Frsky", "Tattu", "ZTW", "uBlox", "VAS", "TAROT", "Tarot", "T-Motor", "T-Motors", "Sunnysky", "SunnySky", "SkyZone", "MRM", "Gemfan", "GemFan", "DYS", "Diatone", "Boscam"]
CORRECT = {"Frsky": "FrSky", "VAS": "Video Aerial Systems", "TAROT": "Tarot", "T-Motors": "T-Motor", "SunnySky": "Sunnysky", "MRM": "MultiRotorMania", "GemFan": "Gemfan"}
NEW_PREFIX = {}
class MultiRotorManiaSpider(CrawlSpider):
    name = "multirotormania"
    allowed_domains = ["multirotormania.com"]
    start_urls = ["http://multirotormania.com/sitemap"]

    rules = (
        Rule(LinkExtractor(restrict_css=[".tree", ".pagination"])),

        Rule(LinkExtractor(restrict_css=".product-container"), callback='parse_item'),
    )

    def parse_item(self, response):
      item = Part()
      item["site"] = self.name
      item["url"] = response.url
      product_name = response.xpath("//*[@id=\"center_column\"]/div[1]/div[3]/font/b")
      if not product_name:
          return
      item["name"] = product_name[0].xpath("text()").extract()[0].strip()

      price = response.css("#our_price_display")
      if price:
        item["price"] = price.xpath("text()").extract()[0]

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
