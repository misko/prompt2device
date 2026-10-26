# DRAFT — NOT SENT — Crow prototype feasibility and itemized quotation

Local workflow note: use the normal JLC catalog/BOM-matching workflow first.
This draft is a contingency checklist for concrete unresolved exceptions, not a
requirement to contact support before checking parts. Do not send it wholesale
without reviewing which questions remain and obtaining contact authority.

Please evaluate a prototype batch of **5 carrier PCBs and 10 microphone pod PCBs**.
These are two designs; not five complete eight-pod systems. Please return an
item-by-item accept/decline/clarification response before any manufacturing or
procurement commitment. No substitution or production-data edit is approved.

Public design reference:
https://github.com/misko/prompt2device/tree/5ddd8d796bdbaeb51476c8835986f681f24b67c1/projects/crow-array/releases/crow-prototype-v3-first-run-5c10p-public-v1

This is a public subset, not the complete manufacturing/engineering evidence
archive. A formal submission must include complete approved controls and exact
board/fab/BOM/CPL identities; this inquiry is not permission to manufacture.

1. **Fabrication feasibility:** evaluate exact carrier 7628A and pod 7628 stack
   requirements, finish, shaped profiles, rail/tooling/fiducial plan and all-layer
   copper clearances. Confirm which precision options, panelization and inspection
   are necessary; do not change functional profiles/copper/holes without review.
   Priority constraints include RJ contact holes 0.89 ±0.05 mm and pegs
   3.25 ±0.05 mm; carrier PJ finished openings 1.60–1.73 mm with the complete
   maker ±0.05-mm pitch pattern; Pico A/B reliefs 2.50–2.65 mm and C/D reliefs
   2.15–2.30 mm, with combined webs/clearances and positioning limits. Complete
   LS43 integrated controls and LS33 module controls, not this summary, govern.
   Please identify any requirement unavailable under standard or custom service.
2. **SMT and stencil workflow:** 915 top-side placements, 32 exact manufacturer/
   MPN identities, 5/10 quantities. Existing consigned BOM/CPL files describe a
   proposal; factory BOMs are empty and are not upload-ready matching records.
   Can each exact identity use existing JLC stock, global sourcing or customer
   consignment? Provide usable quantity, lead time, MOQ, packaging/feeder extras,
   loss allowance and cost separately. Do not sum incompatible inventory pools.
   Manual components will be excluded from the selected SMT population, matching
   your published no-paste policy for unselected/THT positions. Explain how the
   remaining accepted aperture requirements can be reconciled with your optimized
   stencil-generation process; any revised
   process needs review before adoption. Provide placement/orientation previews
   for approval and compatible profiles, including the carrier R3 reflow limit.
3. **Requested manual completion — price separately:** 60 parts: 50 RJHSE-5080
   jacks, 5 PJ-102AH and 5 RECOM R-78E5.0-0.5 modules. Can you source, perform
   and inspect each operation under the released manual assembly controls?
   The purchaser will install 10 CMA-4544PF-W microphones, 10 CPE-203 buzzers
   and five original SC0915 Picos after JLC processing. Exclude all 25 from JLC
   placement and paste; leave their through-holes open for later installation.
   User-part procurement is separate; no loose-part shipment is assumed. The purchaser's
   existing D1-only preparation and module inspection obligations remain; carrier
   relief holes and other fabrication requirements are unchanged.
   Acoustic parts will receive hand-only soldering, with no reflow/wave/wash,
   by the purchaser. Confirm metrology/inspection ownership for finished holes, seating,
   polarity, pose and solder limits. No programming or functional acquisition
   qualification is requested in this prototype assembly quote.
4. **Fallback quote:** if special manual work is unavailable, quote fabrication
   and SMT only, stating which parts and operations are excluded for a separate
   assembler. Do not assign declined operations to the purchaser without a new
   decision. Do not assume loose consigned components can ship with the boards.
5. **Commercial scope:** separately itemize components, bare fabrication/setup,
   stencil/fixtures, SMT, manual modification/completion, inspection, procurement
   fees, shipping and tax. State validity and lead times. Shipping destination
   and final tax/currency details are to be supplied by the purchaser. Do not
   interpret this request as purchase authorization or approval of an estimate.

Required response before commitment: accepted process/inspection scope, exact
parts/allocation route, reviewed production previews, exception list and quote.
Please make exceptions explicit so the design owner can review affected evidence.

Local preparation note, 2026-10-26: this remains NOT SENT. The literature review
in `JLC-CAPABILITY-REVIEW-20261026.md` recommends first reviewing the necessity of
designer-imposed tight limits against ordinary production tolerances. Do not
transmit waived or revised limits without engineering acceptance.

## Exact sourcing route, not a shortage request

Public exact-part availability evidence now covers the earlier exceptions:
JLC C89347 TPS70933DBVR (10 required), C154917 BZT52C3V9-7-F (80), C84494
GRM32ER71A476KE15L (10), and C599441 RJHSE-5080 (50); LCSC C97962
GRM31MR71E225KA93L (80) and C83574 BAT54S-7-F (20); Bürklin 75D7535
C3216X7R1V106K160AC (10); and DigiKey P68.0HCT-ND ERJ-3EKF68R0V (5).
These observations are not reservations or confirmation of JLC-usable stock.
Please establish exact maker/MPN, usable quantities, extra material allowance,
packaging and sourcing route for the complete batch. Do not substitute
automatically or assume overseas, presale and PCBA stock are interchangeable.
The local `SOURCING-RECOVERY-20261026.md` records evidence and freshness limits.

## Public-policy crosscheck — 2026-10-26

Current [rigid capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)
list ordinary through-hole +0.13/−0.08 mm, position ±0.075 mm, and ±0.05 mm
press-fit holes only within 0.55–2.0 mm on multilayer ENIG circular holes. These
defaults do not establish our complete finished-hole requirements. Both boards
meet the published 50 × 50 mm precision-profile minimum; panel/tooling conditions
and exact geometry still require review for both designs.

The [stencil workflow](https://jlcpcb.com/help/article/smt-stencil-data-prepared-for-smt-orders)
generates optimized apertures rather than simply using submitted paste Gerbers;
custom requirements can be conveyed for review. Compatibility remains unconfirmed.

[Personalized services](https://jlcpcb.com/help/article/jlcpcb-supported-personalized-services)
support some manual/jig-assisted operations, but do not confirm the requested
60-part job or complete precision inspection. Pico modification is purchaser-owned.
[Consignment terms](https://jlcpcb.com/help/article/consignment-part-terms-conditions)
separate inventory pools and say unassembled consigned parts cannot accompany
PCBs. These are capability leads, not exact-job acceptance or a quotation.
