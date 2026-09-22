# contract: skills/pcb-design/

**Purpose** — the prompt-to-device orchestration skill: takes a plain-language
hardware brief through iterative development to reviewed, reproducible PCB
fabrication and optional enclosure evidence. Order admission, a physical first
article, firmware, and a product-level digital twin remain separately governed
claims. Carries its own project-independent seed set under
`templates/` (contracts + config schemas + doc starters) — commission copies
from HERE, never from a project (the 2026-07-20 clean-room contamination is
why).

## Allowed

| Pattern | What |
|---|---|
| `SKILL.md` | the small orchestration kernel: lifecycle, invariants, capability-profile decisions, and direct reference router |
| `agents/**` | Codex UI metadata for the installed skill; generated from the current SKILL.md and required to keep `$pcb-design` in the default prompt |
| `contracts.md` | this file |
| `scripts/**` | fail-closed project commissioning, shared connector-assembly contract compiler, publication-boundary orchestration gates, the pure reference router and authority/coverage checker; enclosure and fabrication mechanics remain owned by `pcb-enclosure` and `jlcpcb-fab` |
| `templates/**` | the seed set: `contracts/` (stage contracts, nested to match project layout), `03_src/` + `03_tscircuit/` schema examples, `01_docs/` starters, `ORCHESTRATION_STATE.md` (the coordinator's state-journal skeleton, copied per campaign not per project), `project.gitignore`, `rebuild_all.sh`, `README.md` |
| `references/**` | one-owner orchestration procedures, the typed stage contract, and the machine-readable authority map; KiCad, enclosure and JLC mechanics remain routed to their owning skills |

## Audit

Experimental graph/pilot tools and optional issue accounting do not impose
migration requirements on existing projects. Project drivers and their owning
gates retain authority; new integration needs a named consumer and demonstrated
missing capability. Existing adopted receipt/acceptance contracts still apply.

- `pipeline_registry.py change_impact` computes diagnostic downstream impact
  from declared symbols, stages and categories; it cannot authorize cached
  evidence or execution. `tests/t1_pipeline_registry.py` pins independent
  siblings, propagation, malformed inputs and changed output ownership.
- `scripts/pipeline_issue_ledger.py` owns optional append-only execution/usage
  accounting, distinct from findings, task attempts and engineering verdicts.
  `pcb_flow.py run --issue/--usage-ledger` is its first opt-in consumer.
  Closed records, deduplication, missing usage, overlap and interruption
  semantics are tested in `tests/t1_pipeline_issue_ledger.py`; actual validator
  exit preservation and admission failures in `tests/t2_pcb_flow.py`.
- `scripts/pipeline_usage_import.py` owns versioned offline source manifests,
  explicit Codex turn attribution and coverage; `openrouter_usage_adapter.py`
  normalizes saved receipts. Both consume the ledger's public normalization and
  atomic batch APIs. Schema-2 USAGE has no execution timing and never grants an
  engineering verdict. Source snapshots and manifests remain local; no provider
  call or private transcript export occurs. Validate with
  `tests/t1_pipeline_usage_import.py` and `tests/t1_openrouter_usage_adapter.py`.

- `scripts/commission_project.py` owns the exact scaffold manifest;
  `templates/README.md` summarizes it. A new project must pass
  `contracts_audit.py --walk --root <proj>` with zero violations before design.
- Scaffold CLI coverage counts every file written from the complete plan; it
  does not admit PCB-COMMISSION. The report auditor names its one-report
  denominator. CLI coverage is tested in `tests/t1_pcb_commission.py` and
  `tests/t1_project_reports.py`.
- Template drift is the failure mode this layout kills: there is exactly ONE
  copy of each stage contract (here), so nothing can silently diverge.
- `references/lifecycle-and-backtrack.md` owns deficiency triage. Commission
  seeds `01_docs/DEFICIENCIES.md`; existing release review carries its snapshot
  under verification. This backlog does not replace gate/findings authority
  or introduce a separate approval procedure.
- `scripts/skill_authority_check.py` freezes the pre-refactor policy
  denominator, requires every routed reference to be reachable, and rejects
  duplicate authority or a core outside its line/word budget.
- `scripts/pause_state.py` owns the single current pause manifest and generated
  STATUS/RESUME views. Project prose may explain history but may not compete
  with its checkpoint/receipt hashes or semantic state id.
- `scripts/decision_progress.py` reads optional investigation history inside
  the existing findings ledger. It owns cumulative decision-progress accounting,
  evidence identity and continuation/reassessment output, never engineering
  acceptance. Its closed schema is documented in `references/lifecycle-and-backtrack.md`
  and the 01_docs contract template. Historical observations are author
  assessments, not reconstructed TaskAttempt telemetry. Validate with
  `tests/t1_decision_progress.py`; ordinary unadopted boards remain unchanged.
  Its explicit `reserve_launch` API, called only by named `pcb_flow.py run`
  dispatch, appends a reservation to the same ledger before execution; the
  read-only evaluator refuses further dispatch while an assessment is owed.
- `scripts/connector_assembly_contract.py` owns the exact shared connector
  schema and deterministic base receipt. `scripts/connector_assembly_phase_gate.py`
  owns an additive source/full wrapper bound to that exact receipt, all compiler
  inputs, and `rules/connector_assembly_phases.yaml`. Source admits only closed,
  stable-ID physical-qualification classes; full still requires the unchanged
  base `PASS` with zero unknowns. Exact typed no-operated evidence yields
  applicability-only `N-A`. The current enclosure adapter and all release
  consumers continue to revalidate the base receipt at their existing bar; a
  source wrapper is not service authority. New mappings may not copy connector dimensions; current enclosure
  schema-v1 inline candidates remain a declared migration gap and cannot become
  shared service authority.

- `pipeline_execution.py` preserves schema-1 records and adds explicit schema-2
  completion declarations. `pipeline_runtime.py` owns fresh task allocation,
  bounded process receipts and the coordinator-observed agent open/close adapter;
  `pipeline_artifacts.py` reopens exact declared output sets without promotion.
  Validate with execution, runtime and artifact suites. Host events are observed
  evidence, not authenticated process telemetry or engineering verdicts.

- `scripts/modular_design.py` owns diagnostic schema-1 block membership,
  crossing-interface coverage, and P1–P5 child-work dependencies inside the
  existing lifecycle. It derives refs and complete crossing endpoints from
  generated `circuit.json`, consumes identity-bound schema-1 `TaskAttempt`
  observations, and always leaves engineering acceptance unevaluated. Validate
  with `tests/t1_modular_design.py`; no result authorizes geometry, routing,
  cache reuse, or stage promotion.

- `pipeline_qualification.py` composes startup checks, with native fixture
  mechanics in `kicad-pcb/scripts/qualification_probe.py`. Stable cache identity
  covers executed tools, loaded libraries and probe sources; live reviewer
  availability is separately observed and never promised by that cache.
  `tests/t1_pipeline_qualification.py` covers both native polarities, missing
  reporting support, changed identities and preserved failed attempts.

- Schema-2 same-owner repair allowances are immutable task declarations.
  Runtime dispatch records predecessor identity, coordinator assessment and
  cumulative spend in TaskAttempt output, with one reserved successor per
  predecessor. Named investigations also use the existing findings ledger;
  neither accounting path resets the other. Runtime tests cover admitted
  local repairs, changed premises, semantic handoffs and exhausted/branched tasks.

- `scripts/publication_transport_gate.py` owns the pre-push object census. It
  rejects ordinary Git blobs at GitHub's 100 MiB limit and conservatively
  bounded aggregate batches before the semantic publication gate. Oversized
  durable evidence uses explicit Git LFS paths; new reviews remain compact and
  may not recursively bundle prior frozen inputs.

## Structure

`templates/contracts/<stage>/[<sub>/]contracts.md` mirrors where each file
lands in a project. Schema YAMLs carry their provenance board in a header
comment; the KEYS are the contract, the values are placeholders.

- `scripts/connector_prototype_admission.sh PY CS STAGE ADR [--compile-base]`
  shares mechanics formerly in a single project's admission helper. Call only
  from a project with an independently accepted prototype decision. SOURCE
  must pass against exact current bytes. FULL is always graded and remains
  INCOMPLETE when physical unknowns remain; only exact rc2 after SOURCE success
  can continue, labeled FIRST-ARTICLE-ONLY / DO-NOT-ORDER. Invalid, stale and
  unclassified authority is fatal. This creates no release/order authorization.
  Clean and hostile cases are in `t1_connector_assembly_phase_gate.py`.
