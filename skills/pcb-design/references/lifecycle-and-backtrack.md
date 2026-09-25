# Lifecycle, handoff, and backtrack procedure

Use this procedure to execute stages, bound long-running work, recover from a
red gate, and resume safely from repository state.

## Contents

1. Stage state machine
2. Evidence and journals
3. Planned handoffs
4. Bounded work and visibility
5. D-BACK diagnosis
6. Backtrack destinations
7. Writer and promotion discipline
8. Deficiency triage

Policy IDs owned by this procedure: `D-BACK`, `M-BEACON`, `M-JRNL`, and
`M-LEARN`.

## 1. Stage state machine

Treat the pipeline as a loop, not a one-way checklist:

```text
enter(stage)
  -> validate required inputs and subject identity
  -> perform bounded work
  -> measure the owning gate
     PASS             -> commit evidence; finish journal; advance
     FAIL improving   -> iterate current source/config; remeasure
     FAIL plateau     -> diagnose; backtrack; regenerate downstream
     WAIT human       -> persist commission; pause visibly
     ERROR/TIMEOUT    -> preserve prior accepted bundle; diagnose
```

A repeated red gate with no new hypothesis is the prohibited state. A red gate
that names its owner and backtrack destination is normal pipeline behavior.

Use the typed `StageSpec` and `StageResult` interfaces in
`pipeline-stage-contract.md` for orchestration changes. Commands, paths, and
domain limits stay outside semantic stage identity. The current project driver
remains execution authority until its shadow trace agrees with the typed plan.

## 2. Evidence and journals

Maintain three distinct records:

- `01_docs/journal/<stage>.md`: append start, iteration, stuck, handoff, and
  finish events with measured result and next implication;
- `01_docs/learnings/<stage>.md`: root cause and reusable prevention proposal,
  marked as candidate canon or project-local;
- `01_docs/STATUS[-<board>].md`: overwrite the live seven-field beacon at each
  transition and immediately before/after a long operation.

Do not reconstruct journals at release time. A journal's existence is not
stage coverage; every executed stage needs its own events. The beacon is live
state, not history. Run the beacon checker after a seal and reject duplicated,
stale, or superseded-release claims.

Every load-bearing claim in a handoff or report must be marked `MEASURED` with
method or `INHERITED` with source and unverified status. Never instruct a
successor not to rederive an inherited number.

## 3. Planned handoffs

Require fresh handoffs after adopted schematic review, after accepted
placement/pilot feasibility before global routing, immediately on D-BACK, and
after layout seal. When the host exposes comparable live context telemetry,
warn at 60 percent and require a handoff at 70 percent before beginning more
expensive work. Semantic boundaries remain mandatory when telemetry is
unavailable. At a boundary:

1. Commit the green state.
2. Append a handoff journal entry with current stage, next command, open
   hypotheses, and measured gates.
3. Refresh the status beacon.
4. Generate and validate the compact content-addressed handoff through the
   KiCad flow helper.
5. Generate a strict `TaskEnvelope` naming `context_mode: FRESH`, the exact
   packet, deadline, role ceiling, replacement limit and writer scope.
6. End the current session; do not let it continue mechanical work past a
   mandatory boundary.

A successor reads only the verified handoff, beacon, tail of the current-stage
journal, and exact files named by those records. Do not preload the transcript,
whole journal/learnings directories, or an earlier reviewer's reasoning.

## 4. Bounded work and visibility

Classify execution time before running it:

- local/cheap mechanical checks;
- bounded CPU work;
- network work with retry/backoff;
- independent review wait;
- operator wait.

Separately declare the agent role as `mechanical`, `authoring`, or `judgment`.
`execution_class` attributes time; `agent_role` sets the logical compute
ceiling. Do not reuse one vocabulary for the other. The companion contracts in
`pipeline_execution.py` bind these facts without changing `StageSpec`.

Give executable stages a positive deadline. Stream heartbeats or durable
progress for work whose normal runtime can appear silent. A timeout terminates
the process group, produces a non-pass result, and preserves the previous
accepted artifact bundle.

