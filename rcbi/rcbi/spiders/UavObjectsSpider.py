import scrapy
from scrapy import log
from scrapy.contrib.spiders import SitemapSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from rcbi.items import Part

MANUFACTURERS = ["Rctimer", "RCTimer", "BaseCam", "Elgae", "ELGAE", "ArduFlyer", "Boscam"]
CORRECT = {"Rctimer": "RCTimer", "ELGAE": "Elgae"}
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
        item["url"] = response.url
        product_name = response.css("h1.product_title")
        if not product_name:
            return
        item["name"] = product_name[0].xpath("text()").extract()[0]
        for m in MANUFACTURERS:
          if item["name"].startswith(m):
            if m in CORRECT:
              m = CORRECT[m]
            item["manufacturer"] = m
            item["name"] = item["name"][len(m):].strip()
            break
        return item