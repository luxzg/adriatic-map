#!/usr/bin/env sh
set -eu

if [ "$#" -ne 1 ]; then
    echo "usage: $0 SOURCE_DATE_OR_LAST_MODIFIED" >&2
    exit 2
fi

project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_root"

format_elapsed() {
    elapsed_seconds=$1
    elapsed_minutes=$((elapsed_seconds / 60))
    remaining_seconds=$((elapsed_seconds % 60))
    if [ "$elapsed_minutes" -gt 0 ]; then
        printf '%dm %02ds' "$elapsed_minutes" "$remaining_seconds"
    else
        printf '%ds' "$remaining_seconds"
    fi
}

total_started_at=$(date +%s)
band_number=0
band_count=5

printf 'Generating %s coastal-distance overlays from the reviewed source snapshot.\n' "$band_count"

for distance_nm in 1 3 6 12 20; do
    band_number=$((band_number + 1))
    if [ "$distance_nm" -eq 6 ]; then
        metadata_path="data/generated/metadata.json"
    else
        metadata_path="data/generated/adriatic_${distance_nm}nm.metadata.json"
    fi

    printf '\n[%s/%s] %s NM: generation started.\n' "$band_number" "$band_count" "$distance_nm"
    band_started_at=$(date +%s)

    python3 -m tools.build_coastal_buffer \
        --source data/raw/land-polygons-split-4326.zip \
        --output "data/generated/adriatic_${distance_nm}nm.geojson" \
        --metadata "$metadata_path" \
        --source-date "$1" \
        --buffer-nm "$distance_nm" \
        --simplify-metres 50

    generation_finished_at=$(date +%s)
    generation_elapsed=$((generation_finished_at - band_started_at))
    printf '[%s/%s] %s NM: generation finished in %s; validation started.\n' \
        "$band_number" \
        "$band_count" \
        "$distance_nm" \
        "$(format_elapsed "$generation_elapsed")"

    ./scripts/validate-data.sh "$distance_nm" --update-metadata

    band_finished_at=$(date +%s)
    validation_elapsed=$((band_finished_at - generation_finished_at))
    band_elapsed=$((band_finished_at - band_started_at))
    printf '[%s/%s] %s NM: complete in %s (generation %s, validation %s).\n' \
        "$band_number" \
        "$band_count" \
        "$distance_nm" \
        "$(format_elapsed "$band_elapsed")" \
        "$(format_elapsed "$generation_elapsed")" \
        "$(format_elapsed "$validation_elapsed")"
done

total_finished_at=$(date +%s)
total_elapsed=$((total_finished_at - total_started_at))
printf '\nAll %s overlays generated and validated in %s.\n' \
    "$band_count" \
    "$(format_elapsed "$total_elapsed")"
