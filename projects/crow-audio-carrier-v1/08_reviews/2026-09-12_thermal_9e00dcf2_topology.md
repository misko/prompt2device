subject: crow-audio-carrier-v1 ADR0027 ground-pad-mode floorplan correction schematic delta
source_commit: 9e00dcf23d03b244164476b51fc705ea0728d440
previous_source_commit: 3fc3935a
date: 2026-09-11
reviewer: Codex independent judgment agent /root/carrier_thermal_schematic_delta
context-given: FRESH; immutable complete current/previous packet; prior accepted witnesses supplied only for explicit inheritance
task_id: thermal-schematic-delta
run_id: thermal-schematic-delta
stage_id: KICAD-SCHEMATIC
input_handoff_id: thermal-schematic-delta
commission_sha256: 1144b39162bd17dc0e8f52d80b43d28ac2797afc5ee93a0967706bb0b8140d11
envelope_file_sha256: d86e25f877cd8347b1651c0030760f80a0f492d74c2d055abe581bc6d3a8c35c
subject_raw_sha256: e79444444430ef08c061c7ef605afacb292efdef66d81e20a27ff380ecca0f7a
subject_semantic_sha256: de6f326aefe2a73d52fb92545240a1a10e9052fae59d0377b99eef9915d6416f
circuit_json_sha256: 03e5cdf9450a88c2f99c5d29024821e7c4996870cb19833b7d10e107e9b926e2
native_schematic_sha256: 476127e31b913f56fbffeef305c86672ff4961f09252aac76c65b9a1e2ac3675
netlist_raw_sha256: 861dbec9cbc30fa4219d5cd983d0c81b941469610fb0262d08aaceb4495b0853
schematic_pdf_sha256: 77ffa01b2b5d40ee9e965bd3275818517076da8ef14d98a4117716c79b616832
netlist_sha256: 93c2d97beaeaf816fa2d108771a440e95fa7579e3ea2a7b81f94e72be0b45a92
parts_sha256: bd5dc4f2092cbf0b4a56d07eeff8d7a6ce9d727eaaaef7d40be68318a88bb285
design_rules_sha256: 5891d8028d9864ea0503dc3f63c7520efca45ece640c9db65423680f85b88712
completed_at: 2026-09-12T03:48:27.145437Z
review_stage: pre-route
review_kind: topology
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
inherited_witness_sha256: f1bf59afe6dc980700634ae97ff939ab83a36cc0c781853ba70dd133e8a5491c
inherited_source_witness_sha256: b9edfb74b9d58c813755ea4ae5bbecaa510dd8838698e0e25a1453b0e7f3b673
inherited_scope: prior complete eight-row topology/rating review and its explicit physical qualifications; carried only after fresh proof that current and previous electrical/native projections are identical

# Independent topology delta review

The exact current generated schematic is **SOUND for this pre-route topology delta lens**. This is an electrical-delta continuity judgment, not a fresh full-ratings derivation and not placement, routing, release, or order acceptance.

I independently verified all 637/637 envelope inputs by exact size and SHA-256. Both complete frozen design packets contain 309 files; exactly seven paths differ, matching `changes.json`. The authored change in `floorplan.yaml` moves the existing solid-GND pad-2 selector from logical references `C_ADC_CM3N/P` to `C_ADC_CM2N/P`, following the ADR0027 reference exchange over fixed physical lands. It changes no coordinate, rotation, net, component value, footprint, TSX, channel map, numeric constraint, or electrical rule. The two test changes add the physical-pose preservation regression and update the expected logical references; they do not alter production circuitry.

The channel-map JSON is byte-identical on both sides (SHA-256 `1640e8993f47658a46b2d1c90f9f8082c5a04c5339ca063b6a9efceeb1f41c23`) and still declares `pod_to_adc=[4,3,2,1,5,6,7,8]`. In `circuit.json`, all 10,678 non-warning objects other than one `source_project_metadata.source_filesystem_md5_hash` are byte-for-byte equal. The remaining changes are supplier lookup-warning churn: 1,819 previous versus 1,810 current warning objects, including HTTP-429/result-count variation. Thus no source port, source trace, schematic trace, schematic net label, component, pad, or other electrical object changes.

