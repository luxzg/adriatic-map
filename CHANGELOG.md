# Changelog

All notable code, data, documentation, and workflow changes are recorded here.

## Documentation and validation - 2026-08-22 22:32 CEST

- Recorded the user's successful full five-band regeneration on Linux, completing in
  7m 22s with readable progress/timing output and zero validation mismatches.
- Preserved the regenerated metadata audit timestamps; overlay geometry, areas,
  checksums, and all other metadata remained unchanged.
- Confirmed internet access is required only for the OSM background map; the local
  application and simplified precomputed overlays remain embedded.
- Finalized the decisions against offline basemap packaging, a rock/seamark layer,
  tiled/alternate overlay detail levels, dynamic coastline updates/a database, and
  exact on-click distance calculations.
- No application behavior or geometry changed, so the version remains 0.2.1. Windows
  runtime testing remains the only active TODO.

## 0.2.1 - 2026-08-22 20:29 CEST

- Added visible, flushed phase progress while each coastal-distance band loads source
  land geometry, constructs and simplifies its marine zone, and writes output.
- Added a blank line between bands, generation and validation timings for each band,
  combined per-band timing, and total elapsed time for all five bands.
- Changed the default overlay color from amber to `#0e0af5` and added readable light
  or dark text selection for the color-backed distance badge.
- Recorded the user's successful Linux testing of the five zones, color selection,
  and opt-in point inspection; Windows runtime validation remains open.
- Bumped the application version from 0.2.0 to 0.2.1.

## 0.2.0 - 2026-08-22 20:01 CEST

- Added independently generated and validated 1/3/6/12/20 NM marine overlays from the
  reviewed coastline snapshot, with 6 NM retained as the default.
- Added distance selection, synchronized native color-picker and validated hex color
  controls, plus an explicitly toggled point inspector that is off by default.
- Added approximate precomputed-band classification and selected-overlay membership;
  inspection does not claim an exact or legally determinative distance.
- Generalized the GIS generator and validator for every supported distance, added an
  embedded overlay manifest, and expanded standard tests and runtime smoke checks to
  cover all five datasets.
- Fixed closed-ring point containment so a repeated polygon endpoint cannot cause
  unrelated locations to be classified as polygon-boundary hits.
- Recorded exact output sizes, areas, checksums, source-to-output validation totals,
  Croatian regulatory context, limitations, and the deliberately excluded optional
  complexity in project documentation.
- Bumped the application version from 0.1.2 to 0.2.0.

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

## 0.1.2 - 2026-08-22 18:57 CEST

- Replaced the empty placeholder with the reviewed 1.1 MB Adriatic 6 NM marine
  overlay generated from the current OSM-derived coastline land polygons.
- Added source-to-output validation for 252 regional grid points, open sea, land, a
  Dalmatian corridor, and retention of a coastal zone around a small source islet.
- Recorded the source URL, published and retrieval timestamps, archive size and
  SHA-256, Python/GDAL/PROJ versions, processing parameters, output statistics,
  projection error, and validation results in shipped metadata.
- Added the ODbL generated-data notice to the embedded application, exposed data and
  method links in the UI, and integrated full validation into generation and routine
  tests whenever the ignored source archive is locally available.
- Documented the reviewed snapshot, measured accuracy, known limitations, build/run
  workflow, and remaining user browser-validation checklist.
- Rebuilt Linux amd64 and Windows amd64 executables and smoke-tested the Linux binary,
  including its health response, security headers, UI, exact embedded overlay,
  metadata, data notice, version, and clean shutdown.

## Documentation and workflow - 2026-08-22 19:18 CEST

- Recorded the user's successful Linux visual review, acceptance of the simplified
  overlay, and successful responsive-layout check using browser mobile emulation;
  retained Windows runtime testing as the only release-validation item.
- Documented that the reusable 925,340,242-byte raw archive remains inside the project
  under ignored `data/raw/`, while the reviewed 1.1 MB generated overlay is tracked
  runtime data rather than a placeholder.
- Added a tracked raw-data guide with the source URL, timestamps, exact size, SHA-256,
  format, license, regeneration path, and warning that the publisher URL is a rolling
  snapshot.
- Standardized normal agent/operator work on checked-in commands, recorded module-based
  Python invocation and free-port rules, and added run and self-cleaning smoke-test
  helpers so routine work does not require ad hoc shell command chains.
- Required approved Git, test, build, and helper commands to run as separate tool calls
  rather than being joined with shell control operators that trigger redundant approval.
- Added requested overlay-color and precomputed distance-selector follow-ups and kept
  the remaining original optional features explicitly documented.
