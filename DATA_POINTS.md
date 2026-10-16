# Every data point: why it's here, how we got it, how it stays fresh

Each line on the website exists because it answers a question a real person asks: a neighbor, a reporter, a council member, or a company. If a data point doesn't answer one of those questions, it doesn't belong.

Format for each data point:
- **Why (the hypothesis):** the question it answers, and what we believe it will show.
- **How we got it (first pass, Oct 2026):** where it actually came from.
- **Stays fresh by:** the skill (workflow) that owns it, and how often it runs.
- **How we'd know it's wrong:** the check that catches a bad value.

---

## 0. The list of sites itself

- **Why:** The core claim of the project is "every data center in these two states." If people find one we missed, trust drops. Hypothesis: most sites show up first in state economic development announcements or utility filings, months before local news.
- **How we got it:** Two research agents (one per state) searched, in order: state economic development and governor press releases; utility regulator dockets (Louisiana PSC, Mississippi PSC) for big power contracts; state environmental agencies' air permit notices for generators and turbines; parish and county agendas (rezonings, tax deals); then local and national news. A second Louisiana sweep added Moss Bluff and six leads. Anything with only one weak source became a lead, not a site.
- **Stays fresh by:** `odc-find-sites`, weekly per state. Also resolves open leads.
- **How we'd know it's wrong:** a reader or reporter names a site we don't have; a lead sits open for more than a month; two records describe the same project.

## 1. Basics: name, owner, place, stage, announced date, confidence

- **Why:** People search by place ("data center near me") and by company. Stage tells them if it's a rumor or a building. Confidence tells them how sure we are. Hypothesis: stage changes (announced to building, building to blocked) are the moments people care most.
- **How we got it:** Same sweep as above. Owner and stage from announcements and permits; county and town from rezoning and news.
- **Stays fresh by:** `odc-find-sites` (stage changes, weekly); `odc-verify` raises or lowers confidence (monthly).
- **Wrong if:** news reports a stage we don't show; a weak site never gets a second source.

## 2. Money invested

- **Why:** It's the number companies and officials lead with, and the base for every tax-break argument. Hypothesis: announced money grows over time (Meta went from $10B to $50B), so tracking changes shows how deals evolve.
- **How we got it:** State and company announcements. Tagged real.
- **Stays fresh by:** `odc-site-numbers`, monthly. Old values move to notes, not deleted.
- **Wrong if:** two official figures disagree, or a figure mixes phases.

## 3. Power (MW)

- **Why:** Power is the biggest local worry: will it raise my bill, will they build gas plants? Hypothesis: the bigger the MW, the more new power plants and regulator cases follow.
- **How we got it:** Company pages, utility filings, news. Missing for most Amazon sites.
- **Stays fresh by:** `odc-site-numbers` (monthly), `odc-state-policy` for the dockets behind it, `odc-outreach` when it's not public.
- **Wrong if:** the unit is unclear (MW vs MVA, phase 1 vs full campus). The skill puts the phase in the unit.

## 4. Water use and cooling type

- **Why:** Water is the second biggest worry, especially near farms and small towns. Hypothesis: most new sites claim closed-loop or "no water" cooling, but few publish measured use; the gap between claim and number is the story.
- **How we got it:** Company statements, water contracts in council minutes, news. Mostly company claims; Meta's numbers came via a newspaper.
- **Stays fresh by:** `odc-site-numbers` (monthly), `odc-outreach` (records requests to the water utility).
- **Wrong if:** a claim is shown as a measured number. Claims stay text and say "company claim."

## 5. Power source and power company

- **Why:** Tells people who will pay for new plants and whose rates could move. It's also needed for the before-and-after power bill comparison. Hypothesis: most sites run on new gas plants built by the local utility, paid partly through rates.
- **How we got it:** Utility filings and announcements.
- **Stays fresh by:** `odc-site-numbers` (monthly), `odc-state-policy` (utilities and service areas, yearly).
- **Wrong if:** the utility named doesn't serve that area.

## 6. Land (acres) and exact location

- **Why:** Size of the footprint and exactly where it sits next to homes and schools (the Vicksburg site sits next to an elementary school). Hypothesis: distance to homes predicts how much pushback there is.
- **How we got it:** Rezoning applications, company site pages. Most pins are still approximate (town center).
- **Stays fresh by:** `odc-site-numbers` (monthly; exact coordinates only from permits or official maps).
- **Wrong if:** a pin is shown as exact without an official source.

## 7. Jobs: building jobs promised, long-term jobs promised, jobs so far

- **Why:** Jobs are the main promise used to win approval. Hypothesis: long-term jobs are small (hundreds) next to building jobs (thousands), and promised vs real is where trust breaks.
- **How we got it:** Incentive announcements (promised); company statements and state reports (so far). "So far" is missing almost everywhere.
- **Stays fresh by:** `odc-site-numbers` (monthly), `odc-outreach` (records requests for state job reports).
- **Wrong if:** a construction headcount is shown as permanent jobs.

## 8. Tax break and local tax paid

- **Why:** Tax breaks are the trade the public makes. Local tax paid is what the town actually gets (the Louisiana teacher checks came from sales tax). Hypothesis: break sizes are rarely published, while local taxes paid spike during construction and drop after.
- **How we got it:** Law terms (Louisiana Act 730, Mississippi incentive laws), PILOT deals in news. Dollar sizes almost never public. Local tax paid mostly missing.
- **Stays fresh by:** `odc-site-numbers` (monthly), `odc-state-policy` (incentive laws), `odc-outreach` (records requests to assessors, school boards, economic development agencies).
- **Wrong if:** an estimate of a tax break is shown as official.

