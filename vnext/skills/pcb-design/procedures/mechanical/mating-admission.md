# Registered 3D mating admission

Use the existing routing/mating owner; this is not a second orchestrator or an
assembly/physical qualification receipt. Read [3D evidence](3d-verification.md).
Run the upgraded routing command with a Python environment satisfying
`tools/mechanical-requirements.txt` and pcbnew, for example
`.venv-mechanical/bin/python -B tools/routing.py issue --kind mating ...`.
The owner uses the local `.venv-mechanical/bin/python` for frozen scene replay
when present, otherwise its current interpreter. Downstream owning checks can
therefore call the same gate; a missing kernel runtime fails, never skips replay.

## Explicit adoption

Routing contract version3 retains version2's authority and selected placement
receipt/hash. Add `mating_requirements` (project-relative JSON) and
`mating_receipt` (new project-relative receipt path). Preserve previous contracts
and receipts. Version1/2 are historical: the current CLI cannot issue new
prose-only mating acceptance through them. Historical checks retain their
archived interpretation; they do not claim this upgrade.

Requirements JSON: `{version:1,scope_evidence:[paths],interfaces:{id:row}}`.
Each row has `board`, nonempty unique `references`, `requirement` and nonempty
`evidence`. The coordinator owns this inventory, grounded in actual intended
mating and access claims. Group equivalent references on one board when useful;
review and machine geometry checks still cover every actual instance. Empty
inventory requires an independently justified not-applicable disposition, not
missing geometry. Cable/service access not covered here remains explicit at its
routing/assembly owner; an unspecified enclosure does not acquire a fit claim.

## Review extension

The ordinary independent mating review keeps applicability/geometry/interfaces
criteria, author/reviewer separation, complete subjects and scoped evidence.
Add `mechanical` with exactly:

- `scene_manifest`, `scene_output`: exact registered-scene input/output paths.
- `toolchain`, `toolchain_files`: retained producer directory and exact relative
  file-to-SHA256 inventory. Its `tools/mechanical_scene.py` and dependencies must
  match the scene's recorded tools. Preserve the actual trusted producer; hashes
  are not authentication for arbitrary downloaded code. Archive any required
  producer instructions too. This decouples acceptance-tool evolution from
  unchanged scene evidence; never refresh the old scene's hashes.
- `interfaces`: exactly the contracted IDs. Each maps six checks—`registration`,
  `model_coverage`, `clearance`, `tolerances`, `engagement`, `access`—to
  `{verdict:"PASS",rationale,evidence:[paths]}`. These are independent engineering
  judgments on measured/source-supported facts, not exporter-supplied approval.
  Explain genuine non-applicability within the relevant criterion; don't omit it.
- `limitations`: exhaustive dispositions for the scene's unresolved claims,
  each model's limitations and each board-datum limitation. IDs come from
  `mating_admission.limitation_inventory(report)` (hash of owner + newline + text).
  Each has `classification`, `rationale`, nonempty `evidence`. Classifications:
  `design_resolved`, `physical_qualification`, `outside_mating_scope`.

Qualification classification does not waive an interface check. Unknown design
geometry or a known collision cannot be renamed as a later physical test. Design
acceptance may rely on explicit, independently reviewed finite procurement and
assembly limits with demonstrated feasible geometry, while actual lot inspection
remains unperformed. Do not invent vendor tolerances or capability. Unsupported
engagement/height/seat geometry remains a design gap. A physical first article
is not automatically required before every prototype design release; use the
actual stage and release scope, and retain order/qualification holds separately.

## What the owner enforces

Before issue/check: reverify the accepted placement; bind the requirement inventory,
all scene inputs/artifacts and archived producer; compare scene boards against
current placement pads/nets/layers/outline/keepouts/attributes/models. Only the
existing layout owner's cosmetic projection is ignored. Reject nominal contact,
collision or access failures, missing interface/limitation coverage and failed
feature judgments. Then rerun the frozen producer with the mechanical runtime,
reopening STEP geometry and comparing image pixels. Recheck hashes after replay.
Use the reported subjects in the independent review; final ordinary review
validation binds them all. A report-only pass cannot issue a receipt.

The scene itself remains `INCOMPLETE`/`accepted:false`: it is nominal evidence,
not an engineering verdict. The owning receipt supplies a separately scoped
design-stage judgment only after all checks pass. Physical qualification, full
assembly verification, routing/layout reacceptance and release remain separate.

Positive/negative regressions exercise real scene replay, stale geometry/tools,
changed placement, missing artifacts, collision, incomplete interface/limitation
coverage and false not-applicable claims. Synthetic engineering judgments are
fixtures, not approval of an actual board. Independent real-board review is
still required; unavailable reviewers do not become automatic approval.
