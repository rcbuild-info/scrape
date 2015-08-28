#!/usr/bin/python

import os
import os.path
import sys
import json

def overwriteFields(overwrite, destinations, test = False):
  for destination in destinations:
    if not os.path.isfile(destination) or os.path.islink(destination):
      continue

    with open(destination, "r") as f:
      part = json.load(f)

    part.update(overwrite)

    if not test:
      with open(destination, "w") as f:
        f.write(json.dumps(part, indent=1, sort_keys=True, separators=(',', ': ')))
    else:
      print(destination)
      print(part)
      print

if __name__ == "__main__":
  overwrite = sys.argv[1]
  destinations = sys.argv[2:]
  overwriteFields(json.loads(overwrite), destinations)
