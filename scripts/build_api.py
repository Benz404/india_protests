#!/usr/bin/env python3
"""Build the versioned static JSON API and map into an output directory.

The source dataset remains the single source of truth. Existing v1 endpoint paths
and response fields are retained; metadata additions are backward-compatible.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
GROUPS = ["ruling", "opposition", "students", "workers", "farmers", "environment", "civil"]
API_VERSION = "1.0.0"
SCHEMA_VERSION = "1.0.0"
PROTECTED_ROOT_DIRS = {".git", ".github", "data", "schema", "scripts", "tests", "web"}


def months_between(start, end):
    year, month = map(int, start.split("-"))
    end_year, end_month = map(int, end.split("-"))
    while (year, month) <= (end_year, end_month):
        yield f"{year}-{month:02d}"
        month += 1
        if month == 13:
            year, month = year + 1, 1


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def resolve_output(raw_path):
    out = pathlib.Path(raw_path).expanduser()
    if not out.is_absolute():
        out = ROOT / out
    out = out.resolve()

    if out == ROOT:
        raise ValueError("Refusing to use the repository root as the build output.")
    if out.is_symlink():
        raise ValueError("Refusing to replace a symlink build output.")
    if ROOT in out.parents:
        relative = out.relative_to(ROOT)
        if relative.parts and relative.parts[0] in PROTECTED_ROOT_DIRS:
            raise ValueError(f"Refusing to overwrite protected repository path: {relative}")
    return out


def build(output_dir):
    # Validate before creating or replacing any build output.
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate.py")],
        cwd=ROOT,
        check=True,
    )

    source_path = ROOT / "data" / "protests.json"
    source_bytes = source_path.read_bytes()
    dataset = json.loads(source_bytes.decode("utf-8"))
    records = sorted(
        dataset["records"],
        key=lambda record: (record["start"], record["id"]),
        reverse=True,
    )

    revision = "sha256:" + hashlib.sha256(source_bytes).hexdigest()
    generated = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    by_month = {}
    by_year = {}
    by_group = {group: [] for group in GROUPS}

    for record in records:
        for month in months_between(record["start"], record["end"]):
            by_month.setdefault(month, []).append(record)
            year_records = by_year.setdefault(month[:4], [])
            if record not in year_records:
                year_records.append(record)
        for group in record["groups"]:
            by_group[group].append(record)

    meta = {
        "generated": generated,
        "generated_at": generated,
        "api_version": API_VERSION,
        "schema_version": SCHEMA_VERSION,
        "dataset_revision": revision,
        "count": len(records),
        "counts_by_group": {group: len(items) for group, items in by_group.items()},
        "intensity_scale": {
            "1": "Peaceful",
            "2": "Minor friction (detentions, scuffles)",
            "3": "Heavy policing or disruption",
            "4": "Force or injuries",
            "5": "Serious violence",
        },
    }

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = pathlib.Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.staging-", dir=output_dir.parent))
    backup = None

    try:
        api = staging / "api" / "v1"
        for record in records:
            write_json(api / "records" / f"{record['id']}.json", record)

        write_json(api / "protests.json", {"meta": meta, "records": records})

        for year, items in sorted(by_year.items()):
            write_json(api / "years" / f"{year}.json", {
                "year": year, "count": len(items), "records": items
            })
        for month, items in sorted(by_month.items()):
            write_json(api / "months" / f"{month}.json", {
                "month": month, "count": len(items), "records": items
            })
        for group, items in by_group.items():
            write_json(api / "groups" / f"{group}.json", {
                "group": group, "count": len(items), "records": items
            })

        write_json(api / "index.json", {
            "meta": meta,
            "api_version": API_VERSION,
            "schema_version": SCHEMA_VERSION,
            "endpoints": {
                "all": "api/v1/protests.json",
                "year": "api/v1/years/{YYYY}.json",
                "month": "api/v1/months/{YYYY-MM}.json",
                "group": "api/v1/groups/{group}.json",
                "record": "api/v1/records/{id}.json",
            },
            "years": sorted(by_year),
            "months": sorted(by_month),
            "groups": GROUPS,
        })

        shutil.copy2(ROOT / "web" / "index.html", staging / "index.html")
        (staging / "_headers").write_text(
            "/api/*\n"
            "  Access-Control-Allow-Origin: *\n"
            "  Access-Control-Allow-Methods: GET, HEAD, OPTIONS\n"
            "  Cache-Control: public, max-age=300\n"
            "  X-Content-Type-Options: nosniff\n",
            encoding="utf-8",
        )

        # Replace the previous output only after the complete staging build succeeds.
        if output_dir.exists():
            backup = output_dir.with_name(output_dir.name + ".previous")
            if backup.exists():
                shutil.rmtree(backup)
            output_dir.rename(backup)
        try:
            staging.rename(output_dir)
        except Exception:
            if backup and backup.exists() and not output_dir.exists():
                backup.rename(output_dir)
            raise
        if backup and backup.exists():
            shutil.rmtree(backup)

    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        raise

    print(f"Built {len(records)} records into {output_dir}")
    print(f"API version: {API_VERSION}; schema version: {SCHEMA_VERSION}")
    print(f"Dataset revision: {revision}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="site", help="Output directory (default: site)")
    args = parser.parse_args()

    try:
        output_dir = resolve_output(args.out)
        build(output_dir)
    except (OSError, ValueError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
