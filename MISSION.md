# Mission

**Open Data Centers is a public, neutral record of every large data center in the United States: what it costs the town, what it gives back, and what the company has and hasn't shared.**

AI data centers became a national fight in 2026. Companies and officials say they bring jobs, taxes and teacher raises. Neighbors worry about power bills, water, noise and secret tax deals. Both sides argue without a shared set of facts. This project is that set of facts: sourced, dated, and open to everyone.

## What we're trying to achieve

1. **A page for every site.** Every large data center in each covered state, at any stage, has a public page with its numbers, its news, local pushback, and what the company says.
2. **Every number has a source.** Each figure links to where it came from, has a date, and is tagged real or estimate. Unknown stays blank. Nothing is guessed.
3. **A fair openness score.** One public checklist of 8 things every company should share, applied the same way to everyone. "Hidden" only appears after we asked and they didn't answer.
4. **Before and after.** Power bills, rent, home values, wages and sales tax in each data center county, compared with a look-alike county without one.
5. **Local voices.** People who live nearby can say what changed (verified by phone and ZIP code). Coming soon.
6. **Found by the people who need it.** Each county gets its own page, so a search for "[county] data center" lands here.
7. **Kept fresh by agents.** Each kind of data has its own skill. Routines run them on a schedule and open pull requests that a human reviews.

## What counts as a site

- **In:** data center projects of about 20 MW or more, or $100M or more, plus hyperscale, AI and crypto mining campuses, at any stage: announced, permitted, building, running, paused, blocked, cancelled, closed (ran, then shut down).
- **Tagged small:** telecom, colocation and enterprise server rooms below that size. Listed only when easy to find.
- **One record per campus.** A campus or project is one record, even if it has many buildings. Phases of the same campus are one record. A new campus by the same company in another county is a new record.
- **Running campuses count, whatever year they opened.** Hyperscale, AI and crypto campuses that are already running are in, not only projects announced since 2023.
- **Leads:** possible projects that aren't confirmed yet go in `data/leads.json` until two good sources, or one official source, confirm them.

## Coverage checklist (per state)

A state is "covered" when every box below has a current entry (checked within its refresh window) or an explicit "none found" with the date we looked.

| Area | Where it lives | Refresh | Skill |
|---|---|---|---|
| Every site, all stages | `data/{state}.json` | weekly | `odc-find-sites` |
| Leads resolved or still open | `data/leads.json` | weekly | `odc-find-sites` |
| Site numbers (power, water, jobs, tax, cooling, land, deal) | site `metrics` | monthly | `odc-site-numbers` |
| News for each site | site `news` | weekly | `odc-news` |
| Pushback: lawsuits, petitions, appeals, votes, groups | site `opposition` (+ `scrutiny`) | weekly | `odc-pushback` |
| What the company says | site `official_statements` | monthly | `odc-site-numbers` |
| Openness checklist | site `transparency` + `outreach/log.csv` | when replies arrive | `odc-outreach` |
| Before and after vs. look-alike county | site `before_after` | quarterly | `odc-before-after` |
| Tax-break laws and incentives | `data/states/{st}.json` `incentives` | monthly | `odc-state-policy` |
| Bills in the legislature | `laws_and_bills` | weekly during session, monthly otherwise | `odc-state-policy` |
| Utility regulator dockets | `dockets` | monthly | `odc-state-policy` |
| Utility rate cases | `rate_cases` | monthly | `odc-state-policy` |
| Local pauses, zoning, ordinances | `local_rules` | weekly | `odc-state-policy` |
| Ballot measures | `ballot_measures` | monthly | `odc-state-policy` |
| Polls | `polls` | monthly | `odc-state-policy` |
| Who sells power to homes, by area | `utilities` | yearly | `odc-state-policy` |
| Sources still live, numbers still match | all files | monthly | `odc-verify` |
| Public website rebuilt | `public/` | after every merge | `odc-build-site` |

`python scripts/coverage.py` prints what's missing or stale. Routines read it to pick their next job.

## Rules that never bend

- Never guess. Unknown is blank.
- Before and after shows change, not cause. Always show the comparison county.
- Same checklist, same scoring, for every company.
- Every requests email is a draft until a human sends it.
- Agents open pull requests. They never push straight to the main branch.

## Not in scope (for now)

Places outside the 50 states and DC (adding one is the `odc-add-state` skill). Small server rooms. Opinion pieces written by us. Anything we can't source.
