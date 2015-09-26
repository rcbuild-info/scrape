import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

import copy
import re
import string

CORRECT = {"BlackOut": "Blackout",
           "BobSmithIndustries": "Bob Smith Industries",
           "FeiyuTech": "Feiyu Tech",
           "LawMate": "Lawmate",
           "Shen Drones": "Shendrones",
           "Sky Hero": "SKY Hero",
           "Skylark": "Skylark FPV",
           "SunnySky": "Sunnysky",
           "Tiger Motors": "T-Motor"}
STOCK_STATE_MAP = {"backordered": "backordered",
                   "expected-on": "out_of_stock",
                   "in-stock": "in_stock",
                   "out-of-stock": "out_of_stock"}
STRIP_PREFIX = {"Tiger Motors": ["Tiger Motor", "Tiger"]}
QUANTITY_REGEXS = [re.compile("\(Set of (?P<set>[0-9]+)(( -)? (?P<color>\w+))\)"),
                   re.compile("\(((?P<set>[0-9]+) [pP]ack(( -)? (?P<color>\w+)))?\)"),
                   re.compile("\(((?P<color>\w+)( -)? )?(?P<set>[0-9]+) [pP]ack\)")]
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
        product_name = response.css("div.product-name")
        if not product_name:
            return
        item = Part()
        item["site"] = "getfpv"
        item["name"] = product_name[0].xpath("//h1/text()").extract()[0]

        variant = {}
        variant["timestamp"] = response.headers["Date"]
        if "Last-Modified" in response.headers:
          variant["timestamp"] = response.headers["Last-Modified"]
        item["variants"] = [variant]

        headers = response.css("#product-attribute-specs-table th")
        data = response.css("#product-attribute-specs-table td")
        manufacturer = None
        for i, header in enumerate(headers):
            header = header.xpath("text()").extract()[0]
            if header == "Manufacturer":
              manufacturer = data[i].xpath("text()").extract()[0]
            elif header == "SKU":
              item["sku"] = data[i].xpath("text()").extract()[0].strip()
        if manufacturer and manufacturer != "No":
          item["manufacturer"] = manufacturer

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

        variant["url"] = response.url

        availability = response.css("#div_availability::attr(class)")
        if availability and availability.extract_first() != "unknown-stock-status":
          variant["stock_state"] = STOCK_STATE_MAP[availability.extract_first()]
          variant["stock_text"] = response.css("#div_availability::text").extract_first().strip()

        price = response.css(".product-essential .regular-price .price::text")
        if price:
          special = response.css(".product-essential .special-price .price::text")
          if special:
            variant["price"] = special.extract_first().strip()
          else:
            variant["price"] = price.extract_first().strip()

        # Handle quantity
        for r in QUANTITY_REGEXS:
          q_match = r.search(item["name"])
          if q_match:
            d = q_match.groupdict()
            if d["set"]:
              variant["quantity"] = int(d["set"])
            elif d["pair"]:
              variant["quantity"] = 2 * int(d["pair"])
            if d["color"]:
              variant["description"] = d["color"]
            break

        # Handle tiered pricing for items we know the quantity for.
        if "quantity" in variant:
          tiers = response.css(".tier-price")
          for tier in tiers:
            q = int(tier.css("::text").extract_first().strip().split()[1])
            each_price = tier.css(".price::text").extract_first()
            if each_price[0] != "$":
              continue
            total_price = float(each_price[1:]) * q
            total_price = each_price[0] + "{:.2f}".format(total_price)
            tiered_variant = copy.deepcopy(variant)
            tiered_variant["quantity"] = variant["quantity"] * q
            tiered_variant["price"] = total_price
            item["variants"].append(tiered_variant)


        return item
