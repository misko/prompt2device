# Quote reconciliation — 2 carriers / 8 pods

**Ownership/files update — OR21:** [r5](quote-draft/r5-2c8p-complete/README.md) supersedes
the SMT-only/home-THT split below. JLC now requested to install all 24 Ethernet
jacks, two power jacks and two RECOM modules in addition to 478 SMT parts.
Home list is two Picos/eight microphones/eight buzzers. RECOM sourcing, THT labor,
and allowances remain to be quoted. Complete local placement data is now
prepared/verified; JLC matching and final placement preview remain pending.
Historical prices below are not a current mixed-assembly quote. Older
observations remain unchanged.

2026-10-31 PDT. **Preparation only; not a complete quote or purchase approval.**
Inputs: remote `0b44f57dd7289db691768c4ecdbc671937cf68ed`, its two-carrier
browser observations and sourcing report, and the unchanged r3 per-board files.
The server reviewed public manufacturer/vendor documentation, not the signed-in
account. Account observations below are inherited, not newly verified inventory.
This document supersedes earlier route recommendations for this quote pass;
historical observations and all released/quote-packet bytes remain unchanged.

## Scope fixed for quotation

| Job | Fabricated | JLC assembled | SMT per board | SMT installed |
|---|---:|---:|---:|---:|
| Carrier | 5 | 2 | 127 | 254 |
| Pod | 10 | 8 | 28 | 224 |
| Total | 15 | 10 | — | **478** |

Keep the second carrier SMT-only. Home parts finish **one carrier + eight pods**:
16 RJHSE-5080, one PJ-102AH, one R-78E5.0-0.5, one original SC0915 Pico,
eight CMA-4544PF-W microphones and eight CPE-203 buzzers: **35 installed parts**.
The retained $68.07 home estimate buys 39 parts (two extra microphones and two
extra buzzers at cheaper quantity breaks); it is not a fresh offer. No home
parts for the second carrier are included. JLC excludes all six home identities.
No enclosures, roof hardware, host Raspberry Pi, PSU or cables in this comparison.

## Quantities reconciled, purchasing quantities still conditional

The machine-readable companion is `jlc-2c8p-reconciliation-20261031.csv`.
Gross means the browser's job requirement, not merely installed demand. The
difference may include minima or allowances; its cause has not been confirmed.

| Exact MPN | Installed carrier / pod | Displayed gross carrier / pod | Gross total | Global offer quantity / USD | Regular replenishment quantity / USD |
|---|---:|---:|---:|---:|---:|
| CB3LV-3I-12M288000 | 2 / 0 | 2 / 0 | 2 | 2 / $4.28 | 4 / $10.20 |
| 1206L010/30WR | 16 / 8 | 18 / 10 | 28 | 30 / $21.72 | Not established for this batch |
| GRM21BR71A105KA01L | 4 / 8 | 20 / 20 | 40 | 40 / $6.01 | 407 / $8.71 |
| C2012X7R1V225K125AE | 0 / 8 | 0 / 10 | 10 | 10 / $8.46 | 62 / $8.80 |
| C3216X7R1V106K160AC | 4 / 0 | 4 / 0 | 4 | 10 / $3.41 | 14 / $8.83 |
| PCM1864DBT | 4 / 0 | 4 / 0 | 4 | 4 / $43.70 | Unavailable in ordinary catalog observation |

The installed totals are **54**, versus **88** displayed gross requirements.
The six observed Global Sourcing offers buy **96** pieces: 2 + 30 + 40 + 10 +
10 + 4. Those eight above gross consist of two fuses and six TDK C3216 parts;
they are not additional installed components. The selected RS offer has a
ten-piece minimum. Do not extrapolate its price to four pieces. Do not add a
second generic attrition percentage to already-gross quantities.

For each selected source, JLC must confirm the per-job gross amount and eligible
inventory, then apply that offer's minimum and order multiple to the remaining
need. If an allowance changes with packaging/source, recalculate before pricing.
No final purchase quantity is asserted in the CSV; its final fields are blank.

