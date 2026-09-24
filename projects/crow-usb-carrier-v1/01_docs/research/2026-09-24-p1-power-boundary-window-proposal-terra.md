# P1 power-boundary window proposal

## Scope and inputs

This is a source-owned floorplan reservation proposal for the nine nets in `p1_corridor_requirements.yaml`. It is not copper, a current-capacity result, a thermal result, a P1 receipt, or authority to dispatch P1.

The proposed coordinates are in board mm and are bounded by the current source floorplan SHA-256 `4a457c731c204084a83aa817a29ca8fc8acc07097723adefedc296eb4db37b98`. They were checked against the available isolated P2-derived native board `06_build/modular/p2_input_power_full_a1/review_packet/derived_pofv.kicad_pcb` (SHA-256 `75935c42631f44ca7abc324e21601b7a9aa51503f621fba32ac868c9d897e405`). That board is an unrouted P2 review artifact, not the canonical board and not an acceptable P1 board. The present power contract is SHA-256 `8a15377a61f37c4bc1f204f55170e50c2227fd779dacc6ab05fe4d39cd975ba0`.

The source already declares these physical block envelopes:

| Source cell | Bbox |
|---|---|
| input buck | `[25, 85, 70, 110]` |
| quiet-power and held-bank handoff | `[24, 105, 126, 137]` |
| ADC/reference | `[125, 85, 145, 125]` |
| digital power | `[145, 85, 185, 134]` |
| XU package entry (native body) | `[199.825, 91.325, 217.175, 108.675]` |

The P2 board confirms the important anchor locations: U_BUCK at `(47.500, 97.500)`, U_LDO at `(132.500, 118.200)`, U_3V3X at `(176.300, 105.400)`, U_1V8 at `(170.800, 119.500)`, U_CORE at `(153.300, 113.800)`, and U_XU at `(208.500, 100.000)`. Its 14 tracks make it unsuitable for a copper-capacity inference.

## Proposed source geometry

Add a non-null `geometry` map below `power_boundary_windows`; use a multi-window schema rather than `through_lane`, slots, or a scalar width. Each bbox is a reservation envelope and must remain explicitly `status: INCOMPLETE`. A window records which source cell is to remain available to the named net; it does not reserve a trace centerline or claim that the rectangle is free of bodies, pads, copper, rule areas, or pours.

```yaml
geometry:
  schema: crow-power-boundary-windows-v1
  coordinate_system: board-mm-bbox-[x0,y0,x1,y1]
  status: INCOMPLETE
  windows:
    - {id: gnd_input_return, net: GND, bbox: [25, 85, 70, 110], role: input-buck-local-return-reservation}
    - {id: gnd_hold_return, net: GND, bbox: [24, 105, 126, 137], role: held-bank-and-quiet-power-return-reservation}
    - {id: gnd_adc_return, net: GND, bbox: [125, 85, 145, 125], role: ldo-adc-local-return-reservation}
    - {id: gnd_digital_return, net: GND, bbox: [145, 85, 185, 134], role: regulator-and-digital-local-return-reservation}
    - {id: gnd_xu_return, net: GND, bbox: [199.825, 91.325, 217.175, 108.675], role: xmos-package-return-reservation}

    - {id: n12v_protected_input_cell, net: N12V_PROTECTED, bbox: [25, 85, 70, 110], role: q_in-to-u_buck-input-cell}
    - {id: n5v_buck_source_cell, net: N5V_BUCK, bbox: [25, 85, 70, 110], role: u_buck-output-and-local-output-bank}
    - {id: n5v_buck_hold_entry, net: N5V_BUCK, bbox: [24, 105, 75, 134], role: precharge-and-held-rail-entry}
    - {id: n5v_buck_digital_entry, net: N5V_BUCK, bbox: [145, 85, 185, 134], role: three-downstream-regulator-inputs}

    - {id: n3v3_adc_ldo_adc_cell, net: N3V3_ADC, bbox: [125, 85, 145, 125], role: ldo-output-and-adc-entry}
    - {id: n5v_ldo_hold_bank, net: N5V_LDO_HOLD, bbox: [24, 105, 126, 137], role: held-bank-and-quiet-load-reservation}

    - {id: n0v9_xu_entry, net: N0V9, bbox: [185, 91.325, 201, 108.675], role: digital-power-to-xu-package-handoff}
    - {id: n1v8_xu_entry, net: N1V8, bbox: [185, 91.325, 201, 108.675], role: digital-power-to-xu-package-handoff}
    - {id: n3v3x_xu_entry, net: N3V3X, bbox: [185, 91.325, 201, 108.675], role: digital-power-to-xu-package-handoff}

    - {id: pwr_en_power_source, net: PWR_EN, bbox: [70, 90, 80, 97], role: u_pwr-control-cell}
    - {id: pwr_en_adc_entry, net: PWR_EN, bbox: [95, 103, 101, 107], role: u_adc_pwr_bad-entry-cell}
    - {id: pwr_en_audio_entry, net: PWR_EN, bbox: [20, 108, 24, 112], role: u_audio-entry-cell}
```

