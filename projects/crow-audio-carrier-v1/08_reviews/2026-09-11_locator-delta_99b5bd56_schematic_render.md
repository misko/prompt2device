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
netlist_sha256: 2d798eb77bb10353db70c66048a0e13f34cb0b29f3cbae292a0ae1c3c9fd9efa
parts_sha256: bafd73441627216789c6f1f43b20552e9bf572d4a350103d34d4d9593de90768
design_rules_sha256: 908162895dad6767f920ff33718c0dc814e447d8bdf07c56c9be8e5a9d1db37a
completed_at: 2026-09-11T23:47:15Z
review_stage: pre-route
schematic_pdf_sha256: 040a5c254c55bab339a65a7bd655649bb5224ea68f6d823c95b8e8707133f07d
review_kind: schematic_render
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
inherited_witness_sha256: 7715ba4ffcac4d54673da17b0586258bfe547dbc20b14756be35591c477954e4
inherited_scope: prior fresh inspection of all 19 PDF pages and all 19 native regions, plus its readability findings and limitations; used only after independent exact current PDF and native-geometry continuity proofs

# Independent schematic-render delta review

I find the exact current 19-page PDF **SOUND for this pre-route schematic-render delta lens**. I independently rebound the exact current and previous PDF bytes with bounded 120-dpi `pdftoppm` runs. Each run returned rc 0 and produced 19 pages. Pages 4 and 15 are 1013x1500 pixels; the other 17 are 1500x1013 pixels.

I compared every pixel on every page. All 19 pages differ only in the page-header circuit database caption. The union changed box is x=299..687 and y=83..97 (half-open raster box `[299,83,688,98]`); individual changed-pixel counts are 2,805–2,971. Every pixel from y=98 through each page bottom is identical on all 19 pages. Therefore all circuit-area symbols, references, values, labels, wires, junctions, power/ground markers and functional layout remain exact.

I visually inspected the changed caption strip on every current page in a 19-page contact sheet at the actual rendered scale and inspected complete current pages 1, 4, 6, 14 and 18 at their full raster dimensions. Those pages cover both landscape and portrait formats, input protection, supervision, a representative analog channel, ADC configuration and TDM return. The new caption visibly carries the current circuit JSON hash prefix `e6eebba269f45fb4...`; headings and reviewed circuit content remain readable.

I did not freshly view all 19 native regions. The independent native proof supplies that continuity: 5,021 UUID occurrences form a conflict-free 4,468-entry bijection, and substituting the mapping leaves zero residual native schematic lines, including all visible geometry. That exact proof permits the hash-verified prior 19-region inspection to carry forward within its original scope. It is not a restamp, a fresh full-region claim, or an assertion that locator/model-source evidence accepts orientation or placement.

The ten changed project files were inspected in this lens. Seven PCB silkscreen caption moves, signed-side registration metadata, a 25-reference assembly locator, its conditional waiver, contracts and source tests do not feed schematic drawing geometry. The generated circuit JSON hash changes the page caption, while the native schematic and electrical graph remain equivalent under the complete proofs recorded above. Locator visual usability is a separate owning review and does not become schematic readability acceptance here.

## Findings

- **P0/P1: none.** No blocking or major readability defect appears in the exact current schematic delta.
- **P2 advisory, retained:** the generic annotation warning appears in both fresh export logs; complete endpoint/NC equality finds no connectivity discrepancy, but the warning remains owed at the annotation/ERC boundary.
- **P2 observation, retained:** folded buck/analog/clock/reset wiring and generic native passive rectangles can require deliberate tracing. All independently viewed complete pages remain readable; exact circuit-area pixel continuity preserves the earlier inspection for the other pages.
- **P2 limitations, retained:** locator usability and exact-artifact acceptance, connector orientation/placement, routing, fabrication, assembly, fit, cable service, sourcing allocation and first article remain outside this lens and require `DO-NOT-ORDER`.
