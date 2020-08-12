#!/bin/bash

# First, install pack (this is for running on a Mac):
#   brew install buildpacks/tap/pack
pack build mgoddard/crdb-search-app --env "PGHOST" --env "PGPORT" --env "FLASK_PORT" --path . --builder gcr.io/buildpacks/builder:v1

