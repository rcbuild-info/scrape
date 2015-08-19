#!/usr/bin/python

import os
import os.path
import sys
import json

def stripManufacturerPrefix(manufacturer, destinations, test = False):
  correct = manufacturer
  if ":" in manufacturer:
    s = manufacturer.split(":")
    manufacturer = s[0]
    correct = s[1]

  for destination in destinations:
    if not os.path.isfile(destination) or os.path.islink(destination):
      continue

    with open(destination, "r") as f:
      part = json.load(f)

    if not part["name"].startswith(manufacturer):
      continue

    part["name"] = part["name"][len(manufacturer):].strip()
    part.update({"manufacturer": correct})

    new_destination = part["manufacturer"].replace(" ", "-") + "/" + part["name"].replace(" ", "-").replace("/", "-") + ".json"

    if not test:
      with open(new_destination, "w") as f:
        f.write(json.dumps(part, indent=1, sort_keys=True, separators=(',', ': ')))
      os.remove(destination)
    else:
      print(new_destination)
      print(part)
      print

if __name__ == "__main__":
  manufacturer = sys.argv[1].decode("utf-8")
  destinations = sys.argv[2:]
  stripManufacturerPrefix(manufacturer, destinations)
