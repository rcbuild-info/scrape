import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

MANUFACTURERS = []
CORRECT = {}
NEW_PREFIX = {}
class ArmattanSpider(CrawlSpider):
  name = "armattan"
  allowed_domains = ["armattanquads.com"]
  start_urls = ["http://www.armattanquads.com/sitemap/categories/"]

  rules = (
    Rule(LinkExtractor(restrict_css=[".SubCategoryListGrid", ".SitemapCategories", ".PagingList"])),
    Rule(LinkExtractor(restrict_css=[".ProductDetails"]), callback='parse_item'),
  )

  def parse_item(self, response):
    item = Part()
    item["site"] = self.name
    product_name = response.css(".DetailRow")
    if not product_name:
      return
    item["name"] = product_name[0].xpath("//h1/text()").extract()[0].strip()

    if item["name"].startswith("Armattan"):
      item["name"] = item["name"][len("Armattan"):].strip()

    variant = {}
    item["variants"] = [variant]
    variant["url"] = response.url

    price = response.css(".ProductPrice")
    if price:
      variant["price"] = price.xpath("text()").extract()[0]

    add_to_cart = response.css(".BulkDiscount::attr(style)")
    if add_to_cart:
      style = add_to_cart.extract_first().strip()
      if style == "display:":
        variant["stock_state"] = "in_stock"
      else:
        variant["stock_state"] = "out_of_stock"

    # TODO(tannewt): Handle variants. It'll be tricky because selecting a
    # radio button triggers an AJAX call.

    item["manufacturer"] = "Armattan"
    return item
