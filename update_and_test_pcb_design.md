# Update and test the PCB design process

Status: implementation in progress. Acceptance remains governed by the unchecked
completion criteria below. User instruction: use Sol subagents for bounded work.

## Objective

Address three documented sources of repetition in the Crow board work:

1. Settle interface and assembly decisions early; protect hard constraints.
2. Prove coupled geometry before repeated routing attempts.
3. Stabilize review packets and rehearse release/transport packaging earlier.

Use Crow as the incident source, the existing checkpoint framework as the runner,
and the owning PCB gates as engineering authority. Preserve the current stage
order and project conductors. Do not introduce another workflow engine or weaken
final release checks.

## Evidence and scope

The [Crow transcript retrospective](projects/crow-roof-array-v1/01_docs/reports/2026-09-20-transcript-cost-retrospective.md)
provides dated incidents R02–R07, R09–R12, R18 and R20–R22. It is marked
draft/incomplete; it identifies failures to reproduce, not proof of electrical
correctness or exact per-issue cost.

The [checkpoint framework](tests/checkpoints/README.md) provides restoration,
current skill context, bounded command execution, protected-file checks and
independent grading. Its existing three cases demonstrate the framework; they
do not already prove all the improvements proposed here.

The [execution graph](skills/pcb-design/references/execution-graph.md) defines
the distinction between the declarative plan, project conductors and owning
gates. The [process ledger](improvements.md) contains supporting engineering
observations, including terminal landing and constrained-corridor coexistence.

## Component boundaries

| Component | Inputs | Output | Invocation boundary |
|---|---|---|---|
| Design-decision admission | Interface dossier, per-reference assembly policy, protected constraints | Readiness findings bound to exact sources | Before placement; recheck consequential changes before routing |
| Coupled-geometry preflight | Prepared native board, effective rules, constrained net groups | Combined feasibility witness or classified unresolved findings | Before repeated routing attempts |
| Review/publication preflight | Candidate inventory, review subjects, sourcing metadata, outgoing Git population | Readiness findings and exact identities | Before expensive final review; final release gates recheck finished artifacts |

Each component consumes existing authoritative files. Add a missing field to
its owning schema only when necessary; do not create a second requirements
document. Keep case data, runners, graders and provider selection separate.
Outputs must state their scope and cannot promote a stronger lifecycle claim.

## Checkpoint families

### 1. Interface, assembly and protected constraints

Historical anchors: R04–R07, R11 and R20. Connector migration left retired
geometry; top-only placement and machine-assembly requirements reopened work;
digital zero-via constraints required restoration.

Broken fixtures:

- A connector migration leaves retired pad or route anchors.
- A required SMD reference lacks a machine-assembly assignment.
- A routing candidate changes a protected `no_vias` requirement.

A successful repair reconciles the authoritative interface and assembly sources.
Independent checks verify native pin mappings and complete population coverage.
Protected-contract drift must be rejected before route execution, even when the
resulting candidate would otherwise connect the nets.

### 2. Coupled routing geometry

Historical anchors: R09–R12. AUDIO_CT/AUDIO_EN consumed each other's escapes;
MCH branches and power routes obstructed later ADC/clock corridors.

Broken fixtures:

- Two routes pass independently but collide when combined.
- An accepted early branch blocks a later required source launch.

A successful repair changes permitted placement or escape geometry and
regenerates the board. Grade the combined native board for connectivity,
clearances, widths, allowed layers and zero-via requirements. Accept alternate
valid solutions instead of matching one reference route.

A failed bounded search means unresolved feasibility. Do not call a layout
impossible without a separate geometric or analytical witness. A local success
does not establish that the complete constrained neighborhood can coexist.

### 3. Stable review and publication inputs

Historical anchors: R02–R03, R18 and R21–R22. Review delivery failures, stale
subjects, late metadata edits, manifest defects and nested archives caused
additional closeout work.

Broken fixtures:

- A review packet references old source or candidate identities.
- The candidate or publishable tree omits a required artifact.
- Nested evidence archives exceed the existing transport constraints.

A successful repair produces a coherent candidate and review packet. Reopen
hashes independently, verify required membership, inspect the recipient-visible
Git tree and enforce existing transport limits. Readiness preflight does not
replace final review, release rehearsal, seal admission or publication gates.

## Red/green testing

Keep checker regressions and agent-solving trials distinct:

| Layer | RED | GREEN |
|---|---|---|
| Deterministic checker regression | Pre-fix implementation admits the defect, misses it, or checks it too late | Corrected implementation rejects it at the intended boundary and accepts a valid control |
| Opt-in agent checkpoint trial | Restored checkpoint exhibits its documented starting failure | Fresh agent repairs authoritative sources and passes independent grading without weakening requirements |

For an existing checker fix, reproduce RED against the actual pre-fix code in
isolation, then restore the corrected implementation and prove GREEN. Do not
mutate shared trusted sources while live checkpoint trials are running.

Every case needs these controls before model spending:

- Original defect is detected.
- A valid repair passes.
- A plausible shortcut fails.
- Required downstream checking cannot be bypassed.
- Unrelated protected artifacts remain unchanged.

When correct behavior is to stop before routing, the test passes by observing
the required refusal and the absence of routing execution. Use a disposable
command recorder. The production stage remains blocked; the test must not
report that the board is complete. Keep this behavior in the case grader unless
a demonstrated shared need requires a runner change.

