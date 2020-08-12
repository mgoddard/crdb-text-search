#!/bin/bash

# TODO: Set the host and port of where the app is running
host=localhost
port=18080

if [ $# -ne 1 ]
then
  echo "Usage: $0 url_to_index"
  exit 1
fi

url=$1
curl http://$host:$port/add/crdb_docs/$( echo -n "$url" | base64 )