**Fuse reconciliation:** both jobs showed seven in stock. With one shared,
eligible pool, 18 + 10 − 7 = **21** additional pieces before procurement minima,
not (18 − 7) + (10 − 7) = 14. But seven covers neither complete job. For a
wholly Global Sourcing route, credit **zero** public pieces until pooling is
explicitly supported: cover the full 28 gross, with the observed 30-piece offer
as a pricing candidate. For regular replenishment, 21 is only a conditional
shortfall, not an order quantity. Do not subtract the seven from both jobs or
assume they can be combined with a global lot inside either job.

**Murata:** keep 20 carrier + 20 pod for quotation; do not collapse to 12
installed or a shared minimum of 20 without JLC confirming the allowance rule.
Likewise keep ten C2012 for the eight-pod job. Two oscillators and four ADCs have
no observed allowance above installed count; this is not proof none is needed.

## Fees and route decision

The [current JLC Global Sourcing terms](https://jlcpcb.com/help/article/global-sourcing-parts-order-terms-conditions)
restrict mixing pre-order and global/consigned pools for one MPN within a job.
They require warehouse receipt before assembly use. Fuses are listed for
$20/kind inspection plus a shared certification fee ($20 for one kind):
**potentially $40 here**, subject to JLC's classification of this resettable PPTC.
Packing/loose-part handling, duty, baking and oversized inbound freight may add
charges; ordinary global inbound shipping is described as free. Paid global
orders are noncancelable. These are policy signals, not this job's bill.

| Cost bucket | Current evidence | Required for complete quote |
|---|---|---|
| Six global offer lines | **$87.58**, selected quantities above | Final quantities, supplier, packing, validity and source eligibility |
| Fuse inspection/certification | Conditional **$40** | Applicable or explicitly not applicable; charge once or per procurement transaction |
| Global packing/handling/duty/baking/freight | Unknown, not $0 | Itemized charges and any included amounts |
| Other SMT parts | 26 identities / **424 installed placements** | Both jobs' complete priced selections and allowances |
| Carrier fabrication/engineering | Historical $37.40 = $12.40 + $25 | Refresh actual process and quantity; assembly/components excluded |
| Pod fabrication/engineering | Historical bare-board $14, stale settings | Current ten-bare/eight-assembled job, all engineering fees |
| SMT labor, setup, stencil, feeders, any CTS manual handling | Unknown | Separate per job; avoid adding setup already inside engineering |
| JLC outbound freight, tax/duty | $26.94 was carrier-only, not usable here | Combined-shipment option to the user's actual destination |
| Home kit | Historical **$68.07** | Exact identity, available quantities, shipping/tax; separate from JLC |
| Home labor / tools | User installation; not priced | No factory THT or acoustic installation charge |
| **Complete total / delivery** | **Unknown** | Do not sum partial displays into a purported quote |

If the $40 fuse charge applies, the six-line search benchmark becomes **$127.58
before all other costs**, not $87.58. The four known regular replenishment lines
(CTS and three capacitors) total $36.54; with the historical ADC global line,
that is **$80.24 plus regular fuses and all applicable fees**, not a full route
price. Prices for different quantities/sources cannot be scaled as firm offers.
Record component prepayment separately from PCBA charges; count its cost once,
including unused purchased surplus. If later assembly charges consume prepaid
inventory, reconcile the credit rather than billing the same parts twice.

**Ranked approach:**

1. Prefer JLC-managed procurement, with one eligible source pool per MPN per
   job. Compare regular replenishment for the fuse against its fully landed
   global offer first; the potential $40 dominates small passive savings.
   Use the other exact global or replenishment offers according to confirmed
   arrival and total fees, not minimum unit price. This avoids external shipping
   and consignment work but remains conditional on a non-binding quote.
2. If JLC cannot offer an acceptable exact source, compare exact external
   consignment only for the failed lines, including intake, packing, freight
   and time. No substitutions or shipments are authorized. If either route
   requires buying parts before a complete PCBA quote, return a staged-cost
   decision with the unquoted exposure instead of promising a complete quote.

## Assembly questions: known facts versus remaining acceptance

| Subject | Evidence-supported conclusion | Remaining exact-job question |
|---|---|---|
| CTS X1 | Manufacturer CB3/CB3LV is 7 × 5 mm SMD; Rev. K p4 gives 260 °C maximum / 20 s reflow conditions, MSL1. JLC FAQ explains its Wave Soldering label means manual assembly. This is not evidence of a footprint defect. | Will the selected exact offer use compatible SMD reflow or a separately supported manual procedure, in Economic carrier service? Confirm method, profile, charge and any service change. Do not demand a relabeling if the actual process is compatible. |
| ADC U1/U2 | TI exact PCM1864DBT is TSSOP-30, standard carrier 60-piece tube, MSL2/260 °C. Standard tube size is **not** a demonstrated purchase MOQ. DBTR is a different ordering suffix and remains excluded. | Confirm actual four-piece offer packaging, intake/feeder or loose-part cost, allowances and moisture handling. Exact JLC match must be DBT, not merely a similar package string. |
| Factory population | 127 SMT refs/carrier, 28/pod; no home parts in BOM/CPL. | Review selected identity and preview for every ref, side, center, pin 1 and cathode. Preserve mapped rotations; do not zero or reinterpret them from native angles alone. |
| Stencil / thermal | Released exclusions and assembly limits remain binding. | Preserve all home pads/holes; resolve production aperture optimization against retained controls. Account for factory plus later home thermal cycles, including retained R3 at-most-two-reflow control. |
| Stack / tooling / mechanics | Four layers, 1.6 mm; carrier 7628A, pod 7628. Historical portal rails/defaults were not accepted. | Confirm finish, actual stack, rails/fiducials/fixtures, outline/holes and coupled mechanical controls from released instructions. A quote may stay conditional; production approval may not silently waive them. |
| Home completion | All RJ/PJ/RECOM/Pico/acoustics are user work. Prototype Pico-fit risk previously accepted. | Preserve original SC0915 module-D1-only modification, not carrier D1, and acoustic no-wave/no-wash hand handling. No firmware/functional qualification is included in PCBA. Do not reopen accepted Pico-fit risk without new evidence. |

Sources reviewed publicly on 2026-10-31:
[CTS datasheet](https://www.ctscorp.com/Files/DataSheets/Passives/FCP/Clock-Oscillators/clock-ocillators-CB3_CB3LV-datasheet.pdf),
[JLC assembly FAQ](https://jlcpcb.com/help/article/pcb-assembly-faqs),
[TI exact DBT](https://www.ti.com/product/PCM1864/part-details/PCM1864DBT).
Full design-owned limits remain in the immutable release's README and historical
assembly/process instructions; this table does not replace or amend them.

**ADC source discrepancy:** the public TI page retrieved during this pass
displayed out of stock / login-dependent inventory, whereas the account report
recorded a TI Global Sourcing offer. This does not disprove the account offer,
but it prevents treating its availability as confirmed. Recheck that exact
offer once. The [exact DigiKey DBT page](https://www.digikey.com/en/products/detail/texas-instruments/PCM1864DBT/5213896)
retrieved today showed 673 and $10.45 each below ten ($41.80 for four), tube,
with a warning that small-quantity packaging can change. This is a public
fallback benchmark, not a JLC offer or allocation; check DigiKey *within JLC
Global Sourcing* before considering external consignment. No source was adopted.

## Schedule and next decision

Inherited supplier displays: CTS/fuse/Murata/C2012 8–14 business days, C3216
8–16, ADC 10–14. Regular C3216 showed 28 days of unspecified calendar basis.
None establishes a usable-stock date or delivery date. Capture:
supplier lead trigger → supplier dispatch → JLC intake/usable inventory →
PCBA start/finish → outbound delivery. Ask which steps overlap and whether
the two jobs can ship together; do not simply add the displayed ranges.

Use `MACBOOK-2C8P-QUOTE-HANDOFF-20261031.md` for one focused account pass.
Complete outcome: fully scoped, itemized non-binding quote with dates and
explicit conditional process items. If shortage sourcing prevents that outcome,
stop with the exact payment/commitment boundary and missing amounts. Do not
omit parts, submit the warned noncancelable pre-order quotation, or repeat the
full inventory search. Public technical clarification is progress, not closure
of vendor acceptance, allocation or purchase authority.
