"""Generate Beijing Review Batch (10 tasks, click-to-locate v3.1).

Boss directive 2026-09-05: switch to 北京 data from the hash-pinned master split
(Seed Corpus #2), and shrink to ~10 high-value tasks (label-budget respect).

Pipeline (all computed):
1. Load 北京.csv (16,040 rows).
2. Name-exact-match anchors against OSM R parcels (name is the discriminative key).
3. Encoding hypothesis test (identity / GCJ-like / BD-like) with block-wise FIT/HOLDOUT.
4. Pick 10: 5 blocked, 2 near-truth blind controls, 2 far anomalies, 1 low-precision.
5. Emit manifest + tasks + review_map.html (shared v3.1 template, search over 北京 index).
"""
import csv, json, math, random, re, sys
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
OUT = DATA_ROOT / 'runs/beijing_seed_001/review_batch_v1'
OUT.mkdir(parents=True, exist_ok=True)
SRC = DATA_ROOT / f'corpus/commercial listing dataset/cities/{CITY}.csv'
PARCELS = REF_ROOT / 'beijing_gb50137_all.geojson'

ROSTER = load_review_roster(DATA_ROOT / 'runs/beijing_seed_001')

RATIONALE_OPTIONS = {
    "DECISION_BLOCKED": [
        ("POINT_AT_RAW", "蓝点（数据原值）就是真实位置 → 数据本来就是对的"),
        ("POINT_AT_CONVERTED", "绿点（系统换算后）就是真实位置 → 换算后可用"),
        ("POINT_AT_REF", "红点（参考地块中心）最接近真实位置 → 两个数据点都偏了"),
        ("REF_NOT_RESIDENTIAL", "橙框所在处实际不是住宅用地（农田/果园/厂房等）→ 源头定义或参考有误"),
        ("CLICK_DERIVED", "三个点都不对，我在地图上点出真实位置"),
        ("REF_DOUBT", "橙框参考地块本身画错了位置"),
        ("CANNOT_LOCATE", "在地图上找不到这个小区，无法指认"),
    ],
    "EXTREME_ANOMALY": [
        ("POINT_AT_RAW", "蓝点就在真实位置 → 确实是合法偏远小区"),
        ("CLICK_DERIVED", "蓝点不在真实位置，我点出它真正在哪"),
        ("REF_NOT_RESIDENTIAL", "蓝点落在农田/果园/厂房等非住宅区 → 数据本身的类目或坐标就是错的"),
        ("CANNOT_LOCATE", "在地图上找不到这个小区，无法指认"),
    ],
    "BLIND_CONTROL": [
        ("POINT_AT_RAW", "蓝点就在真实位置 → 位置正确"),
        ("CLICK_DERIVED", "蓝点不在真实位置，我点出它真正在哪"),
        ("CANNOT_LOCATE", "在地图上找不到这个小区，无法指认"),
    ],
    "PRECISION_DEGRADATION": [
        ("PRECISION_SUFFICIENT", "够用：误差对这个用途影响不大"),
        ("PRECISION_INSUFFICIENT", "不够用：误差大到没法排线/选址，需重新采集"),
        ("SOURCE_TRUNCATION", "看着就是导出时被截断的（维持阻断，记录来源问题）"),
    ],
}

TRIM = re.compile(r"[（(].*?[)）]|\s|[-—·]")
def norm(s): return TRIM.sub('', s or '')

# ── 1. Load data ───────────────────────────────────────────────
raw, names = {}, {}
decimals = {}
with open(SRC, encoding='utf-8-sig', newline='') as f:
    for row in csv.DictReader(f):
        sid = str(row['小区ID'])
        try:
            raw[sid] = (float(row['经度']), float(row['纬度']))
        except Exception:
            continue
        names[sid] = {'name': row['小区名'], 'district': row['城区'], 'address': row['地址']}
        lon = row['经度']
        decimals[sid] = len(lon.split('.')[1]) if '.' in lon else 0
print(f"{CITY} records: {len(raw)}")

gj = json.load(open(PARCELS))
parcel_cen, parcel_ring = {}, {}
for feat in gj['features']:
    p = feat['properties']
    if p.get('gb_code') == 'R' and p.get('name') and p['name'] not in parcel_cen:
        g = sg.shape(feat['geometry'])
        parcel_cen[p['name']] = (g.centroid.x, g.centroid.y)
        poly = max(g.geoms, key=lambda x: x.area) if g.geom_type == 'MultiPolygon' else g
        parcel_ring[p['name']] = [[round(x, 6), round(y, 6)] for x, y in list(poly.exterior.coords)[:150]]
