review_stage: pre-route
review_kind: topology
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
subject: crow-usb-carrier-v1, regenerated native schematic after readability presentation change
reviewer: independent topology identity bridge; exhaustive old/new native-netlist comparison
subject_raw_sha256: c8871284836e71fa558fd340c7686ef36c3c10eac07c07e62ea0d544b6066456
subject_semantic_sha256: e6f95058e26686c659cc7744124ac86cd7d042bec8fd811c0cd6581a63f9ff92
schematic_sha256: 8289e9fd1cb9db736cfc41f9c882ed7fa4aad5c8bd039a7f4583a9c21c1ed39b
netlist_sha256: 99d3f71062394d97db1e64bfc93ef6958886378d2c5fb4a2148bb318900c6f31
parts_sha256: e708f4b59642e1df45320def4cecc2990586a0c0f4fd71b46aa94a2ff7004c83
design_rules_sha256: e431f396ca42849da4f7a5dffa3b60383093cd3b9faceec885f510c47a14146e

# Native topology carryover assessment — 2026-09-23

**Decision.** The current native schematic retains the complete component and named-net topology assessed as conditionally **SOUND** by the prior independent witness, `08_reviews/2026-09-23_topology_sol_source.md`. I find no new electrical connection, component identity, value, footprint, or design-policy delta that changes its engineering verdict. This is a **new witness for the current artifact hashes**, based on an exhaustive bridge comparison; the prior full engineering review remains the authority for the pin-level and ratings analysis. This does not promote the board to design-clean, functional, routed, or orderable.

## Bound artifacts and method

| Artifact | Prior | Current |
| --- | --- | --- |
| Circuit JSON raw SHA-256 | `b323ca64ebeec6e7d3660304a03e6bb8c60e041cf1afcf73d436bd9d3b583c64` | `4bbd4ca2d358814edf6617c2a2781253f2c4af8d63b3e0147081d916da64e138` |
| Native schematic raw SHA-256 | `8460145e112b030221391f614975eaf7336706e63e20c0f8c1e68ece1a161f9e` | `8289e9fd1cb9db736cfc41f9c882ed7fa4aad5c8bd039a7f4583a9c21c1ed39b` |
| Shipped native netlist raw SHA-256 | `f0a5f2be4690baac231d0d498e11742e8e9b7d5b022467f97bdf3751023705eb` | `a8047cefa0c437294dda86f9569798984a4f5d4821d87027b103d7ec53dffe97` |
| `pre_route_review_check.netlist_digest` | `3188dfd834775c4d1de4d6b268d9c1c1ca1b4e7ea7c144460974ab957a7298f8` | `99d3f71062394d97db1e64bfc93ef6958886378d2c5fb4a2148bb318900c6f31` |
| Parts digest | `e708f4b59642e1df45320def4cecc2990586a0c0f4fd71b46aa94a2ff7004c83` | same |
| Design-rules digest | `78ba0594488707878b48aae4736158dbdbc45e805c4eb6b4089d0e0e91c8ffc0` | `e431f396ca42849da4f7a5dffa3b60383093cd3b9faceec885f510c47a14146e` |

I parsed the baseline and current KiCad legacy S-expression netlists independently of the review gate. Both contain **568 unique component references, 568 library-part records, 425 unique named nets, and 1,779 net-node occurrences**. All 568 reference sets, values, footprints, other component fields, and 568 library-part records match. The only non-UUID component-record difference is the order of pins `3` and `5` in `U_ADC_CLOCK_OK`'s `units/pins` list; the same physical pin numbers, net nodes, pin functions and pin types remain. Every one of the 425 net names and codes and its complete sorted multiset of `(reference, physical pin, pin function, pin type)` endpoints matches; there are zero added, removed, duplicated, or reassigned endpoint occurrences. Netlist `version`, `groups`, `variants`, `libparts`, `libraries`, source path, tool, and design sheet match exactly. The remaining raw differences are one export date and 568 generated component-instance UUIDs. The gate's byte-order-sensitive normalization retains the changed pin presentation order, explaining why its normalized hash changes despite exact electrical equivalence.

I also parsed the baseline and current Circuit JSON files directly. Canonical sorted-key object multisets match exactly for **568/568 `source_component`, 1,782/1,782 `source_port`, 282/282 `source_net`, 1,636/1,636 `source_trace`, and 7/7 `source_component_internal_connection`** records, with zero objects added or removed in each class. This independently confirms the prior readability-source bridge's electrical-source finding. A new `kicad-cli sch export netlist` from the current native schematic into allocated scratch has the **same current normalized digest** `99d3f710…` as the shipped current netlist. KiCad printed an annotation warning during this scratch export; it did not change the exported topology. The owning schematic/ERC checkpoint must disposition annotation and presentation diagnostics separately.

The only difference between baseline `power_tree.yaml` and current `power_tree.yaml` is `external_source_fuse.circuit_sha256` changing from the prior raw Circuit JSON SHA to the reproduced current raw SHA. Reconstructing the prior rules set by replacing just that file in allocated scratch reproduces the prior digest `78ba0594…`; the current set yields `e431f396…`. The rule's electrical limits, fault envelope, source qualifications, bound references, and test obligations are otherwise byte-identical. The 108 part dossiers are bound by the unchanged gate parts digest; the netlist also independently confirms every populated reference's part value and footprint.

## Scope and retained qualifications

The prior witness's full independent engineering review covered the input fuse/reverse-polarity/TVS chain; all eight eFuse spoke outputs and connector mappings; the main and digital converters and held analog rail; all eight analog input paths and two ADCs; translation, clocks, XMOS, flash boot, and USB. Its manufacturer-record interpretation and conditional **SOUND** verdict carry to the exact current pin/net topology above. This bridge adds exhaustive **old/new identity coverage**, not a second full PVT, analog simulation, or datasheet re-derivation.

The original **DO-NOT-ORDER** qualifications still apply: the actual isolated 11.4–13.2 V source and cable have not been qualified to the one-fault/aggregate-fault waveform limits; the 4 A fuse is not proven to clear every sustained fault; 10.8 V pod floor, surge/pod withstand, protection heating, held-rail capacitance/ESR, hot copper/contact losses, local ambient, and startup/shutdown behavior require routed-board and first-article evidence. The shared ADC SDOUT is safe only with firmware that configures distinct slots and high-impedance TX_FILL before output enable; no working board firmware or measured eight-channel capture is shown. USB enumeration, RF/impedance realization, JLC fabrication/assembly acceptance, routed ERC/DRC, and physical thermal behavior remain outside this pre-route topology bridge. The prior native ERC warning disposition also remains owned by the separate native schematic checkpoint.
