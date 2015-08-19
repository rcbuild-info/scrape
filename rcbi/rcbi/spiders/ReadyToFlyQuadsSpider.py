import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

MANUFACTURERS = ["Tiger", "RTF ", "HQ Prop", "Lemon"]
CORRECT = {"Tiger": "T-Motor", "RTF ": "ReadyToFlyQuads", "HQ Prop": "HQProp", "Lemon": "Lemon Rx"}
class ReadyToFlyQuadsSpider(CrawlSpider):
    name = "readytoflyquads"
    allowed_domains = ["readytoflyquads.com"]
    start_urls = ["http://www.readytoflyquads.com/catalog/seo_sitemap/product/"]

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(LinkExtractor(allow=('seo_sitemap/product/', ))),

        # Extract links matching 'item.php' and parse them with the spider's method parse_item
        Rule(LinkExtractor(allow=('/.*', )), callback='parse_item'),
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
        item["site"] = self.name
        item["url"] = response.url
        product_name = response.css("div.product-name")
        if not product_name:
            return
        item["name"] = product_name[0].xpath("//h1/text()").extract()[0].strip()
        for m in MANUFACTURERS:
          if item["name"].startswith(m):
            item["name"] = item["name"][len(m):].strip()
            if m in CORRECT:
              m = CORRECT[m]
            item["manufacturer"] = m
            break
        return item
