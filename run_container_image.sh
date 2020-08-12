#!/bin/bash

# TODO: change these two environment variables to suit your deployment
docker run --rm -p 18080:18080 -e PGHOST=192.168.1.3,PGPORT=5432,FLASK_PORT=18080 mgoddard/crdb-search-app

