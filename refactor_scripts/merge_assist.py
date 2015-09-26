#!/usr/bin/python
from __future__ import print_function

import os
import os.path
import json
import string

DIRECTORY = "/Users/tannewt/case/parts/AbuseMark"

def token_termer(part):
  return [part["manufacturer"], part["category"]] + part["name"].split()

def bigram_termer(part):
  terms = []
  words = part["name"].split()
  for i, word in enumerate(words[:-1]):
    terms.append((word, words[i+1]))
  return terms

def prop_termer(part):
  terms = []
  words = string.lower(part["name"]).split()
  if "x" in words and words.index("x") < len(words) - 1:
    i = words.index("x")
    if all(char.isdigit() or char in [",", "."] for char in words[i-1]) and all(char.isdigit() or char in [",", "."] for char in words[i+1]):
      size = words[i-1].replace(",", ".")
      pitch = words[i+1].replace(",", ".")
      terms.append(size + "x" + pitch)
  else:
    for word in words:
      if all(char.isdigit() for char in word) and len(word) == 4:
        size = word[0]
        if word[1] != "0" and int(size) >= 3:
          size += "." + word[1]
        elif int(size) < 3:
          size += word[1]
        pitch = word[2]
        if word[3] != "0":
          pitch += "." + word[3]
        terms.append(size + "x" + pitch)
  return terms

def termers(part):
  unfiltered_terms = token_termer(part)# + bigram_termer(part)
  normalized_terms = set([string.lower(term) for term in unfiltered_terms])
  if "prop" in normalized_terms or "props" in normalized_terms or "propeller" in normalized_terms:
    normalized_terms.update(prop_termer(part))
  return normalized_terms

TOTAL_PARTS = 0
SUPPORTED_PARTS = []

TERM_TO_FNS = {}

FN_TO_TERMS = {}

for dirpath, dirnames, filenames in os.walk(DIRECTORY):
  if dirpath.find(".git") > -1:
    continue
  for filename in filenames:
    if filename[-4:] != "json":
      continue
    fn = os.path.join(dirpath, filename)
    if os.path.islink(fn):
      continue
    part = {}

    with open(fn, "r") as f:
      part = json.load(f)

    terms = termers(part)
    FN_TO_TERMS[fn] = terms
    for term in terms:
      if term not in TERM_TO_FNS:
        TERM_TO_FNS[term] = []
      TERM_TO_FNS[term].append(fn)

    if part["category"] != "":
      SUPPORTED_PARTS.append(fn)
    TOTAL_PARTS += 1

pair_score = {}
for fn1 in FN_TO_TERMS:
  similar = {}
  # Add score for every shared term.
  for term in FN_TO_TERMS[fn1]:
    for fn in TERM_TO_FNS[term]:
      if fn == fn1:
        continue
      if fn not in similar:
        similar[fn] = {"terms": [], "score": 0}
      score = float(TOTAL_PARTS) / len(TERM_TO_FNS[term])
      similar[fn]["terms"].append(term + " " + str(score))
      similar[fn]["score"] += score

  # Subtract score for every missing term.
  for fn in similar:
    for term in FN_TO_TERMS[fn1]:
      if term not in FN_TO_TERMS[fn]:
        score = float(TOTAL_PARTS) / len(TERM_TO_FNS[term])
        similar[fn]["terms"].append("-" + term + " " + str(score))
        similar[fn]["score"] -= score

    for term in FN_TO_TERMS[fn]:
      if term not in FN_TO_TERMS[fn1]:
        score = float(TOTAL_PARTS) / len(TERM_TO_FNS[term])
        similar[fn]["terms"].append("-" + term + " " + str(score))
        similar[fn]["score"] -= score
  pair_score[fn1] = similar

filenames = pair_score.items()
filenames.sort(key=lambda x: len(x[0]), reverse=True)
for fn, similar in filenames[:10]:
  if fn in SUPPORTED_PARTS:
    continue
  sorted_similar = sorted(similar.iteritems(), key=lambda x: x[1]["score"], reverse=True)
  print(fn)
  unsupported_count = 0
  supported_count = 0
  for similar_fn, info in sorted_similar:
    if similar_fn not in SUPPORTED_PARTS and unsupported_count < 5:
      print("\t" + similar_fn + " " + str(info["score"]))
      unsupported_count += 1
    elif similar_fn in SUPPORTED_PARTS and supported_count < 5:
      print('\033[92m' + "\t" + similar_fn + " " + str(info["score"]) + '\033[0m')
      supported_count += 1
    # for t in info["terms"]:
    #   print("\t\t" + t)

#print(proposals, "proposals")
#print(len(claimed), "claimed")
print(len(SUPPORTED_PARTS), "supported")
print(TOTAL_PARTS, "total")
print(100 * len(SUPPORTED_PARTS) / TOTAL_PARTS, "%")
