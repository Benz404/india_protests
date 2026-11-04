# Contributing

The easiest way to add a protest is the form at `/add.html` on the live site. It produces a pull request
automatically. Records live in `data/protests.json` if you prefer to edit the file yourself.

## Editorial policy (this is what keeps the map non-partisan)

1. **Every side counts.** Record protests by ruling parties, opposition parties, students, workers,
   farmers, environmental groups and civil society. Do not skip a protest because you agree or
   disagree with it. "Ruling" and "opposition" are relative to the Union government.
2. **Neutral wording.** Describe what happened and what the organisers say. Attribute claims
   ("the unions say", "police say"). No loaded adjectives.
3. **Include the other side.** Fill `response` with the position of the authorities, company or rival
   party. If you could not find one, leave it out. The build will warn, and that gap stays visible.
4. **Sources are required.** At least one `https` link, two where possible, ideally from outlets with
   different leanings. Prefer news agencies and primary documents. Mark organisers' figures as theirs.
5. **Intensity follows facts, not opinion.** (The map covers independent India, 1947 onward.)
   1 peaceful · 2 minor friction (detentions, scuffles) · 3 heavy policing or disruption
   (barricades, water cannon, bandh) · 4 force or injuries (baton charge, tear gas, injured people)
   · 5 serious violence (arson, many injured, deaths). Same rubric for everyone.
6. **Dates and verification.** `start`/`end` are months (`YYYY-MM`); put exact dates in `date_label`.
   Set `last_verified` to the day you checked the sources. Do not guess: write "unconfirmed".
7. **People.** Do not add private individuals' names or personal details.

## Workflow

```bash
python scripts/validate.py          # must pass (errors fail CI, warnings are advice)
python scripts/build_api.py --out site
python -m http.server -d site 8000  # preview at http://localhost:8000
```

## Older (1947 onward) records

- Use a year (`"start": "1973"`) when the month is not known. Year-only records show under "All <year>" but not in a single month.
- Prefer at least two independent sources, and add one that is not a news report from the time, such as a
  university press, a government document or an archive.
- Where sources disagree on a date, say so in `status_text` ("sources give 1973 or 1974"). Do not pick silently.
- Contested events (for example the Emergency, 1984, Kashmir, Ayodhya) need extra care: attribute every claim,
  show each side's position in `response`, and avoid death tolls unless a named source gives them.

## Historical records (1947 onwards)

- Put them in `data/historical.json` (same format). Set `"needs_review": true` until a second person has
  checked them against a stronger source than an encyclopedia.
- Cover every side across every era and government: movements against and for the government of the day,
  and protests by workers, farmers, students, communities and religious and political groups of all kinds.
- Use cautious numbers. If counts are disputed, say so instead of picking one.
