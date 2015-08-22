#!/usr/bin/python

import os
import os.path
import string

import merge

DIRECTORY = "/Users/tannewt/case/parts/HQProp"

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
         "3DBN": "3D Bullnose",
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
  if "Carbon" in parts or "CF" in parts or "carbon" in parts or "(CF" in parts:
    material = "CF"
  if "Slow" in parts or "SF" in parts or "slowflyer" in parts:
    style = "SF"
  elif "reversible" in parts or "3D" in parts:
    style = "3D"
    if "Bull" in parts:
      style = "3DBN"
  elif "E" in parts or "Electric" in parts:
    style = "E"
  elif "DJI" in parts or  "MM" in parts or "MR" in parts or "Multi" in parts or "Multirotor" in parts or "AP" in parts or "multirotor" in parts:
    style = "MR"
  elif "Bullnose" in parts or "(Bullnose)" in parts or "BN" in parts or "bullnose" in parts:
    style = "BN"
  elif "Wood" in parts or "W" in parts:
    style = "W"
    material = "W"

  # Find the size and standardize to LENGTHxPITCH[xBLADES].
  for i, part in enumerate(parts):
    if any(char.isdigit() for char in part):
      if i +1 < len(parts) and parts[i+1] == "x" and i + 2 < len(parts) and all(char.isdigit() or char in [",", "."] for char in parts[i+2]):
        pitch = parts[i+2].replace(",", ".")
        if len(pitch) == 2:
          pitch = pitch[0] + "." + pitch[1]
        size = part.strip('"') + "x" + pitch
      elif "x" in part or "X" in part:
        if part[0] == "x":
          size = parts[i-1].translate(None, '"') + part
        else:
          size = part.translate(None, '"').replace("X", "x").replace(",", ".")
        if part[-1] == "x":
          size += parts[i + 1]
        size = size.strip(string.letters)
        break
      elif len(part) >= 4 and "m" not in part:
        length = part[0]
        if length == "1" or length == "2":
          length += part[1]
        elif part[1] != "0":
          length += "." + part[1]
        pitch = part[2]
        if part[3] != "0":
          pitch += "." + part[3]
        size = length + "x" + pitch

  for term in ["Three-Blade", "3-Blade", "3-bladed", "Triblade", "Dreiblatt"]:
    if term in filename[:-5]:
      size += "x3"
      break

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
  files_to_merge = GROUPING[k]
  if fn in files_to_merge:
    files_to_merge.remove(fn)
  if len(files_to_merge) == 0:
    continue
  merge.mergeFiles([os.path.join(DIRECTORY, x) for  x in files_to_merge],
                   os.path.join(DIRECTORY, fn), part=base_part)
  print(fn)
  for m in files_to_merge:
    print("\t" + m)
  print

print("skipped")
for v in SKIPPED:
  print(v)
