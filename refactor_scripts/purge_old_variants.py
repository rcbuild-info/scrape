#!/usr/bin/python
from __future__ import print_function

import os
import os.path
import json


DIRECTORY = "/Users/tannewt/case/parts"

TOTAL_PARTS = 0
TOTAL_SUPPORTED = 0

UNSUPPORTED_DIR_COUNT = []

for dirpath, dirnames, filenames in os.walk(DIRECTORY):
  if dirpath.find(".git") > -1:
    continue
  unsupported_count = 0
  supported_count = 0
  for filename in filenames:
    if filename[-4:] != "json":
      continue
    fn = os.path.join(dirpath, filename)
    if os.path.islink(fn):
      continue
    part = {}

    with open(fn, "r") as f:
      part = json.load(f)

    if "version" not in part:
      #print(fn)
      continue

    invalid_variants = []
    for i, v in enumerate(part["variants"]):
      if len(v.keys()) == 1:
        invalid_variants.append(i)

    if len(invalid_variants) > 0:
      for i in reversed(invalid_variants):
        del part["variants"][i]
      with open(fn, "w") as f:
        f.write(json.dumps(part, indent=1, sort_keys=True, separators=(',', ': ')))
