---
name: odc-pushback
version: 1.0.0
description: |
  Tracks organized local pushback against each data center (lawsuits, petitions, permit appeals, votes against, organized groups, pauses) and keeps other scrutiny separate.
triggers:
  - "check pushback for {site}"
  - "weekly pushback run"
tools:
  - WebSearch, WebFetch
  - Read, Edit, Bash (validate.py, coverage.py)
mutating: true
---

# Pushback

Owns: `opposition` and `scrutiny` on site records. Sets `checked.opposition`.

## Contract
- `opposition` holds only actions: a lawsuit or legal filing, a petition with a count, a permit appeal, a council or board vote against, a named organized group's action, a push for a pause or ban, a protest with a size.
- Everything else critical (advocacy reports, audits, donations, expert concerns, one official's comment, letters to the editor) goes in `scrutiny`.
- Each entry names who did what, when, and the outcome if known, with source and date.
- Court cases are followed to their latest status, with each step as its own dated entry.

## Phases
1. **Targets** from `python scripts/coverage.py --skill odc-pushback`.
2. **Search** for each site: lawsuits (court records, PACER news, state court news), petitions (Change.org and local coverage), permit appeals and hearings (the state environment agency in `data/states/registry.json`), council and supervisor minutes, protests, and named groups (NAACP, SELC, Earthjustice, local coalitions).
3. **Classify** each find: opposition or scrutiny. When in doubt, scrutiny.
4. **Follow up** on open cases from earlier entries: ruling, appeal, settlement, dismissal.
5. Set `checked.opposition` to today, run validate.py, finish per CONVENTIONS.md.

## Output Format
```json
{"what": "NAACP, represented by SELC and Earthjustice, sued xAI and MZX Tech in U.S. District Court (N.D. Miss.) under the Clean Air Act. Status: pending.", "source": "https://...", "date": "2026-06-12"}
```

## Anti-Patterns
- Don't count news coverage of a protest as a second protest (because the pushback bar would double-count; one event is one entry).
- Don't put a political donation or an advocacy report in `opposition` (because a reviewer caught exactly this in the first build, and it inflates the pushback bar for a company that wasn't actually opposed).
- Don't describe residents by name unless they spoke publicly on the record (because private people deserve care, and this record is public).
