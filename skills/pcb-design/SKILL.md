---
name: pcb-design
description: Drive prompt-to-device development from a plain-language hardware brief through iterative architecture, sourcing, schematic, routed KiCad layout, independent verification, fabrication files, optional enclosure artifacts, release, and first article. Use for a new PCB or device, a resumed design, review, release, enclosure handoff, or physical bring-up.
---

# PCB design

Turn a plain-language device brief into reviewable, regenerable manufacturing
artifacts through explicit development and backtrack cycles. Make every
stronger claim—release, order, first article, production—only at its own
evidence boundary.

Deliver native/rendered schematics, KiCad source, Gerber/drill/BOM/CPL payloads,
PCB renders, STEP assemblies and optional enclosure artifacts. The JLC digital
twin verifies the board; governed firmware and a product-level digital twin
remain future work under IMP-234 and IMP-236.

`pcb-design` owns lifecycle composition. It delegates electrical and layout
mechanics to `kicad-pcb`, manufacturing mechanics to `jlcpcb-fab`, and optional
mechanical work to `pcb-enclosure`. Project `contracts.md` files own exact
artifact membership and immutable release rules. Script `--help` output owns
exact CLI syntax. `improvements.md` records work and rationale; it is never an
engineering authority.

## Quick start

Accept a direct invocation containing only a natural-language brief. Do not
require the user or an upstream agent to translate it into YAML, CLI flags, or
PCB terminology. Preserve the brief verbatim, expose consequential unknowns as
fact locks, and ask only for choices that materially affect safety,
architecture, mating, fabrication, or cost.

From the repository root, put the user's original brief in a UTF-8 text file
and create a new governed scaffold:

```bash
python3 skills/pcb-design/scripts/commission_project.py my-board \
  --brief-file /path/to/original-brief.txt \
  --signal-integrity ordinary \
  --assembly jlcpcb \
  --firmware forbidden \
  --target design
```

Use `high_speed_digital` for USB or another controlled digital interface, and
`rf` only for an intentional RF/microwave path. Add `--foreign-mating` when the
board consumes geometry from hardware this repository does not control. Add
`--enclosure` only when mechanical work is in scope; choose co-design versus
derived later, when the enclosure can bind exact PCB authority. The command
refuses an existing destination and writes no PCB geometry. It creates the
governed source tree, verbatim brief record, capability profile, and a
conductor-enforced `01_docs/COMMISSIONING-HOLD.md`. Success means the scaffold exists;
`PCB-COMMISSION` remains `INCOMPLETE`.
`--assembly jlcpcb` means the populated PCBA evidence path; it is not shorthand
for bare-board fabrication alone.

Inspect the selected plan before design work:

```bash
PROJECT_SLUG=my-board
python3 skills/pcb-design/scripts/skill_reference_router.py \
  --profile "projects/${PROJECT_SLUG}/01_docs/capability-profile.json" \
  --at-stage PCB-COMMISSION \
  --json
```

Resolve the brief's fact locks, capability profile and architecture before
building. The commissioning hold spans commission, architecture and sourcing;
do not invoke a rebuild conductor while it exists. Each stage produces its
own evidence. Manual hold removal is not admission; IMP-235 tracks the missing
commission-admission compositor.

New JLC high-speed projects declare critical selections before either build
conductor; missing declarations on older projects are not selection evidence.
Use the [sourcing admission procedure](references/execution-graph.md) for exact
identity, independent suitability and stock policy. An adopted initial stock
snapshot stays locked against later inventory fluctuations.
`prototype_only` permits only the explicitly scoped research producer with
its reviewed test plan and open release-blocking findings. Ordinary rebuild,
release and order paths still reject it. This restriction takes precedence
over the full/reuse instructions below; research does not remove the hold.

## Plan is not execution

The router selects composable procedures. It does not run gates, prove
applicability, promote artifacts, review releases, or publish.

Read [the execution graph](references/execution-graph.md) before operating a
project. It distinguishes:

1. the 19-stage declarative lifecycle in `skill-authority-map.json`;
2. the real project conductors, `03_src/rebuild_all.sh` and
   `03_src/rebuild_reuse.sh`;
