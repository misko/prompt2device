# contract: skills/kicad-pcb/scripts/

**Purpose** — the shared executable backend and checkers. A board carries
CONFIG, not code: anything a specific board needs beyond these scripts is a
BACKEND GAP to report, not a bespoke script to write here.

## Allowed

| Pattern | What |
|---|---|
| `*.py` | generators, checkers, converters — run with `/usr/bin/python3` (pcbnew) |
| `*.sh` | drivers (e.g. `tsx_to_board.sh`) |
| `*.mjs` | narrow Node-based artifact renderers invoked by the canonical drivers |
| `tests/**` | narrow checker-local regression tests retained beside their implementation |
| `contracts.md` | this file |

## Audit

- `gate_contract_audit.py` inventories executable verdict gates. The imported
  `native_representation.py` authority validator has no CLI or printed verdict;
  its `jlc_twin.py` and `twin_overlay.py` consumers remain audited. A regression
  checks that boundary and rejects a future CLI/verdict hidden as a library.

- `pcb_flow.py qualify/task-run/task-repair/agent-open/agent-close` compose the
  PCB design runtime's qualification and delivery contracts. Native fixture
  mechanics live in `qualification_probe.py`; its children call the same shared
  `pipeline_runtime.run_stage` seam to retain their full receipts. These commands
  do not admit an engineering stage or replace native/domain reviews.

- Each script's module docstring states purpose + usage; incident references
  cite board NAMES/commits as provenance, never `projects/...` paths
  (contracts_audit C-ISO).
- Checkers: clean + known-bad tests in `tests/` (see tests/README.md — the
  known-bad count is the number that matters).
- Long-running children use `process_runner.run_bounded`: streamed output,
  periodic heartbeat, a declared hard timeout, and whole-process-group
  termination. Performance budgets remain a separate signal.
- Major producer stages bracket outputs with `artifact_provenance.py`; route
  import additionally records the selected `build` or `promoted` lineage.
- Project maturity is derived from `01_docs/findings.yaml` by
  `project_state.py`; an orderable first article is never relabelled tested or
  production-ready by prose.
- Generators emit artifacts that downstream gates re-measure independently
  (canon M1: checker and checked share no method).
- `placement_drc_check.py REPORT.json` is the fail-closed P-DRC boundary after
  a fresh KiCad `--refill-zones --schematic-parity` JSON report and before any
  human placement review. It observes unrouted items, permits only the fixed
  preliminary `isolated_copper` class, and explicitly defers `starved_thermal`
  rows only while unrouted connections remain. It prints each exact deferred
  finding; final routed DRC must regrade all pads with unchanged spoke limits.
  Connected-board thermals, every other violation and parity still block. There is deliberately no caller-supplied violation allowlist.
- `model_coverage_check.py BOARD [-o REPORT.json]` is P-MODEL, the independent
  saved-board gate before modeled placement review. Every fitted, non-DNP,
  non-board-only footprint must carry at least one non-empty model file that
  resolves in the headless renderer environment; renderer exit zero alone is
  never body-coverage evidence.
- `reference_plane_check.py BOARD --config rules/nets.yaml [-o REPORT.json]`
  is the opt-in R-REFPLANE final-board gate. Declared high-speed outer-layer
  tracks are projected onto their named adjacent reference layer; foreign
  tracks and through-vias below the source-owned margins fail even when DRC is
  clean. An absent declaration is explicit N-A; a present empty declaration is
  invalid. It complements rather than claims a field solve or full zone proof.
- `render_board.py BOARD OUTPUT [render options]` is the canonical modeled
  review renderer. It reuses P-MODEL's saved-board resolver and passes every
  referenced model-directory token to `kicad-cli` with `-D`; raw headless
  render commands may silently omit stock bodies when those variables exist
  only in KiCad's user data tree. `--dry-run` emits the exact argv and coverage
  denominator without creating an image.
- Route preparation/import synchronize global fabrication settings only when
  `route.common.fab_overrides` supplies an explicit contract. A bare `fab_tier`
  selects router capability and must preserve source Board Setup floors and
  Default-netclass settings. Explicit synchronization still preserves named
  netclasses, assignments, DRC severities, and the source Board Setup
  hole-to-copper floor; KRT's fabrication-override schema has no independent
  hole-clearance field, so its copper-clearance fallback may not lower that
  separate safety constraint.
- `promoted_route_check.py BOARD ROUTE.yaml` is P-ROUTEBASE: before placement
  review can be credited, route prep must be fresh and an existing explicitly
  selected promoted route must match the exact regenerated base's footprint
  placement, pad/net identity, every source/prepared via's position, geometry
  and IPC-4761 process bits, and every deterministic prepared segment. A
  missing promoted artifact is explicit N-A only for a first route; the route
  importer keeps its independent refusal.
- `via_ampacity_check.py BOARD ROUTE.yaml` is A-VIA: after final board saves and
  before DRC, grade named tight series-transition rectangles against a cited
  finished-hole current table. Fill material receives zero credit. The gate
  explicitly declares that geometric same-net membership cannot prove current
  crosses the boundary, so topology/path review and loaded testing remain
  independent obligations.
- `route_ownership_preflight.py ROUTE.yaml [--root PROJECT]` is the progressive O-* boundary:
  many-pad `pour_or_wide_track` nets must name one topology/owner before KRT,
  deterministic owners cannot also be complete generic waves, and explicitly
  shared corridors put constrained/no-via claimants first. Simple boards are
  N-A; the new-project route template enables enforcement.
  The route driver propagates its resolved project root. Explicit roots admit
  only configurations in that project's `03_src` or `06_build`, reject
  conflicting source ancestry and external boards, and resolve build-copy
  rules from `03_src/rules/nets.yaml`, never adjacent scratch rules. Without
  that unambiguous source rules file, a build config is INCOMPLETE; resolved
  config, board and rule paths cannot escape the explicit root via symlinks.
  Without `--root`, source ancestry remains required; source-local ADR-0007 rules
  retain their existing precedence. Location support grants no diagnostic
  allowance and cannot reset an investigation or replace engineering review.
