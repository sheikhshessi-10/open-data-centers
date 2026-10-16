# Site record format

One JSON object per data center site. Files: `data/louisiana.json`, `data/mississippi.json` (JSON array of these objects).

## Scope (what counts)

IN: large data center projects (roughly 20 MW+ or $100M+), hyperscale, AI, or crypto-mining campuses, at any stage: announced, permitted, building, running, paused, blocked, cancelled, closed (ran, then shut down).
TAG SEPARATELY (`"tier": "small"`): small colocation, telecom, enterprise or government server rooms. List them only if easy; don't spend time on them.

## Rules

- Every number or claim has a `source` URL and a `date` (date of the source).
- `kind`: `"real"` (official filing, company statement, government record, measured) or `"estimate"` (a reporter's or analyst's estimate, or our own math).
- Unknown means `null`. Never guess.
- `confidence` on the site itself: `high` (official source confirms it exists), `medium` (two news sources), `low` (one weak source).

## Object

```json
{
  "id": "la-richland-meta-hyperion",
  "name": "Hyperion",
  "owner": "Meta",
  "operator": null,
  "tier": "large",
  "state": "LA",
  "county": "Richland Parish",          // Census name with its word; "Richmond city" for a Virginia independent city
  "town": "Holly Ridge",
  "lat": null, "lng": null,             // exact pin only; with pin_source (URL that gave the address), pin_address, pin_geocoder ("osm" if not Census), pin_precision ("intersection" if not a street address). No pin = shown at the county center.
  "stage": "building",
  "announced": "2024-12-04",
  "confidence": "high",
  "metrics": {
    "investment_usd":      {"value": 10000000000, "unit": "USD", "kind": "real", "source": "...", "date": "..."},
    "power_mw":            null,
    "water_use":           null,
    "power_source":        null,
    "cooling_type":        null,
    "jobs_promised_build": null,
    "jobs_promised_perm":  null,
    "jobs_actual":         null,
    "tax_break":           null,
    "local_tax_paid":      null,
    "community_deal":      null,
    "utility":             null,
    "acres":               null
  },
  "transparency": {
    "power_use": "not_asked|hidden|partly|shared",
    "water_use": "not_asked|hidden|partly|shared",
    "power_source": "not_asked|hidden|partly|shared",
    "tax_break_size": "not_asked|hidden|partly|shared",
    "jobs_promised_vs_actual": "not_asked|hidden|partly|shared",
    "noise_tests": "not_asked|hidden|partly|shared",
    "air_permits": "not_asked|hidden|partly|shared",
    "community_deal": "not_asked|hidden|partly|shared"
  },
  "official_statements": [{"text": "...", "source": "...", "date": "..."}],
  "opposition": [{"what": "lawsuit / petition / council vote / group name", "source": "...", "date": "..."}],
  "news": [{"title": "...", "outlet": "...", "url": "...", "date": "...", "tone": "good|bad|neutral"}],
  "contacts": [{"who": "company community relations / parish permit office / ...", "how": "email/phone/form/address", "value": "...", "source": "..."}],
  "notes": ""
}
```

Every metric value uses the shape `{"value", "unit", "kind", "source", "date"}`.

## Transparency score

Optional field `"transparency_sources": {"noise_tests": {"source": "...", "date": "..."}}` holds evidence for items with no matching metric. Every `shared` or `partly` item needs evidence.

Until all 8 items are settled, show counts ("3 of 8 checked: ..."), not a percent. Once all are settled: score = shared (1) + partly (0.5) + hidden (0), divided by 8. An item only counts as "hidden" once we've asked and logged that request (see `outreach/log.csv`). Before that it's "not yet asked".

## Freshness (added 2026-10-14)

Each site record may carry `"checked": {"metrics": "YYYY-MM-DD", "news": "...", "opposition": "...", "transparency": "...", "contacts": "...", "before_after": "..."}`. The date says when that section was last fully researched. Routines use it to find stale sections. A skill that refreshes a section must update its date, even when nothing new turned up.

`opposition` holds only real opposition: lawsuits, petitions, appeals, council or board votes against, organized groups, moratorium pushes. Other scrutiny (donations, audits, critical reporting) goes in `"scrutiny": [{"what","source","date"}]`.

## Leads file: `data/leads.json`

Possible sites not confirmed yet. Array of `{"id","state","place","what","why_unconfirmed","sources":[url],"added","last_checked","status":"open|promoted|dropped"}`. A lead becomes a site once two good sources, or one official source, confirm a real project.

## State file: `data/states/{LA|MS}.json`

```json
{
  "state": "LA",
  "checked": {"incentives": "YYYY-MM-DD", "laws_and_bills": "YYYY-MM-DD", "...": "one date per section"},
  "incentives": [{"name","law","what","value_known","source","date"}],
  "laws_and_bills": [{"name","status":"enacted|pending|failed","what","source","date"}],
  "regulators": [{"name","role","url"}],
  "dockets": [{"id","regulator","utility","what","site_ids":[],"status","url","date"}],
  "rate_cases": [{"utility","what","impact","source","date"}],
  "local_rules": [{"place","type":"moratorium|zoning|ordinance|ballot","what","status","source","date"}],
  "ballot_measures": [{"place","what","vote_date","result","source"}],
  "polls": [{"who","what","result","source","date"}],
  "utilities": [{"name","type":"investor-owned|co-op|municipal|TVA","serves","url"}],
  "news": [{"title","outlet","url","date","tone"}]
}
```
Same rules as sites: every claim has a source and date, unknown is null, never guess.
