import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

import os.path
import urlparse
import urllib

MANUFACTURERS = ["AtasSphere", "Cobra", "Dinogy", "SkyRC", "SKYRC", "DAL RC (Surveilzone)", "RMRC", "DYS", "HQProp", "Gemfan", "Sunnysky", "Tiger Motor", "Skyzone", "Drone Matters", "DM", "TBS", "SEETEC", "Pololu", "OrangeRx", "OrangeRX", "Lumenier", "ImmersionRC", "IBCrazy", "Futaba", "FrSky"]
CORRECT = {"SKYRC": "SkyRC", "DAL RC (Surveilzone)" : "Surveilzone", "RMRC": "ReadyMadeRC", "Tiger Motor": "T-Motor", "DM": "Drone Matters", "TBS": "Team BlackSheep", "OrangeRX": "OrangeRx"}
NEW_PREFIX = {"DAL RC (Surveilzone)": "DalProp"}
STOCK_STATE_MAP = {"in-stock": "in_stock",
                   "out-of-stock": "out_of_stock"}
class DroneMattersSpider(CrawlSpider):
    name = "dronematters"
    allowed_domains = ["dronematters.com"]
    start_urls = ["http://www.dronematters.com/catalog/seo_sitemap/category/", "http://www.dronematters.com/fpv/antennas/2-4ghz.html"]

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(LinkExtractor(allow=('seo_sitemap/category/', ))),
        Rule(LinkExtractor(restrict_css=".pages", )),
        Rule(LinkExtractor(restrict_css=".sitemap", )),

        # Extract links matching 'item.php' and parse them with the spider's method parse_item
        Rule(LinkExtractor(restrict_css=".product-name"), callback='parse_item')
    )

    def parse_item(self, response):
        item = Part()
        item["site"] = self.name
        product_name = response.css(".product-name h1")
        if not product_name:
            return
        item["name"] = product_name[0].xpath("text()").extract()[0].strip()
        this_manufacturer = []
        for m in MANUFACTURERS + this_manufacturer:
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
        variant["timestamp"] = response.headers["Date"]
        if "Last-Modified" in response.headers:
          variant["timestamp"] = response.headers["Last-Modified"]
        item["variants"] = [variant]

        parsed = urlparse.urlparse(response.url)
        filename = "/" + os.path.basename(parsed[2])
        variant["url"] = urlparse.urlunparse((parsed[0], parsed[1], filename,
                                              parsed[3], parsed[4], parsed[5]))

        prices = response.css(".price-box")
        if prices:
          special = prices.css(".special-price .price::text")
          full_product_price = prices.css(".full-product-price .price::text")
          if special:
            variant["price"] = special.extract_first().strip()
          elif full_product_price:
            # Price is dynamic based on configuration.
            pass
          else:
            variant["price"] = prices.css(".regular-price .price::text").extract_first().strip()

        availability = response.css(".availability")
        if availability:
          description = availability.css("span>span")
          # Don't use the stock text because it may not be true. Some say in stock but are not available.
          #classes = description.css("::attr(class)").extract_first().split()
          #text = description.css("::text").extract_first().strip()
          #print(classes, text)
          #variant["stock_text"] = text
          stock_class = availability.css("::attr(class)").extract_first().split()[1]
          if stock_class in STOCK_STATE_MAP:
            variant["stock_state"] = STOCK_STATE_MAP[stock_class]
          else:
            print(stock_class)
        return item
