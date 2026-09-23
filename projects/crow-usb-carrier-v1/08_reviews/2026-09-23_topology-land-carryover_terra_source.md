---
review_stage: pre-route
review_kind: topology
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
subject_raw_sha256: b7ce794c036aac6c5c6777b4790996f9ed1da71b41f28cd8721c03e454eb3ffb
subject_semantic_sha256: c4835bc93379649200703d9715d0b04e47b21554b3564602eef3ef0076e8ab5b
circuit_json_sha256: cf78dcb8d8c1fc7f696d6f5eaad20a0175c6b27ae0c193d6e1b67bb8937e9193
netlist_sha256: bd06331571ed870fdfbf3043fb1a8c89eaa5d7cff95bfd1a98494f31d01844e5
parts_sha256: 84a7d8bb46bfa0519f60f1f9cd8277d7b74cb1df2e9e27e979061456e9fb1dd3
design_rules_sha256: 63d84be77073a5434132e99e7d5b3da7f63ff0e16e4db7c7fe26edefa8596fb7
helper_path: skills/kicad-pcb/scripts/pre_route_review_check.py
helper_sha256: b02a6d97feef2436ba71053e676d87e04c726b1ceec92cd92cf8a4b5d25c6b4e
evidence: MEASURED mechanical carryover; INHERITED engineering verdict
---

# Canonical land-repair topology carryover

## Decision

**SOUND**, conditionally, as a mechanical carryover from the accepted r2 topology review. The land repair did not change a component, physical pin set, net, or net endpoint. This is not a fresh engineering sign-off for source qualification, placement, routing, fabrication, thermal/contact behaviour, first article, or firmware. Procurement remains **DO-NOT-ORDER** and this review grants no P1 approval.

## Current identity and helper binding

The current raw circuit JSON is `cf78dcb8d8c1fc7f696d6f5eaad20a0175c6b27ae0c193d6e1b67bb8937e9193`; the accepted pre-land baseline JSON is `f4097cb01771b00dcd459068f3655b7dcac93e42bce8242e4c4a6762a000c231`. The current and baseline raw native-netlist byte hashes are respectively `795de956403e127cdec781eb0f313a8128b127a1d2eee28a8ff7738774c457cb` and `2df725538f6b64ccaa1566733be90ccd6030f20d3eb3a13847effd6c772b9b17`.

I used the actual repository helper `skills/kicad-pcb/scripts/pre_route_review_check.py` at SHA-256 `b02a6d97feef2436ba71053e676d87e04c726b1ceec92cd92cf8a4b5d25c6b4e`. Its `netlist_digest()` returns the identical current-helper canonical digest `bd06331571ed870fdfbf3043fb1a8c89eaa5d7cff95bfd1a98494f31d01844e5` for both native netlists. This normalization is limited to KiCad export date, instance UUID, source path, generated sheet properties, and project netclass presentation metadata as defined by that helper; it does not exclude components, pins, nets, endpoints, or no-connect data.

The current helper-derived part and rules bindings are, respectively, `84a7d8bb46bfa0519f60f1f9cd8277d7b74cb1df2e9e27e979061456e9fb1dd3` and `63d84be77073a5434132e99e7d5b3da7f63ff0e16e4db7c7fe26edefa8596fb7`.

## Exhaustive carryover comparison

The legacy KiCad S-expression documents each contain 568 component records, 568 libpart records, and 425 named-net records. The equal canonical whole-netlist digest above therefore binds all component identities, values, footprints, non-generated properties, library pins, net definitions, physical pins, nodes/endpoints, and explicit no-connect records after only the helper's declared KiCad-export normalization.

I also independently partitioned and sorted complete circuit-JSON records. The connectivity-bearing electrical partition (`source_component`, `source_component_internal_connection`, `source_group`, `source_net`, `source_port`, and `source_trace`) is 4,280 records in each artifact and has equal SHA-256 `8b5bb11475c29a56b720a57c171033df1e4c76381470104e304f4c0fd0a8d0ac`. The schematic partition (`schematic_component`, `schematic_element_outside_sheet_warning`, `schematic_group`, `schematic_net_label`, `schematic_port`, `schematic_sheet`, `schematic_text`, and `schematic_trace`) is 4,572 records in each and has equal SHA-256 `d5afd41155c97aa245cac6bc60b1111d7246f1fe742a295cfe5c5d44e93b8ec0`.

`U_XU` remains complete: 129 source ports, 129 distinct pin numbers, covering 1 through 129. The only raw-CJ record-class deltas are one `source_project_metadata` record and the 1,636 generated `source_unnamed_trace_warning` records. They are presentation/provenance diagnostics and are outside the electrical partition; no connectivity-bearing source record changed.

## Why the observed changes are not a logical change

The raw-CJ identity changed because the repaired source emits changed physical-land/provenance data and associated generated warning text. The electrical and schematic partitions above prove that it did not alter the logical circuit or the schematic model.

The associated repair is limited to physical land geometry/chirality: the FTSH, DCK, DCT, DMQ, DCU, and dormant digital DSE native footprint definitions and their TSX land definitions. It corrects copper geometry and signed-coordinate pin-1 chirality; it does not remove, retarget, or electrically alter FTSH pin 7 or any other endpoint. The active digital DSE count remains zero, so its corrected native footprint is latent in this schematic. These are physical corrections only and still require regenerated-board placement/DRC and the separate FTSH keying/mating review.

## Carried conditions

The inherited design verdict remains conditional on a qualified isolated external source/cable and first article. The external fuse is architectural intent, not proof of sustained fault interruption or pod-surge behaviour. Routed-board thermal, copper, contact, hold-up, and hot-operation validation remains open. Shared ADC output behaviour remains dependent on firmware scheduling and safe high-impedance `TX_FILL` windows; firmware was not reviewed. USB/RF integrity, assembly, routed DRC, physical connector mating, and first article remain outside this carryover. These limits preserve **DO-NOT-ORDER**.