Use the cheapest capable compute tier. Scripts own deterministic loops;
low-cost agents may apply table-known config changes; high-judgment work is
reserved for causal diagnosis and upstream backtracking. Do not repeatedly
resume a context-heavy agent for mechanical iterations.

Human review is not a polling accident. Persist an immutable commission and
pause with `INCOMPLETE`; never manufacture a witness or infer acceptance from
silence. The coordinator, not review prose, enforces the deadline: interrupt a
late reviewer, materialize every unfinished checklist row as unresolved, and
allow at most one fresh replacement on the same exact subject. User approval
advances only the stage explicitly under review.

### Routine repairs under one implementation owner

For new bounded subprocess work, the coordinator may pre-admit a schema-2
same-owner repair allowance using the execution runtime. A wrong cwd, missing
directory/executable or missing output can be corrected by that owner inside
the original scope and deadline. Each execution remains a charged, retained
TaskAttempt; setup repairs receive no engineering progress credit.

Use `pcb_flow.py task-repair` with the previous allocated envelope and a
coordinator assessment bound to real evidence. The dispatcher preserves the
deadline, owner, hypothesis, scope, cumulative cap and predecessor chain. It
reserves one successor before launch; changing labels or branching from an old
attempt cannot reclaim that slot. Declared recurring investigations also reserve
through the existing findings ledger, including the initial execution. Assess
those reservations there before another experiment. Neither path resets the other.

A changed premise, scope, unsupported method or plateau still requires fresh
D-BACK judgment. Accepted schematic, placement/pilot and layout-seal boundaries
remain mandatory. Provider failure, unknown cleanup, deadline exhaustion and
context pressure do not authorize an automatic replacement. Older envelopes
without an explicit allowance retain their stricter behavior. Scripts run the
mechanical iterations; the implementation owner need not change for each one.

## 5. D-BACK diagnosis

Stop local iteration after three consecutive attempts with no measured
improvement, when the same finding IDs recur, or when the current configuration
cannot express a remedy.

Before moving upstream:

1. Group findings by cause; do not treat a heterogeneous count as one problem.
2. Reopen the exact artifact and verify the causal hypothesis.
3. Name the upstream decision that produced the finding.
4. Commit the failed attempt as evidence.
5. Append a `stuck` journal event with plateau and hypothesis.
6. Write the learning while the evidence is live.

Triage findings under section 8 first. Resolve cheap independent blockers
before escalating the surviving hard group; leave deferred improvements out
of the current repair loop.

When a checker stops at its first refusal, that refusal is not the complete
repair scope. For repeated failures in a shared source representation, use one
bounded, read-only census of the affected population before the next repair.
Distinguish an incorrect design, valid geometry the checker cannot represent,
and unfinished work belonging to a later stage. Keep the original gate result;
the diagnostic census cannot advance the pipeline. Choose a coherent repair
from the complete causes rather than commissioning one repair per reported row.

For modular placement, track that decision against one current native
candidate. Record required connections proved, DRC findings by class, required
filled-reference proof and external dependencies. A decreasing aggregate count
cannot offset a newly introduced critical violation. A checker extension or
new worker may enable an experiment, but does not itself prove its physical
result or reset the cumulative attempt limits. Reuse isolated quick/full
candidate grading before authoring another geometric approximation.

Before changing a checker because a synthetic fixture behaves unexpectedly,
verify what its real consumer constructed. For native CAD, inspect the exported
geometry and transforms, not only the fixture's intended dimensions. Compare
the original checker, proposed checker and exact product artifact to distinguish
a regression from an existing limitation. A documented limitation still needs
the canon's evidence and cannot discharge an affected product requirement.

### Decision progress for recurring engineering investigations

Use the existing `01_docs/findings.yaml`, not another blocker ledger. Before
repeated analysis, give the finding a requirement citation, relevant operating
states, objective closure condition, owning stage and a decision question.
Separate a demonstrated defect, an unresolved protection argument, a realized
layout check, a first-article measurement and order-time sourcing. Their existing
acceptance boundaries remain authoritative; moving a hold needs explicit cited
scope authority, not a convenient label. A model-validity premise is not a new
product requirement. Invalid model predictions establish neither hardware
failure nor safety. Known defects and unresolved safety arguments remain open.

