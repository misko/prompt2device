# Native routing adapter — pilot

Use `/usr/bin/python3 tools/routing.py`. This builds from editable native KiCad
source, not an autorouter: use KiCad or a separately reviewed project generator
to author copper. Native source and project settings are versioned inputs.
No legacy execution, external routing service, footprint movement or purchases.

```
routing.py issue --kind mating --project PROJECT --review REVIEW
routing.py check --kind mating --project PROJECT
routing.py build --project PROJECT --manifest MANIFEST --output NEW_OUTPUT
routing.py verify --project PROJECT --manifest MANIFEST --output OUTPUT
routing.py issue --project PROJECT --review REVIEW
routing.py check --project PROJECT
```

All paths except PROJECT are project-relative. New output/receipt writes refuse
existing targets. Failed drafts remain available; a successful build/verify can
report incomplete routes and is NOT acceptance.

`01_docs/routing-contract.json` version1 binds `authority`, `authority_sha256`
and `placement_receipt_sha256`. Every operation rechecks the exact placement
receipt and its upstream chain. New placement needs explicit routing re-adoption;
retain prior contracts/candidates/receipts before replacing an active binding.
Do not silently update a hash to repair a stale review.
Version2 adds a required project-relative `placement_receipt` path, permitting
an independently reviewed successor placement receipt without replacing its
historical file. It still reruns the same placement certificate and binds that
exact selected path/hash in every review. Version1 retains its fixed receipt
path and cannot select a different one. Neither version bypasses mating review
or grants routing acceptance from placement alone.
New mating admission requires version3 and the mechanical runtime. Follow
[registered mating admission](../mechanical/mating-admission.md): explicit scope,
frozen real-scene replay, current placement binding and complete independent
feature/limitation judgments. Version3 also selects a versioned mating receipt.

MANIFEST version1 has `boards` with exactly the placement board keys. Each board
entry contains exactly `source` (.kicad_pcb) and `project` (.kicad_pro).
Optional `evidence` is a top-level list, not a board-entry field. Bind generator
scripts and transitive inputs there when they support the review; the producer
does not execute arbitrary code. Native copper is the source of truth.

```json
{
  "version": 1,
  "boards": {
    "main": {"source": "source.kicad_pcb", "project": "source.kicad_pro"}
  },
  "evidence": ["producer.py", "producer-inputs.json"]
}
```

Replace `main` with the actual placement keys and use project-relative paths.
The pilot rejects custom .kicad_dru files and DRC exclusions. It preserves complete
serialized footprint/pad/net/layer/outline identity (including cosmetic footprint
fields); changed footprint content requires explicit upstream handling.
Board-level rule areas and native groups are also protected placement identity;
dropping, weakening or detaching a keepout requires upstream reacceptance.

Build copies into isolation, enables listed DRC checks, refills zones and saves
native boards, runs all-severity/all-track DRC and exports composite F/B previews.
Unreported/ignored checks fail rather than disappear. Verify repeats this process
from source and compares native forms (only top-level ordering ignored), settings,
plots and DRC. Only report date/source name and plot timestamp are non-semantic.
Stale fills and manually edited/forged generated reports fail replay. Engineering
review inspects actual individual layers/returns; a composite is not sufficient
evidence by itself. Native source is sufficient to reproduce the exports; rerunning
an optional author generator is a separately stated reproducibility claim.
Electrical membership is checked through the freshly verified placement-to-
schematic chain and exact native pad/net identity. The CLI is not run with
`--schematic-parity` in this isolated PCB workspace; its empty parity field is
not evidence of a second independent schematic comparison.

Independent reviews are dated `08_reviews/*.md` with exactly one JSON block:
schema1, stage (`KICAD-MATING-IMPORT` or `KICAD-ROUTING`), distinct author/reviewer,
verdict PASS, `subjects` map of exact project-relative file SHA256s, and `checks`
mapping every criterion to {verdict:PASS,evidence:[bound paths],rationale}.
Coordinator alone issues receipts. Each check replays owning verification.

Historical mating criteria: applicability, geometry, interfaces. Add `applicability` equal
to applicable or not_applicable and nonempty bound `scope_evidence`. Applicable
reviews also need nonempty bound `geometry_evidence`; actual fit/collision is
independently reviewed, not automatically measured by this tool. Unknown fails.
The subject set includes routing contract, authority and placement receipt.

Routing criteria: completeness, physical, electrical, interfaces, reproducibility.
Add manifest/output paths; bind all subjects returned by verify plus engineering
sources/reports. No unconnected item or physical DRC fault permits issue. A small
explicit set of library/text/silkscreen findings remains visible for independent
review and layout-seal disposition; it does not include copper/edge/drill faults.
No configurable copper waiver is provided. Stack, loading, timing and thermal
sufficiency remain the independent reviewer's responsibility, not a DRC claim.

Receipts: `06_build/checkpoints/mating_clearance.json` and `routed_board.json`.
This interface preserves the existing journal/status; it does not dispatch work,
count retries, choose a route, or grant manufacturing approval.
