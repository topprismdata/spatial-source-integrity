# Data Policy — What Ships and What Never Ships

This repository ships **code, contracts, and documentation only**. No commercial
dataset, no raw corpus, no run artifact, and no personally identifying
information is included. All conformance tests that need the private corpus
are marked `skipif` and skip automatically in a fresh clone.

## Layout of private data (outside this repo)

```
<SSI_DATA_ROOT>/          # default: repo root, override with SSI_DATA_ROOT
    raw/                  # raw extracts (immutable, hash-pinned in local manifests)
    corpus/               # per-city split corpus + manifests
    runs/                 # per-run artifacts (findings, anchors, review packs, ledgers)
<SSI_REF_ROOT>/           # default: ./refs (gitignored)
    *.geojson             # external reference geometries (e.g. OSM-derived parcels)
```

## Environment variables

| Variable | Purpose |
|---|---|
| `SSI_DATA_ROOT` | Root containing `raw/`, `corpus/`, `runs/` |
| `SSI_REF_ROOT` | Root holding external reference geojson files |
| `SSI_MASTER_CSV` | Master crawl CSV consumed by `tools/split_master_by_city.py` |

## Rules encoded in code

- Raw sources are immutable; every derived representation carries lineage.
- Reviewer rosters are loaded from `runs/<run>/review_roster.json` (private);
  shipped code falls back to neutral placeholders.
- `tools/build_public_repo.py` + `tools/sanitizer_map.json` regenerate the
  public tree from the private working tree; the denylist gate fails the build
  on any surviving sensitive pattern (person names, dataset brands, absolute
  paths, coordinates, hashes, keys).
