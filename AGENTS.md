# Project instructions for AI agents

This repository is a public, small cross-platform Adriatic coastal-distance map.
Keep it simple, portable, reproducible, and clearly unsuitable for navigation.

Use English exclusively in the UI, documentation, source code, comments, notices,
metadata written by this project, and agent-maintained project text. Prefer broad
regional terms such as "the Adriatic", "the Croatian Adriatic coast", or "Dalmatia"
over lists of Croatian towns, islands, or other local names unless a precise named
location is technically necessary for a test or data record.

## Read first

Before changing code, data, build scripts, or workflow, read in full:

1. `AGENTS.md`
2. `README.md`
3. `PROJECT_OUTLINE.md`
4. `PROJECT_SETUP.md`
5. `docs/DATA.md`
6. `TODO.md`
7. the latest `CHANGELOG.md` entries
8. `LICENSE`
9. `THIRD_PARTY_NOTICES.md`
10. `INITIAL_PROMPT.md` for historical context only

The generic `codex-coding-rules` rulebook also applies. Current user instructions
override these files.

## Approved implementation direction

The planning gate was cleared by the user on 2026-08-22. Use a tiny Go server with an
embedded Leaflet UI and reviewed generated data, plus a maintainer-only Python/GDAL
GIS tool. The supported precomputed choices are exactly `1/3/6/12/20 NM`, with 6 NM
as the default. Use normal viewport-only online OSM basemap tiles, keep
coastline-derived land authoritative, and keep raw downloads and intermediates out of
Git.

The overlay color is user-selectable, with `#0e0af5` as the default. Point inspection
must be an explicit toggle, off by default; it reports only the precomputed distance
band and selected-zone classification. It must not imply an exact surveyed distance or
legal determination. The distance choices correspond to bands used in current
Croatian navigation-area rules, but vessel documents, qualifications, additional
restrictions, and official current sources remain authoritative.

Do not add a separate rock layer, offline basemap, multiple detail levels/vector tiles,
dynamic data updates, or a database unless the user explicitly reverses the current
decision. The accepted coastline overlay is adequate and the project must stay simple.

## Public-repository and data safety

- The intended remote is public: `git@github.com:luxzg/adriatic-map.git`.
- Never inspect, print, stage, or publish credentials, private data, machine-local
  configuration, raw personal files, or unrelated files.
- Raw downloads and preprocessing intermediates belong under ignored `data/raw/`
  and `data/work/` paths.
- Only reviewed, redistributable, reasonably sized generated data belongs under
  `data/generated/` and in Git.
- Record each source URL, retrieval date, checksum, license, processing parameters,
  and output statistics as described in `docs/DATA.md`.
- Do not treat image, viewport, extract, country, or clipping boundaries as land.
- Do not treat submerged rocks, reefs, or freshwater shorelines as exposed marine
  land. If the current no-rock-layer decision is ever reversed, preserve any such
  inputs as a separate identifiable layer.

## Engineering workflow

- Prefer the smallest coherent implementation with minimal runtime dependencies.
- Use helper scripts in `scripts/` for repeated build, test, data generation, and
  release tasks once their real commands are known.
- Do not invent commands in docs. Add commands only with the corresponding files,
  then verify them locally.
- Every code or data-generation change must include appropriate automated tests,
  including GIS sanity checks documented in `PROJECT_OUTLINE.md`.
- For frontend changes, perform an actual browser smoke test when tooling permits.
- Update `CHANGELOG.md`, `TODO.md`, `FINISHED_TASKS.md`, and affected documentation
  in the same coherent change.
- Documentation-only changes do not bump the application version.
- Use SemVer beginning at `0.1.0`, with at least a patch bump for each coherent
  code/release pass.
- Before reporting completion, run the documented format/test/build commands, then
  review `git status --short` and the full diff.

Current application commands:

- Test and vet: `./scripts/test.sh`
- Test only the GIS pipeline: `./scripts/test-gis.sh`
- Download the ignored land source: `./scripts/download-data.sh`
- Generate all reviewed overlays: `./scripts/generate-data.sh "<source timestamp>"`
- Validate one distance against the local raw source:
  `./scripts/validate-data.sh <1|3|6|12|20>`
- Build Linux and Windows release binaries: `./scripts/build-release.sh`
- Run from source: `./scripts/run.sh`
- Run on a chosen loopback port: `./scripts/run.sh -listen 127.0.0.1:<port>`
- Run on an automatically selected free port: `./scripts/run.sh -listen 127.0.0.1:0`
- Build and smoke-test the embedded application: `./scripts/smoke-test.sh`

## Standard-command policy

- Prefer the project commands above so each safe recurring command can receive one
  narrowly scoped approval. Do not replace them with long shell one-liners, unusual
  command chains, manually assembled background processes, or arbitrary fixed ports.
- Issue routine approved commands as separate tool calls. In particular, do not join
  `git add`, `git status`, `git diff`, `git commit`, `git push`, tests, or builds with
  `&&`, `;`, pipelines, shell wrappers, or similar operators merely for convenience.
  Separate calls preserve the user's existing narrow approvals and make each action
  and result clear.
- Exceptions are allowed for diagnosis when a standard command fails or does not
  expose enough information. Explain the exception, keep it read-only or reversible
  where possible, and turn repeated diagnostic sequences into a checked-in helper.
- Run Python GIS packages from the repository root through their modules, for example
  `python3 -m tools.build_coastal_buffer`; do not invoke files such as
  `python3 tools/build_coastal_buffer.py` because package imports may then fail.
- The server's `127.0.0.1:8080` address is only a default. Never assume a particular
  test port is free; pass any valid loopback port through `-listen`, or use port `0`
  and read the selected port from the startup message.
- Keep generated caches under the ignored project-local cache directories established
  by the helpers. Do not construct one-off cache/environment commands unless debugging.
- Keep long-running generation visibly active: preserve per-band phase messages,
  one-blank-line band separation, per-band generation/validation timing, and total
  elapsed time. Do not emit thousands of per-source-polygon progress lines.

## Project observations

- The user visually accepted version 0.1.2 on Linux in a normal browser and in mobile
  device emulation. The 50 m topology-preserving simplification is acceptable for this
  informational map. The user later confirmed version 0.2.0 distance zones, color
  selection, and point inspection work on Linux. Windows runtime behavior remains
  untested by the user.
- The reusable 925,340,242-byte source archive lives at
  `data/raw/land-polygons-split-4326.zip`, inside the project rather than a temporary
  directory. It is intentionally ignored and must not be staged. Its provenance,
  checksum, versions, and rolling-source limitation are documented in
  `data/raw/README.md`, `docs/DATA.md`, and generated metadata.
- The `data/generated/adriatic_*nm.geojson` files are not placeholders. They are the
  reviewed, tracked ODbL-derived runtime overlays. Keep their notice, catalog, and
  metadata beside them.

## Git workflow

After the planning gate is cleared, initialize `main`, add the supplied `origin`,
and verify it before the first push. Preserve unrelated user changes. When a commit
is requested, use `git add -A`, a concise multiline message, and push only after
the relevant checks pass. Never force-push or rewrite history unless explicitly
requested.
