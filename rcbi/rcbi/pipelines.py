# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import os
import os.path
import urlparse

import urlparse

from scrapy import log
from scrapy.conf import settings

class JsonFileMergerPipeline(object):
    def open_spider(self, spider):
        self.root = os.path.realpath(spider.settings["JSON_FILE_DIRECTORY"])
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

        while os.path.islink(full_fn):
          full_fn = os.path.realpath(full_fn)

        if "sku" in item and item["sku"] != "":
          sku_fn = os.path.join(self.root, "_skus/" + item["site"] + "/" + item["sku"].replace(" ", "-").replace("/", "-"))
          d = os.path.dirname(sku_fn)
          if not os.path.isdir(d):
              os.makedirs(d)
          if os.path.islink(sku_fn):
            new_full_fn = os.path.realpath(sku_fn)

            # Update the existing file to a link to the new one. This may lose info.
            if full_fn != new_full_fn:
              os.remove(full_fn)
              print(new_full_fn, full_fn)
              os.symlink(os.path.relpath(new_full_fn, os.path.dirname(full_fn)), full_fn)

            full_fn = new_full_fn
          else:
            # Create a sku link to our full_fn
            os.symlink(os.path.relpath(full_fn, os.path.dirname(sku_fn)), sku_fn)

        part_info = {}
        if os.path.isfile(full_fn):
          with open(full_fn, "r") as f:
            part_info = json.loads(f.read())
        else:
          with open(self.part_skeleton, "r") as f:
            part_info = json.loads(f.read())

            # Delete any example objects.
            for i, variant in enumerate(part_info["variants"]):
              if "example" in variant:
                del part_info["variants"][i]

        # Update to version 2.
        if "version" not in part_info:
          part_info["version"] = 2
          # Allow for multiple categories for parts such as PDBs that are also OSDs.
          if part_info["category"]:
            part_info["categories"] = [part_info["category"]]
          else:
            part_info["categories"] = []
          del part_info["category"]

          part_info["weight"] = ""

          # Store store urls as variants rather than a list so we know more about each.
          part_info["variants"] = []
          if "urls" in part_info and "store" in part_info["urls"]:
            for store_url in part_info["urls"]["store"]:
              part_info["variants"].append({"url": store_url})
          del part_info["urls"]["store"]


        # Scraped parts now have weight and price but I'm not sure how we want
        # to store it here. So we drop it for now.
        if "name" not in part_info or not part_info["name"]:
            part_info["name"] = item["name"]
        if "manufacturer" in item and ("manufacturer" not in part_info or not part_info["manufacturer"]):
            part_info["manufacturer"] = item["manufacturer"]
        if "weight" in item and ("weight" not in part_info or not part_info["weight"]):
          part_info["weight"] = item["weight"]

        # map existing urls to their variant object
        url_to_index = {}
        for i, variant in enumerate(part_info["variants"]):
          url_to_index[variant["url"]] = i

        # Update all variants from this one.
        for variant in item["variants"]:
          url = variant["url"]
          if url in url_to_index:
            part_info["variants"][url_to_index[url]].update(variant)
          else:
            part_info["variants"].append(variant)

        # also catalog subpart ids
        # also catalog interchangeable parts
        with open(full_fn, "w") as f:
            f.write(json.dumps(part_info, indent=1, sort_keys=True, separators=(',', ': ')))
        return item
