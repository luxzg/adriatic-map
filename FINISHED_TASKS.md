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

## Deferred by scope

- Configurable/multiple buffer distances, point inspection, vector tiles, and offline
  basemaps are post-v1 possibilities, not active implementation work.
