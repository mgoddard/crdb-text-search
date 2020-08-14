#!/usr/bin/env python3

# Client for the search endpoint

host = "localhost"
port = 18080
index_name = "crdb_docs"
max_results = 6

import base64
import urllib.request
import sys
import json
import time

CHARSET = "utf-8"

if len(sys.argv) < 2:
  print("Usage: %s word [word2 ... wordN]" % sys.argv[0])
  sys.exit(1)

t0 = time.time()
terms = ' '.join(sys.argv[1:])
b64_terms = base64.b64encode(terms.encode(CHARSET)).decode(CHARSET)
url = "http://" + host + ':' + str(port) + "/search/" + index_name + "/" + b64_terms + "/" + str(max_results)
rv = None
with urllib.request.urlopen(url) as fp:
  rv = fp.read().decode("utf-8")

obj = json.loads(rv.rstrip())
print(json.dumps(obj, sort_keys=True, indent=2))
et = time.time() - t0
print("Elapsed time: {:4.2f} ms".format(1.0E+03 * et))

