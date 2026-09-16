subject: crow-audio-carrier-v1 policy-waiver source consistency review
date: 2026-09-11
reviewer: Codex independent judgment agent /root/carrier_waiver_sync_review
context-given: FRESH; immutable 21-input packet; READ_ONLY source; scratch-only native inspection and packaging
source_commit: 57df15a2
review_stage: pre-route
review_kind: source-consistency
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
board_sha256: ef72e6d2f5400b481f397532a58784644b82bc88d5fa527f4c46b7a3356c822b
design_rules_sha256: 9f0466101074f850a63fee128ddee9d527bdad64d6f305d83a5e0267425e6851
task_identity: task_id=waiver-sync-review; run_id=waiver-sync-review; input_handoff_id=waiver-sync-review; stage_id=KICAD-PLACEMENT
envelope_sha256: 5bfae463df850cb8e5b8e235516147f7f082b1e2cae33078debbfd5f032cf16f
reviewer_id: /root/carrier_waiver_sync_review
reviewer_provenance: independent
context_mode: FRESH
raw_subject_sha256: 6db7845a58321cfe34570a3179f70f2f37ceca92cd57e404b28243e4ab9ac7e8
semantic_subject_sha256: 94a87982c956c03609edd51f57a9a46001f280f619e038a6184d8eadf36bfaee
completed_at_utc: 2026-09-12T05:50:53.128235Z
original_policy_waivers_sha256: 35afe158425d63cf3b3cb834d6deb7492cf71a8a46b5e89323a7fae419e261d2
proposed_policy_waivers_sha256: 28d4bf36efee10b32a13ab79e87316984318994c2569397098108145b9421ecc
waiver_id: P-SILK-REF
waiver_ceiling: 25
waiver_ref_count: 25
blocking_finding_ids: []
layout_finding: LAYOUT-001
layout_finding_state: OPEN
layout_attempts_spent: 3/3
locator_prerequisite: fresh exact A-LOCATOR/current-render acceptance REQUIRED

# Independent source-consistency judgment

The proposed one-file source change is SOUND for this bounded source-consistency lens. It changes only the 25 `P-SILK-REF` identities: removes `R_DUMP_TIME1`, `R_FILT2P`, and `R_VMID2_TOP`; adds `C_VDDA2_10N`, `R_FILT1P`, and `R_VMID2_BOT`. The ceiling remains 25, and the complete `why`, `evidence`, and every other policy field are byte-semantically unchanged.

## Independent evidence

All 21 frozen inputs passed exact size and SHA-256 verification before packaging. I copied the exact board to allocated scratch, verified the copy retained SHA-256 `ef72e6d2f5400b481f397532a58784644b82bc88d5fa527f4c46b7a3356c822b`, and inspected it with pcbnew under bounded `pipeline_runtime.run_stage`. It contains 340 footprints and 1002 pads. Its complete 25-reference hidden set equals the proposed policy refs, `refdes_waiver.json`, the 25 assembly-locator source exceptions, the generated locator hidden list and hidden-part set, and all 25 manifest page refs.

The native ref/X/Y/rotation/side/pad-number/net tuples equal the source exception tuples. The source ref/value/MPN/LCSC/X/Y/rotation/side/pad-number/net tuples equal the generated locator tuples. The manifest binds the exact ef72 board and exact locator config. No duplicate exists in any compared 25-ref set.

The owning checker at `assembly_locator_check.py` requires exact equality between policy waiver refs and locator exception refs. The current source list fails that predicate because it carries three stale identities and omits three actual identities. The proposal makes the predicate true without broadening the waiver or changing its conditions.

## Scope and remaining prerequisites

This judgment does not accept render usability, placement, routing, manufacturing readiness, or release packaging. The exception remains conditional on fresh exact A-LOCATOR and current-render acceptance. The earlier focused witness inspected all three added atlas pages, but a fresh full current-render review of all 25 pages remains owed. Canonical renewal must rerun normal project gates after adoption; stale checkpoints cannot be reused. `LAYOUT-001` remains open with 3/3 attempts spent. The order verdict remains DO-NOT-ORDER.
