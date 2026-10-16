---
name: odc-build-site
version: 1.0.0
description: |
  Builds the public website from the data: the map home page, a page per state, per county and per site, plus sitemap and robots, then checks the output before deploy.
triggers:
  - "build the site"
  - "rebuild open data centers"
tools:
  - Bash (python site/build.py, python -m http.server, playwright screenshot)
  - Read
mutating: true
---

# Build site

Owns: `site/` (generator and templates) and `public/` (build output, not committed). Never edits data.

## Contract
- `python scripts/validate.py` passes before building; the build refuses to run otherwise.
- Every site, county with a site, and state gets its own HTML page with a unique title, description and canonical URL, and all key facts written into the HTML itself (readable without JavaScript).
- `public/sitemap.xml` lists every page; `public/robots.txt` points to it.
- The build finishes with zero broken internal links.

## Phases
1. Run `python scripts/validate.py`. Stop if it fails.
2. Run `python site/build.py`. It writes `public/`.
3. Check: `python site/build.py --check` (internal links, titles unique, sitemap count matches pages).
4. Look at the home page, one county page and one site page at desktop and phone width (local server plus a screenshot) once.
5. Deploys happen from the main branch through Vercel after a human merges. Don't deploy from a branch.

## Output Format
```
Built {n} pages (1 home, {s} states, {c} counties, {p} sites) -> public/
Sitemap: {n} urls. Broken links: 0.
```

## Anti-Patterns
- Don't build pages that only fill in with JavaScript (because search engines index the HTML, and the "[county] data center" search plan depends on it).
- Don't commit `public/` (because Vercel builds it, and committed build output drifts from the data).
- Don't include the private backup design or outreach drafts in `public/` (because the owner asked to keep them private).
