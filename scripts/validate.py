#!/usr/bin/env python3
"""Validate data/protests.json. Exit code 1 on errors; warnings never fail the build."""
import json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
GROUPS = {"ruling", "opposition", "students", "workers", "farmers", "environment", "civil"}
STATUSES = {"planned", "ongoing", "ended", "unknown"}
REQUIRED = ["id", "title", "start", "end", "date_label", "scope", "location", "intensity",
            "status", "groups", "topics", "summary", "background", "status_text", "sources", "last_verified"]
MONTH = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def main():
    data = json.loads((ROOT / "data" / "protests.json").read_text(encoding="utf-8"))
    errors, warnings, seen = [], [], set()
    for i, r in enumerate(data["records"]):
        tag = r.get("id", f"#{i}")
        for k in REQUIRED:
            if k not in r or r[k] in ("", None, []):
                errors.append(f"{tag}: missing '{k}'")
        if r.get("id") in seen: errors.append(f"{tag}: duplicate id")
        seen.add(r.get("id"))
        if not MONTH.match(str(r.get("start", ""))): errors.append(f"{tag}: start must be YYYY-MM")
        if not MONTH.match(str(r.get("end", ""))): errors.append(f"{tag}: end must be YYYY-MM")
        elif r.get("start") and r["end"] < r["start"]: errors.append(f"{tag}: end is before start")
        if not DAY.match(str(r.get("last_verified", ""))): errors.append(f"{tag}: last_verified must be YYYY-MM-DD")
        if r.get("intensity") not in (1, 2, 3, 4, 5): errors.append(f"{tag}: intensity must be 1-5")
        if r.get("status") not in STATUSES: errors.append(f"{tag}: status must be one of {sorted(STATUSES)}")
        if r.get("scope") not in ("local", "national"): errors.append(f"{tag}: scope must be local or national")
        bad = set(r.get("groups", [])) - GROUPS
        if bad: errors.append(f"{tag}: unknown groups {sorted(bad)}")
        loc = r.get("location", {})
        if not (6 <= loc.get("lat", 0) <= 38 and 68 <= loc.get("lon", 0) <= 98):
            errors.append(f"{tag}: location is outside India's bounding box")
        for s in r.get("sources", []):
            if not str(s.get("url", "")).startswith("https://") or not s.get("title"):
                errors.append(f"{tag}: each source needs a title and an https URL")
        # Editorial warnings (do not fail)
        if not r.get("response"):
            warnings.append(f"{tag}: no 'response' (other side's view) recorded")
        if len(r.get("sources", [])) < 2:
            warnings.append(f"{tag}: only one source; add a second where possible")
    for w in warnings: print("WARN ", w)
    for e in errors: print("ERROR", e)
    print(f"{len(data['records'])} records, {len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
