#!/usr/bin/env sh
set -eu

project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
GOCACHE="${GOCACHE:-$project_root/.gocache}"
GOMODCACHE="${GOMODCACHE:-$project_root/.gomodcache}"
export GOCACHE
export GOMODCACHE
cd "$project_root"

python3 -m py_compile tools/build_coastal_buffer.py tools/test_build_coastal_buffer.py
python3 -m unittest -v tools.test_build_coastal_buffer
go test ./...
go vet ./...
if command -v node >/dev/null 2>&1; then
    node --check web/app.js
fi
git diff --check
