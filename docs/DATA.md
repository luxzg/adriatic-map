# Geographic data plan

## Preferred land source

Use the WGS84 land polygons published by
[osmdata.openstreetmap.de](https://osmdata.openstreetmap.de/data/land-polygons.html).
They are derived from OSM ways tagged `natural=coastline`, assembled into polygons,
and repaired where possible by the publisher. They represent continents and islands,
avoid artificial country extract edges, and are available under ODbL 1.0.

Use the unsimplified WGS84 source. Do not calculate distance in latitude/longitude or
Web Mercator. Select the complete relevant Adriatic geometry with a buffer beyond the
final marine area before any display clipping.

## Implemented processing steps

1. Download one explicit dated snapshot into ignored `data/raw/`; verify its checksum.
2. Record URL, retrieval timestamp, source timestamp if published, checksum, format,
   and license in machine-readable metadata shipped beside the output.
3. Read all land polygons intersecting an Adriatic area of interest plus a margin
   wider than the maximum supported buffer/simplification tolerance.
4. Validate and repair geometry conservatively; fail with useful diagnostics if a
   repair would discard unexpected geometry.
5. Transform to the approved metric CRS and buffer by exactly 11,112 m.
6. Dissolve overlaps. Intersect with an explicit Adriatic marine mask or otherwise
   remove land so the output represents marine water within range.
7. Simplify topology-preservingly only after correctness tests pass. Measure output
   deviation and verify curated small islands/islets remain represented.
8. Transform output to EPSG:4326 and write reviewed GeoJSON plus build metadata.
9. Run automated geometry, projection-error, clip-edge, and corridor sanity tests.

The implementation is `tools/build_coastal_buffer.py`, invoked through
`scripts/generate-data.sh`. It uses only Python's GDAL/OGR bindings. Current fixed
v1 parameters are:

- Output bounds: 11.4° E to 20.7° E and 39.0° N to 46.1° N.
- Source-selection margin: 1.0° outside every output edge.
- Metric CRS: custom WGS84 azimuthal equidistant projection centered at 43° N, 16° E.
- Buffer: exactly 11,112 m, with 24 segments per quadrant.
- Topology-preserving simplification: 50 m after buffering/dissolving/clipping.
- GeoJSON output precision: 0.000001°.
- Measured maximum short-segment projection error at test samples: 0.076324%.

The source is spatially selected and intersected only at the larger source extent.
The resulting land is dissolved, and holes are explicitly filled before buffering so
freshwater interiors cannot become marine distance sources. The buffered result has
land subtracted and is clipped only to the smaller output bounds.

Because coastline polygons are based on the marine high-water coastline rather than
freshwater lake shores, inland lakes should not become distance sources. Tests must
still verify this invariant and the marine-mask behavior.

## Rocks and other exposed features

Permanently exposed features correctly mapped as coastline islands/islets are already
part of the land-polygon source. Other OSM tags are semantically mixed: `natural=rock`
is often a point for attached exposed rock, while seamark rock tags can describe dry,
awash, or submerged hazards. Counting every such object as land would be incorrect.

Recommendation for v1: keep coastline-derived land authoritative and treat additional
rock extraction as an optional, separate layer. If included, define and test an
explicit allow-list of tags proving the feature is exposed above the relevant water
level; preserve source IDs/tags for audit; never silently combine submerged/ambiguous
features into the land layer.

For a later reproducible extraction, use a bounded OSM data snapshot (for example,
documented Geofabrik regional extracts) or a deliberately bounded one-time query.
The runtime application must never query Overpass for this data.

## Basemap

The proposed v1 uses normal interactive requests to the OSM standard raster tile URL
for only the current viewport. It must show `© OpenStreetMap contributors` visibly,
send a normal browser Referer, honor browser caching, and provide no bulk download or
offline-prefetch feature. The tile URL should be replaceable without restructuring
the application.

## Licensing and publication

OpenStreetMap data is © OpenStreetMap contributors under ODbL 1.0. The generated
overlay is expected to remain an OSM-derived database/data product and must be
published with the required attribution, ODbL notice, and source/processing offer.
The application code license is separate and is GPL-3.0-or-later.

Before committing generated data, review its metadata, attribution, license notice,
size, feature count, geometry validity, bounding box, and absence of raw/private data.

## Accuracy statement to publish with generated data

Record the exact CRS definition, library versions, buffer distance, buffer parameters,
simplification tolerance, source date, output coordinate precision, measured geodesic
error samples, and known source limitations. Do not describe the result as certified
or appropriate for navigation or legal determinations.