Add the optional `investigation` schema below only to recurring investigations.
Routine work and boards without it keep the existing flow. Before and after
each such attempt, run `decision_progress.py PROJECT --finding FINDING_ID` from
this skill's `scripts/`. Use `--shadow` for historical observation before first
adoption. It reopens evidence and emits only continuation/reassessment advice,
never an engineering verdict. A malformed record is invalid even in shadow.
Use `pcb_flow.py run PROJECT --stage STAGE --investigation FINDING_ID -- CMD`
for subsequent bounded local experiments. `REASSESS` stops that launch, not
the entire project. Architecture comparison remains useful bounded work.

The closed schema-1 mapping lives inside the finding:

| Field | Meaning |
|---|---|
| `schema` | `1` |
| `requirement` | `{path, sha256, locator}` citing project authority |
| `due_stage` | Existing lifecycle stage ID; not permission to move a hold |
| `operating_states` | Nonempty relevant-state list, not a universal state catalogue |
| `question` | The design decision to resolve |
| `milestones` | Finite ID-to-closure-condition mapping, declared before the work |
| `max_nonimproving_attempts`, `max_attempts` | Positive cumulative limits; normally three non-improving attempts, plus a justified total budget |
| `launches` | Ordered `{id, subject_sha256}` reservations written before guarded dispatch |
| `history` | Ordered durable coordinator observations, appended rather than rewritten |
| `next` | `{action, hypothesis, on_support, on_reject, uncertainty}` |

Each history observation is exactly `{id, subject_sha256, origin, hypothesis,
result, model_domain, progress, evidence}`. `origin` is `executed` or
`historical_assessment`; retrospective classification never invents execution
timestamps or a TaskAttempt. `model_domain` is `within`, `outside`, `unknown`
or `not_applicable`; `progress` is a list of milestone IDs. Evidence is a
nonempty list of `{path, sha256}` project-relative bindings. The source hash
names the studied subject, not necessarily today's revised circuit.

Credit each evidenced milestone once: candidate elimination, a source
correction, or uncertainty reduction sufficient to change a decision can count.
More samples, precision, reports, new hashes, and repeated GREEN tests do not.
Outside/unknown-domain predictions receive no milestone credit. A coordinator
must assess the content: hash verification cannot prove a scientific claim.
The total cap applies even if every attempt reports novel progress.

`next.action` is `investigate` or `reassess`; the two outcome branches must
name distinct decisions. `uncertainty` is `bounded` or `decision_limiting`.
If uncertainty prevents the experiment deciding between options, reassess the
model, obtain better authority, or compare architectures with credible margin.
Prefer fewer interacting assumptions and lower total verification effort when
they satisfy the brief; do not mandate a particular topology or numeric margin.

History follows the stable finding ID across source revisions and handoffs.
Do not reset it by renaming a finding, deleting history, enlarging budgets, or
claiming a fresh context. A changed decision/requirement requires a reviewed,
evidence-backed reassessment preserving the prior history and cumulative spend;
the read-only guard is not a tamper-proof journal or a scientific reviewer.
Do not automatically close a finding after a milestone or a budget exhaustion.

The evaluator CLI is read-only. The explicit `pcb_flow.py run --investigation`
dispatch seam first reserves a slot in the same ledger, using a nonblocking
Linux advisory lock and a byte-change check. A reservation is not a completed
execution claim; even a failed dispatch must be assessed before continuing.
Append the actual assessment under the reservation's ID/source hash with
`origin: executed`, citing the real outcome including a failed dispatch.
The union of reservation and assessment IDs determines spend, so a completion
does not count twice. `ASSESS_PENDING` refuses another launch until the result
is accounted for. Duplicate explicit YAML keys, which could hide history, are
invalid; ordinary merge-default overrides retain their existing YAML meaning.
Reservation writes preserve semantic fields, not hand-formatting/comments.

The compact PCB handoff derives its decision view from this ledger and pins
both ledger and evaluator. Store raw results once and reference them; do not
copy full models into every handoff. Append the assessment before handing off;
a pending/unreported attempt must be accounted for before another experiment.

