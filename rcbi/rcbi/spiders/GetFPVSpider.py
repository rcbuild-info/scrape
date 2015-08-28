import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

import string

CORRECT = {"BlackOut": "Blackout",
           "BobSmithIndustries": "Bob Smith Industries",
           "FeiyuTech": "Feiyu Tech",
           "LawMate": "Lawmate",
           "Skylark": "Skylark FPV",
           "SunnySky": "Sunnysky",
           "Tiger Motors": "T-Motor"}
STRIP_PREFIX = {"Tiger Motors": ["Tiger Motor", "Tiger"]}
class GetFPVSpider(CrawlSpider):
    name = "getfpv"
    allowed_domains = ["getfpv.com"]
    start_urls = ["http://www.getfpv.com/catalog/seo_sitemap/product/"]

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(LinkExtractor(allow=('seo_sitemap/product/', ))),

        # Extract links matching 'item.php' and parse them with the spider's method parse_item
        Rule(LinkExtractor(allow=('.*html', )), callback='parse_item'),
    )

    def parse_item(self, response):
        headers = response.css("#product-attribute-specs-table th")
        data = response.css("#product-attribute-specs-table td")
        manufacturer = None
        for i, header in enumerate(headers):
            header = header.xpath("text()").extract()[0]
            if header == "Manufacturer":
                manufacturer = data[i].xpath("text()").extract()[0]
        item = Part()
        if manufacturer and manufacturer != "No":
          item["manufacturer"] = manufacturer
        item["site"] = "getfpv"
        item["url"] = response.url
        product_name = response.css("div.product-name")
        if not product_name:
            return
        item["name"] = product_name[0].xpath("//h1/text()").extract()[0]
        if "manufacturer" in item:
            m = item["manufacturer"]
            if m in STRIP_PREFIX:
              for prefix in STRIP_PREFIX[m]:
                if item["name"].startswith(prefix):
                  item["name"] = item["name"][len(prefix):]
            if m in CORRECT:
              item["manufacturer"] = CORRECT[m]
              if item["name"].startswith(CORRECT[m]):
                item["name"] = item["name"][len(CORRECT[m]):]
            if item["name"].startswith(m):
              item["name"] = item["name"][len(m):]
            item["name"] = item["name"].rstrip(string.whitespace).lstrip(string.whitespace + string.punctuation)
            if m == "GetFPV Affiliate":
              item.pop("manufacturer", None)
        return item
