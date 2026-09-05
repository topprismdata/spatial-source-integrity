"""Generate Review Batch V2 (click-to-locate redesign).

Core interaction (boss feedback 2026-09-05, twice): reviewers must NOT interpret
colored points, coordinates, or CRS concepts. They only answer what they know:
"where is this community really?" -> click the map. The system measures distances,
derives the verdict, and the reviewer just confirms confidence and saves.

Constraints kept: page-only feedback, zero free text, roster identity, blind
controls, machine-readable rationale codes (now system-derived from observation).
"""
import csv, json, random, re, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(REPO_ROOT))

import pyarrow.parquet as pq
import shapely.geometry as sg
import pyproj
from ssi.config import DATA_ROOT, REF_ROOT, REPO_ROOT, load_review_roster
from ssi.resolver.transforms import bd09_to_wgs84, wgs84_to_gcj02

OUT = DATA_ROOT / 'runs/xian_seed_001/review_batch_v2'
OUT.mkdir(parents=True, exist_ok=True)
XA_RAW = DATA_ROOT / 'corpus/commercial listing dataset/cities/西安.csv'

ROSTER = load_review_roster(DATA_ROOT / 'runs/xian_seed_001')

# Rationale codes remain 2-tuples (code,label); in click-mode tasks verdict is
# DERIVED by the system from the reviewer's click + measured distances.
RATIONALE_OPTIONS = {
    "DECISION_BLOCKED": [
        ("POINT_AT_RAW", "蓝点（数据原值）就是真实位置 → 数据本来就是对的"),
        ("POINT_AT_CONVERTED", "绿点（系统换算后）就是真实位置 → 换算后可用"),
        ("POINT_AT_REF", "红点（参考地块中心）最接近真实位置 → 两个数据点都偏了"),
        ("CLICK_DERIVED", "三个点都不对，我在地图上点出真实位置"),
        ("REF_DOUBT", "橙框参考地块本身画错了位置"),
        ("CANNOT_LOCATE", "在地图上找不到这个小区，无法指认"),
    ],
    "EXTREME_ANOMALY": [
        ("POINT_AT_RAW", "蓝点就在真实位置 → 确实是合法偏远小区"),
        ("CLICK_DERIVED", "蓝点不在真实位置，我点出它真正在哪"),
        ("CANNOT_LOCATE", "在地图上找不到这个小区，无法指认"),
    ],
    "BLIND_CONTROL": [
        ("POINT_AT_RAW", "蓝点就在真实位置 → 位置正确"),
        ("CLICK_DERIVED", "蓝点不在真实位置，我点出它真正在哪"),
        ("CANNOT_LOCATE", "在地图上找不到这个小区，无法指认"),
    ],
    "PRECISION_DEGRADATION": [
        ("PRECISION_SUFFICIENT", "够用：2 位小数的误差对这个用途影响不大"),
        ("PRECISION_INSUFFICIENT", "不够用：误差大到没法排线/选址，需重新采集"),
        ("SOURCE_TRUNCATION", "看着就是导出时被截断的（维持阻断，记录来源问题）"),
    ],
    "INVESTIGATION_REQUIRED": [
        ("MASTER_MATCH_SUFFICIENT", "认可这条证据链 → file1 封存报废"),
        ("NEED_PRODUCER_INTERVIEW", "方向没错，但还需访谈生产方定案"),
        ("CONTRADICTING_INFO", "我掌握相反情况（例如 file1 仍在被某流程使用）"),
    ],
}

CLICK_Q = ("【怎么做】你知道这个小区在哪里，机器不知道——所以由你指认：\n"
           "① 地图是高德路网（有中文地名，可缩放拖动）。按门牌「{addr}」+周边地名，找到「{name}」实际的那片楼。\n"
           "② 直接选：蓝点（数据原值）、绿点（系统换算后）、红点（参考地块中心）——哪个就是它的真实位置？\n"
           "③ 三个都不对，才在地图上点一下它的真实位置。\n"
           "④ 系统自动给结论草稿，你确认置信度并保存。\n"
           "不用理解任何坐标系概念。")
CLICK_Q_BLIND = ("【怎么做】在高德路网图上找到「{name}」实际的那片楼（门牌：{addr}）。\n"
                 "② 选：蓝点在不在真实位置上？不在就点地图标出真实位置。\n"
                 "（此单不展示机器意见与换算结果）")

# ── 1. Load Seed Corpus #2 (master split, raw) ─────────────────
raw, names = {}, {}
with open(XA_RAW, encoding='utf-8-sig', newline='') as f:
    for row in csv.DictReader(f):
        sid = str(row['小区ID'])
        try:
            raw[sid] = (float(row['经度']), float(row['纬度']))
        except Exception:
            continue
        names[sid] = {'name': row['小区名'], 'district': row['城区'], 'address': row['地址']}
print(f"Seed Corpus #2 西安 rows: {len(raw)}")
aligned = {sid: bd09_to_wgs84(x, y) for sid, (x, y) in raw.items()}

anchors = pq.read_table(DATA_ROOT / 'runs/xian_seed_001/entity_matching/accepted_anchors.parquet').to_pylist()
anchor_by_sid = {}
for a in anchors:
    anchor_by_sid.setdefault(a['source_record_id'], a)