3. the owning gates that grade exact schematic, board, fabrication, review,
   release, and physical evidence.

Conditional stages omitted by a profile remain disclosure-time `UNKNOWN`
placeholders. They are not evidence that engineering applicability is false.

## Lifecycle at a glance

```text
commission -> architecture -> sourcing
  -> [RF context/source] -> schematic -> placement -> [foreign mating]
  -> routing -> [RF realized] -> layout seal
  -> fabrication -> assembly verification -> [RF fab review]
  -> release review -> release seal
  -> publication | first article -> production
```

Targets stop at `layout seal`, `release seal`, `publication`, `first article`,
or `production`. High-speed digital composes inside ordinary schematic/layout/
fabrication stages; it does not select RF-named stages. Firmware is a separate
explicit handoff and never appears because a board merely contains a
programmable part.

For new native work, run the startup qualification described in
[execution-runtime.md](references/execution-runtime.md). Use its validated task
delivery path for bounded work with declared outputs. Keep one implementation
owner through pre-admitted routine repairs; scripts handle mechanical loops.
Independent review still starts with a fresh live reviewer qualification and
retains every semantic handoff boundary.

At each selected stage:

```text
validate exact inputs and applicability
  -> run bounded work with progress
  -> reopen outputs through the owning gate
     PASS       persist, commit, journal, advance
     FAIL       change owning source, regenerate, regrade
     INCOMPLETE persist what is owed and pause visibly
     timeout    preserve the previous accepted bundle and diagnose
     plateau    classify the cause and backtrack to its upstream owner
```

