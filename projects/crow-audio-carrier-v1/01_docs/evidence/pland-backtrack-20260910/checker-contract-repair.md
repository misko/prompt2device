# Five inherited checker-contract failures repaired

MEASURED baseline: root reproduced five obligations and all95 gate rows on the
exact262-file HEAD18c96c58-era tool/test cohort (the direct comparison used
5c89d76b, whose generic source was unchanged). Baseline output and source hashes
are preserved in native-kernel-attempt archive da81f0f7. The audit was correct:
three tools lacked CLI coverage denominators; two suites used assertions the
explicit G-RED invocation contract did not recognize. Their prior bad-input
library/CLI assertions are retained; no claim that these gates lacked ALL tests.

CHANGED: scaffold output now states the complete written file population;
report audit names its one-report denominator. Enclosure layout counts all
tracked project paths, names unscoped root entries, prints its denominator on
success and findings, and returns INCOMPLETE/rc2 over an empty population.
A maintained PCBA CLI case accepts two exact stock rows, then rejects one
insufficient row with actualrc1 and coverage1passing/2graded/2total. Enclosure
coverage likewise uses the actual CLI and an added tracked misplaced mesh.
Gate-contract auditor, skip list, regexes, thresholds and vacuity floor unchanged.

MEASURED behavioral RED before source edits: scaffold lacked44/44 count;
report lacked1/1; enclosure lacked4/4 and falsely passed an empty index.
All four new coverage assertions failed for those exact reasons. The PCBA CLI
clean/bad control already passed unchanged production code, as expected for
making existing behavior visible to G-RED. Its failure was the audit's missing
recognized CLI fixture, not a newly claimed stock-verdict bug.

MEASURED final same tests and full relevant suites:
- t1_pcb_commission:8/8 PASS,4 known-bad,1.467311s.
- t1_project_reports:6/6 PASS,3 known-bad,0.364192s.
- t1_enclosure_layout:11/11 PASS,7 known-bad,0.915200s.
- t1_pcba_availability:45/45 PASS,32 known-bad,0.414442s.
- t1_gate_contract:37/37 PASS,24 known-bad,1 declared blind spot reproduced,
  1 default slow test skipped;6.578949s. The existing audit itself now passes.
- t1_contracts:17/17 PASS,13 known-bad,5.026799s.
All ten wrapper processes reaped; actual argv/start/end/PID/rc/duration and full
stdout are retained. Normal test harness semantics were used; no native oracle
run is claimed from these generic checker tests.

MEASURED archive 9cb9fc1cc99958bb2b2a8c4e3a4c9e031d51148ec1bd55a2639480e2dccd3bf8,
55 regular members, 161261 archive bytes; every member reopened
against checker-contract-repair-manifest.json. It contains exact before/after
source/tests/contracts and every RED/GREEN log/receipt. Root is sole live writer.
No board, old escape checker, native model, rule, checkpoint or release changed.
Generic tool source changes keep the already-stale canonical checkpoint stale;
normal full regeneration remains mandatory. This closes these five generic
checker obligations only, with no kernel/P-LAND/placement acceptance implied.

## Final evidence boundary

MEASURED structure suite17/17 passed again after staging the new archive/contract entries.

```json
{
  "argv": [
    "/usr/bin/python3",
    "tests/t1_contracts.py"
  ],
  "cwd": "/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901",
  "start": "2026-09-10T23:22:55.476944+00:00",
  "timeout_seconds": 120,
  "rc": 0,
  "timed_out": false,
  "duration_seconds": 4.227131181163713,
  "end": "2026-09-10T23:22:59.704192+00:00",
  "pid": 2343740
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
    "Five generic checker obligations fixed: affected70/70, gate-contract37/37, structure17/17 PASS. Fresh kernel contract judgment verified672 inputs, deadline23:48:49Z. Native kernel unadopted; old public P-LAND and strict canonical restart still owed."
  ],
  "cwd": "/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901",
  "start": "2026-09-10T23:22:59.705026+00:00",
  "timeout_seconds": 60,
  "rc": 0,
  "timed_out": false,
  "duration_seconds": 1.0687176277861,
  "end": "2026-09-10T23:23:00.774141+00:00",
  "pid": 2344083
}
```

```text
handoff -> /home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/agent_handoff.yaml (5648 bytes, stage placement)
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
  "start": "2026-09-10T23:23:00.774350+00:00",
  "timeout_seconds": 60,
  "rc": 0,
  "timed_out": false,
  "duration_seconds": 1.1176981530152261,
  "end": "2026-09-10T23:23:01.892121+00:00",
  "pid": 2344102
}
```

```text
handoff valid: /home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/agent_handoff.yaml (stage placement)
```
