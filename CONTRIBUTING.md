# Contributing

Thanks for helping. The one rule: every fact needs a source link and a date. Unknown stays blank.

## Fix or add something without code

[Open an issue](https://github.com/sheikhshessi-10/open-data-centers/issues) with the site, what's wrong or missing, and a link to the source (a government record, company page, regulator filing or news story). Trackers and directory sites are useful leads, but they can't be the source.

## Run it locally

```bash
python scripts/validate.py          # check the data against the rules
python scripts/coverage.py          # see what's missing or stale
python site/build.py --check        # build the site into public/ and check links
python -m http.server -d public     # preview at http://localhost:8000
```

Python 3.10 or newer. No packages needed.

## Where things live

- `data/{state}.json`: one record per site. Format in [data/SCHEMA.md](data/SCHEMA.md).
- `data/states/`: each state's tax breaks, bills, utility cases, local rules and records law. `data/states/registry.json` lists the covered states and their official sources.
- `data/leads.json`: possible sites waiting for confirmation.
- `outreach/`: how public records requests work, templates, and the request log.
- `scripts/`: the rule checker, the coverage report, and the patch merger agents use.
- `site/`: the static site generator.
- `.claude/skills/`: one agent skill per kind of data. Start with `.claude/skills/CONVENTIONS.md`, [PIPELINE.md](PIPELINE.md) and [DATA_POINTS.md](DATA_POINTS.md) (why each number exists).
- [MISSION.md](MISSION.md): the goals, what counts as a site, and the coverage checklist.

## Pull requests

Run `python scripts/validate.py` before you open one; the same check runs on every pull request. Agent runs open pull requests on branches named `odc/<skill>/<date>`; a person reviews and merges. Nothing goes straight to `main`.
