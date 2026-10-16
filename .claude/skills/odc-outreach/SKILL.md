---
name: odc-outreach
version: 1.0.0
description: |
  Finds the right offices and contacts for each data center, drafts public records requests and company transparency requests, logs what was sent, and updates the openness checklist when replies or deadlines arrive.
triggers:
  - "draft records requests for {site}"
  - "log a reply from {office}"
  - "check request deadlines"
tools:
  - WebSearch, WebFetch
  - Read, Write, Edit, Bash (validate.py, coverage.py)
  - mcp__claude_ai_Gmail__create_draft (drafts only; never send)
mutating: true
---

# Outreach

Owns: `contacts` and `transparency` on site records (plus `transparency_sources` for evidence from replies), `outreach/log.csv`, and `outreach/drafts/` (private, gitignored). Sets `checked.contacts` and `checked.transparency`.

## Contract
- Nothing is ever sent by an agent. Drafts go to `outreach/drafts/{site_id}.md` (and Gmail drafts when a sender is configured). A human sends and confirms.
- `log.csv` gets a row only after the human confirms a send, with the legal deadline from the state's `records_law` in `data/states/registry.json` (Louisiana 3 business days, Mississippi 7 working days), and 21 days for companies.
- A transparency item becomes `hidden` only when its logged request was refused or passed its deadline with no answer. Replies with the data make it `shared` or `partly`, with the reply as evidence.
- Every contact has a source; directory-site phone numbers are marked "confirm before use".

## Phases
1. **Read** `outreach/PLAYBOOK.md` and `outreach/templates.md`.
2. **Contacts:** for each target site, find the offices that hold the missing items (assessor, permits or planning, school board, industrial development board, state economic development, utility regulator docket, environmental agency, water utility) and the company's community-relations route.
3. **Draft** one request per office (the state's template in `outreach/templates.md`, citing the registry's `records_law`) and one company request (template C), narrow and dated, existing records only. Check the regulator docket and permit search first; don't request what's already public.
4. **Stop** and list the drafts for the human. Do not send.
5. **When told a request was sent:** add the log row with the deadline.
6. **Deadline check:** for each open log row past its deadline, draft a follow-up (template D) and, for company requests, mark the asked items `hidden`.
7. **Replies:** put new numbers into `metrics` (as `real`, with the document as source, coordinating with `odc-site-numbers` in the PR body), update `transparency`, close the log row.
8. Set `checked.contacts`/`checked.transparency`, run validate.py, finish per CONVENTIONS.md.

## Output Format
`outreach/log.csv` row:
```
2026-10-20,la-richland-meta-hyperion,Richland Parish School Board,records-LA,"monthly sales tax 2022-now; 13th check amounts",2026-10-23,open,,,,outreach/drafts/la-richland-meta-hyperion.md
```

## Anti-Patterns
- Don't send, or fill in a sender identity the owner hasn't confirmed (because sending is on the owner's confirm-first list, and a request signed wrong can be ignored).
- Don't mark `hidden` from a missing web page (because "hidden" means "we asked and they didn't share", and a wrong label invites a complaint).
- Don't commit drafts or log rows that contain the sender's personal phone or address (because the repo is public). Keep those in the gitignored drafts folder.
