import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

MANUFACTURERS = ["Walkera", "Eachine", "DYS", "FrSky", "EMAX", "Feiyu Tech", "Tarot", "Gemfan", "Flysky", "ZTW", "Diatone", "Sunnysky", "RCTimer", "Hobbywing", "Boscam", "ImmersionRC", "SkyRC", "Aomway", "Flycolor"]
CORRECT = {"SKYRC": "SkyRC", "Emax": "EMAX", "Skyzone": "SkyZone", "AOMWAY": "Aomway", "SunnySky": "Sunnysky", "GEMFAN": "Gemfan", "FlySky": "Flysky"}
MANUFACTURERS.extend(CORRECT.keys())
NEW_PREFIX = {}
STRIP_PREFIX = ["New Version ", "Original ", "2 Pairs "]
class BanggoodSpider(CrawlSpider):
  name = "banggood"
  allowed_domains = ["banggood.com"]
  start_urls = ["http://www.banggood.com/Wholesale-Multi-Rotor-Parts-c-2520.html",
                "http://www.banggood.com/Wholesale-FPV-System--c-2734.html"]

  rules = (
    Rule(LinkExtractor(restrict_css=[".page_num"])),
    Rule(LinkExtractor(restrict_css=".title"), callback='parse_item'),
  )

  def parse_item(self, response):
    item = Part()
    item["site"] = self.name
    product_name = response.css(".good_main h1")
    if not product_name:
      return
    item["name"] = product_name[0].xpath("text()").extract()[0].strip()

    for prefix in STRIP_PREFIX:
      if item["name"].startswith(prefix):
        item["name"] = item["name"][len(prefix):]
        break

    sku = response.css("[itemprop=\"sku\"]::text")
    if sku:
      sku = sku.extract_first().strip()
      if sku[:3] == "SKU":
        sku = sku[3:]
      item["sku"] = sku

    variant = {}
    item["variants"] = [variant]
    variant["url"] = response.url

    buy_link = response.css(".buy_link")
    if buy_link:
      # They have a typo in their css class.
      preorder = buy_link.css(".perorder")
      buy_now = buy_link.css(".buynow")
      if preorder:
        variant["stock_state"] = "backordered"
      elif buy_now:
        variant["stock_state"] = "in_stock"
      else:
        print("unknown stock state")

    stock_text = response.css(".good_main .status")
    if "stock_state" in variant and stock_text:
      variant["stock_text"] = stock_text.xpath("string(.)").extract_first().strip()

    # TODO(tannewt): Support multiple Bangood warehouses.
    warehouse = response.css(".item_con .active::text")
    if warehouse:
      variant["location"] = warehouse.extract_first().strip()

    currency = response.css("[itemprop=\"priceCurrency\"]::attr(content)")
    if currency:
      price = response.css("[itemprop=\"price\"]::text")
      if price:
        currency = currency.extract_first()
        if currency != "USD":
          print(currency)
          return
        variant["price"] = "$" + price.extract_first().strip()

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
