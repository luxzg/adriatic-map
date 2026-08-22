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

### 2026-08-22 — Reproducible GIS pipeline 0.1.1

- Implemented Python/GDAL source archive discovery, safely margined land selection,
  geometry repair/dissolve, freshwater-hole filling, custom metric transformation,
  exact 11,112 m buffer, land subtraction, output clipping, topology-preserving
  simplification, WGS84 GeoJSON export, and detailed generation metadata.
- Added safe source download and generation helpers that keep the large raw archive
  and intermediates ignored and refuse to overwrite an existing source archive.
- Added synthetic GIS tests for the exact nautical-mile conversion, freshwater-hole
  suppression, marine-only buffering, clip bounds, output licensing, and projection
  distortion.
- Measured maximum projection error at representative Adriatic test segments as
  0.076324%, below the 0.5% validation gate.

### 2026-08-22 — Reviewed 6 NM overlay 0.1.2

- Downloaded the 925,340,242-byte OSM-derived coastline archive into the ignored raw
  data directory and verified its published timestamp and SHA-256 checksum.
- Generated the valid 1,052,107-byte WGS84 MultiPolygon overlay from 4,722 selected
  source features, covering 58,001.174 km² within the configured Adriatic bounds.
- Validated 252 source-to-output grid classifications with zero mismatches plus open
  sea, land, corridor, and small-islet retention samples.
- Visually reviewed a full-region rendering for island-dense areas, open-sea gaps,
  both coasts, regional extremes, and output-edge artefacts.
- Added full provenance/tool metadata, the embedded ODbL notice and data-method links,
  repeatable validation helpers, and the updated user-facing documentation.
- Cross-built the self-contained Linux amd64 and Windows amd64 executables and
  smoke-tested the Linux runtime and every embedded application/data resource.

## Deferred by scope

- Configurable/multiple buffer distances, point inspection, vector tiles, and offline
  basemaps are post-v1 possibilities, not active implementation work.
