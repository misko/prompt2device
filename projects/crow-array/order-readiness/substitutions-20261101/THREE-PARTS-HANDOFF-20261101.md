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

## Backend agent handoff — ready to paste

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
