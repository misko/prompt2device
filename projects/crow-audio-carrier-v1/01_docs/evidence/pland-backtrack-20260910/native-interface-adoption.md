# Failed interface launch: executor owns the output precondition

MEASURED 2026-09-10T21:55:55.121654+00:00: root read the complete initial and corrected reports and exact
command stderr/metadata. Independent final audit found647/647 packet inputs
unchanged and all3 producer scripts exact. PID2087572 absent. All18 regular
members of archive71ba9e0af07ff616a2893bdc744ba98eeefaf33ce53420ee0a85af2646fdfe51
reopened against exact SHA/size; no previous artifact removed or rewritten.
Corrected report SHA0d95282e7572259d5bbe0ed58bd9b3d64a2bb3fa3ceae27797e5d4cdf76e1f08.

MEASURED: the worker bootstrap created the requested output directory with
mkdir(parents=True), then the frozen producer's exclusive directory creation
refused it. Actual single command rc1/0.056826s, start21:51:44.418538Z,
end21:51:44.475375Z. The exception occurred at module initialization before ANY
producer child. No fixture build, native census, public CLI or DRC ran. This
is an executor/output-lifecycle failure, not evidence against the scalar native
interface, the geometry hypothesis or the checker. The one-execution commission
is closed with failure; no retry or replacement was authorized within it.

Administrative corrections: the initial report contained a malformed empty-output
SHA; it is preserved as result.initial.md and corrected in final result.md. The
worker admitted creating the directory before launch. Its output-manifest rows
all rehash, but omitted final result.md and process-cessation.json (besides itself).
Root's complete18-member archive includes them all. Do not call the worker's own
manifest complete. Actual final process audit21:53:48 is later than its manifest.

D-BACK DECISION: move the directory-lifecycle precondition into the producer's
own controller. Keep atomic freshness and all native/CLI assertions. A revised
controller should accept an existing private parent and atomically allocate a
new unique child with tempfile.mkdtemp, then print its actual absolute output
path before running any stage. The operator will no longer create or name the
transaction directory. This closes a cross-owner protocol dependency instead
of allowing an existing output tree, deleting evidence, relaxing assertions or
repeating the failed command. Existing fixture/census scripts must remain exact;
only directory allocation in the frozen execution controller may change.

Before further execution root must freeze and hash the revised controller and
its exact argv/parent semantics. A fresh mechanical handoff may execute that
new source package once with unchanged stage assertions and explicit final
manifest ordering. No mechanical worker may repair code or repeat a command.
All prior author, diagnosis and first-interface attempt histories/caps remain
closed and retained. The separate compiled rule/native kernel and public test
integration boundaries remain uncommissioned and unaccepted.

INHERITED native0physical/514completeconnectiongaps/0parity and accepted schematic
unchanged; source checker/tests and all project native/source/rules/models/routes/
checkpoints/releases unchanged. Original483preimages and stale checkpoints remain.
No electrical progress or release/order acceptance; DO-NOT-ORDER persists.

## Actual administrative validation

MEASURED contracts17/17PASS13known-bad; no native admission.

```json
{
  "argv": [
    "/usr/bin/python3",
    "tests/t1_contracts.py"
  ],
  "cwd": "/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901",
  "start": "2026-09-10T21:55:55.195181+00:00",
  "timeout_seconds": 120,
  "rc": 0,
  "timed_out": false,
  "duration_seconds": 4.978082738118246,
  "end": "2026-09-10T21:56:00.173344+00:00",
  "pid": 2099298
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
    "One native-interface launch failed before child stages because worker precreated output. Original attempt closed. Producer-owned atomic output directory revision and fresh mechanical handoff owed; no source repair acceptance."
  ],
  "cwd": "/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901",
  "start": "2026-09-10T21:56:00.173629+00:00",
  "timeout_seconds": 60,
  "rc": 0,
  "timed_out": false,
  "duration_seconds": 1.1672382920514792,
  "end": "2026-09-10T21:56:01.340978+00:00",
  "pid": 2099539
}
```

```text
handoff -> /home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/agent_handoff.yaml (5622 bytes, stage placement)
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
  "start": "2026-09-10T21:56:01.341282+00:00",
  "timeout_seconds": 60,
  "rc": 0,
  "timed_out": false,
  "duration_seconds": 1.1668055451009423,
  "end": "2026-09-10T21:56:02.508219+00:00",
  "pid": 2099610
}
```

```text
handoff valid: /home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/agent_handoff.yaml (stage placement)
```
