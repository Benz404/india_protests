# India Protest & Peace Map

An open, non-partisan, interactive map of protests across India, with a free static JSON API.
It records protests by **ruling parties, opposition parties, students, workers, farmers,
environmental groups and civil society**, and shows the other side's response where one exists.

- **Map:** `web/index.html` (hover for a preview, click for details, filter by year, month, group, keyword)
- **Data:** `data/protests.json`, one record per protest, validated against `schema/protest.schema.json`
- **API:** plain JSON files built from the data (no server, no database)

## Quick start

```bash
python scripts/validate.py
python scripts/build_api.py --out site
python -m http.server -d site 8000   # open http://localhost:8000
```

Python 3.9+ standard library only.

## API

All endpoints are static files, served with CORS enabled.

| Endpoint | Returns |
|---|---|
| `/api/v1/index.json` | metadata, list of years, months, groups, endpoint templates |
| `/api/v1/protests.json` | every record, newest first, plus `meta` (counts by group, intensity scale) |
| `/api/v1/years/2026.json` | records active in a year |
| `/api/v1/months/2026-11.json` | records active in a month (multi-month protests appear in each month) |
| `/api/v1/groups/students.json` | records by protester group |
| `/api/v1/records/{id}.json` | one record |

Groups: `ruling`, `opposition`, `students`, `workers`, `farmers`, `environment`, `civil`.

### Use it on your website

```html
<script>
fetch("https://benz404.github.io/india_protests/api/v1/months/2026-11.json")
  .then(r => r.json())
  .then(({records}) => records.forEach(r => console.log(r.title, r.intensity)));
</script>
```

Or embed the map as is: `<iframe src="https://benz404.github.io/india_protests/"></iframe>`.
To point the map at another copy of the API, add `?api=https://example.org/api/v1/protests.json`.

## Record format

```json
{
  "id": "arunachal-pradesh-siang-dam-2026-10",
  "title": "Arunachal Pradesh — Siang dam",
  "start": "2026-10", "end": "2026-10", "date_label": "Oct 23–25, 2026",
  "scope": "local",
  "location": {"name": "Arunachal Pradesh", "state": "Arunachal Pradesh", "lat": 28.1, "lon": 95.1},
  "intensity": 5, "status": "unknown",
  "groups": ["environment"], "topics": "Environment · Land",
  "summary": "...", "background": "...", "status_text": "...", "response": "...",
  "sources": [{"title": "Express Tribune / AFP", "url": "https://..."}],
  "last_verified": "2026-11-01"
}
```

`intensity` follows a fixed rubric (see CONTRIBUTING.md). Nationwide protests use `"scope": "national"`
and a pin near the centre of the country.

## Deploy

**GitHub Pages:** Settings → Pages → Source: *GitHub Actions*. The included workflow validates every
pull request and deploys on push to `main`.

**Netlify:** build command `python scripts/build_api.py --out site`, publish directory `site`.
The build writes a `_headers` file that allows cross-origin requests.

## Adding a record (easy way)

Open **`/add.html`** on the live site (for example https://benz404.github.io/india_protests/add.html).
Fill in the form, click the place on the map, and press **Send for review**. This opens a pre-filled
GitHub issue. A bot validates it and opens a pull request. The maintainer checks the wording, sources and
the other side's response, then merges. The site and API rebuild by themselves.

**One-time setup for the maintainer:** Settings → Actions → General → Workflow permissions →
choose *Read and write permissions* and tick *Allow GitHub Actions to create and approve pull requests*.

Advanced: you can also edit `data/protests.json` directly, then run `python scripts/validate.py`.

## Limitations

- This is a curated sample compiled from news reports, **not a complete or official record**.
  Coverage is uneven across states and months; the validator lists records with missing responses
  or a single source.
- Intensity is a rubric score based on reported facts, not a measure of a protest's merit.
- State outlines are simplified from the [datameet/maps](https://github.com/datameet/maps) Survey of
  India–based data (Ladakh is merged into Jammu & Kashmir there). Check that project's licence
  before redistributing the boundaries.
- Corrections are welcome. Open an issue with a source.

## Licence

Code: MIT (`LICENSE`). Data text: please attribute "India Protest Map contributors" and the linked
sources; choose a data licence (for example CC BY 4.0) before publishing.
