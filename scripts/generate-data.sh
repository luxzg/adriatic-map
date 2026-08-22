#!/usr/bin/env sh
set -eu

if [ "$#" -ne 1 ]; then
    echo "usage: $0 SOURCE_DATE_OR_LAST_MODIFIED" >&2
    exit 2
fi

project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_root"

for distance_nm in 1 3 6 12 20; do
    if [ "$distance_nm" -eq 6 ]; then
        metadata_path="data/generated/metadata.json"
    else
        metadata_path="data/generated/adriatic_${distance_nm}nm.metadata.json"
    fi

    python3 -m tools.build_coastal_buffer \
        --source data/raw/land-polygons-split-4326.zip \
        --output "data/generated/adriatic_${distance_nm}nm.geojson" \
        --metadata "$metadata_path" \
        --source-date "$1" \
        --buffer-nm "$distance_nm" \
        --simplify-metres 50

    ./scripts/validate-data.sh "$distance_nm" --update-metadata
done
