import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

MANUFACTURERS = ["Graupner", "Flite Test", "FT"]
CORRECT = {"FT": "Flite Test"}
NEW_PREFIX = {}
QUANTITY = {}
class FliteTestSpider(CrawlSpider):
    name = "flitetest"
    allowed_domains = ["store.flitetest.com"]
    start_urls = ["http://store.flitetest.com/"]

    rules = (
        Rule(LinkExtractor(restrict_css=[".sf-menu", ".CategoryPagination"])),

        Rule(LinkExtractor(restrict_css=".ProductDetails"), callback='parse_item'),
    )

    def parse_item(self, response):
      item = Part()
      item["site"] = self.name
      item["url"] = response.url
      product_name = response.css(".product-heading h1")
      if not product_name:
          return
      item["name"] = product_name[0].xpath("text()").extract()[0].strip()

      price = response.css(".VariationProductPrice")
      if price:
        item["price"] = price.xpath("text()").extract()[0].strip()
      else:
        price = response.css(".RetailPrice")
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
