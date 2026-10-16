# Conventions for every Open Data Centers skill

Read this before running any `odc-*` skill. These rules beat anything a single skill says.

## Files
- `data/states/registry.json`: the covered states, each with its official sources, records law and local news outlets. Every skill gets its source list from here, never from memory.
- `PIPELINE.md`: the order skills run in, and which skill owns which data point. `DATA_POINTS.md`: why each data point exists.
- `MISSION.md`: goals, what counts as a site, coverage checklist and refresh windows.
- `data/SCHEMA.md`: the record formats. Read before writing data.
- `data/louisiana.json`, `data/mississippi.json`: one array of site records each.
- `data/leads.json`: unconfirmed possible sites.
- `data/states/LA.json`, `data/states/MS.json`: statewide laws, dockets, rate cases, local rules, ballots, polls, utilities, news.
- `outreach/`: records request playbook, templates, log. `outreach/drafts/` is private (gitignored).
- `scripts/validate.py`: the rule checker. `scripts/coverage.py`: the job list.

## Data rules
1. Every number or claim has `source` (URL), `date` (YYYY-MM-DD of the source) and, for metrics, `kind` (`real` or `estimate`).
2. Unknown is `null`. Never guess, never fill from memory.
3. Prefer, in order: government records and dockets, company filings and pages, local and major newspapers. Trackers, aggregators and AI/crypto news sites are leads only, never sources.
4. One weak source means `confidence: "low"`. Two independent good sources, or one official one, means `medium` or `high`.
5. `opposition` is only real opposition: lawsuits, petitions, appeals, votes against, organized groups, pushes for a pause. Everything else critical goes in `scrutiny`.
6. Before and after shows change, never cause.
7. A transparency item is `hidden` only after `outreach/log.csv` shows we asked and they refused or the deadline passed.

## Write rules
- **When other skills run at the same time (routines, parallel agents), never edit `data/*.json` directly.** Write one patch file to `data/_incoming/<skill>-<target>.json` (format at the top of `scripts/merge_patches.py`), then the run merges with `python scripts/merge_patches.py`. Running alone, a skill may edit the files directly.
- Each skill writes only its own fields (listed in the skill). Don't touch another skill's fields, except to fix a broken source you happened to find (note it in the PR).
- After refreshing a section, set `checked.<section>` to today's date on that record, even if nothing changed.
- Save after every site or two, so partial work survives.
- Read-modify-write shared files (`leads.json`): load, change your entries, write back. Never overwrite other entries.

## Finish rules
1. Run `python scripts/validate.py`. Fix everything it reports.
2. Run `python scripts/coverage.py --skill <your skill>` and confirm your jobs went down.
3. In routines: commit to a new branch `odc/<skill>/<YYYY-MM-DD>` and open a pull request titled `<skill>: <what changed>` with a short list of changes and any doubts. Never push to `main`.
4. Never send email, post, or file anything outside the repo. Drafts only.

## Report format (PR body and chat)
```
<skill> run, <date>
Changed: <n> records (<ids>)
New: <list>
Doubts: <list, or "none">
Jobs left for this skill: <n>
```
