# JLC r7 MacBook session — 2026-11-01

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
