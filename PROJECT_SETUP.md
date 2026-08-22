# Project setup and workflow

This file records the approved and implemented setup.

## Known repository details

- Local root: `/home/luka/dev/adriatic-map`
- Intended public GitHub remote: `git@github.com:luxzg/adriatic-map.git`
- Intended default branch: `main`
- Repository initialized on `main`, with the public `origin` configured and pushed
- Available locally: Git 2.53.0, Go 1.26.0, Python 3.13.12, GDAL `ogr2ogr`
- Not currently importable in system Python: GeoPandas/Shapely/pyproj as a set
- Available GIS runtime: GDAL 3.12.3 command-line tools and Python bindings
- Project language: English exclusively
- Project license: GPL-3.0-or-later, excluding third-party and OSM-derived material
  governed by its own stated license

## Repository layout

```text
/
  cmd/adriatic-map/       # tiny Go server
  web/                    # HTML/CSS/JS and locally vendored frontend assets
  data/
    generated/            # reviewed distributable overlay + metadata (tracked)
    raw/                  # source downloads (ignored)
    work/                 # intermediates (ignored)
  tools/                  # Python GIS generation code
  scripts/                # repeatable build/test/data/release helpers
  docs/DATA.md
```

The reviewed 1.1 MB generated overlay is tracked with metadata and an ODbL notice.
Raw OSM downloads, local environments, build outputs, secrets, and intermediates are
ignored by `.gitignore`.

## Implementation workflow

1. Keep these docs synchronized with implementation and verify license/data notices.
2. Initialize Git on `main`; configure and verify the supplied `origin`; review and,
   if approved, publish a separate docs/license-only initial commit.
3. Implement one small vertical slice: server, map, placeholder/test overlay loading,
   and controls, without claiming GIS correctness yet.
4. Implement the reproducible GIS pipeline and tests against the available Python
   GDAL bindings; document any additional prerequisites before requiring them.
5. Generate and inspect the real overlay; record source metadata and validation.
6. Run format, automated tests, Go builds for Linux/Windows, and runtime smoke tests.
7. Update docs/status/changelog, review the full diff, then commit and push each
   coherent pass as requested.

These repeated commands have checked-in helper scripts and have been verified locally.

## Verified application commands

```bash
./scripts/test.sh
./scripts/test-gis.sh
./scripts/download-data.sh
./scripts/generate-data.sh "SOURCE LAST-MODIFIED TIMESTAMP"
./scripts/validate-data.sh
./scripts/build-release.sh
go run ./cmd/adriatic-map
curl -sS http://127.0.0.1:8080/healthz
```

The test script uses ignored project-local Go build/module caches, runs synthetic GIS
tests, validates the tracked overlay against the raw source when it is available, runs
all Go tests and `go vet`, checks JavaScript syntax when Node.js is available, and
checks the working diff for whitespace errors. The release script cross-builds Linux
amd64 and Windows amd64 binaries into ignored `dist/` and prints SHA-256 checksums. The
server binds only to loopback by default and opens the system browser; use
`-open=false` in automated or headless environments.

## GIS maintainer prerequisites

The pipeline uses Python's GDAL/OGR bindings directly and does not require GeoPandas,
Shapely, pyproj, a database, or a Python virtual environment. On Debian/Ubuntu, install
missing prerequisites manually:

```bash
sudo apt install gdal-bin python3-gdal curl
```

The current pipeline is validated on Linux with Python 3.13 and GDAL 3.12. End users
running a release binary need none of these tools. The source download is about 925 MB
as of 2026-08-22 and is stored under ignored `data/raw/`; generation intermediates
belong under ignored `data/work/`.

## Release model

- Source stays small and public.
- End users download a platform binary containing the UI and reviewed overlay.
- Maintainers use Python only when regenerating geographic data.
- Release binaries and checksums go in GitHub Releases, not Git history.
- Application version: SemVer from `0.1.0`; docs-only changes do not bump it.

## Git repository

The repository uses `main`, is connected to the public GitHub `origin`, and is pushed
after each tested coherent pass. Generated release binaries remain ignored and are
intended for a later explicit GitHub Release rather than Git history.
