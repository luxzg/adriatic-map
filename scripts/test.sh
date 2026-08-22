#!/usr/bin/env sh
set -eu

project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
GOCACHE="${GOCACHE:-$project_root/.gocache}"
GOMODCACHE="${GOMODCACHE:-$project_root/.gomodcache}"
export GOCACHE
export GOMODCACHE
cd "$project_root"

go test ./...
go vet ./...
if command -v node >/dev/null 2>&1; then
    node --check web/app.js
fi
git diff --check