The XU handoff deliberately ends at x=201 rather than asserting a route into the package: native XU supply pads span both its west and south/east edges (for example N0V9 pads 5/11/14/18 at x=200.838 and pad 129 is GND). P2 must choose individual pin escapes and local decoupler loops. The three PWR_EN boxes are endpoints only; no intervening corridor is claimed.

The named local anchors that should be encoded with this geometry, for a native remeasurement, are: Q_IN.1/.2/.3 and U_BUCK.2/.3/.4 for N12V_PROTECTED; U_BUCK.7--10/.12--15/.22/.30, C_OUT1.1 and D_HOLD.2 for N5V_BUCK; Q_PRE.3 and C_HOLD1.1 through C_HOLD16.1 for N5V_LDO_HOLD; U_LDO.9/.10 and U_ADC_A.1/.19/U_ADC_B.1/.16/.19 for N3V3_ADC; U_XU's named supply pads for N0V9/N1V8/N3V3X; and U_PWR.6/U_ADC_PWR_BAD.2/U_AUDIO.3 for PWR_EN. The full endpoint denominator remains the modular-plan interface list, not these convenient anchor samples.

## Division of P1 and P2 evidence

P1 needs the source reservation map, exact net and pad identities, no overlap with a subsequently declared source rule area, and a hash-bound native board measurement showing that each listed source cell still exists. For signal allocations, it also needs the already-declared continuous filled GND reference below each signal lane. P1 must retain `p1_accepted: false`.

P2 owns every local copper fact within these boxes: input capacitor-to-U_BUCK VIN/return loop; U_BUCK VOUT/return and switch-current loop; Q_PRE/D_HOLD and the held-bank sharing/return; U_LDO IN/OUT/OUTS/SET/EP/thermal-via topology; the three TPS62822 input, switch, output and quiet-feedback loops; XU package escape/decoupling; ADC/analog local entry; and PWR_EN local return/routing. The eight channel loads on N5V_LDO_HOLD are P2 local distribution, not a P1 scalar corridor. This preserves the existing 89-ref P2 ledger's saved copper obligations.

## Current, thermal, and reference gates

Do not derive a trace width, via count, current-density limit, thermal limit, or acceptance threshold from these bboxes. The power tree supplies only bounded planning inputs: 2.185 A normal upstream delivery with 3.4 A instantaneous fault screen for the input source, N5V_BUCK 1.9 A, N3V3X 1.0 A, N1V8 0.30 A, N0V9 1.2 A, and N3V3_ADC 0.25 A. The held-rail text contains conditional wake/dump screens, not a universal routing-current acceptance; GND and PWR_EN have no scalar rail-current criterion. Those facts must stay attributed to `power_tree.yaml`, rather than becoming new P1 acceptance values.

A future native evidence packet should therefore contain separate, non-promoting gates:

1. Hash-bind floorplan, power-tree, modular plan, board, and a proposed power-window contract; report every window and its exact endpoint pad/net denominator. Reject absent, off-outline, malformed, or source-rule-area overlapping boxes.
2. Measure actual copper geometry separately for each P2-owned path: layer, copper thickness, minimum neck width, pad/land access, via drill/plating and count, path length, and series path resistance. Compare only against an existing applicable contract (the 52-milliohm input copper/vias/joints allocation is specific to the upstream delivery budget); otherwise report the measurement as ungraded.
3. Record the actual GND zone net/layers/fill state, voids, stitching vias and return access for each window. The current P2-derived board must not be credited: it is not a canonical P1 board and no filled-plane continuity claim is made here.
4. Keep thermal evidence separate: component identity, dissipating operating condition, copper area/vias/stackup and measurement or validated model. Existing physical gates remain owed, including Q_IN/F_IN hot behavior, buck/inductor and LDO thermal behavior, held-bank/precharge pulse sharing, and upstream source/cable qualification.

`p1_corridor_capacity.py` is intentionally not the power-window checker. In the `crow-p1` profile it requires the nine power net names exactly once via `power_boundary_nets`, omits `power_boundary_windows` from its lane-allocation set, and unconditionally reports reference-plane/pour continuity as unmeasured. Its scalar `through_lane`, pitch and optimistic slot capacity must not be used to turn a power envelope into a current/thermal result or to obtain PASS by deleting a zone. A dedicated source-window validator and the separate native/P2 evidence above are required.

## Disposition

This proposal makes the previously null source geometry concrete while keeping every power window `INCOMPLETE`. It does not change the canonical source, the PCB, the current or thermal contracts, or the active P1 campaign.