print(f"named R parcels: {len(parcel_cen)}")

# ── 2. Name anchors ────────────────────────────────────────────
pcen_by_norm = {}
for pn in parcel_cen:
    pcen_by_norm.setdefault(norm(pn), pn)
cands = []
for sid, nm in names.items():
    if sid not in raw: continue
    pn = pcen_by_norm.get(norm(nm['name']))
    if pn:
        cands.append({"sid": sid, "parcel": pn, "name": nm['name'],
                      "district": nm['district'], "address": nm['address']})
print(f"name-anchored candidates: {len(cands)}")

# ── 3. Hypothesis test with block-wise split ───────────────────
geod = pyproj.Geod(ellps="WGS84")
def blk(sid):
    x, y = raw[sid]; return f"{round(x,2)}_{round(y,2)}"
by_block = {}
for c in cands:
    by_block.setdefault(blk(c['sid']), []).append(c)
rng = random.Random(20260905)
fit, hold = [], []
for b, grp in by_block.items():
    g2 = grp[:]
    rng.shuffle(g2)
    half = max(1, len(g2)//2)
    fit.extend(g2[:half]); hold.extend(g2[half:])
HYP = {"identity": lambda x, y: (x, y), "GCJ-like→WGS84": gcj02_to_wgs84, "BD-like→WGS84": bd09_to_wgs84}
def resid(c, hname):
    px, py = parcel_cen[c['parcel']]
    tx, ty = HYP[hname](*raw[c['sid']])
    _, _, d = geod.inv(tx, ty, px, py)
    return d
def p50(vals):
    vs = sorted(vals); return vs[len(vs)//2] if vs else None
scores = {h: p50([resid(c, h) for c in hold]) for h in HYP}
print("holdout P50(m) by hypothesis:", {k: round(v) if v else None for k, v in scores.items()})
best_h = min((v, k) for k, v in scores.items() if v is not None)[1]
print(f"best encoding hypothesis for {CITY}: {best_h}")

# ── 4. Pick 10 tasks ───────────────────────────────────────────
cand_by_sid = {c['sid']: c for c in cands}
def resid_sid(sid, h):
    c = cand_by_sid.get(sid)
    return round(resid(c, h), 1) if c else None

blocked = [c for c in cands if 200 < (resid(c, best_h) or 0) < 3000]
near = [c for c in cands if (resid(c, best_h) if resid(c, best_h) is not None else 9e9) < 80]
prec_sids = [s for s in raw if decimals.get(s, 9) <= 3][:5]
xs = sorted(v[0] for v in raw.values()); ys = sorted(v[1] for v in raw.values())
medx, medy = xs[len(xs)//2], ys[len(ys)//2]
anom = sorted(cands, key=lambda c: -math.hypot(raw[c['sid']][0]-medx, raw[c['sid']][1]-medy))[:60]

sel = []
sel += [(c, 'DECISION_BLOCKED', True, 'PREDICTION_VISIBLE') for c in rng.sample(blocked, min(5, len(blocked)))]
sel += [(c, 'BLIND_CONTROL', True, 'PREDICTION_HIDDEN') for c in rng.sample(near, min(2, len(near)))]
sel += [(c, 'EXTREME_ANOMALY', True, 'PREDICTION_HIDDEN') for c in rng.sample(anom, min(2, len(anom)))]
for s in prec_sids[:1]:
    nm = names[s]
    sel.append(({"sid": s, "name": nm['name'], "district": nm['district'], "address": nm['address'], "parcel": None},
                'PRECISION_DEGRADATION', False, 'PREDICTION_VISIBLE'))
tasks = []
for c, cat, click, vis in sel:
    sid = c['sid']
    al = HYP[best_h](*raw[sid]) if best_h != 'identity' else raw[sid]
    ring = parcel_ring.get(c['parcel']) if cat != 'BLIND_CONTROL' else None
    cen = parcel_cen.get(c['parcel']) if cat != 'BLIND_CONTROL' else None
    t = {
        "task_id": f"HRT-BJ-{cat[:4]}-{sid}", "category": cat, "subject_id": sid,
        "name": c.get('name'), "district": c.get('district'), "address": c.get('address'),
        "click_mode": click, "default_base": "amap" if click else None,
        "prediction_visibility": vis,
        "reviewer_role_required": {"DECISION_BLOCKED": "DATA_STEWARD", "EXTREME_ANOMALY": "REVIEWER",
                                     "BLIND_CONTROL": "REVIEWER", "PRECISION_DEGRADATION": "DOMAIN_EXPERT"}[cat],
        "question": {
            'DECISION_BLOCKED': f"【怎么做】地图是高德路网（有中文地名）。按【小区名】（不是地址）找到它的真实楼群：{c.get('name')}，门牌参考：{c.get('address') or '无'}。\n三选一：蓝点=数据原值 / 绿点=系统换算后（假设：{best_h}）/ 红点=参考地块中心。哪个是真实位置？都不对才点地图。",
            'EXTREME_ANOMALY': "【怎么做】这个小区离城区较远。按名称在图上找到它：蓝点在不在真实楼群上？不在就点地图。",
            'BLIND_CONTROL': "（盲审对照）按名称找到该小区真实位置，判断蓝点是否就在其上。不展示参考与换算。",
            'PRECISION_DEGRADATION': "数据里该点小数位很少（网格误差可达公里级）。对选址/排线用途来说够用吗？",
        }[cat],
        "raw": [round(raw[sid][0], 6), round(raw[sid][1], 6)],
        "raw_gcj": [round(v, 6) for v in wgs84_to_gcj02(*raw[sid])] if click else None,
        "aligned": None if (cat == 'BLIND_CONTROL' or not click) else [round(al[0], 6), round(al[1], 6)],
        "aligned_gcj": None if (cat == 'BLIND_CONTROL' or not click) else [round(al[0]+0.006, 6), round(al[1]+0.0024, 6)],
        "parcel_ring": ring, "parcel_centroid": [round(cen[0], 6), round(cen[1], 6)] if cen else None,
        "parcel_ring_wgs": None, "parcel_centroid_wgs": None,
        "residual_aligned_m": resid_sid(sid, best_h),
        "d06_score": None, "precision_degraded": cat == 'PRECISION_DEGRADATION',
        "ref_parcel_name": c.get('parcel') if cat != 'BLIND_CONTROL' else None,
        "ref_name_matches": True,
        "landuse_at_data_point": None,  # filled below
        "rationale_options": [list(o) for o in RATIONALE_OPTIONS[cat]],
    }
    tasks.append(t)

# land-use cross-check: what is OSM actually at/near the DATA point (boss's 样本小区 finding)
POLYGONS = []
for feat in gj['features']:
    p_ = feat['properties']
    try:
        g_ = sg.shape(feat['geometry'])
        if g_.is_valid and not g_.is_empty:
            POLYGONS.append((g_, p_.get('gb_code'), p_.get('osm_fclass'), p_.get('name', '')))
    except Exception:
        pass
from shapely.geometry import Point as Pt
def landuse_at(sid):
    pt = Pt(*raw[sid])
    hits = []
    for g_, code, fc, nm in POLYGONS:
        try:
            if g_.contains(pt):
                hits.append((code, fc, nm))
                if len(hits) >= 3: break
        except Exception:
            continue
    return hits
for t in tasks:
    lu = landuse_at(t['subject_id'])
    code = lu[0][0] if lu else '?'
    t['landuse_at_data_point'] = [{'gb': c, 'fclass': f, 'name': n} for c, f, n in lu] or \
        [{'gb': '无', 'fclass': 'OSM此处无地块覆盖', 'name': ''}]
    if t['click_mode'] and (code != 'R') and not any(c == 'REF_NOT_RESIDENTIAL' for c, _ in t['rationale_options']):
        t['rationale_options'].insert(3, ('REF_NOT_RESIDENTIAL',
            '蓝点/橙框所在处实际不是住宅用地（农田/果园/厂房等）→ 源头类目定义或坐标本身有误'))
    if code != 'R':
        print(f"  ⚠ 用地存疑: {t['subject_id']} {t['name']} → 数据点处 OSM 覆盖 = {code if lu else '无'}")

# correct GCJ display-frame overlays for Amap basemap
def g_(pt): return [round(pt[0], 6), round(pt[1], 6)]
for t in tasks:
    if t.get('parcel_centroid'):
        t['parcel_centroid'] = g_(wgs84_to_gcj02(*t['parcel_centroid']))
    if t.get('parcel_ring'):
        t['parcel_ring'] = [list(wgs84_to_gcj02(x, y)) for x, y in t['parcel_ring']]

# machine belief per task: which hypothesis wins NOW, margin to runner-up, residual class
for t in tasks:
    sid = t['subject_id']
    c = cand_by_sid.get(sid)
    if c is not None:
        rs = {h: resid(c, h) for h in HYP}
        rank = sorted((v, h) for h, v in rs.items() if v is not None)
        t['machine_belief'] = {
            "top_hypothesis": rank[0][1], "top_p50_m": round(rank[0][0], 1),
            "runner_up": rank[1][1] if len(rank) > 1 else None,
            "margin_ratio": round((rank[1][0] / rank[0][0]) if len(rank) > 1 and rank[0][0] else 9.99, 2),
            "record_residual_m": round(rs.get(best_h) or 0, 1),
            "machine_prediction": ("BLOCK(dp02>200m)" if (rs.get(best_h) or 0) > 200 else "ALLOW(dp02<=200m)"),
            "uncertainty_note": "margin<1.5x ⇒ label is high-information (active learning)"}
    else:
        t['machine_belief'] = {"top_hypothesis": None, "machine_prediction": "N/A(precision class)",
                                "uncertainty_note": "labels calibrate precision policy"}

DATA_INDEX = [[sid, names[sid]['name'], names[sid]['district'], names[sid]['address'],
               round(raw[sid][0], 6), round(raw[sid][1], 6)] for sid in raw]

manifest = {
    "batch_id": "beijing_review_batch_v1", "city": CITY, "task_count": len(tasks),
    "data_source": {"corpus": "commercial listing dataset_master_split (Seed Corpus #2)", "file": SRC, "rows": len(raw)},
    "anchor_evidence": {"name_matched_candidates": len(cands),
                         "fit": len(fit), "holdout": len(hold),
                         "holdout_p50_m": {k: round(v, 1) if v else None for k, v in scores.items()},
                         "best_encoding_hypothesis": best_h,
                         "caveat": "dataset-level weak evidence; each record still needs human pick/click"},
    "roster": ROSTER,
    "input_mode": "PICK_ONE_OF_THREE_OR_CLICK + OPTION_ONLY_NO_FREE_TEXT",
    "search_hint": "search by 小区名 (name is the discriminative key; addresses often disagree)",
    "learning_contract": "Each human label updates machine confidence: hypothesis posterior (identity/GCJ/BD), dp02 threshold calibration, and FP/FN rate of current policy. ~10 uncertainty-sampled labels per batch are treated as active-learning signal for RULE/hypothesis confidence — NOT as RL training data (no online updates; SSI Phase 2 governance).",
    "created_at": datetime.now(timezone.utc).isoformat(),
}
(OUT / 'review_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
(OUT / 'tasks.json').write_text(json.dumps(tasks, ensure_ascii=False), encoding='utf-8')

HTML = (REPO_ROOT / 'tools/review_pack_template.html').read_text(encoding='utf-8')
html = (HTML.replace('__TASKS__', json.dumps(tasks, ensure_ascii=False))
            .replace('__MANIFEST__', json.dumps(manifest, ensure_ascii=False))
            .replace('__DATA_INDEX__', json.dumps(DATA_INDEX, ensure_ascii=False, separators=(',', ':'))))
(OUT / 'review_map.html').write_text(html, encoding='utf-8')

pq.write_table(pa.Table.from_pylist(
    [{"sid": c["sid"], "name": c["name"], "district": c["district"], "parcel": c["parcel"],
      "resid_identity_m": round(resid(c, "identity"), 1),
      "resid_gcj_m": round(resid(c, "GCJ-like→WGS84"), 1),
      "resid_bd_m": round(resid(c, "BD-like→WGS84"), 1),
      "split": "FIT" if c in fit else "HOLDOUT", "block": blk(c["sid"])} for c in cands]),
    str(OUT / 'candidate_anchors.parquet'))
print(f"tasks={len(tasks)} html={len(html)//1024}KB -> {OUT}/review_map.html")
