import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

import copy
import json
import re

VARIANT_JSON_REGEX = re.compile("product: ({.*}),")

class ShendronesSpider(CrawlSpider):
    name = "shendrones"
    allowed_domains = ["shendrones.myshopify.com"]
    start_urls = ["http://shendrones.myshopify.com/collections/all"]

    rules = (
        Rule(LinkExtractor(restrict_css=[".grid-item"]), callback='parse_item'),
    )

    def parse_item(self, response):
      item = Part()
      item["site"] = self.name

      variant = {}
      variant["timestamp"] = response.headers["Date"]
      if "Last-Modified" in response.headers:
        variant["timestamp"] = response.headers["Last-Modified"]
      item["variants"] = [variant]
      base_url = response.url

      item["manufacturer"] = "Shendrones"

      # Find the json info for variants.
      body = response.body_as_unicode()

      m = VARIANT_JSON_REGEX.search(body)
      if m:
        shopify_info = json.loads(m.group(1))
        global_title = shopify_info["title"]
        preorder = False
        if global_title.endswith("Pre Order"):
          global_title = global_title[:-len("Pre Order")].strip()
          variant["stock_state"] = "backordered"
          preorder = True
        for v in shopify_info["variants"]:
          if v["title"] != "Default Title":
            item["name"] = global_title + " " + v["title"]
            variant["url"] = base_url + "?variant=" + str(v["id"])
          else:
            item["name"] = global_title
            variant["url"] = base_url
          variant["price"] = "${:.2f}".format(v["price"] / 100)
          if not preorder:
            if v["inventory_quantity"] <= 0:
              if v["inventory_policy"] == "deny":
                variant["stock_state"] = "out_of_stock"
              else:
                variant["stock_state"] = "backordered"
            elif v["inventory_quantity"] < 3:
              variant["stock_state"] = "low_stock"
              variant["stock_text"] = "Only " + str(v["inventory_quantity"]) + " left!"
            else:
              variant["stock_state"] = "in_stock"

          yield item
          item = copy.deepcopy(item)
          variant = item["variants"][0]
