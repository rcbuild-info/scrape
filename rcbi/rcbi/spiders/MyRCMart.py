import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

import urlparse
import urllib

MANUFACTURERS = ["Walkera", "WL Toys", "Syma", "RCX"]
CORRECT = {"RCXHOBBY.COM": "RCX", "Fatshark": "FatShark", "HobbyWing": "Hobbywing"}
NEW_PREFIX = {}
class MyRCMartSpider(CrawlSpider):
    name = "myrcmart"
    allowed_domains = ["myrcmart.com"]
    start_urls = ["http://www.myrcmart.com/"]

    rules = (
        Rule(LinkExtractor(restrict_css=[".menucateg", ".menusubcateg", ".pageResults"])),
        Rule(LinkExtractor(restrict_xpaths="/html/body/table[2]/tr/td[2]/table/tr[3]/td/table/tr[1]/td/table")),

        Rule(LinkExtractor(deny=[".*buy_now.*", ".*product_review.*"], restrict_css=".productListing-data"), callback='parse_item'),
    )

    def parse_item(self, response):
      item = Part()
      item["site"] = self.name
      product_name = response.css("td.pageHeading")
      if not product_name:
          return
      item["name"] = product_name[0].xpath("text()").extract()[0]

      parsed = urlparse.urlparse(response.url)
      qs = urlparse.parse_qs(parsed.query)
      qs.pop("cPath", None)
      # By default all values in qs will be a list and cause funky % encoding
      # in the resulting url. So, if the list is one value then we replace the
      # list with it.
      for k in qs:
          if len(qs[k]) == 1:
              qs[k] = qs[k][0]
      item["url"] = urlparse.urlunparse((parsed[0], parsed[1], parsed[2],
                                         parsed[3], urllib.urlencode(qs),
                                         parsed[5]))

      details = response.css("td.prod_detail")
      manufacturer = None
      for i in xrange(len(details) / 2):
          text = details[2*i].xpath("text()").extract()
          if len(text) == 0:
            continue
          header = text[0]
          data = details[2*i+1].xpath("text()").extract()[0]
          if header == "Manufacturer:" and data != "Other":
            manufacturer = data
          elif header == "Weight:":
            item["weight"] = data

      price = response.css("td.prod_detail_price")
      if price:
        special = price[1].css(".productSpecialPrice")
        if special:
          item["price"] = special.xpath("text()").extract()[0]
        else:
          item["price"] = price[1].xpath("text()").extract()[0]

      if not manufacturer:
        for m in MANUFACTURERS:
          if item["name"].startswith(m):
            item["name"] = item["name"][len(m):].strip("- ")
            item["manufacturer"] = m
            break
      else:
        item["manufacturer"] = manufacturer

      if "manufacturer" in item:
          m = item["manufacturer"]
          if m in NEW_PREFIX:
            item["name"] = NEW_PREFIX[m] + " " + item["name"]
          if m in CORRECT:
            item["manufacturer"] = CORRECT[m]
            m = CORRECT[m]
          if item["name"].startswith(m):
            item["name"] = item["name"][len(m):].strip("- ")
      return item
