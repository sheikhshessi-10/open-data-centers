---
name: odc-add-state
version: 1.0.0
description: |
  Brings a new state into Open Data Centers: registers it with its official sources and records law, creates its empty data files, then runs the full pipeline (state policy, site sweep, numbers, news, pushback, before-and-after) until the coverage report is clean for that state.
triggers:
  - "add {state} to open data centers"
  - "start covering {state}"
  - "expand to a new state"
tools:
  - WebSearch, WebFetch
  - Read, Write, Edit, Bash (validate.py, coverage.py, merge_patches.py, site/build.py)
  - Agent (one per skill, in parallel, writing patch files)
mutating: true
---

# Add a state

Owns: the state's entry in `data/states/registry.json`, the new empty files, and the first full pipeline run. After that, the normal routines keep the state fresh with no code changes.

## Contract
- The registry entry has every required field: code, name, slug, 2-digit Census FIPS code, county word ("County", "Parish", "Borough"), site file name, official sources (economic development, governor news, utility regulator, environment agency, water agency, legislature, revenue), the public records law with its response deadline and cite, and 6 or more local news outlets. Each URL is checked to load.
- No code is edited. If a script or page needs a code change for the new state, that is a bug in the code: fix it so it reads the registry, and note it in the PR.
- The pipeline runs in the order below, and the state counts as launched only when `python scripts/coverage.py` shows no P1 jobs for it.
- Outreach for the new state stops at drafts, like everywhere else.

## Phases
1. **Research the state's plumbing** (no site research yet):
   - The official sources above, with working URLs.
   - The public records law: name, cite, who can ask, response deadline and its cite. Read the statute or the attorney general's guide; don't trust a summary.
   - The 2-digit FIPS code (Census) and the county word.
   - Local news outlets that cover business and local government.
2. **Register.** Add the entry to `data/states/registry.json`. Create `data/{slug}.json` as `[]` and `data/states/{CODE}.json` as `{"state": "{CODE}", "checked": {}}`. Add the state's records request template to `outreach/templates.md` (copy template A, swap in the law, cite and deadline). Run `python scripts/validate.py`. When several states are added at once by parallel agents, each agent writes `{"registry_entries": [...]}` to `data/_incoming/registry-<group>.json` instead, and `python scripts/merge_patches.py` adds the entries and creates the empty files.
3. **Statewide picture first:** run `odc-state-policy` for the state. Incentive laws and utility dockets point to where the sites are.
4. **Find sites:** run `odc-find-sites` for the state as a full sweep since 2023, then a second sweep a week later (the second Louisiana pass found a site the first one missed).
5. **Fill each site, in parallel**, each skill writing its own patch file to `data/_incoming/`: `odc-site-numbers`, `odc-news` + `odc-pushback`, `odc-before-after`. Then `python scripts/merge_patches.py` and `python scripts/validate.py`.
6. **Contacts and drafts:** run `odc-outreach` to collect contacts and draft requests. Stop for the human.
7. **Audit:** run `odc-verify` on the whole state.
8. **Build:** `python site/build.py --check`. The state, county and site pages appear automatically, and the map adds the state and its neighbors.
9. **Report** per CONVENTIONS.md, with the coverage numbers for the state.

## Output Format
Registry entry: same shape as the Louisiana and Mississippi entries in `data/states/registry.json`.
Launch report:
```
{State} launched {date}: {n} sites ({stages}), {n} leads, state file sections filled {n}/9.
Coverage jobs left for {CODE}: P1 {n}, P2 {n}, P3 {n}.
Drafts waiting: {n}. Doubts: {list}.
```

## Anti-Patterns
- Don't start the site sweep before the statewide research (because the dockets and incentive laws are the best map of where projects are; skipping them is how a first pass misses sites).
- Don't hard-code the state anywhere in scripts or pages (because the next state would need code edits again; everything reads the registry).
- Don't copy another state's records deadline (because each state's law differs; Louisiana is 3 business days and Mississippi is 7 working days).
