# Readability R2 source-identity bridge audit

Read-only audit. The initially supplied candidate `build/circuit.json` path was stale and remained `4bbd…`; the corrected producer artifact below is `dist/src/crow_carrier/circuit.json`.

## Artifact identity

| Artifact | SHA-256 observed now |
|---|---|
| Root CJ | `4bbd4ca2d358814edf6617c2a2781253f2c4af8d63b3e0147081d916da64e138` |
| Producer dist CJ | `f4097cb01771b00dcd459068f3655b7dcac93e42bce8242e4c4a6762a000c231` |

The specified producer `dist` artifact has the requested `f409…` hash. The earlier `build/circuit.json` lookup was stale and observed `4bbd…`; it is retained here as pathfinding evidence only and is not the compared candidate.

## Source-record comparison

Canonical JSON-key-sorted record multisets match exactly between root `4bbd…` and producer-dist `f409…`:

| Record type | Old | Candidate | Old-only | Candidate-only |
|---|---:|---:|---:|---:|
| `source_component` | 568 | 568 | 0 | 0 |
| `source_port` | 1,782 | 1,782 | 0 | 0 |
| `source_net` | 282 | 282 | 0 | 0 |
| `source_trace` | 1,636 | 1,636 | 0 | 0 |
| `source_component_internal_connection` | 7 | 7 | 0 | 0 |
| `source_group` | 5 | 5 | 0 | 0 |

No specified source-record type changed. Full source-component records match, which includes component identity, values, manufacturer/supplier part numbers, and any footprint/source attributes carried by those records. The XMOS component remains a 129-port, four-side perimeter arrangement with identical pin labels and pin sequences. The 16 source ports of `U_TDM_XLATE` are unchanged.

Across the complete JSON record set, changed record types are `schematic_component`, `schematic_element_outside_sheet_warning`, `schematic_net_label`, `schematic_port`, `schematic_sheet`, `schematic_text`, `schematic_trace`, `source_project_metadata`, and `source_unnamed_trace_warning`. The specified engineering-source record types above are unchanged. Against `1ffff78b`, the candidate worktree shows the two presentation TSX files and `03_src/rebuild_all.sh` as authored changes, plus generated `build/circuit.json` and `build/schematic.pdf` artifacts. This audit makes no native KiCad/netlist/parity claim.

## E-FAULT disposition

The raw source-identity condition for an E-FAULT pin advance from `4bbd…` to `f409…` is satisfied. Any advance remains conditional on full root producer reproduction of the stated `f409…` bytes and all normal required gates. This audit does not make a native KiCad/netlist/parity claim.
