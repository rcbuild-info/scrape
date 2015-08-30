#!/usr/bin/python

import os
import os.path
import string

import merge

DIRECTORY = "/home/tannewt/code/rcbuild.info-parts/Gemfan"

GROUPING = {}
SKIPPED = []

MATERIAL = {"W": "Wood",
            "CFN": "Carbon Fiber Nylon",
            "CF": "Carbon Fiber",
            "FG": "Fiberglass Nylon",
            "ABS": "ABS"}
STYLE = {"W": "",
         "MR": "Multirotor",
         "SF": "Slow Flyer",
         "3D": "3D",
         "E": "Electric",
         "BN": "Bullnose",
         "T": "T-Type"}

for filename in os.listdir(DIRECTORY):
  if os.path.islink(os.path.join(DIRECTORY, filename)):
    continue
  if filename[-4:] != "json":
    continue
  size = None
  material = "FG"
  style = "MR"

  parts = filename[:-5].split("-")
  if "Carbon" in parts or "CF" in parts:
    if "Nylon" in parts or "Fill" in parts or "Blend" in parts or "Composite" in parts:
      material = "CFN"
    else:
      material = "CF"
  elif "ABS" in parts:
    material = "ABS"
  if "Slow" in parts or "SF" in parts:
    style = "SF"
  elif "reversible" in parts or "3D" in parts:
    style = "3D"
  elif "E" in parts or "Electric" in parts:
    style = "E"
  elif "Bullnose" in parts or "(Bullnose)" in parts:
    style = "BN"
  elif "T" in parts:
    style = "T"
  elif "Wood" in parts:
    style = "W"
    material = "W"

  # Find the size and standardize to LENGTHxPITCH[xBLADES].
  for i, part in enumerate(parts):
    if part == "x" and all(char.isdigit() or char == "." for char in parts[i - 1]) and all(char.isdigit() or char == "." for char in parts[i + 1]):
      size = parts[i - 1] + "x" + parts[i + 1]
      break
    elif any(char.isdigit() for char in part):
      if "x" in part or "X" in part:
        size = part.translate(None, '"').replace("X", "x").replace(",", ".")
        if part[-1] == "x":
          size += parts[i + 1]
        size = size.strip(string.letters)
        break
      elif len(part) >= 4 and "m" not in part and "PCS" not in part:
        length = part[0]
        if length in ["1", "2"]:
          length += part[1]
        elif part[1] != "0":
          length += "." + part[1]
        pitch = part[2]
        if part[3] != "0":
          pitch += "." + part[3]
        size = length + "x" + pitch
        
  if size and ("Triblade" in parts or "3-Blade" in filename[:-5]):
    size += "x3"

  t = (size, material, style)

  if any(x is None for x in t) or "Motor" == parts[0]:
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
  base_part = {u'category': u'prop', u'name': name, u'subpart': [], u'equivalent': [], u'urls': {u'store': [], u'related': [], u'manufacturer': []}, u'manufacturer': u'Gemfan', u'replacement': []}
  merge.mergeFiles([os.path.join(DIRECTORY, x) for  x in GROUPING[k]],
                   os.path.join(DIRECTORY, fn), part=base_part)
  print(k)
  for v in GROUPING[k]:
    print("\t" + v)
  print

print("skipped")
for v in SKIPPED:
  print(v)
