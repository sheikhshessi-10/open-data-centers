---
name: odc-verify
version: 1.0.0
description: |
  Audits the record: opens sources to confirm they still say what the data claims, flags dead links, checks low-confidence sites, and catches wrong categories, before anything misleading goes public.
triggers:
  - "verify the data"
  - "check sources"
  - "monthly audit"
tools:
  - WebFetch, WebSearch, Bash (python link checks)
  - Read, Edit, Bash (validate.py, coverage.py)
mutating: true
---

# Verify

Owns: fixes to any field when its source is wrong or dead (only the minimum fix), `confidence`, and the audit section of the PR body. Does not add new facts.

## Contract
- Every run samples at least 20 values at random, plus every value changed since the last audit, plus every `confidence: low` site.
- For each sampled value: the source loads, and it states the value, unit and date in the record. Mismatches are fixed or the value set to null with a note.
- Dead links are replaced with an archived copy (web.archive.org) when one exists.
- `opposition` entries that aren't real opposition move to `scrutiny`.

## Phases
1. **Sample:** run `python scripts/coverage.py --skill odc-verify` and draw the sample (python `random.sample` over all metric values, seeded with today's date so reruns match).
2. **Check links:** HEAD/GET every URL in the sample; list failures.
3. **Check claims:** open each source and compare. Record: ok / mismatch / dead.
4. **Fix** mismatches minimally. Never "improve" a value beyond what the source says.
5. **Low-confidence sites:** search for a second good source. Raise confidence or keep it low.
6. **Category check:** scan `opposition` against the rule in CONVENTIONS.md.
7. Run validate.py, finish per CONVENTIONS.md, with the audit table in the PR body.

## Output Format
PR body audit table:
```
| record.field | result | note |
|---|---|---|
| ms-rankin-avaio-taurus.metrics.acres | mismatch | company 329, state release 175; kept company, noted both |
```

## Anti-Patterns
- Don't trust a page's summary snippet; open the page (because summaries got summit details wrong in early research).
- Don't delete a value just because its link died (because the claim may still be true); swap in an archived copy first.
- Don't add new facts during an audit (because audit PRs are reviewed for correctness, not new content; mixing them hides changes).
