---
review_stage: pre-route
review_kind: schematic_render
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
subject_raw_sha256: 2b9a33b6473029138362253c48a28406138221e2dbf28907fb1a6f5a3dfd5410
subject_semantic_sha256: 98519dc0734619c9d4a7c659ffdeed28eb59fbe8b33f49e6441ca9b1309c955b
circuit_json_sha256: 2b9a33b6473029138362253c48a28406138221e2dbf28907fb1a6f5a3dfd5410
schematic_pdf_sha256: f9bfdffda2b9868414df030f38c9caa79fb9c2accf4db1e32815668e80c3d60d
netlist_sha256: efee66262e060ac952371d67435925a3b3c6786851b2117531ab5f040c1fa830
parts_sha256: 94417f2eb2803309b2a1f7cb9d5135846f8e26090577842e10b814bb27add50d
design_rules_sha256: 2faf5c5a8401ff38720973129bd02e716cb66cedef44e64dc01b2948dbf0e1ad
helper_path: /home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/skills/kicad-pcb/scripts/pre_route_review_check.py
helper_sha256: b02a6d97feef2436ba71053e676d87e04c726b1ceec92cd92cf8a4b5d25c6b4e
---

# Canonical r2 schematic-render review

## Decision: SOUND

I compared all 92 current PDF body rasters with preserved 416d bodies, excluding the hash-bearing header. Pages 1–53 and 55–92 are body-identical; page 54 is the only changed body. I inspected page 54 at readable full-page scale and 180 dpi. The former overlap is corrected: `XU_RESET_N` leaves `U_XU_3V3_OK.RESET_N` with clear separation from `R_3V3X_FB_TOP` (453 kΩ), `N3V3X`, and the feedback divider. The 3V3X regulator, input/output capacitors, divider, supervisor, and labels are legible.

Pages 55 and 56 inherit the prior direct review only because their body rasters are exact matches; their previously crowded but distinguishable feedback/enable text is unchanged. Render soundness does not waive the separate native ERC warning disposition or any source, PCB, physical-USB, thermal, placement/routing, or first-article gate. **DO-NOT-ORDER** remains in force.
