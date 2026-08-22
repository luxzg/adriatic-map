# Adriatic Map

Adriatic Map is a small cross-platform web application for exploring the
parts of the Adriatic Sea that are within a mathematically calculated distance of
the nearest exposed land. The first target is **6 nautical miles (11,112 metres)**
from mainland coasts, islands, and islets represented in published geographic data.

> **Informational visualization only. Not an official nautical chart or a substitute
> for official navigational data.**

## Status

Version 0.1.2 provides the complete first prototype: the tested local application,
the reviewed 6 NM overlay generated from OSM-derived coastline land polygons, and the
reproducible Python/GDAL pipeline used to build and validate it. See
[PROJECT_OUTLINE.md](PROJECT_OUTLINE.md) for the v1 scope and [docs/DATA.md](docs/DATA.md)
for the exact data method and limitations.

## Included in v1

- Interactive Adriatic map with pan and zoom.
- A precomputed, merged 6 NM coastal-distance overlay.
- Overlay visibility and opacity controls.
- Quick views for the full Adriatic and Dalmatia.
- Detailed OSM-derived mainland, island, and islet geometry.
- Reproducible offline preprocessing; no large live Overpass request at startup.
- Linux and Windows operation without a database.

The application is a tiny Go executable that serves an embedded local Leaflet
frontend and prepared overlay. A separate Python GIS tool regenerates the overlay;
end users do not need Python or GIS packages.

## Data and attribution

The land source is the OSM-derived coastline polygon dataset published at
[osmdata.openstreetmap.de](https://osmdata.openstreetmap.de/data/land-polygons.html).
OpenStreetMap data is © OpenStreetMap contributors and licensed under the
[ODbL 1.0](https://www.openstreetmap.org/copyright). A normal interactive OSM
basemap is used for v1 and retains visible attribution.

The application code and original project content are licensed under
[GPL-3.0-or-later](LICENSE). OSM inputs and generated OSM-derived data remain governed
by their applicable ODbL terms. See [docs/DATA.md](docs/DATA.md) and the shipped
[generated-data notice](data/generated/NOTICE.md) for the data workflow, provenance,
validation, and limitations.

## Run from source

Go 1.26 or newer is required:

```bash
go run ./cmd/adriatic-map
```

The server listens on <http://127.0.0.1:8080/> and opens the default browser. Use
`-open=false` to suppress browser launch or `-listen 127.0.0.1:9000` to select a
different local port. Stop it with Ctrl+C.

## Build and test

On Linux, run the complete test/vet/check workflow and build both platform binaries:

```bash
./scripts/test.sh
./scripts/build-release.sh
```

Outputs are written to ignored `dist/`:

- `adriatic-map-linux-amd64`
- `adriatic-map-windows-amd64.exe`

On Windows PowerShell with Go installed:

```powershell
.\scripts\build-windows.ps1
.\dist\adriatic-map-windows-amd64.exe
```

Release binaries contain the UI and overlay data and require no database or Python.
The basemap requires internet access. Planning and deeper setup are documented in
[PROJECT_SETUP.md](PROJECT_SETUP.md).

## Regenerate geographic data

End users do not need GIS software. Maintainers regenerating the overlay need Python
3, GDAL command-line tools and Python bindings, `curl`, and about 1 GB for the ignored
source archive:

```bash
./scripts/download-data.sh
./scripts/test-gis.sh
./scripts/generate-data.sh "SOURCE LAST-MODIFIED TIMESTAMP"
```

The download helper never overwrites an existing source archive. The generation
metadata records its size and SHA-256 checksum, source and retrieval timestamps,
tool versions, projection, buffer and simplification parameters, output bounds,
area, validation samples, and measured projection error. `scripts/test.sh` performs
the full source-to-output validation when the ignored source archive is present. See
[docs/DATA.md](docs/DATA.md) for the exact method.

## AI assistance

This project is being designed and developed with assistance from OpenAI Codex and
other AI tools. AI-produced changes remain subject to human review, testing, data
license compliance, and the navigation disclaimer above.
