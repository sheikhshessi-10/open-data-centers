# Open Data Centers

A public, neutral, sourced record of every large data center in **the United States** (all 50 states and DC; Louisiana and Mississippi have the deepest data so far): what it costs the town, what it gives back, and what the company has and hasn't shared.

- Every number links to its source, has a date, and is tagged `real` or `estimate`. Unknown stays blank.
- Every site, county and state has its own page, so a search for "[county] data center" lands on the facts.
- Each company gets the same 8-item openness checklist. "Hidden" only appears after we asked and got no answer.

Read [MISSION.md](MISSION.md) for the goals, what counts as a site, and the coverage checklist.

## What's in the repo

| Path | What it is |
|---|---|
| `data/louisiana.json`, `data/mississippi.json` | One record per site. Format in [data/SCHEMA.md](data/SCHEMA.md). |
| `data/states/` | Statewide laws, incentives, utility cases, local rules, ballots, polls, utilities. |
| `data/leads.json` | Possible sites not yet confirmed. |
| `outreach/` | How we request public records, templates, and the request log. |
| `scripts/validate.py` | Checks every data file against the rules. Runs on every pull request. |
| `scripts/coverage.py` | Lists what's missing or stale. The agent routines use it as their job list. |
| `site/` | Builds the static website into `public/`. |
| `.claude/skills/` | One skill per kind of data, run by agents on a schedule. See `.claude/skills/CONVENTIONS.md`. |

## Run it

```bash
python scripts/validate.py          # check the data
python scripts/coverage.py          # see what's missing or stale
python site/build.py --check        # build the website into public/ and check links
python -m http.server -d public     # preview at http://localhost:8000
```

Python 3.10 or newer. No packages needed.

## How the data stays fresh

Each kind of data has its own agent skill: finding sites, site numbers, news, pushback, before-and-after numbers, state policy, records requests, source checks, and the site build. Scheduled routines run `scripts/coverage.py`, pick the stale jobs, run the matching skill, and open a pull request. A human reviews and merges. Nothing is pushed straight to `main`, and no email is ever sent by an agent.

## Contribute

Found a wrong number, a missing site, or a dead link? Open an issue or a pull request. Every change needs a source URL and a date. Run `python scripts/validate.py` before you submit.

## License

- Code: [MIT](LICENSE)
- Data (`data/`): [CC BY 4.0](data/LICENSE). Credit "Open Data Centers" with a link.
- County and state shapes: [us-atlas](https://github.com/topojson/us-atlas) (ISC), built from U.S. Census Bureau boundary files.
