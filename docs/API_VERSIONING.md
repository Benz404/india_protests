# API versioning policy

## Version dimensions

This project tracks three separate identifiers:

- **API version** describes endpoint paths, response envelopes and field semantics.
- **Schema version** describes the structure and constraints of an individual protest record.
- **Dataset revision** identifies the exact source dataset used to generate a build.

The current API and schema versions are both `1.0.0`. Dataset revision is calculated as
`sha256:<hex-digest>` over the exact UTF-8 bytes of `data/protests.json`.

## Compatibility rules for v1

1. Existing endpoint paths and established response fields remain available.
2. New optional response fields may be added.
3. Clients should ignore unknown fields and should not assume object key order.
4. Existing fields must not silently change meaning, type or units.
5. Removing or renaming a field, changing its meaning, or changing an established response
   envelope requires a new major API version (for example `/api/v2/`).
6. A schema change that remains backward-compatible may increment the schema minor or patch
   version; a breaking record change requires a new schema major version and an explicit migration.
7. Dataset corrections do not, by themselves, require an API version change. They produce a new
   dataset revision.

## Metadata

The `meta` object on the all-records endpoint and API index exposes:

- `generated`: retained legacy UTC build timestamp.
- `generated_at`: explicit UTC build timestamp.
- `api_version`: API contract version.
- `schema_version`: record schema version.
- `dataset_revision`: SHA-256 source dataset fingerprint.
- `count`, `counts_by_group`, `intensity_scale`: dataset metadata.

## Deprecation

Do not remove a v1 endpoint or field without first documenting the replacement, announcing a
deprecation period, and publishing a migration guide. Because this is a static public dataset,
old immutable dataset snapshots should be retained when a release archive is introduced.
