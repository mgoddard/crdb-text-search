#!/usr/bin/env python3

import psycopg2
import psycopg2.errorcodes
from bs4 import BeautifulSoup
import logging
import sys
import html
import re
from collections import defaultdict
import urllib.request
import os.path
import ssl
import nltk
from nltk.corpus import stopwords
import time

#
# Prior to running, set the two required connection parameters as environment variables:
#
#   $ export PGHOST=192.168.1.4
#   $ export PGPORT=5432
#
# Time for indexing 410 HTML docs, 46 MB total
# ./html_indexer.py crdb_docs *.html  36.17s user 1.25s system 42% cpu 1:27.18 total
#

docs_sql = "INSERT INTO docs (idx_name, uri, content, n_words) VALUES "
words_sql = "INSERT INTO words (idx_name, uri, word, cnt) VALUES "

# All English words, lower case
word_list_url = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"
word_list_file = "words_alpha.txt"
english = set()
sno = nltk.stem.SnowballStemmer("english")
stops = set(stopwords.words("english"))

# Name of the index, since there could be more than one
idx_name = None

if len(sys.argv) < 3:
  print("Usage: %s index_name file.html [file2.html ... fileN.html]" % sys.argv[0])
  sys.exit(1)

def insert_row(conn, sql, do_commit=True):
  with conn.cursor() as cur:
    try:
      cur.execute(sql)
    except:
      logging.debug("insert_row(): status message: {}".format(cur.statusmessage))
      return
  if do_commit:
    try:
      conn.commit()
    except:
      logging.debug("insert_row(): status message: {}".format(cur.statusmessage))
      print("Retrying commit() in 1 s")
      time.sleep(1)
      conn.commit()

def index_file(idx, in_file):
  html = ""
  with open(in_file, mode='rt') as f:
    for line in f:
      html += line
  soup = BeautifulSoup(html, 'html.parser')
  text = soup.get_text()
  text = re.sub(r"['\",{}]", "", text) # Clean any special chars out of this

  words = defaultdict(int)
  n_words = 0
  for w in re.split(r"\W+", text): # Split string on any non-word characters
    if len(w) == 0:
      continue
    w = sno.stem(w) # Stem the word (this also lower-cases it)
    if w in english:
      words[w] += 1
      n_words += 1

  words_a = [idx] # Put index name into this array so queries can use it within GIN index
  words_vals = []
  for k in words:
    words_a.append(k)
    words_vals.append("('" + idx + "', '" + in_file + "', '" + k + "', " + str(words[k]) + ")")
  insert_row(conn, docs_sql + "('" + idx + "', '" + in_file + "', '{" + ','.join(words_a) + "}', " + str(n_words) + ")", False)
  insert_row(conn, words_sql + ','.join(words_vals))

# Word list is assumed to contain one word per line
def load_word_list():
  if not os.path.isfile(word_list_file):
    with urllib.request.urlopen(word_list_url, context=ssl.SSLContext()) as infile, open(word_list_file, mode="wt") as outfile:
      for line in infile:
        line = infile.read().decode("utf-8")
        outfile.write(line)

  with open(word_list_file, mode="rt") as f:
    for w in f:
      w = w.strip()
      if not w in stops: # Skip English stop words
        english.add(sno.stem(w))

# main()
# NOTE: host and port are set in env
conn = psycopg2.connect(
  database='defaultdb',
  user='root'
)

load_word_list()
idx_name = sys.argv[1]

t0 = time.time()
for in_file in sys.argv[2:]:
  print("Indexing file " + in_file + " now ...")
  index_file(idx_name, in_file)
t1 = time.time()
print("Total time: " + str(t1 - t0) + " s")

conn.close()

