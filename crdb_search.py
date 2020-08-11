#!/usr/bin/env python3

# Flask web app version of the CRDB text index/search example

import psycopg2
import psycopg2.errorcodes
from bs4 import BeautifulSoup
import logging
import sys
import html
import re
from collections import defaultdict
import urllib.request
import requests
import os.path
import ssl
import nltk
from nltk.corpus import stopwords
import time
# For Web app
from flask import Flask, request, Response, g
import urllib
import json
import base64

#
# Prior to running, set the two required connection parameters as environment variables:
#
#   $ export PGHOST=192.168.1.4
#   $ export PGPORT=5432
#

app = Flask(__name__)
port = int(os.getenv("PORT", 18080))

conn = psycopg2.connect(
  database='defaultdb',
  user='root'
)

CHARSET = "utf-8"
docs_sql = "INSERT INTO docs (idx_name, uri, content, n_words) VALUES "
words_sql = "INSERT INTO words (idx_name, uri, word, cnt) VALUES "

word_lists = [
  "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt",
  "https://raw.githubusercontent.com/mgoddard/crdb-text-search/master/specialized_words.txt"
]
vocab = set()
sno = nltk.stem.SnowballStemmer("english")
stops = set(stopwords.words("english"))

# For using requests to retrieve a URL
headers = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET",
  "Access-Control-Allow-Headers": "Content-Type",
  "Access-Control-Max-Age": "3600",
  "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0"
}

def get_html(url):
  req = requests.get(url, headers)
  return req.content

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

# Clean any special chars out of text
def clean_text(text):
  return re.sub(r"['\",{}]", "", text)

# Decode a base64 encoded value to a UTF-8 string
def decode(b64):
  b = base64.b64decode(b64)
  return b.decode(CHARSET).strip()

# The search/query
@app.route("/search/<idx>/<q_base_64>/<int:limit>")
def do_search(idx, q_base_64, limit):
  q = decode(q_base_64)
  q = clean_text(q)
  terms = []
  for term in re.split(r"\W+", q):
    if len(term) == 0:
      continue
    term = sno.stem(term)
    if term in vocab:
      terms.append(term)
  q_sql = """
  WITH d AS (
    SELECT idx_name, uri, n_words
    FROM docs
    WHERE content @> """
  # '{crdb_docs, instal, insecur}'
  q_sql += "'{" + idx + "," + ','.join(terms) + "}'"
  q_sql += """
  ), w AS (
    SELECT idx_name, uri, SUM(cnt) n
    FROM words
    WHERE idx_name = """
  # 'crdb_docs' AND word IN ('instal', 'insecur')
  q_sql += "'" + idx + "' AND word IN (" + ','.join(["'" + x + "'" for x in terms]) + ")"
  q_sql += """
    GROUP BY (idx_name, uri)
  )
  SELECT w.uri, (100.0 * n/n_words)::NUMERIC(9, 3) score FROM w
  JOIN d ON d.idx_name = w.idx_name AND d.uri = w.uri
  ORDER BY score DESC
  LIMIT """
  q_sql += str(limit)
  print("SQL: " + q_sql)
  return "SQL", 200

# Use this for indexing an HTML document.
# EXAMPLE:
#   curl http://localhost:18080/add/crdb_docs/$( echo -n "https://www.cockroachlabs.com/blog/distributed-sql-webinar/" | base64 )
@app.route("/add/<idx>/<url_base_64>")
def index_url(idx, url_base_64):
  url = decode(url_base_64)
  print("Indexing " + url + " now")
  html = get_html(url)
  soup = BeautifulSoup(html, 'html.parser')
  text = soup.get_text()
  text = clean_text(text)

  words = defaultdict(int)
  n_words = 0
  for w in re.split(r"\W+", text): # Split string on any non-word characters
    if len(w) == 0:
      continue
    w = sno.stem(w) # Stem the word (this also lower-cases it)
    if w in vocab:
      words[w] += 1
      n_words += 1

  words_a = [idx] # Put index name into this array so queries can use it within GIN index
  words_vals = []
  for k in words:
    words_a.append(k)
    words_vals.append("('" + idx + "', '" + url + "', '" + k + "', " + str(words[k]) + ")")
  insert_row(conn, docs_sql + "('" + idx + "', '" + url + "', '{" + ','.join(words_a) + "}', " + str(n_words) + ")", False)
  insert_row(conn, words_sql + ','.join(words_vals))
  print("OK")
  return "OK", 200

# Word list is assumed to contain one word per line
def load_word_list(url):
  word_file = "/tmp" + "/" + os.path.basename(url)
  # Fetch only if it's not already in /tmp/
  if not os.path.isfile(word_file):
    with urllib.request.urlopen(url, context=ssl.SSLContext()) as u, open(word_file, mode="wt") as outfile:
      for line in u:
        line = u.read().decode(CHARSET)
        outfile.write(line)
  with open(word_file, mode="rt") as f:
    for w in f:
      w = w.strip()
      if not w in stops: # Skip stop words
        vocab.add(sno.stem(w)) # Add the stemmed version of the word, w

if __name__ == '__main__':
  for url in word_lists:
    load_word_list(url)
  app.run(host='0.0.0.0', port=port, threaded=True, debug=True)
  # At shutdown
  conn.close()

