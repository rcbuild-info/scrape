# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import os
import os.path

from scrapy import log
from scrapy.conf import settings

class JsonFileMergerPipeline(object):
    def open_spider(self, spider):
        self.root = spider.settings["JSON_FILE_DIRECTORY"]
        self.part_skeleton = spider.settings["PART_SKELETON_FILE"]
        
    def process_item(self, item, spider):
        if item["manufacturer"]:
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
        else:
            with open(self.part_skeleton, "r") as f:
                part_info = json.loads(f.read())
        if "name" not in part_info or not part_info["name"]:
            part_info["name"] = item["name"]
        if "manufacturer" not in part_info or not part_info["manufacturer"]:
            part_info["manufacturer"] = item["manufacturer"]
        if "url" not in part_info:
            part_info["url"] = [item["url"]]
        elif item["url"] not in part_info["url"]:
            part_info["url"].append(item["url"])
        part_info["url"] = filter(bool, part_info["url"])
        # also catalog subpart ids
        # also catalog interchangeable parts
        with open(full_fn, "w") as f:
            f.write(json.dumps(part_info, indent=1))
        return item
