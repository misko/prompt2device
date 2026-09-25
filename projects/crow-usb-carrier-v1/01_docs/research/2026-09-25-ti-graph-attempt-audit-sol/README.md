# Crow TI research versus the P1–P5 work graph

**Audit finding: the source-bound TI placement and route trials are not recorded as P1 work-item attempts.** On the exact current `03_src/modular_plan.json` and generated `circuit.json` bound in `receipt.json`, `modular_design.evaluate` passes 569/569 functional owners and 59/59 cross-block nets. Its sole P1 root, `p1_floorplan_569_after_native_evidence_abort`, is `READY` with **0/1 attempts**, no observed completion, and `engineering_acceptance: NOT_EVALUATED`. The named P1 evidence output `06_build/evidence/modular_work/p1_floorplan_569_after_native_evidence_abort.json` does not exist. All dependent P2–P5 work remains blocked by the P1 root or later prerequisites.

The three archived failed `TaskAttempt` records are real but belong to earlier P1 task IDs and different graph subjects; the current evaluator rejects them as unknown work items. The hash-bound unified TI P1 diagnostic returns `FAIL`/`p1_accepted=false`, while the later source-generated ADC8N local-route trial remains research with no canonical P1/P2 promotion. Neither has a current-root `TaskAttempt`, output completion, or entry in an observations index. `modular_design` deliberately reads only explicitly supplied `attempt_path` observations; a research board, DRC result, or route receipt does not silently spend a work-item attempt.

No formal attempt is added here. The current root allows one attempt. The focused checker test uses a **temporary counterfactual**, never a saved or observed attempt, to show that one failed current-subject receipt would make the root `BACKTRACK_REQUIRED` at 1/1 and leave all descendants unrecorded. Writing an attempt-looking JSON for the research failure without a real bounded runtime envelope would misstate how it was produced and consume the sole allowance if later indexed.

The minimal valid recording step, when a fresh P1 dispatch is actually admitted, is to freeze the exact plan/circuit and governed candidate inputs, launch one schema-2 `TaskEnvelope` for the current P1 root with `attempt_index=0` and `replacement_index=0`, retain the runtime's immutable `TaskAttempt` and completion outputs under the project evidence root, and add its relative `attempt_path` to an observations index. Reopen it with `modular_design.py PLAN CIRCUIT --observations INDEX --evidence-root PROJECT`. If it fails, preserve `BACKTRACK_REQUIRED` and repair through a new authorized graph/subject rather than resetting or incrementing the one-attempt budget. If it passes, `WORK_RECORDED` would mean only delivery; independent P1 geometry and downstream gates still decide engineering acceptance. The present TI research has unresolved P1 and coupled P2 placement/route debt, so this packet is an audit of the recording boundary, not an attempt launch.

Reproduce from repository root:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-graph-attempt-audit-sol/audit.py
python3 -m unittest discover -s projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-graph-attempt-audit-sol -p 'test_graph.py' -q
```

`audit.py` pins the current plan/circuit bytes, unified TI checker result, and ADC8N route note; reopens the archived attempts through `TaskAttempt.from_mapping`; and uses the actual graph evaluator for both the zero-observation state and temporary one-failure budget test. It writes only this research receipt. No canonical source/board, P1/P2 acceptance, or graph attempt ledger changed.
