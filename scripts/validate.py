#!/usr/bin/env python3
"""Validate the protest dataset against the published JSON Schema and editorial invariants."""
from __future__ import annotations

import json
import pathlib
import sys
from datetime import date

from jsonschema import Draft202012Validator, FormatChecker

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "protests.json"
SCHEMA_PATH = ROOT / "schema" / "protest.schema.json"
GROUPS = {"ruling", "opposition", "students", "workers", "farmers", "environment", "civil"}


def load_json(path: pathlib.Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read valid JSON from {path.relative_to(ROOT)}: {exc}") from exc


def validate_dataset(dataset=None, schema=None):
    """Return (errors, warnings); does not mutate the input dataset."""
    if dataset is None:
        dataset = load_json(DATA_PATH)
    if schema is None:
        schema = load_json(SCHEMA_PATH)

    errors = []
    warnings = []

    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        return [f"Invalid JSON Schema: {exc}"], warnings

    if not isinstance(dataset, dict) or not isinstance(dataset.get("records"), list):
        return ["Dataset must be an object containing a 'records' array."], warnings

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    seen_ids = set()

    for index, record in enumerate(dataset["records"]):
        if not isinstance(record, dict):
            errors.append(f"records[{index}]: record must be a JSON object")
            continue

        record_id = record.get("id", f"records[{index}]")
        for error in validator.iter_errors(record):
            location = ".".join(str(part) for part in error.absolute_path)
            field = f"{location}: " if location else ""
            errors.append(f"{record_id}: {field}{error.message}")

        if isinstance(record_id, str):
            if record_id in seen_ids:
                errors.append(f"{record_id}: duplicate id")
            seen_ids.add(record_id)

        # JSON Schema patterns validate the shape; these checks validate real calendar months.
        for field in ("start", "end"):
            value = record.get(field)
            if isinstance(value, str):
                try:
                    year, month = value.split("-", 1)
                    date(int(year), int(month), 1)
                except (ValueError, TypeError):
                    errors.append(f"{record_id}: '{field}' is not a real calendar month")

        start, end = record.get("start"), record.get("end")
        if isinstance(start, str) and isinstance(end, str) and end < start:
            errors.append(f"{record_id}: end is before start")

        location = record.get("location")
        if isinstance(location, dict):
            lat, lon = location.get("lat"), location.get("lon")
            # bool is a subclass of int in Python, but is not a valid coordinate.
            if isinstance(lat, bool) or isinstance(lon, bool):
                errors.append(f"{record_id}: coordinates must be numeric, not boolean")

        sources = record.get("sources", [])
        if isinstance(sources, list):
            if len(sources) < 2:
                warnings.append(f"{record_id}: only one source; add a second where possible")
        if not record.get("response"):
            warnings.append(f"{record_id}: no 'response' (other side's view) recorded")

    return errors, warnings


def main():
    try:
        dataset = load_json(DATA_PATH)
        schema = load_json(SCHEMA_PATH)
        errors, warnings = validate_dataset(dataset, schema)
    except ValueError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1

    for warning in warnings:
        print("WARN ", warning)
    for error in errors:
        print("ERROR", error)

    count = len(dataset.get("records", [])) if isinstance(dataset, dict) else 0
    print(f"{count} records, {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
