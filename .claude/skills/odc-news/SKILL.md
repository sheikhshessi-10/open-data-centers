---
name: odc-news
version: 1.0.0
description: |
  Keeps each data center's news feed current: finds new articles about the site, tags each one good, bad or neutral, and drops duplicates and weak outlets.
triggers:
  - "refresh the news for {site}"
  - "weekly news run"
tools:
  - WebSearch (mode "extended" for local news), WebFetch
  - Read, Edit, Bash (validate.py, coverage.py)
mutating: true
---

# News

Owns: `news` on site records and `news` in `data/states/{st}.json`. Sets `checked.news`.

## Contract
- Every item has title, outlet, url, date and tone (`good`, `bad` or `neutral`).
- No duplicates: the same story syndicated across outlets is kept once, preferring the original outlet.
- Tone describes the story's effect on the site's local case, not our opinion: jobs or money arriving is `good`, harm or a fight is `bad`, process news is `neutral`.
- Each site keeps its 15 newest items plus any item another field cites.

## Phases
1. **Targets** from `python scripts/coverage.py --skill odc-news`.
2. **Search** for each site: site name, owner + county, owner + town, and the site's old names. Limit to items since `checked.news`. Prefer the state's local outlets listed in `data/states/registry.json` (`local_news`), then nearby papers and TV stations.
3. **Screen out** press-release reposts, AI-written content farms, paywalled stubs with no text, and items that only mention the site in passing.
4. **Tag** tone and add. If a story reports a new number, stage change or opposition action, list it in the PR body for the owning skill instead of editing those fields.
5. **Statewide news:** add 1 to 3 key state-level stories to the state file.
6. Set `checked.news` to today, run validate.py, finish per CONVENTIONS.md.

## Output Format
```json
{"title": "Meta is investing $40B more to expand Richland Parish data center project", "outlet": "WWNO / WRKF", "url": "https://...", "date": "2026-07-14", "tone": "neutral"}
```

## Anti-Patterns
- Don't tag tone by headline alone (because headlines often overstate. Read the body.)
- Don't edit metrics or opposition from a news story (because those fields belong to other skills with stricter source rules; hand them off in the PR body).
- Don't keep items without a working URL (because the site links every item, and dead links erode trust).
