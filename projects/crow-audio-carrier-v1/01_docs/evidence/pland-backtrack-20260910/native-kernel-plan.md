# Separate compiled-rule and native candidate kernel boundary

This implements decomposition adopted by fixture-dback-adoption.md, after the
native interface/schema and geometric counterexample in native-complete-classes-adoption.md.
It does not resume either exhausted whole-checker author. Prior histories/caps
remain, and public integration is a distinct later boundary. No new native API
exploration is needed to reproduce the admitted scalar/shape interface.

Scope: add skills/kicad-pcb/scripts/land_witness.py as a reusable library with
no standalone gate verdict and tests/t1_land_witness.py as its hermetic property
and independent native-oracle suite. Add its precise library/test contract home
to scripts/contracts.md and tests/README.md. Do not change escape_check.py,
t1_escape_tier.py, P-LAND policy/public wording or board/source/native files.
The library must expose a clear candidate validation/search interface ready for
later public integration, without circular imports or production /tmp/project
paths. The unchanged launch_points helper may be consumed lazily/injected if
needed, but the actual sample set must remain exactly the existing one.

Implement complete supported AST once, partial-evaluate invariant object attrs,
then evaluate actual candidate Track shape/width/layer for each trial. Finite
declared minimum widths return an actual constant-width witness or blocking
NO_VALIDATED_WITNESS. Never return a maximum, numerical width deficit or proof
of impossibility. Candidate record: source pad ref/num, start/end in native IU,
width, one layer, width rule, limiting other-net pad/rule/gap/required/margin.
48directions/1mmreach/2mmcap/actual adaptive30um set(at most37 simple-poly points).
One pad at a time; other-pad obstacles only; other-net vias/zones and simultaneous
witness interaction remain downstream, explicitly stated in the library doc.

Seven mandatory groups, closed by implemented native-compatible behavior or
NAMED blocking unsupported cases (not warnings/floorless/silent ignoring):
1. Native effective shape per candidate layer and native start containment.
   Unsupported shape/holes/layer semantics must reject with pad identity; no
   polygon approximation in final clearance. Full physical/copper/unreadable
   counts and native object lifetime must be preserved for later integration.
2. Sound obstacle bound includes every board/class/effective/pad/footprint/custom
   clearance. Use real bounding boxes and candidate length/half-width; or avoid
   pruning. GetOwnClearance is a singleton cached rule evaluation, NOT the pair
   oracle. Missing DRC engine returning0 must not quietly weaken the baseline.
3. Reject B-dependent width AST before any partial Boolean fold, even an area
   term hidden behind an A-type false branch. Both A/B orderings for clearance;
   candidate Type is Track, so Pad–Pad relaxations cannot exempt it.
4. Parse all attributes and full relevant constraints, ordered per-constraint
   last-match. Reject unsupported min/max/opt/severity/rule attrs by name; do not
   accept first-min prefixes or silently drop a second relevant constraint.
   Unrelated constraint kinds can be explicitly listed as outside pad-launch
   scope; unknown/malformed forms must not disappear. No missing-width-rule
   vacuous success. Do not claim arbitrary KiCad language support.
5. Exact supported literal/class/wildcard/layer semantics. Compound NetClass
   may be explicitly rejected, including ADC,Default from retained sparse
   fixture; it must not become no-declared-floor. Reject unsupported escaping,
   property comparisons or multilayer Pad.Layer semantics unless independently
   proven. Native area shape collision includes the actual capsule, both sides
   and zone layer; unknown/non-rule-area references must name the unsupported
   condition. Boolean&&/||same-precedence left association, parentheses/negation.
6. Native local-clearance precedence and board minima. KiCad10.0.4 source:
   PAD::GetClearanceOverrides returns explicit pad optional else FP optional;
   nonzero local override wins before custom rules, clamped to board minimum.
   Explicitzero follows a different branch. Custom rules can return before the
   board-minimum fallback. Either implement each with native controls or reject
   conflicting/zero/custom-below-board cases explicitly. Never invent a universal
   clamp by reading the manual alone. The current FID clearances0.6 must enter
   the spatial bound even though class/custom maxima are0.25.
7. Public scope/denominator integration remains owed later. Expose honest,
   structured results and exclusion inventory now. Nominal pour geometry cannot
   certify filled connection; same-net via bucket must preserve actual layers.
   Do not add routed MODEL-REFUTED/maximality claims to this library.

Validation entry: reproduce independent native base0physical/0opens and hostile
exactly2 Track–X1.3/X1.4 clearance findings/0opens, now explicitly using
--all-track-errors on private copies of the exact accepted complete-class
fixture. Retain all actual DRC records, including the prior count failure.
This is the upstream reporting-contract correction and kernel oracle, NOT a
fourth local frozen-interface execution. No need to rerun original producer.
Also test the old sparse classes as a named unsupported control if not supported.
Use exact adopted evaluator18-station native matrix as reference after safe
verified extraction, plus focused controls for the seven guards. Existing native
matrix was36 specified-track outcomes; do not mislabel it public search proof.
Native circle-vs-polygon discrepancy and an outside-start candidate must bite.
Local/FP overrides and below-board constraints require native-backed behavior
or explicit blocking coverage. Unsupported tests must fail the relevant API
for the named reason, not missing API/empty fixture errors.

