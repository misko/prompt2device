---
review_stage: pre-route
review_kind: topology
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
subject_raw_sha256: 39f7aa07c34cbe95b93448fa0116a927f48f6a6c70349e5a3caf4b7711319790
subject_semantic_sha256: d6ee9aa05a8cdcfda6e6ad2c421b822d4724cde4316fdc8a7180f8204be3c24d
circuit_json_sha256: f4097cb01771b00dcd459068f3655b7dcac93e42bce8242e4c4a6762a000c231
netlist_sha256: bd06331571ed870fdfbf3043fb1a8c89eaa5d7cff95bfd1a98494f31d01844e5
parts_sha256: e708f4b59642e1df45320def4cecc2990586a0c0f4fd71b46aa94a2ff7004c83
design_rules_sha256: 01cbdb3874b372c114280175932764c6bf8b7a168d69223f5ec90ec612590f4e
evidence: MEASURED mechanical carryover; INHERITED engineering verdict
---

# Independent topology carryover bridge

## Decision

**SOUND** as a mechanical carryover of the prior full topology engineering review, because this audit found no electrical delta from the r2 baseline. This is not a new PVT, source qualification, layout, or firmware analysis. The order state remains **DO-NOT-ORDER**.

## Current and baseline binding

| Item | r2 baseline | Current |
|---|---|---|
| native netlist raw SHA-256 | `a8047cefa0c437294dda86f9569798984a4f5d4821d87027b103d7ec53dffe97` | `2df725538f6b64ccaa1566733be90ccd6030f20d3eb3a13847effd6c772b9b17` |
| normalized helper netlist SHA-256 | `99d3f71062394d97db1e64bfc93ef6958886378d2c5fb4a2148bb318900c6f31` | `bd06331571ed870fdfbf3043fb1a8c89eaa5d7cff95bfd1a98494f31d01844e5` |
| circuit JSON raw SHA-256 | `4bbd4ca2d358814edf6617c2a2781253f2c4af8d63b3e0147081d916da64e138` | `f4097cb01771b00dcd459068f3655b7dcac93e42bce8242e4c4a6762a000c231` |
| design-rules SHA-256 | `e431f396ca42849da4f7a5dffa3b60383093cd3b9faceec885f510c47a14146e` reconstructed | `01cbdb3874b372c114280175932764c6bf8b7a168d69223f5ec90ec612590f4e` |

The baseline rule digest was independently reconstructed with the current rules and route projection, substituting only baseline `power_tree.yaml`. It matches the prior carryover witness. The current and baseline power-tree files differ in one semantic line only: `external_source_fuse.circuit_sha256`, updated from the baseline circuit JSON hash to the current circuit JSON hash. Thus the rules-digest change is fully explained and no other design-rule input changed.

## Exhaustive mechanical comparison

The two native netlists were parsed as KiCad S-expressions and compared after sorting the appropriate unordered collections.

- **Components:** 568/568 references, values, footprints, libsource identifiers, properties, units, and physical pin sets match exactly.
- **Library parts:** 568/568 match, including every libpart pin set.
- **Named nets:** 425/425 match by code, name, class, and every endpoint tuple `(ref, pin, pinfunction, pintype)`; no endpoint was added, removed, or retargeted.
- **Current source data:** all connectivity-bearing source classes match the baseline exactly: 568 `source_component`, 1,782 `source_port` (including all 129 `U_XU` and 16 `U_TDM_XLATE` ports), 282 `source_net`, 1,636 `source_trace`, 7 `source_component_internal_connection`, and 5 `source_group`. The 28 refdes-convention warnings also match.

All raw netlist hash differences are explained by the exporter date and all 568 generated schematic-instance UUIDs, plus the presentation ordering of the 16-pin `U_TDM_XLATE` component record. Its pin set and every net endpoint are unchanged. The current circuit JSON differs in presentation-derived records: one fewer schematic trace/outside-sheet warning, a source-filesystem MD5, and the generated trace-number text in all unnamed-trace warnings. The underlying 1,636 source traces and every connectivity-bearing source record above are identical; no electrical source pin changed.

## Carried engineering limits

The preceding full topology review remains conditional on a qualified isolated external source/cable and first article: the external fuse is an architectural requirement, not proof of sustained fault interruption or pod-surge behavior. Thermal/copper/contact behavior, rail hold-up and hot behavior still need routed-board and physical validation. The shared ADC output remains dependent on firmware scheduling and safe high-impedance `TX_FILL` slots; no firmware was reviewed here. USB/RF integrity, routed DRC, assembly, and first-article checks also remain outside this bridge. These inherited limits are why this SOUND schematic carryover is not permission to order.

