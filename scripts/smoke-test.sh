#!/usr/bin/env sh
set -eu

project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
temporary_directory=$(mktemp -d "${TMPDIR:-/tmp}/adriatic-map-smoke.XXXXXX")
server_pid=""

cleanup() {
    if [ -n "$server_pid" ]; then
        kill "$server_pid" 2>/dev/null || true
        wait "$server_pid" 2>/dev/null || true
    fi
    rm -r -- "$temporary_directory"
}
trap cleanup EXIT INT TERM

cd "$project_root"
./scripts/build-release.sh

./dist/adriatic-map-linux-amd64 \
    -open=false \
    -listen 127.0.0.1:0 \
    >"$temporary_directory/server.log" 2>&1 &
server_pid=$!

application_url=""
attempt=0
while [ "$attempt" -lt 50 ]; do
    application_url=$(awk '/ is available at http:\/\// { print $NF; exit }' \
        "$temporary_directory/server.log")
    if [ -n "$application_url" ]; then
        break
    fi
    if ! kill -0 "$server_pid" 2>/dev/null; then
        echo "application exited before becoming ready" >&2
        sed -n '1,80p' "$temporary_directory/server.log" >&2
        exit 1
    fi
    attempt=$((attempt + 1))
    sleep 0.1
done

if [ -z "$application_url" ]; then
    echo "application did not report a listening URL" >&2
    exit 1
fi

curl --fail --silent --show-error "${application_url}healthz" \
    --output "$temporary_directory/health.json"
curl --fail --silent --show-error "$application_url" \
    --output "$temporary_directory/index.html"
curl --fail --silent --show-error "${application_url}data/adriatic_6nm.geojson" \
    --output "$temporary_directory/adriatic_6nm.geojson"
curl --fail --silent --show-error "${application_url}data/metadata.json" \
    --output "$temporary_directory/metadata.json"
curl --fail --silent --show-error "${application_url}data/NOTICE.md" \
    --output "$temporary_directory/NOTICE.md"

grep -F '"status":"ok"' "$temporary_directory/health.json" >/dev/null
grep -F 'Informational visualization only.' "$temporary_directory/index.html" >/dev/null
grep -F '"generated": true' "$temporary_directory/metadata.json" >/dev/null
grep -F 'ODbL 1.0' "$temporary_directory/NOTICE.md" >/dev/null
cmp data/generated/adriatic_6nm.geojson "$temporary_directory/adriatic_6nm.geojson"

echo "smoke test passed at $application_url"
