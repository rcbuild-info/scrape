import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

MANUFACTURERS = ["Gemfan", "HQprop", "Cobra", "SunnySky"]
CORRECT = {"HQprop": "HQProp", "SunnySky": "Sunnysky"}
NEW_PREFIX = {}
class FPVReconnSpider(CrawlSpider):
    name = "fpvreconn"
    allowed_domains = ["fpv-reconn.com"]
    start_urls = ["http://fpv-reconn.com/store/"]

    rules = (
        Rule(LinkExtractor(restrict_css=["#menu", ".links"])),

        Rule(LinkExtractor(restrict_css=".name"), callback='parse_item'),
    )

    def parse_item(self, response):
      item = Part()
      item["site"] = self.name
      item["url"] = response.url
      product_name = response.css("#content h1")
      if not product_name:
          return
      item["name"] = product_name[0].xpath("text()").extract()[0].strip()

      price = response.css(".price")
      if price:
        item["price"] = price.xpath("text()").extract()[0][len("Price:"):].strip()

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
