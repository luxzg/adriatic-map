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

### 2026-08-22 — Linux user acceptance and workflow hardening

- User-tested version 0.1.2 on Linux and accepted the visual geometry and 50 m
  simplification as suitable for informational use.
- User-tested the responsive layout through browser mobile-device emulation and found
  it reasonably usable.
- Confirmed the raw archive remains reusable inside ignored project storage and the
  compact generated overlay remains tracked with its provenance and license notice.
- Added stable run and smoke-test helpers plus project rules for package-based Python
  invocation, arbitrary/free ports, and standardized commands with diagnostic-only
  exceptions.

### 2026-08-22 — Distance, color, and inspection controls 0.2.0

- Generated and source-validated independent 1/3/6/12/20 NM overlays from the same
  reviewed coastline snapshot, totaling 5,354,919 tracked bytes.
- Added a distance selector with 6 NM as the default and lazy per-distance loading.
- Added synchronized native color-picker and validated six-digit hex controls.
- Added a point inspector that is disabled by default and classifies clicks into
  approximate precomputed bands only while explicitly enabled.
- Added reusable GeoJSON containment utilities and automated polygon, hole, boundary,
  real-data band, manifest, endpoint, build, and runtime smoke coverage.
- Documented the Croatian regulatory context without claiming the map can establish
  the legal limit applicable to a vessel, skipper, or voyage.

### 2026-08-22 — Generation progress and default color 0.2.1

- Recorded the user's successful Linux testing of all five zones, the overlay color
  control, and opt-in point inspection.
- Added flushed GIS phase messages so a long-running band visibly progresses through
  source loading, geometry construction/simplification, and output writing.
- Added one-blank-line band separation plus generation, validation, combined-band,
  and all-band elapsed times to the standard generation helper.
- Changed the default overlay color to `#0e0af5` and kept badge text readable across
  light and dark user-selected colors.

## Deliberately not planned

- A separate rock/seamark layer, because the accepted coastline polygons already
  provide the intended land definition and mixed hazard semantics add complexity.
- Offline basemap packaging, because normal viewport-only OSM tile access meets the
  intended connected local use without a large tile archive.
- Multiple detail levels or vector tiles, because the compact GeoJSON overlays already
  perform adequately.
- Dynamic source updates or a database, because the reviewed static snapshot and
  reproducible offline generation cover the intended use.
