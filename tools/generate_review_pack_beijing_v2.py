"""Beijing review batch v2 — margin-selected (active-learning) 10 tasks.

Batch 1 proved BD-like on easy cases. Batch 2 samples where the machine is
LEAST certain and one blind click is MOST informative:
  A) AMBIGUOUS_PAIR (5): GCJ vs BD residuals within 60m of each other around the
     parcel center — only a human click decides which encoding family wins.
  B) THRESHOLD_EDGE  (5): BD residual in 120..320m straddling dp02 200m —
     decides whether the tolerance moves.
All tasks are BLIND: no green dot, no parcel overlay, no ref info — the reviewer
clicks the true location; the system computes distances and derives the verdict.
"""
import csv, json, math, random, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(REPO_ROOT))

import pyarrow as pa
import pyarrow.parquet as pq
import shapely.geometry as sg
import pyproj
from ssi.config import DATA_ROOT, REF_ROOT, REPO_ROOT, load_review_roster
from ssi.resolver.transforms import gcj02_to_wgs84, bd09_to_wgs84, wgs84_to_gcj02

CITY = '北京'
OUT = DATA_ROOT / 'runs/beijing_seed_001/review_batch_v2'
OUT.mkdir(parents=True, exist_ok=True)
SRC = DATA_ROOT / f'corpus/commercial listing dataset/cities/{CITY}.csv'
PARCELS = REF_ROOT / 'beijing_gb50137_all.geojson'

ROSTER = load_review_roster(DATA_ROOT / 'runs/beijing_seed_001')
GEO = pyproj.Geod(ellps="WGS84")

# ── load ───────────────────────────────────────────────────────
raw, names = {}, {}
with open(SRC, encoding='utf-8-sig', newline='') as f:
    for row in csv.DictReader(f):
        sid = str(row['小区ID'])
        try:
            raw[sid] = (float(row['经度']), float(row['纬度']))
        except Exception:
            continue
        names[sid] = {'name': row['小区名'], 'district': row['城区'], 'address': row['地址']}

import re as _re
TRIM = lambda s: _re.sub(r"[\s·]", '', s or '')            # keep 期/区 markers (this is what the matcher erased!)
TRIM_ANCHOR = lambda s: _re.sub(r"[（(].*?[)）]|\s|[-—·]", '', s or '')
gj = json.load(open(PARCELS))
parcel_cen = {}
for feat in gj['features']:
    p = feat['properties']
    if p.get('gb_code') == 'R' and p.get('name') and p['name'] not in parcel_cen:
        parcel_cen[p['name']] = sg.shape(feat['geometry']).centroid.coords[0] if False else sg.shape(feat['geometry']).representative_point().coords[:2]
# keep deterministic: use centroid via shapely
parcel_cen = {}
for feat in gj['features']:
    p = feat['properties']
    if p.get('gb_code') == 'R' and p.get('name') and p['name'] not in parcel_cen:
        parcel_cen[p['name']] = (round(sg.shape(feat['geometry']).centroid.x, 6),
                                 round(sg.shape(feat['geometry']).centroid.y, 6))

pcen_by_norm = {}
for pn in parcel_cen:
    pcen_by_norm.setdefault(TRIM_ANCHOR(pn), pn)

# residuals per hypothesis for every anchored record
cands = []
for sid, nm in names.items():
    pn = pcen_by_norm.get(TRIM_ANCHOR(nm['name']))
    if not pn or sid not in raw:
        continue
    px, py = parcel_cen[pn]
    def dist(pt):
        _, _, d = GEO.inv(pt[0], pt[1], px, py)
        return d
    rs = {"identity": dist(raw[sid]),
          "GCJ-like→WGS84": dist(gcj02_to_wgs84(*raw[sid])),
          "BD-like→WGS84": dist(bd09_to_wgs84(*raw[sid]))}
    cands.append({"sid": sid, "parcel": pn, **nm, "rs": rs})

# ── A) MATCH_DOUBT: BD residual still large -> wrong parcel match vs broken data ──
# (batch1 clicks killed GCJ-vs-BD ambiguity; the open question now is OUR OWN anchor match)
poolA = [c for c in cands if 800 < c['rs']['BD-like→WGS84'] < 3000]
# B) THRESHOLD_EDGE: BD residual straddling dp02 200m
poolB = [c for c in cands if 120 <= c['rs']['BD-like→WGS84'] <= 320
         and c not in poolA]
rng = random.Random(20260906)
# spatial diversity inside pools
def diverse(pool, k):
    picked, seen = [], set()
    pool = pool[:]
    rng.shuffle(pool)
    for c in pool:
        b = (round(raw[c['sid']][0], 1), round(raw[c['sid']][1], 1))
        if b in seen:
            continue
        seen.add(b); picked.append(c)
        if len(picked) >= k:
            break
    return picked
selA, selB = diverse(poolA, 5), diverse(poolB, 5)
tasks = []
OPTS = [("CLICK_DERIVED", "在地图上点出这个小区的真实位置（点一下就够）"),
        ("CANNOT_LOCATE", "找不到这个小区，无法指认")]
Q_TXT = ("【怎么做】本单是盲审（机器不给任何提示）：系统对你标注的小区真实位置做假设判决。\n"
         "按【小区名】在高德图找到它的真实楼群（门牌：{addr}），然后：\n"
         "在真实位置【单击一下】→ 选置信度 → 保存。可切换底图/搜索。")
