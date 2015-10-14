# -*- coding: utf-8 -*-
import scrapy
from scrapy import log
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from rcbi.items import Part

import re

WAREHOUSE_RE=re.compile("\( ?(RU|USA|US|AR|AUS|AU|EU|UK|NL) [Ww]arehouse ?\)")
MANUFACTURERS = ["Turnigy", "Walkera", "ZTW", "Zippy", "Rhino", "Hobbywing", "OrangeRx", "HobbyKing", "Goteck", "Futaba", "Flycolor", "Corona"]
CORRECT = {"ZIPPY": "Zippy", "TURNIGY": "Turnigy", "OrangeRX": "OrangeRx", "Hobbyking": "HobbyKing", u"Hobbyking™": "HobbyKing", u"HobbyKing™": "HobbyKing", u"Hobbyking® ™": "HobbyKing", u"HobbyKing® ™" : "HobbyKing", u"Hobbyking®" : "HobbyKing", u"HobbyKing®" : "HobbyKing", "Hobby King": "HobbyKing", u"Durafly™": "Durafly"}
MANUFACTURERS.extend(CORRECT)
MANUFACTURERS.sort(key=lambda x: len(x), reverse=True)
NEW_PREFIX = {}
class HobbyKingSpider(CrawlSpider):
  name = "hobbyking"
  allowed_domains = ["hobbyking.com"]
  start_urls = ["http://www.hobbyking.com/"]

  rules = (
    Rule(LinkExtractor(restrict_css=["#nav", ".paging"])),
    Rule(LinkExtractor(restrict_xpaths="//*[@id=\"tableContent\"]/div/table[2]/tr/td[2]/a")),
    Rule(LinkExtractor( restrict_xpaths=["//*[@id=\"tableContent\"]/div/table[2]/tr/td/table/tr[2]/td[2]/table/tr/td[2]/div[1]", "//*[@id=\"tableContent\"]/div/table[2]/tr/td/table/tr[2]/td[2]/table/tr/td[2]/div[2]/div[5]/div[3]"]), callback='parse_item'),
  )

  def parse_item(self, response):
    item = Part()
    item["site"] = self.name
    product_name = response.css("#productDescription")
    if not product_name:
      return

    variant = {}
    item["variants"] = [variant]

    variant["url"] = response.url
    item["name"] = product_name[0].xpath("text()").extract()[0]
    suffix = WAREHOUSE_RE.search(item["name"])
    if suffix != None:
      item["name"] = item["name"][:suffix.start()].strip()

    headers = response.xpath("//*[@class=\"data_tbl\"]/table/tr/td/table/tr[2]/td[2]/table/tr/td[1]/span/table/tr/td[1]/text()")
    details = response.xpath("//*[@class=\"data_tbl\"]/table/tr/td/table/tr[2]/td[2]/table/tr/td[1]/span/table/tr/td[2]/text()")
    manufacturer = None
    for i, header in enumerate(headers):
      header = header.extract()
      if len(header) == 0:
        continue
      data = details[i].extract()
      if header == "Weight (g)":
        item["weight"] = data

    price = response.css("#price_lb")
    if price:
      variant["price"] = price[0].xpath("text()").extract()[0].strip()

    stock = response.css("#pstock2")
    if stock:
      q = stock[0].xpath("text()").extract()[0]
      if q == "BK":
        variant["stock_state"] = "backordered"
      elif q == "0":
        variant["stock_state"] = "out_of_stock"
        variant["stock_text"] = q
      else:
        variant["stock_state"] = "in_stock"
        variant["stock_text"] = q

    sku = response.css("#desc_sku")
    if sku:
      item["sku"] = sku[0].xpath("text()").extract()[0]

    variant["location"] = response.xpath("//*[@id=\"details\"]/div[1]/div[2]/div/table/tbody/tr[1]/td[2]/text()").extract()[0].strip()

    if not manufacturer:
      for m in MANUFACTURERS:
        if item["name"].startswith(m):
          item["name"] = item["name"][len(m):].strip("- ")
          item["manufacturer"] = m
          break
    else:
      item["manufacturer"] = manufacturer

    if "manufacturer" in item:
      m = item["manufacturer"]
      if m in NEW_PREFIX:
        item["name"] = NEW_PREFIX[m] + " " + item["name"]
      if m in CORRECT:
        item["manufacturer"] = CORRECT[m]
        m = CORRECT[m]
      if item["name"].startswith(m):
        item["name"] = item["name"][len(m):].strip("- ")
    return item
