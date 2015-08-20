import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

import urlparse
import urllib

MANUFACTURERS = ["Gemfan", "HQprop", "Cobra", "SunnySky", "FPV-Reconn"]
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

      parsed = urlparse.urlparse(response.url)
      qs = urlparse.parse_qs(parsed.query)
      qs.pop("path", None)
      # By default all values in qs will be a list and cause funky % encoding
      # in the resulting url. So, if the list is one value then we replace the
      # list with it.
      for k in qs:
          if len(qs[k]) == 1:
              qs[k] = qs[k][0]
      item["url"] = urlparse.urlunparse((parsed[0], parsed[1], parsed[2],
                                         parsed[3], urllib.urlencode(qs),
                                         parsed[5]))

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