gj = json.load(open(REF_ROOT / 'xian_gb50137_all.geojson'))
parcel_cen, parcel_ring = {}, {}
for feat in gj['features']:
    p = feat['properties']
    if p.get('gb_code') == 'R' and p.get('name') and p['name'] not in parcel_cen:
        g = sg.shape(feat['geometry'])
        parcel_cen[p['name']] = (round(g.centroid.x, 6), round(g.centroid.y, 6))
        poly = max(g.geoms, key=lambda x: x.area) if g.geom_type == 'MultiPolygon' else g
        parcel_ring[p['name']] = [[round(x, 6), round(y, 6)] for x, y in list(poly.exterior.coords)[:150]]

d06, d03 = {}, set()
for line in open(DATA_ROOT / 'runs/xian_seed_001/intrinsic/findings.jsonl'):
    fd = json.loads(line)
    if fd.get('finding_code') == 'F-D06-INTRINSIC-OUTLIER':
        m = re.search(r'([\d.]+) MAD', fd.get('explanation', ''))
        d06[fd['target_id']] = float(m.group(1)) if m else None
    elif fd.get('finding_code') == 'F-D03-PRECISION-DEGRADATION':
        d03.add(fd['target_id'])

geod = pyproj.Geod(ellps="WGS84")
resid_aligned = {}
for sid, a in anchor_by_sid.items():
    cen = parcel_cen.get(a['reference_name'])
    if cen and sid in aligned:
        _, _, dist = geod.inv(aligned[sid][0], aligned[sid][1], cen[0], cen[1])
        resid_aligned[sid] = round(dist, 2)

# ── 2. Build tasks ─────────────────────────────────────────────
rng = random.Random(20260905)
tasks = []
queue = [json.loads(l) for l in open(DATA_ROOT / 'runs/xian_seed_001/review_queue/human_review_tasks.jsonl')]

def geo_fields(sid):
    a = anchor_by_sid.get(sid)
    rn = a['reference_name'] if a else ''
    ring = parcel_ring.get(rn)
    cen = parcel_cen.get(rn)
    al = aligned.get(sid)
    return {
        "raw": list(raw[sid]) if sid in raw else None,
        "aligned": list(al) if al else None,
        "aligned_gcj": list(wgs84_to_gcj02(al[0], al[1])) if al else None,
        "raw_gcj": list(wgs84_to_gcj02(*raw[sid])) if sid in raw else None,
        "parcel_ring": [list(wgs84_to_gcj02(x, y)) for x, y in ring] if ring else None,
        "parcel_centroid": list(wgs84_to_gcj02(cen[0], cen[1])) if cen else None,
        "parcel_ring_wgs": [list(p) for p in ring] if ring else None,
        "parcel_centroid_wgs": list(cen) if cen else None,
        "residual_aligned_m": resid_aligned.get(sid),
        "d06_score": d06.get(sid),
        "precision_degraded": sid in d03,
        "ref_parcel_name": rn,
        "ref_name_matches": (re.sub(r"[\s()（）\-—·]", '', rn) in re.sub(r"[\s()（）\-—·]", '', names.get(sid, {}).get('name', '')) or
                             re.sub(r"[\s()（）\-—·]", '', names.get(sid, {}).get('name', '')) in re.sub(r"[\s()（）\-—·]", '', rn)) if rn else False,
    }

for t in queue:
    cat = t['category']
    sid = str(t['subject'])
    if cat == 'INVESTIGATION_REQUIRED':
        tasks.append({"task_id": t['task_id'], "category": cat, "subject_id": "FILE1",
            "name": "file1 血统调查", "district": "—", "address": "—",
            "click_mode": False, "default_base": None,
            "raw": None, "aligned": None, "parcel_ring": None, "parcel_centroid": None,
            "residual_aligned_m": None, "d06_score": None, "precision_degraded": False,
            "facts": [
                "两个旧文件都来自commercial listing dataset 8 月西安数据：文件名标着 GCJ02（file1）和 WGS84（file2）——经核查两个标签都不可信。",
                "事实①：file2 与全国 47 万行主表中的西安部分逐字一致 → 它只是主表截取件。",
                "事实②：file1 比 file2 晚 3 分 35 秒生成，每一行恰好等于对 file2 再做一次坐标加偏（12,505/12,505）。",
                "事实③：file2 本身已是加偏坐标，再套一次 = 双重偏移，实测偏离真实位置约 1.5 公里。",
                "系统已拒绝发布 file1 的任何坐标；本裁决台数据源已切换为主表拆分文件。",
            ],
            "question": "请裁定：file1 是被重复加偏弄坏的文件，不应再投入使用。你同意吗？",
            "reviewer_role_required": "DATA_STEWARD", "prediction_visibility": "PREDICTION_VISIBLE"})
        continue
    nm = names.get(sid, {})
    disp = nm.get('name', '该小区') or '该小区'
    addr = nm.get('address', '') or ''
    click = cat in ('DECISION_BLOCKED', 'EXTREME_ANOMALY')
    role = {'DECISION_BLOCKED': 'DATA_STEWARD', 'PRECISION_DEGRADATION': 'DOMAIN_EXPERT',
            'EXTREME_ANOMALY': 'REVIEWER'}[cat]
    visibility = 'PREDICTION_HIDDEN' if cat == 'EXTREME_ANOMALY' else 'PREDICTION_VISIBLE'
    if cat == 'EXTREME_ANOMALY':
        question = CLICK_Q_BLIND.replace('{name}', disp).replace('{addr}', addr)
    elif cat == 'DECISION_BLOCKED':
        question = CLICK_Q.replace('{name}', disp).replace('{addr}', addr)
    else:
        question = "数据里这个点只保留了 2 位小数（误差范围约 ±1.1 公里）。对你的业务来说够用吗？直接选一种情况即可。"
    tasks.append({"task_id": t['task_id'], "category": cat, "subject_id": sid,
        "name": disp, "district": nm.get('district', ''), "address": addr,
        "click_mode": click, "default_base": "amap" if click else None,
        "question": question,
        "reviewer_role_required": role,
        "prediction_visibility": visibility, **geo_fields(sid)})

