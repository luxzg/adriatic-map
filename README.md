# Adriatic Map

Adriatic Map is a planned small cross-platform web application for exploring the
parts of the Adriatic Sea that are within a mathematically calculated distance of
the nearest exposed land. The first target is **6 nautical miles (11,112 metres)**
from mainland coasts, islands, and islets represented in published geographic data.

> **Informational visualization only. Not an official nautical chart or a substitute
> for official navigational data.**

## Status

The documentation and implementation direction are approved. Application and data
pipeline work is underway. See [PROJECT_OUTLINE.md](PROJECT_OUTLINE.md) for the v1
scope and [TODO.md](TODO.md) for active work.

## Planned v1

- Interactive Adriatic map with pan and zoom.
- A precomputed, merged 6 NM coastal-distance overlay.
- Overlay visibility and opacity controls.
- Quick views for the full Adriatic and Dalmatia.
- Detailed OSM-derived mainland, island, and islet geometry.
- Reproducible offline preprocessing; no large live Overpass request at startup.
- Linux and Windows operation without a database.

The selected architecture is a tiny Go executable that serves an embedded local
Leaflet frontend and a prepared overlay. A separate Python GIS tool would regenerate
the overlay; end users would not need Python or GIS packages.

## Data and attribution

The preferred land source is the OSM-derived coastline polygon dataset published at
[osmdata.openstreetmap.de](https://osmdata.openstreetmap.de/data/land-polygons.html).
OpenStreetMap data is © OpenStreetMap contributors and licensed under the
[ODbL 1.0](https://www.openstreetmap.org/copyright). A normal interactive OSM
basemap is proposed for v1 and will retain visible attribution.

The application code and original project content are licensed under
[GPL-3.0-or-later](LICENSE). OSM inputs and generated OSM-derived data remain governed
by their applicable ODbL terms. See [docs/DATA.md](docs/DATA.md) for the proposed data
workflow and limitations.

## Running and development

Startup, build, test, and data-generation commands will be added only after the
architecture is approved and the corresponding scripts have been implemented and
verified. Planning and repository setup are documented in
[PROJECT_SETUP.md](PROJECT_SETUP.md).

## AI assistance

This project is being designed and developed with assistance from OpenAI Codex and
other AI tools. AI-produced changes remain subject to human review, testing, data
license compliance, and the navigation disclaimer above.
