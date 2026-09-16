subject: crow-audio-carrier-v1 Cat5e pod-harness schematic delta
source_commit: 7baeac34c94fb0ce94e64e634344902464877069
previous_source_commit: f7fd347e
date: 2026-09-12
reviewer: Codex independent judgment agent /root/carrier_cat_schematic_delta
context-given: FRESH; immutable complete current/previous packet; prior accepted witnesses supplied only for explicit inheritance
commission_sha256: 6fa59a6dd48e9eb555ae4dd4b04e0b38818f48eb451f2082d460fcdc18f49ee1
envelope_sha256: 768b225c68aa6e17196f1c2cd1ecc3a577a4bf435f295762cf65205aaa60e17c
envelope_file_sha256: 21357bc54a9e927cd4e08a5b3d9449a911a26c3eb8dbf056afb251daed177c48
subject_raw_sha256: c82c561f2ca22515d329c22c4c29d2cafaf6a0361c8a6c3dcc023735a21e9796
subject_semantic_sha256: 2423802a6050d62c4e4dc0763c168a0b479f1822caa0d1ce86108ed44abb119b
circuit_json_sha256: 818e9c68b3744b197a3dcc6e9bbdec2290f469e736b2aa3ba98d09e97e106524
native_schematic_sha256: 749d276e842440a6a2fab9eef06070d3f5710cb0c823dd37758805eea95658f0
netlist_raw_sha256: cab99e8401ae124a65d1e1fb8b21aea2e3d3bfbf34122a404f1f0fb7388b6683
schematic_pdf_sha256: c7f100ffc25e33030e98c3be048412d76b51770803b643518f5b5749185a0943
netlist_sha256: 2d798eb77bb10353db70c66048a0e13f34cb0b29f3cbae292a0ae1c3c9fd9efa
parts_sha256: e2f7a9284d65bc07a61f336c1d3eb7e0eb381b9efaca2e90e52ca91e6c1c7eb0
design_rules_sha256: 0637fdb2d3f5ab247c301147ad6ed875343674c225e5036a2bb1935bd025cec3
completed_at: 2026-09-12T00:51:51Z
review_stage: pre-route
review_kind: topology
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
inherited_witness_sha256: 87466124e7d39caf24c0f337b051df095b762e4ef599edea69bb531390330328
inherited_scope: prior complete eight-row topology/rating review and its explicitly unresolved physical qualifications; used only after independent current electrical equivalence proof

# Independent topology delta review

I find the exact current schematic **SOUND for this pre-route topology delta lens**. This is a continuity judgment over the Cat5e pod-harness source change, not a fresh full-ratings derivation. I independently verified all 624/624 envelope inputs by exact size and SHA-256. The complete packet contains 295 previous and 303 current files: 286 are byte-identical, eight are added, nine are modified, and none are removed. The resulting 17-row inventory exactly matches `changes.json`.

The eight new files are the WAGO 221-415 record and part declaration, Belden 7939A/8503 records, part declarations and PDFs. `02_parts/README.md` documents their off-board status and retained physical holds. The shared `spoke_interface.yaml` keeps the four-position Micro-Fit PCB map exactly: cavity 1 +12V_POD, 2 GND, 3 AUDIO+, 4 AUDIO-. It replaces 6541PA with Belden 7939A: blue is the audio pair; orange, green and brown each provide one supply/return conductor; separate WAGO 221-415 joins feed one 22-AWG 8503 pigtail per power contact. At 15 m, the declared screen remains 0.938 ohm cable loop, 1.4725 ohm with hot multiplier and non-cable allocation, 0.14725 V drop at 100 mA, and 10.65275 V from the 10.8 V carrier minimum. This is a design screen, not measured harness qualification.

The other authored changes update the checker-pinned shared-contract hash, register the new cable/join/pigtail evidence sources, change the cable evidence grade to `unknown`, and add the installed-cable-route deferral. `model_registration.yaml`, all 3D models, TSX source, schematic presentation source, route geometry, electrical-invariant/net/power rules, part values, and PCB footprints are byte-identical. Manufacturer/model-source acceptance is therefore not treated as human orientation, placement, service-space, or mating approval. The supplied repaired Cat source review and source receipts were used only to classify this source delta: carrier and pod SOURCE gates pass, while carrier FULL remains INCOMPLETE with 21 source-admitted physical unknowns and the pod FULL gate remains INCOMPLETE with its installed cable-route unknown.

