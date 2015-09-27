import scrapy
from scrapy import log
from scrapy.spiders import SitemapSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

MANUFACTURERS = ["Rctimer", "RCTimer", "BaseCam", "Elgae", "ELGAE", "ArduFlyer", "Boscam"]
CORRECT = {"Rctimer": "RCTimer", "ELGAE": "Elgae"}
STOCK_STATE_MAP = {"available-on-backorder": "backordered",
                   "in-stock": "in_stock",
                   "out-of-stock": "out_of_stock"}
class UavObjectsSpider(SitemapSpider):
    name = "uavobjects"
    allowed_domains = ["uavobjects.com"]
    sitemap_urls = ["http://www.uavobjects.com/product-sitemap.xml"]

    sitemap_rules = [
        ('/product/', 'parse_item'),
    ]

    def parse_item(self, response):
        item = Part()
        item["site"] = "uavobjects"
        product_name = response.css("h1.product_title")
        if not product_name:
            return
        item["name"] = product_name[0].xpath("text()").extract()[0]

        variant = {}
        variant["timestamp"] = response.headers["Date"]
        item["variants"] = [variant]
        variant["url"] = response.url

        price = response.css("[itemprop=\"price\"]::attr(content)")
        if price:
          price = float(price.extract_first())
          variant["price"] = "${:.2f}".format(price)

        stock = response.css(".stock")
        if stock:
          c = stock.css("::attr(class)").extract_first().split()[-1]
          if c in STOCK_STATE_MAP:
            variant["stock_state"] = STOCK_STATE_MAP[c]
            variant["stock_text"] = stock.css("::text").extract_first().strip()
          else:
            print(c)

        for m in MANUFACTURERS:
          if item["name"].startswith(m):
            if m in CORRECT:
              m = CORRECT[m]
            item["manufacturer"] = m
            item["name"] = item["name"][len(m):].strip()
            break
        return item
