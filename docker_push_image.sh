#!/bin/bash

. ./current_tag.sh

docker push mgoddard/crdb-search-app:$tag

