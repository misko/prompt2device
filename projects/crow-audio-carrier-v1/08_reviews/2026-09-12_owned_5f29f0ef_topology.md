subject: crow-audio-carrier-v1 owned label/source/locator canonical schematic delta
source_commit: 5f29f0ef835add806f128d758ab5aa215f9a9d35
previous_source_commit: 9e00dcf23d03b244164476b51fc705ea0728d440
date: 2026-09-11
reviewer: Codex independent judgment agent /root/carrier_owned_schematic_delta
context-given: FRESH; immutable complete current/previous packet; prior accepted witnesses supplied only to identify inherited scope and limitations
task_id: owned-schematic-delta
run_id: owned-schematic-delta
stage_id: KICAD-SCHEMATIC
input_handoff_id: owned-schematic-delta
commission_sha256: 8c175d2a8e833bc1d04617828a093f8de744de0c2a7e8c241bf1070512e217b9
envelope_file_sha256: 52caf29b149d951b1e4773674a229052fa630acfc8be788b6b5c6ce7ab939240
subject_raw_sha256: 663238a310ca60206afb41d8e1b9cf99eaa57f7a8ea47f8cceaf704ccd9ca9d8
subject_semantic_sha256: 9dd28e58d13e37f84b7b4e7884277aa6f3f20cf26b327a7e3185124617434aca
circuit_json_sha256: aa7d4772dd9ab207d22cfb015fd1bc144f444087a39c81b76bfe69c19992f51d
native_schematic_sha256: d96f19ff7dd926ee6b8286cf11ca35bb6cb990d077a6bf12c623e78a363747e5
netlist_raw_sha256: e55b1c3f9c1e382522354d2fb5f481471b6c4c2b49d071cdf45e60e02b5b914a
netlist_sha256: 93c2d97beaeaf816fa2d108771a440e95fa7579e3ea2a7b81f94e72be0b45a92
parts_sha256: bd5dc4f2092cbf0b4a56d07eeff8d7a6ce9d727eaaaef7d40be68318a88bb285
design_rules_sha256: 9f0466101074f850a63fee128ddee9d527bdad64d6f305d83a5e0267425e6851
completed_at: 2026-09-12T05:37:40.587345Z
review_stage: pre-route
review_kind: topology
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
inherited_witness_sha256: b6dca233781d145f96210e65340ee0affaabdf17f857e97952b2029ec2887d45
inherited_source_witness_sha256: fac026b33e509fc8368bdbc731fbabdffaca821250ad7ce9629c0d5d1c8dadcc
inherited_scope: prior complete eight-row topology/rating review and its explicit physical qualifications; carried only after fresh complete native and component/pin/net/NC equivalence proof

# Independent topology delta review

The exact current generated schematic is **SOUND for this pre-route topology delta lens**. This is an electrical-delta continuity judgment, not a fresh full-ratings derivation and not placement, routing, release, or order acceptance.

I independently verified all 637/637 envelope inputs by exact size and SHA-256. Both complete frozen design packets contain 309 files and exactly the seven declared paths differ. The electrical source, TSX, component/part definitions, constraints other than assembly-locator membership, and `03_src/adc_channel_map.json` are byte-identical. The channel map retains SHA-256 `1640e8993f47658a46b2d1c90f9f8082c5a04c5339ca063b6a9efceeb1f41c23` and `pod_to_adc=[4,3,2,1,5,6,7,8]`, so the previously accepted ADR0027 north-ADC mapping is unchanged.

The changed authored files are non-electrical for this lens. `contracts.md` documents generic priority/preferred-offset behavior. `floorplan.yaml` adds only preferred silkscreen offsets `R_DUMP_TIME1=[[1.1,-1.6]]` and `R_VMID2_TOP=[[1.5,4.1]]`. `assembly_locator.yaml` keeps 25 exceptions, removes `R_DUMP_TIME1`, `R_FILT2P`, and `R_VMID2_TOP`, and adds `C_VDDA2_10N`, `R_FILT1P`, and `R_VMID2_BOT`; this changes the owning rules digest from `5891d8028d9864ea0503dc3f63c7520efca45ece640c9db65423680f85b88712` to `9f0466101074f850a63fee128ddee9d527bdad64d6f305d83a5e0267425e6851` because locator configuration is included, without changing a circuit endpoint. The focused source witness is used only for those two label choices and the 25-entry locator candidate; model-source acceptance does not establish schematic or physical orientation approval.

