import scrapy
from scrapy import log
from scrapy.spiders import SitemapSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

MANUFACTURERS = ["Boscam", "Tattu", "T-Motor", "Tarot", "Hobbywing", "DUPU"]
CORRECT = {"T-motor": "T-Motor", "hobbywing": "Hobbywing", "SunnySky": "Sunnysky", "Skylark": "Skylark FPV", "SUNNYSKY": "Sunnysky", "HobbyWing": "Hobbywing", "BOSCAM": "Boscam"}
MANUFACTURERS.extend(CORRECT.keys())
STRIP_PREFIX = ["TIGER MOTOR ", "New ", "NEW "]
class FPVModelSpider(SitemapSpider):
    name = "fpvmodel"
    allowed_domains = ["fpvmodel.com"]
    sitemap_urls = ["http://www.fpvmodel.com/sitemap.xml"]

    sitemap_rules = [
        ('.*\.html', 'parse_item'),
    ]

    def parse_item(self, response):
      item = Part()
      item["site"] = self.name
      item["url"] = response.url
      product_name = response.css(".item-goods h1")
      if not product_name:
          return
      item["name"] = product_name[0].xpath("text()").extract()[0].strip()

      for prefix in STRIP_PREFIX:
        if item["name"].startswith(prefix):
          item["name"] = item["name"][len(prefix):]

      price = response.css(".format-price")
      if price:
        item["price"] = price.xpath("text()").extract()[0].strip()

      for m in MANUFACTURERS:
        if item["name"].startswith(m):
          if m in CORRECT:
            m = CORRECT[m]
          item["manufacturer"] = m
          item["name"] = item["name"][len(m):].strip()
          break
      return item
