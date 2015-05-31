import scrapy
from scrapy import log
from scrapy.contrib.spiders import SitemapSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from rcbi.items import Part

MANUFACTURERS = ["Rctimer", "RCTimer", "BaseCam", "Elgae", "ELGAE", "ArduFlyer", "Boscam", "T-Motor", "HQProp", "Suppo", "Flyduino", "SLS", "Frsky"]
CORRECT = {"Rctimer": "RCTimer", "ELGAE": "Elgae", "Frsky": "FrSky"}
class FlyduinoSpider(SitemapSpider):
    name = "flyduino"
    allowed_domains = ["flyduino.net"]
    sitemap_urls = ["http://flyduino.net/sitemap.xml"]
    
    def parse(self, response):
        item = Part()
        item["site"] = "flyduino"
        item["url"] = response.url
        product_name = response.css("div.hproduct")
        if not product_name:
            return
        item["name"] = product_name[0].xpath("//h1/text()").extract()[0]
        for m in MANUFACTURERS:
          if item["name"].startswith(m):
            if m in CORRECT:
              m = CORRECT[m]
            item["manufacturer"] = m
            item["name"] = item["name"][len(m):].strip()
            break
        return item