In `circuit.json`, the complete 10,679-object non-warning sequence is identical after removing the sole `source_project_metadata.source_filesystem_md5_hash`. Warning objects changed from 1,810 to 1,841 because supplier lookup results/HTTP-429 messages churned. No source component, source port, source trace, source net, schematic component, schematic port, schematic trace, schematic net label, pad, or other electrical object changed.

The native schematics each contain 5,021 UUID occurrences and 4,468 unique UUIDs. Occurrence-aligned substitution establishes a conflict-free bijection of all 4,468 unique UUIDs (mapping digest `3d7d9849fee964897e45c103dbe735326ef3c36c2882a87bf8908f0046913cbf`); complete substituted native text equals the previous text with zero residual lines. Their title dates are unchanged. This proves every generated native ADC pin identity and every geometry/text record are unchanged rather than relying on counts.

Fresh bounded `kicad-cli` exports from hash-verified scratch copies returned rc 0. Fresh current equals canonical current, fresh previous equals canonical previous, and current equals previous across all 333 `(reference,value,footprint)` components, 220 complete named-net partitions, 937 `(net,ref,pin,pinfunction,pintype)` nodes, and 42 `+no_connect` nodes. The complete projection digest is `6549fb3266d04511c01cae80a883c0497fa2a0c994822f0fd3e716e143da1d9d`. The owning normalized netlist and parts digests remain unchanged; only the locator-owned rules digest changes as classified above.

Only after those complete zero-electrical-delta proofs did I carry forward the hash-verified prior topology witness. I did not freshly rederive the ratings. Its eight obligation rows and limits remain:

1. **Input/spokes:** protected J9 and eight fused branches; 11.4–13.2 V, 1-A trunk/0.10-A branches and conditional 10.896-V header remain bound. Thermal rerating/selectivity remain outstanding.
2. **Buck/held supply:** diode isolation, 3.3-uH selection, precharge and dump polarities remain. Ripple/startup qualification remains outstanding.
3. **LT3041:** A-grade pinout, SET network and separate output capacitors remain. Effective capacitance, ESR/ESL, Kelvin returns and thermal evidence remain outstanding.
4. **Analog:** all sixteen legs, feedback, 30-nF grounded loads and passive bias remain; the 1.2-Vrms differential envelope remains conditional on stability/noise/THD qualification. The overall-shield Cat5e harness still requires gain/noise/crosstalk/phase requalification.
5. **ADC:** supplies, internal LDO, references, polarized filters and five straps retain the secondary 48-kHz/eight-slot mode and ADR0027 channel polarity/association. The label/locator source delta changes no schematic identity.
6. **MCH:** clock/data direction, Ioff buffers/defaults and presence enable remain; 24.576/12.288-MHz clocks, 48-kHz framing and approximately 0.320-mA sensing remain. Arbitrary hot insertion/brownout is unproven.
7. **Reset/transitions:** supervisor/CLR/timing/NMOS sink remain; 120–350-ms release and nominal 4.732/3.170-V thresholds remain. Pulse minimum, gate drive and assertion timing require measurement.
8. **Allocations:** 12.977-mA injection versus 16.190-mA bleed and 30.742/10.605-us time constants remain conditional. Charge, return error, tracking and derating remain allocations.

## Findings

- **P0/P1: none.** The seven-file delta has zero electrical effect and preserves the accepted topology/rating review within its stated inherited scope.
- **P2 advisory, retained:** both fresh exports emit KiCad's generic annotation warning. Complete endpoint/NC equality finds no discrepancy, but annotation/ERC disposition remains owed.
- **P2 physical limitation, open:** `LAYOUT-001` remains open with 3/3 investigation spend exhausted. Simultaneous north-pad clearance, <=1-mm P/N spread, matching, legal vias and filled In1.Cu/In2.Cu reference continuity remain unproven.
- **P2 physical/capture limitation, retained:** connector orientation/mating, installed Cat harness service space, thermal/selectivity, analog performance, serialized 8/8 impulse/USB-slot capture, placement, routing, planes, DRC/parity, assembly and first article remain unqualified. These limits require `DO-NOT-ORDER`.