- `route_candidate_workspace.py grade` is the sole authoritative candidate
  receipt producer. It materializes candidate PCB bytes under a fresh basename
  with exact prepared `.kicad_pro/.kicad_dru`, then runs P-ROUTEBASE, via delta,
  physical DRC and requested connectivity. Candidate sidecars are never rule
  authority; accepted receipts are relocatable and hash-verified.
- `route_progress_guard.py` bounds per-wave exploration by semantic novelty;
  output hashes and raw coordinates cannot reset a plateau. The route driver
  persists the decision beside route progress when opted in.
- `pcb_flow.py run --investigation FINDING_ID` invokes the PCB design owner's
  decision-progress guard before a named local experiment. It cannot bypass an
  engineering gate. Handoffs with adopted investigations include a derived
  compact view plus ledger/evaluator digests; validation reopens both, including
  cited evidence. Handoffs without investigations retain their existing shape.
  A named launch reserves an ID/source-bound ledger slot before dispatch;
  pending assessment blocks another launch and completed assessment does not
  double-count spend. No automatic scientific assessment or finding closure.
- `pcb_flow.py run --issue ID --usage-ledger PATH` composes opt-in accounting
  through `pipeline_issue_ledger.py`; an investigation may supply the issue ID
  and its reserved attempt identity. Initial persistence failure stops launch;
  terminal persistence failure is reported separately and preserves the actual
  command exit. No telemetry field grants engineering acceptance or retry.
- `route_experiment_store.py` gives each retained attempt exactly one terminal
  state and one content-addressed evidence set. The accepted pointer is
  exclusive and pruning is dry-run only.
- **The GATE family (canon G-*) — the checkers are themselves governed
  (ADR-0004).** `gate_contract_audit.py [--root DIR]` walks every
  `skills/*/scripts/*.py` that prints a PASS/FAIL verdict and requires three
  obligations: **G-INPUT** name the artifact graded, so a reader can tell
  shipped bytes from a reconstruction (canon M6); **G-COVER** emit an `N/M`
  coverage denominator; **G-RED** have a `tests/` fixture using `must_fail`.
  A script it cannot parse is **G-PARSE FAIL**, never a skip.
  WHY: `contracts_audit.py` governs FOLDERS and nothing governed the CHECKERS,
  so A-AMP graded **10 of 57** declared net-class currents fleet-wide (any
  qualifier — "7 A worst case", "6 A / 5 A" — makes `parse_amps` return None
  and `rules_audit.py:336` files it under OKS as "n/a (no current: declared)",
  a message wrong 100% of the time since zero classes declare none);
  `bom_source_check.row_kind` dropped `RS1/RS2` and `CE1` while printing PASS;
  and `labeled_resistance("10mOhm")` returned 1.0e7 because the multiplier is
  uppercased, so milli decoded as mega.
  **Its acceptance test is adversarial** and pinned in `t1_gate_contract.py`:
  it must flag `rules_audit.py` and `bom_source_check.py`, the two scripts
  measured silent BEFORE it existed. A gate-on-gates that reports this tree
  clean is decoration and should be deleted rather than trusted.
  `SKIP_BASENAMES` lists generators/libraries that produce rather than grade;
  adding a name there is a coverage decision and must be justified.
- **VACUITY (canon G-VACUOUS), the fourth obligation.** G-RED asks *can this
  gate fail at all* — 31/31 answer yes. G-VACUOUS asks *can it fail ON THE CASE
  IT EXISTS FOR*, and six gates were measured GREEN on 2026-07-28/29 with their
  subject false: `R-LEN` PASSes cooksense on the word `lengthens` in a comment
  about creepage; `keypad_isolation_6mm`'s `B.NetName != ''` exempts the shell
  tab it was written for (**1.0672 mm against a 6.000 mm constraint**, 106
  pairs); A-RENDER's verdict rests on **2 of 203** parts; `waiver_provenance`
  passed a waiver typed `2.62 mm` that measures **3.085 mm**, over the 3 mm it
  claimed; E-OFF is N-A on an undeclared cell; P-FACT prints `OK — 0/0` on a
  malformed assertion.
  **THE DECLARATION IS A FIXTURE, NOT PROSE** — a declared blind spot with no
  fixture is worse than an undeclared one, being the `keep_short` defect (39 of
  181 budgets naming a datasheet pin function) one level up. So: the gate's
  MODULE DOCSTRING carries a `VACUITY:` block AND `tests/` carries
  `@test(..., kind="vacuity", gate="<basename>.py")` constructing that input and
  asserting the gate PASSES. Both homes or neither — prose alone FAILS, an
  orphan fixture FAILS, a fixture whose FIRST assertion is `must_fail` is a
  FALSE declaration and FAILS (a `must_fail` CONTRAST after the subject is
  wanted), a fixture asserting nothing FAILS, and a fixture naming a gate
  outside the inventory FAILS so a rename cannot silently un-declare.
  The block is read from `ast.get_docstring` ONLY: a `VACUITY:` in a comment,
  nested docstring or code string does not count, because crediting text
  anywhere in a file is exactly R-LEN's defect.
  **DRU predicates count.** `--dru BOARD.kicad_dru` grades rule-file conditions
  against the board's own inventory (`dru_inventory`, geometry-free): a
  condition NO object can satisfy — a netclass, net or `insideArea` the board
  lacks — and a `NetName != ''` conjunct on a clearance-family constraint.
  A THIRD species needs geometry (`dru_area_members`, pcbnew): a rule whose
  every name resolves and which STILL matches nothing, because a named rule
  area is not a populated one. That is how a PRESERVED rule dies —
  `generate_rules_generic` used to carry any rule it did not own forward
  forever. It now retires a positively derived zero using `dru_subject`, which
  parses the board as TEXT; this gate must NOT import that module, because a
  checker sharing the emitter's derivation proves nothing about it (canon M1).
  Both matchers read the BARE `(rule X` spelling as well as the quoted one:
  requiring quotes made this gate skip all 6 `pad_rescue_stubs` rules in the
  fleet — the only rule family it was preserved-vs-regenerated for. A
  predicate that excludes its subject is worse than a silent Python gate,
  because it makes DRC itself report zero.
  **THE RATCHET:** coverage is reported for all 31 and every OWED gate is
  printed BY NAME; only a false declaration, a declaration without a fixture,
  and a drop below the committed `VACUITY_FLOOR` FAIL. Adoption is **5/31** as
  of 2026-07-29. Raise `VACUITY_FLOOR` in the SAME commit that adds a
  declaration; `t1_gate_contract.py t_vacuity_floor_is_pinned_to_the_measured
  _count` pins it to the tree from outside and refuses a lowering — that pin is
  what breaks the circularity, since G-VACUOUS itself passes a repo where
  nothing is declared and declares that blind spot in its own docstring.
