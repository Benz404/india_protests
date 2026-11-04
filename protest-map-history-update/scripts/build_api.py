#!/usr/bin/env python3
"""Build the static JSON API (and the map page) into an output folder.

    python scripts/build_api.py --out site

Everything is plain files, so it can be hosted on GitHub Pages, Netlify or any static host.
"""
import argparse, json, pathlib, shutil, datetime, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
GROUPS = ["ruling", "opposition", "students", "workers", "farmers", "environment", "civil"]

def months_between(a, b):
    y, m = int(a[:4]), int(a[5:])
    ey, em = int(b[:4]), int(b[5:])
    while (y, m) <= (ey, em):
        yield f"{y}-{m:02d}"
        m += 1
        if m == 13: y, m = y + 1, 1

def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="site")
    out = ROOT / ap.parse_args().out
    if out.exists(): shutil.rmtree(out)
    sys.path.insert(0, str(ROOT / "scripts"))
    from validate import load_all
    recs = sorted(load_all(), key=lambda r: (r["start"], r["id"]), reverse=True)
    api = out / "api" / "v1"
    by_month, by_year, by_group = {}, {}, {g: [] for g in GROUPS}
    for r in recs:
        for y in range(int(r["start"][:4]), int(r["end"][:4]) + 1):
            by_year.setdefault(str(y), []).append(r)
        if len(r["start"]) == 7 and len(r["end"]) == 7:  # month files only for month-precise records
            for m in months_between(r["start"], r["end"]):
                by_month.setdefault(m, []).append(r)
        for g in r["groups"]: by_group[g].append(r)
        write(api / "records" / f"{r['id']}.json", r)
    meta = {"generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "count": len(recs), "counts_by_group": {g: len(v) for g, v in by_group.items()},
            "intensity_scale": {"1": "Peaceful", "2": "Minor friction (detentions, scuffles)",
                                "3": "Heavy policing or disruption", "4": "Force or injuries",
                                "5": "Serious violence"}}
    write(api / "protests.json", {"meta": meta, "records": recs})
    for y, v in by_year.items(): write(api / "years" / f"{y}.json", {"year": y, "count": len(v), "records": v})
    for m, v in by_month.items(): write(api / "months" / f"{m}.json", {"month": m, "count": len(v), "records": v})
    for g, v in by_group.items(): write(api / "groups" / f"{g}.json", {"group": g, "count": len(v), "records": v})
    write(api / "index.json", {"meta": meta, "endpoints": {
        "all": "api/v1/protests.json", "year": "api/v1/years/{YYYY}.json",
        "month": "api/v1/months/{YYYY-MM}.json", "group": "api/v1/groups/{group}.json",
        "record": "api/v1/records/{id}.json"},
        "years": sorted(by_year), "months": sorted(by_month), "groups": GROUPS})
    for page in ("index.html", "add.html"):
        shutil.copy(ROOT / "web" / page, out / page)
    (out / "_headers").write_text("/api/*\n  Access-Control-Allow-Origin: *\n  Cache-Control: public, max-age=300\n")
    print(f"Built {len(recs)} records into {out}")

if __name__ == "__main__":
    main()
