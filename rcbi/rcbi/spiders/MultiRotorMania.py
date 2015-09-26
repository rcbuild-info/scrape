import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

MANUFACTURERS = ["HQProp", "FrSky", "Hawkeye", "Eachine", "Frsky", "Tattu", "ZTW", "uBlox", "VAS", "TAROT", "Tarot", "T-Motor", "T-Motors", "Sunnysky", "SunnySky", "SkyZone", "MRM", "Gemfan", "GemFan", "DYS", "Diatone", "Boscam", "X-CAM"]
CORRECT = {"Frsky": "FrSky", "VAS": "Video Aerial Systems", "TAROT": "Tarot", "T-Motors": "T-Motor", "SunnySky": "Sunnysky", "MRM": "MultiRotorMania", "GemFan": "Gemfan"}
NEW_PREFIX = {}
STOCK_STATE_MAP = {"http://schema.org/InStock": "in_stock",
                   "http://schema.org/OutOfStock": "out_of_stock"}
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
      product_name = response.xpath("//*[@id=\"center_column\"]/div[1]/div[3]/font/b")
      if not product_name:
          return
      item["name"] = product_name[0].xpath("text()").extract()[0].strip()

      variant = {}
      variant["timestamp"] = response.headers["Date"]
      if "Last-Modified" in response.headers:
        variant["timestamp"] = response.headers["Last-Modified"]
      item["variants"] = [variant]

      variant["url"] = response.url
      if variant["url"].startswith("http://www."):
        variant["url"] = variant["url"].replace("http://www.", "http://")

      price = response.css("#our_price_display")
      if price:
        variant["price"] = price.css("::text").extract_first()

      stock = response.css("[itemprop=\"availability\"]::attr(href)")
      if stock:
        value = stock.extract_first().strip()
        if value in STOCK_STATE_MAP:
          variant["stock_state"] = STOCK_STATE_MAP[value]
        else:
          print(value)

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
