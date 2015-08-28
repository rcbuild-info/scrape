import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

MANUFACTURERS = ["Rctimer", "RCTimer", "BaseCam", "Elgae", "ELGAE", "ArduFlyer", "Boscam", "T-Motor", "HQProp", "Suppo", "Flyduino", "SLS", "Frsky"]
CORRECT = {"Rctimer": "RCTimer", "ELGAE": "Elgae", "Frsky": "FrSky"}
class FlyduinoSpider(CrawlSpider):
    name = "flyduino"
    allowed_domains = ["flyduino.net"]
    start_urls = ["http://flyduino.net/"]

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(LinkExtractor(restrict_css=".categories")),

        # Extract links matching 'item.php' and parse them with the spider's method parse_item
        Rule(LinkExtractor(restrict_css=".article_wrapper h3"), callback='parse_item'),
    )

    def parse_item(self, response):
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
