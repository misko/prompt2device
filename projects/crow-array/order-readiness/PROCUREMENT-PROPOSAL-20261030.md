# Consolidated procurement proposal — 5 carriers + 10 pods

Prepared 2026-10-30 PDT under local vNext. **Proposal only; no purchases or
manufacturing submissions authorized.** No engineering change or replacement
part is proposed. This covers the complete batch's procurement ownership, not
a fully priced turnkey order. The sealed release remains DO-NOT-ORDER.

## Reviewed evidence and recommendation

Verified remote branch `codex/crow-jlc-source-review-20261030` at
`b39eb5a45cad93410c6e01a9b09eaf7d69e39a83`, then fast-forwarded the clean local
branch. The commit adds only `JLC-PRICING-20261030.md`, its JSON and STATUS.
The pricing rows match all seven shortage identities, C-codes and installed
quantities in the earlier browser evidence. Their five regular line estimates
sum correctly to $74.78. RECOM's new explicit unavailability supersedes the
earlier ordinary replenishment assumption despite a displayed catalog price.

Preferred: **28 existing JLC catalog identities + five regular replenishment
identities + two Global Sourcing identities** for JLC installation. Separately
procure the three user-installed identities. Keep the unchanged exact parts and
approved JLC/user installation split. The complete 38-row draft is
`procurement-proposal-20261030.csv`; it is a decision worksheet, **not an upload
BOM or purchase order**. Blank prices/quantities mean unquoted, never zero.

OR9 observations are signed-in browser transcriptions, without screenshots or
raw payloads; some searches overlapped loading. They support candidate routes,
not independently verified allocations or an exhaustive cheapest-offer ranking.
Global supplier stock is not JLC-ready stock. Browser report validations ran
against its earlier base; this proposal is checked against the fetched commit.

## Seven priced recovery lines

Carrier/pod columns are installed batch need. Planned query quantities below
are provisional before factory-required attrition and packing for each board job.

| Exact MPN / C-code | Carrier / pod need | Proposed source | Provisional qty | Indicative USD | Observed lead time |
|---|---:|---|---:|---:|---|
| CB3LV-3I-12M288000 / C17275161 | 5 / 0 | JLC regular replenishment | 5 | 13.23 | Unknown |
| 1206L010/30WR / C2153988 | 40 / 10 | JLC regular replenishment | 50 | 34.21 | Unknown |
| GRM21BR71A105KA01L / C97917 | 10 / 10 | JLC regular replenishment | 407 | 9.04 | Unknown |
| C2012X7R1V225K125AE / C2167593 | 0 / 10 | JLC regular replenishment | 62 | 9.14 | Unknown |
| C3216X7R1V106K160AC / C2182140 | 10 / 0 | JLC regular replenishment | 14 | 9.16 | Unknown |
| R-78E5.0-0.5 / C5199916 | 5 / 0 | JLC Global Sourcing → Sager | 10 | 48.05 | Displayed 10–16 business days |
| PCM1864DBT / C2863172 | 10 / 0 | JLC Global Sourcing → DigiKey, tube | 10 | 104.88 | Displayed 8–14 business days |
| **Seven-line component subtotal** | **85 / 25** | | **558** | **227.71** | **No confirmed batch arrival date** |

Of 558 provisionally purchased pieces, 110 are installed and 448 are nominal
surplus before attrition: 387 Murata capacitors, 52 TDK 0805 capacitors, four TDK
1206 capacitors and five RECOM modules. This is not an approved spare purchase
or a promise of loose delivery. Shared carrier/pod parts must cover both jobs;
do not combine incompatible regular/global/consignment pools for one part.

The five regular lines total $74.78; two global lines total $152.93. Use displayed
line totals rather than rerounding prices inconsistently. No credits are taken
for unallocated public-stock fuses. Displayed global attrition/minimum-assembly
fields on alternative offers are not accepted quantities for the selected
regular offers or both jobs.

