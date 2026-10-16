# Outreach Playbook: how we get the numbers

Written 2026-10-13. Two routes. Use both for every site.

## Route 1: public records requests (strongest)

Government offices must answer by law. Companies don't have to. So ask the government for what it already holds about the data center.

| Ask | Who holds it | What we get |
|---|---|---|
| Tax break deal, PILOT / incentive contract, jobs promised | State economic development agency (Louisiana Economic Development, Mississippi Development Authority), parish/county industrial board | tax_break, jobs_promised, community_deal |
| Sales tax collected by month, before vs after | Parish/county sales tax collector, school board finance office | local_tax_paid, before/after |
| Property tax assessment | Parish assessor / county tax assessor | local_tax_paid |
| Zoning, site plan, noise study, traffic study | Parish/county planning and permits, council or board of supervisors minutes | noise_tests, acres, stage |
| Power contract, new power plants, who pays for grid upgrades | State utility regulator dockets (Louisiana PSC, Mississippi PSC). Usually already public online, so search the docket before requesting | power_mw, power_source, utility |
| Water supply contract, gallons per day | City/county water utility, water district, groundwater permits (state DEQ / water board) | water_use |
| Air permits for backup generators or gas turbines | Louisiana DEQ, Mississippi DEQ (permit search is public online) | air_permits, power_source |
| Any nondisclosure agreement with the company | Same offices above | Shows what's being hidden, and by whom |

**The laws:**
- **Louisiana Public Records Law, La. R.S. 44:1 and following.** Any adult (18+) can ask. The office must respond within **3 business days**. If it withholds a record, it must say in writing which exemption it's using (R.S. 44:32). The governor's office only answers Louisiana residents. Check the current text on legis.la.gov before citing deadlines.
- **Mississippi Public Records Act of 1983, Miss. Code Ann. § 25-61-1 and following.** Anyone can ask. The office must produce or deny in writing within **7 working days**, up to 14 for big requests (§ 25-61-5). It can charge fees, often paid up front (§ 25-61-7). If a company claims trade secrets, the release can take up to about 21 days while the company is notified.
- **Trade secret pushback is normal.** Google fought releasing its water use in The Dalles, Oregon, and lost: the city settled and released 2012-2021 water records. Microsoft dropped its trade-secret claim in Racine, Wisconsin. A "trade secret" label doesn't end a request. Log every denial and the exemption cited, because that feeds the transparency score.

## Route 2: ask the company directly (weaker, but needed for the score)

- Write to the site's community relations contact, the press office, or the data center's local page form.
- Ask for the same 8 transparency items.
- Give a clear deadline (21 days) and say their answer, or lack of one, will be shown publicly.
- **A transparency item only becomes "hidden" after we asked and logged it.** Before that it stays "not_asked." This is what makes the score fair and defensible.

## Rules

- **Drafts only.** Shessi sends every email himself. Never auto-send.
- Every request goes in `log.csv` the day it's sent: date, site id, who, route, what was asked, deadline, status, reply date, result.
- Sender: a real person's name and address. Records requests from a named person get handled faster than ones from an anonymous project.
- Ask for existing records only. Don't ask offices to make new reports. That's a legal reason to refuse.
- Keep requests narrow and dated, like "January 2023 to present". Broad requests get slowed down or charged fees.

## Blocked until Shessi decides

- Project name and sender email address (needed to sign and send).
- Mailing address for paper copies (optional).