cand_ctrl = [s for s, r in resid_aligned.items()
             if r < 200 and s not in {x['subject_id'] for x in tasks}]
for sid in rng.sample(cand_ctrl, min(10, len(cand_ctrl))):
    nm = names.get(sid, {})
    disp = nm.get('name', '该小区') or '该小区'
    tasks.append({"task_id": f"HRT-CTRL-{sid}", "category": "BLIND_CONTROL", "subject_id": sid,
        "name": disp, "district": nm.get('district', ''), "address": nm.get('address', ''),
        "click_mode": True, "default_base": "amap",
        "question": CLICK_Q_BLIND.replace('{name}', disp).replace('{addr}', nm.get('address', '') or ''),
        "reviewer_role_required": "REVIEWER", "prediction_visibility": "PREDICTION_HIDDEN",
        **geo_fields(sid)})

for t in rng.sample([x for x in tasks if x['category'] == 'DECISION_BLOCKED'], 10):
    t['second_review_blind'] = True
for t in tasks:
    t['rationale_options'] = RATIONALE_OPTIONS[t['category']]

# ── 3. Manifest + tasks.json ───────────────────────────────────
manifest = {
    "batch_id": "review_batch_v2", "interaction": "CLICK_TO_LOCATE_V3",
    "data_source": {"corpus": "commercial listing dataset_master_split (Seed Corpus #2)",
                     "file": XA_RAW, "rows": len(raw)},
    "created_at": datetime.now(timezone.utc).isoformat(),
    "expected_task_count": len(tasks),
    "expected_task_ids": sorted(t['task_id'] for t in tasks),
    "expected_by_category": {c: sum(1 for t in tasks if t['category'] == c)
                              for c in sorted({t['category'] for t in tasks})},
    "click_mode_count": sum(1 for t in tasks if t.get('click_mode')),
    "blind_hidden_count": sum(1 for t in tasks if t['prediction_visibility'] == 'PREDICTION_HIDDEN'),
    "second_review_blind_dp02": sum(1 for t in tasks if t.get('second_review_blind')),
    "roster": ROSTER,
    "input_mode": "PICK_ONE_OF_THREE_OR_CLICK + OPTION_ONLY_NO_FREE_TEXT",
    "search": {"local_index": "all 西安 data records (jump aid, unverified)", "nominatim": "OSM geocode (same family as parcels)", "amap_web": "ditu.amap.com POI cross-check"},
    "verdict_options": "POINT_AT_RAW/POINT_AT_CONVERTED/POINT_AT_REF (pick) | CLICK_DERIVED (fallback)",
    "verdict_derivation": "system-computed from click vs data points (raw & assumed-transform); reviewer confirms confidence",
    "thresholds": {"dp02_tolerance_m": 200.0, "provenance": "EXPERIMENTAL_FIXTURE (not customer-approved)"},
    "reconciliation_rule": "88/88-or-declare-sampled-N/M; unknown reviewer id = reject; off-menu rationale code = reject",
}
(OUT / 'review_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
(OUT / 'tasks.json').write_text(json.dumps(tasks, ensure_ascii=False), encoding='utf-8')

DATA_INDEX = [[sid, names[sid]['name'], names[sid]['district'], names[sid]['address'],
               round(raw[sid][0], 6), round(raw[sid][1], 6)] for sid in raw]
HTML = (REPO_ROOT / 'tools/review_pack_template.html').read_text(encoding='utf-8')
html = HTML.replace('__TASKS__', json.dumps(tasks, ensure_ascii=False)) \
           .replace('__MANIFEST__', json.dumps(manifest, ensure_ascii=False)) \
           .replace('__DATA_INDEX__', json.dumps(DATA_INDEX, ensure_ascii=False, separators=(',', ':')))

(OUT / 'review_map.html').write_text(html, encoding='utf-8')
print(f"tasks={len(tasks)} click={manifest['click_mode_count']} "
      f"hidden_blind={manifest['blind_hidden_count']} html={len(html)//1024}KB")
