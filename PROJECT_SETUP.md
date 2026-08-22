# Project setup and workflow

This file records the approved setup. Commands that depend on files not yet created
are deliberately not documented as if they already work.

## Known repository details

- Local root: `/home/luka/dev/adriatic-map`
- Intended public GitHub remote: `git@github.com:luxzg/adriatic-map.git`
- Intended default branch: `main`
- Implementation approved on 2026-08-22; Git initialization is the next workflow step
- Available locally: Git 2.53.0, Go 1.26.0, Python 3.13.12, GDAL `ogr2ogr`
- Not currently importable in system Python: GeoPandas/Shapely/pyproj as a set
- Project language: English exclusively
- Project license: GPL-3.0-or-later, excluding third-party and OSM-derived material
  governed by its own stated license

## Proposed repository layout

```text
/
  cmd/adriatic-map/       # tiny Go server, after approval
  web/                    # HTML/CSS/JS and locally vendored frontend assets
  data/
    generated/            # reviewed distributable overlay + metadata (tracked)
    raw/                  # source downloads (ignored)
    work/                 # intermediates (ignored)
  tools/                  # Python GIS generation code
  scripts/                # repeatable build/test/data/release helpers
  docs/DATA.md
```

The final generated overlay should be tracked only if its license is documented and
its size is practical for normal Git/GitHub use. Raw OSM downloads, local environments,
build outputs, secrets, and intermediates are ignored by the proposed `.gitignore`.

## Implementation workflow

1. Keep these docs synchronized with implementation and verify license/data notices.
2. Initialize Git on `main`; configure and verify the supplied `origin`; review and,
   if approved, publish a separate docs/license-only initial commit.
3. Implement one small vertical slice: server, map, placeholder/test overlay loading,
   and controls, without claiming GIS correctness yet.
4. Implement the reproducible GIS pipeline and tests against the available Python
   GDAL bindings; document any additional prerequisites before requiring them.
5. Generate and inspect the real overlay; record source metadata and validation.
6. Run format, automated tests, Go builds for Linux/Windows, and a browser smoke test.
7. Update docs/status/changelog, review the full diff, then commit and push each
   coherent pass as requested.

Repeated commands will receive checked-in helper scripts. Exact commands and required
package-install instructions will be added and verified during implementation, rather
than guessed during planning.

## Proposed release model

- Source stays small and public.
- End users download a platform binary containing the UI and reviewed overlay.
- Maintainers use Python only when regenerating geographic data.
- Release binaries and checksums go in GitHub Releases, not Git history.
- Application version: SemVer from `0.1.0`; docs-only changes do not bump it.

## Git initialization (documented, not yet run)

The approved initialization sequence is:

```bash
git init
git branch -M main
git remote add origin git@github.com:luxzg/adriatic-map.git
git remote -v
```

The initial commit and `git push -u origin main` should happen only after reviewing
the public file set and running the checks applicable at that point.
