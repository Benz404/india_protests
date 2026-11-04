#!/usr/bin/env python3
"""Check that every source link in data/*.json still opens. Prints broken links; never edits data.

    python scripts/check_links.py
"""
import sys, urllib.request, urllib.error, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from validate import load_all

def ok(url):
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers={"User-Agent": "india-protest-map-link-check"})
            with urllib.request.urlopen(req, timeout=20) as r:
                if r.status < 400: return True
        except urllib.error.HTTPError as e:
            if e.code in (403, 429): return True   # site blocks bots; cannot tell
        except Exception:
            pass
    return False

bad = 0
seen = set()
for r in load_all():
    for s in r["sources"]:
        if s["url"] in seen: continue
        seen.add(s["url"])
        if not ok(s["url"]):
            bad += 1; print("BROKEN", r["id"], s["url"])
print(f"{len(seen)} links checked, {bad} broken")
