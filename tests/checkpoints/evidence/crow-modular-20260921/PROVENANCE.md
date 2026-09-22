# Crow modular trial reconstruction provenance

The carrier trial input was prepared from commit
`d7c3ac4416b1ee3c233b98de869ad410e2e61788`, whose Crow carrier project tree is
`aa582e5ac63c235731140bed64fd5070504ad522`. There is no historical revision
that combines the current selected parts with a genuinely untouched
post-selection/pre-placement state. This tree is therefore labeled a
**reconstructed current-parts replay input**, not a recovered checkpoint.

The preparer copied selected part dossiers, exact footprint/model libraries,
TSX schematic intent, and accepted electrical/interface/assembly/stackup
authority. It generated a fresh input floorplan intended to contain only an
inherited envelope and mounting-hole set, stackup, fabrication minima, pin/net
assertions and connector edge-facing constraints. Its component anchor map is
empty.

Preparation finding: the initial 304-member run incorrectly narrowed the
pinned baseline outline from `x1: 172.0` (156 mm width) to ADR-0030's proposed
`x1: 170.0` (154 mm width), while leaving the baseline M3 centers unchanged.
The initial manifest and hashes remain preserved as forensic truth for the
already launched schematic envelope. The preparer is corrected for future runs
to copy the pinned baseline `board.outline` and `board.mounting_holes` values
verbatim and label them inherited trial inputs, not hard requirements. The
initial child was not rewritten under its running owner. After that owner
finished, the placement handoff restored the pinned 156 mm envelope, preserving
the empty anchor map and recording the change in `INPUT_ADJUSTMENTS.json` and
`PLACEMENT_INPUT_BOUNDARY.md` in the isolated trial.

The fresh schematic trial also exposed a missing inherited input:
`rules/protection_paths.yaml` references `01_docs/FIRST_ARTICLE_TEST_PLAN.md`,
which the initial selection omitted. The source E-SURGE check correctly
remained incomplete. Future preparation includes that requirements document;
the coordinator restored its exact pinned bytes after the schematic writer
finished, then reran the source gate: four of four gate families passed. This is a reconstruction repair, not a relaxed rule or
physical first-article evidence.

The reconstruction excludes generated CAD, netlists and PDFs; build output;
release payloads; reviews; journal, research and report archives; current
`route.yaml`; promoted/final route chains; route seeds; learned component
anchors/repeated-cell poses/regions; placement keepouts and zones; locator and
model-registration poses; and solution-specific waivers. The old solved board
and copper are unavailable inside the child directory.

`crow_modular_trial.py prepare` required the complete live source project to be
clean against the pinned baseline, captured SHA-256 identities for every
selected source file before copying, compared them again afterward, and
rechecked the baseline diff. `crow_modular_trial.py verify` reopened every
copied member, reproduced the input-tree digest, rejected forbidden paths, and
confirmed that no learned placement anchors, zones or keepouts survived.
That verification applies to the frozen initial input. Once the trial writes
fresh schematic or physical candidates, runtime provenance and explicit
source-bound comparisons must track those outputs; the initial-input verifier
is expected to reject the mutated working tree rather than bless later work.

No schematic producer, KiCad native generator, placement tool, router, DRC,
review, fabrication or release command was run during reconstruction. The
inherited TSX is schematic intent only. Fresh schematic generation and review
are the first trial result; every physical result remains owed.


## Execution checkpoint after schematic generation

Implementation commit: `d9a49cee`. Isolated mutable trial:
`/home/mouse9911/gits/circuits-trials/crow-modular-20260921/crow-audio-carrier-v1`.
The original carrier project remains unchanged. The trial inherits schematic
intent; this is fresh generation and review, not a claim of independent
schematic invention from only a bill of materials.

Measured source evidence: 333/333 component census, 178/178 net labels,
241/241 pin assertions, zero blocking native ERC errors, four of four
early-design gate families, and the complete E-CLOSURE battery at 9/9 specialists. The modular plan owns all 333 components across
12 blocks and covers all 33 crossing nets. Its 27 placement child tasks remain
pending at this checkpoint. These counts do not prove physical feasibility.

The first schematic author delivered artifacts but its runtime attempt is
INCOMPLETE because Python cache writes escaped its declared scope. That failed
receipt remains preserved. Later source rechecks and an independent review
packet reopen the artifacts; the failed delivery is not rewritten as PASS.
An initial reviewer-delivery probe likewise failed on the output directory;
a separately admitted corrected probe passed. Native qualification passed
four of four checks. No token or cost total is inferred from absent telemetry.

Focused implementation validation passed: modular tests 10/10, trial-input
checks 4/4, progressive disclosure 14/14, PCB documentation 15/15 and schema
reader 28/28. Skill authority and the default contract audit passed. The full
contract suite had three existing project failures outside this change;
whole-repository success is not claimed. Sol performed the implementation,
trial generation, and independent implementation review.


During independent visual review, an apparent clipped-title finding was
withdrawn after reopening the pages individually at original detail: the
batched image viewer had misled the reviewer. The coordinator stopped the
already dispatched presentation repair. Its writer-scope comparison passed;
source, PDF, and circuit hashes were unchanged. The aborted attempt remains
INCOMPLETE, not a claimed successful repair. Independent review continued
against the original packet.


The independent schematic review subsequently completed with topology SOUND
and schematic-render SOUND (all 19 pages inspected). Runtime delivery PASS;
`pre_route_review_check.py --phase schematic` reopened both reviews and passed
2/2 required artifacts. This admits placement work only. Both reviews retain
`DO-NOT-ORDER`. The completed packet and outputs are at the sibling
`schematic-review/06_build/task_runs/review/` under the trial root.

