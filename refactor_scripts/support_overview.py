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

    if "category" in part and part["category"] != "":
      supported_count += 1
    elif "categories" in part and len(part["categories"]) > 0:
      supported_count += 1
    else:
      unsupported_count += 1
  TOTAL_PARTS += unsupported_count + supported_count
  TOTAL_SUPPORTED += supported_count

  if unsupported_count > 0:
    UNSUPPORTED_DIR_COUNT.append((dirpath, unsupported_count))

UNSUPPORTED_DIR_COUNT.sort(key=lambda x: x[1])
for d in UNSUPPORTED_DIR_COUNT:
  print(d[0], d[1], 100 * d[1] / (TOTAL_PARTS - TOTAL_SUPPORTED), "%")

print()
print(TOTAL_SUPPORTED, "supported")
print(TOTAL_PARTS, "total")
print(100 * TOTAL_SUPPORTED / TOTAL_PARTS, "%")
