subject: crow-audio-carrier-v1 north ADC channel-map generated schematic delta
source_commit: 131e0ddaf61efd14aa447ef37b24b370fd8b53a4
previous_source_commit: f2675b431c4372a1a81d0fdfa0ca81f0a27ecd68
date: 2026-09-12
reviewer: Codex independent judgment agent /root/carrier_channel_schematic_delta
context-given: FRESH; immutable complete current/previous packet; prior accepted witnesses supplied only for explicit inheritance
task_id: channel-schematic-delta
run_id: channel-schematic-delta
stage_id: KICAD-SCHEMATIC
input_handoff_id: channel-schematic-delta
commission_sha256: 1bd5d3900496aa303b1a3af7728f707bb99c4cb8f387d4b400be7bd8a151b814
envelope_file_sha256: eb68b5cf3ed2c692a5417afb377b6f1be255444ea26a629fca90970d27c9f017
subject_raw_sha256: a2dc7a70dac26451770d037caf8d37c80f0f609ecb6141524f1888e48c268c05
subject_semantic_sha256: 7e538070d89a01027f21c0709d4daf2acf9546670543a8c9a9d2287b073c76ce
circuit_json_sha256: a4f853e36ea7570fbf09a52a81a9e10b8b6882698f763e59af08c7699d2c4499
native_schematic_sha256: 7239f984b576897ad6e8ee720c5724ee5f488aff1c8df0cdfaca2de78d9c83e4
netlist_raw_sha256: 73ab326395fde1488fb9369ac0c794257d45455e982b7d36a5439cab84534172
schematic_pdf_sha256: 280cf241707058fe2274e03647232c6cd054f995f1d8e13e887cccf92dd4a56e
netlist_sha256: 93c2d97beaeaf816fa2d108771a440e95fa7579e3ea2a7b81f94e72be0b45a92
parts_sha256: bd5dc4f2092cbf0b4a56d07eeff8d7a6ce9d727eaaaef7d40be68318a88bb285
design_rules_sha256: 5891d8028d9864ea0503dc3f63c7520efca45ece640c9db65423680f85b88712
completed_at: 2026-09-12T03:08:50.591543Z
review_stage: pre-route
review_kind: topology
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
inherited_witness_sha256: 6a43038cab9545b2d92775c6f8cf1f6bdaf131d5a181974c673b9641857ea166
inherited_source_witness_sha256: 6b273adc623ea2bc9ac3b1e2c8253eff621eaed725521e2412c291a57e32fec3
inherited_scope: prior complete eight-row topology/rating review and its explicit physical qualifications; carried only for unchanged domains after exhaustive current residual classification

# Independent topology delta review

The exact current generated schematic is **SOUND for this pre-route topology delta lens**. This is an electrical-delta continuity judgment, not a fresh full-ratings derivation and not placement, routing, release, or order acceptance.

I verified all 644/644 envelope files before and after work by exact declared size and SHA-256. The complete frozen packet has 309 current files and 306 previous files; exactly 19 items differ, and their paths and hashes agree with `changes.json`. The authored delta adds ADR0027, the typed channel map and its hostile/positive test, then binds the same map through architecture, brief, first-article contract, ADC dossier, analog checker, floorplan, route seed declarations, net rules, fanout test and TSX producer. Generated circuit JSON, PDF, native schematic and canonical netlist are the four remaining changed items. The ADC dossier and geometry/rule edits exchange logical capacitor references and net names across the same eight north physical locations; values, footprints, physical pose multiset, P/N, reference domain, track width, layer and segment points remain unchanged. The documentation and test changes state the prospective capture identity and keep physical capture `OWED`; they do not themselves prove a recording, orientation, placement, route, plane, or first article.

The channel map is exactly `pod_to_adc=[4,3,2,1,5,6,7,8]`, so fixed hardware slots 0..7 identify pods `[4,3,2,1,5,6,7,8]`. The generated circuit JSON changes the expected eight `source_port`, eight `source_trace`, and eight `schematic_net_label` objects, plus filesystem metadata and supplier/source diagnostic churn. Each electrical trace change is confined to U_ADC pins 39,40,41,42,45,46,47,48. No connector, AFE, ISO, south ADC input, supply, reference, clock, reset, component value, footprint, or no-connect membership changes.