Reviewed artifact identities:

| Artifact | SHA-256 |
|---|---|
| Fresh circuit JSON | `adff7da6a45109578739994c51a664133fa0f06327a1b97b239361cc7cf33520` |
| Human schematic PDF | `0ad692b855784ddee1d40c268985794c82ab8cc06dc485840862c880322effa2` |
| Native schematic | `eef3b223966eb658b75761ee251ffad94c20be33e5ef307a648bad61ffdf3aed` |
| Raw exported netlist | `d9115fbff897dcbcd82e7e55ce7ec9697eaa83d86437ec5ad0aec39e25a99379` |
| Modular source plan | `db2e6bb5e6f1af0477c76eb1f491fa488761f675d6b9ce082cf2c08e22ec8dc9` |

A separately bounded Sol physical-trial owner subsequently generated a coarse
placement from the empty anchors. Its delivery completed, but engineering
remained INCOMPLETE at P2; see the physical-trial findings below. Placement
acceptance and full-board routing remain pending.

## Model-binding reconstruction finding

The initial reconstruction copied the selected 3D model assets and their
provenance but dropped three scalar `placement.patterns[].model_override`
bindings from the pinned source: the sixteen `C_A1P/N` through `C_A8P/N` film
capacitors, eight `F1` through `F8` branch fuses, and `F_IN`. Those bindings
replace only the model filename and contain no offset, scale, rotation, side or
board coordinate. Their omission made the coarse physical candidate unable to
recover the selected package model identity from the retained assets alone.

The initial manifest remains immutable forensic evidence, and the active trial
was not modified under its running owner. Future preparation now projects
exactly each source `match` selector and scalar `${KIPRJMOD}/../03_src/lib/3dmodels/`
path, verifies that it resolves to a copied `.step` or `.wrl` beneath that
library, and rejects mappings/transforms, path traversal, or any adjacent
placement field. Root must restore these three model-only bindings through an
explicit new trial mapping at the next idle placement boundary. This restores
selected package model identity; it does not inherit model-registration vectors,
component placement, board geometry, copper, or physical model-coverage proof.

## Physical-trial findings

The first current trial candidate (`20d7dd4bda069e96aceb7cab490d03f09ffdcb6884a37265737d1fec5121453c`)
has 333 fitted components and passes the outline, coarse corridor-capacity and
courtyard/body screens. It has **54 failures out of 62** P-ADJ checks and
**268 failures out of 353** P-ADJ-PAIR checks. These numerators count failures,
not passes. All 415 proximity endpoints resolve. This is an unaccepted
placement candidate; the zero-floor pad-overlap screen does not establish
fabrication clearance.

The first receive-channel-1 satellite pilot was rejected: it cleared both
ADC1 common-mode attachment failures, but retained 22 channel pair failures
and worsened the global proximity results. This led to a bounded coupled
AFE/isolator/passive experiment, with every unrelated component frozen.
Neither pilot is a routed-block proof. P3 local copper, P4 combined witnesses,
P5 independent placement review and full-board routing remain unexecuted.

The trial also exposed an execution error: an early report recorder produced
27 successful delivery records without doing the corresponding engineering
work. Those records are preserved in the trial's
`06_build/modular/excluded-status-report-attempts.json` and excluded from its
active observation index. They earn no child-work credit. The recorder now
refuses P3-P5 and fails on red P2 measurements. The reusable workflow explicitly
keeps engineering-failed dependencies undispatched even when delivery of their
failure report succeeds. The coverage helper remains a delivery/identity
checker, not a physical acceptance authority.

A coordinator diagnostic restored only the selected scalar model bindings and
regenerated the coarse candidate in a separate directory. Native comparison
found zero changes to component poses or pad positions/net identities. The
owning MODEL-COVERAGE gate passed 333/333 at the correct project depth. This
proves model-file resolution, not registration, mating or placement acceptance.
Diagnostic evidence is in the campaign's `model-binding-diagnostic/` directory;
the active trial was not changed during the coupled writer's attempt.

## Bounded coupled repair closeout

Sol completed two additional CH1 experiments after the first rejected pilot.
The final collision-free candidate has 54/62 global P-ADJ failures and 269/353
global pair failures; its channel-specific failures are 2 and 23 respectively
(previous coarse candidate: 2 and 22). Independent native reopening confirmed
all 306 surrounding fitted components plus four mounting holes stayed fixed
and every pin/net identity remained unchanged. The local attempt cap is
reached. The documented P1/P4 backtrack joins U_ADC, C_FILT1_1U and C_ADC_CM1P/N
at the ADC north bank with the still-unsolved receive-chain placement. This
is evidence for changing the work scope, not proof of infeasibility.

The coupled runtime receipt is INCOMPLETE: a temporary log escaped the admitted
writer directory. The coordinator preserved that finding and independently
reopened the useful native evidence; no delivery or placement PASS is granted.

After runtime closure, the model bindings were restored in the active trial
and its coarse board regenerated. The owning MODEL-COVERAGE gate passed
333/333 and native comparison found zero pose/pad changes across 337 footprints.
Its new SHA-256 is `7554e172335ec4179e4f3bd77666f5808ef79f69da340cd004be59ff3086fcfd`.
The coupled candidate remains unpromoted. Old receipts retain their exact old
subjects. The trial HANDOFF.md records the current state and evidence paths.

Implementation validation: modular 10/10, preparation 6/6, schema-reader 28/28,
progressive-disclosure 14/14 and PCB-documentation 15/15. These software checks
do not substitute for the uncompleted physical/routing trial.
