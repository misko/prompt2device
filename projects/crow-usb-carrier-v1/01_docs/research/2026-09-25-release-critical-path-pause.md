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
| ADC analog boundary | The old wide nine-slot reservations overlap the ADC7 portal. Exact accounting finds 18 nets/88 native pads. Sixteen ADC N/P nets fit geometry-free, null-capacity branch debt; both VMID nets fail source-owner containment at eight resistor pads, and `ADC8N` has a foreign-region capacitor ([negative packet](2026-09-25-ti-adc-analog-88-accounting-sol/README.md)). A 15-part coupled board restores endpoint owner/foreign containment but leaves only 0.005 mm at two ADC8-cap cell edges and adds 21 silk warnings, so independent review rejects it for P2 as placed ([candidate](2026-09-25-ti-vmid-coupled-ch8-sol/README.md), [review](2026-09-25-ti-vmid-coupled-ch8-terra-review.md)). A bounded cap move with other parts fixed finds no positive-mouth pose under exploratory locality screens, and a two-cell recut leaves other members unassigned ([bound](2026-09-25-ti-ch8-margin-repair-bound-sol/README.md)). Functional ownership may span several physical cells, but the exact J8 connector pocket needs an overhang model and mechanical evidence ([review](2026-09-25-ti-ch8-owner-pocket-review-sol.md)). | Redesign the complete channel-8 physical partition with local support placement and exclusive USB neighbors; retain J8's functional owner and fixed pose. Require a usable cap entry, full member accounting, and continuous return before P2. Keep branch and portal records at zero route/capacity credit until P2/P3 prove each path. |
| Tested local escapes | A three-ref direct-lane move creates five rough slots but moves an XU decoupler's nearest same-net pad from 2.783 to 6.811 mm ([probe](2026-09-25-ti-tdm-xu-three-ref-candidate-sol.md)). A 16-mm south extension fits three audio parts, but related-pad distances become 45–77 mm and the GND plane still ends at the old edge ([probe](2026-09-25-ti-south-audio-cell-probe-sol/README.md)). | Treat both as rejected electrical placements. Test whole-group refloorplan candidates rather than more isolated corridor or outline edits. The board outline is an initial assumption, not a size maximum; any size change must carry its related circuitry and reference plane with it. |
| Power P1 | Five of nine witnesses replay as local virtual faces without capacity credit. Four cross-region power nets have 42/27/68/34 native endpoints. A one-pad shared-port probe falsely cleared their diagnostics; the checker now rejects it for missing the full power-net denominator ([replay](2026-09-25-unified-power-boundary-replay-terra.md)). | Keep the five exact P2 pad-to-face debts. Account for all terminals on the four remaining nets with no-credit branch records, or implement a reviewed power transition schema with separate entry subset, all-terminal local debt, current, thermal and filled-return proof before claiming a physical handoff. |
| Connector physical FULL | A four-layer, 1.60-mm nominal edge-registration coupon candidate exists, but is unmeasured, lacks an exact mate/edge tolerance, and does not establish equivalence to the board's 1.63-mm KiCad target ([coupon](usb4215_edge_registration_coupon_4l_target_terra/process_target_measurement_record.md)). | Bind the intended mating plug/enclosure and fabricator stackup, then set measurable edge/slot/seating limits before any physical qualification. No coupon or PCB fabrication is authorized by this note. |
| USB ESD release boundary | The selected TI TVS remains `PROTOTYPE_ONLY`; public XMOS records do not give a powered/rail-off USB-pad transient envelope for numeric coordination ([D13 analysis](2026-09-24-ti-xu316-usb-esd-coordination-sol.md)). XMOS's XU316 reference schematics name `NUP4114`, but do not publish the missing limit or a transferable Crow qualification ([reference review](2026-09-25-xmos-xu316-usb-esd-reference-topology-terra.md), [alternate part disposition](2026-09-25-nup4114-alternate-disposition-sol.md)). | Obtain applicable XMOS limits or an owner-approved exact-board powered/off stress qualification. Until then design-clean/release remains blocked regardless of routing. |

The checked-in ordinary netlist still names the earlier Nexperia USB ESD part.
An isolated governed TSX rebuild produces the selected TI part, and its fresh
native board matches the frozen TI research board on all 569 footprint and pad
identities and shapes; the reviewed `Q_PRE` pose is the only board pose change
([source-to-native audit](2026-09-25-ti-usb-esd-pad-authority-sol.md)). TI's land
drawing does not mandate square corners, so the native roundrect footprint
does not require a D13 change. Shape-sensitive placement work must use the
fresh TI native source/profile rather than the stale ordinary netlist.

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
