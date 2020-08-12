#!/bin/bash

# TODO: Set the host and port of where the app is running
host=localhost
port=18080

max_results=6

if [ $# -lt 1 ]
then
  echo "Usage: $0 word [word2 ... wordN]"
  exit 1
fi

curl http://$host:$port/search/crdb_docs/$( echo -n "$@" | base64 )/$max_results