The native files each contain 5,021 UUID occurrences and 4,468 unique UUIDs. A positional structural comparison produced a conflict-free, injective 4,468-entry bijection (digest `4d25f080c476b38d14ebdc01da5c8779eed3eca27f5530bcfefae571de985537`). After substitution, the complete 1.15-MB schematic has only eight residual global-label text changes at the fixed U_ADC terminals; the unified residual is 26 lines. Both declared title dates are exactly `2026-09-11`. This classifies every native residual rather than claiming equivalence.

Fresh bounded `kicad-cli` exports of scratch copies returned rc 0. Fresh current equals canonical current, and fresh previous equals canonical previous, across every component reference/value/footprint, named net, complete node tuple `(net,ref,pin,pinfunction,pintype)`, and explicit NC tuple. Each side has 333 components, 220 nonempty named net partitions, 937 nodes and 42 NC nodes. The current-versus-previous delta is exactly eight removed and eight added node tuples, all at U_ADC:

| Logical pod net | Previous physical ADC pins P/N | Current physical ADC pins P/N | Fixed slot |
|---|---:|---:|---:|
| ADC1P/N | 40/39 | 48/47 (IN4) | 3 |
| ADC2P/N | 42/41 | 46/45 (IN3) | 2 |
| ADC3P/N | 46/45 | 42/41 (IN2) | 1 |
| ADC4P/N | 48/47 | 40/39 (IN1) | 0 |
| ADC5P/N | 14/13 | unchanged | 4 |
| ADC6P/N | 16/15 | unchanged | 5 |
| ADC7P/N | 20/19 | unchanged | 6 |
| ADC8P/N | 22/21 | unchanged | 7 |

The exact owning netlist digests are current `93c2d97b...` and previous `2d798eb7...`; the changed digest is explained completely by those eight P/N-preserving memberships. This supports the source intent and removes the former north ordering reversal. It does not prove the simultaneous legal corridor, matching, filled-plane continuity, or physical USB-slot identity.

Only after the exhaustive residual proof did I use the hash-verified prior accepted topology witness and corrected-source witness. The eight inherited obligation rows and their limits remain:

1. **Input/spokes:** protected J9 and eight fused branches; 11.4–13.2 V, 1-A trunk/0.10-A branches and conditional 10.896-V header remain bound. Thermal rerating/selectivity remain outstanding.
2. **Buck/held supply:** diode isolation, 3.3-uH selection, precharge and dump polarities remain. Ripple/startup qualification remains outstanding.
3. **LT3041:** A-grade pinout, SET network and separate output capacitors remain. Effective capacitance, ESR/ESL, Kelvin returns and thermal evidence remain outstanding.
4. **Analog:** all sixteen legs, feedback, 30-nF grounded loads and passive bias remain; the 1.2-Vrms differential envelope remains conditional on stability/noise/THD qualification. The overall-shield Cat5e harness still requires gain/noise/crosstalk/phase requalification.
5. **ADC:** supplies, internal LDO, references, polarized filters and five straps retain the secondary 48-kHz/eight-slot mode and channel polarity. ADR0027 changes only the north logical-to-physical association enumerated above.
6. **MCH:** clock/data direction, Ioff buffers/defaults and presence enable remain; 24.576/12.288-MHz clocks, 48-kHz framing and approximately 0.320-mA sensing remain. Arbitrary hot insertion/brownout is unproven.
7. **Reset/transitions:** supervisor/CLR/timing/NMOS sink remain; 120–350-ms release and nominal 4.732/3.170-V thresholds remain. Pulse minimum, gate drive and assertion timing require measurement.
8. **Allocations:** 12.977-mA injection versus 16.190-mA bleed and 30.742/10.605-us time constants remain conditional. Charge, return error, tracking and derating remain allocations.

## Findings

- **P0/P1: none.** The exact 19-file delta implements the intended fixed association without an additional topology defect.
- **P2 advisory, retained:** both fresh native exports emit KiCad's generic annotation warning. The complete 333-component/937-node/42-NC comparisons find no identity or connectivity discrepancy, but annotation/ERC disposition remains owed.
- **P2 physical limitation, open:** `LAYOUT-001` remains open with 3/3 investigation spend. The source association removes ordering reversal but does not prove simultaneous clearance for all 32 north pads/24 paths, <=1-mm P/N spread, matching, legal vias, or filled In1.Cu/In2.Cu reference continuity.
- **P2 physical/capture limitation, retained:** installed Cat harness route/service space, connector orientation/mating, thermal/selectivity, analog performance, serialized 8/8 impulse/USB-slot capture, placement, routing, planes, DRC/parity, assembly and first article remain unqualified. These limits require `DO-NOT-ORDER`.
