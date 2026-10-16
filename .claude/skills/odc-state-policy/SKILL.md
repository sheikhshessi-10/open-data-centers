---
name: odc-state-policy
version: 1.0.0
description: |
  Maintains the statewide picture for every covered state (see data/states/registry.json): tax-break laws and incentives, bills, utility regulator dockets, rate cases, local pauses and zoning rules, ballot measures, polls, and which utilities serve which areas.
triggers:
  - "update state policy for {state}"
  - "check dockets and bills"
  - "weekly state run"
tools:
  - WebSearch, WebFetch
  - browser-harness (regulator docket sites that need a real browser)
  - Read, Edit, Bash (validate.py, coverage.py)
mutating: true
---

# State policy

Owns: everything in `data/states/{LA|MS}.json`, except `news` (owned by `odc-news`). Sets `checked.<section>` in the state file (use a dict of section dates).

## Contract
- Every entry has a source URL and date. Dockets come from the regulator's own site whenever possible; numbers from advocacy reports are marked "unverified" in `what` until checked there.
- Bills carry their current status and the date of that status.
- Local rules include every parish or county pause, ban, zoning change or ordinance about data centers, with status.
- Each docket lists the `site_ids` it concerns, when clear.

## Phases
1. **Targets** from `python scripts/coverage.py --skill odc-state-policy`.
2. **Bills:** search the state's legislature site (registry `sources.legislature`) for "data center", "large load", "hyperscale", "water", "ratepayer". During session, check weekly.
3. **Dockets and rate cases:** the state's utility regulator docket search (registry `sources.utility_regulator`) for each utility in the state file's `utilities` list. Record new filings, orders and hearing dates.
4. **Incentives:** check state economic development and revenue pages for program changes and any published cost figures.
5. **Local rules, ballots, polls:** search council and supervisor news, election sites, and university or media polls.
6. **Utilities:** yearly, confirm who serves homes in each parish or county with a site.
7. Set the section dates, run validate.py, finish per CONVENTIONS.md.

## Output Format
See "State file" in `data/SCHEMA.md`. Example docket:
```json
{"id": "U-37425", "regulator": "Louisiana PSC", "utility": "Entergy Louisiana", "what": "Three gas plants and a transmission line to serve Meta Hyperion. Approved 2025-08-20.", "site_ids": ["la-richland-meta-hyperion"], "status": "approved", "url": "https://...", "date": "2025-08-20"}
```

## Anti-Patterns
- Don't copy docket numbers from an advocacy report without checking the regulator's site (because the first Mississippi pass did this and couldn't confirm them).
- Don't record a bill as law until the governor signs it or it becomes law without a signature (because many bills die late, and the site would show a law that doesn't exist).
- Don't leave a section empty without a dated "none found" note (because empty and not-yet-searched look the same, and coverage.py treats empty as a job).