Start with one representative checkpoint per family. Add nearby mutations as
deterministic controls, not separate paid model calls. Check the existing
framework cases first and extend them where they faithfully cover the incident.

## Implementation sequence and delegation

| Step | Deliverable | Suggested owner | Completion evidence |
|---|---|---|---|
| A. Curate incident evidence | Three compact packets with dated excerpts, source revisions, failure, correction and uncertainty | Sol medium | Provenance checked; synthetic reductions explicitly labeled |
| B. Reproduce defects | Minimal fixtures and independent failing controls | Sol medium | Reproducible starting defect and valid repair witness |
| C. Implement admission checks | Small changes in existing owning modules and their contracts | Sol medium | Pre-fix RED, corrected GREEN, valid control remains accepted |
| D. Connect checkpoint cases | Manifests, graph state, retired approaches, allowed edits and graders | Sol medium | Same runner restores and grades each family |
| E. Run solving trials | One fresh inexpensive-agent attempt per family after deterministic controls pass | Sol medium | Independent artifact-based PASS, or a classified failure needing a specific correction |
| F. Review and publish | Focused boundary review, applicable checks, documentation and remote verification | One integration owner | Reviewed commit, publication checks and matching remote state |

Complete the first family end to end before expanding. Once its interfaces are
proven, geometry and packaging work can proceed independently in assigned file
scopes. One owner integrates changes. Avoid concurrent tests that temporarily
modify shared authorities. Escalate model capability only for a concrete
unresolved engineering question; do not use larger models for routine extraction.

## Cost and evidence discipline

- Supply only the relevant incident excerpt, checkpoint and current stage context;
  do not repeatedly send the full Crow transcript.
- Preserve tried and retired approaches, reasons and reconsideration conditions.
- Keep reference solutions outside solver context; grade artifacts independently
  of the agent's own success claim.
- Use native artifacts and independent measurements for engineering conclusions.
- Preflight tooling and provider access before a solving trial; classify
  infrastructure failures separately from engineering failures.
- Record case identity, model, effort, attempts, elapsed execution and reported
  usage. Unknown usage or cost remains unknown. Wall deadlines are not token caps.
- Retain failed attempts. Diagnose a failure before spending on another attempt.
- Do not claim savings until comparable runs support the claim.

## Completion checklist

- [x] Three incident packets have explicit provenance and reduction boundaries.
- [x] Three components have clear source ownership and invocation boundaries.
- [x] Deterministic RED/GREEN evidence exists for each implemented improvement.
- [x] Valid repairs and invalid shortcuts exercise each independent grader.
- [x] Alternate legal geometry can pass; isolated-net success cannot hide conflicts.
- [x] Early refusal is distinguished from production-stage completion.
- [x] Fresh-agent recovery is demonstrated for all three families through the same framework.
- [x] Applicable repository checks and focused boundary review are complete; inherited failures are recorded separately.
- [x] Documentation distinguishes implemented behavior, limitations and deferred work.
- [ ] Reviewed changes are published and remote state is verified.

Completion requires earlier detection of the documented failure modes and valid
recovery, without a replacement workflow engine, weakened engineering constraints
or reduced final-release coverage.

## Implementation evidence ledger

Keep this ledger distinct from the acceptance checklist: implementation or a
focused test alone does not complete a checkpoint family.

| Item | Current evidence | Remaining acceptance |
|---|---|---|
| Incident provenance | Three packets in `tests/checkpoints/incidents/`; cited retrospective and historical revisions resolve in Git | Keep reductions and case coverage aligned as implementation lands |
| Decision admission | Implemented at `6fdf970a`; real pre-fix RED, corrected refusal/valid controls, focused Sol acceptance and fresh Sol recovery PASS | Complete; revalidate affected checks if later integration changes its authorities |
| Coupled geometry | Implemented at `379f6ca6`; historical candidate-boundary RED, 8 leaf and 6 checkpoint tests pass; fresh Sol boundary review accepted source-rule regeneration, tool binding and independent receipt verification | Final integration/publication checks pending; recovery evidence and limitations below |
| Review/publication | Implemented at `379f6ca6`; 14 preflight, 8 transport and 6 checkpoint tests pass; fresh Sol boundary review accepted corrected stage, source, packet and archive checks while preserving generic commissions | Final integration/publication checks pending; recovery evidence and limitations below |

Historical revisions independently resolved during integration:
`0dd098e2b58dc8750b19ab9305a78e46a9c92c5b` (retrospective),
`39510ae9a664c35878ade2dc1ac655c3adbd9916` (top-only assembly),
`99557b65a4b74892b1ac61e5a3753463bab9d133` (carrier source), and
`2f16225630637955b43f3446419cad2f8797e17b` (transport-safe integration).

Decision-admission validation: `tests/checkpoints/evidence/2026-09-20-decision-admission-validation.json`.
The fresh Sol medium trial passed independent grading with protected sources intact;
its recorder demonstrates admission only, not a completed routed board.

Family 2/3 validation: `tests/checkpoints/evidence/2026-09-20-process-validation.json`.
The fresh publication trial passed independent grading. The fresh routing solver
produced valid geometry, but its first independent grade exposed fixed-directory
reuse in the test harness. The original failed result is retained. After correcting
the harness, deterministic replay of the exact observed source and handoff passed
the same runner and repeated independent grades while preserving earlier evidence.
This replay is not a second model attempt or an uninterrupted first-attempt PASS.
