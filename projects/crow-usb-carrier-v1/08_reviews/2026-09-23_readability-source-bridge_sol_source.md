# Crow schematic readability candidate: electrical identity bridge

Date: 2026-09-23 UTC. Read-only independent comparison. Original: `/tmp/crow-topology-review-20260923/projects/crow-usb-carrier-v1/03_tscircuit/build/circuit.json`, SHA-256 `b323ca64ebeec6e7d3660304a03e6bb8c60e041cf1afcf73d436bd9d3b583c64`. Candidate: `/tmp/crow-schematic-readability-20260923/projects/crow-usb-carrier-v1/03_tscircuit/build/circuit.json`, SHA-256 `4bbd4ca2d358814edf6617c2a2781253f2c4af8d63b3e0147081d916da64e138`.

**Finding: electrical source identity is exact.** Parsing every JSON object and comparing canonical sorted-key object multisets by record type gives byte-for-byte equality of all 568 `source_component`, 1,782 `source_port`, 282 `source_net`, 1,636 `source_trace`, and 7 `source_component_internal_connection` records. The 5 `source_group` and 28 `source_refdes_convention_warning` records are also identical. Consequently all 568 source refdes, encoded values, exact manufacturer part numbers, pin numbers/names, port connectivity-map keys, net names, trace terminal IDs, and declared internal connections are unchanged. This is an exact whole-population comparison, not a spot sample. `U_XU` retains its exact XU316-1024-TQ128-C24 source component and all 129/129 numbered source ports (no missing/duplicate pin), with identical per-pin names and connectivity keys; their canonical tuple SHA-256 is `46b320e38757300f1c7261df9f2ccfdf94bf697398efa8a27d7e26741919ea74` for both files.

Record types that changed, expressed as old→new count and exact-object multiset removed/added, are:

| Type | Count | Removed/added | Disposition |
|---|---:|---:|---|
| `schematic_component` | 568→568 | 36/36 | Symbol dimensions, pin presentation and position. |
| `schematic_port` | 1776→1776 | 252/252 | Presentation pin locations. |
| `schematic_net_label` | 1064→1068 | 225/229 | Drawn labels/anchors, not `source_net` membership. |
| `schematic_trace` | 764→766 | 129/131 | Drawn wire geometry, not `source_trace` terminal identities. |
| `schematic_text` | 198→198 | 22/22 | Presentation text placement. |
| `schematic_sheet` | 39→39 | 4/4 | Sheet layout bounds/centers. |
| `schematic_element_outside_sheet_warning` | 158→154 | 112/108 | Geometry diagnostics. |
| `source_unnamed_trace_warning` | 1636→1636 | 1636/1636 | Message-only TSX trace-render ordinal churn (`<trace#11811...>` etc); all actual `source_trace` objects are exact. |
| `source_project_metadata` | 1→1 | 1/1 | Filesystem MD5 changes with source styling. |

Every other present type (`schematic_group` and the source types above) compares exactly. The complete file has 10,517→10,519 objects; the net +2 comes from two extra drawn `schematic_trace` records, not electrical traces.

The candidate working tree at `15e8f46e348d0cbcc294c17f047af427ee8ff93d` changes only `z_schematic_presentation.tsx` for the TSX source: compact control-sheet poses, wider XU symbol, longer horizontal pin margins and a buffer pin arrangement. The other authored edits add renderer text-scale/detail-tile options and pass those options in `rebuild_all.sh`. The diff from `34ea0019` does not modify the circuit hardware modules, part dossiers, footprints, net rules or other TSX source. The checked-in native KiCad schematic in both isolated trees still has the same raw SHA-256 `8460145e112b030221391f614975eaf7336706e63e20c0f8c1e68ece1a161f9e`; it has **not** been regenerated from the candidate, so this comparison does not claim a new native netlist or footprint parity pass. Circuit JSON has no `pcb_component`/footprint records: footprint identity is supported by unchanged hardware source and the unchanged existing native schematic, and must be rechecked on generated KiCad/PCB outputs.

**E-FAULT disposition.** Advancing the raw `external_source_fuse.circuit_sha256` pin from `b323…` to `4bbd…` is safe as a *source identity update* if and only if the authoritative producer reproduces the exact `4bbd4ca2…` Circuit JSON bytes and the same five electrical source-record classes above remain exact against `b323…`. The raw pin currently rejects the candidate solely because presentation changes alter the full-file hash; the electrical projection has no delta. Update the pin only for the final reproduced candidate and rerun E-FAULT/early-design checks and the full conductor before accepting any schematic checkpoint. Updating `power_tree.yaml` also changes the design-rules digest and makes the existing topology review hash stale, even though its pin-net engineering conclusion carries over mechanically; the review/identity gate must be renewed against the final generated netlist and rules. This bridge is not a substitute for that conductor, native regeneration, ERC, schematic readability witness, or post-change review.
