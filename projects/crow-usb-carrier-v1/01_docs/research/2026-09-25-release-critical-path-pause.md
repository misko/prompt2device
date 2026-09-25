# Crow release critical path — 2026-09-25

**Engineering strategy pause; no design or release admission.** The current
checkpoint remains `prototype-layout-diagnostic`. The TI board
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`
is unrouted with 499 native opens. These experiments do not replace the locked
part-selection stock screen, reopen inventory, or change canonical Crow source.

| Gate | Current evidence | Next discriminating test |
| --- | --- | --- |
| USB P1 accounting | The independently replayed two-physical DP/DN plus unresolved VBUS/presence packet has zero USB coarse diagnostics, exact terminal denominators, and `p1_accepted: false` ([packet](2026-09-25-ti-usb-two-physical-vbus-branch-sol/README.md), [review](2026-09-25-ti-usb-two-physical-vbus-branch-review-terra.md)). The data path has only rough 2/2 and 3/2 stage slots. VBUS has null physical capacity. | Preserve the single linked data path and explicit VBUS trees. Prove the two fused VBUS launch sites and their current/return constraints after the CC-ESD collision is resolved; then route and grade P2/P3. Do not add another top-level USB reservation. |
| ADC/audio macro placement | All 54 timing pads across 14 nets are counted, but four two-terminal crossings and misowned `AUDIO_EN` pads still fail closed ([ledger](2026-09-25-ti-adc-timing-complete-probe-sol.md), [negative packet](2026-09-25-ti-adc-timing-all14-accounting-sol/README.md)). A local four-part move improves ADC7 portal margin to 0.255 mm without moving fixed refs ([candidate](2026-09-25-ti-adc7-four-part-margin-sol/README.md)), but close courtyards remain and source-level silk cleanup leaves 11/13 affected labels ambiguously nearer other parts ([probe](2026-09-25-ti-adc7-source-silk-probe-sol/README.md), [follow-up](2026-09-25-ti-adc7-source-silk-probe-sol/ownership_followup.md)). | Build a coupled ADC7/8, audio/TDM and XU-west floorplan candidate with a real ADC7 mouth, related-part proximity, readable labels and filled-return path. Preserve all fixed refs and the exact 54-pad timing denominator. Do not promote the local four-part move on DRC cleanliness alone. |
| ADC analog boundary | The old wide nine-slot reservations overlap the ADC7 portal. Exact accounting finds 18 nets/88 native pads. Sixteen ADC N/P nets fit geometry-free, null-capacity branch debt; both VMID nets fail source-owner containment at eight resistor pads, and `ADC8N` has a foreign-region capacitor ([negative packet](2026-09-25-ti-adc-analog-88-accounting-sol/README.md)). With all other parts fixed, a nine-part search fails an exploratory locality screen ([bound](2026-09-25-ti-vmid-eight-part-bound-sol/README.md)). A 15-part coupled board restores exact owner/foreign containment but leaves only 0.005 mm at two ADC8-cap cell edges and adds 21 silk warnings, so independent review rejects it for P2 as placed ([candidate](2026-09-25-ti-vmid-coupled-ch8-sol/README.md), [review](2026-09-25-ti-vmid-coupled-ch8-terra-review.md)). | Test a typed channel-8/USB cell recut together with local support placement for a usable cap entry and return mouth; reject a merely nonoverlapping envelope. Re-run the full checker; keep branch and portal records at zero route/capacity credit until P2/P3 prove each path. |
| Tested local escapes | A three-ref direct-lane move creates five rough slots but moves an XU decoupler's nearest same-net pad from 2.783 to 6.811 mm ([probe](2026-09-25-ti-tdm-xu-three-ref-candidate-sol.md)). A 16-mm south extension fits three audio parts, but related-pad distances become 45–77 mm and the GND plane still ends at the old edge ([probe](2026-09-25-ti-south-audio-cell-probe-sol/README.md)). | Treat both as rejected electrical placements. Test whole-group refloorplan candidates rather than more isolated corridor or outline edits. The board outline is an initial assumption, not a size maximum; any size change must carry its related circuitry and reference plane with it. |
| Power P1 | Five power witnesses can be rewritten as local virtual faces without capacity credit. Four cross-region handoffs lack a valid source-owned transition ([audit](2026-09-25-power-boundary-window-diagnostic-terra.md), [repair](2026-09-25-power-boundary-local-witness-repair-terra.md)). | After the macro floorplan settles, declare exact shared transition ownership or a power-specific integration contract, with current/return obligations, then rerun the native check. |
| Connector physical FULL | A four-layer, 1.60-mm nominal edge-registration coupon candidate exists, but is unmeasured, lacks an exact mate/edge tolerance, and does not establish equivalence to the board's 1.63-mm KiCad target ([coupon](usb4215_edge_registration_coupon_4l_target_terra/process_target_measurement_record.md)). | Bind the intended mating plug/enclosure and fabricator stackup, then set measurable edge/slot/seating limits before any physical qualification. No coupon or PCB fabrication is authorized by this note. |
| USB ESD release boundary | The selected TI TVS remains `PROTOTYPE_ONLY`; public XMOS records do not give a powered/rail-off USB-pad transient envelope for numeric coordination ([D13 analysis](2026-09-24-ti-xu316-usb-esd-coordination-sol.md)). | Obtain applicable XMOS limits or an owner-approved exact-board powered/off stress qualification. Until then design-clean/release remains blocked regardless of routing. |

## Execution order

1. Decide the available board/mate envelope. Keep current fixed connector and
   other P1-fixed poses until a reviewed mechanical change is authorized.
2. Build an **isolated coupled refloorplan** for ADC7/8, audio/TDM, XU-west,
   and the channel-8 support parts. The four-part and nine-part local screens
   bound smaller moves but are not accepted placements. Measure electrical
   proximity, assembly-label legibility, native pad access, and all envelope/
   region ownership before editing canonical P1 source.
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
