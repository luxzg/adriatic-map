# Raw geographic source data

This tracked file keeps the ignored raw-data directory visible and documents its
contents. Large source archives belong here inside the project, never in a temporary
directory and never in Git.

The current local archive is:

- Path: `data/raw/land-polygons-split-4326.zip`
- Source: <https://osmdata.openstreetmap.de/download/land-polygons-split-4326.zip>
- Published source timestamp: `2026-08-22T03:36:41Z`
- Local retrieval timestamp: `2026-08-22T16:44:25Z`
- Size: 925,340,242 bytes
- SHA-256: `43587830123e64eec8d4b5ac9259fdeb335b27e951fd36c3cc44eaa318e63e01`
- Format: zipped unsimplified WGS84 shapefile
- License: ODbL 1.0; © OpenStreetMap contributors

Download the current publisher archive with:

```bash
./scripts/download-data.sh
```

The publisher URL is a rolling current snapshot. A future download may have a new
timestamp, size, and checksum; record those new values rather than claiming it is the
2026-08-22 input. The helper refuses to overwrite an existing archive. Exact tool and
processing versions for the reviewed output are in `../generated/metadata.json`, with
the complete method in `../../docs/DATA.md`.

The five reviewed derived runtime overlays are intentionally tracked under
`../generated/` because they total only 5,354,919 bytes (about 5.4 MB). They are actual
data, not placeholders, and remain governed by the adjacent ODbL notice. The files and
their metadata are enumerated by `../generated/overlays.json`.
