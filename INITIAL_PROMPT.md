# Adapted initial project brief

> Historical context: adapted from the user-supplied ChatGPT web-agent prompt on
> 2026-08-22. Place-specific examples and non-English terminology were generalized at
> the user's direction. This is not current implementation truth; confirmed decisions
> in `PROJECT_OUTLINE.md`, `PROJECT_SETUP.md`, and later user instructions take
> precedence.

Create a small cross-platform web application that interactively shows the Adriatic Sea and highlights all sea areas that are within a configurable distance of the nearest land feature.

The primary purpose is currently to visualize the area within **6 nautical miles of the nearest mainland coast, island, islet, or other relevant exposed land feature**.

The application must run easily on both Linux and Windows desktop systems.

## Main requirement

Display an interactive map of the Adriatic with a GIS-derived overlay showing:

**distance from nearest land <= 6 NM**

where:

* 1 NM = 1852 metres
* 6 NM = 11,112 metres

The overlay must be calculated from actual geographic geometry. Do NOT approximate the distance visually and do NOT treat map/image boundaries as land.

The important initial area is the Croatian Adriatic coast, particularly Dalmatia. Preferably load enough geographic data to cover the **entire Adriatic**, including every bordering country, so that calculations near the edge of a displayed viewport are always correct.

## Geographic data

Use a real published geographic dataset.

OpenStreetMap is a good preferred source because sufficiently detailed OSM coastline/land data can include:

* mainland coastline
* islands
* small islands
* islets
* possibly relevant rocks / exposed features

Natural Earth may be used as a fallback or for initial prototyping, but its generalized geometry is probably insufficient for the final detailed Adriatic-island implementation.

Investigate the most appropriate way to obtain detailed OSM land/coastline geometry.

Do not make the application dependent on making huge live Overpass API requests every time it starts.

Prefer:

1. obtain/download the required geographic source data;
2. preprocess it once;
3. save the resulting simplified geometry or generated buffer locally;
4. let the web UI load the prepared GeoJSON/vector data quickly.

Keep the preprocessing procedure reproducible and documented.

### Small islands and rocks

Include smaller islands/islets wherever the geographic dataset provides real land polygons.

Also investigate OSM features representing exposed rocks and similar land features.

If rock features are included, keep them as a separately identifiable source/layer so they can later be enabled or disabled independently.

Do not invent land geometry.

## 6 NM calculation

The 6 NM zone must be a mathematically computed geospatial buffer.

Do not perform the calculation directly in latitude/longitude degrees.

Use either:

* an appropriate metric projected CRS for the Adriatic, or
* a library that performs correct geodesic buffering/distance calculations.

The result should be sufficiently accurate for visualization at normal nautical-chart zoom levels.

The calculation must happen against the complete relevant dataset BEFORE clipping or displaying a viewport.

For example:

* calculate using the entire Adriatic land dataset;
* then display/crop whatever viewport the user selects.

This avoids the earlier problem where the western or southern image boundary was accidentally interpreted as land.

Merge overlapping 6 NM buffers so the result appears as a continuous region.

Holes representing inland lakes must NOT create coastal-distance zones. We are interested in the marine coastline, not freshwater bodies inside mainland polygons.

## Important validation case

Use one or more narrow inter-island corridors along the Dalmatian coast as sanity checks.

Where the minimum sea distance is below approximately 12 NM, the 6 NM buffers from both sides must touch or overlap.

If a sizeable ">6 NM" gap appears in such a corridor, something is wrong with the geometry, units or projection.

Add a few similar automated GIS sanity tests if practical.

## Interactive map UI

Use a lightweight mapping library such as:

* Leaflet, or
* MapLibre GL JS / OpenLayers if there is a good reason.

Use an OpenStreetMap-compatible basemap.

The UI should initially be very simple.

Required controls:

* pan
* zoom
* toggle the 6 NM overlay
* overlay opacity slider
* fit/view entire Adriatic
* fit/view Dalmatia
* optional current buffer-distance display

Initial overlay styling:

* semi-transparent orange/amber zone = within 6 NM
* normal map = outside the zone
* optional thin outline at the 6 NM limit

Make the map usable on desktop and reasonably usable on a tablet/mobile browser as well.

## Useful optional feature

If easy to implement cleanly, make the buffer distance configurable:

* input in NM
* default = 6 NM
* examples: 1, 3, 6, 12 NM

However, do not compromise the quality or simplicity of the initial 6 NM implementation.

If dynamic buffering of the full coastline is computationally expensive, keep 6 NM pre-generated in v1 and design the code so additional precomputed distances can later be added.

## Optional inspection feature

A useful later feature would be clicking anywhere on the sea and displaying:

* latitude / longitude
* approximate distance to nearest land
* whether the point is within the selected NM limit

Do not make this necessary for the first working implementation.

## Architecture

Keep this deliberately small.

Preferred possibilities, in order of simplicity:

### Option A – static web application

* HTML
* CSS
* JavaScript
* Leaflet/MapLibre
* locally stored generated GeoJSON/vector overlay

A simple local HTTP server can be used to serve it.

### Option B – tiny Go application

A small Go executable that:

* serves the static frontend;
* serves prepared GeoJSON/vector files;
* requires no database;
* has minimal external runtime dependencies.

This would be particularly convenient because the same project can build small binaries for Linux and Windows.

### Preprocessing

It is perfectly acceptable, and probably preferable, to use a separate Python preprocessing script with:

* GeoPandas
* Shapely
* pyproj

to prepare the detailed land dataset and generate the 6 NM union geometry.

That script is a build/data-generation tool and does not need to run when the web application is used.

Suggested overall architecture:

`OSM/source coastline data`
→ `Python GIS preprocessing`
→ `clean marine land geometry`
→ `11,112 m buffer`
→ `union/dissolve`
→ `simplified GeoJSON or vector representation`
→ `Go/static web application`
→ `interactive Leaflet/MapLibre map`

## Geometry simplification

The detailed Adriatic coastline can produce extremely large GeoJSON.

Use topology-preserving simplification where beneficial, but make sure small islands do not disappear.

If necessary, produce multiple levels of detail or investigate vector tiles.

For v1, prioritize correctness over extreme optimization.

The application should still load reasonably quickly on an ordinary desktop PC.

## Data attribution

Respect and display attribution required by whichever map/geographic datasets are used, especially OpenStreetMap.

Document:

* geographic data source
* preprocessing steps
* CRS/projection used
* buffer calculation
* simplification tolerance
* approximate expected accuracy

## Safety / scope

Clearly display a small note such as:

**"Informational visualization only. Not an official nautical chart or a substitute for official navigational data."**

Do not present the overlay as certified navigation data.

## Repository structure

Keep the repository understandable, for example:

```text
/
  README.md
  cmd/server/             # only if Go server is used
  web/
    index.html
    app.js
    style.css
  data/
    adriatic_6nm.geojson
  tools/
    build_coastal_buffer.py
  docs/
    DATA.md
```

Exact structure may differ if there is a cleaner solution.

## First implementation goal

Build a working prototype rather than overengineering it.

I should be able to:

1. start the application locally;
2. open it in a browser;
3. see the Adriatic map;
4. zoom into the Dalmatian archipelago;
5. see an accurately computed 6 NM overlay;
6. zoom in sufficiently to see how the overlay follows smaller islands/islets;
7. toggle the overlay and change its opacity.

Before considering the task complete, visually and mathematically validate several representative locations, especially narrow inter-island corridors along the Dalmatian coast.

Provide simple Linux and Windows startup/build instructions in the README.
