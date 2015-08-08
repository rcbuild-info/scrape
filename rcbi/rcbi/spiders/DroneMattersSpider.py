import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

import urlparse
import urllib

MANUFACTURERS = ["AtasSphere", "Cobra", "Dinogy", "SkyRC", "SKYRC", "DAL RC (Surveilzone)", "RMRC", "DYS", "HQProp", "Gemfan", "Sunnysky", "Tiger Motor", "Skyzone", "Drone Matters", "DM", "TBS", "SEETEC", "Pololu", "OrangeRx", "OrangeRX", "Lumenier", "ImmersionRC", "IBCrazy", "Futaba", "FrSky"]
CORRECT = {"SKYRC": "SkyRC", "DAL RC (Surveilzone)" : "Surveilzone", "RMRC": "ReadyMadeRC", "Tiger Motor": "T-Motor", "DM": "Drone Matters", "TBS": "Team BlackSheep", "OrangeRX": "OrangeRx"}
NEW_PREFIX = {"DAL RC (Surveilzone)": "DalProp"}
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
        item["url"] = response.url
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
        return item
