import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

MANUFACTURERS = []
CORRECT = {}
NEW_PREFIX = {}

STOCK_STATE_MAP = {"http://schema.org/InStock": "in_stock",
                   "http://schema.org/OutOfStock": "out_of_stock"}
class MiniQuadFPVSpider(CrawlSpider):
    name = "miniquadfpv"
    allowed_domains = ["miniquadfpv.com"]
    start_urls = ["http://miniquadfpv.com/ship/"]

    rules = (
        Rule(LinkExtractor(restrict_css=[".woocommerce-pagination"])),
        Rule(LinkExtractor(restrict_css=[".product a:first-child"]), callback='parse_item'),
    )

    def parse_item(self, response):
      item = Part()
      item["site"] = self.name
      product_name = response.css(".product_title")
      if not product_name:
          return
      item["name"] = product_name[0].xpath("text()").extract()[0].strip()

      item["manufacturer"] = "THug FRAMES"

      sku = response.css("[itemprop=\"sku\"]::text")
      if sku:
        item["sku"] = sku.extract_first().strip()

      variant = {}
      variant["timestamp"] = response.headers["Date"]
      item["variants"] = [variant]
      variant["url"] = response.url

      price = response.css(".price .amount")
      if price:
        variant["price"] = price.xpath("text()").extract()[0]

      availability = response.css("[itemprop=\"availability\"]::attr(href)").extract_first()
      if availability:
        variant["stock_state"] = STOCK_STATE_MAP[availability]
        if item["name"].endswith("PRE ORDER"):
          item["name"] = item["name"][:-len("PRE ORDER")].strip(u" \u2013")
          variant["stock_state"] = "backordered"
          variant["stock_text"] = "PRE ORDER"

      return item
