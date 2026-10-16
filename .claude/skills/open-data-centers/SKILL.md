---
name: open-data-centers
version: 2.0.0
description: |
  Routes Open Data Centers work to the right skill. Reads the coverage report, picks the most urgent jobs, and hands each to the skill that owns that kind of data.
triggers:
  - "update open data centers"
  - "what's missing on open data centers"
  - "run the data center routine"
tools:
  - Bash (python scripts/coverage.py, scripts/validate.py)
  - Skill (odc-* skills)
  - Agent (parallel runs of independent skills)
mutating: true
---

# Open Data Centers (router)

> **Router note:** this skill does no research itself. It picks jobs and delegates.
> Skills: `odc-add-state` (new states), `odc-find-sites`, `odc-site-numbers`, `odc-news`, `odc-pushback`, `odc-before-after`, `odc-state-policy`, `odc-outreach`, `odc-verify`, `odc-build-site`.

## Contract
- Every run starts from `python scripts/coverage.py --json`, never from memory.
- Jobs go to the skill named in the report, highest priority first.
- Skills that touch different fields run in parallel. Two skills never edit the same field at the same time.
- The run ends with `scripts/validate.py` passing and one PR per skill.

## Phases
1. **Read** `MISSION.md` and `.claude/skills/CONVENTIONS.md`.
2. **Plan.** Read `data/SECOND_PASS.md` (gaps left by the first national sweep) and give those to `odc-find-sites` first, one or two states per run. Run `python scripts/coverage.py --json`. Group the jobs by skill. Take every P1 job, then P2 jobs up to about 10 per skill per run.
3. **New state?** If the person asks to cover a new state, run `odc-add-state` and stop here.
4. **Delegate.** For each skill with jobs, run it with the list of targets: in a routine, one Agent per skill in parallel, each writing a patch file to `data/_incoming/`; interactively, the Skill tool. `odc-build-site` runs last, after the others merge.
5. **Merge and verify.** Run `python scripts/merge_patches.py`, then `python scripts/validate.py`. If it fails, send the failing records back to the skill that owns them.
6. **Report** using the format in CONVENTIONS.md, one block per skill.

## Output Format
```
Open Data Centers run, {date}
Jobs at start: {n}. Jobs done: {n}. Jobs left: {n}.
{per-skill report blocks}
Needs a human: {drafts to send, doubts to resolve}
```

## Anti-Patterns
- Don't research inside the router (because the specialist skills hold the source rules for each data type, and the router doesn't).
- Don't run two skills on the same file section at once (because the second write silently drops the first one's changes).
- Don't call a run done while validate.py fails (because CI blocks the PR anyway, and a red PR wastes the reviewer's time).
