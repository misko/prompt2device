subject: crow-audio-carrier-v1 locator/source-policy schematic delta
source_commit: 99b5bd5689c761a05392cb46213ddc04d6588e33
previous_source_commit: 7bfb3a9e
date: 2026-09-11
reviewer: Codex independent judgment agent /root/carrier_locator_schematic_delta
context-given: FRESH; immutable complete current/previous packet; prior accepted witnesses supplied only for explicit inheritance
commission_sha256: 4f700aaaf52b1cb69318d80bae86e7116b6f3821d214081849562a7f90af27a2
envelope_sha256: 62f3ad57b54b20f051e3e811bfdb777dcbc2af5ce1921c46f0c7b7b5d4861f06
subject_raw_sha256: 03bf594b644aa395131deb214a81ce4f694dda96a05335ccdc78a57eb9475bed
subject_semantic_sha256: 41749ed3a2faef855f11c973f87a0a936748180029baa6cc1f6075b2cf1a1edc
circuit_json_sha256: e6eebba269f45fb48074715fd00ca936410bd3cae734babf5d6720d0fd12a234
native_schematic_sha256: 93eaa7f3a54d2d1c095bea3d8198b48e3c0539c01cc347d6a80081c9c0e284b5
netlist_raw_sha256: df60866e6963e5cb7f9e3d89e3a35a0348b30e68b8ca4d953c8b17fe109f485c
schematic_pdf_sha256: 040a5c254c55bab339a65a7bd655649bb5224ea68f6d823c95b8e8707133f07d
netlist_sha256: 2d798eb77bb10353db70c66048a0e13f34cb0b29f3cbae292a0ae1c3c9fd9efa
parts_sha256: bafd73441627216789c6f1f43b20552e9bf572d4a350103d34d4d9593de90768
design_rules_sha256: 908162895dad6767f920ff33718c0dc814e447d8bdf07c56c9be8e5a9d1db37a
completed_at: 2026-09-11T23:47:15Z
review_stage: pre-route
review_kind: topology
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
inherited_witness_sha256: 29b714bd14ee42c9c422613f51dfe5273362f97f4cf6ac6c3fe8b5742d6c1d72
inherited_scope: prior complete eight-row topology/rating review and its explicitly unresolved physical qualifications; used only after independent current electrical equivalence proof

# Independent topology delta review

I find the exact current schematic **SOUND for this pre-route topology delta lens**. This is a continuity judgment over the locator/source-policy change, not a fresh full-ratings derivation. I independently verified 608/608 envelope inputs by exact size and SHA-256. The complete supplied project inventory contains 293 previous and 295 current files: 285 are byte-identical, eight are modified, two are added, and none are removed. The resulting ten-row inventory exactly matches `changes.json`.

The source/rule changes are physical and policy changes. Seven channel captions move in `floorplan.yaml`; the Samtec registration group gains `mount_side: front`; `assembly_locator.yaml` adds 25 exact top-side reference identities with position, rotation and pad/net tuples; and `policy_waivers.yaml` conditionally names the same 25-reference `P-SILK-REF` exception set. The waiver is explicitly dependent on current checked locator artifacts and independent render acceptance and grants no routing or order authority. Contracts document that ownership, and two source tests grade all eight channel captions plus a seven-caption hostile control. These changes do not alter authored electrical connections, values, footprints, part dossiers or net rules. Model-source acceptance is not treated as human orientation, placement or mating approval.

The four generated artifacts change in raw bytes: circuit JSON, PDF, native schematic and canonical netlist. The circuit JSON change includes regenerated supplier-warning identities/order; it changes the PDF header's circuit-hash caption. That diagnostic churn is not electrical evidence. I therefore established topology from the native source and complete parsed net membership.

The native files contain 5,021/5,021 UUID occurrences and 4,468/4,468 unique UUIDs. An independently checked 4,468-entry bijection is consistent across every occurrence, injective in both directions and has digest `ccf818f877efbec33280da9b7938029c88961eb5b34c280ccc60da045548932f`. After applying it, the complete previous native schematic equals the current native schematic byte for byte: zero residual lines. This covers every symbol/value/property, pin attachment, wire, label, coordinate, visible geometry and the unchanged declared title date `2026-09-11`.

Fresh bounded `kicad-cli` exports returned rc 0. Current and previous exports and their canonical counterparts each contain 333/333 components, 220/220 named partitions, 937/937 component-pin memberships and 42/42 explicit no-connect memberships. Current export equals current canonical for all component refs, values, footprints, 937 net tuples and 42 NC tuples. Previous export likewise equals previous canonical. Current and previous exports also match each other on every one of those fields. The nonzero full-membership denominators establish source-graph equivalence rather than a count-only claim.

Only after that proof did I reopen and hash-verify the prior accepted topology witness. Its eight obligations and physical limits remain:

1. **Input/spokes:** protected J9/eight fused branches; 11.4–13.2 V, 1-A trunk/0.10-A branches and conditional 10.896-V header remain bound; thermal rerating/selectivity remain outstanding.
2. **Buck/held supply:** diode isolation, 3.3-uH selection, precharge and dump polarities remain; ripple/startup qualification remains outstanding.
3. **LT3041:** A-grade pinout, SET network and separate output capacitors remain; effective capacitance, ESR/ESL, Kelvin returns and thermal evidence remain outstanding.
4. **Analog:** all sixteen legs, feedback, 30-nF grounded loads and passive bias remain; the 1.2-Vrms differential envelope remains conditional on stability/noise/THD qualification.
5. **ADC:** supplies, internal LDO, references, polarized filters and five straps retain the secondary 48-kHz/eight-slot mode and channel polarity.
6. **MCH:** clock/data direction, Ioff buffers/defaults and presence enable remain; 24.576/12.288-MHz clocks, 48-kHz framing and approximately 0.320-mA sensing remain; arbitrary hot insertion/brownout is unproven.
7. **Reset/transitions:** supervisor/CLR/timing/NMOS sink remain; 120–350-ms release and nominal 4.732/3.170-V thresholds remain; pulse minimum, gate drive and assertion timing require measurement.
8. **Allocations:** 12.977-mA injection versus 16.190-mA bleed and 30.742/10.605-us time constants remain conditional; charge, return error, tracking and derating remain allocations.

## Findings

- **P0/P1: none.** No electrical topology defect or incompleteness was introduced by the classified ten-file delta.
- **P2 advisory, retained:** both fresh native exports emit the generic annotation warning. Each still yields 333 unique components and exact 937 endpoint/42 NC continuity; resolve or disposition it at the annotation/ERC boundary.
- **P2 limitations, retained:** thermal/selectivity, analog performance, power transitions, sourcing allocation, locator usability/hash acceptance, connector orientation/mating, placement, routing, assembly and first article remain unqualified and keep `DO-NOT-ORDER`.
