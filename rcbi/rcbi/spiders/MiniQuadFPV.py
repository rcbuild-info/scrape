import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

MANUFACTURERS = []
CORRECT = {}
NEW_PREFIX = {}
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
      item["url"] = response.url
      product_name = response.css(".product_title")
      if not product_name:
          return
      item["name"] = product_name[0].xpath("text()").extract()[0].strip()

      price = response.css(".price .amount")
      if price:
        item["price"] = price.xpath("text()").extract()[0]

      item["manufacturer"] = "THug FRAMES"
      return item
