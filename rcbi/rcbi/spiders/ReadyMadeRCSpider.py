import scrapy
from scrapy import log
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from rcbi.items import Part

import urlparse
import urllib

MANUFACTURERS = ["Blackout", "Abusemark", "DuBro", "Eagle Tree", "DroneKraft",
                 "EMAX", "Sunnysky", "Tiger Motor", "Gemfan", "DYS", "Pololu",
                 "Gens Ace", "SmartFPV", "FatShark", "RMRC", "Sasquatch Labs",
                 "TGA Frames", "Society 808", "TrueRC", "Drone Frames", "XOAR",
                 "Happy Flyers", "Finwing", "EyeFly", "CXN", "Zeiss", "FrSky",
                 "Castle Creations", "AIMDROIX", "3DR", "APC",
                 "Direct Drive HQ Prop", "DJI", "Dubro", "Electric (E) HQ Prop",
                 "Flying Cinema", "Fr Sky", "FrSKY", "Xhover",
                 "Multirotor HQ Prop", "Wood HQ Prop"]
CORRECT = {"RMRC - Made in China" : "ReadyMadeRC", "RMRC": "ReadyMadeRC",
           "TGA Frames" : "TGA Frame", "Eagle Tree": "Eagle Tree Systems",
           "CXN": "CXN Designs", "3DR": "3DRobotics", "Tiger Motor": "T-Motor",
           "Abusemark": "AbuseMark", "Direct Drive HQ Prop": "HQProp",
           "Dubro" : "DuBro", "Electric (E) HQ Prop": "HQProp",
           "Fr Sky": "FrSky", "FrSKY": "FrSky", "Multirotor HQ Prop": "HQProp",
           "Slow Fly HQ Prop": "HQProp", "Wood HQ Prop": "HQProp",
           "Xhover": "XHover", "RC Tiger Motor": "T-Motor"}
NEW_PREFIX = {"Direct Drive HQ Prop": "Direct Drive",
              "Electric (E) HQ Prop": "Electric",
              "Multirotor HQ Prop": "Multirotor",
              "Slow Fly HQ Prop": "Slow Fly",
              "Wood HQ Prop": "Wood"}
class ReadyMadeRCSpider(CrawlSpider):
    name = "readymaderc"
    allowed_domains = ["readymaderc.com"]
    start_urls = ["http://www.readymaderc.com/store/index.php?main_page=site_map"]

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(LinkExtractor(allow=('.*main_page=index.*', ))),

        # Extract links matching 'item.php' and parse them with the spider's method parse_item
        Rule(LinkExtractor(allow=('.*products_id.*', )), callback='parse_item'),
    )

    def parse_item(self, response):
        headers = response.css("#productDetailsList li")
        manufacturer = None
        for i, header in enumerate(headers):
            header = header.xpath("text()").extract()[0]
            if header.startswith("Manufactured by or for: "):
                manufacturer = header[len("Manufactured by or for: "):]
        item = Part()
        if manufacturer:
          item["manufacturer"] = manufacturer
        item["site"] = self.name
        parsed = urlparse.urlparse(response.url)
        qs = urlparse.parse_qs(parsed.query)
        qs.pop("cPath", None)
        # By default all values in qs will be a list and cause funky % encoding
        # in the resulting url. So, if the list is one value then we replace the
        # list with it.
        for k in qs:
            if len(qs[k]) == 1:
                qs[k] = qs[k][0]
        item["url"] = urlparse.urlunparse((parsed[0], parsed[1], parsed[2],
                                           parsed[3], urllib.urlencode(qs),
                                           parsed[5]))
        product_name = response.css("#productListHeading")
        if not product_name:
            return
        item["name"] = product_name[0].xpath("text()").extract()[0]
        this_manufacturer = []
        if "manufacturer" in item:
          this_manufacturer = [item["manufacturer"]]
        for m in MANUFACTURERS + this_manufacturer:
          if item["name"].startswith(m):
            item["name"] = item["name"][len(m):].strip("- ")
            if "manufacturer" not in item:
              item["manufacturer"] = m
              break
        if "manufacturer" in item:
            m = item["manufacturer"]
            if m in NEW_PREFIX:
              item["name"] = NEW_PREFIX[m] + " " + item["name"]
            if m in CORRECT:
              item["manufacturer"] = CORRECT[m]
        return item