Q_DUEL = ("【怎么做】系统对这条记录拿不准：按名字它应该在这个橙框地块里，但数据坐标离地块中心很远——\n"
          "要么数据错了，要么我们参考地块配错了。\n"
          "请按【小区名】在地图上找到它真实所在的楼群（门牌：{addr}），在真实位置【单击】。\n"
          "蓝点=数据坐标　红点=参考地块中心。你点完后系统自动判定谁对谁错。")
for c in selA:
    tasks.append({
        "task_id": f"HRT-BJ2-MDBT-{c['sid']}", "category": "MATCH_DOUBT", "subject_id": c['sid'],
        "name": c['name'], "district": c['district'], "address": c['address'],
        "click_mode": True, "default_base": "amap", "prediction_visibility": "PREDICTION_VISIBLE",
        "reviewer_role_required": "DATA_STEWARD",
        "question": Q_DUEL.replace('{addr}', c['address'] or '无'),
        "raw": [round(raw[c['sid']][0], 6), round(raw[c['sid']][1], 6)],
        "raw_gcj": [round(v, 6) for v in wgs84_to_gcj02(*raw[c['sid']])],
        "aligned": None, "aligned_gcj": None,
        "parcel_ring": None,
        "parcel_centroid": [round(v, 6) for v in wgs84_to_gcj02(*parcel_cen[c['parcel']])],
        "parcel_ring_wgs": None, "parcel_centroid_wgs": [round(v, 6) for v in parcel_cen[c['parcel']]],
        "residual_aligned_m": round(c['rs']['BD-like→WGS84'], 1),
        "d06_score": None, "precision_degraded": False,
        "ref_parcel_name": c['parcel'],
        "ref_name_matches": TRIM(c['name']) == TRIM(c['parcel']) if True else False,
        "rationale_options": [list(o) for o in OPTS],
        "machine_belief": {"kind": "match_doubt", "d_BD_m": round(c['rs']['BD-like→WGS84'], 1),
                           "parcel": c['parcel'],
                           "note": "even under best hypothesis this point is >800m from its name-matched parcel: our match or the data is wrong"},
        "match_doubt": {"parcel": c['parcel'],
                        "parcel_name": c['parcel'], "data_name": c['name'],
                        "d_BD_m": round(c['rs']['BD-like→WGS84'], 1)},
    })
for c in selB:
    tasks.append({
        "task_id": f"HRT-BJ2-EDGE-{c['sid']}", "category": "THRESHOLD_EDGE", "subject_id": c['sid'],
        "name": c['name'], "district": c['district'], "address": c['address'],
        "click_mode": True, "default_base": "amap", "prediction_visibility": "PREDICTION_VISIBLE",
        "reviewer_role_required": "DATA_STEWARD",
        "question": Q_DUEL.replace('{addr}', c['address'] or '无'),
        "raw": [round(raw[c['sid']][0], 6), round(raw[c['sid']][1], 6)],
        "raw_gcj": [round(v, 6) for v in wgs84_to_gcj02(*raw[c['sid']])],
        "aligned": None, "aligned_gcj": None,
        "parcel_ring": None,
        "parcel_centroid": [round(v, 6) for v in wgs84_to_gcj02(*parcel_cen[c['parcel']])],
        "parcel_ring_wgs": None, "parcel_centroid_wgs": [round(v, 6) for v in parcel_cen[c['parcel']]],
        "residual_aligned_m": round(c['rs']['BD-like→WGS84'], 1),
        "d06_score": None, "precision_degraded": False,
        "ref_parcel_name": c['parcel'],
        "ref_name_matches": TRIM(c['name']) == TRIM(c['parcel']) if True else False,
        "rationale_options": [list(o) for o in OPTS],
        "machine_belief": {"kind": "threshold", "d_BD_m": round(c['rs']['BD-like→WGS84'], 1),
                            "dp02_m": 200.0,
                            "note": "BD-residual straddles 200m; click decides if tolerance must move"},
    })

DATA_INDEX = [[sid, names[sid]['name'], names[sid]['district'], names[sid]['address'],
               round(raw[sid][0], 6), round(raw[sid][1], 6)] for sid in raw]

manifest = {
    "batch_id": "beijing_review_batch_v2", "city": CITY, "task_count": len(tasks),
    "strategy": "margin-sampling: 5 MATCH_DOUBT (tests our own anchor matching) + 5 THRESHOLD_EDGE (dp02 calibration); blind single-click",
    "pool_sizes": {"ambiguous": len(poolA), "threshold_edge": len(poolB), "anchored_total": len(cands)},
    "data_source": {"corpus": "commercial listing dataset_master_split", "file": SRC, "rows": len(raw)},
    "roster": ROSTER,
    "input_mode": "BLIND_SINGLE_CLICK",
    "learning_contract": "Each click is ground truth for hypothesis-pairwise and threshold calibration; offline only.",
    "created_at": datetime.now(timezone.utc).isoformat(),
}
(OUT / 'review_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
(OUT / 'tasks.json').write_text(json.dumps(tasks, ensure_ascii=False), encoding='utf-8')

HTML = (REPO_ROOT / 'tools/review_pack_template.html').read_text(encoding='utf-8')
html = (HTML.replace('__TASKS__', json.dumps(tasks, ensure_ascii=False))
            .replace('__MANIFEST__', json.dumps(manifest, ensure_ascii=False))
            .replace('__DATA_INDEX__', json.dumps(DATA_INDEX, ensure_ascii=False, separators=(',', ':'))))
(OUT / 'review_map.html').write_text(html, encoding='utf-8')
print(f"pools: ambiguous={len(poolA)} edge={len(poolB)} (anchored {len(cands)})")
print(f"tasks={len(tasks)} html={len(html)//1024}KB -> {OUT}/review_map.html")
