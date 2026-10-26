# Pinned existing owners — schematic pilot binding

Resolve the baseline checkout from the root `dependencies.json` lock (or the
context helper's explicit `--baseline-root` override during local tests).
Paths below are relative to that validated dependency root. Read every
selected instruction file **completely** before acting. This candidate is a
dispatcher, not a copy of these owners or a claim that the typed Python
runtime executes the full project graph.

| Task | Required baseline instructions |
|---|---|
| All schematic actions | `skills/pcb-design/SKILL.md`; `skills/pcb-design/workflow/STAGES.md`; `skills/pcb-design/references/execution-graph.md`; `skills/kicad-pcb/SKILL.md`; `skills/kicad-pcb/references/design-policies.md` |
| Generate | `skills/kicad-pcb/references/tscircuit-folder.md`; `skills/kicad-pcb/references/schematic-generation.md`; `skills/pcb-design/references/early-boundary-gates.md`; `skills/pcb-design/references/commission-and-scope.md` when intake/sourcing evidence is not yet accepted |
| Review | `skills/pcb-design/references/review-and-publication.md`; `skills/kicad-pcb/references/pin-review-protocol.md` for imported pin-map facts/readability lens; `skills/kicad-pcb/references/schematic-generation.md` |
| Repair | Failed action's references above; `skills/pcb-design/references/lifecycle-and-backtrack.md`; `skills/pcb-design/references/early-boundary-gates.md` when electrical closure failed |
| Resume/recover | `skills/pcb-design/references/lifecycle-and-backtrack.md`; `skills/pcb-design/references/operator-checkpoints.md`; then the references of the next selected action |

Also load graph-selected conditional owners: `skills/kicad-pcb/references/signal-integrity.md`
for high-speed digital, or `skills/kicad-pcb/references/rf/rf-context.md` and
`skills/kicad-pcb/references/rf-schematic-review-protocol.md` for RF. The
project's nearest `contracts.md`, capability profile, original brief, accepted
source/part receipts, current journal/findings and exact candidate evidence
remain mandatory. Resolve disputed datasheet facts against the pinned exact
part/revision, not a summary.

The project `03_src/rebuild_all.sh` owns changed-source execution and its
schematic checkpoint. Its documented `--resume-after-schematic-review`
continues only after exact review acceptance; this run stops before placement
instead. `03_src/rebuild_reuse.sh` is for unchanged pinned schematic source.
The project conductor, `pcb_flow.py` where invoked, and KiCad/JLC scripts own
actual command order, bounded process execution and gate verdicts. Consult
their `--help`; this binding does not invent flags for individual gates.

Existing project records own state: `01_docs/STATUS.md` and journal for human
progress; `01_docs/pause_state.json` for current pause authority where used;
attempts, findings, exact receipts and review commissions at the project
paths required by the owning driver and contracts. Status and handoff prose
are views, not substitutes for reopenable hashes and gate evidence. The
baseline disclosure router is not execution. A typed shadow stage result is
not an accepted bundle. Missing owner files, stale identities, contradictory
pause views or a missing gate must fail visibly, never be guessed into PASS.