The regenerated circuit JSON changes only three element types: one `source_project_metadata` filesystem hash and supplier diagnostics (`source_part_not_found_warning` 48 to 83; `supplier_footprint_mismatch_warning` 153 to 130). Every other 32 element types, including all 333 source/schematic/PCB/CAD components, 937 source/schematic/PCB ports, 178 source nets, 697 schematic traces, 454 labels, and 19 sheets, are exactly equal in original list order. Diagnostic churn is not electrical acceptance.

The native files contain 5,021/5,021 UUID occurrences and 4,468/4,468 unique UUIDs. An independently checked 4,468-entry bijection is consistent across every occurrence, injective in both directions, and has digest `086cc4a89ba29ff944a69e7e4a8b417a2457c6f9a61795e6615de50224af2c70`. Substituting the mapping makes the complete previous native schematic exactly equal to current: zero residual lines. Each contains exactly one declared title date, `2026-09-11`.

Fresh bounded `kicad-cli` exports returned rc 0. Fresh current, fresh previous, canonical current, and canonical previous each contain 333 components, 220 named net partitions, 937 complete node tuples `(net, ref, pin, pinfunction, pintype)`, and 42 explicit no-connect tuples. All six pairwise comparisons agree on every component reference/value/footprint, net name, node tuple, and NC tuple. All four normalize under the copied owning gate to `2d798e...`. This establishes electrical equivalence with nonzero full-membership denominators rather than counts alone.

Only after that proof did I reopen and hash-verify the prior accepted topology witness. Its eight obligations and limits remain:

1. **Input/spokes:** protected J9/eight fused branches; 11.4-13.2 V, 1-A trunk/0.10-A branches and conditional 10.896-V header remain bound; thermal rerating/selectivity remain outstanding.
2. **Buck/held supply:** diode isolation, 3.3-uH selection, precharge and dump polarities remain; ripple/startup qualification remains outstanding.
3. **LT3041:** A-grade pinout, SET network and separate output capacitors remain; effective capacitance, ESR/ESL, Kelvin returns and thermal evidence remain outstanding.
4. **Analog:** all sixteen legs, feedback, 30-nF grounded loads and passive bias remain; the 1.2-Vrms differential envelope remains conditional on stability/noise/THD qualification. The new overall-shield Cat5e harness additionally requires gain/noise/crosstalk/phase requalification.
5. **ADC:** supplies, internal LDO, references, polarized filters and five straps retain the secondary 48-kHz/eight-slot mode and channel polarity.
6. **MCH:** clock/data direction, Ioff buffers/defaults and presence enable remain; 24.576/12.288-MHz clocks, 48-kHz framing and approximately 0.320-mA sensing remain; arbitrary hot insertion/brownout is unproven.
7. **Reset/transitions:** supervisor/CLR/timing/NMOS sink remain; 120-350-ms release and nominal 4.732/3.170-V thresholds remain; pulse minimum, gate drive and assertion timing require measurement.
8. **Allocations:** 12.977-mA injection versus 16.190-mA bleed and 30.742/10.605-us time constants remain conditional; charge, return error, tracking and derating remain allocations.

## Findings

- **P0/P1: none.** No electrical topology defect or incompleteness was introduced by the classified 17-file delta.
- **P2 advisory, retained:** both fresh native exports emit KiCad's generic annotation warning. Each still yields 333 unique components and exact 937 endpoint/42 NC continuity; resolve or disposition it at the annotation/ERC boundary.
- **P2 physical limitation, current:** the Cat source contract is coherent after repair and SOURCE passes, but installed cable route/service space, glands, joins, crimps, shield treatment, complete hot-loop resistance, analog performance, fault/thermal behavior, all-eight serviceability and first article remain unqualified. FULL is INCOMPLETE.
- **P2 limitations, retained:** prior thermal/selectivity, analog, power-transition, sourcing, connector orientation/mating, placement, routing, assembly and first-article obligations remain and keep `DO-NOT-ORDER`.
