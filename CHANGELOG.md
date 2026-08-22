# Changelog

All notable code, data, documentation, and workflow changes are recorded here.

## Documentation - 2026-08-22 17:53 CEST

- Established the provisional project documentation structure and planning gate.
- Recorded the proposed Go/frontend/Python-GIS architecture, public-repository safety,
  geographic data workflow, licensing split, validation expectations, and AI credit.
- Added a conservative `.gitignore` proposal for secrets, local state, raw geographic
  downloads, GIS intermediates, Python caches, and build artifacts.
- Preserved the original supplied project brief as historical context.
- No application code, generated GIS data, Git repository, commit, or remote was made.

## Documentation - 2026-08-22 18:08 CEST

- Established English as the exclusive language for UI, documentation, code, comments,
  notices, and project-maintained text.
- Replaced unnecessary Croatian place-name lists and local terminology with broader
  English regional descriptions, including in the user-authorized initial brief.
- Replaced the Croatian navigation warning with an English informational-use notice.
- Added the full GNU GPL v3 license text for original project content under
  GPL-3.0-or-later and retained ODbL governance for OSM inputs and generated
  OSM-derived data.
- No application code, Git initialization, commit, or push was performed.

## Documentation - 2026-08-22 18:17 CEST

- Cleared the planning gate and recorded the approved Go/Leaflet/Python-GDAL v1
  architecture, online basemap model, coastline-only land source, generated-data
  policy, versioning, and per-pass commit workflow.
- Converted the TODO from unresolved decisions to active implementation work.
- No application code was included in this documentation checkpoint.

## 0.1.0 - 2026-08-22 18:32 CEST

- Added a small standard-library Go server with embedded browser and data assets,
  graceful shutdown, automatic browser launch, and a health/version endpoint.
- Added the responsive English Leaflet UI with pan/zoom, fixed 6 NM display, overlay
  toggle, opacity slider, full-Adriatic and Dalmatia views, visible OSM attribution,
  generation status, and informational-use warning.
- Vendored checksum-verified Leaflet 1.9.4 under its BSD 2-Clause license.
- Added a deliberately empty placeholder overlay so no invented geometry is displayed
  before the reproducible GIS output is ready.
- Added repeatable tests, vet/check workflow, Linux/Windows amd64 builds, JavaScript
  syntax validation, and a successful loopback server smoke test.

## 0.1.1 - 2026-08-22 18:38 CEST

- Added the reproducible Python/GDAL pipeline for safely margined OSM land selection,
  geometry repair/dissolve, freshwater-hole filling, custom metric projection, exact
  11,112 m buffering, land subtraction, final clipping, simplification, WGS84 export,
  and detailed source/accuracy metadata.
- Added safe source download/generation helpers and integrated five synthetic GIS tests
  into the standard test workflow.
- Verified metric projection distortion at representative Adriatic samples is
  0.076324%, below the 0.5% gate.
- Documented the 925 MB source archive, maintainer prerequisites, fixed v1 parameters,
  ignored raw-data workflow, and regeneration commands.
