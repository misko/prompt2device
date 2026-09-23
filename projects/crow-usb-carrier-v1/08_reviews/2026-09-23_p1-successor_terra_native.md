---
review_kind: p1-successor-native-candidate
design_verdict: DEFECTIVE
order_verdict: DO-NOT-ORDER
board_sha256: b2f59a1b2a8ef91dd1160d6b0074f6a045c4fa0e8d58611bdba98f076acd6fa5
source_electrical_semantic_sha256: 98519dc0734619c9d4a7c659ffdeed28eb59fbe8b33f49e6441ca9b1309c955b
---

# P1 successor native candidate review

## Decision: DEFECTIVE — DO-NOT-ORDER

I inspected the archived candidate reports and top render. The candidate is a useful placement starting point: 568 footprints / 1,870 pads, all 27 declared anchors, all 16 hold capacitors inside their banks, no reported support or ADC courtyard intrusions, and 568/568 resolved models with no missing courtyards. The `model_registration` CLI exit of 0 is only N-A because no registration contract exists; it is not a registration acceptance.

The actual DRC classification ran and failed: 41/41 violations are classified, comprising 40 `silk_over_copper` and one `silk_edge_clearance` at USB, with 499 unrouted connections. Eight schematic-parity findings remain: every `U_SPOKE1`–`U_SPOKE8` has a PCB Description field while the schematic field is blank. The duplicate `drc_classification SKIPPED` row is shell bookkeeping and does not supersede the preceding real FAIL. The top render is consistent with an unrouted, densely placed candidate and cannot establish manufacturable copper clearance or assembly readability.

**P1 source/model findings:** the candidate’s board semantic fingerprint is expressly a source-electrical projection inherited from 2b9a; it is not proof of native-board equivalence. The `U_DUMP` / `C_DUMP_LOGIC` adjacency appears in DRC item references, but the governing adjacency rule is ungraded, so source-side constraint coverage is incomplete. That rule needs an explicit, graded source constraint before it can be used as an acceptance argument.

**P2 local-adjacency/implementation findings:** the 41 silkscreen violations, USB edge clearance, all 499 unrouted connections, and the eight footprint/schematic Description mismatches are board-local defects requiring native cleanup and recheck. They are not waived by the anchor, hold-bank, 3D-model, or source-projection counts. Physical routing, copper/current/thermal behavior, USB integrity, DRC clearance, and first-article evidence remain open.
