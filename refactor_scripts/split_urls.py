#!/usr/bin/python

import os
import os.path
import json

DIRECTORY = "/home/tannewt/code/rcbuild.info-parts"

for dirpath, dirnames, filenames in os.walk(DIRECTORY):
  for filename in filenames:
    if filename[-4:] != "json":
      continue
    fn = os.path.join(dirpath, filename)
    print(fn)
    part = {}
    with open(fn, "r") as f:
      part = json.load(f)
    urls = {}
    urls["store"] = part["url"]
    urls["manufacturer"] = []
    urls["related"] = []
    part["urls"] = urls
    part.pop("url", None)
    print(part)
    with open(fn, "w") as f:
      json.dump(part, f, indent=1)