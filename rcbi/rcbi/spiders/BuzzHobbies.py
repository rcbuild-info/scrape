import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

import urllib
import urlparse

MANUFACTURERS = ["Boscam", "Cobra", "DYS", "Gemfan", "HQProp", "Pololu", "ImmersionRC", "Horeson"]
CORRECT = {"HQProps": "HQProp"}
MANUFACTURERS.extend(CORRECT.keys())
MANUFACTURERS.sort(key=len, reverse=True)
NEW_PREFIX = {}
QUANTITY = {}
STOCK_STATE_MAP = {"outstock": "out_of_stock",
                   "instock": "in_stock"}
class BuzzHobbiesSpider(CrawlSpider):
  name = "buzzhobbies"
  allowed_domains = ["buzzhobbies.com.au"]
  start_urls = ["http://buzzhobbies.com.au"]

  rules = (
    Rule(LinkExtractor(restrict_css=[".navbar-nav", ".pagination .links"])),
    Rule(LinkExtractor(restrict_css=[".inner .name"]), callback='parse_item'),
  )

  def parse_item(self, response):
    item = Part()
    item["site"] = self.name
    product_name = response.css(".page-header h1")
    if not product_name:
      return
    item["name"] = product_name[0].xpath("text()").extract()[0].strip()

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

    variant = {}
    item["variants"] = [variant]

    parsed = urlparse.urlparse(response.url)
    qs = urlparse.parse_qs(parsed.query)
    qs.pop("path", None)
    # By default all values in qs will be a list and cause funky % encoding
    # in the resulting url. So, if the list is one value then we replace the
    # list with it.
    for k in qs:
      if len(qs[k]) == 1:
        qs[k] = qs[k][0]
    variant["url"] = urlparse.urlunparse((parsed[0], parsed[1], parsed[2],
                                          parsed[3], urllib.urlencode(qs),
                                          parsed[5]))

    price = response.css(".price-normal")
    if price:
      variant["price"] = price.css("::text").extract_first().strip()

    for quantity in QUANTITY:
      if quantity in item["name"]:
        variant["quantity"] = QUANTITY[quantity]
        item["name"] = item["name"].replace(quantity, "")

    stock = response.css(".stock span")
    if stock:
      stock_class = stock.css("::attr(class)").extract_first()
      text = stock.css("::text").extract()[-1].strip()
      variant["stock_text"] = text
      if stock_class in STOCK_STATE_MAP:
        variant["stock_state"] = STOCK_STATE_MAP[stock_class]
      else:
        print(stock_class)

    return item
