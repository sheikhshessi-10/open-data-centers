---
name: odc-site-numbers
version: 1.0.0
description: |
  Fills and refreshes the hard numbers for a data center site (money, power, water, cooling, land, jobs, tax break, local tax paid, deal with the town, exact location) plus the company's own official statements, every value sourced and tagged real or estimate.
triggers:
  - "update the numbers for {site}"
  - "fill missing metrics"
  - "monthly numbers refresh"
tools:
  - WebSearch, WebFetch
  - browser-harness (pages that need a real browser), Bash (pdf text extraction)
  - Read, Edit, Bash (validate.py, coverage.py)
mutating: true
---

# Site numbers

Owns: `metrics`, `official_statements`, `lat`/`lng`, `transparency_sources`, and `transparency` items moving from `not_asked` to `shared` or `partly` when the company itself published the item. Sets `checked.metrics`.

## Contract
- Every metric has value, unit, kind, source and date. Newer official numbers replace older ones; the older value moves to `notes` with its source.
- `kind: real` only for government records, company filings or statements, and measured data. Reporter or analyst figures are `estimate`.
- Exact coordinates only from a permit, plat, company page or official map. Otherwise lat/lng stay null (the site builder shows a town-center pin marked approximate).
- A transparency item moves to `shared`/`partly` only when the company itself published it, with evidence in the matching metric or `transparency_sources`.

## Phases
1. **Pick targets** from `python scripts/coverage.py --skill odc-site-numbers` or the list given.
2. **For each site, check these sources for each empty or stale metric:**
   - investment_usd, jobs_promised_*: state economic development release, governor release, incentive agreement.
   - power_mw, power_source, utility: regulator docket filings (large-load or special contract), company page, utility press release.
   - water_use, cooling_type: water utility contract or council minutes, state water permit, company sustainability page.
   - tax_break, local_tax_paid: incentive law terms, PILOT or fee-in-lieu agreement, assessor records, school board or sales tax reports.
   - jobs_actual: company statement, state job reports, local reporting with a named source.
   - acres, lat/lng: rezoning application, plat, permit, company site map.
   - community_deal: community benefit agreement, council resolution, company commitments page.
3. **Official statements:** add the company's own newest statements about the site (press release, newsroom, testimony), quoted briefly, with source.
4. **Write**, then set `checked.metrics` to today.
5. **Verify** with validate.py. Re-open the source of every value you changed.
6. **Finish** per CONVENTIONS.md.

## Output Format
```json
"power_mw": {"value": 500, "unit": "MW (expected at full build)", "kind": "real", "source": "https://...", "date": "2026-05-08"}
```
Text values are allowed when no single number exists, e.g. `"value": "Closed-loop cooling, no continuous water draw (company claim)"`.

## Anti-Patterns
- Don't mix phases or units in one value, like phase 1 MW with full-campus MW (because the cards rank sites by these numbers, and a mixed value ranks wrong). Put the phase in `unit` and the other figure in `notes`.
- Don't mark a reporter's number `real` (because "real" tells readers it's an official figure, and the openness score relies on that line).
- Don't overwrite a number without moving the old one to `notes` (because changes over time, like Meta's $10B growing to $50B, are part of the story).
