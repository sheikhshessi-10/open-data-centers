---
name: odc-before-after
version: 1.0.0
description: |
  Builds the before-and-after view for a data center county: home power price, rent, home values, wages, jobs and sales tax from two years before the announcement to now, side by side with a look-alike comparison county without a data center.
triggers:
  - "before and after for {site}"
  - "quarterly cost of living run"
tools:
  - WebSearch, WebFetch, Bash (python for CSV/API pulls)
  - Read, Edit, Bash (validate.py, coverage.py)
mutating: true
---

# Before and after

Owns: `before_after` on site records. Sets `checked.before_after`.

## Contract
- Every series has yearly (or monthly) points with source and date, for both the site county and the comparison county.
- The comparison county is chosen by a stated rule (same state, similar population, similar median income, no data center, not adjacent if possible) and the reason is written down.
- Power bills are compared across counties only when the two counties buy home power from different companies. Otherwise the series tracks that one company's rate changes and the rate cases tied to data centers.
- Text never says the data center caused a change.

## Phases
1. **Targets** from `python scripts/coverage.py --skill odc-before-after`. One record per county is enough; sites in the same county share the result (copy it to each).
2. **Pick the comparison county** using Census population and median household income (ACS 5-year). Write `comparison_county` and `comparison_reason`.
3. **Find each county's home power company** from `data/states/{st}.json` `utilities` or the utility's service map.
4. **Pull series**, from the announcement year minus 2 to the latest:
   - Home power price: EIA-861 utility data (average residential cents per kWh), plus state regulator rate filings.
   - Rent: HUD Fair Market Rents (county), ACS median gross rent; Zillow ZORI where a county series exists.
   - Home values: ACS median home value; Zillow ZHVI county series.
   - Wages and jobs: BLS QCEW county average weekly wage and employment.
   - Sales tax: state revenue department reports by parish or county, or the school board's reports.
5. **Write** to `before_after`, set `checked.before_after`, run validate.py, finish per CONVENTIONS.md.

## Output Format
```json
"before_after": {
  "comparison_county": "Franklin Parish",
  "comparison_reason": "Same region, population 19k vs 20k, income within 8%, no data center",
  "power_company": {"site": "Entergy Louisiana", "comparison": "Entergy Louisiana", "compare_bills": false},
  "series": {
    "rent_fmr_2br": {"unit": "USD/month", "site": {"2022": 690, "2026": 760}, "comparison": {"2022": 680, "2026": 715}, "source": "https://www.huduser.gov/...", "date": "2026-10-01", "kind": "real"}
  }
}
```

## Anti-Patterns
- Don't compare power bills between two counties served by the same company (because they pay the same state-set rate, so any gap is noise, not evidence).
- Don't use a neighboring county as the comparison if workers commute in for construction (because the boom spills over and hides the difference).
- Don't round or smooth the series (because readers check the numbers against the source).
