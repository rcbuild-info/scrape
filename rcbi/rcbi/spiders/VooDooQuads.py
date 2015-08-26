import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

MANUFACTURERS = ["Zippy", "Skyzone", "RUNCAM", "Pololu", "OrangeRX", "Kypom", "GEMFAM"]
CORRECT = {"GEMFAM": "Gemfan", "RUNCAM": "RunCam", "OrangeRX": "OrangeRx"}
NEW_PREFIX = {}
class VooDooQuadsSpider(CrawlSpider):
    name = "voodooquads"
    allowed_domains = ["voodooquads.com"]
    start_urls = ["http://www.voodooquads.com/"]

    rules = (
        Rule(LinkExtractor(restrict_css=["#Menu", ".sf-menu"])),
        Rule(LinkExtractor(restrict_css=[".ProductImage"]), callback='parse_item'),
    )

    def parse_item(self, response):
      item = Part()
      item["site"] = self.name
      item["url"] = response.url
      product_name = response.css(".ProductMain h1")
      if not product_name:
          return
      item["name"] = product_name[0].xpath("text()").extract()[0].strip()

      price = response.css(".ProductPrice")
      if price:
        item["price"] = price.xpath("text()").extract()[0]

      if "VDQ" in item["name"] or "VooDoo" in item["name"]:
        item["manufacturer"] = "VooDoo Quads"
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
