#!/usr/bin/python

import os
import os.path
import sys
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


def mergeFiles(merges, destination, part = None, test = False):
  if os.path.isfile(destination):
    with open(destination, "r") as f:
      part = json.load(f)
  for fn in merges:
    with open(fn, "r") as f:
      this_part = json.load(f)
      if part:
        part = merge(part, this_part)
      else:
        part = this_part

  for fn in merges:
    target = os.path.relpath(destination, os.path.dirname(fn))
    if not test:
      os.remove(fn)
      os.symlink(target, fn)
    else:
      print("symlink " + fn + " -> " + target)
  if not test:
    with open(destination, "w") as f:
      json.dump(part, f, indent=1, sort_keys=True)
  else:
    print(destination)
    print(part)
    print

if __name__ == "__main__":
  merges = sys.argv[1:-1]
  destination = sys.argv[-1]
  mergeFiles(merges, destination)
