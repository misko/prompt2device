subject: crow-audio-carrier-v1 passive/footprint schematic delta
source_commit: 39d54efbe16a56f776969c4de8a60e49ac095750
previous_source_commit: 654faac4ddcd4addc9950d5d9a8cb508d71d580f
date: 2026-09-11
reviewer: Codex independent judgment agent /root/carrier_passive_schematic_delta
context-given: FRESH; immutable complete current/previous packet; prior accepted witnesses supplied only for explicit inheritance
commission_sha256: ae0c2b064d2f560c4b9c830e2ed99fc5cf717b4d889438585abb3e6f4bab4e5e
envelope_sha256: dddedb43ec6d60532033619692bc44368fda0886c8c5668250c78d3e9d079f4b
subject_raw_sha256: 5bead0fac60fa521be452627c088d6a9d64f59609bb1ecda473b996e6f1020b0
subject_semantic_sha256: 2d9918425e27d2bc6978a2357cfdb581b9ae17a58ad4cafb5225fb548d383346
circuit_json_sha256: 13017d6d3277667d67839899ca2089618cf08a9a1ae94559e44c96a86193708e
native_schematic_sha256: b8dcfae8e60edd89b78ff8c168c775b859d40fb89a47f87eea2c7025f0707260
netlist_raw_sha256: 7d6c13021cf441e22129cadd204724b25cfae6e85ce5a0696b224ab03d9fa77e
netlist_sha256: 2d798eb77bb10353db70c66048a0e13f34cb0b29f3cbae292a0ae1c3c9fd9efa
parts_sha256: bafd73441627216789c6f1f43b20552e9bf572d4a350103d34d4d9593de90768
design_rules_sha256: 072e13c96a25657108d8e7df0df4dd646433dfbbde696fbc8ae41513aae01b30
completed_at: 2026-09-11T21:10:18Z
review_stage: pre-route
review_kind: topology
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
inherited_witness_sha256: 35a6c717a98aa2aeda2abc6c545b323da2974a5c1f496c28a8e18a7d887db53e
inherited_scope: prior complete eight-row topology/rating review and its explicitly unresolved physical qualifications; used only after independent current electrical equivalence proof

# Independent topology delta review

I find the exact current schematic **SOUND for this pre-route topology delta lens**. This is a continuity judgment over all changed inputs, not a fresh full-ratings derivation. I independently verified 601/601 packet inputs by exact size and SHA-256. The computed complete inventory is 282 previous and 293 current files: 262 common files are byte-identical, 20 are modified, 11 are added, and none are removed. This exactly matches `changes.json`; every row and its classification is retained in `evidence.json`.

The four changed part dossiers retain their MPNs, values, pin maps and electrical limits. They change footprint/source/escape/gotcha/layout metadata for the Littelfuse fuse, 2N7002K, AO3401A package evidence and R_PWR_TOP. The TSX changes only add/select exact footprint geometry for F1-F8, Q_PRE_EN, Q_RST1 and R_PWR_TOP; their authored connection expressions are unchanged. Floorplan changes move the eight fuses and project manual-population exclusions. Assembly/model-registration/adjudication rules, footprints, a resistor STEP model, provenance, contracts and test-helper migration affect physical/model policy or its verification. They explain the changed parts/rules digests but do not assert human orientation, placement, mating or assembly acceptance.

The native files have 5,021/5,021 UUID occurrences and 4,468/4,468 unique UUIDs. An independently checked 4,468-entry bijection (mapping digest `47f45fed9e66bab1f90b935cee2a86f4de53e4a86bc63edef603b00263870b0a`) is consistent across every repeated occurrence; the UUID sets themselves are disjoint. After applying that bijection, the complete 101-line unified residual contains exactly eleven changed hidden `Footprint` property values: F1-F8, Q_PRE_EN, Q_RST1 and R_PWR_TOP. The declared title date is 2026-09-11 in both files. Every symbol/value/MPN field, pin UUID attachment, coordinate and native geometry byte outside those footprint values is equal.

Fresh bounded `kicad-cli` exports returned rc 0 and exactly reproduce their corresponding canonical membership. Current and previous each contain 333/333 components, 220/220 named partitions, 937/937 component-pin memberships and 42/42 explicit NC memberships. All 937 net tuples and all 42 NC tuples match across versions. Component values match; only the same eleven footprint strings differ. The owning netlist digest changed from `4aa555c194aac4e97f340c357d14123a31f5750204df00af79e9b83131cc4f9b` to `2d798eb77bb10353db70c66048a0e13f34cb0b29f3cbae292a0ae1c3c9fd9efa` because that digest intentionally binds footprint properties, so graph equivalence was established from full parsed membership rather than digest equality.

The prior topology witness was reopened and hash-verified only after this proof. Its eight obligations remain:

1. **Input/spokes:** protected J9/eight fused branches; 11.4-13.2 V, 1-A trunk/0.10-A branches and conditional 10.896-V header remain bound; thermal rerating/selectivity remain outstanding.
2. **Buck/held supply:** diode isolation, 3.3-uH selection, precharge and dump polarities remain; ripple/startup qualification remains outstanding.
3. **LT3041:** A-grade pinout, SET network and separate output capacitors remain; effective capacitance, ESR/ESL, Kelvin returns and thermal evidence remain outstanding.
4. **Analog:** all sixteen legs, feedback, 30-nF grounded loads and passive bias remain; the 1.2-Vrms differential envelope remains conditional on stability/noise/THD qualification.
5. **ADC:** supplies, internal LDO, references, polarized filters and five straps retain the secondary 48-kHz/eight-slot mode and channel polarity.
6. **MCH:** clock/data direction, Ioff buffers/defaults and presence enable remain; 24.576/12.288-MHz clocks, 48-kHz framing and approximately 0.320-mA sensing remain; arbitrary hot insertion/brownout is unproven.
7. **Reset/transitions:** supervisor/CLR/timing/NMOS sink remain; 120-350-ms release and nominal 4.732/3.170-V thresholds remain; pulse minimum, gate drive and assertion timing require measurement.
8. **Allocations:** 12.977-mA injection versus 16.190-mA bleed and 30.742/10.605-us time constants remain conditional; charge, return error, tracking and derating remain allocations.

## Findings

- **P0/P1: none.** No electrical topology defect or incompleteness was introduced by the classified delta.
- **P2 advisory, retained:** both native exports emit the generic annotation warning. The export still yields 333 unique components and exact 937 endpoint/42 NC continuity; no causal diagnosis is claimed. Resolve or disposition it at the annotation/ERC boundary.
- **P2 limitations, retained:** thermal/selectivity, analog performance, power transitions, sourcing allocation, connector orientation/mating, placement, routing, assembly and first article remain unqualified and keep the order verdict `DO-NOT-ORDER`.
