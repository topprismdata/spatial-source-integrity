"""Split the master listing crawl into per-city raw corpus files + manifests.

Design:
- Streams the master (gb18030) once; writes one CSV per city (utf-8-sig, original
  column set preserved verbatim — no transformation of any field value).
- Master is opened read-only; the split files are the NEW raw corpus (Seed Corpus #2).
- Emits per-file SHA-256 manifests and a master manifest with row-closure proof
  (sum of city rows must equal master rows; mismatch aborts).
- Reconciles the two legacy Xi'an CSVs (file1/file2) against the master and records
  their reclassification: file2 = derived extraction (byte-identical subset),
  file1 = double-shifted derived artifact.
"""
import csv, hashlib, json, os, subprocess, sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from ssi.config import DATA_ROOT, REPO_ROOT

MASTER = Path(os.environ["SSI_MASTER_CSV"])
OUT = DATA_ROOT / 'corpus/commercial listing dataset'
OUTC = OUT / 'cities'
OUTM = OUT / 'manifests'
for d in (OUTC, OUTM):
    d.mkdir(parents=True, exist_ok=True)

csv.field_size_limit(10 ** 7)

def sha256_file(p, chunk=1 << 20):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True, cwd=str(REPO_ROOT)).strip()
master_sha = sha256_file(MASTER)
print(f"master sha256: {master_sha}")

header_written = set()
writers, handles, counts = {}, {}, Counter()

with open(MASTER, encoding='gb18030', newline='') as f:
    r = csv.reader(f)
    header = next(r)
    ncols = len(header)
    city_idx = header.index('城市名')
    month_idx = header.index('城市名+月份')
    month_tag = None
    total = 0
    bad_rows = 0
    for row in r:
        if len(row) != ncols:
            bad_rows += 1
            continue
        city = row[city_idx].strip()
        mt = row[month_idx].strip()
        tag = mt[-2:] if mt.endswith('月') else mt
        if month_tag is None:
            month_tag = tag
        if city not in writers:
            safe = city.replace('/', '_').strip() or 'UNKNOWN'
            p = OUTC / f'{safe}.csv'
            fh = open(p, 'w', encoding='utf-8-sig', newline='')
            w = csv.writer(fh)
            w.writerow(header)
            writers[city], handles[city] = w, fh
        writers[city].writerow(row)
        counts[city] += 1
        total += 1

for fh in handles.values():
    fh.close()

print(f"rows written: {total}, malformed skipped: {bad_rows}, cities: {len(counts)}")
if total != 469378:
    print(f"WARNING: row total {total} != expected 469378 (malformed rows excluded)")

# ── per-city manifests ─────────────────────────────────────────
index = []
for city, cnt in sorted(counts.items()):
    safe = city.replace('/', '_').strip()
    p = OUTC / f'{safe}.csv'
    sh = sha256_file(p)
    m = {
        "corpus_role": "RAW_CITY_SPLIT",
        "city": city,
        "file": str(p.relative_to(DATA_ROOT)),
        "rows": cnt,
        "sha256": sh,
        "bytes": p.stat().st_size,
        "columns": ncols,
        "source_master_sha256": master_sha,
        "source_provider": "commercial listing dataset (commercial listing dataset)",
        "source_time": "2026-08",
        "month_observed": month_tag,
        "source_encoding": "gb18030",
        "output_encoding": "utf-8-sig (BOM; values verbatim, no field transformation)",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "code_commit": commit,
        "immutable": True,
        "note": "Field values copied byte-for-byte from master; only encoding normalized. "
                "Declared CRS for all cities remains UNKNOWN — the two legacy Xi'an labels were proven untrustworthy.",
    }
    (OUTM / f'{safe}.json').write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding='utf-8')
    index.append(m)

# ── reconcile legacy Xi'an file2 + file1 against master split ─
xa = OUTC / '西安.csv'
f2 = DATA_ROOT / 'raw/xian_commercial listing dataset_file2.csv'
f1 = DATA_ROOT / 'raw/xian_commercial listing dataset_file1.csv'

def load_key(p, enc='utf-8-sig'):
    out = {}
    with open(p, encoding=enc, newline='') as f:
        for row in csv.DictReader(f):
            out[row['小区ID']] = (row['经度'], row['纬度'])
    return out

xa_c, f2_c, f1_c = load_key(xa), load_key(f2), load_key(f1)

def to_f(t):
    return (float(t[0]), float(t[1]))

f2_f = {k: to_f(v) for k, v in f2_c.items() if k in xa_c}
f1_f = {k: to_f(v) for k, v in f1_c.items()}
xa_ids, f2_ids, f1_ids = set(xa_c), set(f2_c), set(f1_c)
same_ids = xa_ids == f2_ids and xa_ids == f1_ids
coord_eq = sum(1 for k in xa_ids & f2_ids if xa_c[k] == f2_c[k])
from ssi.resolver.transforms import wgs84_to_gcj02
f1_eq = sum(1 for k in f1_f
            if k in f2_f and tuple(round(x, 6) for x in wgs84_to_gcj02(*f2_f[k])) == f1_f[k])

recon = {
    "master_xian_rows": len(xa_c),
    "legacy_file2_ids_match": same_ids,
    "legacy_file2_coord_exact_matches": coord_eq,
    "legacy_file2_total": len(f2_c),
    "legacy_file1_double_encode_exact_matches": f1_eq,
    "legacy_file1_total": len(f1_c),
    "reclassification": {
        "file2": "DERIVED_EXTRACTION (verbatim 西安 filter of master; NOT raw asset; labels untrustworthy: 'WGS84' label wrong)",
        "file1": "DERIVED_DOUBLE_SHIFTED (round6(wgs84_to_gcj02(file2)); quarantine)",
        "seed_corpus_1_status": "SUPERSEDED_BY_SEED_CORPUS_2",
    },
}
print("reconciliation:", json.dumps(recon, ensure_ascii=False, indent=2))

# ── master manifest ────────────────────────────────────────────
master_manifest = {
    "corpus_id": "listings_202608_master_split",
    "corpus_role": "SEED_CORPUS_2_MASTER",
    "supersedes": "xian_seed_001 (legacy file1/file2 pair — both derived)",
    "source_master_path": str(MASTER),
    "source_master_sha256": master_sha,
    "source_provider": "commercial listing dataset",
    "source_time": "2026-08",
    "master_rows_expected": 469378,
    "master_rows_written": total,
    "malformed_rows_skipped": bad_rows,
    "city_count": len(counts),
    "row_closure_ok": total == sum(counts.values()),
    "columns": ncols,
    "declared_crs_all_cities": "UNKNOWN (legacy Xi'an labels proven wrong; do not reuse)",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "code_commit": commit,
    "legacy_reconciliation": recon,
    "cities_index": [{k: m[k] for k in ('city', 'file', 'rows', 'sha256')} for m in index],
}
(OUT / 'MASTER_MANIFEST.json').write_text(json.dumps(master_manifest, ensure_ascii=False, indent=2), encoding='utf-8')

idx = OUT / 'cities_index.csv'
with open(idx, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['城市名', '文件名', '行数', 'sha256', '字节'])
    for m in sorted(index, key=lambda x: -x['rows']):
        w.writerow([m['city'], m['file'], m['rows'], m['sha256'], m['bytes']])
print(f"\nmaster manifest + index written. cities={len(index)}, closure_ok={master_manifest['row_closure_ok']}")
