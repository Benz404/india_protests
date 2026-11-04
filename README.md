<p align="center"><img src="web/logo.svg" width="110" alt="The Vinci Terminal logo"></p>

<h1 align="center">India Protest &amp; Peace Map</h1>

<p align="center">An open, non-partisan, sourced record of protests across India since 1947,<br>with an interactive map and a free JSON API.</p>

<p align="center"><a href="https://benz404.github.io/india_protests/">Open the map</a> ·
<a href="https://benz404.github.io/india_protests/add.html">Add a protest</a> ·
<a href="https://benz404.github.io/india_protests/api/v1/index.json">API</a></p>

---

## About The Vinci Terminal

The Vinci Terminal is an independent project that builds free tools for learning. It hosts physics and science
simulations for students and publishes independent research. Follow it on Instagram:
[@the_vinci_terminal](https://instagram.com/the_vinci_terminal).

## Why this map exists

Protest is one of the ways a democracy talks to itself. People take to the streets from every side: ruling parties
and opposition parties, students, workers, farmers, environmental groups and ordinary citizens. A record of those
voices is only useful if no side owns it.

So this project is open, sourced and checkable:

- **Every side is included.** Records cover ruling-party, opposition, student, worker, farmer, environmental and
  civil-society protests. "Ruling" and "opposition" mean relative to the Union government of the time.
- **Every record names its sources** and, where one exists, shows the response of the other side.
- **Intensity follows a fixed rubric of reported facts**, never opinion: 1 peaceful, 2 minor friction (detentions,
  scuffles), 3 heavy policing or disruption, 4 force or injuries, 5 serious violence.
- **The data and code are public.** Anyone can correct a record or bring a better source.

## What is in it

- `data/protests.json`: recent protests (2026)
- `data/recent_2022_2025.json`: 2022 to 2025
- `data/historical.json`: landmark protests from 1947 to 2021

Records marked `"needs_review": true` are starter entries compiled from general references and not yet checked against
primary sources. The map says so on each one. Coverage is a curated sample, **not a complete or official record**.

## Quick start

```bash
python scripts/validate.py
python scripts/build_api.py --out site
python -m http.server -d site 8000   # open http://localhost:8000
```

Python 3.9+, standard library only.

## API

Static JSON files, served with CORS enabled. No key needed.

| Endpoint | Returns |
|---|---|
| `/api/v1/index.json` | metadata, years, months, groups, endpoint templates |
| `/api/v1/protests.json` | every record, newest first, plus `meta` |
| `/api/v1/years/2026.json` | records active in a year |
| `/api/v1/months/2026-11.json` | records active in a month |
| `/api/v1/groups/students.json` | records by protester group |
| `/api/v1/records/{id}.json` | one record |

Groups: `ruling`, `opposition`, `students`, `workers`, `farmers`, `environment`, `civil`.

```js
fetch("https://benz404.github.io/india_protests/api/v1/groups/workers.json")
  .then(r => r.json()).then(d => console.log(d.count, d.records));
```

Embed the whole map: `<iframe src="https://benz404.github.io/india_protests/" style="width:100%;height:90vh;border:0"></iframe>`

## Add a record

Open [`/add.html`](https://benz404.github.io/india_protests/add.html), fill in the form, click the place on the map and
press **Send for review**. A bot validates the record and opens a pull request. The maintainer checks the wording,
sources and the other side's response, then merges. The site and API rebuild automatically.

You can also edit the JSON files directly. See [CONTRIBUTING.md](CONTRIBUTING.md) for the editorial policy.

**One-time maintainer setup:** Settings, Actions, General, Workflow permissions: choose *Read and write permissions* and
tick *Allow GitHub Actions to create and approve pull requests*.

## Deploy

**GitHub Pages:** Settings, Pages, Source: *GitHub Actions*. The workflow validates every pull request and deploys on
push to `main`.

**Netlify:** build command `python scripts/build_api.py --out site`, publish directory `site`.

Run `python scripts/check_links.py` now and then to find source links that stopped working.

## Limitations

- Coverage is uneven across states, years and causes. Help fill the gaps.
- Present-day state names are used even for events before a state was created.
- State outlines are simplified from [datameet/maps](https://github.com/datameet/maps) data. Ladakh is merged into
  Jammu and Kashmir there. Check that project's licence before redistributing the boundaries.
- Corrections are welcome. Open an issue with a source.

## Licence

Code: MIT (see `LICENSE`). Please credit "India Protest Map contributors" and the linked sources when reusing the data,
and choose a data licence (for example CC BY 4.0) before publishing it. The logo belongs to The Vinci Terminal and is
not covered by the MIT licence.
