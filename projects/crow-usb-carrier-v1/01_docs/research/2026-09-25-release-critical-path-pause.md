# Crow release critical path — 2026-09-25

**Engineering strategy pause; no design or release admission.** The current
checkpoint remains `prototype-layout-diagnostic`. The TI board
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`
is unrouted with 499 native opens. These experiments do not replace the locked
part-selection stock screen, reopen inventory, or change canonical Crow source.

| Gate | Current evidence | Next discriminating test |
| --- | --- | --- |
| Physical block authority | A native 569-ref census finds 115 parts outside their functional owner's broad primary rectangle and 139 parts entering a foreign planning region. There are no cross-owner body/pad overlaps; one 0.020-mm courtyard corner collision between `C_IN3` and `Q_PRE` was removed by a reviewed 0.30-mm `Q_PRE` source move ([census](2026-09-25-ti-global-owner-census-terra/README.md), [repair](2026-09-25-ti-cin3-qpre-owner-repair-sol/README.md), [review](2026-09-25-cin3-qpre-owner-repair-review-terra.md)). | Regenerate a new exact research board from the updated source, then replace broad overlapping planning rectangles with exclusive physical pockets and explicit handoffs. Fixed connector overhangs need their own evidence; a collision-free placement alone gives no route or P1 credit. |
| Unified P1 admission | One hash-bound native replay now combines USB, ADC analog, ADC7 portal, timing and power on the same 15-part research board. USB and all 18 ADC analog nets have exact no-credit accounting; P1 still `FAIL`s on five timing source/accounting items and nine power witnesses, with nine derivative global denominator errors ([packet](2026-09-25-ti-unified-p1-diagnostic-sol/README.md), [independent review](2026-09-25-ti-unified-p1-review-terra.md)). The 15-part board itself is rejected for P2 as placed. | Repair the timing physical handoffs and power source-owned transitions on a viable floorplan, then rebuild one unified packet and recheck every denominator. A cleaner `INCOMPLETE` diagnostic is not P1 engineering admission. |
| USB P1 accounting | The independently replayed two-physical DP/DN plus unresolved VBUS/presence packet has zero USB coarse diagnostics, exact terminal denominators, and `p1_accepted: false` ([packet](2026-09-25-ti-usb-two-physical-vbus-branch-sol/README.md), [review](2026-09-25-ti-usb-two-physical-vbus-branch-review-terra.md)). The data path has only rough 2/2 and 3/2 stage slots. VBUS has null physical capacity. | Preserve the single linked data path and explicit VBUS trees. Prove the two fused VBUS launch sites and their current/return constraints after the CC-ESD collision is resolved; then route and grade P2/P3. Do not add another top-level USB reservation. |
| ADC/audio macro placement | All 54 timing pads across 14 nets are counted, but four two-terminal crossings and misowned `AUDIO_EN` pads still fail closed ([ledger](2026-09-25-ti-adc-timing-complete-probe-sol.md), [negative packet](2026-09-25-ti-adc-timing-all14-accounting-sol/README.md)). A coupled 46-pose TI research board now preserves all 27 fixed refs, clears the ADC7 portal, has zero cross-owner native collision pairs, and retains three rough timing mouths ([candidate](2026-09-25-ti-integrated-placement-sol/README.md)). Its exact project-rule replay gives the same 213 DRC issue identities and 499 opens as baseline; the earlier 699-issue bare-board comparison omitted Crow's POFV rule profile ([profile replay](2026-09-25-ti-iso8-profile-replay-sol/README.md), [independent correction](2026-09-25-ti-integrated-placement-review-terra.md)). The candidate still has a 0.005-mm ADC8 cap owner margin, 28 source-unencoded label moves and no filled return or routes. | Rebaseline the integrated candidate against the fresh governed TI native source, then redesign the pinched channel-8 support pocket and source-encode readable labels. Preserve all fixed refs and the exact 54-pad timing denominator; prove local return and complete P1 handoffs before promoting placement. |
| ADC analog boundary | Exact accounting finds 18 nets/88 native pads. In the full-profile 46-pose TI research union, a 0.20-mm southwest `C_ADC_AC8N1` move raises both concerned owner/USB margins from 0.005 to 0.205 mm, preserves all 27 fixed refs and 569 pad identities, and leaves the 213 DRC issue identities/499 opens unchanged ([source-generated replay](2026-09-25-ti-adc8-cap-integrated-replay-sol/README.md), [independent review](2026-09-25-ti-adc8-cap-integrated-review-terra.md)). A 15.180-mm local ADC8N F.Cu route now joins two exact pads with continuous filled In1 GND reference and no added full-profile DRC issues, but it crosses 3.96 mm of `usb_vbus_sense` planning region and leaves two ADC8N pads unjoined ([route](2026-09-25-ti-adc8n-local-route-sol/README.md), [review](2026-09-25-ti-adc8n-local-route-review-terra.md)). The 36-ref physical-cell lower bound is **UNSAT**: fixed J8's full envelope starts at y=19.955 while the board starts at y=20.000 ([probe](2026-09-25-ti-adc8-exclusive-cell-unsat-sol/README.md)); eleven other channel-8 refs hit foreign planning rectangles. | Mechanically qualify J8's exact overhang/mate and review a narrow connector-cell exception or outline/connector redesign; recut channel-8 and neighboring cells with all 36 refs accounted for, including the ADC8N/USB-sense crossing. Then bind all 88 ADC endpoints and continuous filled return before P2. Promote the cap and route only with that coupled source model; branch and portal records retain zero route/capacity credit until P2/P3 prove each path. |
| Tested local escapes | A three-ref direct-lane move creates five rough slots but moves an XU decoupler's nearest same-net pad from 2.783 to 6.811 mm ([probe](2026-09-25-ti-tdm-xu-three-ref-candidate-sol.md)). A 16-mm south extension fits three audio parts, but related-pad distances become 45–77 mm and the GND plane still ends at the old edge ([probe](2026-09-25-ti-south-audio-cell-probe-sol/README.md)). | Treat both as rejected electrical placements. Test whole-group refloorplan candidates rather than more isolated corridor or outline edits. The board outline is an initial assumption, not a size maximum; any size change must carry its related circuitry and reference plane with it. |
| Power P1 | Five of nine witnesses replay as local virtual faces without capacity credit. Four cross-region power nets have 42/27/68/34 native endpoints. A one-pad shared-port probe falsely cleared their diagnostics; the checker now rejects it for missing the full power-net denominator ([replay](2026-09-25-unified-power-boundary-replay-terra.md)). | Keep the five exact P2 pad-to-face debts. Account for all terminals on the four remaining nets with no-credit branch records, or implement a reviewed power transition schema with separate entry subset, all-terminal local debt, current, thermal and filled-return proof before claiming a physical handoff. |
| Connector physical FULL | A four-layer, 1.60-mm nominal edge-registration coupon candidate exists, but is unmeasured, lacks an exact mate/edge tolerance, and does not establish equivalence to the board's 1.63-mm KiCad target ([coupon](usb4215_edge_registration_coupon_4l_target_terra/process_target_measurement_record.md)). | Bind the intended mating plug/enclosure and fabricator stackup, then set measurable edge/slot/seating limits before any physical qualification. No coupon or PCB fabrication is authorized by this note. |
| USB ESD release boundary | The selected TI TVS remains `PROTOTYPE_ONLY`; public XMOS records do not give a powered/rail-off USB-pad transient envelope for numeric coordination ([D13 analysis](2026-09-24-ti-xu316-usb-esd-coordination-sol.md)). XMOS's XU316 reference schematics name `NUP4114`, but do not publish the missing limit or a transferable Crow qualification ([reference review](2026-09-25-xmos-xu316-usb-esd-reference-topology-terra.md), [alternate part disposition](2026-09-25-nup4114-alternate-disposition-sol.md)). | Obtain applicable XMOS limits or an owner-approved exact-board powered/off stress qualification. Until then design-clean/release remains blocked regardless of routing. |

The guarded prototype-only schematic adoption has now replaced the stale
Nexperia generated circuit, PDF, native schematic, and netlist with one exact
TI bundle ([receipt and netlist](2026-09-25-ti-prototype-schematic-adoption/README.md),
[independent post-execution review](2026-09-25-prototype-schematic-adoption-postexecution-review-terra.md)).
E-FAULT, P-PREC and ERC pass on that schematic subject. The ordinary schematic
checkpoint, pinned reuse schematic, PCB and release remain unchanged and
unaccepted; ordinary critical-selection admission still rejects
`PROTOTYPE_ONLY`. The native TI board matches the frozen TI research board on
all 569 footprint and pad identities and shapes, with the reviewed `Q_PRE`
pose the only board pose change ([source-to-native audit](2026-09-25-ti-usb-esd-pad-authority-sol.md)).
TI's land drawing does not mandate square corners, so the native roundrect
footprint does not require a D13 change. Future shape-sensitive placement work
must bind this TI source/profile and obtain fresh canonical topology/render
review before ordinary schematic-stage promotion.

J8's existing connector contract already selects Würth `615008160221` with
Telegärtner `100009141` as mate. Its 0.045-mm nominal envelope overhang can be
recorded as CAD-bound planning evidence, but a checker-consumable named J8
edge-cell exception needs measured edge registration/seating bound to that
exact board and connector ([measurement plan](2026-09-25-j8-edge-overhang-evidence-plan-terra.md),
[schema proposal](2026-09-25-j8-edge-cell-contract-proposal-sol.md),
[independent contract review](2026-09-25-j8-edge-cell-contract-review-terra.md)).
Even a measured cell would remain `INCOMPLETE`; connector FULL requires the
separate mate/service/group qualification. Do not treat the digital connector
fit prototype or an unrelated USB coupon as physical J8 evidence.

## Execution order

1. Decide the available board/mate envelope. Keep current fixed connector and
   other P1-fixed poses until a reviewed mechanical change is authorized.
2. Rebuild the coupled ADC7/8, audio/TDM and XU-west research placement from
   the current governed TI native source with its complete project rules and
   post-generation process areas. Repair the channel-8 support pocket and
   source-encode legible reference labels; measure electrical proximity,
   native pad access, filled return, and all envelope/region ownership before
   editing canonical P1 source.
3. Bind exact source handoffs on that candidate, including the four power
   transitions. Re-run the complete P1 diagnostic census and independent
   review. An `INCOMPLETE` coarse screen is evidence of debt, not acceptance.
4. Only after P1 engineering admission, proceed through block placement,
   critical local routing, joint proof, connector FULL and exact-board
   electrical qualification. Then run native DRC, fabrication/assembly review,
   release rehearsal and seal checks. Physical orders remain a separate action.

The next design decision is the coupled refloorplan's exact ownership and
support-part placement. This does not reopen the locked stock screen. Any
broadened outline is a design option to test, not a way to waive local
placement or return-plane evidence.
