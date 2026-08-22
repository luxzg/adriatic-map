# Project outline

## Goal

Provide a small local web map that correctly visualizes Adriatic marine areas within
1, 3, 6, 12, or 20 NM of the nearest relevant exposed land geometry. The complete
source geometry must be processed before the output is clipped for display.

Initial geographic emphasis is the Croatian Adriatic coast, particularly Dalmatia.
The calculation extent should cover the entire Adriatic coast, including every
bordering country, with a safety margin beyond the display extent.

## V1 architecture

1. Download a dated OSM-derived coastline land-polygon snapshot.
2. Clip only after selecting all source geometry within an Adriatic safety margin.
3. Repair/normalize geometry, project it to an agreed metric CRS, create independent
   1/3/6/12/20 NM buffers, dissolve overlaps, restrict results to Adriatic marine
   water, simplify without deleting meaningful small features, and export GeoJSON in
   WGS84.
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

## Current scope

- Five fixed precomputed 1/3/6/12/20 NM overlays, with 6 NM as the default.
- Pan, zoom, distance selection, overlay toggle, opacity and color controls,
  full-Adriatic view, and Dalmatia view.
- Opt-in point inspection reporting coordinates, an approximate precomputed distance
  band, and selected-zone membership; disabled by default.
- User-selectable fill and outline color with an amber/orange default.
- Visible OSM attribution, data/source information, and navigation disclaimer.
- Responsive desktop and basic tablet/mobile layout.
- Reproducible data-generation inputs, parameters, tests, and metadata.
- Linux and Windows build/start documentation.

## Deliberately not planned

- Additional rock/seamark extraction: the accepted coastline polygons already provide
  a clear and useful land definition; ambiguous rock semantics add complexity without
  a current need.
- Offline basemap packages: the application intentionally requests ordinary OSM tiles
  for the visible viewport and does not ship or bulk-download a separate tile archive.
- Multiple detail levels or vector tiles: the five compact GeoJSON files perform well
  enough without another data format or selection system.
- Dynamic source updates or a database: the reviewed static coastline snapshot and
  reproducible offline generation cover the intended use.

## Explicit non-goals

- Certified navigation, legal-distance determination, or route planning.
- Treating viewport, extract, country, image, or clipping boundaries as land.
- Large live Overpass queries during application startup.
- Invented rock/islet geometry or silently counting underwater hazards as land.
- A framework-heavy frontend, container stack, or long-running external service.

## Validation gate for v1

Automated checks should cover at least:

- Every supported nautical-mile preset converts to metres exactly in generation
  parameters and metadata: 1/3/6/12/20 NM equals 1,852/5,556/11,112/22,224/37,040 m.
- Selected narrow inter-island corridors along the Dalmatian coast change membership
  at the expected precomputed distance band.
- Selected known land points are inside land, selected distant marine points are not
  accidentally classified because of a clip edge, and inland lakes do not create
  marine coastal zones.
- Every output is valid WGS84 GeoJSON, lies within the intended Adriatic extent, and
  contains no unexpected edge-following buffer artefacts.
- Projection/buffering error is measured against geodesic reference samples near the
  northern, southern, eastern, and western limits.
- Simplification retains a curated sample of small Adriatic islands/islets and stays
  within an agreed positional tolerance.

Manual review should include Dalmatian island corridors, the northern and southern
Adriatic, and both eastern and western coasts at several normal chart-like zoom levels.
