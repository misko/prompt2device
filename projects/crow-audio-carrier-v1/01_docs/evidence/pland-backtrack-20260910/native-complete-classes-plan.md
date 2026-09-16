# Complete native version4 fixture classes

UNEXECUTED source decision after native-owned-output-adoption.md. Package
3aa78234c2007b00d366a4af041ae7725bb0379682f07dd1d186d62703abe6b9 contains exactly3 scripts bound by native-complete-classes-manifest.json.
Only fixture class dictionaries change to the already exercised generator schema;
execute.py and census.py are byte-exact. The old checker/test and all project
source/native data remain unchanged. No new API or weakened assertion.

```diff
--- sparse/fixture.py
+++ complete/fixture.py
@@ -84,7 +84,13 @@
     pcbnew.SaveBoard(str(oracle), b)
     pro = {'board': {'design_settings': {'rules': {'min_clearance': .1, 'min_track_width': .1}, 'drc_exclusions': []}},
            'net_settings': {'meta': {'version': 4}, 'classes': [{'name': k, 'clearance': c, 'track_width': .2,
-                                        'via_diameter': .6, 'via_drill': .3}
+                                        'via_diameter': .6, 'via_drill': .3,
+                                        'microvia_diameter': .3, 'microvia_drill': .2,
+                                        'diff_pair_gap': .25, 'diff_pair_width': .2,
+                                        'diff_pair_via_gap': .25, 'wire_width': 6,
+                                        'bus_width': 12, 'line_style': 0,
+                                        'pcb_color': 'rgba(0, 0, 0, 0.000)',
+                                        'schematic_color': 'rgba(0, 0, 0, 0.000)'}
                                        for k, c in [('Default', .1), ('ADC', .1), ('Low', .1), ('High', .25)]],
                             'netclass_patterns': patterns},
            'meta': {'version': 1}}
```

Prediction: each of4 reloaded boards has5 copper/2 declared-floor/3 floorless,
plainADC/Low/High class names, F.Cu only,0 unreadable/vias/pours and public0/oracle1
tracks. Unchanged old public CLI must fail X1.1 at floor0.2 and landable0.12,
using0.25 clearance. Native base must have0 physical/0 opens; hostile exactly
2 track-clearance violations/0 opens. No schematic exists; parity not invoked.
Any mismatch rejects admission and preserves complete logs. The sparse compound
case remains evidence of an additional production class-matching defect.

Exact command: `/usr/bin/python3 EXTRACTED/execute.py REPOSITORY EXISTING_PRIVATE_PARENT`.
The producer creates its own unique child and prints OUTPUT_DIRECTORY. Fresh
mechanical worker verifies packet and archive before execution; no script edits,
retry, replacement, alternative APIs or extra scans. One execution,420s outer,
60s each child,10minute task/final60second closure. Stop first failed stage.
Write full actual argv/start/PID/rc/duration/stdout/stderr and every output. Write
report and process/input audits before final output manifest, listing all regular
files except itself, then stop all processes/writes. This is the third interface
execution; no fourth same-stage attempt. All preceding caps and histories stand.

Even full diagnostic admission does not install maintained regression or accept
production repair. Next boundaries remain compiled-rule/native-kernel, then
public verdict/denominator/hostile-corpus integration and actual pre-fix RED /
final GREEN/full relevant suites, followed by strict canonical regeneration.
All seven semantic guards and physical/release/order gates remain required.

## Actual administrative validation

MEASURED contracts17/17PASS13known-bad; diagnostic producer still unexecuted.

```json
{
  "argv": [
    "/usr/bin/python3",
    "tests/t1_contracts.py"
  ],
  "cwd": "/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901",
  "start": "2026-09-10T22:25:49.738094+00:00",
  "timeout_seconds": 120,
  "rc": 0,
  "timed_out": false,
  "duration_seconds": 4.9268705600406975,
  "end": "2026-09-10T22:25:54.665087+00:00",
  "pid": 2176188
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
    "Native scalar interface and atomic output accepted; sparse version4 fixture classes caused zero declared floors. Complete-class source frozen for third interface execution. No public/native DRC or maintained RED; all prior caps and release gates retained."
  ],
  "cwd": "/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901",
  "start": "2026-09-10T22:25:54.665277+00:00",
  "timeout_seconds": 60,
  "rc": 0,
  "timed_out": false,
  "duration_seconds": 1.067094039870426,
  "end": "2026-09-10T22:25:55.732421+00:00",
  "pid": 2176564
}
```

```text
handoff -> /home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/agent_handoff.yaml (5652 bytes, stage placement)
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
  "start": "2026-09-10T22:25:55.732573+00:00",
  "timeout_seconds": 60,
  "rc": 0,
  "timed_out": false,
  "duration_seconds": 1.1170567530207336,
  "end": "2026-09-10T22:25:56.849678+00:00",
  "pid": 2176615
}
```

```text
handoff valid: /home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/agent_handoff.yaml (stage placement)
```
