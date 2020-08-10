#!/usr/bin/env python3

#
# This is used to build a domain specific lexicon to add to the English one being used,
# so that we can index and search on words don't appear in that English word list.
#

# Runs in about 20 seconds on this set of HTML files
"""
[mgoddard@brutus crdb-v20.2-docs]$ time ~/Python/gen_lexicon.py *.html > specialized_words.txt
~/Python/gen_lexicon.py *.html > specialized_words.txt  18.21s user 0.34s system 102% cpu 18.070 total
"""

import sys
if len(sys.argv) < 2:
  print("Usage: %s file.html [file2.html ... fileN.html]" % sys.argv[0])
  sys.exit(1)

from bs4 import BeautifulSoup
import re
import os.path
from collections import defaultdict
from nltk.corpus import stopwords
import urllib.request
import ssl

stops = set(stopwords.words("english")) # This yields a lower cased set of words
word_list_url = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"
word_list_file = os.path.basename(word_list_url)
english = set()
new_words = defaultdict(int)
avoid_re = re.compile(r"^(\d+|_+)$")

def load_word_list():
  if not os.path.isfile(word_list_file):
    with urllib.request.urlopen(word_list_url, context=ssl.SSLContext()) as infile, open(word_list_file, mode="wt") as outfile:
      for line in infile:
        line = infile.read().decode("utf-8")
        outfile.write(line)
  with open(word_list_file, mode="rt") as f:
    for w in f:
      w = w.strip().lower()
      english.add(w)

def process_file(in_file):
  html = ""
  with open(in_file, mode='rt') as f:
    for line in f:
      html += line
  soup = BeautifulSoup(html, 'html.parser')
  text = soup.get_text().lower()
  text = re.sub(r"['\",{}]", "", text) # Clean any special chars out of this
  for w in re.split(r"\W+", text): # Split string on any non-word characters
    if len(w) == 0 or avoid_re.match(w):
      continue
    if w not in stops and w not in english:
      new_words[w] += 1

# main()
load_word_list()

for in_file in sys.argv[1:]:
  #print("Indexing file " + in_file + " now ...")
  process_file(in_file)

# Dump the list of specialized terms in order of decreasing frequency
for k, v in sorted(new_words.items(), key=lambda item: item[1], reverse=True):
  #print(k + "\t" + str(v))
  if v <= 6:
    break
  print(k)

