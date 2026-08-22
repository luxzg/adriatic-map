#!/usr/bin/env sh
set -eu

if [ "$#" -ne 1 ]; then
    echo "usage: $0 SOURCE_DATE_OR_LAST_MODIFIED" >&2
    exit 2
fi

project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_root"

python3 -m tools.build_coastal_buffer \
    --source data/raw/land-polygons-split-4326.zip \
    --output data/generated/adriatic_6nm.geojson \
    --metadata data/generated/metadata.json \
    --source-date "$1" \
    --buffer-nm 6 \
    --simplify-metres 50

./scripts/validate-data.sh --update-metadata