## 6. Backtrack destinations

| Symptom | Reopen | Change |
|---|---|---|
| Local clearance/via tail | Placement | Adjacency, orientation, corridor |
| Congestion across regions | Placement, then architecture | Floorplan area, bank split, outline |
| Width/via/hole floor impossible | Fab tier or part | `D-TIER` or `D-ESC` |
| Package cannot escape | Part selection | Package/part |
| No compliant sourceable part | Architecture, then specification | Topology or `D-SPEC` |
| Schematic/parity churn | Dossier/source | Pin map, aliases, source model |
| Critical route omitted | Route contract | Net inventory, engine, layer/via policy |
| Repeated 3D registration error | Model/adjudication producer | Frame, anchor, source model—not render pixels |
| Architecture difficulty caused by ambiguous requirement | Brief/specification | Ask user or record simplest conservative reading |

Fix the owning source—brief, ADR, dossier, TSX, floorplan, rules, or promoted
route. Regenerate every downstream artifact. Never patch `04_kicad`, CSVs, or
a staged release by hand.

The same stage may be re-entered three times on genuinely different upstream
hypotheses. A fourth arrival requires escalation one stage farther upstream or
an honest-stop ADR naming the exhausted hypothesis space.

## 7. Writer and promotion discipline

Only one writer/process edits a board's live source tree. Parallel work is
limited to independent research, calculation, or read-only review of exact
artifacts. Speculative downstream work belongs in an isolated permanent
worktree and cannot be promoted while an upstream gate is red.

Every producer follows a transaction:

1. write to a fresh sibling staging directory;
2. reject undeclared, missing, empty, stale, or unparsable outputs;
3. reopen outputs and cross-check key fields;
4. write the bundle manifest last;
5. atomically promote only a passing bundle;
6. preserve the previous accepted bundle on failure.

Promote the final route chain into committed source. Keep generated build data
disposable unless a contract names it as release or resume evidence. Commit at
green gates so Git remains the geometry undo and handoff boundary.

## 8. Deficiency triage

Use `01_docs/DEFICIENCIES.md` as the small, human-readable release backlog.
Commission seeds it from the skill template; on an existing project, create it
when the first item needs deferral. Classify each finding once:

- **Fix now:** violates the current brief, fails a required gate/review, or
  lacks evidence required at the current boundary for electrical function,
  safety, assembly, mating, or manufacturability. Unknown impact is not
  evidence of a minor issue.
- **Defer:** evidence shows the current release meets its requirements and
  remains functional, safe, manufacturable, and usable as documented. Examples
  include optional extra labels when required markings are already legible,
  cosmetic render polish, and optional test-access improvements when the
  required bring-up procedure already works.
- **Later-boundary hold:** belongs to an explicitly separate order,
  first-article, or production boundary under its existing rules. Stock
  shortages or owed hardware measurements are not cosmetic deficiencies;
  preserve their actual hold and make no stronger readiness claim.

For each deferred item record a stable ID, affected revision/refs, practical
impact, evidence supporting deferral (including any workaround), owner, and
next-release action with a closure test. Link an existing review finding or
`findings.yaml` row rather than creating a competing gate verdict. The list
cannot waive a gate, lower a floor, or drop a user requirement. If the impact
cannot be established cheaply from current evidence, retain the blocker and
name the specific test needed to decide it.

Within the agreed scope, the implementing agent may defer eligible items
without another permission round or separate review commission. Include the
list in the existing review packet. Reviewers still report blockers; merely
preferring a deferred enhancement does not reopen it. Reopen only when new
evidence changes its impact or affected scope, or during next-release planning.
Do not reroute, regenerate renders, or repeat accepted reviews solely to polish
an eligible deferred item.

Before sealing, reconcile the list with actual gate/review outcomes and copy
it into staged `verification/DEFICIENCIES.md`; summarize remaining items and
later-boundary holds in the release handoff. Use the normal manifest hashing
and seal procedure. This is disclosure within the existing review, not a new
approval gate. Never backfill a sealed release. At the next revision, triage
carried items against the new brief; keep IDs and record closure evidence or
an explicit continued deferral rather than silently dropping them.
