# What the national sweeps still miss

Three national sweeps ran on 2026-10-15 (pass 1: 655 sites; pass 2: 826; pass 3: 921 sites, 434 open leads, 391 exact pins). Pass 3 went company by company (colocation 10-Ks and location pages, crypto miners' SEC filings, Google/Meta/Microsoft location lists) and filled policy sections for 18 states.

## Still open after pass 3
- **Pins:** 530 sites have no exact pin. Best sources found: EPA ECHO facility records, state air-permit databases (Maricopa, Nevada, Utah, Virginia DEQ), Texas TDLR building filings, Georgia DRI filings. Pins that rest only on an LLC name were left off on purpose.
- **Company lists not yet checked:** Apple, Oracle, xAI, OpenAI/Stargate, Anthropic, CoreWeave, Nebius, Fluidstack, Poolside, Amazon state by state; Iron Mountain, NTT, EdgeConneX, T5, 365, DataBank colocation.
- **Crypto without counties:** CleanSpark's 7 Exponential Digital Tennessee sites and 5 Georgia LN Energy sites; Cipher's Mikeska, McLennan, Milsing; Soluna's other sites.
- **Centersquare records** were added on "utility power 20 MW+" with county from town name only; confirm addresses.
- **Possible overlaps:** MARA Hannibal vs Bitdeer Clarington (OH); CyrusOne Sulphur Springs lead vs MSB Sulphur Springs (TX); QTS Phoenix 4 lead vs Prime Avondale (AZ); CyrusOne Carrollton county (Dallas vs Denton); Rubix AK Steel county (Greenup vs Boyd).

The lists below are from before pass 3; some lines are now done. Both shared one session's web search limit, which kept running out. **An empty section means "not checked", not "nothing exists".** Run `odc-find-sites` on these in a fresh session (or when search is available), one region per agent, and delete a line when it's done.

## Sites still not swept
- **Running colocation over 20 MW** (company pages blocked or no MW published): Equinix and Digital Realty in Atlanta, Dallas, Houston, Chicago, NY/NJ, Miami, Silicon Valley, LA; CoreSite CH1/CH2, SV1/SV2; Flexential and DataBank in Charlotte, Raleigh, Nashville, Memphis, Louisville, Indianapolis, Detroit, Grand Rapids, Milwaukee, Minneapolis; H5 Cleveland; 365 Data Centers.
- **Crypto mines**: Colorado, Ohio (Standard Power Coshocton), Illinois (beyond Hut 8), Michigan, Wisconsin, Florida, Maryland, Arkansas, Kentucky (beyond Calvert City/Paducah/Murray), New Mexico, Arizona, North Dakota and Wyoming (beyond those recorded); CleanSpark's 10 Tennessee sites (named in SEC filings, counties unknown).
- **AWS running campuses** in Loudoun and Prince William (no public campus list) and COPT's 33 cloud shells.
- **Arizona**: Yuma, Mohave, Yavapai, Cochise; Pima County pause; Phoenix ordinances.
- **Texas**: Digital Realty Houston/Dallas, Switch/Data Foundry Houston, Soluna's other sites.
- **Oregon**: Google's second The Dalles campus, Apple Prineville expansion, Morrow County and Cascade Locks rules.
- **Washington**: Microsoft campuses beyond Quincy, East Wenatchee and Malaga, if any.
- **Ohio**: the "$1 billion data center that fell apart" (Mahoning Matters, 2026-09-28).
- **Georgia**: Switch Douglas County stage, Microsoft Palmetto stage, Hampton overlap (Henry County parcel check).

## Statewide sections still empty
- Utility dockets: KY (beyond 2), TN (TVA), DC, CT, RI, VT, NH, NC (separate large-load docket?), SC (Duke settlement number), ND, SD (incentives), WV (Appalachian Power case number).
- Incentives: NY section number, NH, VT, RI, MT, SD, DE, AK, HI.
- Bills: Nevada 2025 session, DC Council, Kansas since SB 98.
- Rate cases and utilities: most states.

## Records to settle
- Possible duplicates: Hampton GA (3 records), Geronimo vs Wildwood Ranch (MO), Conway vs Google Little Rock (AR), Smoaks overlay vs Eagle Rock Rhodes (SC), Amazon Quarry vs Willard Road and STACK NVA05 vs NVA02 (VA), Big Watt Taylor vs Project Comal (TX), AboutBit vs Fluidstack Merom (IN).
- Bundled records to split if addresses turn up: Microsoft Catawba (NC), CyrusOne Sterling (VA), AWS Morrow/Umatilla (OR), CleanSpark Dalton and Cheyenne, Google Dorchester (SC), King of Prussia (PA).
- Stages that are guesses: QTS PHX2, STACK, Compass, Novva and NTT in Arizona; STACK NVA04/06, Vantage II/III, Microsoft Arcola in Virginia; Cipher Black Pearl and Barber Lake (TX, may be running).

## Rules that apply on every rerun
- Trackers point to candidates; they are never the source.
- Same owner and same county is probably the same campus: check before adding.
- Every lead needs a source URL (validate.py rejects it otherwise).
- Parallel agents: each uses its own scratchpad subfolder, and **never runs scripts/merge_patches.py**. Only the lead merges, and uses `--upsert` when agents re-send sites an earlier merge already took in.
