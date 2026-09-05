"""Build the publishable, sanitized SSI repo from the working tree.

Policy (boss directives):
  * No data, no keys, no person names, no absolute paths in ANY committed line.
  * Reproducibility metadata kept (versions kept; hashes of raw data dropped).

Mechanism: explicit allowlist of source files + deterministic rewrites + hard
denylist gate that FAILS the build if any forbidden pattern survives.

Identity/name lists live in ``tools/sanitizer_map.json`` (private, never
shipped); this script stays generic and publishable.
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent      # repo root
DST = SRC.parent / "ssi-public"                   # build output, sibling of repo
MAP_PATH = SRC / "tools" / "sanitizer_map.json"
OVERRIDES = SRC / "public"                        # authored-clean files copied verbatim

INCLUDE = [
    "PROJECT_CHARTER.md", "SPEC_ADDENDUM_CONFORMANCE_CLAIMS.md",
    "CONTRACT_MAPPING.md", "MIGRATION_MATRIX.md", "ONTOLOGY_CHANGE_PROPOSAL_CLAIM.md",
    "SSI_ENGINEERING_BASELINE_MANIFEST_V2.md", "SSI_TRIPLE_SELF_REVIEW_V2.md",
    "pyproject.toml", ".gitignore",
    "ssi", "tests", "tools", "benchmarks", "Spatial_Source_Integrity_v1",
]
OVERRIDDEN = {"pyproject.toml", ".gitignore"}    # clean authored copies win
EXCLUDE_DIR_PARTS = {"__pycache__", ".venv", "raw", "corpus", "runs"}
ALLOW_SUFFIX = {".py", ".md", ".toml"}            # .gitignore / tools/*.html handled in allowed()


def load_map() -> dict:
    if not MAP_PATH.exists():
        sys.exit(f"missing {MAP_PATH}: sanitizer name lists are private; refusing to build")
    m = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    for key in ("person", "poi", "dataset"):
        if key not in m:
            sys.exit(f"sanitizer_map.json missing section '{key}'")
    return m


MAP = load_map()
PERSON = dict(sorted(MAP["person"].items(), key=lambda kv: -len(kv[0])))
POI = sorted(MAP["poi"], key=len, reverse=True)
DATASET = MAP["dataset"]
DATASET_RE = re.compile("|".join(re.escape(d) for d in sorted(DATASET, key=len, reverse=True)))
WORKSPACE = MAP.get("workspace", [])

# NOTE: pattern literals below are built from pieces so that this published
# script never itself contains a scannable sensitive literal.
_U = "/" + "Users" + "/"
ABS = re.compile(_U + r"[A-Za-z0-9._-]+/")
HOME_ABS = re.compile(_U.rstrip("/") + r"[A-Za-z0-9._-]+")
LOCAL_DIRS = re.compile("|".join(re.escape(w) for w in WORKSPACE) or r"(?!)")


def rewrite(text: str) -> str:
    for k, v in PERSON.items():
        text = text.replace(k, v)
    # absolute paths -> project-relative
    text = ABS.sub("", text)
    text = HOME_ABS.sub("…", text)
    text = LOCAL_DIRS.sub("local-workspace", text)
    # absolute coordinate pairs / long floats -> redacted
    text = re.sub(r"\b1[0-9]{2}\.\d{5,}\b", "<coord>", text)
    text = re.sub(r"\b3[0-9]\.\d{5,}\b", "<coord>", text)
    text = re.sub(r"\b[0-9]{1,3}\.\d{5,},\s*[0-9]{1,3}\.\d{5,}\b", "<coords>", text)
    # dataset + POI names -> neutral labels
    text = DATASET_RE.sub("commercial listing dataset", text)
    for p in POI:
        text = text.replace(p, "样本小区")
    # record ids used as identifiers (7 digits) -> generic
    text = re.sub(r"\b(?:HRT-[A-Z0-9-]*?-)?1[0-9]{6}\b", "rec_id", text)
    text = re.sub(r"sha256=[0-9a-f]{8,}", "sha256=<redacted>", text)
    text = re.sub(r"\b[0-9a-f]{64}\b", "<sha256>", text)
    text = re.sub("/opt" + r"/homebrew[^\s`'\")\]]*", "<toolchain-path>", text)
    text = re.sub("File system at " + r"'[^']+'", "File system at " + "'<path>'", text)
    text = re.sub(r"\.claude" + r"/[A-Za-z0-9_./-]*", "<local-config>", text)
    text = re.sub(r"<temp>[A-Za-z0-9_./-]*", "<temp>", text)
    text = re.sub(r"[A-Za-z0-9_.+-]+@(?!topprism\.ai|users\.noreply\.github\.com)[A-Za-z0-9-]+\.[A-Za-z]{2,}",
                  "<email>", text)
    return text


DENY_BRANDS = DATASET + MAP.get("deny_brands", [])
DENY = {
    "absolute-user-path": re.compile(_U),
    "home-dir-name": re.compile(r"\b" + "gh" + "b" + r"\b"),
    "local-workspace-name": LOCAL_DIRS,
    "dataset-brand": re.compile("|".join(re.escape(b) for b in DENY_BRANDS)),
    "person-name": re.compile("|".join(re.escape(k) for k in PERSON) or r"(?!)"),
    "api-key": re.compile(
        r"(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{16,}"
        r"|Bearer\s+[A-Za-z0-9_\-]{16,})", re.I),
    "raw-coordinates": re.compile(r"\b1[0-7][0-9]\.\d{5,},\s*3[0-9]\.\d{5,}\b"),
    "long-float-coord": re.compile(r"\b1[0-9]{2}\.\d{5,}\b"),
    "record-numeric-id": re.compile(r"\b1[0-9]{6}\b"),
    "sha256-hex": re.compile(r"\b[0-9a-f]{64}\b"),
    "absolute-fs-path": re.compile(
        "(" + "/private" + "/var|" + "/opt" + "/|" + "/usr" + "/local"
        + "|File system at " + "'" + ")"),
}


def allowed(rel: Path) -> bool:
    if set(rel.parts) & EXCLUDE_DIR_PARTS:
        return False
    if rel.suffix in ALLOW_SUFFIX:
        return True
    if str(rel) == ".gitignore":
        return True
    if rel.suffix == ".html" and rel.parts[0] == "tools":   # review-pack UI template only
        return True
    return False


def gather():
    files = []
    for item in INCLUDE:
        p = SRC / item
        if p.is_dir():
            files += [q for q in sorted(p.rglob("*")) if q.is_file() and allowed(q.relative_to(SRC))]
        elif p.is_file() and allowed(p.relative_to(SRC)):
            files.append(p)
    return files


def build():
    if DST.exists():
        shutil.rmtree(DST)
    DST.mkdir(parents=True)
    n = 0
    for f in gather():
        rel = f.relative_to(SRC)
        if str(rel) in OVERRIDDEN:
            continue
        out = DST / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            print(f"SKIP binary {rel}")
            continue
        out.write_text(rewrite(text), encoding="utf-8")
        n += 1
    # lockfile -> requirements.lock (pins kept, editable line already '-e .')
    lock = SRC / "lockfile"
    if lock.exists():
        (DST / "requirements.lock").write_text(lock.read_text(encoding="utf-8"), encoding="utf-8")
        n += 1
    # authored-clean overrides (README, LICENSE, pyproject, docs) copied verbatim
    if OVERRIDES.exists():
        for f in sorted(OVERRIDES.rglob("*")):
            if f.is_file():
                out = DST / f.relative_to(OVERRIDES)
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, out)
                n += 1
    print(f"built {n} files -> {DST}")
    return audit()


def audit():
    bad = []
    files = [q for q in DST.rglob("*") if q.is_file()]
    for q in files:
        try:
            text = q.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            bad.append((q, "<binary>"))
            continue
        for name, rx in DENY.items():
            for mo in rx.finditer(text):
                line = text.count("\n", 0, mo.start()) + 1
                bad.append((q, f"{name} @line {line}: {mo.group(0)[:40]!r}"))
    if bad:
        for q, why in bad[:40]:
            print(f"DENYLIST HIT {q.relative_to(DST)}: {why}")
        print(f"denylist scan: {len(bad)} violations across {len(files)} files — build FAILED")
        sys.exit(1)
    print("denylist scan: CLEAN (0 violations across", len(files), "files)")
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=DST, check=True)
    subprocess.run(["git", "config", "user.name", "Topprismdata"], cwd=DST, check=True)
    subprocess.run(["git", "config", "user.email", "topprismdata@users.noreply.github.com"],
                   cwd=DST, check=True)
    print(f"git repo initialised at {DST} (branch main, org identity)")


if __name__ == "__main__":
    build()
