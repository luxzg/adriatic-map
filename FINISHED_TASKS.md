# Finished tasks

This file archives completed, skipped, dropped, and deliberately deferred work. It is
a status record, not a duplicate of the chronological changelog.

## Completed

### 2026-08-22 — Initial documentation pass

- Read the requested coding rulebook and supplied project brief in full.
- Inspected the project root and confirmed it was empty and not initialized as Git.
- Recorded known public GitHub repository details and a public-repository safety model.
- Drafted the project-specific docs, scope, workflow, data plan, validation plan, and
  safe `.gitignore` baseline without making application code changes.

### 2026-08-22 — Language and licensing decisions

- Established English as the exclusive language for UI, documentation, code, comments,
  notices, and project-maintained text.
- Generalized unnecessary Croatian place names and local terminology, including in the
  editable historical brief, to region-level English descriptions.
- Added GPL-3.0-or-later licensing for original project content while retaining the
  applicable ODbL terms for OSM inputs and generated OSM-derived data.

### 2026-08-22 — V1 implementation direction approved

- Cleared the planning gate for all non-optional v1 work.
- Selected the Go/Leaflet application and Python/GDAL preprocessing architecture.
- Approved viewport-only online OSM basemap use and a local precomputed overlay.
- Selected coastline-derived land for v1, with ambiguous additional rock features
  deferred as a separately auditable optional layer.
- Approved tracked reviewed generated data when practical, SemVer from `0.1.0`, and
  multiline commits for each coherent implementation pass.

### 2026-08-22 — Application shell 0.1.0

- Implemented the standard-library Go server with an embedded responsive Leaflet UI,
  runtime health/version endpoint, graceful shutdown, and optional browser launch.
- Added pan/zoom, overlay visibility and opacity controls, full-Adriatic and Dalmatia
  views, visible OSM attribution, data status, and the navigation disclaimer.
- Vendored checksum-verified Leaflet 1.9.4 assets and its BSD 2-Clause license.
- Added an explicitly empty placeholder GeoJSON rather than invented geometry.
- Added Go endpoint/header/static-asset tests, JavaScript syntax validation, project
  test/build helpers, and verified Linux/Windows amd64 cross-builds.
- Smoke-tested the built Linux server on a free loopback port and confirmed its HTML,
  health endpoint, security headers, embedded data, and clean shutdown.

## Deferred by scope

- Configurable/multiple buffer distances, point inspection, vector tiles, and offline
  basemaps are post-v1 possibilities, not active implementation work.
