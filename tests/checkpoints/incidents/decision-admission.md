# Incident packet: decision admission

## Scope and provenance

This packet supports the planned **Interface, assembly and protected constraints** checkpoint family. It covers retrospective incidents R04–R07, R11 and R20; it is not itself a readiness result. The retrospective is `projects/crow-roof-array-v1/01_docs/reports/2026-09-20-transcript-cost-retrospective.md` at verified revision `0dd098e2b58dc8750b19ab9305a78e46a9c92c5b` (2026-09-20). Earlier event history was bounded through `git log`, `git blame` and the named journals; raw session material was not used.

Verified historical anchors:

- 2026-09-12: RJ45 source acceptance and later footprint/model repair, revisions `33b0443f`, `ada576b0`, `6a19815f`.
- 2026-09-13: top-only SMD requirement and source enforcement, revision `39510ae9a664c35878ade2dc1ac655c3adbd9916`.
- 2026-09-15: digital `no_vias` restoration is recorded as R11; the exact first correcting commit was not isolated by this bounded audit: **UNKNOWN**.
- 2026-09-16: completed carrier source and machine-population correction, revisions `99557b65a4b74892b1ac61e5a3753463bab9d133` and `97e8f35d371d3f473766a92e56922b83566bc62c`.

## Compact source excerpts (9 lines)

> R04: cable migration passed through Cat cable with Molex before the exact factory RJ45 source was adopted.
>
> R05: retired Micro-Fit coordinates, conflicting footprints and missing model transforms survived the migration.
>
> R07: the top-only SMD requirement arrived after mixed-side placement and reopened placement review.
>
> R11: apparent routing progress was inadmissible until digital no-via contracts were restored.
>
> R20: the carrier correction assigned 306 top SMDs to machine placement and 27 THT parts to manual fitting.

The first four summaries come from the dated R04, R05, R07 and R11 rows in the retrospective at `0dd098e2`; the last is corroborated by the 2026-09-16 journal entry introduced at `97e8f35d`. They are paraphrases, not transcript quotations.

## Failure, cause and correction

The established failures were authority drift across a high-fanout connector migration, a late assembly-side decision, incomplete per-reference assembly ownership, and loss of protected route constraints. The records directly establish the changes and resulting rework. The broader root-cause statement—decisions were admitted too late or were not protected at the routing boundary—is an **inference** used to design the checkpoint.

Successful historical corrections were adoption of the exact RJ45 source and matching native identities, regeneration for top-only placement, an assembly policy in which every fitted SMD is top-side and machine assigned, and restoration of zero-via digital routing. Current authorities include:

- `projects/crow-audio-carrier-v1/03_src/rules/assembly.yaml`
- `projects/crow-mic-pod-v3/03_src/rules/assembly.yaml`
- `projects/crow-audio-carrier-v1/03_src/rules/nets.yaml`
- `projects/crow-audio-carrier-v1/03_src/floorplan.yaml`
- `projects/crow-mic-pod-v3/03_src/floorplan.yaml`
- both projects' `03_src/rules/connector_assemblies.yaml` and generated native boards

The owning schemas and native artifacts remain authoritative; this packet must never become a second requirements source.

## Exact regression properties

The planned family must prove all of the following:

1. Retired connector pads, route anchors, pin mappings or model identities are rejected after migration; the current native pin mapping must match the interface authority.
2. Every required fitted SMD has exactly one machine-assembly assignment and obeys the declared side policy; manual/THT exclusions remain explicit and complete.
3. A candidate that changes a protected `no_vias` declaration is refused before any routing command runs. The recorder must show zero route invocations and the stage remains blocked.
4. A valid reconciled control passes; a superficially connected candidate that weakens the contract fails; downstream checking and unrelated protected artifacts cannot be bypassed or modified.

These are **planned** RED/GREEN properties from `update_and_test_pcb_design.md`. Existing `crow-assembly-population` exercises a different archived consignment defect, and no existing checkpoint proves this complete Crow interface/assembly/no-via family.

## Retired approaches and reduction limits

Retired approaches: mixed-side fitted SMD placement; old Micro-Fit geometry after RJ45 adoption; treating routing success under weakened `no_vias` rules as progress; and deriving a complete assembly census from machine BOM rows alone. Reconsider only after an explicit interface or assembly-policy change updates every owning authority and invalidates affected downstream receipts; protected routing constraints require an engineering decision, not a solver shortcut.

Any checkpoint fixture will be a labeled reduction. It cannot reproduce all connector mechanics, source migrations, 333 carrier components, reviewer history, or the complete 13-net digital contract. It proves only the stated mutations at the admission boundary. It cannot establish electrical correctness, placement completion, route completion, live JLC allocation, or release readiness. No per-issue token, time or money attribution is known.
