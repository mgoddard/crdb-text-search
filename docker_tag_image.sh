#!/bin/bash

tag=1.1

docker tag mgoddard/crdb-search-app mgoddard/crdb-search-app:$tag
docker image tag mgoddard/crdb-search-app:$tag mgoddard/crdb-search-app:latest

