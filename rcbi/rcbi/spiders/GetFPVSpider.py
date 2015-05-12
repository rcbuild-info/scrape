import scrapy
from scrapy import log
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from rcbi.items import Part

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
        item["manufacturer"] = manufacturer
        item["site"] = "getfpv"
        item["url"] = response.url
        product_name = response.css("div.product-name")
        if not product_name:
            return
        item["name"] = product_name[0].xpath("//h1/text()").extract()[0]
        return item