- **NET REFERENCES (canon E-NETREF).** `net_reference_audit.py PROJECT_DIR`
  (`--root REPO` for the fleet, `--kinds` to print the denominator) grades
  ELEVEN enumerated kinds of net-name reference in hand-authored source —
  `nets.yaml`, `electrical_invariants.yaml`, `power_tree.yaml`,
  `02_parts/*/part.yaml`, `03_src/floorplan.yaml` including net-shaped tokens in
  silk caption PROSE — against the exported `.net`. Each kind carries a NAMED
  CONSUMER, which is the argument that a miss costs something; adding a kind
  without one is not allowed. Verdicts are RESOLVED / GHOST (fails) / UNREACHED
  (reported, does not fail), never a silent skip, and every unresolved name gets
  a near-miss diagnosis with its own counted denominator.
  WHY: cooksense v1.7 measured **10 of 123** referenced net names absent from
  its own netlist and the first fleet sweep **64 of 908** — a `GND_ISO` silk
  caption that reached the shipped F.Silkscreen, an eFuse input-decoupling
  `keep_short` addressed to `5V_SELV` so three real rails carried zero graded
  capacitors, and `supplies: {N3V3: 3.3}` hiding a whole rail from every
  `node_level` grade.
  **The oracle is read by a method the checked side does not share** (canon M1):
  two regexes over the netlist's `(nets ...)` section, NOT
  `electrical_invariants.py`'s s-expression tokenizer and not pcbnew — so this
  audit cannot inherit a parser bug from the gate whose narrow `supplies:` case
  it widens. `supplies:` STAYS owned by `electrical_invariants.py`, which can
  refuse at load time; the overlap on that one field is deliberate.
  **Matching is EXACT.** Only `nets.yaml` `classes.<C>.nets[]` honours `*`/`?`,
  because those become KiCad netclass PATTERNS. Substring matching is the defect
  that let `GND_ISO` pass a human read against `SPI_MISO`, and
  `t1_net_reference.py` pins it: the fixture asserts the gate FAILS *and* that a
  naive containment resolver PASSES the same bytes.
- **REALIZED COPPER LENGTH (canon R-LEN).** `copper_length_audit.py
  PROJECT_DIR` (`--census` for a per-net table on any routed board with no
  declaration needed, `--strict` to make UNREACHED exit 1, `--schema` for the
  authoritative field list, `--root REPO` for the fleet) measures the length of
  the COPPER — track centrelines, arc centrelines as r*theta, via barrel
  z-length — for the `length_match:` groups declared in
  `03_src/rules/nets.yaml`, and grades their spread against a derived DRIFT
  ceiling plus an optional REPRODUCIBILITY `pin:`. `--json` is a strict
  machine-output mode: stdout is one parseable JSON document with no human
  report prefix; omit it for the human-readable report. `--json-output PATH`
  writes that same document directly for release evidence.
  WHY: R-LEN had been `re.search(r"length|spread", audit_src)` over the
  project's `audit_board.py` since the canon was written, so a COMMENT
  satisfied it. Measured 2026-07-29 — smc0985-cooksense PASSED on two remarks
  about a creepage slot being lengthened; pluto-rx2-8way PASSED on comments
  plus a check that grades pad-centre RADIUS; crow-recorder-central-v2 was the
  only honest pass in the fleet (it sums `t.GetLength()` over the USB pair, and
  promoting that bespoke check into this shared one is canon M8's second
  strike); and **pluto-cal-switch — whose release artifact IS a published
  length delta — graded N-A, "no timing-critical nets declared"**, while its own
  `A-SYM` printed *"the D4 delta is a placement property, not a routing
  outcome"* over footprint positions. Phase is a property of COPPER, and the
  router that lays it is stochastic.
  **The judgement is in the tolerance, not the arithmetic:** the requirement is
  that the delta be KNOWN, STABLE and REPRODUCIBLE, never that it be zero. The
  switch's own published insertion-phase window is already 1.00 mm of copper
  part-to-part at 13.19 deg/mm, so a matching target tighter than that is not
  physics; `pin:` grades the FILE, which is exact and free, and is what catches
  a re-route silently invalidating a published picosecond.
  **The board is read WITHOUT pcbnew** (canon M1: pcbnew generated and imported
  this copper), and `t1_copper_length.t_reader_agrees_with_pcbnew` MEASURES the
  independence claim against `PCB_TRACK.GetLength()` — 351 nets across four
  real routed boards, 0 disagreements above 1 um. Member nets are graded where
  they ENTER as `net_reference_audit.py` kind **K12** (canon M-ENTRY).
  **NOT WIRED INTO `policy_audit.py` at landing, deliberately** — see the note
  at the `R-LEN` row there for exactly what is owed.
