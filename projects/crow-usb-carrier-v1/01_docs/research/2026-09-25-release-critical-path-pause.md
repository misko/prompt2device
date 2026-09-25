# Crow release critical path — 2026-09-25

**Engineering strategy pause; no design or release admission.** The current
checkpoint remains `prototype-layout-diagnostic`. The TI board
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`
is unrouted with 499 native opens. These experiments do not replace the locked
part-selection stock screen, reopen inventory, or change canonical Crow source.

| Gate | Current evidence | Next discriminating test |
| --- | --- | --- |
| USB P1 accounting | The independently replayed two-physical DP/DN plus unresolved VBUS/presence packet has zero USB coarse diagnostics, exact terminal denominators, and `p1_accepted: false` ([packet](2026-09-25-ti-usb-two-physical-vbus-branch-sol/README.md), [review](2026-09-25-ti-usb-two-physical-vbus-branch-review-terra.md)). The data path has only rough 2/2 and 3/2 stage slots. VBUS has null physical capacity. | Preserve the single linked data path and explicit VBUS trees. Prove the two fused VBUS launch sites and their current/return constraints after the CC-ESD collision is resolved; then route and grade P2/P3. Do not add another top-level USB reservation. |
| ADC/audio macro placement | All 54 timing pads across 14 nets are counted, but four two-terminal crossings and misowned `AUDIO_EN` pads still fail closed ([ledger](2026-09-25-ti-adc-timing-complete-probe-sol.md), [negative packet](2026-09-25-ti-adc-timing-all14-accounting-sol/README.md)). Channels 7/8 and TDM/XU need coupled ownership changes ([map](2026-09-25-ti-adc78-tdm-xu-joint-refloorplan-map-terra.md)). | Repartition the complete audio/TDM, ADC7/8 and XU-west neighborhood, keeping all fixed refs. For each candidate require full native-envelope ownership, local bypass/oscillator distances, exact 54-pad denominator, four-net neck access, and explicit filled-return debt. Reject a layout that clears a portal by moving critical support parts away from their ICs. |
| Tested local escapes | A three-ref direct-lane move creates five rough slots but moves an XU decoupler's nearest same-net pad from 2.783 to 6.811 mm ([probe](2026-09-25-ti-tdm-xu-three-ref-candidate-sol.md)). A 16-mm south extension fits three audio parts, but related-pad distances become 45–77 mm and the GND plane still ends at the old edge ([probe](2026-09-25-ti-south-audio-cell-probe-sol/README.md)). | Treat both as rejected electrical placements. Test whole-group refloorplan candidates rather than more isolated corridor or outline edits. The board outline is an initial assumption, not a size maximum; any size change must carry its related circuitry and reference plane with it. |
| Power P1 | Five power witnesses can be rewritten as local virtual faces without capacity credit. Four cross-region handoffs lack a valid source-owned transition ([audit](2026-09-25-power-boundary-window-diagnostic-terra.md), [repair](2026-09-25-power-boundary-local-witness-repair-terra.md)). | After the macro floorplan settles, declare exact shared transition ownership or a power-specific integration contract, with current/return obligations, then rerun the native check. |
| Connector physical FULL | A four-layer, 1.60-mm nominal edge-registration coupon candidate exists, but is unmeasured, lacks an exact mate/edge tolerance, and does not establish equivalence to the board's 1.63-mm KiCad target ([coupon](usb4215_edge_registration_coupon_4l_target_terra/process_target_measurement_record.md)). | Bind the intended mating plug/enclosure and fabricator stackup, then set measurable edge/slot/seating limits before any physical qualification. No coupon or PCB fabrication is authorized by this note. |
| USB ESD release boundary | The selected TI TVS remains `PROTOTYPE_ONLY`; public XMOS records do not give a powered/rail-off USB-pad transient envelope for numeric coordination ([D13 analysis](2026-09-24-ti-xu316-usb-esd-coordination-sol.md)). | Obtain applicable XMOS limits or an owner-approved exact-board powered/off stress qualification. Until then design-clean/release remains blocked regardless of routing. |

## Execution order

1. Decide the available board/mate envelope. Keep current fixed connector and
   other P1-fixed poses until a reviewed mechanical change is authorized.
2. Build one **isolated macro refloorplan** for ADC7/8, audio/TDM, XU-west,
   and their support parts. Measure electrical proximity and all native
   envelope/region ownership before editing canonical P1 source. Abandon a
   candidate on the first real contradiction.
3. Bind exact source handoffs on that candidate, including the four power
   transitions. Re-run the complete P1 diagnostic census and independent
   review. An `INCOMPLETE` coarse screen is evidence of debt, not acceptance.
4. Only after P1 engineering admission, proceed through block placement,
   critical local routing, joint proof, connector FULL and exact-board
   electrical qualification. Then run native DRC, fabrication/assembly review,
   release rehearsal and seal checks. Physical orders remain a separate action.

The next design decision is macro placement, not another stock screen or a
new generic checker exception. Any broadened outline is a design option to
test, not a way to waive local placement or return-plane evidence.
