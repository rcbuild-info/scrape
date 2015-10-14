import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

import copy
import json
import re

import os.path
import urlparse
import urllib

MANUFACTURERS = ["Cobra", "DYS", "EchoQuad", "FlySky", "FrSky", "Diatone", "Gemfan", "ImmersionRC", "ZTW"]
CORRECT = {"HQ": "HQProp", "DAL": "Surveilzone", "OrangeRX": "OrangeRx"}
STRIP_PREFIX = ["HQ Prop", "OrangeRx"]

VARIANT_JSON_REGEX = re.compile("product: ({.*}),")

class ShendronesSpider(CrawlSpider):
  name = "flyingrobot"
  allowed_domains = ["flyingrobot.co"]
  start_urls = ["http://flyingrobot.co"]

  rules = (
    Rule(LinkExtractor(restrict_css=["nav.main", ".pagination"])),
    Rule(LinkExtractor(restrict_css=[".product .details"]), callback='parse_item'),
  )

  def parse_item(self, response):
    item = Part()
    item["site"] = self.name

    variant = {}
    item["variants"] = [variant]

    parsed = urlparse.urlparse(response.url)
    filename = "/products/" + os.path.basename(parsed[2])
    base_url = urlparse.urlunparse((parsed[0], parsed[1], filename,
                                          parsed[3], parsed[4], parsed[5]))

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

      if "vendor" in shopify_info:
        if shopify_info["vendor"] in MANUFACTURERS:
          item["manufacturer"] = shopify_info["vendor"]
          if global_title.startswith(item["manufacturer"]):
            global_title = global_title[len(item["manufacturer"]):].strip(" -")
        elif shopify_info["vendor"] in CORRECT:
          item["manufacturer"] = CORRECT[shopify_info["vendor"]]
        for strip in STRIP_PREFIX:
          if global_title.startswith(strip):
            global_title = global_title[len(strip):].strip(" -")

      for v in shopify_info["variants"]:
        if v["title"] != "Default Title":
          item["name"] = global_title + " " + v["title"]
          variant["url"] = base_url + "?variant=" + str(v["id"])
        else:
          item["name"] = global_title
          variant["url"] = base_url
        variant["price"] = "R {:.2f}".format(v["price"] / 100)
        if not preorder:
          if v["inventory_quantity"] <= 0:
            if v["inventory_policy"] == "deny":
              variant["stock_state"] = "out_of_stock"
            else:
              variant["stock_state"] = "backordered"
          elif v["inventory_quantity"] < 3:
            variant["stock_state"] = "low_stock"
            variant["stock_text"] = "Currently " + str(v["inventory_quantity"]) + " in stock."
          else:
            variant["stock_state"] = "in_stock"
            variant["stock_text"] = "Currently " + str(v["inventory_quantity"]) + " in stock."

        yield item
        item = copy.deepcopy(item)
        variant = item["variants"][0]
