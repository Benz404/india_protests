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
5. **Intensity follows facts, not opinion.**
   1 peaceful · 2 minor friction (detentions, scuffles) · 3 heavy policing or disruption
   (barricades, water cannon, bandh) · 4 force or injuries (baton charge, tear gas, injured people)
   · 5 serious violence (arson, many injured). Same rubric for everyone.
6. **Dates and verification.** `start`/`end` are months (`YYYY-MM`); put exact dates in `date_label`.
   Set `last_verified` to the day you checked the sources. Do not guess: write "unconfirmed".
7. **People.** Do not add private individuals' names or personal details.

## Workflow

```bash
python scripts/validate.py          # must pass (errors fail CI, warnings are advice)
python scripts/build_api.py --out site
python -m http.server -d site 8000  # preview at http://localhost:8000
```
