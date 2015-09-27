import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

import urlparse
import urllib

MANUFACTURERS = ["Boscam", "Orange", "Rotorgeeks", "Loc8tor", "Skyzone", "T-Motor", "Zippy", "FrSKY"]
CORRECT = {"Abusemark": "AbuseMark", "FrSKY": "FrSky", "HQ Prop": "HQProp", "Orange": "OrangeRx"}
PREFIX_TO_MANUFACTURER = {"Nano-Tech": "Turnigy"}
STRIP_PREFIX = {"HQProp": ["HQ"], "Lemon Rx": ["Lemon"]}
STOCK_STATE_MAP = {"In Stock": "in_stock",
                   "Out Of Stock": "out_of_stock",
                   "Pre-Order": "backordered"}
class RotorGeeksSpider(CrawlSpider):
    name = "rotorgeeks"
    allowed_domains = ["rotorgeeks.com"]
    start_urls = ["http://rotorgeeks.com/index.php?route=information/sitemap"]

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(LinkExtractor(allow=('.*route=product/category.*', ))),

        # Extract links matching 'item.php' and parse them with the spider's method parse_item
        Rule(LinkExtractor(allow=('.*route=product/product.*', )), callback='parse_item'),
    )

    def parse_item(self, response):
        headers = response.css(".description span")
        data = response.css(".description a")
        manufacturer = None
        for i, header in enumerate(headers):
            header = header.xpath("text()").extract()[0]
            if header == "Brand:":
                manufacturer = data[i].xpath("text()").extract()[0]
        item = Part()
        if manufacturer and manufacturer != "No":
          item["manufacturer"] = manufacturer
        item["site"] = self.name
        product_name = response.css("#content h1")
        if not product_name:
            return
        item["name"] = product_name[0].xpath("text()").extract()[0].strip()
        for m in MANUFACTURERS:
          if item["name"].startswith(m):
            item["name"] = item["name"][len(m):].strip()
            item["manufacturer"] = m
            break
        for prefix in PREFIX_TO_MANUFACTURER:
          if item["name"].startswith(prefix):
            item["manufacturer"] = PREFIX_TO_MANUFACTURER[prefix]
            break

        if "manufacturer" in item:
          m = item["manufacturer"]
          if m in CORRECT:
            item["manufacturer"] = CORRECT[m]
          m = item["manufacturer"]
          if item["name"].startswith(m):
            item["name"] = item["name"][len(m):].strip()
          if m in STRIP_PREFIX:
            for prefix in STRIP_PREFIX[m]:
              if item["name"].startswith(prefix):
                item["name"] = item["name"][len(prefix):].strip()

        product_code = response.css("#otp-model::text")
        if product_code:
          item["sku"] = product_code.extract_first().strip()

        variant = {}
        variant["timestamp"] = response.headers["Date"]
        item["variants"] = [variant]

        text = response.css(".description::text")
        # Skip the first. Its a newline before the first span.
        text_index = 1
        for h in headers:
          label = h.css("::text").extract_first().strip()
          value = text[text_index].extract().strip()
          text_index += 2

          if label == "Availability:":
            variant["stock_text"] = value
            if value in STOCK_STATE_MAP:
              variant["stock_state"] = STOCK_STATE_MAP[value]
            else:
              print(value)
          elif label == "Product Code:":
            item["sku"] = value

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

        price = response.css(".product-info .price")
        if price:
          special = price.css(".price-new::text")
          if special:
            variant["price"] = special.extract_first().strip()
          else:
            variant["price"] = price.css("::text").extract_first().split()[1]
        return item
