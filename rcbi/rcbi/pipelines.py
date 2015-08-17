# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import os
import os.path
import urlparse

from scrapy import log
from scrapy.conf import settings

class JsonFileMergerPipeline(object):
    def open_spider(self, spider):
        self.root = spider.settings["JSON_FILE_DIRECTORY"]
        self.part_skeleton = spider.settings["PART_SKELETON_FILE"]

    def process_item(self, item, spider):
        if "manufacturer" in item and item["manufacturer"]:
            fn = item["manufacturer"].replace(" ", "-") + "/" + item["name"].replace(" ", "-").replace("/", "-") + ".json"
        else:
            fn = "UnknownManufacturer/" + item["site"] + "/" + item["name"].replace(" ", "-").replace("/", "-") + ".json"
        full_fn = os.path.join(self.root, fn)
        d = os.path.dirname(full_fn)
        if not os.path.isdir(d):
            os.makedirs(d)
        part_info = {}
        if os.path.isfile(full_fn):
          with open(full_fn, "r") as f:
            part_info = json.loads(f.read())
        elif os.path.islink(full_fn):
          full_fn = os.path.realpath(full_fn)
          with open(full_fn, "r") as f:
            part_info = json.loads(f.read())
        else:
          with open(self.part_skeleton, "r") as f:
            part_info = json.loads(f.read())

        # Scraped parts now have weight and price but I'm not sure how we want
        # to store it here. So we drop it for now.
        if "name" not in part_info or not part_info["name"]:
            part_info["name"] = item["name"]
        if "manufacturer" in item and ("manufacturer" not in part_info or not part_info["manufacturer"]):
            part_info["manufacturer"] = item["manufacturer"]
        if "urls" not in part_info:
            part_info["urls"] = {}
            part_info["urls"]["store"] = [item["url"]]
        elif item["url"] not in part_info["urls"]["store"]:
            part_info["urls"]["store"].append(item["url"])
        part_info["urls"]["store"] = filter(bool, part_info["urls"]["store"])

        # Some stores provide the same item under different urls depending on
        # the category. In this case the filename is still the same so here we
        # ensure we only have one of them. We also start at the end of the list
        # so we keep the newest urls.
        store_urls = part_info["urls"]["store"]
        store_url_ids = set()
        unique_store_urls = []
        for url in reversed(store_urls):
          parsed = urlparse.urlparse(url)
          if parsed.query != "" or os.path.basename(parsed.path) == "":
            unique_store_urls.append(url)
            continue

          key = (parsed.netloc, os.path.basename(parsed.path))
          if key not in store_url_ids:
            unique_store_urls.append(url)
            store_url_ids.add(key)
        # Reverse the list again to approximate the original order.
        part_info["urls"]["store"] = list(reversed(unique_store_urls))
        # also catalog subpart ids
        # also catalog interchangeable parts
        with open(full_fn, "w") as f:
            f.write(json.dumps(part_info, indent=1, sort_keys=True, separators=(',', ': ')))
        return item