Triage findings through the [deficiency workflow](references/lifecycle-and-backtrack.md#8-deficiency-triage).
Record supported non-blocking improvements in `01_docs/DEFICIENCIES.md` and
continue; reopen them only on new evidence or at next-release planning.

## Core invariants

1. Preserve the original prompt verbatim in `01_docs/BRIEF.md`; later user
   directives append to its log rather than rewriting history.
2. Keep one writer per live board. Parallel agents may research or review in
   isolated worktrees; they do not concurrently mutate the same design.
3. Change human-owned source and regenerate. Never repair generated KiCad,
   route candidates, fabrication payloads, or sealed releases in place.
4. Grade the bytes just produced. Reviews and receipts bind both raw and
   semantic identity; never refresh an independently reviewed decision snapshot from current source to make a change pass.
5. Require a nonzero denominator and explicit applicability. Zero findings
   over zero graded items is `INCOMPLETE`, not success.
6. Bound every producer/reviewer attempt with progress and a deadline. An
   error, timeout, or optional diagnostic never replaces prior accepted state.
7. Separate claims: generated, DRC-clean, layout-sealed, fabrication-staged,
   release-sealed, published, order-ready, first-article-passed, and production
   authorized are different states.
8. Commit at green boundaries. Backtracking changes the owning source and
   invalidates every downstream artifact whose semantic input changed.
9. Treat human schematic readability and registered 3D mating direction as
   real gates, not decoration after machine checks.
10. Start with the cheapest fabrication tier that satisfies locked facts.
    Advanced stackup/process capability needs evidence and a decision record.
11. Treat every operated connector as a complete receptacle/mate/tool/cable
    assembly. Bare-body or render clearance never proves fastening or service.

## Stage ownership

| Work | Owner and boundary |
|---|---|
| Brief, requirements, architecture, lifecycle, backtracking | `pcb-design` |
| Schematic/netlist, placement, routing, DRC/parity, SI/RF realization | `kicad-pcb` |
| Gerber/drill/BOM/CPL, stock/population/rotation, JLC twin and staging | `jlcpcb-fab` |
| Enclosure intent, access, independent fasteners, motion sweeps, fit/thermal evidence and enclosure releases | `pcb-enclosure` |
| Exact project/release contents | nearest project `contracts.md` |
| Publication admission | `pcb-design` publication gate plus repository protection |
| Physical authorization | first-article card and measured record |

Enclosure work is a parallel lifecycle. Its `CAD_READY`, `PRINT_VERIFIED`, and
`THERMALLY_VERIFIED` statuses describe only one exact mechanical candidate.
They do not promote the PCB. An enclosure release may bind an unchanged PCB
release without resealing it. Firmware currently ends at an explicit handoff;
the absent firmware release stream is tracked by IMP-234.

## Reference router

Read a selected reference completely before acting. Do not load unrelated
domains. References longer than 100 lines have a contents list.

### PCB lifecycle

| Need | Read |
|---|---|
| Commission, fact locks, sourcing, module/tier decisions | [commission-and-scope.md](references/commission-and-scope.md) |
| Connector mate/tool/cable facts and shared service contract | [connector-assembly-contract.md](references/connector-assembly-contract.md) |
| Canonical stage/command/dependency map | [execution-graph.md](references/execution-graph.md) |
| Backtrack, checkpoint, journal, or handoff | [lifecycle-and-backtrack.md](references/lifecycle-and-backtrack.md) |
| Human investigation report | [project-reports.md](references/project-reports.md) |
| Bounded task/process/agent execution | [execution-runtime.md](references/execution-runtime.md) |
| Operator pause/resume evidence | [operator-checkpoints.md](references/operator-checkpoints.md) |
| Review, seal, supersession, publication | [review-and-publication.md](references/review-and-publication.md) |
| Stage/result/artifact/review schemas | [pipeline-stage-contract.md](references/pipeline-stage-contract.md) |
| Part-freeze/electrical/placement boundary composition | [early-boundary-gates.md](references/early-boundary-gates.md) |
| Functional decomposition, block interfaces, and P1–P5 child work | [modular-design.md](references/modular-design.md) |
| Compute/model tier | [compute-tiers.md](references/compute-tiers.md) |
### KiCad electrical and layout

| Need | Read |
|---|---|
| Policy IDs and electrical/layout canon | [design-policies.md](../kicad-pcb/references/design-policies.md) |
| TSX and schematic generation | [tscircuit-folder.md](../kicad-pcb/references/tscircuit-folder.md), then [schematic-generation.md](../kicad-pcb/references/schematic-generation.md) only for its documented fallback/review boundary |
| Placement, adjacency, body clearance, corridors | [placement-and-proximity.md](../kicad-pcb/references/placement-and-proximity.md) |
| Selected-IC reference research and datasheet/layout precedents | [layout-precedents.md](../kicad-pcb/references/layout-precedents.md) |
| Physical stack and source-to-prep ownership | [source-to-prep-authority.md](../kicad-pcb/references/source-to-prep-authority.md) |
| Route mechanics | [routing-pipeline.md](../kicad-pcb/references/routing-pipeline.md) and [fast-pcb-flow.md](../kicad-pcb/references/fast-pcb-flow.md) |
| Route ownership, transaction, exploration | [route-ownership.md](../kicad-pcb/references/route-ownership.md), [route-candidate-contract.md](../kicad-pcb/references/route-candidate-contract.md), [route-exploration.md](../kicad-pcb/references/route-exploration.md) |
| High-speed digital | [signal-integrity.md](../kicad-pcb/references/signal-integrity.md) |
| RF applicability/context | [rf-context.md](../kicad-pcb/references/rf/rf-context.md) |
| RF reviews | [rf-schematic-review-protocol.md](../kicad-pcb/references/rf-schematic-review-protocol.md), [rf-pcb-review-protocol.md](../kicad-pcb/references/rf-pcb-review-protocol.md), [rf-fab-review-protocol.md](../kicad-pcb/references/rf-fab-review-protocol.md) |

### Manufacturing and physical work

| Need | Read |
|---|---|
| JLC BOM/CPL/stock/population/rotation | [assembly-and-order.md](../jlcpcb-fab/references/assembly-and-order.md) |
| JLC CAD twin/model registration | [digital-twin.md](../jlcpcb-fab/references/digital-twin.md) |
| Edge-connector mating orientation | [connector-orientation.md](../jlcpcb-fab/references/connector-orientation.md) |
| Exact fabrication/assembly staging | [release-staging.md](../jlcpcb-fab/references/release-staging.md) |
| Physical board bring-up | [first-article-bringup.md](../jlcpcb-fab/references/first-article-bringup.md) |
| Enclosure commission and schema | [mechanical-commission.md](../pcb-enclosure/references/mechanical-commission.md), [configuration-schema-v2.md](../pcb-enclosure/references/configuration-schema-v2.md), [interface-schema.md](../pcb-enclosure/references/interface-schema.md) |
| Enclosure assembly and geometry | [assembly-and-motion.md](../pcb-enclosure/references/assembly-and-motion.md), [enclosure-topologies.md](../pcb-enclosure/references/enclosure-topologies.md), [connector-access.md](../pcb-enclosure/references/connector-access.md), [fasteners-and-inserts.md](../pcb-enclosure/references/fasteners-and-inserts.md), [fdm-printability.md](../pcb-enclosure/references/fdm-printability.md) |
| Enclosure evidence and release | [verification-and-release.md](../pcb-enclosure/references/verification-and-release.md), [release-stream.md](../pcb-enclosure/references/release-stream.md) |

## Operate the current project

Read `01_docs/STATUS.md`, the journal tail, capability profile, current source,
latest accepted receipts, and latest non-superseded release before acting. Run
the full project conductor when TSX or schematic source changed. Use the reuse
conductor only when the pinned schematic is unchanged. Fresh route exploration
is a separate candidate workflow; canonical rebuild replays the authenticated
route source selected by `03_src/route.yaml`.
Exact commands and branch behavior are in `references/execution-graph.md` and
the owning scripts' `--help`.

At release, stage mutable bytes first, run the independent review battery once
per material state, rehearse the publication-internal contract, then follow the
project's normative two-commit seal. Never mutate a sealed directory. Before a
material push, require `P-PUBLISH PASS` from `pcb_publication_gate.py` against
the exact base/head pair.

After three non-improving iterations on one engineering decision, use `D-BACK`.
New schemas, reports or agents do not reset it; use the native loop in `references/modular-design.md`.
For recurring engineering investigations, apply the decision-progress protocol
in `references/lifecycle-and-backtrack.md`; a new model or handoff is not a reset.
A fresh agent resumes from committed source, the live beacon, journal, and
content-addressed handoff—not from hidden conversation history.

Use the [single-candidate operator workflow](references/modular-design.md#single-candidate-operator-workflow):
prepare, evaluate, repair, adopt through the owning conductor, then release.
Bind source, board, netlist and effective rules in the existing candidate record.
Derive native geometry without changing design intent or refreshing approval;
invalidate affected reviews when their subject changes. Keep the existing
findings budget and acceptance consumer; add no parallel status registry.

Use the existing project driver and owning checks; fix authoritative source
and rerun affected mandatory gates. The [stage graph](references/pipeline-stage-contract.md)
is diagnostic, not reuse permission. [Issue accounting](references/execution-runtime.md)
is optional and grants no engineering acceptance. Experimental pilots and
adapter migration are not prerequisites for ordinary board work. Add process
infrastructure only for a named consumer and concrete failure that existing
tools cannot handle; keep nonblocking convenience work in the deficiency list.

## Human reports

For investigations and option comparisons, follow
[the project report contract](references/project-reports.md) under
`01_docs/reports/`. Distinguish measured/cited facts, inferences, proposals and
owed tests. Adopt decisions into their owning ADR/source; reports do not grant
design authority.

## Validate changes to this skill

Run the authority and documentation gates after changing this skill, router,
catalog, templates, or references:

```bash
python3 skills/pcb-design/scripts/skill_authority_check.py
python3 tests/t1_skill_progressive_disclosure.py
python3 tests/t1_pcb_documentation.py
```

Run the applicable pipeline unit suites before changing execution authority.
Preserve previous behavior through Git history, not a second live legacy skill.

## Report

Report assumptions and decisions, selected target, current stage, measured gate
scoreboard with denominators, exact artifact/release paths, source and seal
commits, and every operator/order/first-article hold. Mark claims `MEASURED` or
`INHERITED`; use readiness language no stronger than the evidence.