The native schematics each contain 5,021 UUID occurrences and 4,468 unique UUIDs. Positional structure establishes a conflict-free injective 4,468-entry bijection (digest `b4a1f7570b9ffd1523805d93d50d81532e6843ad417b0d5a9bbf1c453157b1d3`); substituting the bijection makes the complete native texts exactly equal with zero residual lines. Their declared title dates are both `2026-09-11`. This proves complete native geometry and generated U_ADC pin identities unchanged, rather than relying on node counts.

Fresh bounded `kicad-cli` exports from hash-verified scratch copies returned rc 0. Fresh current equals canonical current, fresh previous equals canonical previous, and current equals previous across all 333 component `(reference,value,footprint)` tuples, 220 named net partitions, all 937 `(net,ref,pin,pinfunction,pintype)` nodes, and all 42 explicit NC nodes. Each complete projection has independent SHA-256 `208a011b23f34ee39b6765dccfe702f304548205bb3a37772f13a77d50df4897`. The owning normalized netlist, parts, and design-rules digests are unchanged at the exact values above. The generic KiCad annotation warning occurs in both fresh export logs.

Only after those exhaustive zero-delta proofs did I use the hash-verified prior topology and focused thermal-source witnesses. Their eight obligation rows and limits remain:

1. **Input/spokes:** protected J9 and eight fused branches; 11.4–13.2 V, 1-A trunk/0.10-A branches and conditional 10.896-V header remain bound. Thermal rerating/selectivity remain outstanding.
2. **Buck/held supply:** diode isolation, 3.3-uH selection, precharge and dump polarities remain. Ripple/startup qualification remains outstanding.
3. **LT3041:** A-grade pinout, SET network and separate output capacitors remain. Effective capacitance, ESR/ESL, Kelvin returns and thermal evidence remain outstanding.
4. **Analog:** all sixteen legs, feedback, 30-nF grounded loads and passive bias remain; the 1.2-Vrms differential envelope remains conditional on stability/noise/THD qualification. The overall-shield Cat5e harness still requires gain/noise/crosstalk/phase requalification.
5. **ADC:** supplies, internal LDO, references, polarized filters and five straps retain the secondary 48-kHz/eight-slot mode and ADR0027 channel polarity/association. This floorplan-only correction changes no schematic identity.
6. **MCH:** clock/data direction, Ioff buffers/defaults and presence enable remain; 24.576/12.288-MHz clocks, 48-kHz framing and approximately 0.320-mA sensing remain. Arbitrary hot insertion/brownout is unproven.
7. **Reset/transitions:** supervisor/CLR/timing/NMOS sink remain; 120–350-ms release and nominal 4.732/3.170-V thresholds remain. Pulse minimum, gate drive and assertion timing require measurement.
8. **Allocations:** 12.977-mA injection versus 16.190-mA bleed and 30.742/10.605-us time constants remain conditional. Charge, return error, tracking and derating remain allocations.

## Findings

- **P0/P1: none.** The seven-file delta has zero electrical effect and preserves the previously accepted topology within its stated scope.
- **P2 advisory, retained:** both fresh native exports emit KiCad's generic annotation warning. Complete endpoint/NC equality finds no discrepancy, but annotation/ERC disposition remains owed.
- **P2 physical limitation, open:** `LAYOUT-001` remains open with 3/3 investigation spend exhausted. Simultaneous north-pad clearance, <=1-mm P/N spread, matching, legal vias and filled In1.Cu/In2.Cu reference continuity remain unproven.
- **P2 physical/capture limitation, retained:** connector orientation/mating, installed Cat harness service space, thermal/selectivity, analog performance, serialized 8/8 impulse/USB-slot capture, placement, routing, planes, DRC/parity, assembly and first article remain unqualified. These limits require `DO-NOT-ORDER`.
