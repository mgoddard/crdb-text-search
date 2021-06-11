#!/bin/bash

for file in ./crdb-v20.2-docs/*.html
do
  f=$( basename $file)
  curl http://localhost:18080/add/crdb_docs/$( echo -n "https://www.cockroachlabs.com/docs/stable/$f" | base64 )
done

