import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

STOCK_STATE_MAP = {"available-on-backorder": "backordered",
                   "in-stock": "in_stock",
                   "out-of-stock": "out_of_stock"}
class InfiniteFPVSpider(CrawlSpider):
    name = "infinitefpv"
    allowed_domains = ["infinitefpv.com"]
    start_urls = ["http://www.infinitefpv.com/shop/"]

    rules = (
        Rule(LinkExtractor(restrict_css=[".product-categories"])),
        Rule(LinkExtractor(restrict_css=[".inner_product"]), callback='parse_item'),
    )

    def parse_item(self, response):
      item = Part()
      item["site"] = self.name
      product_name = response.css("[itemprop='name']")
      if not product_name:
          return
      item["name"] = product_name[0].xpath("//h1/text()").extract_first().strip()

      variant = {}
      variant["timestamp"] = response.headers["Date"]
      item["variants"] = [variant]
      variant["url"] = response.url

      price = response.css(".price .amount")
      if price:
        variant["price"] = price.css("::text").extract_first()

      stock = response.css(".stock")
      if stock:
        c = stock.css("::attr(class)").extract_first().split()[-1]
        if c in STOCK_STATE_MAP:
          variant["stock_state"] = STOCK_STATE_MAP[c]
          variant["stock_text"] = stock.css("::text").extract_first().strip()
        else:
          print(c)

      item["manufacturer"] = "infiniteFPV"
      return item
