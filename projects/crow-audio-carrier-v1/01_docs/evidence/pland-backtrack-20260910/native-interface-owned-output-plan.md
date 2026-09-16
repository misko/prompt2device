# Producer-owned fresh output directory

Root source decision98f95b84 reopens directory lifecycle ownership after the
operator precreated a path required to be absent. Original command/outputs and
one-attempt cap remain closed; no old output is removed and no old command is
retried. Revised exact package08251554658e563c958f1be34e468c1b3658a87f901c15aeb3b252ffbb8402d4 contains3scripts bound by
native-interface-owned-output-manifest.json. UNEXECUTED at package preparation.

Only execution-controller directory allocation changes. fixture.py and census.py
remain byte-exact, and the complete stage code and all assertions are unchanged.
The argument is now an EXISTING PRIVATE PARENT; tempfile.mkdtemp atomically creates
a unique child and OUTPUT_DIRECTORY prints its actual absolute path. This
retains fresh-output isolation without cross-owner absent-path coordination.

```diff
--- original/execute.py
+++ owned-output/execute.py
@@ -1,11 +1,13 @@
 """One frozen native-interface admission run. No repair/retry branches."""
 from pathlib import Path
 from datetime import datetime, timezone
-import collections, hashlib, json, os, re, signal, subprocess, sys, time
+import collections, hashlib, json, os, re, signal, subprocess, sys, time, tempfile
 SOURCE = Path(__file__).parent
 REPO = Path(sys.argv[1]).resolve()
-OUT = Path(sys.argv[2]).resolve()
-OUT.mkdir(parents=True, exist_ok=False)
+OUT_PARENT = Path(sys.argv[2]).resolve()
+assert OUT_PARENT.is_dir(), 'existing private output parent required'
+OUT = Path(tempfile.mkdtemp(prefix='native-interface-run-', dir=OUT_PARENT))
+print(json.dumps({'OUTPUT_DIRECTORY': str(OUT)}), flush=True)
 CHECKER = REPO/'skills/kicad-pcb/scripts/escape_check.py'
 EXPECTED_SHA = 'cb0d0cf6cb593b5f231fa372920e7dc6adf10bce95c0d734fac0900d3fd3ddf3'
 def sha(q):
```

Exact command for a fresh mechanical worker:
`/usr/bin/python3 EXTRACTED/execute.py REPOSITORY EXISTING_PRIVATE_PARENT`.
One execution, outer420s/child60s/task10min withfinal60sclosure. No worker edits,
repair, alternative APIs, retries or replacement. Rehash allpacket inputs and
all3source members before safe private extraction. Preserve every actual output
and original failure; stop first failed assertion with no invented admission.
The final report must identify OUTPUT_DIRECTORY from actual captured stdout,
retain complete native categories and 0/0/not-invoked parity distinctions, and
write process/input audits and report BEFORE its output-manifest inventory.
A complete manifest lists all files except itself; root verifies every row.

Unchanged native-interface admission:4native reloaded boards each5copper /
2declared-floor /3floorless and exact classes; old publicCLI named X1.1floor0.2
fails on0.12sampledwidth inbothcases at nonzero denominator; nativebase0physical/
0opens andnativehostile2trackclearance/0opens. NoSCH/parityinvocation. These remain
predictions until executed. Passing this diagnostic does not install maintained
RED/GREEN or accept the separate compiled-rule and public integration boundaries.
All previous author/diagnosis/interface caps/history and project release/physical/
order holds remain. No live source/checker/tests/native/model/checkpoint changes.

## Actual administrative validation

MEASURED contracts17/17PASS13known-bad; producer still unexecuted.

```json
{
  "argv": [
    "/usr/bin/python3",
    "tests/t1_contracts.py"
  ],
  "cwd": "/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901",
  "start": "2026-09-10T21:57:32.444775+00:00",
  "timeout_seconds": 120,
  "rc": 0,
  "timed_out": false,
  "duration_seconds": 4.224272184073925,
  "end": "2026-09-10T21:57:36.669123+00:00",
  "pid": 2103548
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
    "Revised frozen controller owns atomic fresh output child; native fixture and assertions unchanged. One fresh mechanical admission owed. No maintained method repair or native placement acceptance; all prior failures/caps retained."
  ],
  "cwd": "/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901",
  "start": "2026-09-10T21:57:36.669289+00:00",
  "timeout_seconds": 60,
  "rc": 0,
  "timed_out": false,
  "duration_seconds": 1.1166281749028713,
  "end": "2026-09-10T21:57:37.785963+00:00",
  "pid": 2103805
}
```

```text
handoff -> /home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/agent_handoff.yaml (5626 bytes, stage placement)
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
  "start": "2026-09-10T21:57:37.786663+00:00",
  "timeout_seconds": 60,
  "rc": 0,
  "timed_out": false,
  "duration_seconds": 1.1177270049229264,
  "end": "2026-09-10T21:57:38.904738+00:00",
  "pid": 2103850
}
```

```text
handoff valid: /home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/agent_handoff.yaml (stage placement)
```
