#!/bin/bash

. ./current_tag.sh

# Change these environment variables as required to suit your deployment
docker run --rm -p 18080:18080 -e PGHOST=192.168.1.3,PGDATABASE=defaultdb,PGUSER=root,PGPORT=5432,FLASK_PORT=18080 mgoddard/crdb-search-app:$tag

