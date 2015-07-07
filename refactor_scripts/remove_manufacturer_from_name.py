#!/usr/bin/python

import os
import os.path
import json

DIRECTORY = "/home/tannewt/code/rcbuild.info-parts"

def merge(original, new):
    if "name" not in original or not original["name"]:
        original["name"] = new["name"]
    if "manufacturer" in new and ("manufacturer" not in original or not original["manufacturer"]):
        original["manufacturer"] = new["manufacturer"]
    for urltype in ["store", "manufacturer", "related"]:
        for url in new["urls"][urltype]:
            if url not in original["urls"][urltype]:
                original["urls"]["store"].append(url)
    return original

for dirpath, dirnames, filenames in os.walk(DIRECTORY):
  if dirpath.find(".git") > -1:
    continue
  for filename in filenames:
    if filename[-4:] != "json":
      continue
    fn = os.path.join(dirpath, filename)
    if os.path.islink(fn):
      continue
    part = {}
    with open(fn, "r") as f:
      part = json.load(f)
    if not part["manufacturer"]:
      continue
    if part["name"].startswith(part["manufacturer"]):
      part["name"] = part["name"][len(part["manufacturer"]):]

    fn = os.path.join(dirpath, filename)
    bn = os.path.basename(dirpath)
    if filename.startswith(bn):
      fn = os.path.join(dirpath, filename[len(bn):].strip("-"))
    else:
      continue
    if os.path.isfile(fn):
        existing = {}
        with open(fn, "r") as f:
          existing = json.load(f)
        part = merge(existing, part)
        print(fn, "exists!", part)
    else:
      os.remove(os.path.join(dirpath, filename))
    with open(fn, "w") as f:
      json.dump(part, f, indent=1, sort_keys=True)
