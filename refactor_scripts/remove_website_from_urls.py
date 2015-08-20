#!/usr/bin/python

import os
import os.path
import json
import sys
import urlparse

DIRECTORY = "/Users/tannewt/case/parts"

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

    for website in sys.argv[1:]:
      for category in part["urls"]:
        part["urls"][category] = [url for url in part["urls"][category] if urlparse.urlsplit(url)[1] != website]

    with open(fn, "w") as f:
      json.dump(part, f, indent=1, sort_keys=True, separators=(',', ': '))
