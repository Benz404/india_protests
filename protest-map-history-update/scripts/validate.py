#!/usr/bin/env python3
"""Validate data/protests.json. Exit code 1 on errors; warnings never fail the build."""
import json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
GROUPS = {"ruling", "opposition", "students", "workers", "farmers", "environment", "civil"}
STATUSES = {"planned", "ongoing", "ended", "unknown"}
REQUIRED = ["id", "title", "start", "end", "date_label", "scope", "location", "intensity",
            "status", "groups", "topics", "summary", "background", "status_text", "sources", "last_verified"]
MONTH = re.compile(r"^\d{4}(-(0[1-9]|1[0-2]))?$")
DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ID = re.compile(r"^[a-z0-9-]+$")

def strings(x):
    if isinstance(x, str): yield x
    elif isinstance(x, dict):
        for v in x.values(): yield from strings(v)
    elif isinstance(x, list):
        for v in x: yield from strings(v)

def load_all():
    """Records from every data/*.json file (protests.json = recent, historical.json = 1947 onward)."""
    out = []
    for f in sorted((ROOT / "data").glob("*.json")):
        out += json.loads(f.read_text(encoding="utf-8"))["records"]
    return out

def check(records):
    """Return (errors, warnings) for a list of records."""
    errors, warnings, seen = [], [], set()
    for i, r in enumerate(records):
        tag = r.get("id", f"#{i}")
        for k in REQUIRED:
            if k not in r or r[k] in ("", None, []):
                errors.append(f"{tag}: missing '{k}'")
        if r.get("id") in seen: errors.append(f"{tag}: duplicate id")
        seen.add(r.get("id"))
        if not ID.match(str(r.get("id", ""))): errors.append(f"{tag}: id may use only a-z, 0-9 and hyphens")
        if not MONTH.match(str(r.get("start", ""))): errors.append(f"{tag}: start must be YYYY or YYYY-MM")
        if not MONTH.match(str(r.get("end", ""))): errors.append(f"{tag}: end must be YYYY or YYYY-MM")
        elif r.get("start") and r["end"] < r["start"]: errors.append(f"{tag}: end is before start")
        for k in ("start", "end"):
            if MONTH.match(str(r.get(k, ""))) and not (1947 <= int(r[k][:4]) <= 2100):
                errors.append(f"{tag}: {k} year must be 1947 or later (this map covers independent India)")
        if not DAY.match(str(r.get("last_verified", ""))): errors.append(f"{tag}: last_verified must be YYYY-MM-DD")
        if r.get("intensity") not in (1, 2, 3, 4, 5): errors.append(f"{tag}: intensity must be 1-5")
        if r.get("status") not in STATUSES: errors.append(f"{tag}: status must be one of {sorted(STATUSES)}")
        if r.get("scope") not in ("local", "national"): errors.append(f"{tag}: scope must be local or national")
        bad = set(r.get("groups", [])) - GROUPS
        if bad: errors.append(f"{tag}: unknown groups {sorted(bad)}")
        loc = r.get("location", {})
        if not (isinstance(loc.get("lat"), (int, float)) and isinstance(loc.get("lon"), (int, float))
                and 6 <= loc["lat"] <= 38 and 68 <= loc["lon"] <= 98):
            errors.append(f"{tag}: location is missing or outside India's bounding box")
        for s in r.get("sources", []):
            if not str(s.get("url", "")).startswith("https://") or not s.get("title"):
                errors.append(f"{tag}: each source needs a title and an https URL")
        if any("<" in t or ">" in t for t in strings(r)):
            errors.append(f"{tag}: text must not contain < or >")
        if not r.get("response"): warnings.append(f"{tag}: no 'response' (other side's view) recorded")
        if r.get("needs_review"): warnings.append(f"{tag}: starter record, still needs a check against primary sources")
        if len(r.get("sources", [])) < 2: warnings.append(f"{tag}: only one source; add a second where possible")
    return errors, warnings

def main():
    records = load_all()
    errors, warnings = check(records)
    for w in warnings: print("WARN ", w)
    for e in errors: print("ERROR", e)
    print(f"{len(records)} records, {len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
