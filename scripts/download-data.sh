#!/usr/bin/env sh
set -eu

project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
destination="$project_root/data/raw/land-polygons-split-4326.zip"
partial="$destination.part"
source_url="https://osmdata.openstreetmap.de/download/land-polygons-split-4326.zip"

mkdir -p "$(dirname -- "$destination")"
if [ -e "$destination" ]; then
    echo "source archive already exists: $destination"
    sha256sum "$destination"
    exit 0
fi

curl --fail --location --show-error --retry 3 --output "$partial" "$source_url"
mv "$partial" "$destination"
sha256sum "$destination"