## 9. Deal with the town (community deal)

- **Why:** Shows what the company promised the town besides taxes: roads, schools, scholarships. Hypothesis: promises are vague and rarely tracked to delivery.
- **How we got it:** Company commitments pages, council resolutions.
- **Stays fresh by:** `odc-site-numbers` (monthly), `odc-outreach` (asks what's been delivered).
- **Wrong if:** a promise is shown as delivered.

## 10. What the company says (official statements)

- **Why:** Fairness. The company's own words sit next to the critics'. Hypothesis: showing both sides makes the site trusted by both.
- **How we got it:** Company newsrooms, press releases, testimony.
- **Stays fresh by:** `odc-site-numbers` (monthly).
- **Wrong if:** a quote isn't from the company itself.

## 11. Company openness checklist (8 items) and score

- **Why:** The project's signature. It turns "they won't tell us" into a fair, comparable score, and gives companies a reason to share. Hypothesis: once scores are public, some companies will send data to raise theirs.
- **How we got it:** So far only from what companies published ("partly" where it's partial). Nothing is "hidden" yet, because nothing has been asked.
- **Stays fresh by:** `odc-outreach` (drafts requests, logs sends, marks "hidden" after a deadline passes, updates on replies). Runs when replies or deadlines arrive, and weekly for deadline checks.
- **Wrong if:** an item is "hidden" with no logged request. The checker blocks this.

## 12. Pushback (opposition) and other scrutiny

- **Why:** Shows where people are fighting and how. Hypothesis: pushback clusters around power plants, generators and school-adjacent sites, and it predicts pauses and cancellations.
- **How we got it:** Court filings, petitions, permit appeals, council minutes, news. A cleanup moved 24 items that weren't real opposition (donations, reports, approvals) into "scrutiny."
- **Stays fresh by:** `odc-pushback`, weekly. Follows court cases to their outcome.
- **Wrong if:** a vote for the project or a news story is counted as opposition.

## 13. News feed

- **Why:** One place for every story about a site, tagged good, bad or neutral. Hypothesis: news tone over time shows how a town's mood shifts.
- **How we got it:** Research agents collected 5 to 15 stories per big site.
- **Stays fresh by:** `odc-news`, weekly.
- **Wrong if:** dead links, duplicates, or tone tagged from the headline only.

## 14. Where to ask for records (contacts)

- **Why:** Lets anyone, not just us, request the hidden numbers. Hypothesis: making the request path public multiplies the pressure.
- **How we got it:** Government sites; some phone numbers from directories (marked "confirm before use").
- **Stays fresh by:** `odc-outreach`, every 3 months.
- **Wrong if:** a number or address bounces.

## 15. Before and after (not built yet)

- **Why:** Answers the biggest question with evidence: did power bills, rent, home prices and wages change faster here than in a similar town without a data center? Hypothesis: rent and home prices rise during construction; power-bill effects show up statewide through rate cases, not county by county.
- **How we'll get it:** HUD rents, Census survey, Zillow, BLS county wages, federal energy office utility prices, state sales tax reports, compared with a look-alike county.
- **Stays fresh by:** `odc-before-after`, every 3 months.
- **Wrong if:** two counties on the same power company are compared on bills (same state-set rate), or the text says the data center caused a change.

## 16. Statewide picture (state pages)

- **Why:** Many answers live at the state level: tax-break laws, bills, utility cases, rate cases, local pauses, ballot votes, polls, who serves which area. Hypothesis: state rules decide where sites land (Louisiana's tax break, Mississippi's special sessions).
- **How we got it:** Two research agents, one per state (in progress).
- **Stays fresh by:** `odc-state-policy`: bills weekly during the legislative session, dockets and incentives monthly, local rules weekly, utilities yearly.
- **Wrong if:** a bill shown as law isn't signed; a docket number doesn't exist on the regulator's own site.

## 17. Scores bars on each card

- **Why:** Lets people compare sites at a glance, like Nomad List. Each bar is computed from the data above, never typed in by hand:
  - Data found = how many of the 13 numbers are public.
  - Company openness = the checklist score (gray until we've asked).
  - Local pushback = count of real opposition actions.
  - News coverage = number of stories.
  - Size = money invested.
- **Stays fresh by:** `odc-build-site` after every merge.

## 18. Local voices (not built yet)

- **Why:** The people living next to a site know things no record shows. Hypothesis: verified local comments are what make people come back and share the page.
- **How we'll get it:** Comments verified by phone number and ZIP code. Needs a small backend; not built.
- **Stays fresh by:** people, plus a moderation routine (to be designed).

---

## Routine plan

| Routine | Runs | What it does |
|---|---|---|
| Weekly sweep | Mondays | `odc-find-sites` (both states), `odc-news`, `odc-pushback`, `odc-state-policy` (bills, local rules) |
| Monthly refresh | 1st of the month | `odc-site-numbers`, `odc-state-policy` (dockets, incentives, rate cases, polls), `odc-verify` |
| Quarterly | Jan, Apr, Jul, Oct | `odc-before-after`, `odc-outreach` contact check |
| On demand | when replies arrive | `odc-outreach` (log reply, rescore) |
| After every merge | automatic | `odc-build-site` through Vercel |

Every routine starts with `python scripts/coverage.py`, does only the stale jobs, runs `python scripts/validate.py`, and opens a pull request for a human to approve.
