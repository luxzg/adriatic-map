#!/usr/bin/env sh
set -eu

project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_root"

case "${1:-}" in
    ""|--*)
        distance_nm=6
        ;;
    *)
        distance_nm=$1
        shift
        ;;
esac

case "$distance_nm" in
    1|3|12|20)
        metadata_path="data/generated/adriatic_${distance_nm}nm.metadata.json"
        ;;
    6)
        metadata_path="data/generated/metadata.json"
        ;;
    *)
        echo "unsupported distance: $distance_nm (expected 1, 3, 6, 12, or 20)" >&2
        exit 2
        ;;
esac

python3 -m tools.validate_generated_overlay \
    --source data/raw/land-polygons-split-4326.zip \
    --overlay "data/generated/adriatic_${distance_nm}nm.geojson" \
    --metadata "$metadata_path" \
    "$@"
