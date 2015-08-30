#!/usr/bin/python

import copy
import os
import os.path
import sys

import merge

def setManufacturer(manufacturer, destinations, test=False):
  base_part = {u'category': "", u'name': "", u'subpart': [], u'equivalent': [], u'urls': {u'store': [], u'related': [], u'manufacturer': []}, u'manufacturer': manufacturer, u'replacement': []}

  for destination in destinations:
    destination = destination.decode("utf-8")
    new_destination = os.path.join(manufacturer.replace(" ", "-"), os.path.basename(destination))
    if test:
      print(destination, new_destination)
    else:
      merge.mergeFiles([destination], new_destination, part=copy.deepcopy(base_part))

if __name__ == "__main__":
  manufacturer = sys.argv[1].decode("utf-8")
  destinations = sys.argv[2:]
  setManufacturer(manufacturer, destinations)
