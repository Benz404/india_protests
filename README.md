# India Protest & Peace Map

An open, non-partisan, interactive map of protests across India, with a free static JSON API.
It records protests by **ruling parties, opposition parties, students, workers, farmers,
environmental groups and civil society**, and shows the other side's response where one exists.

- **Map:** `web/index.html` (hover for a preview, click for details, filter by year, month, group, keyword)
- **Data:** `data/protests.json`, one record per protest, validated against `schema/protest.schema.json`
- **API:** plain JSON files built from the data (no application server or database)

## Quick start

Python 3.9+ is required. Install the development dependency used for JSON Schema validation:

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate.py
python scripts/build_api.py --out site
python -m http.server -d site 8000   # open http://localhost:8000
```

## API v1

The public API is static JSON. Existing v1 endpoint paths and response shapes are maintained.
New metadata fields are additive; clients should ignore fields they do not use.

| Endpoint | Returns |
|---|---|
| `/api/v1/index.json` | metadata, years, months, groups and endpoint templates |
| `/api/v1/protests.json` | every record, newest first, plus `meta` |
| `/api/v1/years/2026.json` | records active in a year |
| `/api/v1/months/2026-11.json` | records active in a month |
| `/api/v1/groups/students.json` | records by protester group |
| `/api/v1/records/{id}.json` | one record |

Groups: `ruling`, `opposition`, `students`, `workers`, `farmers`, `environment`, `civil`.

### Version and dataset metadata

The `meta` object includes:

- `api_version`: API contract version (currently `1.0.0`).
- `schema_version`: protest-record schema version (currently `1.0.0`).
- `dataset_revision`: SHA-256 digest of the exact source `data/protests.json` bytes.
- `generated_at`: UTC timestamp for the build. The legacy `generated` field remains available.
- `count`, `counts_by_group`, and `intensity_scale`: existing dataset metadata.

The dataset revision changes when the source JSON file changes, including formatting-only changes.
It identifies the exact source file used for a build; it is not a claim that every source report
has been independently re-verified at build time.

### Compatibility policy

- Existing `/api/v1/` paths and established response fields are retained.
- New response fields may be added; clients should tolerate unknown fields.
- Existing fields will not be silently repurposed or removed from v1.
- A breaking response or semantic change requires a new major API version (for example `/api/v2/`).
- The record schema version is tracked separately from the API version.

See [API versioning policy](docs/API_VERSIONING.md).

### Example: use the API from JavaScript

```javascript
fetch("https://YOUR-HOST/api/v1/months/2026-11.json")
  .then(response => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  })
  .then(({ records }) => records.forEach(record => {
    console.log(record.title, record.intensity);
  }));
```

Replace `https://YOUR-HOST` with the deployed site origin. Static hosting must be configured
to serve the generated files and, for cross-origin browser use, send suitable CORS headers.

### Example: use the API from Python

```python
import requests

url = "https://YOUR-HOST/api/v1/protests.json"
response = requests.get(url, timeout=20)
response.raise_for_status()
payload = response.json()

print(payload["meta"]["dataset_revision"])
for record in payload["records"]:
    print(record["title"], record["intensity"])
```

## Data and record format

Each record has a stable lowercase-hyphenated `id`, month-level `start` and `end` values
(`YYYY-MM`), a human-readable `date_label`, a location, intensity, status, groups, narrative
fields, source links and a `last_verified` date (`YYYY-MM-DD`). The `response` field is optional
when the other side's position could not be found; contributors must not guess it.

`intensity` follows the fixed editorial rubric in [CONTRIBUTING.md](CONTRIBUTING.md). It is a
classification of reported events, not a measure of a protest's merit, popularity or legitimacy.

## Validation and tests

```bash
python scripts/validate.py
python -m unittest discover -s tests -v
python scripts/build_api.py --out site
```

The validator enforces the Draft 2020-12 JSON Schema plus cross-field rules such as chronological
month ranges and unique IDs. Editorial warnings (for example, a single source or missing response)
do not fail validation. CI runs validation and regression tests before deployment.

## Deploy

**GitHub Pages:** Settings → Pages → Source: *GitHub Actions*. The included workflow validates,
tests, builds and deploys on pushes to `main`.

**Netlify or Cloudflare Pages:** build command `python scripts/build_api.py --out site`,
publish directory `site`. The build emits a `_headers` file for hosts that support this convention.

**CORS note:** GitHub Pages does not apply the Netlify/Cloudflare `_headers` convention. Same-origin
requests work normally; cross-origin browser requests require a host or proxy that sends CORS headers.

## Updating

Edit `data/protests.json` (or review an issue/PR), run validation and tests, then merge. CI rebuilds
the API. Contributors do not need to commit generated files.

## Limitations

- This is a curated sample compiled from news reports, **not a complete or official record**.
  Coverage is uneven across states and months.
- Intensity is a rubric score based on reported facts, not a measure of a protest's merit.
- Source links are recorded as provenance; a successful build does not guarantee that every source
  URL remains available or that every claim has been independently verified.
- State outlines are simplified from the [datameet/maps](https://github.com/datameet/maps)
  Survey of India–based data (Ladakh is merged into Jammu & Kashmir there). Check that project's
  licence before redistributing the boundaries.
- Corrections are welcome. Open an issue with a source.

## Licence

Code: MIT (`LICENSE`). Data text: please attribute "India Protest Map contributors" and the linked
sources; choose and publish a data licence before broad redistribution.
