# JLC r7 MacBook session — 2026-11-01

Latest follow-up is recorded at the end of this file. Initial unsaved-form state
below is historical; the continuation contains the two current saved draft URLs.

Source: commit `20f23f8d6fdc3cdd8db8a3c6ace1c2b0dbcba377`; isolated worktree. The r7 verification passed for 97 files, with `production_ready: false`. Existing r6 drafts were not opened or changed.

## Current browser state

Two new, **unsaved and incomplete** forms are open in separate Chrome tabs at `https://cart.jlcpcb.com/quote`. This generic URL does not identify a saved draft. Do not close or refresh the tabs if their current state is needed. No new durable draft names or URLs have been obtained.

- Carrier: uploaded r7 `carrier-gerbers.zip`, parsed as 200 × 100 mm, four layers; 5 fabricated, 2 assembled; Standard PCBA, top side. ENIG and precision outline selected. JLC proposes two 5 mm rails and a 200 × 110 mm panel; edge treatment and depaneling remain open. The requested 7628A stackup was not accepted because its thickness acknowledgement remains a hold. The earlier board-screen price was $67.93; it is not a PCBA quote and may change.
- Pod: uploaded r7 `pod-gerbers.zip`, parsed as 85 × 78 mm, four layers; 10 fabricated, 8 assembled; Standard PCBA, top side. ENIG, precision outline and JLC04161H-7628 were selected. JLC proposes two 5 mm rails and an 85 × 88 mm panel; edge treatment and depaneling remain open. The board screen showed $42.24, excluding components and assembly. A separate shipping estimate of $26.94 appeared, subject to change and not a combined final shipping quote.

For both forms, production-file and parts-placement review were selected with “Do not confirm automatically” checked in the respective dialogs. These settings are not approval of the files or placement. Recheck all selections when resuming: forms are unsaved, and enabling assembly changed some page behavior.

## Boundary and missing evidence

The assembly-service terms checkbox is preselected, and advancing with NEXT may accept those terms. The handoff forbids approving disclaimers, so the session stopped before NEXT pending clarification/authorization. The BOM and CPL files have **not** been uploaded, no components have been matched or reserved, and no placement preview or complete quote has been obtained. Current stock, CTS sourcing, exact LUTE/TRACO matches, assembly method, lead times, fees, tax and final shipping are unknown. Board prices are indicative only, not complete PCBA costs.

The carrier stackup thickness warning, rails, finish and mechanical/process controls remain manufacturing holds. Preserve the r7 home-install list and LUTE/TRACO qualification requirements. No purchases, reservations, vendor messages, production approvals or manufacturing commitments were made.

## Continuation after assembly-terms authorization

The user explicitly authorized NEXT and acceptance of the assembly service terms for quote preparation. The two Gerber forms advanced to automatically saved JLC assembly drafts, and each r7 BOM and CPL was uploaded and processed:

