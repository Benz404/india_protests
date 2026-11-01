#!/usr/bin/env python3
"""Add a record submitted through the web form (an issue whose body holds a ```json block).

Reads ISSUE_BODY from the environment, validates it, appends it to data/protests.json and writes
result.md (a message for the issue). Never executes anything from the issue: it only parses JSON.
Exit code 1 means the record was rejected.
"""
import json, os, re, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from validate import check, ROOT

def fail(msg):
    pathlib.Path("result.md").write_text("Sorry, this record was not added.\n\n" + msg + "\n\nPlease fix it and submit again using the form.\n")
    print(msg); sys.exit(1)

body = os.environ.get("ISSUE_BODY", "")
m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", body, re.S) or re.search(r"(\{.*\})", body, re.S)
if not m: fail("I could not find a JSON record in the issue.")
try: rec = json.loads(m.group(1))
except Exception as e: fail(f"The JSON could not be read: {e}")
if not isinstance(rec, dict): fail("The record must be a JSON object.")

path = ROOT / "data" / "protests.json"
data = json.loads(path.read_text(encoding="utf-8"))
ids = {r["id"] for r in data["records"]}
base, n = str(rec.get("id", "")), 2
while rec.get("id") in ids:
    rec["id"] = f"{base}-{n}"; n += 1
errors, warnings = check(data["records"] + [rec])
errors = [e for e in errors if e.startswith(str(rec.get("id"))) or e.startswith("#")]
if errors: fail("\n".join("- " + e for e in errors))
data["records"].append(rec)
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
pathlib.Path("result.md").write_text("Record added in a pull request for review.\n" + "\n".join("- note: " + w for w in warnings if w.startswith(rec["id"])))
print("added", rec["id"])
