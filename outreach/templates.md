# Request templates

Fill `{braces}`. Keep each request to one office and one site.

---

## A. Louisiana public records request

Subject: Public Records Request under La. R.S. 44:1 et seq. ({SITE_NAME}, {PARISH})

Dear Records Custodian,

Under the Louisiana Public Records Law (La. R.S. 44:1 et seq.), I request copies of the following records held by {OFFICE}, covering {START_DATE} to the present:

1. {RECORD_1, e.g. "Any agreement, contract, or memorandum of understanding between {OFFICE} and {COMPANY} (or its affiliates, including {LLC_NAME}) about the data center at {LOCATION}."}
2. {RECORD_2, e.g. "Monthly sales and use tax collection totals for {PARISH}, January 2022 to present."}
3. {RECORD_3, e.g. "Any non-disclosure or confidentiality agreement signed with {COMPANY} or its affiliates."}

Electronic copies by email are preferred. If any record is withheld, please cite the specific exemption in writing as required by La. R.S. 44:32(D). If fees will exceed ${FEE_CAP}, please tell me before processing.

Thank you,
{SENDER_NAME}
{SENDER_EMAIL}
{SENDER_PHONE}

---

## B. Mississippi public records request

Subject: Public Records Request under Miss. Code Ann. § 25-61-1 et seq. ({SITE_NAME}, {COUNTY} County)

Dear Public Records Officer,

Under the Mississippi Public Records Act of 1983 (Miss. Code Ann. § 25-61-1 et seq.), I request copies of the following records held by {OFFICE}, covering {START_DATE} to the present:

1. {RECORD_1}
2. {RECORD_2}
3. {RECORD_3}

Electronic copies by email are preferred. Please send a cost estimate before processing if fees will exceed ${FEE_CAP}. If any record is denied, please state the reason and the legal basis in writing as required by § 25-61-5.

Thank you,
{SENDER_NAME}
{SENDER_EMAIL}
{SENDER_PHONE}

---

## Any other state's public records request

Use template A, and swap in that state's `records_law` from `data/states/registry.json`: the law's name, its cite, the response deadline and the deadline cite. Some states set no number of days ("promptly", "within a reasonable time"). Quote the law's own words and don't invent a number. Some states only let their own residents ask (for example Virginia, Tennessee, Kentucky, Arkansas, Alabama and Delaware). Check `who_can_ask` before sending.

## C. Company transparency request

Subject: Public data request for {SITE_NAME} ({COUNTY}, {STATE}): {PROJECT_NAME}

Hello {CONTACT_NAME or "Community Relations team"},

{PROJECT_NAME} is a public, neutral record of data centers in the United States. It shows local residents the facts about each site, from the company and from public records, side by side.

We use one checklist for every company and score how much each one shares. For {SITE_NAME}, could you share any of the following, or point to where it's already published?

1. Expected and current power use (MW)
2. Water use (gallons per day or year) and the water source
3. Where the site's power comes from
4. The size and terms of any tax incentive
5. Jobs promised (construction and permanent) and jobs filled to date
6. Noise studies or sound limits
7. Air permits for backup generators or on-site power
8. Any community benefit agreement or local commitments

We'll publish your answers with credit and a link, next to the public records. Items you choose not to share will be marked as not shared as of {DEADLINE_DATE}, and you can update them anytime.

Thank you,
{SENDER_NAME}
{PROJECT_NAME}, {PROJECT_URL}
{SENDER_EMAIL}

---

## D. Follow-up (after deadline passes)

Subject: Re: {ORIGINAL_SUBJECT}

Hello, following up on my request of {SENT_DATE}. {LA: "Under La. R.S. 44:32, a response was due within three business days." / MS: "Under Miss. Code Ann. § 25-61-5, a response was due within seven working days." / Company: "We'll publish the current status on {DATE}."} Could you share an update or expected date?

Thank you,
{SENDER_NAME}
