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
        if "name" not in part_info or not part_info["name"]:
            part_info["name"] = item["name"]
        if "manufacturer" in item and ("manufacturer" not in part_info or not part_info["manufacturer"]):
            part_info["manufacturer"] = item["manufacturer"]
        if "urls" not in part_info:
            part_info["urls"] = {}
            part_info["urls"]["store"] = [item["url"]]
        else:
          domain = urlparse.urlparse(item["url"]).netloc
          part_info["urls"]["store"] = filter(lambda x: urlparse.urlparse(x).netloc != domain, part_info["urls"]["store"])

          part_info["urls"]["store"].append(item["url"])
        part_info["urls"]["store"] = filter(bool, part_info["urls"]["store"])
        # also catalog subpart ids
        # also catalog interchangeable parts
        with open(full_fn, "w") as f:
            f.write(json.dumps(part_info, indent=1, sort_keys=True))
        return item
