#!/usr/bin/python

import os
import os.path
import sys
import json

def printColor(color, text):
  print(color + text + '\033[0m')

def normal(text):
  print(text)

def red(text):
  printColor('\033[91m', text)

def boldred(text):
  printColor('\033[91;1m', text)

def green(text):
  printColor('\033[92m', text)

def boldgreen(text):
  printColor('\033[92;1m', text)

def gray(text):
  printColor('\033[90m', text)

def listFiles(files, sites):
  for fn in files:
    if fn.endswith(".directory"):
      continue
    if not sites and os.path.islink(fn):
      gray(fn)
    elif os.path.isfile(fn) and not os.path.islink(fn):
      with open(fn, "r") as f:
        part = json.load(f)
        keep = True
        if sites:
          keep = False
          if "version" not in part:
            for url in part["urls"]["store"]:
              for site in sites:
                if site in url:
                  keep = True
                  break
              if keep:
                break
          else:
            for variant in part["variants"]:
              for site in sites:
                if site in variant["url"]:
                  keep = True
                  break
              if keep:
                break
        if "category" in part and part["category"] != "":
          if not keep:
            red(fn)
          else:
            green(fn)
        elif "categories" in part and len(part["categories"]) > 0:
          if not keep:
            boldred(fn)
          else:
            boldgreen(fn)
        elif keep:
          normal(fn)
    elif os.path.isdir(fn):
      dn = fn
      for fn in os.listdir(dn):
        listFiles([os.path.join(dn, fn)], sites)

if __name__ == "__main__":
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument("--site", nargs="+")
  parser.add_argument("fns", nargs="+")
  args = parser.parse_args()

  listFiles(args.fns, args.site)
