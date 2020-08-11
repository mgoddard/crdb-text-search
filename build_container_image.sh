#!/bin/bash

# First, install pack (this is for running on a Mac):
#   brew install buildpacks/tap/pack
pack build crdb-search-app --path . --builder gcr.io/buildpacks/builder:v1

