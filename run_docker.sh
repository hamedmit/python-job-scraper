#!/usr/bin/env bash

set -e

docker compose run --rm \
  --user "$(id -u):$(id -g)" \
  jobscraper