- [Carrier draft: carrier-gerbers](https://cart.jlcpcb.com/smt-order/?pcbFileNo=d36999d20e3d4544a4e7d21e9b703b41): 5 fabricated / 2 assembled, Standard top-side PCBA.
- [Pod draft: pod-gerbers](https://cart.jlcpcb.com/smt-order/?pcbFileNo=71c384e886a94642a54e0c804cea3a97): 10 fabricated / 8 assembled, Standard top-side PCBA.

JLC displayed the specified LUTE fuse C7542926 on both BOMs, carrier TRACO TSR 1-2450 C6886877, ADC PCM1864DBTR C544855 and Samsung r7 capacitor codes. Their displayed MPN/code matches are evidence of portal matches, not independent manufacturer, package or engineering approval. JLC initially left repeated rows unchecked: carrier C4/C12/C22/C13/C23/C15/C25/C18/C28 for C1711 and C14/C24/C16/C26/C17/C27 for C710992; pod R5/R9/R10 for C844747. Each was selected using the exact already specified code and MPN. Portal confirmed-count labels became inconsistent (37 confirmed against 30 detected carrier rows; 23 against 21 pod rows), so do not interpret those counts as coverage proof. No substitution was made.

Carrier X1, CB3LV-3I-12M288000 / C17275161, shows 2 shortfall and no selectable part. Exact-MPN public-inventory search returned 0 JLCPCB stock, 0 idle stock, and 0 in the shown personal inventory pools. A matched MPN alone does not establish manufacturer; supplier identity and assembly method remain unverified. Proceeding from the carrier BOM produced a dialog offering “Do not place” or “Select parts”; chose Select parts and did not omit X1. Consequently the carrier placement preview, including U10 pin/body alignment, and full carrier PCBA quote remain blocked. Global sourcing/consignment terms and dates remain unverified; no procurement was initiated.

The pod placement viewer rendered a 3D top-side preview including F1 and J1. Visual presence is not a full pin/polarity/placement audit or production approval. The quote tab showed $42.24 PCB plus $119.74 Standard PCBA = **$161.98**, excluding shipping and tax. PCBA breakdown: setup $25.75; stencil $8.27; panel $0; large size $0; components (20 items) $32.77; feeder loading $29.45; SMT $1.40; placement confirmation $0.45; hand soldering $3.61; manual assembly $1.06; handling $16.47; packaging $0.51. PCB build 3 days; selected assembly 5–6 days, with $49.63 / $99.25 expedited choices. These figures are provisional and depend on unresolved identity, placement, rail and process review; no shipping or tax total is included. The earlier separate $26.94 shipping estimate was on the board screen and is not a final combined quote.

The home-install list remains unchanged. Carrier stackup acknowledgement, both rail/depaneling and finish controls, full manufacturer/package audit, physical preview, actual THT methods and LUTE/TRACO process qualification remain open. No orders, purchases, reservations, vendor messages or production approvals were made; no SAVE TO CART action was taken.

## Read-only TinyFish follow-up and coordinator review — 2026-11-01

Base: shared commit `3326fbaf272392b82ffb66a496190c6df14fdbf6`, fast-forwarded
without modifying the r7 package. Scope remains carrier 5 fabricated / 2 assembled
and pod 10 fabricated / 8 assembled. CTS remains unchanged and required.

### Exact clock sourcing: stock does not resolve assembly eligibility

[Browser run](https://agent.tinyfish.ai/runs/abc97a46-fef8-40c8-b375-80d9d9e73290)
reported the following at the signed-in
[Global Sourcing page](https://jlcpcb.com/user-center/smtPrivateLibrary/orderParts/?global=1):

| Exact CTS source | Reported distributor stock | MOQ | Indicative price | Procurement-to-warehouse lead |
| --- | ---: | ---: | --- | --- |
| DigiKey 110-CB3LV-3I-12M288000CT-ND | 1,449 | 1 | $2.1389 each at quantity 2; calculated $4.28, not a displayed two-piece quote | 8–14 business days |
| DigiKey 110-CB3LV-3I-12M288000TR-ND | 1,449, shared with CT; do not sum | 1,000 | $1,400 displayed minimum | 8–14 business days |
| Questcomp CB3LV-3I-12M288000 | 472 | 18 | $72.08 displayed minimum | 10–15 business days |

All three reportedly exposed a visible disabled-Add tooltip:
“This component is not available for purchase as it does not support PCB assembly.”
Treat this as a current portal eligibility blocker, not proof that the physical
part cannot be assembled. Seek factory clarification before sourcing. The tool
reported a lead-time tooltip excluding another 1–2 business days order review;
no usable-stock calendar date, job-specific purchase quantity or final fees were
confirmed. The displayed attrition value of zero does not establish zero required
spares. Reject the tool's erroneous $2,800 two-unit TR calculation and its claim
that the CT offer is purchasable despite the disabled Add button.

The [Global Sourcing terms](https://jlcpcb.com/help/article/global-sourcing-parts-order-terms-conditions)
make paid orders noncancelable/nonreturnable, require assembly eligibility review
and warehouse arrival before use, and retain minimum/attrition requirements.
Possible handling and other charges prevent treating component-only arithmetic
as a complete quote. No sourcing flow was initiated.

### Pod matching: useful evidence, incomplete acceptance

[Browser run](https://agent.tinyfish.ai/runs/72dec5ef-937d-4588-b07a-18903577a4ab)
reported 21 selected groups with matching designators, MPNs and JLC codes on the
correct pod draft, assembly quantity 8. R5 and R9/R10 remain separate groups
sharing C844747; supplier quantities may be pooled across those groups.

Coordinator corrections to the browser result:

- The source label JLCPCB is not the component manufacturer. Manufacturer/package
  verification was not completed by opening individual part details.
- Per-board BOM quantities cannot be directly compared to batch procurement
  quantities. For example U2 needs 8 installed, while R5/R9/R10 collectively need
  24. Reported quantities of 8 and 32 respectively are not evidence of a BOM
  mismatch; the latter's spare/fee basis remains unconfirmed. Do not call all
  displayed quantities multiples of eight; several are not.
- A normal matched J1 row does not prove the requested manual assembly route is
  wrong. A Basic library classification is not a component substitution.
- A BOM voltage requirement versus a higher-rated exact part is not automatically
  an electrical mismatch. No new C5 defect is established by this audit.
- This run found placement/quote tabs inaccessible. It did not revalidate the
  MacBook preview or $161.98 figure, nor establish that those observations were
  invalid. Polarity/pin placement acceptance remains open.

JLC's [assembly FAQ](https://jlcpcb.com/help/article/pcb-assembly-faqs) confirms
general through-hole/manual assembly support and says its Wave Soldering label
denotes manual assembly. This resolves the general capability question, not the
specific thermal handling or dimensional requirements of this job.

### Resolution boundary and next action

Fresh `python3 projects/crow-array/order-readiness/r7_quote.py verify` returned
PASS for 97 files, `production_ready: false`. No design/package edits. Do not
repeat inventory searches to solve an assembly-eligibility restriction. No
manufacturer or placement acceptance is inferred from row counters or package
hash verification.

Preferred next step: user-authorized, non-binding JLC inquiry below, preserving
CTS and all installed requirements. Second choice: user-authorized qualification
of a stocked clock alternative; this is not currently authorized and requires
electrical/footprint review. External consignment alone does not establish JLC
will assemble the same clock. Moving it to home assembly also requires an
explicit work-split decision; do not silently omit X1.

### Proposed JLC inquiry — UNSENT, requires user authorization

Please review these existing drafts for a non-binding quotation only:
carrier d36999d20e3d4544a4e7d21e9b703b41 (5 fabricated / 2 assembled) and
pod 71c384e886a94642a54e0c804cea3a97 (10 fabricated / 8 assembled).
Do not purchase, reserve, substitute, omit parts or start manufacturing.

1. Carrier X1 is CTS CB3LV-3I-12M288000, two installed. Your Global Sourcing
   DigiKey cut-tape SKU 110-CB3LV-3I-12M288000CT-ND shows stock but a disabled Add
   tooltip saying PCB assembly is unsupported. Is this a catalog restriction,
   packaging issue or actual assembly prohibition? Can you assemble this exact
   part by a manufacturer-compatible process? Please specify required procurement
   quantity including attrition, all charges and usable warehouse lead time.
2. Please provide a way to inspect both complete placement previews and obtain
   itemized pricing without excluding X1 or committing to a noncancelable order.
   Confirm exact manufacturers/packages, including LUTE C7542926 and TRACO
   C6886877, and pooled R5/R9/R10 quantity/attrition on the pod.
3. Please reconcile carrier JLC04161H-7628A (published nominal 1.5542 mm, offered
   ±10%) and pod JLC04161H-7628 with the supplied job controls. Confirm proposed
   two 5 mm rail geometry, delivery/removal and finished-edge requirements.
   Do not treat the thickness acknowledgement as a waiver of finished-hole,
   seating, lead preparation, pose or other retained mechanical requirements.
4. Please confirm the actual assembly processes for RJ jacks, power jacks and
   TRACO TSR 1-2450, and compatibility with the retained LUTE reflow/no-whole-board-
   wave restrictions and manufacturer thermal limits. Request the applicable
   control documents if unavailable; do not infer acceptance from this summary.
   Picos, microphones and buzzers remain home installed. Keep production-file
   and placement review manual, with no automatic confirmation.

This draft has not been sent. No purchase, reservation, substitution, order,
production approval or manufacturing commitment occurred. Follow-up findings
are local and not yet published.
