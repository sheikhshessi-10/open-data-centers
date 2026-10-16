# The pipeline

How data gets into Open Data Centers, step by step, and which skill does each step. Every step is a skill in `.claude/skills/`, so an agent can run it alone or as part of a routine.

## The steps, in order

```
                 ┌──────────────────────┐
 new state ────► │ 1. odc-add-state     │  register sources + records law, empty files
                 └─────────┬────────────┘
                           ▼
                 ┌──────────────────────┐
                 │ 2. odc-state-policy  │  tax-break laws, bills, utility cases, rate cases,
                 └─────────┬────────────┘  local pauses, ballots, polls, who serves which area
                           ▼
                 ┌──────────────────────┐
                 │ 3. odc-find-sites    │  every site at every stage + leads
                 └─────────┬────────────┘
             ┌─────────────┼──────────────┬───────────────────┐
             ▼             ▼              ▼                   ▼
   ┌──────────────┐ ┌─────────────┐ ┌──────────────┐ ┌──────────────────┐
   │4a. site-     │ │4b. news     │ │4c. pushback  │ │4d. before-after  │   run in parallel,
   │   numbers    │ │             │ │              │ │                  │   each writes a patch
   └──────┬───────┘ └──────┬──────┘ └──────┬───────┘ └────────┬─────────┘   to data/_incoming/
          └────────────────┴───────┬───────┴──────────────────┘
                                   ▼
                 ┌──────────────────────────────┐
                 │ merge_patches.py + validate  │
                 └─────────┬────────────────────┘
                           ▼
                 ┌──────────────────────┐
                 │ 5. odc-outreach      │  contacts + request drafts (a human sends)
                 └─────────┬────────────┘  replies and deadlines update the openness score
                           ▼
                 ┌──────────────────────┐
                 │ 6. odc-verify        │  re-open sources, fix mismatches, dead links
                 └─────────┬────────────┘
                           ▼
                 ┌──────────────────────┐
                 │ 7. odc-build-site    │  pages for every state, county and site
                 └──────────────────────┘
```

The router skill `open-data-centers` reads `python scripts/coverage.py` and runs only the steps that have stale or missing work.

## Which skill fills which data point

| Data point | Skill | Refresh |
|---|---|---|
| The list of sites, stage, leads | odc-find-sites | weekly |
| Money, power, water, cooling, power source, power company, land, exact pin, jobs promised, jobs so far, tax break, local tax paid, deal with the town, company statements | odc-site-numbers | monthly |
| News | odc-news | weekly |
| Pushback and other scrutiny | odc-pushback | weekly |
| Rent, home values, wages, jobs, power price, sales tax vs. a look-alike county | odc-before-after | every 3 months |
| Laws, incentives, bills, utility cases, rate cases, local rules, ballots, polls, utilities by area | odc-state-policy | weekly to yearly by section |
| Contacts, records requests, openness checklist | odc-outreach | weekly deadline check, and when replies arrive |
| Source checks, confidence | odc-verify | monthly |
| Pages, score bars, sitemap | odc-build-site | after every merge |
| A new state | odc-add-state | once per state |

Why each data point exists: see [DATA_POINTS.md](DATA_POINTS.md).

## Parallel runs never clash

Skills running at the same time never write the data files directly. Each writes one patch file to `data/_incoming/` (format at the top of `scripts/merge_patches.py`). `python scripts/merge_patches.py` applies them all, then `python scripts/validate.py` checks the result. Each skill owns its own fields, so patches don't overlap.

## Routines

| Routine | When | Runs |
|---|---|---|
| Weekly | Mondays | find-sites, news, pushback, state-policy (bills, local rules), outreach deadline check |
| Monthly | 1st of the month | site-numbers, state-policy (dockets, incentives, rate cases, polls), verify |
| Quarterly | Jan, Apr, Jul, Oct | before-after, outreach contact check |
| On merge | automatic | build-site (Vercel) |

Each routine: start from `coverage.py`, run the skills, merge patches, validate, open one pull request. A human approves. Nothing goes to `main` without review, and no email leaves without a human.

## Adding a state

Run `odc-add-state`. It adds the state to `data/states/registry.json` and runs steps 2 through 7. No code changes: every script, page and map reads the registry.
