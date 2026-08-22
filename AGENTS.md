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

The planning gate was cleared by the user on 2026-08-22. Implement the non-optional
v1 scope using a tiny Go server with an embedded Leaflet UI and reviewed generated
data, plus a maintainer-only Python/GDAL GIS tool. Use normal viewport-only online
OSM basemap tiles, keep coastline-derived land authoritative in v1, and keep raw
downloads and intermediates out of Git.

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
  land. Preserve optional rock inputs as a separate identifiable layer.

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
- Generate the reviewed overlay: `./scripts/generate-data.sh "<source timestamp>"`
- Build Linux and Windows release binaries: `./scripts/build-release.sh`
- Run from source: `go run ./cmd/adriatic-map`
- Runtime health/version check: `curl -sS http://127.0.0.1:8080/healthz`

## Git workflow

After the planning gate is cleared, initialize `main`, add the supplied `origin`,
and verify it before the first push. Preserve unrelated user changes. When a commit
is requested, use `git add -A`, a concise multiline message, and push only after
the relevant checks pass. Never force-push or rewrite history unless explicitly
requested.
