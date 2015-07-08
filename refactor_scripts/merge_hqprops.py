#!/usr/bin/python

import os
import os.path
import string

import merge

DIRECTORY = "/home/tannewt/code/rcbuild.info-parts/HQProp"

GROUPING = {}
SKIPPED = []

MATERIAL = {"W": "Wood",
            "CF": "Carbon Fiber Composite",
            "FG": "Fiberglass Composite"}
STYLE = {"DD": "Direct Drive",
         "W": "",
         "MR": "Multirotor",
         "SF": "Slow Flyer",
         "3D": "3D",
         "E": "Electric",
         "BN": "Bullnose"}

for filename in os.listdir(DIRECTORY):
  if os.path.islink(os.path.join(DIRECTORY, filename)):
    continue
  if filename[-4:] != "json":
    continue
  size = None
  material = "FG"
  style = "DD"

  parts = filename[:-5].split("-")
  if "Carbon" in parts or "CF" in parts:
    material = "CF"
  if "Slow" in parts or "SF" in parts:
    style = "SF"
  elif "reversible" in parts or "3D" in parts:
    style = "3D"
  elif "E" in parts or "Electric" in parts:
    style = "E"
  elif "DJI" in parts or  "MM" in parts or "MR" in parts or "Multi" in parts or "Multirotor" in parts or "AP" in parts:
    style = "MR"
  elif "Bullnose" in parts or "(Bullnose)" in parts:
    style = "BN"
  elif "Wood" in parts:
    style = "W"
    material = "W"

  # Find the size and standardize to LENGTHxPITCH[xBLADES].
  for i, part in enumerate(parts):
    if any(char.isdigit() for char in part):
      if "x" in part or "X" in part:
        size = part.translate(None, '"').replace("X", "x").replace(",", ".")
        if part[-1] == "x":
          size += parts[i + 1]
        size = size.strip(string.letters)
        break
      elif len(part) >= 4 and "m" not in part:
        length = part[0]
        if part[1] != "0":
          length += "." + part[1]
        pitch = part[2]
        if part[3] != "0":
          pitch += "." + part[3]
        size = length + "x" + pitch

  t = (size, material, style)

  if any(x is None for x in t):
    SKIPPED.append(filename)
    continue
  if t not in GROUPING:
    GROUPING[t] = []
  GROUPING[t].append(filename)

keys = GROUPING.keys()
keys.sort()
for k in keys:
  fn = "-".join(k) + ".json"
  size, material, style = k
  name = " ".join((size, STYLE[style], MATERIAL[material]))
  base_part = {u'category': u'prop', u'name': name, u'subpart': [], u'equivalent': [], u'urls': {u'store': [], u'related': [], u'manufacturer': []}, u'manufacturer': u'HQProp', u'replacement': []}
  merge.mergeFiles([os.path.join(DIRECTORY, x) for  x in GROUPING[k]],
                   os.path.join(DIRECTORY, fn), part=base_part)
  print(k)
  for v in GROUPING[k]:
    print("\t" + v)
  print

for v in SKIPPED:
  print(v)
