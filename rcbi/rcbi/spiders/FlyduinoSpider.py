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
    Rule(LinkExtractor(restrict_css=".categories")),
    Rule(LinkExtractor(restrict_css=".article_wrapper h3"), callback='parse_item'),
  )

  def parse_item(self, response):
    item = Part()
    item["site"] = "flyduino"
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

    sku = response.css("#artnr::text")
    if sku:
      item["sku"] = sku.extract_first().strip()

    weight = response.css("#weight::text")
    if weight:
      item["weight"] = weight.extract_first().strip() + "kg"

    variant = {}
    item["variants"] = [variant]
    variant["url"] = response.url

    price = response.css("#price::text")
    if price:
      variant["price"] = price.extract_first().strip()

    availability = response.css(".signal_image")
    if availability:
      classes = availability.css("::attr(class)").extract_first().split()
      # Skip the text because it may be in German or English
      if "a2" in classes:
        variant["stock_state"] = "in_stock"
      elif "a1" in classes:
        variant["stock_state"] = "low_stock"
      elif "a0" in classes:
        variant["stock_state"] = "out_of_stock"

    return item
