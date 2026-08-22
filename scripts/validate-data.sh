#!/usr/bin/env sh
set -eu

project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_root"

python3 -m tools.validate_generated_overlay \
    --source data/raw/land-polygons-split-4326.zip \
    --overlay data/generated/adriatic_6nm.geojson \
    --metadata data/generated/metadata.json \
    "$@"
