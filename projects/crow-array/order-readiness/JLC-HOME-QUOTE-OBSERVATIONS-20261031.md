# JLC home-install quote observation — 2026-10-31

Observed in the existing browser session approximately 09:40 PDT. Quote-only;
no purchases, reservations, parts-cart additions, substitutions, messages or
manufacturing commitments. Prices and availability are snapshots, not offers
to purchase or allocated inventory. The r3 packet was locally verified before
the pass; no new BOM or Gerber upload was performed.

## Assembly quantities

For the existing five-bare-carrier Economic draft, JLC offered two and five
assembled carriers. Two was selectable and the draft was left at **two
assembled/five bare**, not one; this is the smallest choice observed here,
not a claim that other channels cannot offer one. The pod draft retained
**eight assembled/ten bare**, Standard, with prior proposed JLC rails still
conditional. No extra quantities are purchase- or build-approved.

At two carriers plus eight pods the per-board BOM implies 478 JLC SMT
placements: 254 carrier and 224 pod. Finishing only one carrier and eight pods
at home requires the 35 parts in the r3 A scenario; finishing both carriers
requires 46, assuming no existing home inventory or spares. Extra fabricated
boards remain unassembled. Five plus eight requires 859 SMT placements; 35
home parts finish one carrier and eight pods, or 79 finish all five carriers
and eight pods. These are scope calculations, not procurement quantities.

The carrier form showed $37.40 for the two-assembly setting: $25 engineering
and $12.40 board; component and assembly lines were dashes. The same draft
previously showed $38.60 with five assemblies, likewise without components
or assembly charges. Portal defaults, dimensions including tooling, stack,
stencil and process remain unaccepted. Neither figure is a complete PCBA quote.
Shipping shown separately for the two-carrier screen was $26.94 UPS estimate;
it is not a combined shipment quote. Do not compare or sum these incomplete
amounts as an all-in order.

## Two-carrier draft shortages

After selecting two, the carrier SMT matching screen showed five shortfall
lines. Quantities shown are JLC screen quantities, not final purchase needs:

| Exact MPN | JLC displayed required | Screen shortfall | Displayed stock |
|---|---:|---:|---:|
| C3216X7R1V106K160AC | 4 | 4 | 0 |
| GRM21BR71A105KA01L | 20 | 20 | 0 |
| 1206L010/30WR | 18 | 11 | 7 |
| PCM1864DBT | 4 | 4 | 0 |
| CB3LV-3I-12M288000 | 2 | 2 | 0 |

The previously inspected eight-pod screen showed TDK C2012X7R1V225K125AE
short 10, Murata GRM21BR71A105KA01L short 20, and fuse 1206L010/30WR demand
10, stock 7, shortfall 3. Both job screens can display the same seven fuses;
do not count them twice. If 18+10 are gross requirements and those seven are
one eligible shared pool, 21 is an illustrative combined shortfall, subject
to JLC confirming reservation, pooling and allowances. The two Murata lines
each show 20 despite 12 physically installed across 2+8; no pooling of job
allowances is assumed. None of these is an approved purchase quantity.

## Exact listing snapshots

Read-only JLC catalog screens, for PCBA sourcing, showed:

| Exact MPN | Public stock | Listing observation |
|---|---:|---|
| CTS CB3LV-3I-12M288000 | 0 | Pre-order minimum 4, estimated $10.20 total |
| Littelfuse 1206L010/30WR | 7 | In-stock listing showed 7, not enough for both jobs; replenishment quantity/date needs confirmation |
| Murata GRM21BR71A105KA01L | 0 | Pre-order minimum 407, estimated $8.71 total |
| TDK C2012X7R1V225K125AE | 0 | Pre-order minimum 62, estimated $8.80 total |
| TDK C3216X7R1V106K160AC | 0 | Pre-order minimum 14, estimated $8.83 total; listing showed estimated 28 days |
| TI PCM1864DBT | 0 | Exact tube part showed Consign Part; ordinary listing does not establish a purchasable offer. DBTR is a different suffix and was not selected. |

The listing minimum prices are indicative displayed minimum-line estimates,
not final account offers, additional job quantities, usable-stock dates or
fees. The prior $104.88 exact ADC Global Sourcing observation for ten units
is historical, not a proven MOQ, fresh offer or allocation. Actual global
and replenishment purchase terms, separate fees, and post-receipt availability
remain unconfirmed; no pre-order was initiated.

## Ranked paths and boundary

1. Preferred: complete the two-carrier/eight-pod JLC proposal, if the user
   accepts that minimum. Request exact sourcing for the six identities and
   confirm allowances, stock allocation, dates, setup, components, fabrication,
   assembly, shipping/tax and process holds. Existing preview is incomplete;
   JLC warned that continuing without missing parts would omit them, so they
   remain required. Prepaid parts, reservation or an actual order require a
   separate user decision.
2. Compare five-carrier/eight-pod JLC and the submitted PCBWay 1+8 inquiry
   after itemized review. PCBWay currently includes factory through-hole work,
   so reconcile scope and cost before comparing. Its $29/$88 figures are
   assembly-only provisional amounts, not complete PCBA totals.

Validation: `home_assembly_plan.py verify` passed; 35 order-readiness tests
passed; `publication.py verify` passed for all 256 preserved release files.
Placement preview, component allocation, stack and manufacturing acceptance
remain open. Existing r3/release data were not changed.
