# Crow public-only design admission — 2026-09-23

D11 supersedes the signed-in BOM Tool prerequisite for the engineering workflow. Public records and jlcsearch are the permitted sourcing inputs. No login, account inventory, BOM upload, private records or supplier communication is needed for design continuation.

Adopted independently accepted public-path candidate7cbbf19c as46e72215. Crow's conductor now verifies the exact request against current Circuit JSON and assembly policy, then runs the existing public-catalog pre-layout gate. It has no authenticated response fallback. The shared checker now binds every observed MPN to the actual source and permits the existing Molex catalog spelling only through an exact dossier/code-bound alias. Forged ordinary and aliased MPN tests reject; stale requests/stock, insufficient quantity and code mismatches also reject. Existing suite47/47 passes. D7/D10/D9 remain unchanged.

Root refreshed the request after the assembly policy hash changed, preserving the former blank request/response under ignored historical-pre-d11. Current request covers88 exact JLC codes. Root public prelayout is ACCEPTED4/4, source identity568/568, E-CLOSURE9/9, M-FRESH audit1/1. Native qualification4/4 passes after repairing two repository-isolation defects in a documentation example and a live-project-dependent unit test. Schema-reader audit992/992 has zero orphans; authority, disclosure14/14 and documentation15/15 pass. ERC has zero errors; all4155 retained warnings are converter/library classes (2613endpoint_off_grid,568footprint_link_issues,974lib_symbol_issues), not independently baselined design acceptance.

## Evidence and limits

- Canonical circuit SHA-256: b323ca64ebeec6e7d3660304a03e6bb8c60e041cf1afcf73d436bd9d3b583c64.
- Public stock sidecar: `06_build/sourcing/public-stock.json`, emitted by the actual public checker; 88/88 pass. It explicitly sets predicts_jlc_assembly_allocation=false. It is dated observation, not a reservation.
- Independent policy review: `08_reviews/2026-09-23_public-prelayout_sol_source.md`.
- Schematic checkpoint pins7/7 current circuit/PDF/native/netlist/manifest/provenance/driver files. This preserves review subjects; it does not accept their design.
- PR-REVIEW remains0/2 accepted witnesses. Preliminary independent PDF review finds unreadable text on the XMOS and clock/control pages, with additional small-text pages identified in `08_reviews/2026-09-23_schematic-readability_sol_source.md`. Backtrack authored presentation before placement. Do not manufacture SOUND reviews or resume past this gate.
- A live reviewer-delivery probe produced the required result, but root placed its host-event file inside a protected read-only project snapshot; the runtime correctly closed INCOMPLETE. Preserve that attempt, use an external host-event path on a bounded replacement, and keep formal reviewer availability UNKNOWN until a valid probe closes. This is separate from native-tool qualification.

Public sourcing is sufficient for this design boundary under D11. Actual allocation, supplier assembly losses and final economics remain unmeasured; DO-NOT-ORDER and ASSEMBLY FULFILLMENT: ORDER-TIME CHECK continue to apply to any future release. No purchasing or firmware was performed. No routed PCB or sealed release exists.

Recorded sidecar SHA-256: 5831a934d605ddd2ec52e484d5055ae835a6168335666a263fc15fa546d68982.
Recorded prelayout receipt SHA-256: 5663702c205654a380e7ed33bb798464efc343cdcc68b35d96359568a679a99c.