- **IMPORTED FACTS (canon M-IMPORT / D-MATE, ADR-0005 phase 3).**
  `import_provenance_check.py PROJECT_DIR` (or `--root REPO` for every board)
  grades the PROVENANCE of every fact a board consumes from hardware this repo
  did not design. Input: the board's `03_src/rules/mates.yaml` and the device
  record `external_hardware/<device>/{README.md,facts.yaml}`. Findings: **M-EXIST** (the id
  exists AND its `quote:` appears verbatim in the human record, with the value
  inside it — a machine index drifted from its record is not evidence),
  **M-GRADE** (MEASURED/CITED/ESTIMATED/OWED; absent or unknown is a FAIL,
  never a skip), **M-BAR** (ESTIMATED + `use: dimensional` needs a PARSEABLE
  error bar), **M-PROXY** (the grade must match the METHOD — a number off a
  rendered plot is not MEASURED however reproducibly it was extracted; the
  keyword list deliberately excludes "derived", because subtracting two caliper
  readings is still a measurement), **M-OWED** (a fact nobody has may not be
  spent dimensionally, and must state how to obtain it), **M-RESTATE** (a board
  that writes a value has made a second home for it), **D-MATE** (every
  consumption names its site; a BRIEF declaring a Mating fact-lock must have
  the yaml). WHY: every other gate here compares OUR artifacts to OUR
  artifacts. pluto-cal-switch's PlutoPlus SMA span came off an undimensioned
  vector assembly plot at 35.60 mm — three independent extractions agreeing to
  0.003 mm — and a caliper on two physical units read 35.04 and 34.72 mm,
  10-18x the ±0.05 mm mating window. No gate could see it, because the number
  never came from an artifact any gate reads.
  **It says NOTHING TO GRADE, not PASS, when no board declares a mates.yaml**
  — most boards mate to nothing foreign, and a gate that cried wolf on all of
  them would train readers to ignore red; but an empty denominator may never
  read as a pass (M-COVER). Known-bads in `t1_import_provenance.py`, headed by
  the PlutoPlus record AS IT STOOD BEFORE THE CALIPER.
  DECLARED SCOPE LIMIT: it grades PROVENANCE, not correctness, and it is NOT a
  mating-feasibility checker (error bar vs mating budget). That has been run
  once, by hand, on one interface; canon M8 promotes on the SECOND board
  needing it.
- **PUBLISHED BOUNDS (canon M-BOUND, the ADR analogue of M4's `evidence:`).**
  `adr_bound_provenance.py ROOT [--adr NAME] [--no-regen] [--strict-owed]`
  grades every inequality bound an ADR publishes. Input: `docs/decisions/` plus
  every `*/01_docs/decisions/[0-9]*.md`; a bound is DECLARED by a line reading
  `<!-- bound -->` followed by a fenced `yaml` block carrying `{id, claim,
  relation, value, unit, corner, command, governs{evaluate, budget, unit},
  standard_value{series, series_why}, chosen, tolerance, tolerance_why, grade,
  requires, why_not_rerunnable, corner_commands}`. `command` is re-run from the
  repo root and diffed against `value`; `governs.evaluate` carries a `{value}`
  placeholder and is run TWICE MORE, and those two runs are the whole gate.
  Findings: **B-REGEN** (the command disagrees beyond `tolerance`), **B-FLIP**
  (the value the ADR says it CHOSE satisfies the published bound and not the
  regenerated one — a REVERSED VERDICT, separate from B-REGEN and excused by no
  tolerance), **B-CORNER** (the bound, nudged inward by its own declared
  tolerance, violates its own `governs.budget` — so it was not derived at the
  corner it declares; fails ON THAT ALONE, independent of every other check),
  **B-STDVAL** (the nearest standard value admissible under the bound,
  re-evaluated at the declared corner, violates that budget), **B-SERIES** (the
  series is unnamed, unknown, or unjustified), **B-TOL** (no `tolerance_why`, or
  a tolerance >= the margin to the nearest value the bound must rule on),
  **B-SCHEMA** / **B-GRADE** / **B-CMD** (as M4's, and the denylist is
  `waiver_provenance.MUTATING`, IMPORTED rather than copied — one dialect).
  Ladder and ratchet are M4's verbatim: CITED -> UNVERIFIED -> ESTIMATED ->
  OWED, `CITED_FLOOR` and `OWED_CEILING`, coverage reported and every OWED
  document named.
  WHY: smc0985-cooksense ADR-0024 published `R_pd <= 592 Ohm` as the one-line
  takeaway of a document whose entire argument is worst-case. **592 is the
  NOMINAL corner**; the worst-case bound is **559.283 Ohm**; and **560 Ohm, the
  nearest E24 value under 592, gives 0.700712 V against a 0.700 V budget and
  FAILS by 0.7 mV.** The published bound permitted exactly one standard value
  and that value does not clear — the failure the ADR is NAMED after, reproduced
  in its own summary line. The chosen 470 Ohm was unaffected, so no gate could
  have found it from the board: **A BOUND IS NOT A NUMBER, IT IS A NUMBER PLUS
  THE SET OF PARTS YOU CAN ACTUALLY BUY.** The series is DECLARED PER BOUND and
  never assumed, because it changes the verdict (E24 admits 560 under 592, E96
  admits 590, a stocked-set declaration may admit only 470) — a safety
  pull-down and a decoupling cap are not sourced from the same supply chain, and
  one global default standing in for two is the "the generator was two
  generators all along" defect (0.9375 mm board silk vs 0.75 mm refdes, same
  day) one level up.
  AND IT IS FOUR DOCUMENTS, NOT ONE (canon M-WIDTH — name the class, enumerate
  the members). Re-deriving all 108 published bounds found: cooksense ADR-0024
  (above, corrected since); **cooksense ADR-0018:213, `V <= 1.0 V => R >= 1 564
  Ohm`, STILL PUBLISHED** — in a section headed verbatim "WORST CASE, INJECTED
  PULL-UP" whose own column header reads `3.3 · 680/(680+R)`, while the board's
  `power_tree.yaml` declares 3V3 `vout_max: 3.399` and the ADR takes 3.201 V for
  the opposite direction forty lines earlier; the true bound is **1 631.3 Ohm**,
  and the published one admits E24 1.60 k (1.0137 V), E96 1.58 k (1.0227 V) and
  E96 1.62 k (1.0049 V), NOT ONE OF WHICH CLEARS. usb-hub-3s-v3 ADR-0003's
  `PASS <= 300 uA`, which that board's `power_tree.yaml` retired in writing
  ("the old `<= 300 uA` WOULD HAVE FAILED A GOOD BOARD") — a gate that cannot
  PASS, published as a bound. crow-recorder-central-v2 ADR-0007's `~1.1 A hold`
  F_BEEP PTC, naming MINISMDC110F against six pods firing together at 0.900 A
  where this repo's own x0.8-at-50 C derating puts that part at 0.880 A — 560 Ohm
  in a different unit.
  MEASURED 2026-07-29: **37 of 72 ADRs publish an inequality bound, 108 bounds
  in all, 0 declare a block** — so the gate is a NAMED DEBT under `OWED_CEILING
  = 37` and reds nothing today; the next ADR publishing a typed bound must
  declare it or raise the ceiling in the same commit. Known-bads in
  `t1_adr_bounds.py`, headed by ADR-0024's real 592 Ohm bound (caught twice) and
  red-verified by ABLATION: with B-CORNER and B-STDVAL excised the same bytes
  PASS, because a `command:` solving at the nominal corner regenerates 592.3077
  and AGREES with the typed 592.3 — the M4-shaped half of the gate is satisfied
  by the defect.
  DECLARED SCOPE LIMIT: it catches a MISLABELLED corner, not a badly CHOSEN one.
  An ADR that says `corner: nominal` and does nominal arithmetic is internally
  consistent and passes, even when the document's argument is worst-case; and
  `governs.evaluate` is the ADR author's arithmetic, so an evaluator wrong in
  the same direction as the bound agrees with it (canon M1 — the gate owns the
  ladder, the E-series and the relation, never the physics). The `VACUITY:`
  block and its bound fixture are OWED: promoting them requires
  `gate_contract_audit.VACUITY_FLOOR` 5 -> 6.