New-library tests may prove its clean/bad contracts; missing-module RED would
only prove the library did not exist and is NOT the old checker regression.
Do not run/claim the unchanged full escape suite as GREEN for this code. Run
complete new t1_land_witness and relevant t1_contracts/t1_gate_contract once on
final code; keep full child output beyond harness tail truncation. One bounded
standard authoring commission,3consecutive nonimproving implementation iterations,
35minute hard limit with final120seconds for report/audits/handoff. No automatic
extension/replacement. Do not commit; root reads full source/evidence and adopts.

All original483 preimages must be verified before edits, including their
470 frozen inputs. Only the designated author is live writer during this task;
root becomes read-only until handback. No canonical regeneration, live native
DRC/save, geometry/rule/checkpoint/model/route/review/release changes. Unknown
dependencies are reported concretely before widening scope.

## Actual boundary validation

MEASURED contracts17/17PASS13known-bad; native kernel still unimplemented.

```json
{
  "argv": [
    "/usr/bin/python3",
    "tests/t1_contracts.py"
  ],
  "cwd": "/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901",
  "start": "2026-09-10T22:32:20.536014+00:00",
  "timeout_seconds": 120,
  "rc": 0,
  "timed_out": false,
  "duration_seconds": 4.428944421932101,
  "end": "2026-09-10T22:32:24.965053+00:00",
  "pid": 2195076
}
```

```text
  [clean    ] contracts_audit: the real repo (non-projects scope) is clean, and its verdict CARRIES ITS DENOMINATOR ... ok
  [clean    ] contracts_audit passes a well-governed fixture tree ... ok
  [known-bad] contracts_audit FAILS a stray file its contract never permitted ... ok
  [known-bad] contracts_audit FAILS a governed subfolder that lost its contract ... ok
  [known-bad] contracts_audit FAILS a tree with no contracts.md at all ... ok
  [known-bad] contracts_audit FAILS a skill that references a concrete project path ... ok
  [clean    ] contracts_audit does NOT flag the projects/<name> placeholder ... ok
  [clean    ] a project seeded from the skill templates audits clean (template/contract coherence pinned) ... ok
  [known-bad] contracts_audit reads a pattern cell whose pipes are ESCAPED — `*.c\|*.h\|*.rs\|*.py` permits all four, not just the first ... ok
  [known-bad] contracts_audit does not split a pattern cell on a pipe inside a BACKTICK code span either ... ok
  [known-bad] the 05_firmware TEMPLATE permits a header and a src/ tree — the contract and the auditor now agree ... ok
  [known-bad] the 01_docs contract's OWN prompt-hash command reproduces the digest a commission records — and refuses an altered prompt ... ok
  [known-bad] skill<->contract sync: every emitted check-ID is in canon; no contract cites a check-ID that exists nowhere in the skill ... ok
  [known-bad] --projects RAW EXIT CODE IS READ, and the per-unit debt ceiling is TIGHT ... ok
  [known-bad] --present grades PRESENCE for untracked files, because a stray worktree is a governed tree and audits CLEAN ... ok
  [known-bad] a pattern cell listing several backticked patterns SEPARATED BY COMMAS is read as all of them — the pipe bug's twin ... ok
  [known-bad] a DECLARED FIELD WITH NO CONSUMER is a defect — every field in a skills reference yaml is read by something, or its row says how many are not ... ok

  17 passed, 0 failed
  13 of those are KNOWN-BAD fixtures that made their checker fail as required
```

```json
{
  "argv": [
    "/usr/bin/python3",
    "skills/kicad-pcb/scripts/pcb_flow.py",
    "handoff",
    "projects/crow-audio-carrier-v1",
    "--stage",
    "placement",
    "--blocker",
    "Geometric counterexample measured; exact2 hostile count unadmitted because all-track-errors omitted. Three interface attempts closed. Separate compiled-rule/native-kernel authoring must validate both pairs and seven guards; old public checker/tests remain unchanged."
  ],
  "cwd": "/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901",
  "start": "2026-09-10T22:32:24.965282+00:00",
  "timeout_seconds": 60,
  "rc": 0,
  "timed_out": false,
  "duration_seconds": 1.1667817740235478,
  "end": "2026-09-10T22:32:26.132115+00:00",
  "pid": 2195410
}
```

```text
handoff -> /home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/agent_handoff.yaml (5663 bytes, stage placement)
```

```json
{
  "argv": [
    "/usr/bin/python3",
    "skills/kicad-pcb/scripts/pcb_flow.py",
    "validate",
    "projects/crow-audio-carrier-v1"
  ],
  "cwd": "/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901",
  "start": "2026-09-10T22:32:26.132361+00:00",
  "timeout_seconds": 60,
  "rc": 0,
  "timed_out": false,
  "duration_seconds": 1.2680996619164944,
  "end": "2026-09-10T22:32:27.400531+00:00",
  "pid": 2195498
}
```

```text
handoff valid: /home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/agent_handoff.yaml (stage placement)
```
