# Completed native judgment retained; delivery gate timed out

MEASURED: root startup qualification PASS4/4; separate fresh live availability
probe delivered its exact13-word challenge and schema2 attempt PASS. These are
runtime/tool availability results, not board acceptance.

The fresh native-semantics reassessment was commissioned once at
2026-09-11T02:16:51.542745Z with a hard deadline02:31:51.501439Z and zero
replacements. The reviewer wrote a complete24,102-byte judgment and1,458,211-byte
evidence record; evidence created_at is02:31:34.464032Z. Root observed all three
outputs at02:31:41Z and subsequently received the real host FINAL_ANSWER.
The exact host-event delivery instant was not independently timestamped.
Root invoked coordinator closure too late: .closing and finished_at are
02:32:01.863005Z and02:32:01.863050Z,10.362 seconds after the deadline.
The immutable TaskAttempt is TIMED_OUT with agent-delivery INCOMPLETE. It did
not execute its later output or writer checks. No backdating, second closure,
receipt replacement, or inference of a passing attempt is permitted.

The coordination failure is root-owned. The reviewer completed substantive
work, but completion prose and filesystem timestamps do not substitute for the
owning delivery gate. The verdict GO in the preserved report is UNADOPTED.
No production authoring, placement continuation or release gate is admitted.

MEASURED independent post-failure preservation: all24 input packet bindings
still match; all12 newly recorded process PIDs are absent;70 inline files in
evidence.json rehash exactly; original public checker/test and four native
board/project/rule/schematic inputs remain unchanged. All483 historical
preimages match both their Git blobs and their copied archive. Eight existing
tool/contract files differ from that historical checkpoint, so full strict
canonical regeneration remains owed after an accepted checker repair.

The new archive retains111 regular members, including every new review scratch
file and both successful startup/availability receipts. Its manifest separately
reopens3485 historical extracted members through three existing durable archives
instead of nesting repeated archive copies. ArchiveSHA:
9ca5188d297ac806316e5955d3053bbf73be949c5a44e445dd14a51607b27160.
Raw completed judgment, failed setup commands, focused native controls and the
additional false-PASS diagnostic with its unrelated native failures are intact.
Observed old-checker defects are not a completed maintained behavioral RED;
no maintained GREEN or kernel source exists.

Process correction prepared for any explicitly admitted replacement: prepare
the coordinator close command before launch; give the reviewer an eight-minute
work/delivery cutoff inside a ten-minute attempt; reserve the last two minutes
for host completion, independent reopen and closure. Interrupt unfinished work
at the earlier cutoff rather than consuming the closing buffer. This changes
future orchestration practice only; it does not repair this terminal attempt.
The original replacement_limit0 remains unchanged. A replacement is not launched
without explicit admission. See native-semantics-replacement-plan.md.

The isolated checkout /tmp/carrier-native-kernel-implementation-20260911 remains
untouched at7d2c5d9d. Root retains sole live writer. All previous exhausted
whole-method/witness/kernel commissions, source-investigation history and
physical/orientation/routing/release/order holds remain unchanged.

## Measured preservation-boundary validation

Contracts17/17 PASS,13known-bad; compact handoff generated and validated.
These validate durable evidence structure, not the timed-out review.

```json
{
  "schema": 1,
  "pid": 2857914,
  "stage_id": "contracts",
  "run_id": "20260911T023742Z-e449b972",
  "status": "PASS",
  "started_at": "2026-09-11T02:37:42.252121Z",
  "finished_at": "2026-09-11T02:37:46.529215Z",
  "elapsed_s": 4.277094,
  "returncode": 0,
  "work_timing": {
    "work_class": "local",
    "started_at": "2026-09-11T02:37:42.252121Z",
    "finished_at": "2026-09-11T02:37:46.529215Z",
    "elapsed_s": 4.277094
  },
  "log_path": "/tmp/carrier-native-timeout-validation-9jj49bzc/contracts.log",
  "output_bytes": 2028,
  "output_lines": 20,
  "console_child_lines": 5,
  "suppressed_child_lines": 15,
  "findings": [],
  "outputs": []
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
  "schema": 1,
  "pid": 2858267,
  "stage_id": "handoff",
  "run_id": "20260911T023746Z-e2972b3a",
  "status": "PASS",
  "started_at": "2026-09-11T02:37:46.529671Z",
  "finished_at": "2026-09-11T02:37:47.590674Z",
  "elapsed_s": 1.061005,
  "returncode": 0,
  "work_timing": {
    "work_class": "local",
    "started_at": "2026-09-11T02:37:46.529671Z",
    "finished_at": "2026-09-11T02:37:47.590674Z",
    "elapsed_s": 1.061005
  },
  "log_path": "/tmp/carrier-native-timeout-validation-9jj49bzc/handoff.log",
  "output_bytes": 168,
  "output_lines": 1,
  "console_child_lines": 1,
  "suppressed_child_lines": 0,
  "findings": [],
  "outputs": []
}
```

```text
handoff -> /home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/agent_handoff.yaml (5621 bytes, stage placement)
```

```json
{
  "schema": 1,
  "pid": 2858294,
  "stage_id": "validate",
  "run_id": "20260911T023747Z-2414eb04",
  "status": "PASS",
  "started_at": "2026-09-11T02:37:47.591172Z",
  "finished_at": "2026-09-11T02:37:48.650604Z",
  "elapsed_s": 1.05943,
  "returncode": 0,
  "work_timing": {
    "work_class": "local",
    "started_at": "2026-09-11T02:37:47.591172Z",
    "finished_at": "2026-09-11T02:37:48.650604Z",
    "elapsed_s": 1.05943
  },
  "log_path": "/tmp/carrier-native-timeout-validation-9jj49bzc/validate.log",
  "output_bytes": 160,
  "output_lines": 1,
  "console_child_lines": 1,
  "suppressed_child_lines": 0,
  "findings": [],
  "outputs": []
}
```

```text
handoff valid: /home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/agent_handoff.yaml (stage placement)
```
