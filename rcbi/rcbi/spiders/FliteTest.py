import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

MANUFACTURERS = ["Graupner", "Flite Test", "FT"]
CORRECT = {"FT": "Flite Test"}
NEW_PREFIX = {}
QUANTITY = {}
class FliteTestSpider(CrawlSpider):
  name = "flitetest"
  allowed_domains = ["store.flitetest.com"]
  start_urls = ["http://store.flitetest.com/"]

  rules = (
      Rule(LinkExtractor(restrict_css=[".category-list", ".pagination"])),
      Rule(LinkExtractor(restrict_css=".ProductName"), callback='parse_item'),
  )

  def parse_item(self, response):
    item = Part()
    item["site"] = self.name
    product_name = response.css("[itemprop=\"name\"]")
    if not product_name:
      return
    item["name"] = product_name[0].xpath("text()").extract()[0].strip()

    variant = {}
    item["variants"] = [variant]
    variant["url"] = response.url

    price = response.css(".VariationProductPrice")
    if price:
      variant["price"] = price.xpath("text()").extract()[0].strip()
    else:
      price = response.css(".RetailPrice")
      if price:
        variant["price"] = price.xpath("text()").extract()[0].strip()

    for quantity in QUANTITY:
      if quantity in item["name"]:
        variant["quantity"] = QUANTITY[quantity]
        item["name"] = item["name"].replace(quantity, "")

    add_to_cart = response.css(".AddToCartButtonRow::attr(style)")
    if add_to_cart:
      style = add_to_cart.extract_first().strip()
      if style == "display:":
        variant["stock_state"] = "in_stock"
      else:
        variant["stock_state"] = "out_of_stock"

    for m in MANUFACTURERS:
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
