import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

MANUFACTURERS = ["DYS", "HQ Prop", "Sunnysky", "Tiger Motor", "Cobra"]
CORRECT = {"HQ Prop": "HQProp", "Tiger Motor": "T-Motor"}
NEW_PREFIX = {}
QUANTITY = {"4x ": 4, "8x ": 8}
class ImpulseRCSpider(CrawlSpider):
    name = "impulserc"
    allowed_domains = ["impulserc.com"]
    start_urls = ["http://impulserc.com/"]

    rules = (
        Rule(LinkExtractor(restrict_css=[".sublist", ".pager"])),
        Rule(LinkExtractor(restrict_css=[".product-title"]), callback='parse_item'),
    )

    def parse_item(self, response):
      item = Part()
      item["site"] = self.name
      item["url"] = response.url
      product_name = response.css("[itemprop='name']")
      if not product_name:
          return
      item["name"] = product_name[0].xpath("text()").extract()[0].strip()

      price = response.css("[itemprop='price']")
      if price:
        item["price"] = price.xpath("text()").extract()[0].strip()

      for quantity in QUANTITY:
        if quantity in item["name"]:
          item["quantity"] = 4
          item["name"] = item["name"].replace(quantity, "")
          
      if "Alien" in item["name"] or "String Theory" in item["name"] or "Warpquad" in item["name"]:
        item["manufacturer"] = "ImpulseRC"

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
