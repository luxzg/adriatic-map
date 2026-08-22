# Adriatic Map

Adriatic Map is a small cross-platform web application for exploring the
parts of the Adriatic Sea that are within a mathematically calculated distance of
the nearest exposed land. It provides precomputed **1, 3, 6, 12, and 20 nautical
mile** choices from mainland coasts, islands, and islets represented in published
geographic data.

> **Informational visualization only. Not an official nautical chart or a substitute
> for official navigational data.**

## Status

Version 0.2.1 provides five reviewed distance overlays, user-selectable overlay color,
and an opt-in point inspector. It also adds readable progress and elapsed-time output
to the reproducible Python/GDAL generation workflow and uses `#0e0af5` as the default
overlay color. See
[PROJECT_OUTLINE.md](PROJECT_OUTLINE.md) for the v1 scope and [docs/DATA.md](docs/DATA.md)
for the exact data method and limitations.

## Included in v1

- Interactive Adriatic map with pan and zoom.
- Precomputed, merged 1/3/6/12/20 NM coastal-distance overlays.
- Distance selection plus overlay visibility, opacity, color-picker, and hex controls.
- Point inspection that is off by default and reports an approximate precomputed
  distance band only when enabled.
- Quick views for the full Adriatic and Dalmatia.
- Detailed OSM-derived mainland, island, and islet geometry.
- Reproducible offline preprocessing; no large live Overpass request at startup.
- Linux and Windows operation without a database.

The application is a tiny Go executable that serves an embedded local Leaflet
frontend and prepared overlays. A separate Python GIS tool regenerates the overlays;
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
./scripts/run.sh
```

The server listens on <http://127.0.0.1:8080/> and opens the default browser. Use
`./scripts/run.sh -open=false` to suppress browser launch or pass any available
loopback port, for example `./scripts/run.sh -listen 127.0.0.1:9000`. Port `0` asks
the operating system to choose a free port and the application prints and opens the
resulting URL. Stop it with Ctrl+C.

An internet connection is required to display the OpenStreetMap background map. The
application and coastal-distance overlays are embedded locally, but without internet
access the OSM background will show missing/blank tiles. Offline basemap packaging is
not supported or planned.

## Build and test

On Linux, run the complete test/vet/check workflow and build both platform binaries:

```bash
./scripts/test.sh
./scripts/build-release.sh
./scripts/smoke-test.sh
```

Outputs are written to ignored `dist/`:

- `adriatic-map-linux-amd64`
- `adriatic-map-windows-amd64.exe`

On Windows PowerShell with Go installed:

```powershell
.\scripts\build-windows.ps1
.\dist\adriatic-map-windows-amd64.exe
```

Release binaries contain the UI and all five overlay datasets and require no database
or Python.
The basemap requires internet access. Planning and deeper setup are documented in
[PROJECT_SETUP.md](PROJECT_SETUP.md).

## Regenerate geographic data

End users do not need GIS software. Maintainers regenerating the overlays need Python
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

Generation prints the active band and GIS phase as work progresses. After every band,
it reports generation, validation, and combined elapsed time; a final line reports the
total time for all five bands. Individual source polygons are not logged because the
pipeline processes thousands of them as aggregate geometry.

A user-validated complete regeneration on the documented Linux system took 7 minutes
22 seconds. Actual time depends on CPU and storage performance.

The 925 MB raw archive is stored inside this project at
`data/raw/land-polygons-split-4326.zip`, not in a temporary directory. It remains
available locally for reuse but is deliberately ignored by Git. The tracked
[raw-data guide](data/raw/README.md) records its URL, timestamps, exact byte size,
SHA-256, format, license, and rolling-snapshot caveat. The five reviewed derived
overlays total about 5.4 MB under `data/generated/`; they are intentionally tracked
and are not placeholders.

## Distance presets and legal context

The chosen bands match distance limits used for Croatian boat and yacht navigation
areas in Article 37 of the applicable regulation. The Croatian Ministry currently
lists the base regulation and its amendment as official sources:

- [Official Croatian Ministry legal-source listing](https://mmpi.gov.hr/more-86/upisnik-brodova-republike-hrvatske/upute-za-upis/pravni-izvori-24663/upis-plovila/25288)
- [Official Gazette regulation, Article 37](https://narodne-novine.nn.hr/clanci/sluzbeni/2020_01_13_223.html)
- [Official Gazette 2020 amendment](https://narodne-novine.nn.hr/clanci/sluzbeni/full/2020_04_52_1047.html)

This map does not establish which limit applies to a vessel or skipper. Registration,
technical category, issued documents, qualifications, weather/time restrictions,
local rules, and current official sources must be checked separately.

Inspection reports a band such as “more than 3 NM and within 6 NM,” not an exact
distance. A point outside every marine overlay may be more than 20 NM from mapped
land, on land, or outside the covered region.

## AI assistance

This project is being designed and developed with assistance from OpenAI Codex and
other AI tools. AI-produced changes remain subject to human review, testing, data
license compliance, and the navigation disclaimer above.
