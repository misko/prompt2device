---
review_stage: pre-route
review_kind: schematic_render
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
subject_raw_sha256: b7ce794c036aac6c5c6777b4790996f9ed1da71b41f28cd8721c03e454eb3ffb
subject_semantic_sha256: c4835bc93379649200703d9715d0b04e47b21554b3564602eef3ef0076e8ab5b
circuit_json_sha256: cf78dcb8d8c1fc7f696d6f5eaad20a0175c6b27ae0c193d6e1b67bb8937e9193
schematic_pdf_sha256: 7daff0d1e51bb4b9bdae2a0fac763cb9eaa90b8466215c912a14facfcfebff92
netlist_sha256: bd06331571ed870fdfbf3043fb1a8c89eaa5d7cff95bfd1a98494f31d01844e5
parts_sha256: 84a7d8bb46bfa0519f60f1f9cd8277d7b74cb1df2e9e27e979061456e9fb1dd3
design_rules_sha256: 63d84be77073a5434132e99e7d5b3da7f63ff0e16e4db7c7fe26edefa8596fb7
helper_path: skills/kicad-pcb/scripts/pre_route_review_check.py
helper_sha256: b02a6d97feef2436ba71053e676d87e04c726b1ceec92cd92cf8a4b5d25c6b4e
evidence: MEASURED body-carryover; INHERITED visual-readability verdict
---

# Canonical land-repair schematic-render carryover

## Decision

**SOUND**, conditionally, as a mechanical carryover of the accepted visual/readability review. The current PDF is a 92-page, 900 x 607.5 pt PDF 1.7 artifact, SHA-256 `7daff0d1e51bb4b9bdae2a0fac763cb9eaa90b8466215c912a14facfcfebff92`. The accepted baseline is also 92 pages at 900 x 607.5 pt, SHA-256 `5431a70e23f7b0bddbbaf4096b6c93bb3bb7a5a7dee5cb3a5c64a8930c3d7c7d`.

This result inherits the baseline's full 92-page readability finding; it does not represent a second full manual visual review. Procurement remains **DO-NOT-ORDER**, and no P1 approval is granted.

## Body-equality evidence

I extracted text from every page in raw and layout modes. After replacing only the circuit-JSON SHA token in the page header, all 92 page body-token sequences are equal. The ordered aggregate of the 92 masked per-page token hashes is `10980cc7cef63f72393bd800dec9c12bd0108c0048ce563aac8e0992e7bd5e2b` for both PDFs; no page has a token delta.

I rasterized all 92 pages at 72 dpi and compared each current/baseline pair. The only unmasked deltas were in the top source-hash-bearing header line: the current header says abbreviated `cf78dcb8d8c1fc7f…`, while the baseline says `f4097cb01771b00d…`; the changed glyph advances shift only the header suffix on that line. Masking that header suffix (the exact circuit-hash text and its layout-dependent following header text) produced pixel-identical raster bodies for all 92 pages. No schematic-body pixels were masked, and there were no unexpected content deltas.

I inspected representative current pages 1 (power input), 32 (ADC overview), 57 (XMOS overview), 62 (XMOS detail center tile), and 92 (USB frontend), including the changed-hash header context. They agree with the inherited visual classification; page 62's empty center is expected pagination whitespace, not missing content.

## Binding and scope

The current raw circuit JSON SHA-256 is `cf78dcb8d8c1fc7f696d6f5eaad20a0175c6b27ae0c193d6e1b67bb8937e9193`. The current native netlist canonical digest from the actual repository helper `skills/kicad-pcb/scripts/pre_route_review_check.py` (helper SHA-256 `b02a6d97feef2436ba71053e676d87e04c726b1ceec92cd92cf8a4b5d25c6b4e`) is `bd06331571ed870fdfbf3043fb1a8c89eaa5d7cff95bfd1a98494f31d01844e5`. The topology carryover establishes the no-logical-change basis behind the render carryover.

The six repaired native land definitions affect physical footprint geometry/chirality, not this schematic render's circuit content. This review establishes only render-body carryover and inherited readability. It does not cover source qualification, physical connector mating/keying, placement, routing, DRC, manufacturing, thermal behaviour, firmware, or ordering.
