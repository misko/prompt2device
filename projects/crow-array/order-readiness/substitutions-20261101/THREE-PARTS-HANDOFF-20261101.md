# Three remaining parts — images and backend handoff

This is a visual reference and a quote-only handoff, not a purchase list or
production approval. Quantities and prices below are **unreserved JLC search
observations from 2026-10-31 Pacific**, not current stock guarantees. Pictures
are enlarged and not to scale; the first two are representative series images,
not photographs verified as the exact ordered frequency or fuse marking.

## Littelfuse 1206L010/30WR — resettable fuse

![Representative Littelfuse 1206L series fuse](https://mm.digikey.com/Volume0/opasdata/d220001/medias/images/202/POLYFUSE-1206L.jpg)

1206 surface-mount package, about 3.2 × 1.6 mm. [Exact-part DigiKey listing](https://www.digikey.com/en/products/detail/littelfuse-inc/1206L010-30WR/6346986).
JLC Global Sourcing showed DigiKey cut tape `18-1206L010/30WRCT-ND`, MOQ 1,
estimated attrition 2, minimum assembly quantity 2 and 8–14 business days;
30 pieces showed **$21.72**. Matching pages showed gross requirements of 18
carrier and 10 pod; confirm per-job allowances and pooling before using 30 as
a purchase quantity. Seven public units shown in both jobs may be one pool;
do not combine public stock with Global Sourcing stock for the same component.

## CTS CB3LV-3I-12M288000 — 12.288 MHz oscillator

![Representative CTS CB3/CB3LV oscillator](https://www.mouser.co.il/images/ctselectroniccomponents/lrg/CB3_CB3LV_SPL.JPG)

7 × 5 mm surface-mount package. The pictured series example has a different
frequency marking. [Exact-part DigiKey listing](https://www.digikey.com/en/products/detail/cts-frequency-controls/CB3LV-3I-12M288000/4308709).
JLC Global Sourcing showed DigiKey cut tape `110-CB3LV-3I-12M288000CT-ND`,
MOQ 1, estimated attrition 0, minimum assembly quantity 0 and 8–14 business
days; two pieces showed **$4.28**. CTS specifies reflow for the series while
JLC's library labels this part wave soldering; actual method, process limits,
cost and acceptance remain to be confirmed.

## RECOM R-78E5.0-0.5 — 5 V regulator

![RECOM R-78E5.0-0.5 regulator](https://www.partco.fi/9534-thickbox_default/switching-regulator-module-15a-5v.jpg)

Three-pin through-hole regulator. [Exact-part manufacturer listing](https://backoffice.recom-power.com/en/products/switching-regulators/switching-regulators-sip/rec-p-R-78E5.0-0.5.html).
JLC Global Sourcing showed DigiKey tube `945-1648-5-ND`, MOQ 1, estimated
attrition 0, minimum assembly quantity 0 and 8–14 business days; two pieces
showed **$9.69**. JLC's same-text YLPTEC C18212367 auto-match is **unchecked**;
it is not the specified manufacturer. The exact RECOM must be sourced and
selected before the required U10 placement can be accepted.

The three illustrative lines total **$35.69** before fees, shipping, tax and
all other board and assembly costs. The quantities, eligible sources, JLC
warehouse arrival dates and factory acceptance remain unconfirmed; the quoted
lead-time ranges are not delivery dates. Fuse inspection/3C fees and component
handling fees may apply. See the [browser session report](JLC-MACBOOK-SESSION-20261031.md)
for the full evidence and the matched r6 replacement rows.

## Backend reconciliation — 2026-11-01

Continued from `75447f43`; no BOM/CPL or release changes. The October 31
signed-in observations above have not been refreshed in the account yet.

| Exact part | Installed: carrier job + pod job | Last displayed gross need | Historical priced quantity | Remaining quantity question |
| --- | ---: | ---: | ---: | --- |
| Littelfuse 1206L010/30WR | 16 + 8 = 24 | 18 + 10 = 28 | 30 | Confirm the two per-job allowances and one pool serving both jobs; 30 includes two beyond the displayed gross, not an approved spare allowance |
| CTS CB3LV-3I-12M288000 | 2 + 0 = 2 | 2, with zero sourcing attrition shown | 2 | Confirm exact job minimum and usable quantity |
| RECOM R-78E5.0-0.5 | 2 + 0 = 2 | 2, with zero sourcing attrition shown | 2 | Confirm exact RECOM eligibility and required quantity, not the YLPTEC match |

Do not add the fuse attrition field again to 18 and 10. Do not extrapolate a
28-piece price from the 30-piece illustration. The unreserved $35.69 remains
a dated three-line subtotal, not a complete sourcing or PCBA quote.

### Public stock refresh

Read-only CLI observations at approximately 2026-11-01 14:46 UTC are retained
in [quote-reconciliation-20261101](quote-reconciliation-20261101/).

| Exact JLC identity | Public observation | What this establishes |
| --- | --- | --- |
| Littelfuse C2153988 | In-stock label, no verified public quantity; overseas field 7, presale field 5 | Insufficient evidence of 28 usable pieces; do not sum these fields |
| CTS C17275161 | Out of stock; overseas/presale zero | No public-stock solution established |
| RECOM C5199916 | Ordinary purchase disabled; out of stock | Exact Global Sourcing candidate still needs checking; the retailer's lifecycle wording is not manufacturer EOL confirmation |

The secondary index supplied no usable stock count. These public checks do
not inspect private inventory, reserve stock, or refresh the historical
DigiKey-through-JLC offers.

### Policy findings and unresolved charges

For a single component in a job, JLC permits public plus pre-order inventory,
or Global Sourcing plus consignment inventory, but not cross-combination of
those groups. Therefore do not subtract seven public fuses from the Global
Sourcing requirement, or count a shared seven-piece pool twice. Different
MPNs need not all use one sourcing route. Actual cross-job allocation remains
unconfirmed. [JLC inventory guidance](https://jlcpcb.com/help/article/how-to-use-my-own-parts-for-pcb-assembly-order).

JLC's Global Sourcing terms require assembly review and warehouse arrival;
unpaid supplements can block use. They specify $20 per part-kind commodity
inspection for categories including fuses, plus a separately described/shared
3C fee. The exact combined charge is unresolved. Modules may attract 3–30%
duty; RECOM applicability is unknown. Packing preparation, baking and
oversize-shipping charges are conditional, not automatic additions. Paid
Global Sourcing orders are noncancelable.
[Terms and charges](https://jlcpcb.com/help/article/global-sourcing-parts-order-terms-conditions).

The historical 8–14-business-day ranges do not establish usable warehouse
dates. Record the lead-time trigger, receiving/inspection delay, and when each
exact identity becomes selectable for both jobs; do not invent calendar dates.

JLC says placing a PCBA order occupies components and does not support review
before payment. An unpaid order is therefore not an acceptable quote-only
workaround under the user's no-reservation instruction.
[PCBA FAQ, question 9](https://jlcpcb.com/help/article/pcb-assembly-faqs-part-2).

### Next signed-in check — read-only

1. Verify the existing drafts still specify fabrication 5/10, assembly 2/8,
   all required r6 rows, and the deselected YLPTEC identity. Do not re-upload
   or reset selections merely to inspect them.
2. Inspect the three exact DigiKey Global Sourcing offers above and My Parts
   inventory. Record current supplier SKU, packing, MOQ, per-job gross demand,
   attrition, source pool, indicative prices and available fee/date fields.
   Compare fuse quantities 28 and 30 only if the search UI supports a
   non-binding calculation without adding to cart or submitting anything.
3. Check whether assembly eligibility is explicitly documented for each exact
   part. The CTS wave/manual label versus manufacturer reflow specification
   remains unresolved; general THT support does not approve the RECOM module's
   seating, process or exact job. Retain the existing process/mechanical holds.
4. View placement previews and itemized prices only if already available
   without changing required coverage or committing stock. Keep carrier
   JLC04161H-7628A thickness acknowledgement open; preserve pod rail review,
   stencil/inspection controls and both no-auto-confirm preferences.
5. Stop at any Add/order/reservation, noncancelable quote, payment, vendor
   contact, or required-part omission boundary. Save the exact missing field
   and gate instead of repeating the same blocked step. No additional
   substitutions or manufacturing approval are authorized.

### Signed-in follow-up — 2026-11-01 Pacific

User completed sign-in; TinyFish reached the authenticated account. The first
pass did not find the three targets in visible private inventory and failed
to reach the saved Crow drafts. This is not proof of absent supplier offers
or missing drafts. A second pass used the retained
[direct Global Sourcing search](https://jlcpcb.com/user-center/smtPrivateLibrary/orderParts/?global=1)
successfully. [Normalized observations and run IDs](quote-reconciliation-20261101/signed-in-observations.json)
retain the evidence limits without unrelated account data or credentials.

| Exact DigiKey offer | Reported supplier stock | MOQ | Reported lead | Price evidence |
| --- | ---: | ---: | --- | --- |
| 18-1206L010/30WRCT-ND | 45,522 | 1 | 8–14 business days | Visible tiers 1+ $0.9535 and 5+ $0.7859; full tiers/28- or 30-piece total not confirmed |
| 110-CB3LV-3I-12M288000CT-ND | 1,449 | 1 | 8–14 business days | 1+ $2.1389; two-piece arithmetic rounds to $4.28 before fees |
| 945-1648-5-ND | 32,691 | 1 | 8–14 business days | 1+ $4.8447; two-piece arithmetic rounds to $9.69 before fees |

These are browser-agent reports of distributor offers, not owned/allocated
JLC stock, a refreshed job quote or guaranteed dates. Do not replace the old
$35.69 subtotal with a calculation using incomplete fuse price tiers.

The browser reports were inconsistent about an assembly-not-supported
tooltip. A targeted verification ultimately stated the text was in hidden
`display:none` popovers, no hover-trigger occurred, and no screenshot was
returned. Reject both the claimed visible rejection and the inference that
zero attrition means unsupported assembly. All three exact offers' eligibility
remains **unverified**, not accepted or rejected.

No additional retry is scheduled. Next: inspect the exact row's actual visible
hover/disabled state in the MacBook browser, safely calculate fuse totals in
the search UI, and provide direct existing-draft URLs if further remote
inspection is wanted. Do not click Add as an eligibility test. If the only
confirmation route requires vendor contact or a sourcing/order submission,
stop for new authority. Fees, usable dates, job allocation, previews, carrier
thickness warning and all factory process/mechanical holds remain open.
All three browser passes reported no cart additions, draft changes, orders,
reservations, vendor messages or terms acceptance.

## LUTE/TRACO stock and qualification — 2026-11-01 Pacific

User authorized availability checks and qualification, keeping CTS unchanged;
not adoption or purchasing. Used find-substitute-part to separate availability,
compatibility and acceptance. Both remain **same-footprint candidates**, not
packaging-only equivalents or fully accepted production substitutions.

| Original / installed need | Candidate | Regular JLC stock / available order quantity | Result |
| --- | --- | --- | --- |
| Littelfuse 1206L010/30WR / 24 | LUTE 1206L010/30NR, [C7542926](https://jlcpcb.com/partdetail/C7542926) | 33,902 / 33,897 | SMT; sufficient catalog stock; recommend conditional quote review |
| RECOM R-78E5.0-0.5 / 2 | TRACO POWER TSR 1-2450, [C6886877](https://jlcpcb.com/partdetail/C6886877) | 267 / 167 | THT/Wave Soldering label; sufficient catalog stock; recommend conditional quote review |

Both showed ordinary Add-to-assembly-library controls, MOQ 1 and no pre-order
indicator. Neither was added. Two browser passes are retained by run ID in
[normalized observations](quote-reconciliation-20261101/candidate-observations.json).
Discard the first pass's inference of guaranteed immediate assembly and its
incorrect SMT label for TRACO. No explicit warehouse-ready date, job allocation,
loading allowance or final assembly acceptance was obtained. Stock and orderable
quantities are not additive. The screen did not explain their difference.

**Time/cost judgment:** ordinary stock should avoid these two originals' observed
8–14-business-day Global Sourcing route. This is an inference, not a delivery
promise. Unchanged CTS may still set the overall schedule. At displayed 1+ unit
prices, 24 fuses cost $0.94 and two regulators $12.99, rounded; $13.94 combined
from unrounded amounts, before attrition, setup, assembly, shipping and tax.
This is not a quote. The original 28/30-piece fuse figures must not be copied
as the replacement's required quantity. JLC must calculate replacement-specific
gross demand for 16 carrier and 8 pod installations.

### Bounded engineering review

LUTE: retains 0.10-A hold, 0.25-A trip, 30-V/40-A ratings; specified trip at
0.5 A is 1.0 s. Post-trip/reflow resistance maximum rises from 10 to 15 ohms.
Its 60-C hold table gives 70 mA versus the 50-mA pod allocation. This is not
a lifetime guarantee: the use cautions limit the table's test basis and warn
about repeated trips/process heat. Body maximum is 3.60 x 1.90 x 1.20 mm.
Recommended lands are 1.00 x 1.80 mm, 1.80-mm gap; actual r6 lands are
1.25 x 1.75 mm, 2.80-mm centers. They have nominal terminal overlap but are
not identical to the recommendation. Retain a land/paste review. Reflow is
specified; no blanket hand-rework or solvent-cleaning approval. Process details
and cleaning compatibility must be resolved, not inferred from generic SMT
eligibility. [Manufacturer-authored sheet, LCSC mirror](https://atta.szlcsc.com/upload/public/pdf/source/20240318/5A22D9BB0BD0A87D0C930C7F021BC012.pdf).

TRACO: pin order input/GND/output and 2.54-mm pitch match U10. Its 6.5–36-V
input, 5-V output, 1-A capacity and 470-uF capacitive-load ceiling cover the
retained steady-state budget. At 85 C the stated derating yields 400 mA;
actual proposed enclosure limit remains 60 C, not expanded to 85 C. Body is
11.7 x 7.5 x 10.1 mm, dimensional tolerance ±0.5 mm; pitch ±0.25 mm,
pins 0.50 x 0.25 mm ±0.05. Existing 1-mm drills do not alone prove finished-hole
fit across tolerance. Update body/courtyard/model and seating checks if adopted.
Ripple is typical, not a guaranteed maximum. Current limiting is 250% typical,
with automatic short recovery; do not treat this as a guaranteed fault ceiling.
Recommended input fuse is application-dependent. Recheck startup/inrush against
existing 1-A input protection, fault cycling, noise and thermal behavior; do not
silently up-rate that fuse. Wave limit is 265 C/10 s; actual JLC handling remains
to be confirmed. [Manufacturer-authored sheet, LCSC mirror](https://datasheet.lcsc.com/datasheet/pdf/b086eec99820b18ef472dfe38fa17d0f.pdf?productCode=C5966845).

### Actual circuit and margin checks

Read-only native r6 inspection verified carrier U10 pad 1 `/12V`, pad 2 `/GND`,
pad 3 `/5V`; D2 connects module output anode to Pico `/VSYS` cathode. Thus the
existing reverse-blocking topology is retained; waveform behavior is not proven
by that topology. U10 is at (182,38) mm, rotation zero, pitch 2.54 mm. Nearby
R2 is at (182,47), R1 at (186,51), C2 at (182,51). The nominal smaller-depth
TRACO body shows no obvious adjacent-body conflict, but this is not a full
tolerance/3D or fabrication check. No net, footprint, placement or routing changed.

Recovered retained first-run source at
`/home/mouse9911/gits/crow-first-run-5c10p-20261022/project/03_src/recovery/first-run-r3-source/`:
`ROOF-INTERFACE.md` SHA256
`f2dcad8c938e0e821ae41b691323df86471751a467dc023f018ac8575c95f0ed`
matches the public architecture review's recorded digest. `INTERFACE-DESIGN.md`
SHA256 `da08b04da596410ba3ea16ab806a8568eaeb629135150124202b365babec16f5`
provides the power-budget derivation. These files were only read, not changed.

The retained planning bounds are 50 mA/pod including buzzer, 300 mA at the
5-V module, 9.8-V protected carrier low line, and 1-ohm total cable/contact
resistance. Original hot PTC assumption was 20 ohms each (twice its room-
temperature post-trip maximum), giving 7.75 V at the pod. Applying the same
**engineering sensitivity allowance**, not a manufacturer hot guarantee, gives
30 ohms each for LUTE: `9.8 - 0.05*(30+30+1) = 6.75 V`. That still exceeds
the 3.3-V LDO's regulation requirement and the buzzer's 3-V operating floor.
At room-temperature resistance maxima the additional two-fuse drop is 0.5 V.
Keep hot startup/recovery and buzzer calibration in first-article validation;
do not call these calculations measured performance. [Buzzer source](https://www.sameskydevices.com/product/resource/cpe-203.pdf).

### Decision and smallest next step

1. Preferred: carry these two candidates into a separately authorized quote
   revision after affected land/footprint and process review. Preserve the
   existing prototype bench-test gates, with the changed power assumptions
   explicitly recorded. They are plausible sourcing improvements, not an
   already accepted replacement BOM.
2. Fallback: retain exact Littelfuse/RECOM Global Sourcing if the handling or
   footprint work costs more time than waiting for the unchanged CTS clock.

Before promotion: reconcile LUTE reflow/cleaning/rework and land/paste details;
reconcile TRACO body/lead tolerances, input-fuse/startup behavior and assembly
process; then regenerate only affected BOM/native/quote artifacts and run their
checks. Bench waveforms remain later prototype qualification, not an invented
prerequisite requiring purchased hardware for this desk review. In the browser,
obtain exact replacement per-job demand, fees and placement previews only within
non-binding controls. Keep carrier stackup and all existing factory holds open.
No additional supplier search or browser retries are queued for this review.

Validation: `git diff --check` passed; the r6 public verifier passed all 94
unchanged payload files (production-ready remains false). Quantity, conditional
margin, evidence-state and decimal-currency assertions passed. An initial binary
floating-point rounding assertion was replaced with decimal arithmetic for the
$13.9350 half-cent estimate; no quote price was inferred from that arithmetic.

## Qualification completed and r7 prepared — 2026-11-01

User subsequently authorized adopting these two parts if qualification passed.
Both passed the **controlled-prototype quote** desk review, not production or
hardware acceptance. See [r7-review.json](r7-review.json) and
[r7 upload instructions](../quote-draft/r7-2c8p-stocked-power/README.md).
This supersedes the earlier recommendation-only state; raw observations remain
historical and unchanged. Exact stock allocation and factory handling remain
open. CTS is unchanged, so no guaranteed whole-build schedule saving is asserted.

The decisive mechanical evidence was the retained LS43 free-lead contract:
finished U10 holes .92..1.13 mm, combined prepared center error <=.10 mm,
actual annulus >=.13 mm and force-free insertion. TRACO's maximum .55x.30-mm
section gives .04675-mm radial clearance under that contract. This is not
rigid worst-pitch insertion or permission to transfer forming load into its case.
The LUTE expanded body and TRACO body/pose envelopes clear the neighboring
footprint bounds. Both component-specific process requirements are now explicit
in the quote instructions instead of being inferred from a JLC category label.

Generator `r7_quote.py` consumes the verified r6 baseline; it leaves prior
artifacts intact. The new footprint has corrected F.Fab/courtyard geometry and
no incorrect inherited 3D model. Only U10's carrier CPL center changes; copper,
drills, mask, paste, silk and both fabrication ZIPs are preserved. Counts remain
478 SMT, 28 factory THT and 18 home placements. Local package manifest SHA256:
`765b066dacf03d34d038cc2e29ef78abf749b91de29a678113f6661d265ce835`.

Fresh KiCad exports/DRC/ERC and validation receipt are in `r7-validation/`.
Both netlists are unchanged, source/PCB/BOM identities agree, and zero ERC/DRC
violations/unconnected items were reported. The four inherited ERC disabled
categories remain recorded; no new waiver. 35 quote regression tests passed,
including seven for r7; deterministic replay covers 97 files. An initial build
hit a generic library reference mismatch; using the actual board's retained
land library corrected it. Final table review also caught an old fuse value
string and lowercase scope-footprint field; both were fixed, regression-tested,
and ALL KiCad exports regenerated. Intermediate outputs were preserved under
`/tmp/crow-r7-checks-X1KVU4`, not substituted for final results. Existing KiCad
property-enum/duplicate-image/lock warnings did not prevent successful checks.

Recheck from repository root:

```sh
python3 projects/crow-array/order-readiness/r7_quote.py verify
python3 -B -m unittest discover -s projects/crow-array/order-readiness -p 'test_*quote.py'
python3 projects/crow-array/order-readiness/r7_validate.py
python3 projects/crow-array/order-readiness/substitutions-20261101/verify_public.py
```

The last two checks respectively inspect retained fresh KiCad results and r6
integrity; they do not execute physical tests or obtain factory approval.
No browser changes, purchases, reservations, messages or pushes in this turn.

## Backend agent handoff — r6 originals, historical baseline

> Continue Crow's r6 quote for 5 fabricated / 2 assembled carriers and 10
> fabricated / 8 assembled pods on `codex/crow-jlc-source-review-20261030`.
> The user authorized the four r6 replacement identities for this quote-only
> session. No purchases, payment, reservation, noncancelable pre-orders,
> vendor messages or manufacturing commitments. Do not silently omit any
> required part or adopt additional replacements.
>
> Start with `substitutions-20261101/JLC-MACBOOK-SESSION-20261031.md`, this
> report, `substitutions-20261101/HANDOFF.md` and current `STATUS.md`. Both r6
> BOM/CPL pairs were processed in the existing JLC drafts, and the four r6
> replacement MPN/C-code matches appeared selected. JLC reselected the wrong
> YLPTEC regulator and reset ten grouped rows during processing; those required
> grouped rows were restored and YLPTEC U10 was deselected. Verify the live
> draft and do not interpret its inconsistent summary counts as proof of full
> coverage.
>
> Resolve exact sourcing and assembly eligibility for Littelfuse
> 1206L010/30WR, CTS CB3LV-3I-12M288000 and RECOM R-78E5.0-0.5. Reconcile
> per-job gross quantities, attrition, source pools, packing, inspections/fees
> and usable warehouse dates. The $35.69 candidate total is dated, unreserved
> and incomplete. The pod's NEXT offered to leave unselected parts unplaced;
> Select parts was chosen. Find a non-binding route to complete placements and
> itemized PCBA pricing; stop if the only available path acquires or reserves
> parts, or if pre-order terms make the quotation noncancelable.
>
> Recheck ENIG, precision routing, stackups, rail and stencil controls, CTS
> handling, THT seating and all 506 factory placements. The carrier 7628A
> thickness warning remains unaccepted; the released design already documents
> the 1.5542 mm layer sum, but the ±10% warning and full mechanical/factory
> agreement remain open. Recheck production-file and placement review settings
> and the no-auto-confirm preferences. Obtain actual placement previews and
> itemized fabrication, parts, SMT/THT labor, setup, sourcing, shipping and
> tax information before any later order decision. Quote-file integrity is
> not production approval.
