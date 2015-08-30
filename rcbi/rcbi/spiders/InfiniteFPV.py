import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

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
      item["url"] = response.url
      product_name = response.css("[itemprop='name']")
      if not product_name:
          return
      item["name"] = product_name[0].xpath("//h1/text()").extract()[0].strip()

      price = response.css(".price .amount")
      if price:
        item["price"] = price.xpath("text()").extract()[0]

      item["manufacturer"] = "infiniteFPV"
      return item
