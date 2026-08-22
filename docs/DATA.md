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

1. Download one explicit snapshot into ignored `data/raw/`; verify its checksum.
2. Record URL, retrieval timestamp, published source timestamp, checksum, format,
   and license in machine-readable metadata shipped beside the output.
3. Read all land polygons intersecting an Adriatic area of interest plus a margin
   wider than the maximum supported buffer/simplification tolerance.
4. Validate and repair geometry conservatively; fail with useful diagnostics if a
   repair would discard unexpected geometry.
5. Transform to the approved metric CRS and independently buffer by exactly 1,852,
   5,556, 11,112, 22,224, and 37,040 m (1/3/6/12/20 NM).
6. For each distance, dissolve overlaps. Intersect with an explicit Adriatic marine
   mask or otherwise remove land so the output represents marine water within range.
7. Simplify each result topology-preservingly only after correctness tests pass.
   Measure output deviation and verify curated small islands/islets remain represented.
8. Transform each output to EPSG:4326 and write reviewed GeoJSON plus build metadata.
9. Run automated geometry, projection-error, clip-edge, corridor, and cross-band
   sanity tests.

The implementation is `tools/build_coastal_buffer.py`, invoked through
`scripts/generate-data.sh`. The helper builds and validates all five distances; use
`scripts/validate-data.sh DISTANCE` to validate one supported distance. It uses only
Python's GDAL/OGR bindings. Current fixed parameters are:

- Output bounds: 11.4° E to 20.7° E and 39.0° N to 46.1° N.
- Source-selection margin: 1.0° outside every output edge.
- Metric CRS: custom WGS84 azimuthal equidistant projection centered at 43° N, 16° E.
- Buffers: exactly 1,852/5,556/11,112/22,224/37,040 m, each with 24 segments per
  quadrant.
- Topology-preserving simplification: 50 m after buffering/dissolving/clipping.
- GeoJSON output precision: 0.000001°.
- Measured maximum short-segment projection error at test samples: 0.076324%.

The source is spatially selected and intersected only at the larger source extent.
The resulting land is dissolved, and holes are explicitly filled before buffering so
freshwater interiors cannot become marine distance sources. The buffered result has
land subtracted and is clipped only to the smaller output bounds.

## Reviewed 0.2.0 data snapshot

The tracked overlays were generated and reviewed on 2026-08-22 with these recorded
inputs and results:

- Source timestamp: `2026-08-22T03:36:41Z`; local retrieval timestamp:
  `2026-08-22T16:44:25Z`.
- Source archive: 925,340,242 bytes; SHA-256
  `43587830123e64eec8d4b5ac9259fdeb335b27e951fd36c3cc44eaa318e63e01`.
- Tools: Python 3.13.12, GDAL 3.12.3, and PROJ 9.8.1.
- Selected input: 4,722 features and 4,725 polygons after the safely margined spatial
  selection.
- Output: five valid WGS84 MultiPolygons totaling 5,354,919 bytes:

  | Distance | Area (km²) | Bytes | SHA-256 |
  | --- | ---: | ---: | --- |
  | 1 NM | 14,049.202 | 1,160,648 | `c62e4c08b5d66bd2cecb344991daae5cd6aaccf77fc7456bb7eacb498430dc49` |
  | 3 NM | 34,090.783 | 1,083,500 | `58b874a91695710c63a56ae944d1bbf45734a6935beb63d087d28e7ba788294c` |
  | 6 NM | 58,001.174 | 1,052,107 | `e9154b7d1f1f1fd23c5b54c9e88e39f35f8d5f78ad42bd309645a73afcb29c05` |
  | 12 NM | 99,073.399 | 1,034,570 | `23b8b2f76f09adce8ec70f1ec6f1c6537321305f55af094e750e5bf01048c14e` |
  | 20 NM | 143,908.576 | 1,024,094 | `bc7ef2332dfa6c0af966ffd1291b6d130cfed91e1bb9d6af0951265a32ebb443` |

- Automated source-to-output review: 1,258 regional grid classifications across the
  five outputs, two additional points skipped within the configured boundary
  tolerance, and zero mismatches. Each output also passed three marine samples, two
  land samples, one Dalmatian corridor sample, and retention of a coastal zone around
  a roughly 0.01 km² source islet.
