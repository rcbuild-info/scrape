import scrapy
from scrapy import log
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from rcbi.items import Part

MANUFACTURERS = ["Boscam", "Orange", "Rotorgeeks", "Loc8tor", "Skyzone", "T-Motor", "Zippy", "FrSKY"]
CORRECT = {"Abusemark": "AbuseMark", "FrSKY": "FrSky", "HQ Prop": "HQProp", "Orange": "OrangeRx"}
PREFIX_TO_MANUFACTURER = {"Nano-Tech": "Turnigy"}
STRIP_PREFIX = {"HQProp": ["HQ"], "Lemon Rx": ["Lemon"]}
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
        item["url"] = response.url
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
        return item
