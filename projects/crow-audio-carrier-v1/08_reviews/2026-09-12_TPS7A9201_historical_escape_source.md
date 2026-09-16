# Crow audio carrier v1 — historical TPS7A9201 escape-tier dossier correction

subject: crow-audio-carrier-v1 historical TPS7A9201DSKR escape-tier dossier correction
date: 2026-09-12
reviewer: Codex independent judgment agent /root/carrier_escape_dossier_review
context-given: FRESH; immutable 130-input source/dossier packet; supplied original placement-preflight logs; proposed-part.yaml; READ_ONLY source
source_commit: d70fbd108ad1fbfe9aef82a7752c7c31b10ed85c
review_stage: D-BACK source correction
review_kind: source-dossier
review_scope: noncanonical historical dossier/model-consistency judgment; not a canonical pin, layout, render, routing, fabrication, or release review
board_sha256: ef72e6d2f5400b481f397532a58784644b82bc88d5fa527f4c46b7a3356c822b
parts_sha256: bd5dc4f2092cbf0b4a56d07eeff8d7a6ce9d727eaaaef7d40be68318a88bb285
proposed_parts_sha256: b7840639dac129aff1dbbea0a6a92124a00c1d124459334375d252e799675a2b
partial_packet_rules_sha256: 3780a832b741cc80b6eb068681244a04bbc2230cd231427493d2ec6ebae457fa
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
completed_at: 2026-09-12T06:55:32Z
task_identity: task_id=escape-dossier-review; run_id=escape-dossier-review; input_handoff_id=escape-dossier-review; stage_id=KICAD-PLACEMENT
envelope_sha256: 269343255dfcb2379b4be70e7b698c5d4c45718fe4897c0db5cee3b17a14b62b
envelope_file_sha256: 157444b076b4fb40b7ac635633f229b6fe903d18ad28f3fbccf079919856a37f
reviewer_id: /root/carrier_escape_dossier_review
reviewer_provenance: independent judgment; FRESH context; no child agents; read-only exact-packet source/model review
raw_subject_sha256: 2db1d0ebafb4d9bb8ffe9ce4855a88b89d1c1d01cf131e22698dbe4ed0ff74bb
semantic_subject_sha256: d8a1c7f1b0d114cf389cfaa0ead9f4f4ee4e66853adb9bf5a73dde7fae99784b
input_coverage: 130/130 packet inputs verified by declared size and SHA-256 before judgment
part_declaration_coverage: 87/87
original_escape_outcome: FAIL; 87/87 graded; 1 problem
proposed_escape_outcome: PASS; 87/87 graded; 0 problems
correction_field_count: 1
correction_field: escape.tier_required
correction_old_value: jlc_4layer_standard
correction_new_value: jlc_4layer_advanced
current_board_fab_tier: jlc_4layer_advanced
current_native_tps7a92_occurrences: 0 across exact PCB and schematic text
current_native_lt3041_occurrences: 12 across exact PCB and schematic text
blocking_finding_ids: []

## Engineering verdict

The proposed correction is **SOUND**. Replace exactly the historical `TPS7A9201DSKR` dossier field `escape.tier_required: jlc_4layer_standard` with `escape.tier_required: jlc_4layer_advanced`. The proposal changes one semantic leaf and no other dossier field. Its manufacturer identity, superseded status, package, footprint, pin map, limits, gotchas, original source attribution, layout notes, locators, and all statements of work still owed remain unchanged.

The owning escape model evaluates a `dfn` at `0.5 mm` pitch as infeasible at `jlc_2layer_default`, infeasible at `jlc_4layer_standard`, feasible at `jlc_4layer_advanced`, infeasible at `jlc_6layer_standard`, and feasible at `jlc_6layer_smallvia`. Its lowest-rank answer is therefore `jlc_4layer_advanced`. The supplied original preflight graded all 87 declarations and reported this dossier as its sole P-ESC problem. My independent bounded rerun reproduces that exact 87/87 FAIL with one problem. Substituting only `proposed-part.yaml` produces 87/87 PASS with zero problems; the isolated original/proposed package runs likewise change from one failure to PASS.

The primary TI PDF is byte-bound by SHA-256 `e0c0a695e933d9656a7c6fefad654c5129d76a22ac8398d26eacfb844dd4532e`. I freshly inspected rendered PDF pages 30–33. They identify DSK0010A as a 2.5 × 2.5 mm WSON, show ten perimeter lands on two rows at 0.5 mm pitch, and show exposed thermal pad 11. This verifies the `dfn`/`0.5` inputs to the owning model. It does not establish that the package is physically impossible on every cheaper process or placement. The verdict is that the dossier must agree with this repository's declared escape model.

## Current design and historical scope

The dossier itself says `status: superseded`. ADR0025 selects LT3041 as the current regulator. Independent text census of the exact packet finds no TPS7A92 occurrence in either the PCB or schematic and finds LT3041 in both. The live design already declares `fab_tier: jlc_4layer_advanced`, and the active LT3041 dossier already requires that same advanced tier. The correction therefore changes neither the installed part nor current board tier, geometry, pin binding, or route source. It does not claim that any historical TPS7A9201 placement, route, fabrication, assembly, or order was accepted.

This frozen packet omits some contributors used by the complete owning `design_rules_digest(project)` projection, including route/floorplan context. The computed `partial_packet_rules_sha256` is recorded only as the semantic digest of the packet's available rule inputs; it is not the canonical current-project `design_rules_sha256` and must not be used to restamp any canonical review. This noncanonical report intentionally omits the canonical field rather than substituting a partial value or borrowing an out-of-packet value.

## Required downstream renewal

The correction changes the owning all-part digest from `bd5dc4f2092cbf0b4a56d07eeff8d7a6ce9d727eaaaef7d40be68318a88bb285` to `b7840639dac129aff1dbbea0a6a92124a00c1d124459334375d252e799675a2b`. Consequently, every current review or checkpoint that binds the all-part digest becomes stale even though the installed part and board bytes do not change. At minimum, the owning pre-route topology and schematic-render reviews bind `parts_sha256`, as does the pre-route physical-pin review. The authored checkpoint and any broader source census may also invalidate schematic or physical bindings and must be re-evaluated by their owners.

No review should be restamped in place. Root must apply the single source edit, rerun the owning checks and preflight, renew each invalidated canonical review/checkpoint with its complete required metadata, and retain all route, DRC/parity, return, thermal, sourcing, assembly, release, and first-article obligations. This source judgment grants no waiver and does not retire any guard.

## Delivery verdict

**COMPLETE for the allocated independent source/dossier judgment; DO-NOT-ORDER for the product.** Evidence includes every bounded argv/cwd/runtime receipt, the complete original and proposed 87-part checker logs, isolated package/model logs, exact semantic diff, full 130-input verification, primary-PDF extraction and four inspected page renders. The initial inventory helper failure and failed optional montage launch are retained in full; both are tooling/packaging events and do not affect the engineering result. The inventory helper was corrected and passed in the same live attempt, and the four source page images were inspected directly.

This report does not replace the canonical pin, layout, render, topology, schematic-render, routing, fabrication, assembly, or release reviews. Those lenses retain their separate authority and renewal requirements.