- **THE LIVE BEACON (canon M9 / M-BEACON).** `pcb_status.py` READS the beacon;
  `status_beacon_check.py [PROJECT ...] [--root REPO]` grades it against the
  TREE — the two are deliberately separate scripts, because a reader that
  validated its own input would prove nothing (canon M1). Four findings:
  **M-BEACON-DUP** (a field appears twice — an APPEND into a file the 01_docs
  contract says is OVERWRITTEN, which the reader's last-wins rule renders as a
  frame nobody wrote), **M-BEACON-FIELD** (a missing field; the one that makes
  AGE unevaluable, and unevaluable is a FAIL — M-COVER), **M-BEACON-REL** (a
  completed-seal claim must name the LIVE release), **M-BEACON-AGE**
  (`updated:` may not predate that board's newest seal). Release identity and
  ordering are IMPORTED from `jlcpcb-fab/scripts/release_index.py`, never
  re-derived (M-WIDTH). WHY: M9 made the beacon mandatory and nothing made it
  TRUE — measured 2026-07-27, EVERY beacon in the fleet named the wrong
  release, 13 findings across 4 of 6 boards. Known-bads in `t1_status.py` are
  the REAL drifted files (`tests/fixtures/beacons/`), not synthetic ones,
  including the mtime ADJACENT-PROPERTY red-verify.
  DECLARED SCOPE LIMIT: whether a project OWES a beacon is a LIFECYCLE question
  it does not answer — it grades the beacons that EXIST and prints the projects
  with none BY NAME, so the gap is visible rather than silent.
- **THE REGRADE — the only control for defects that BECOME wrong (ADR-0004).**
  `fleet_regrade.py [--root DIR] [--project NAME]` runs today's standalone
  gates against EVERY sealed release and answers two questions: does it still
  pass, and **which of today's gates NEVER GRADED it**. The second is the one
  that was missing — a gate ID that exists today and appears in NONE of a
  release's shipped verification artifacts never graded it, and an absent
  verdict is not a pass.
  **RUN IT WHENEVER A GATE LANDS.** Shifting left cannot reach this class:
  interposer v1.0 sealed 2026-07-24 with `J_KEY_MATRIX` at CPL 90.0 from
  name-DB rule `^JST_GH_SM,180`, which was REFUTED on 2026-07-25 — the day
  AFTER. It was correct by the knowledge of its day and became a P0 overnight,
  silently, because the pad array is symmetric about its own centre. Its
  `policy_audit.md` carries NO A-POP/A-POS/A-ROT/A-POL/A-BODY/A-STOCK row at
  all, sealed during the days that family was landing and never re-graded.
  It reports its own coverage and names every gate it could not run; a FAIL on
  a release carrying `SUPERSEDED.md` is marked as history, so the live defects
  are not buried under superseded siblings.
  KNOWN GAP IT REPORTS RATHER THAN HIDES: a board superseded by a SUCCESSOR
  PROJECT (crow-mic-pod -> crow-mic-pod-v2) carries no `SUPERSEDED.md`, because
  that file names a successor directory inside the same `07_releases/`. Those
  read as live and are not. The supersede convention has no cross-project form;
  special-casing it inside the tool would hide a real gap in the contract.
  **First run, 2026-07-27: 26 releases regraded, 8 live, 5 live failures, and
  every live release never graded by FAB-PAYLOAD or RENDER** — both landed that
  day, which is the mechanism working, not a defect.

- **SCHEMATIC OCCLUSION IS GEOMETRY, AND A DIRECTION IS TWO FACTS (canon S11).**
  `sch_occlusion.py SHEET.kicad_sch [--max N] [--verbose] [--json OUT]` places
  every glyph a `.kicad_sch` draws — global-label plates by their REACH, symbol
  bodies / pin lines / ground glyphs by the instance ROTATION — and reports a
  finding wherever TEXT lands on another drawn object. `policy_audit.py` imports
  it for the S-OCCL row; the ceiling `soccl_max` is 0 and no board overrides it.
  Reference/Value rows must clear their own pin/glyph conductors as well as
  foreign conductors. The own-body convention does not exempt pin shafts;
  the direction-scoped label endpoint attachment rule remains separate.
  The converter's property search applies the same obligation. Its native
  shafts use authored port sides (including up/down facing aliases), with
  coordinate inference only when side metadata is absent. Connection tips
  remain at the authored electrical coordinates. The 2026-09-10 regression
  contrasts eight own-pin crossings with eight clear controls; converter
  fixtures independently measure property ink and body-edge termination in
  KiCad exports. Pin-name/number text remains the declared blind spot below.
  Layout-mode source pages are packed into bounded native columns by rigid
  grid translations, never scaled to disguise an overflow. KiCad 10.0.4
  silently clamps custom exports at 3048 mm; a declared paper dimension is
  therefore not export evidence. The converter rejects an unplaceable source
  page or final modeled extent explicitly, without writing a clipped output
  or falling back to grid mode. Permanent tests measure actual SVG strokes
  (including pin text and frame) and independently exported PDF page sizes,
  contrast an unchanged small drawing, reject excessive width/height, and
  preserve exact node identities and within-page scale. The runtime obstacle
  bound retains its declared pin-text omission; exported-ink verification is
  the independent check on that limitation.
  Authored `capacitor_polarized...` semantics retain a visible positive cross
  beside the source-positive pad in native layout mode. Polarity hints alone
  do not polarize an ordinary capacitor, and ambiguous positive/negative pads
  fail explicitly. Four orientations, swapped positive-pad identity, and a
  nonpolar clear control are checked against actual KiCad drawing strokes.
  The global GND power flag occupies a separate visible grounded wire stub;
  its bounded placement search clears final drawing obstacles by 0.635 mm
  and fails if no clear candidate exists. A grounded-capacitor regression
  rejects the former flag/body intrusion while preserving exact node sets
  and zero error-severity ERC. Grid-mode semantic emission is outside these
  layout-mode repairs; no general readability acceptance follows from them.
  Native component Values prefer an authored manufacturer MPN over purchasing
  codes, while resistor/capacitor engineering values and supplier-only fallback
  remain visible. Layout-mode hidden `Manufacturer Part Number` and JSON
  `Supplier Part Numbers` fields preserve the exact source identity maps;
  footprint/tie lookup still consumes all original sourcing identifiers.
  Authored `schematic_sheet.display_name` captions appear in the native page
  margin and participate in final export bounds. Function and engineering
  annotations belong to that source; the shared converter infers no circuit
  function from a reference or MPN. Permanent tests export actual KiCad glyphs
  and netlists to check identity, passive controls, headings, and connectivity.
  S-OCCL places only plain native free text at 0 degrees, square 1.27 mm font,
  default vertical centering and absent/left/right horizontal justification.
  Actual KiCad 10.0.4 SVG glyphs establish its -0.2500 mm vertical offset from
  property text; other sizes, styles, rotations and unmeasured glyphs remain
  UNPLACED failures. Independent rendered-ink calibration and clear/body/wire
  controls exercise this class without changing the zero-occlusion threshold.
  WHY IT MOVED OUT OF `policy_audit.py`: the model inlined there built every
  plate as `if ang == 180: reach -x else: reach +x`. `justify` — which is what
  selects the SENSE — was read nowhere, the vertical axis did not exist (68 of
  1507 fleet labels sit at 90/270), and there was no symbol geometry of any
  kind. MEASURED 2026-07-31 across the converter fix at `948ef54d`:
  **pluto-rx2-8way-v2 read 4 findings before and 4 after while 3 of the 4 were
  REPLACED**; direction-aware the same two sheets read 88 -> 11 and the
  interposer 58 -> 0.
  **EVERY CONSTANT IS MEASURED FROM `kicad-cli sch export svg` INK** (canon M1 —
  the emitter must not grade its own angles): the `(angle, justify)` table, the
  no-`justify` default, the rotation transform, and the two text metrics. Two
  inherited constants were wrong in OPPOSITE directions and both are now
  measured — a plate's cross extent (2.5408 mm against 2.2, silence) and a
  property text's half-height (0.53x font against 0.9, a 70%-too-tall box that
  INVENTED findings the render refutes).
  **AND THE WIDTH WAS A FIXED-WIDTH MODEL OVER A PROPORTIONAL FONT — the FOURTH
  inherited constant found wrong, 2026-07-31.** `CH_W = 1.05` per character is
  now a measured per-character ADVANCE table: independently derived from 294
  rendered plates (98 characters x 3 name lengths), every advance an exact
  integer TWENTY-FIRST of the font size, k from 8 to 28, residual < 0.0008 mm.
  It was NOT read off `circuit_json_to_kicad_sch.py`'s own table for the same
  font — a checker that inherits the checked module's arithmetic is not a second
  measurement (canon M1) — and the test re-derives the whole table from ink on
  every run so a shared error cannot survive. Against the 1507 real fleet plates
  the flat model is too SHORT on 596 (worst 1.6654 mm), too WIDE on 911 (worst
  1.1173 mm) and **EXACT ON ZERO**; the corrected model matches the box KiCad
  draws to 0.000210 mm on all 1507. The same sweep added the plate base per
  SHAPE (passive 1.3341 / input+output 2.4454 / bidirectional+tri_state 3.5567 mm),
  linear scaling in the font SIZE (both read from the sheet now, and a label
  declaring neither is UNPLACED rather than assumed), the same advance table for
  PROPERTY text (the flat `PROP_W = 0.82` modelled `AVDD_MCU_3V3_RAIL` 1.47 mm
  short) and a per-character vertical INK envelope (a descender reaches
  1.0029 mm below the anchor against a symmetric 0.6731).
  **THE ADVANCE SUM IS NOT AN UPPER BOUND ON INK.** Three glyphs in 98 draw
  outside their own advance cell — `\` by 0.0098 left / 0.2321 right, and `_`,
  the fleet's commonest label character, by 0.1112 right — so `text_pad` carries
  those three measured overhangs and only the first/last character can matter
  (largest overhang 0.2321 mm, smallest advance 0.4838 mm). A character the
  table has never measured makes the object UNPLACED naming the character.
  **THE MODEL IS A CENTRELINE MODEL, and the pen is a NAMED residual**: KiCad
  strokes at a measured 0.1524 mm, so ink reaches 0.0762 mm past every
  centreline on both sides of every comparison. Inflating the boxes instead is
  not available — it would make every label overlap the pin it attaches to by
  exactly the pen width.
  **FALSIFIED IN BOTH DIRECTIONS**: 68 of 68 text-vs-text findings on four
  post-fix sheets confirmed as real ink overlaps, 0 unconfirmed; and the two
  findings the width fix GAINED were confirmed in ink as well (central-v2
  `label USB_VDD33 x pin FB_u33.1`, 0.0943 mm of rendered pin inside the
  rendered plate; cal-switch `label HDR_CTRL_ADC x pin U_MCU.19`, the whole
  1.2700 mm pin line). The converse sweep is the gate's DECLARED VACUITY (pin
  NAME/NUMBER text is not placed — KiCad derives its position from the body
  edge, `pin_names (offset)`, the hide flags and the rotation, and guessing
  would invent findings on every board).
  An object it cannot PLACE is a FAIL naming it, never a pass (M-COVER);
  0 unplaced across all 8 fleet sheets. 11 known-bad + 1 vacuity in
  `tests/t1_occlusion.py`, four axes in two shapes each, with the RED side
  re-extracted from `git show 948ef54d:policy_audit.py` (direction) and
  `git show c90c51c3:sch_occlusion.py` (width) and RUN every run.
  TWO DECLARED SCOPE LIMITS: it grades the `.kicad_sch`, not the
  `pdf/schematic.pdf` a human reads — the premise pluto-rx2-8way-v2's withdrawn
  waiver rested on; and **a green verdict is not evidence that labels point at
  the right pin**, because the converter's de-collision pass run over the
  PRE-FIX direction derivation produces a sheet with zero collisions and every
  plate still naming the wrong pin.

- **RELEASE SELECTION IS SCOPED TO A BOARD, AND IMPORTED, NEVER RE-DERIVED.**
  `policy_audit.py` takes `--board <04_kicad stem>` on a MULTI-BOARD project
  and resolves M-REL / M-BOM / A-POP / A-BODY against **that board's** release
  series via `jlcpcb-fab/scripts/release_index.py` — never `rels[-1]`.
  A release set it cannot attribute is a FAIL that names the directory, never
  a silent pick (canon M-COVER), and every dependent row fails with it rather
  than falling through to `06_build` as though nothing were wrong.
  The report's header line states the board graded and the alternatives.
  WHY: `smc0985-cooksense` builds `cooksense` AND `interposer` and holds both
  series in one `07_releases/`. `interposer-…` sorts LAST, so `rels[-1]`
  resolved to the interposer while `boards[0]` handed the audit the cooksense
  board — four checks graded the wrong archive, and M-REL demanded
  `SUPERSEDED.md` on `cooksense-v1.4`, the LIVE release, blocking a v1.5 seal
  (measured 2026-07-27). `power_topology.py` reads its fuse declaration through
  the same index, newest release first, and NAMES the file and line the number
  came from — it printed `fuse rated 3401 A` off `AO3401A` in a part list.
  Pinned by `tests/t1_release_index.py` and `t1_audit.py`
  (`t_mrel_scopes_to_the_board_under_audit`, red-verified).

- **FINITE NATIVE PAD-LAUNCH WITNESSES (canon P-LAND, M-ENTRY).**
  `escape_check.py --board B.kicad_pcb [--project B.kicad_pro]
  [--dru D.kicad_dru] [--verbose]` delegates to library-only
  `land_witness.py`. All three explicit files must exist; project overrides
  must select the board companion. Entire version-1 rule syntax is admitted
  before grading, including structurally valid diff_pair_gap constraints
  reported outside launch scope. Unsupported syntax, physical constraints,
  assignment/class gaps, geometry, or native configuration mismatch blocks.
  Conditions support exact A/B NetName, NetClass and Type comparisons;
  NetName star/question-mark patterns (brackets literal); negation and native
  OR-before-AND precedence; native insideArea/intersectsArea; exact enabled
  layer scopes. B-dependent widths are rejected before any folding.

  Candidates are real constant-width native Tracks, resolved in original
  rule order independently for width and Track–Pad clearance (both pair
  orders). Native optional PAD/FP local-clearance precedence is preserved;
  explicit custom clearance and width may be below board defaults. Complete
  effective classes and native constituent membership are required. No-net
  sources are excluded but their native Default-class pads remain obstacles.
  Native shapes validate source starts and every relevant other-net pad on
  the layer. Areas ClearArcs then Deflate once by native DRC epsilon with
  ALLOW_ACUTE_CORNERS/ARC_LOW_DEF. Clearance uses native Collide at
  max(0, required-epsilon); raw gap/margin is separate evidence.

  The fixed deterministic policy is sorted positive declared widths <=2 mm;
  bbox centre plus adaptive extent/0.03-mm proposals rounded to at most five
  intervals on each axis (<=37 proposals, 1-IU edge inset); native source
  admission; 48 directions; 1-mm reach; enabled source copper layers. No
  distance pruning is applied. Invariant-only width rejection is recorded.
  `VALIDATED_WITNESS` includes exact start/end/layer/width/rule and limiting
  pair. `NO_VALIDATED_WITNESS` records complete finite coverage, without a
  maximum-width, deficit, impossibility or routing-cause claim.

  Every copper pad belongs to one priority bucket: unreadable, no net,
  no declared floor, nominal same-net pour, native via on land, or graded.
  Physical/copper/noncopper counts reconcile. Nominal pours and vias do not
  prove connectivity. Actual incident same-net track geometry/width/UUIDs are
  inventoried outside the finite search. Unsupported topology, net ties,
  teardrops, non-normal padstacks and hole proxies block; present ordinary
  THT/custom copper shapes remain supported. Drill/physical-hole checks are
  downstream. Zero grading blocks. D-ESC/package/tier behavior is unchanged.

  Maintained `t1_land_witness.py` freezes the native-clean five-pad base
  (same positive public RED/GREEN, 2 graded/5 copper/3 floorless), exact
  hostile UUID pairs, 36 matrix outcomes, ten precedence controls, area and
  exact epsilon thresholds, no-net Default semantics, thirteen immutable ADC
  witnesses and complete hostile native search coverage in bounded batches.
  `t1_escape_tier.py` preserves CAL/RX2/CRC and QSPI contrasts. The helper is
  part of pcb_flow tool identity, verified by a helper-only mutation that
  makes a previously fresh handoff stale. This gate clears no downstream
  source, placement, route, native DRC, connectivity or release gate.

- **OBSERVED GRADING (canon GG-SHADOW / GG-RESOLVE) — M-COVER's observation
  arm.** `trace_audit.py --subject PROJECT_DIR` is the only gate here that
  grades OTHER GATES AT RUNTIME. Everything above proves a checker prints
  `N graded / M total`; this one proves N and M describe the artifact the
  checker was pointed at. It installs `../gradelib/` on `PYTHONPATH`, runs a
  DERIVED battery (a script that takes a project dir, prints a verdict — the
  detector IMPORTED from `gate_contract_audit`, never re-implemented, canon M1
  — and opens no socket) against a `cp -a --reflink=auto` COPY of the subject,
  and emits **GG-SHADOW** (a same-basename file under the root that nothing
  opened) and **GG-RESOLVE** (a path a gate SELECTED — one look at that name —
  that is absent while the basename exists elsewhere).
  **GG-SHADOW's "nothing opened it" IS A FLEET UNION over EVERY TRACE**
  (`opened_union()`), and a tracer writes one trace per PROCESS, so a gate that
  dispatches a worker subprocess per board is graded on its children's reads
  too. `gg_shadow(real=...)` has NO DEFAULT, deliberately: a default would
  restore the per-trace read-set that made the verdict a function of the gate's
  process topology (MEASURED: dispatcher RAW EXIT 1 with 2 false findings vs
  its in-process twin at RAW EXIT 0, same 2-file read-set).
  **`--subject` IS MANDATORY.** There is no repo-level predicate, so a
  subject-less run has nothing to do and exits 2 rather than printing a green
  that says nothing about whether any gate can see its board.
  **IT DOES NOT WRITE INTO THE PROJECT** — traced gates open `*.kicad_prl`
  (every `pcbnew.LoadBoard` does) and `06_build/policy_audit.md` for writing,
  and a grader must not mutate its subject. The sandbox is a REPO
  (`<tmp>/repo/projects/<name>` with every other top-level entry SYMLINKED
  beside it) so a gate resolving a repo-relative path by walking up still
  resolves; symlinks inside the subject are PRESERVED, because a copy that
  dereferenced them would silently repair the defect being reported.
  `--in-place` opts out and says so; MEASURED, the two modes agree exactly.
  **THE READ COUNT IS NOT A PROOF OF OBSERVATION AND MUST NEVER BE QUOTED AS
  ONE.** Neither the write-set (a METHOD test) nor the pre-run snapshot (an
  EXISTENCE test) is an IDENTITY test, so it counts **ANY pre-existing file ANY
  gate happens to open**. A battery gate's own output is the WORST case, not
  the boundary — MEASURED, three lines of prose in `01_docs/BRIEF.md` (nobody's
  output, graded by nothing) lift a genuinely-blind board from exit 3 to exit 0
  exactly as `06_build/policy_audit.md` does, so the OWED identity test closes
  one arm and not the other. The caveat is printed on the same line as
  the number and carried in the `--json` sidecar as
  `read_count_proves_observation: false`. Only the ZERO carries a verdict
  (exit 3). The gate declares this as its `VACUITY:` blind spot and
  `t1_trace_audit.py` reproduces BOTH ARMS on every run.
  Exit codes are a VOCABULARY: **2** invocation · **3** graded nothing · **4**
  unresolved · **5** unobservable — the canary came back silent OR a trace hit
  the `GRADELIB_MAX_EVENTS` cap; never a skip, and a truncated read-set carries
  NO verdict, because "nothing opened this file" is the one claim a PREFIX
  cannot support and truncation therefore manufactures FALSE findings.
  **VERDICT LINES ARE HEADED BY THE EXIT WORD, NEVER BY A CHECK-ID** (`GG NO
  FINDING` / `GG FINDINGS` / `GG GRADED NOTHING` / `GG UNRESOLVED` /
  `GG UNOBSERVABLE`): they used to be headed `GG-TRACE`, a withdrawn family's
  id with no canon row.
  Six withdrawn `GG-*` families have neither a canon row nor an emitter, and
  `t_no_canon_gg_row_lacks_an_emitter` checks both directions — over `Finding`
  ids AND over verdict-line labels, by two independent methods (an AST scan of
  the source and a scan of real run OUTPUT).

## Structure

One file per tool; no package/`__init__.py` — scripts are invoked by path.
`__pycache__/` is gitignored, never committed.

- `critical_path_check.py BOARD --config POLICY --json REPORT` promotes the
  common saved-copper short-path and branch-dominance mechanism to source
  configuration. It grades nonempty denominators and exact layer/stack/endpoint
  identities and rejects unrepresented physical contacts, zones and arcs.
  Its admitted geometry is an endpoint graph of ordinary straight tracks,
  ordinary vias and explicitly supported pad syntax. Full-file S-expression
  parsing normalizes net, layer and direct-position fields into one analysis
  representation before all inherited geometry readers run; equivalent quoted,
  bare, numbered and whitespace variants retain their native meaning. Invalid
  arity, conflicting identities and duplicate geometry fields are refused. The
  shared land_witness tokenizer admits only native/JSON-common metadata escapes
  (quote, backslash and b/f/n/r/t) by explicit opt-in. JSON-only unicode/slash
  and other unsupported escape dialects refuse; native meanings are never
  inferred from JSON-only decoding. Geometry identities and identity-dispatch
  property keys additionally reject escapes in their original token spelling
  and decoded control characters. Its default rule-language parser stays strict.
  This admitted subset follows KiCad DSNLEXER escape semantics documented at
  https://dev-docs.kicad.org/en/components/sexpr/; it is not a claim of support
  for the complete native escape grammar. copper_length_audit
  exposes the same reader for decoded analysis text without changing its file
  API. Original board bytes are never rewritten. A separate serialized object
  census refuses hidden primitives; all copper graphics, unknown pad
  or via modifiers, unsupported intermediate-layer joins and ambiguous pad
  anchors are refused. Rounded graph vertices may merge only physically
  touching endpoint copper, with unchanged pad membership. These refusals
  preserve graph fidelity and are not substitutes for native DRC or clearance.
  Project conductors retain mandatory invocation; component ESD behavior remains
  outside this geometric gate. Known-bad and declared-vacuity fixtures live in
  `t1_critical_path_check.py`.