- Earlier visual geometry review of the unchanged 6 NM output covered the northern
  and southern Adriatic, both coasts, island-dense zones, open-sea gaps, and output
  edges; no obvious clipping-edge or land-fill artefacts were found. The user later
  confirmed on Linux that all five selectable zones display and operate correctly.

The authoritative machine-readable records are `data/generated/metadata.json` for
6 NM and `data/generated/adriatic_DISTANCEnm.metadata.json` for the other distances.
`data/generated/overlays.json` is the runtime catalog. The generated overlays are
accompanied by `data/generated/NOTICE.md` and remain governed by ODbL 1.0.

The user repeated the complete five-band generation and validation workflow on Linux
on 2026-08-22. It completed in 7m 22s, every band again had zero grid mismatches, and
the GeoJSON outputs, areas, and checksums remained unchanged. The tracked metadata
audit timestamps record this later successful run.

The 925 MB archive remains locally reusable at the ignored project path
`data/raw/land-polygons-split-4326.zip`; it was not downloaded to or removed from a
temporary directory. `data/raw/README.md` keeps the directory and provenance visible
in a fresh clone. The publisher URL serves a rolling current snapshot, so later
downloads may not reproduce the exact 2026-08-22 checksum. A regeneration must record
the newly retrieved snapshot's timestamp, size, and checksum rather than reuse old
values.

Because coastline polygons are based on the marine high-water coastline rather than
freshwater lake shores, inland lakes should not become distance sources. Synthetic
tests verify this invariant and the marine-only buffer behavior.

## Rocks and other exposed features

Permanently exposed features correctly mapped as coastline islands/islets are already
part of the land-polygon source. Other OSM tags are semantically mixed: `natural=rock`
is often a point for attached exposed rock, while seamark rock tags can describe dry,
awash, or submerged hazards. Counting every such object as land would be incorrect.

The accepted coastline geometry already gives the intended result, so a separate rock
or seamark layer is deliberately not planned. If that decision is ever reversed, it
must use an explicit allow-list proving features are exposed above the relevant water
level, preserve source IDs/tags for audit, and never silently combine submerged or
ambiguous hazards into the land layer. Runtime Overpass queries remain out of scope.

## Basemap

V1 uses normal interactive requests to the OSM standard raster tile URL
for only the current viewport. It must show `© OpenStreetMap contributors` visibly,
send a normal browser Referer, honor browser caching, and provide no bulk download or
offline-prefetch feature. The tile URL should be replaceable without restructuring
the application.

## Licensing and publication

OpenStreetMap data is © OpenStreetMap contributors under ODbL 1.0. The generated
overlay is expected to remain an OSM-derived database/data product and must be
published with the required attribution, ODbL notice, and source/processing offer.
The application code license is separate and is GPL-3.0-or-later.

The committed generated data was reviewed for metadata, attribution, license notice,
size, feature count, geometry validity, bounding box, and absence of raw/private data.

## Accuracy and limitations

The exact CRS definition, library versions, buffer distance and parameters,
simplification tolerance, timestamps, coordinate precision, source checksum, output
statistics, and measured validation results are recorded in metadata. The maximum
measured local scale error is 0.076324%; simplification may move the displayed
boundary by up to its 50 m configured tolerance in ordinary cases. The result also
inherits OSM coastline completeness and temporal limitations and is clipped to the
documented regional display bounds.

The overlay is an informational visualization. It is not certified and must not be
used for navigation, route planning, legal-distance determinations, or as a substitute
for official nautical data.

Point inspection performs containment checks against the five simplified precomputed
overlays. It reports only a band such as “more than 3 NM and within 6 NM”; it does not
calculate an exact distance. A point outside all overlays is ambiguous: it may be more
than 20 NM from mapped land, on land, or outside the configured region.

The preset values correspond to navigation-area distances in Article 37 of Croatia's
applicable boat and yacht regulation, as listed by the
[Croatian Ministry](https://mmpi.gov.hr/more-86/upisnik-brodova-republike-hrvatske/upute-za-upis/pravni-izvori-24663/upis-plovila/25288)
and published in the
[Official Gazette](https://narodne-novine.nn.hr/clanci/sluzbeni/2020_01_13_223.html).
The application does not determine which band applies to any vessel or person; users
must consult current official documents and requirements.
