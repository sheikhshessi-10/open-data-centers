---
name: odc-find-sites
version: 1.0.0
description: |
  Sweeps a covered state for data center projects not yet on record, resolves open leads, and adds confirmed sites as new records with basic sourced facts.
triggers:
  - "find new data centers in {state}"
  - "check the leads"
  - "weekly site sweep"
tools:
  - WebSearch (use mode "extended" for local and recent items), WebFetch
  - Read, Write, Edit, Bash (validate.py, coverage.py)
mutating: true
---

# Find sites

Owns: new records in `data/{state}.json` (id, name, owner, operator, tier, state, county, town, lat, lng, stage, announced, confidence, first metrics, first news) and all of `data/leads.json`. Also owns `stage` changes on existing records.

## Contract
- Every new site meets the "What counts" rule in MISSION.md and has at least two good sources or one official source. Otherwise it's a lead.
- Every open lead is re-checked and ends as `open` (with a new `last_checked`), `promoted` (now a site) or `dropped` (with the reason in `why_unconfirmed`).
- Stage changes (announced to permitted, building to running, anything to blocked or cancelled) are applied with a source.
- New records get `checked` dates only for the sections actually researched.

## Phases
1. **Load** the state's site file and `data/leads.json`. List known ids, owners and places so you don't add duplicates (same owner + same county is probably the same project).
2. **Sweep** these sources for the state, newest first, last 30 days on weekly runs. A full sweep covers every campus that is running today whatever year it opened, plus everything announced since 2023. Take the names and URLs from the state's entry in `data/states/registry.json` (`sources`, `local_news`):
   - Economic development agency and governor press releases.
   - Utility regulator dockets: new large-load contracts and special contracts. Also the dockets already listed in `data/states/{CODE}.json`.
   - Environment agency air permit notices for generators and turbines.
   - Parish and county council, police jury and supervisor agendas: rezonings, PILOT or fee-in-lieu deals, industrial board votes.
   - Local news searches: "data center" plus each parish or county name, "hyperscale", "AI campus", "crypto mining", "bitcoin mine", "megasite".
   - For a full sweep, also use trackers, subsidy databases and company location pages to build the list of candidates. These are leads only: confirm each with an official source or two good sources before it becomes a site.
3. **Decide** for each find (one record per campus, see MISSION.md): new site, update to an existing site (stage change), or lead.
4. **Write.** New sites follow SCHEMA.md exactly. Transparency defaults to `not_asked`. Leads get `added` and `last_checked` set to today.
5. **Resolve leads.** For each open lead, search again. Promote, keep or drop.
6. **Verify.** Run `python scripts/validate.py`, then open the sources of every new site and confirm each one says what the record claims.
7. **Finish** per CONVENTIONS.md.

## Output Format
New site skeleton (fill what's sourced, `null` the rest):
```json
{"id":"{st}-{county}-{owner}-{short}","name":"...","owner":"...","operator":null,"tier":"large","state":"LA","county":"... Parish","town":"...","lat":null,"lng":null,"stage":"announced","announced":"YYYY-MM-DD","confidence":"medium",
 "metrics":{"investment_usd":{"value":0,"unit":"USD","kind":"real","source":"https://...","date":"YYYY-MM-DD"}},
 "transparency":{"power_use":"not_asked","water_use":"not_asked","power_source":"not_asked","tax_break_size":"not_asked","jobs_promised_vs_actual":"not_asked","noise_tests":"not_asked","air_permits":"not_asked","community_deal":"not_asked"},
 "official_statements":[],"opposition":[],"scrutiny":[],"news":[],"contacts":[],"checked":{"metrics":"YYYY-MM-DD"},"notes":""}
```

`county` is the Census name with its word: "Loudoun County", "Richland Parish", "Richmond city" (a Virginia independent city), "Anchorage Municipality", "District of Columbia". `validate.py` rejects names that don't match the map.

## Anti-Patterns
- Don't add a site from a tracker or listicle alone (because early research found trackers listing rumors and wrong owners; trackers are leads only).
- Don't create a second record for a project that changed names or owners, like xAI to SpaceXAI (because duplicate pages split the news and pushback). Update the existing record and note the old name.
- Don't delete cancelled or blocked sites (because what got stopped, and why, is part of the public record). Set the stage instead.
