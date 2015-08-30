import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

class ShendronesSpider(CrawlSpider):
    name = "shendrones"
    allowed_domains = ["shendrones.myshopify.com"]
    start_urls = ["http://shendrones.myshopify.com/collections/all"]

    rules = (
        Rule(LinkExtractor(restrict_css=[".grid-item"]), callback='parse_item'),
    )

    def parse_item(self, response):
      item = Part()
      item["site"] = self.name
      item["url"] = response.url
      product_name = response.css("h1[itemprop='name']")
      if not product_name:
          return
      item["name"] = product_name[0].xpath("text()").extract()[0].strip()

      price = response.css(".productPrice")
      if price:
        item["price"] = price.xpath("text()").extract()[0]

      item["manufacturer"] = "Shendrones"
      return item