Sources: [pushed pricing report](https://github.com/misko/prompt2device/blob/b39eb5a45cad93410c6e01a9b09eaf7d69e39a83/projects/crow-array/order-readiness/JLC-PRICING-20261030.md)
and [observations](https://github.com/misko/prompt2device/blob/b39eb5a45cad93410c6e01a9b09eaf7d69e39a83/projects/crow-array/order-readiness/JLC-PRICING-20261030.json).
The displayed business-day ranges have an unconfirmed endpoint; do not convert
them to promised warehouse dates, add them together, or call 16 days the batch
lead time while the regular lines have no dates.

## Rest of the batch and assembly ownership

| Procurement/installation group | Exact identities | Installed pieces | Price status |
|---|---:|---:|---|
| Existing JLC catalog candidates | 28 | 865 | Not priced by OR9; retain OR6 dated availability |
| Five regular recovery lines above | 5 | 95 | $74.78 indicative, not quoted |
| Two global recovery lines above | 2 | 15 | $152.93 indicative, not quoted |
| External parts for user installation | 3 | 25 | Not priced by OR9 |
| **Total installed scope** | **38** | **1,000** | **Whole-batch total unknown** |

JLC requested installation: **915 SMT + 60 manual parts** (50 RJHSE-5080,
five PJ-102AH, five RECOM modules). User installs **five SC0915 Picos, ten
CMA-4544PF-W microphones and ten CPE-203 buzzers**. User ownership does not
establish that these parts are already on hand; purchase quantities depend on
inventory confirmation. Preserve protected acoustic hand-soldering and Pico
D1-only preparation/inspection. Do not assign rejected JLC operations to the
user without a new decision. Pico-fit risk was already accepted; do not reopen
that investigation without new evidence.

Among the 28 catalog candidates, Panasonic ERJ-3EKF68R0V versus ERJ3EKF68R0V and
Same Sky PJ-102AH versus historical CUI are the two OR7 source-supported naming
reconciliations. They are draft matches, not blanket normalization or a new
vendor approval. The original 26/7/2 browser classification is preserved.

The complete cost proposal must still itemize: remaining 28 JLC identities;
three user-installed identities; attrition/minima/packing extras; five carrier
and ten pod bare boards; setup/stencils; SMT and manual assembly; sourcing/import
fees; shipping and taxes. No enclosure, roof supports, host Pi, PSU or deployment
cables are priced here. $227.71 is neither the full build cost nor a spending cap.
Historical release cost ranges are not promoted into a current quotation.

## Ranked alternatives

1. **Preferred — JLC-managed route above.** Avoids customer consignment logistics
   and keeps factory supply together. It requires actual selected-offer fees,
   usable-stock timing, intake quantities and process/matching acceptance.
2. **Fallback — exact external sourcing/consignment for failed or impractical
   lines only.** Retain OR8 DigiKey/Bürklin leads, but refresh those exact offers
   if this route is selected. Destination shipping, applicable JLC consignment
   charges and packing must be quoted before comparison. This is not assumed
   faster or cheaper. Do not silently replace DBT with DBTR.

CTS Global Sourcing at $10.69 would save only $2.54 versus its regular estimate;
keep regular provisionally unless its actual date/process makes global better.
The observed global capacitor offers are substantially above the regular line
totals. Do not choose them merely to reduce surplus. The second exact ADC lead,
TI direct at $109.26, remains a fallback, not evidence DigiKey stock is reserved.
No new public stock pass was performed for this evidence-consolidation task.

## What happens next — one integrated job review, no repeat stock loop

This proposal selects a preferred path; it does not satisfy order admission.
The next discriminating artifact is an **itemized exact-job quote and matching/
process review for both boards**, not another seven-line research report.

1. Prepare reviewed carrier/pod vendor drafts outside the immutable release,
   binding the 38-row worksheet to actual refs/footprints and the 60/25 ownership
   split. Existing factory BOM exports are empty and are not ready to upload.
   Keep manual parts out of machine CPL; preserve user-installation paste/hole
   exclusions. These vendor drafts are subsequent work, not produced here.
2. Collect in one job review the remaining pricing, required quantities and
   packing, exact matches/placement previews, compatible CTS SMD installation,
   RECOM manual installation and ADC tube handling, plus usable-stock timing.
   Preserve the release's stencil, stack/rails/DFM, mechanical and controlled-
   assembly requirements. If a requirement conflicts with JLC's standard flow,
   return a focused process/engineering decision rather than assume a waiver.
3. Stop before any new external action: the current authority covers a proposal,
   not BOM upload, vendor submission/contact, cart changes, reservation or payment.
   If quote discovery requires these, obtain scoped authority for the specific
   action; no payment just to discover a final price. If the full scope cannot
   be confirmed prepayment, expose that residual commitment risk explicitly.
4. Present one complete cost/scope proposal for approval. Procurement and later
   board manufacture are distinct commitments. After any separately authorized
   parts order, verify usable inventory before relying on it for PCBA.

All nine sealed ordering holds remain historical open records. Later user
decisions settle installation ownership and the discussed Pico-fit risk, but
do not establish supplier execution or rewrite independent engineering evidence.
The live proposal narrows the next work; it does not claim stock, manufacturing,
firmware or physical qualification acceptance.

## Validation boundary

Deterministic tests bind all 38 rows to the source worksheet and all seven price
rows to OR9, check board-split arithmetic, exact identities, ownership, missing
price semantics, RECOM/ADC routing and the $227.71 subtotal. Publication checks
protect the 256 immutable payloads. These checks do not verify supplier statements
or act as independent engineering admission. Publication authorized 2026-10-31
on `codex/crow-jlc-source-review-20261030`; see `MACBOOK-QUOTE-HANDOFF.md` for
the next bounded task. Main and the sealed release are not changed.

Results: 15 publication tests and 22 order-readiness tests pass (37 total),
including four proposal-accounting tests. Preservation passes for 256 payloads;
both OR6 browser and OR9 pricing evidence pairs are byte-identical to b39eb5a4.
