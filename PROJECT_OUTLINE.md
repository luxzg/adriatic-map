# Project outline

## Goal

Provide a small local web map that correctly visualizes Adriatic marine areas within
6 NM (11,112 m) of the nearest relevant exposed land geometry. The complete source
geometry must be processed before the output is clipped for display.

Initial geographic emphasis is the Croatian Adriatic coast, particularly Dalmatia.
The calculation extent should cover the entire Adriatic coast, including every
bordering country, with a safety margin beyond the display extent.

## V1 architecture

1. Download a dated OSM-derived coastline land-polygon snapshot.
2. Clip only after selecting all source geometry within an Adriatic safety margin.
3. Repair/normalize geometry, project it to an agreed metric CRS, buffer by 11,112 m,
   dissolve overlaps, restrict the result to Adriatic marine water, simplify without
   deleting meaningful small features, and export GeoJSON in WGS84.
4. Validate geometry and distances with automated GIS tests and recorded metrics.
5. Serve a small Leaflet UI and reviewed generated data from one Go executable.
6. Request normal basemap tiles only for the user's current viewport; never prefetch
   or bulk-download OSM's standard tiles.

Why this direction: the Go runtime can be a single Linux/Windows binary and the GIS
stack remains a maintainer-only build dependency. A purely static app is smaller in
source but still needs a local HTTP server, which is less predictable on Windows.

The selected projection is a custom Adriatic-centered azimuthal-equidistant CRS,
with its definition recorded exactly in data metadata. Its maximum measured local
scale error across representative regional samples is 0.076324%, below the 0.5%
acceptance gate. EPSG:3857 is not used for the distance calculation.

## V1 scope

- Fixed precomputed 6 NM overlay.
- Pan, zoom, overlay toggle, opacity slider, full-Adriatic view, and Dalmatia view.
- Amber/orange fill with an optional thin 6 NM boundary.
- Visible OSM attribution, data/source information, and navigation disclaimer.
- Responsive desktop and basic tablet/mobile layout.
- Reproducible data-generation inputs, parameters, tests, and metadata.
- Linux and Windows build/start documentation.

## Deferred unless unusually easy

- Multiple or dynamically calculated distances (1/3/6/12 NM).
- Click-to-inspect nearest-land distance and classification.
- Multiple levels of detail or vector tiles.
- Offline basemap tiles.
- Dynamic source updates or a database.

## Explicit non-goals

- Certified navigation, legal-distance determination, or route planning.
- Treating viewport, extract, country, image, or clipping boundaries as land.
- Large live Overpass queries during application startup.
- Invented rock/islet geometry or silently counting underwater hazards as land.
- A framework-heavy frontend, container stack, or long-running external service.

## Validation gate for v1

Automated checks should cover at least:

- 6 NM equals exactly 11,112 m in generation parameters and metadata.
- Selected narrow inter-island corridors along the Dalmatian coast have no sizeable
  `>6 NM` gap where opposing 6 NM zones should meet or overlap.
- Selected known land points are inside land, selected distant marine points are not
  accidentally classified because of a clip edge, and inland lakes do not create
  marine coastal zones.
- The output is valid WGS84 GeoJSON, lies within the intended Adriatic extent, and
  contains no unexpected edge-following buffer artefacts.
- Projection/buffering error is measured against geodesic reference samples near the
  northern, southern, eastern, and western limits.
- Simplification retains a curated sample of small Adriatic islands/islets and stays
  within an agreed positional tolerance.

Manual review should include Dalmatian island corridors, the northern and southern
Adriatic, and both eastern and western coasts at several normal chart-like zoom levels.
