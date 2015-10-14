import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

MANUFACTURERS = []
CORRECT = {"AbuseMarK": "AbuseMark", "Emax": "EMAX", "Fat Shark": "FatShark", "Gens ace": "Gens Ace", "Mobius": "SpyTec"}
NEW_PREFIX = {}
QUANTITY = {}
STOCK_STATE_MAP = {"This product is no longer in stock": "out_of_stock"}
class FPVRacingCHSpider(CrawlSpider):
  name = "fpvracingch"
  allowed_domains = ["fpvracing.ch"]
  start_urls = ["http://fpvracing.ch/"]

  rules = (
    Rule(LinkExtractor(restrict_css=["#block_top_menu", ".pagination"])),
    Rule(LinkExtractor(restrict_css=["h5[itemprop='name']"]), callback='parse_item'),
  )

  def parse_item(self, response):
    item = Part()
    item["site"] = self.name
    product_name = response.css("[itemprop='name']")
    if not product_name:
      return
    item["name"] = product_name[0].xpath("text()").extract()[0].strip()

    sku = response.css("[itemprop='sku']::text")
    if sku:
      item["sku"] = sku.extract_first().strip()

    manufacturer = response.css("#manufacturer span::text")
    if manufacturer:
      item["manufacturer"] = manufacturer.extract_first().strip()

    if "manufacturer" in item:
      m = item["manufacturer"]
      if item["name"].startswith(m):
        item["name"] = item["name"][len(m):].strip()
      if m in NEW_PREFIX:
        item["name"] = NEW_PREFIX[m] + " " + item["name"]
      if m in CORRECT:
        item["manufacturer"] = CORRECT[m]

    variant = {}
    item["variants"] = [variant]
    variant["url"] = response.url

    price = response.css("[itemprop='price']")
    if price:
      variant["price"] = price.css("::text").extract_first().strip()

    for quantity in QUANTITY:
      if quantity in item["name"]:
        variant["quantity"] = QUANTITY[quantity]
        item["name"] = item["name"].replace(quantity, "")

    stock = response.css("span.delivery-value::text")
    if stock:
      text = stock.extract_first().strip()
      variant["stock_text"] = text
      if text in STOCK_STATE_MAP:
        variant["stock_state"] = STOCK_STATE_MAP[text]
      elif text.endswith("Werktage"):
        variant["stock_state"] = "in_stock"
      else:
        print(text)

    return item
