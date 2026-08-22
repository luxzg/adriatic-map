#!/usr/bin/env sh
set -eu

project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
GOCACHE="${GOCACHE:-$project_root/.gocache}"
GOMODCACHE="${GOMODCACHE:-$project_root/.gomodcache}"
export GOCACHE
export GOMODCACHE
cd "$project_root"

mkdir -p dist
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -trimpath -o dist/adriatic-map-linux-amd64 ./cmd/adriatic-map
CGO_ENABLED=0 GOOS=windows GOARCH=amd64 go build -trimpath -o dist/adriatic-map-windows-amd64.exe ./cmd/adriatic-map

sha256sum dist/adriatic-map-linux-amd64 dist/adriatic-map-windows-amd64.exe
