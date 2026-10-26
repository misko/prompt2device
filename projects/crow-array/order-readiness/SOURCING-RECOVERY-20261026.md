# Exact-part recovery — 26 October 2026

This OR3 supplement supersedes the **eight exception dispositions**, not the
historical observations, in SOURCING-20261026.md. Scope remains 5 carriers and
10 pods. No substitutions, supplier submissions, reservations or purchases.
No ordering receipt or engineering acceptance is issued.

## Result

Seven exceptions now have exact supplier availability evidence fetched directly
today. The eighth has a substantially newer positive opened-page observation
(four days old rather than four months). No demonstrated global shortage remains
in these eight identities. This is not confirmation of real-time stock for all
38 identities or of JLC assembly allocation.

| Exact MPN | Installed need | Supplier evidence | Disposition |
|---|---:|---|---|
| TPS70933DBVR | 10 | JLC C89347 exact Product: InStock | Availability supported; PCBA allocation unconfirmed |
| BZT52C3V9-7-F | 80 | JLC C154917 exact Product: InStock | Availability supported; PCBA allocation unconfirmed |
| GRM32ER71A476KE15L | 10 | JLC C84494 exact Product: InStock | Availability supported; PCBA allocation unconfirmed |
| GRM31MR71E225KA93L | 80 | LCSC C97962 exact Product: InStock, inventoryLevel 1,520 | Sufficient advertised supply; assembly route unconfirmed |
| BAT54S-7-F | 20 | LCSC C83574 exact Product: InStock, inventoryLevel 19,970 | Sufficient advertised supply; assembly route unconfirmed |
| RJHSE-5080 | 50 | JLC C599441 explicitly names hyphenated MPN, Amphenol ICC, InStock | Exact identity resolved without assuming a punctuation alias; manual-part route still open |
| C3216X7R1V106K160AC | 10 | Bürklin 75D7535 exact TDK Product: InStock; matching product data: 1,185 | Sufficient advertised supply; consignment/shipping unconfirmed |
| ERJ-3EKF68R0V | 5 | DigiKey P68.0HCT-ND exact Panasonic 0603: 64,642; opened rendition crawled four days ago | Strong positive availability evidence, not a live allocation check |

The first six records, exact URLs, maker/package fields, HTTP retrieval times,
response hashes and discovery responses are retained in
`code-stock-recovery-20261026.json`. TDK evidence is in `buerklin-20261026.json`.
Panasonic observation: opened 2026-10-26 approximately 15:37 UTC,
[exact DigiKey product](https://www.digikey.com/en/products/detail/panasonic-industry/ERJ-3EKF68R0V/1746805),
manufacturer/MPN/package in lines 974–1001 and target stock in line 1026 of the
browser rendition; not the substitute table above it. Direct raw DigiKey access
was denied, so no current raw-response hash or live-inventory claim is made.

The remaining 30 identities retain OR2 observations and their original cache-age
limitations in `supplier-observations-20261026.csv`. We have not refreshed those
30 again or converted them into reservations. Batch demand excludes assembler
loss allowances and feeder extras, which still require an exact-job quantity.

## What changed the outcome

JLCSearch MPN queries returned empty/unrelated results, but **catalog-code
queries** returned exact TPS70933DBVR, BZT52C3V9-7-F and BAT54S-7-F results.
Other code queries remained empty despite exact supplier offers. Therefore an
empty aggregate result cannot determine availability.

Raw supplier pages contain Product JSON-LD offers omitted by the previous
text extraction. The project helper matches exact MPN and catalog SKU, retains
maker identity for review, and excludes navigation/related-product stock.
The existing vNext parser is unchanged: its `availability_verified: false`
reflects its narrower field extraction, not a contradiction of the separately
retained exact-product offer. Neither extractor issues acceptance.

JLC Product InStock statements meet the existing design-availability policy
when no direct PCBA quantity is published. Overseas/presale quantities are
retained separately, not added together or represented as usable assembly stock.
Likewise JLCSearch counts remain discovery evidence, not supplier allocation.
LCSC and Bürklin inventory is not automatically JLC inventory. The report does
not resolve the prior supplier-reported Murata NRND observation or authorize a
part change; that remains a lifecycle note for procurement review.

## Publicly resolved manufacturing questions

- Both boards exceed JLC's published 50 × 50 mm minimum for precision profiling.
  Panel/tooling conditions and exact geometry still require review.
- JLC normally generates paste only for selected SMT components, excluding
  unselected/THT positions. Thus excluding the manual Pico and acoustic parts
  aligns with the normal population workflow. The release's restrictions on
  automatic aperture changes still need reconciliation with JLC optimization.
- JLC's ±0.05 mm press-fit service is a possible path for the 0.89 mm RJ contact
  holes, but its published diameter range does not cover the 3.25 mm pegs or
  Pico relief holes. It also does not establish the complete pitch/pose limits.

Sources checked today: [JLC capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)
and [stencil workflow](https://jlcpcb.com/help/article/smt-stencil-data-prepared-for-smt-orders).
These findings narrow questions; they do not waive frozen source controls.

## Remaining real ordering work

1. Resolve exact fabrication/process compatibility: finished holes, pitch and
   registration, placement/seating tolerances, paste review and inspection.
   Generic public capabilities do not promise these exact limits.
2. Select an executable SMT/manual completion route, including original Pico
   D1 removal and acoustic hand soldering. The public factory BOM/CPL files are
   still header-only; stocked catalog discoveries do not make them upload-ready.
3. Bind all exact identities to that route, including usable quantity, packaging,
   attrition, lead time and any consignment. Obtain an exact itemized quote and
   purchaser approval. No catalog check establishes an account allocation.

Recommended route: resolve process feasibility with one consolidated exact-job
inquiry, then finalize stock-versus-consignment mapping and production files.
Fallback: JLC fabrication/SMT plus a qualified manual assembler. If source
controls prove impractical, engineering must review their rationale and reissue
affected evidence rather than silently relaxing the sealed release.

The inquiry is prepared but **not sent**. No physical qualification, firmware
validation, ordering hold or sealed acceptance was changed by this research.
