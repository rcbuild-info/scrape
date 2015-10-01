#!/usr/bin/python

import os
import os.path
import sys
import json

def maybe_update_to_2(part_info):
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

DIRECTORY = "/home/tannewt/code/rcbuild.info-parts"
def merge(original, new):
  if "name" not in original or not original["name"]:
    original["name"] = new["name"]
  if "manufacturer" in new and ("manufacturer" not in original or not original["manufacturer"]):
    original["manufacturer"] = new["manufacturer"]
  for urltype in ["manufacturer", "related"]:
    for url in new["urls"][urltype]:
      if url not in original["urls"][urltype]:
        original["urls"][urltype].append(url)
  if not original["weight"] and new["weight"]:
    original["weight"] = new["weight"]
  for variant in new["variants"]:
    if variant.keys() == ["url"]:
      continue
    original["variants"].append(variant)
  original["variants"].sort(key=lambda x: x["url"])
  return original


def mergeFiles(merges, destination, part = None, test = False, override=None):
  if os.path.islink(destination):
    destination = os.realpath(destination)
  if os.path.isfile(destination):
    with open(destination, "r") as f:
      destination_part = json.load(f)
      maybe_update_to_2(destination_part)
      if part:
        part.update(destination_part)
      else:
        part = destination_part
  for fn in merges:
    if os.path.islink(fn):
      continue
    with open(fn, "r") as f:
      this_part = json.load(f)
      maybe_update_to_2(this_part)
      if part:
        part = merge(part, this_part)
      else:
        part = this_part

  if override:
    part.update(override)

  for fn in merges:
    target = os.path.relpath(destination, os.path.dirname(fn))
    if not test and fn != target:
      os.remove(fn)
      os.symlink(target, fn)
    else:
      print("symlink " + fn + " -> " + target)
  if not test:
    with open(destination, "w") as f:
      f.write(json.dumps(part, indent=1, sort_keys=True, separators=(',', ': ')))
  else:
    print(destination)
    print(part)
    print

if __name__ == "__main__":
  merges = sys.argv[1:-1]
  destination = sys.argv[-1]
  mergeFiles(merges, destination)
