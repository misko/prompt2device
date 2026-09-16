subject: crow-audio-carrier-v1 focused exact-ref priority code review and preferred-offset measurement
date: 2026-09-11
reviewer: Codex independent judgment agent /root/carrier_silk_slot_review
context-given: FRESH; immutable 178-file packet; READ_ONLY source; scratch-only native measurements
source_commit: 5a8b8ca236e0969410da07fd470ecb2892900f77
board_sha256: 0ab5b6dae425074f2515dc3c3d737e56f2292d83140590dca592b7b964e73090
design_rules_sha256: 5891d8028d9864ea0503dc3f63c7520efca45ece640c9db65423680f85b88712
review_kind: noncanonical D-BACK focused shared-code review and native label-slot measurement
code_verdict: SOUND
physical_proposal_verdict: INCOMPLETE-NO-JUSTIFIED-PREFERRED-OFFSETS
engineering_verdict: CURRENT-BOARD-LOCATOR-BLOCKED
order_verdict: DO-NOT-ORDER
baseline_hidden_refs: 25
current_hidden_refs: 27
rejected_candidate_hidden_refs: 28
accepted_hidden_ceiling: 25

# Focused D-BACK judgment

## Shared-code verdict — SOUND

The optional `silk.refdes.priority_refs` implementation is sound for its stated ordering-only scope. It rejects non-lists, non-string or empty members, duplicates, wildcards/unknown refs, and hole refs. Exact entries retain authored list order. Every fallback entry carries the same prefix/TP and lexical keys as the old implementation, so absent or empty `priority_refs` preserves legacy order. The priority path still calls the unchanged four-pose, 84-offset `_place_owned` routine and therefore retains frame, pad/body/silk collision, ownership/degradation, text-size, rotation and stroke behavior; it cannot force placement. The shared template contract describes these limits. The supplied focused native fixture independently demonstrates a non-vacuous winner change, physical-geometry equality, omitted/empty equivalence, blocked-placement refusal, and all nine hostile inputs; GREEN is 3/3 after RED 1/3. Supplied broader evidence is generic 62/62 including 37 known-bad and schema 898/898. I found no concrete correction.

The project candidate is correctly rejected. Prioritizing `C_VDDA2_10N`, `R_FILT1P`, and `R_VMID2_BOT` made those three visible, but changed 14 reference fields and newly hid `R_CFG2`, `R_CFG5`, `R_FILT2P`, and `R_LDO_SET`. Hidden count therefore worsened from 27 to 28, above the unchanged ceiling of 25. No candidate DRC or visual acceptance is warranted.

## Physical proposal — incomplete; do not add preferred offsets

I found no justified per-ref `preferred_offsets` entry under the requested constraints. Against the exact current board, I exhaustively sampled a 0.1 mm grid inside an 11.0 mm radius for all three targets, with 0°/90° and 0.70/0.55 mm poses: 37,980 offsets per pose, 151,920 poses per reference, 455,760 total. The collision model used the production pad, fitted-body, front-silk, frame and centroid-ownership predicates and reserved every one of the 306 currently visible native references. Valid owned, collision-free slots were 0 for each target.

The old accepted positions were `C_VDDA2_10N` (-8.2,0.0) at 0.55 mm/0°, `R_FILT1P` (-6.0,+6.0) at 0.55 mm/0°, and `R_VMID2_BOT` (0.0,+3.6) at 0.55 mm/0°. The rejected priority candidate selected (-5.0,-5.0) at 0.55 mm, (-5.4,0.0) at 0.70 mm, and (0.0,-2.9) at 0.70 mm respectively, but those choices consumed four current-visible slots. The dense central silk seen in the native F.Silk plot is consistent with the zero-slot result. Because the search included arbitrary two-axis grid offsets beyond the ordinary axis/equal-diagonal 84-offset pattern, it directly tested the property ordinary search misses; none satisfies preservation. Inventing a preferred offset would merely hide another label or violate collision/ownership.

## Remaining validation

The locator blocker remains: current hidden 27 versus previous/ceiling 25. No source candidate, board mutation, DRC, parity, routing, fabrication, locator update, or release action was performed. A different repair needs a separately authorized source/layout hypothesis; it must still preserve the 25 ceiling and all visible identities, then receive native geometry/net/zone comparison, DRC/parity, exact omission census and visual acceptance.

## Evidence limits and visual inspection

I visually inspected the native 1800×1200 front-silkscreen plot from a hash-verified scratch copy; it shows the exceptionally dense ADC/filter/reference field where these labels compete. A 3D render attempt was preserved as an original FAIL because 49 of 333 model references were unresolved from the isolated copy (284/333 resolved); no 3D image or acceptance is claimed. The 2D native plot is sufficient only for density/context. Exact feasibility comes from native bounding boxes and the full measured denominator.
