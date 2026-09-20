# Bounded execution runtime

This reference owns how an already-selected PCB pipeline stage is executed. It
does not decide whether the stage applies, whether an engineering artifact
passes, or which artifact is accepted. Those decisions remain with the stage
contract and the owning domain gate.

Runtime policy ID owned here: `M-BOUND`.

## Contents

1. Authority boundary
2. Task envelope and attempt
3. Process-group control and filesystem detection
4. Terminal outcomes and replacement
5. Migration and canaries
6. Validated task delivery
7. Startup qualification
8. Same-owner repair admission
9. Issue-level accounting

## Authority boundary

The runtime receives a reviewed task envelope and direct argv. It may execute,
observe, terminate, and record that attempt. It may not synthesize missing
inputs, retry without an admitted replacement, reinterpret a gate verdict, or
promote a partial artifact.

Keep these axes separate:

- `StageSpec` says what engineering work exists.
- applicability says whether project facts require it.
- `TaskEnvelope` says how one bounded attempt may run.
- the owning gate judges the resulting engineering evidence.
- an artifact transaction chooses whether verified bytes replace an accepted
  bundle.

The current shared runtime is bounded, not hermetic. It does not enforce network
isolation, syscall/read confinement, executable digests, or OS-level writer and
process containment. Do not call a future run hermetic unless those properties
are enforced and recorded. A declaration alone is evidence of intent, not
containment.

## Task envelope and attempt

`pipeline_execution.py` owns closed schema-1/2 `TaskEnvelope` and schema-1 `TaskAttempt`,
`WriterScope`, and `AgentSpan` objects. Generated envelopes live under
`06_build`; they are not authored project policy.

Every executable attempt names:

- task, stage, run, and exact semantic/raw subject identities;
- direct argv, explicit cwd, finite deadline, and execution class;
- a content-addressed input packet checked before and after execution;
- an explicit environment projection rather than an accidental shell session;
- read-only or exclusive writer paths with no traversal;
- one durable attempt output path and the permitted replacement count.

Fresh-context work requires a non-empty input packet. Reviewers are fresh and
read-only. Non-agent work records context as not applicable. Model names never
enter project authority; role escalation above the recommended mechanical,
authoring, or judgment role requires a reason.

`pipeline_runtime.run_stage(...)` is the low-level bounded-process seam, and
`execute_attempt(...)` adds the content-addressed task-envelope contract.
`process_runner.run_bounded(...)` is the compatibility adapter used by the
engineering paths migrated in this robustness slice. Those migrated paths must
not retain a second timeout/process implementation. This is a scoped migration,
not a claim that every legacy subprocess owner in the repository has already
been converted. Within the migrated `pcb_flow.py` path, read-only local Git
provenance probes remain a direct-process exception: each has a 30-second
timeout, performs no network operation or project mutation, and runs before
engineering execution.

Nested bounded execution currently requires Linux `/proc` process metadata.
The outer runtime uses it to discover every child-owned subgroup before killing
the parent. On a host without that metadata, a nested attempt is refused before
launch; it never falls back to an undiscoverable subgroup.

## Process-group control and filesystem detection

The runner must:

1. verify every declared input byte and cwd before launch;
2. use direct argv and an explicit environment;
3. start a new process group, retain every stdout/stderr byte read before any
   bounded transport cutoff, and emit heartbeat;
4. enforce the finite deadline even if the group leader exits while a
   descendant keeps an inherited pipe open;
5. after leader exit and pipe EOF, inspect the original process group; a quiet
   remaining group member is a runtime error, not successful completion;
6. terminate the original process group, then escalate after the grace period;
7. verify inputs again and inventory writer paths after exit;
8. reject detected undeclared changes inside the snapshotted project root or
   changed inputs as `INCOMPLETE`;
9. persist exactly one terminal attempt and release the writer lease in
   `finally`.

Process-group containment is bounded execution, not a sandbox. A hostile child
can create a new session and escape `killpg`; the runner cuts any inherited
output transport after the deadline/grace period and returns a non-passing
result, but cgroup/subreaper containment would be required to guarantee that
such a foreign-session process is itself reaped.

Writer-scope comparison is likewise post-hoc detection, not confinement. It
observes the project-root snapshot; it cannot prevent writes or prove the
absence of writes elsewhere on the host.

Runtime output belongs in a fresh workspace. It cannot update a live board,
accepted pointer, release, or stage result until the owning gate and artifact
transaction reopen and verify it.

Network posture is fail-closed only when the runner actually enforces it. Until
then, `network: forbidden` is a recorded expectation and the attempt must not be
described as network-isolated. The same truth rule applies to tool digests and
read-set tracing.

## Terminal outcomes and replacement

An attempt ends once as `PASS`, `FAIL`, `TIMED_OUT`, `INCOMPLETE`, `ERROR`, or
`HANDOFF_REQUIRED`. Timeout, stale input, undeclared write, missing output,
telemetry loss, or runtime error never becomes PASS. Non-pass terminal states
name unresolved rows and preserve the previous accepted bundle.

Only the coordinator may admit a replacement, and only within the envelope's
limit. A late or superseded attempt remains forensic evidence and cannot update
authority. Token telemetry is optional; missing telemetry is `UNKNOWN`, and
different accounting authorities or metrics are never summed.

For recurring engineering investigations, the coordinator uses the cumulative
decision-progress protocol in `lifecycle-and-backtrack.md`. A TaskEnvelope's
`max_nonimproving_attempts` is an attempt declaration, not by itself persistent
cross-handoff enforcement. Its limit must agree with the finding's investigation
budget. The separate read-only guard and opt-in `pcb_flow.py run --investigation`
launch check do not extend StageSpec, execute domain reviews, or grant admission.
The named launch reserves durable spend before dispatch and refuses another
launch while its outcome lacks an assessment. Failed dispatch is still a
reservation, not fabricated execution telemetry. The evaluator CLI stays read-only.

## Migration and canaries

Adopt the shared runner in three steps:

1. shadow the legacy conductor and compare argv, cwd, input hashes, elapsed
   outcome, process cleanup, writes, and stage result;
2. make the shared runner authoritative while the legacy adapter remains a
   compatibility shim;
3. delete the duplicate implementation after simple, high-speed digital, RF,
   and multi-layer canaries agree.

`pcb_flow.py` intentionally applies a finite 3600-second safety ceiling when a
legacy project declares no `flow.timeouts_s.<stage>` and no
`flow.timeouts_s.default`. This replaces the old effectively-unbounded wait.
Projects with legitimately longer work must declare a stage-specific timeout;
promotion canaries must exercise that declaration rather than silently raising
the fleet-wide fallback.

Known-bad tests must cover descendants with inherited pipes, descendants that
redirect all output, timeout cleanup, stale input, writer-scope escape,
duplicate terminal writes, late replacements, and a missing executable. A
shadow runtime must not change authoritative identity, verdict, pointer, or
median elapsed time beyond the documented migration budget.


## Validated task delivery

Use the opt-in `pcb_flow.py task-run PROJECT --envelope FILE -- COMMAND` for
subprocess work with required outputs. Schema-1 readers remain supported;
new task delivery requires a schema-2 envelope with two additional fields:

- `completion: {outputs: [...], checks: [...]}`: nonempty sorted unique output
  paths and check IDs. Output paths are relative to the allocated output
  directory; `result.json` is reserved and implicit.
- `repair: null`, or a predeclared same-owner allowance described below.

`output_path` names `06_build/task_runs/<run>/attempt.json`. The CLI allocates
a unique run and persists its exact revised envelope. The runtime owns run
creation. The producer gets `PCB_TASK_OUTPUT_DIR` and `PCB_TASK_SCRATCH_DIR`;
create files inside these existing directories. `PCB_TASK_SUBJECT_JSON` carries
the exact subject for result.json. Design edits still require the
envelope's writer scope. The CLI projects PATH/LANG/LC_ALL and the unchanged HOME; API callers may
supply other explicit environment values, which are excluded from the receipt.
Full stdout/stderr share one lossless log, with byte census and digest.

The producer writes every declared output plus `result.json`, exactly:
`{"subject": <envelope subject>, "checks": {"<check ID>": "PASS"}, "unresolved": []}`.
Missing/extra files, malformed files, symlinks, stale subjects, incomplete check
census or unresolved work cannot pass. This checks delivery consistency;
independent engineering judgment and artifact promotion still follow separately.
Failure retains partial files and an explicit terminal attempt. Persist needed
forensic evidence in the project's durable evidence home before clearing build.

For agents, run `agent-open PROJECT --envelope FILE` before dispatch. It returns
the allocated envelope and paths. Launch through the available host agent tool,
delivering this exact envelope. Then run `agent-close PROJECT --envelope ALLOCATED
--host-event EVENT.json`. The coordinator records the observed host event with
exact keys `host`, `agent_id`, `state`, `envelope_sha256`, `cleanup`, `detail`.
`state` is completed/error/running/unknown; `cleanup` is confirmed/unknown.
A completed host state and confirmed cleanup are required in addition to the
handback. Capture the event from host tools, never from the worker's own prose.
The adapter cannot authenticate host testimony or launch reviewers from a shell.
Missing host telemetry remains UNKNOWN; a provider failure or late delivery
closes non-pass. Interrupt through the host if needed; never act on a stale PID.
A durable closure latch prevents late callbacks from replacing a terminal result.


## Startup qualification

Before native work, use `pcb_flow.py qualify PROJECT` (default total deadline
120 seconds; `--python`, `--kicad-cli`, `--timeout-s` select the actual tools).
This runs a project-independent complete-netclass fixture through serialization,
explicit project reload and clean/hostile native DRC. The hostile result must
name the exact two pads; empty or partial native reporting cannot qualify.
Every child uses the bounded runtime and retains its logs and result records.

Successful native evidence is cached below `06_build/cache/`, keyed by actual
executable, imported Python module/shared-library, probe/runtime source and
isolated configuration identities. Changed or missing evidence invalidates it.
Repository contract/authority audits run again independently; an unrelated board
edit does not invalidate an unchanged API probe. Qualification never changes
board geometry or admits a design/release stage.

Live reviewer availability remains separate and uncached. When review is next,
use the agent open/close adapter with a fresh bounded probe packet and one small
required result; launch through the host and observe delivery. A probe's success
shows current launch/delivery availability, not future quota or review quality.
Commission the actual engineering review freshly afterward. Without a successful
live probe, reviewer availability stays UNKNOWN and review admission remains owed;
independent authorized preparation can continue. Native compatibility PASS is
explicitly scoped to tools and repository contracts, not to reviewers.


## Same-owner repair admission

Schema-2 subprocess envelopes may set `repair` to exactly `owner_id`,
`hypothesis_sha256`, `max_attempts`, `setup_remedies`, and `finding_id`.
The positive total cap includes the initial attempt. Setup remedies are a sorted
subset of `wrong_cwd`, `missing_directory`, `missing_executable`, `missing_output`.
`finding_id` is null for ordinary tasks or names the existing recurring
investigation; its cumulative accounting remains independently binding.
Agent/reviewer replacement uses its separate existing admission boundary.

After a failed attempt, run `pcb_flow.py task-repair PROJECT --envelope
ALLOCATED/envelope.json --assessment FILE -- COMMAND`. The coordinator's JSON
assessment has exactly `owner_id`, `hypothesis_sha256`, `classification`
(setup/engineering), `remedy` (an admitted setup token or null for engineering),
`improved` (boolean), `boundary` (existing semantic boundary or null), `d_back`
(boolean), `context_used_pct` (number or null), `reason`, and `evidence` (nonempty
PacketItem mappings with name/path/size/sha256).
PacketItem `name` uses lowercase letters, digits and underscores, starting with
a letter (for example `failed_child_log`); paths use ordinary relative filenames. Reopen the actual evidence before
classifying it; matching hashes cannot judge whether a causal explanation is true.

An initial repair-enabled launch claims its stage, semantic subject and hypothesis
once, independently of task/owner naming; reissuing task-run cannot reset spend.
The command records the assessment in the successor TaskAttempt, preserves the
original deadline and scope, and claims the predecessor once before dispatch.
All executions consume the original total allowance. Setup errors increment the
non-improving count, never earn progress credit, and cannot be retroactively
removed from campaign history. A failed dispatch retains its reservation; it
cannot silently retry. Missing/stale evidence, different owner or hypothesis,
mandatory handoff/context boundary, runtime containment error or exhausted limits
refuse local continuation. A known missing-executable launch failure may use that
specifically pre-admitted remedy. No retries run automatically.

Keep the predecessor attempt/envelope/evidence chain while this task is active;
archive the chain before clearing build scratch. These are the existing attempt
records, not a second findings ledger. The single-writer rule still applies:
claims detect competing successors, but do not make filesystem history tamper-proof.


### Complete construction example

Run this Python from the repository root with an existing scratch project as
its first argument. The scratch project must contain `input.txt`. It writes an
admissible envelope; adjust stage, required checks, input packet and owning
scope for the actual commission. Task/check IDs allow hyphens; packet names
use underscores. The allowance is declared before the initial execution.

<!-- executable-task-example -->
```python
import hashlib, json, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
sys.path.insert(0, "skills/pcb-design/scripts")
from pipeline_execution import TaskEnvelope
from pipeline_identity import TypedIdentityInput, subject_identity
project = Path(sys.argv[1]).resolve()
data = (project / "input.txt").read_bytes()
subject = subject_identity("report", 1, [TypedIdentityInput(
    "input", "mapping", {"text": data.decode()}, data)])
envelope = TaskEnvelope(
    schema=2, task_id="report-1", stage_id="PCB-COMMISSION", run_id="report-1",
    subject=subject, executor="subprocess", execution_class="local",
    recommended_agent_role=None, agent_role=None, role_escalation_reason=None,
    context_mode="NOT_APPLICABLE", input_handoff_id=None,
    input_packet=[{"name": "source", "path": "input.txt", "size": len(data),
                   "sha256": hashlib.sha256(data).hexdigest()}],
    deadline_at=(datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat().replace("+00:00", "Z"),
    max_nonimproving_attempts=3, replacement_limit=0,
    writer_scope={"mode": "READ_ONLY", "paths": []},
    output_path="06_build/task_runs/report-1/attempt.json",
    completion={"outputs": ["report.md"], "checks": ["report-complete"]},
    repair={"owner_id": "report-owner", "hypothesis_sha256": hashlib.sha256(b"summarize input").hexdigest(),
            "max_attempts": 2, "setup_remedies": ["wrong_cwd"], "finding_id": None})
(project / "task-envelope.json").write_text(envelope.to_json() + "\n")
```

Launch with `pcb_flow.py task-run PROJECT --envelope PROJECT/task-envelope.json
-- /usr/bin/python3 producer.py`. The producer reads input.txt, writes report.md
inside `PCB_TASK_OUTPUT_DIR`, and writes the exact-subject result.json described
above. A successful delivery requires the `report-complete` check.

For a real wrong-path failure, the coordinator prepares an assessment like the
following. Replace the hypothesis and evidence binding with the original
allowance and actual retained child log; do not manufacture a setup diagnosis.

```json
{
  "owner_id": "report-owner",
  "hypothesis_sha256": "<original repair hypothesis SHA-256>",
  "classification": "setup", "remedy": "wrong_cwd", "improved": false,
  "boundary": null, "d_back": false, "context_used_pct": null,
  "reason": "The retained traceback names the wrong relative input path; correct it within the original scope.",
  "evidence": [{"name": "failed_child_log", "path": "<project-relative attempt.json.log>",
                "size": 123, "sha256": "<actual log SHA-256>"}]
}
```

Repair with the allocated previous envelope (the envelope.json beside its
attempt.json), not the original template. The command prints the successor path.
The two-execution example allowance leaves no third launch, even if the second
execution fails. No additional agent is needed for this correction.

## Issue-level accounting

`pipeline_issue_ledger.py` is an optional accounting adapter, not a second
findings ledger or admission gate. Reuse a stable finding ID across agents and
retries; `findings.yaml` still owns closure, hypotheses, evidence and attempt
allowances. Use a separate shared-overhead issue for genuinely shared work
instead of inventing fractional token attribution.

The first adopted consumer is the existing bounded command path:

```bash
python3 skills/kicad-pcb/scripts/pcb_flow.py run "$PROJECT" \
  --stage routing --issue ISSUE-17 \
  --usage-ledger "$PROJECT/01_docs/issue_usage.jsonl" -- COMMAND ARG
python3 skills/pcb-design/scripts/pipeline_issue_ledger.py summary \
  --ledger "$PROJECT/01_docs/issue_usage.jsonl" --issue-id ISSUE-17
```

With `--investigation ISSUE-17`, `--usage-ledger` uses that issue and the existing
reserved attempt ID; an explicitly different `--issue` is rejected. Attribution
alone never invokes or replaces investigation admission. Other commands and
unattributed runs retain their existing behavior. Each run prints its stable
IDs. Input provenance stores command, source and tool digests, not command text
or credentials. These hashes describe the observation; they do not independently
prove a command read only those inputs.

The schema/API is owned by the ledger module. `record_start` durably records
intent before launch; `record_run` records terminal execution. A start without
a terminal remains incomplete. Initial accounting failure prevents the opted-in
launch. A terminal accounting failure prints `ISSUE ACCOUNTING INCOMPLETE`,
leaves that start open and preserves the actual command result. This adapter
runs outside runtime event callbacks so an accounting error cannot rewrite a
domain verdict. The compatibility runner exposes only coarse execution statuses;
a runtime cleanup error may be recorded as FAIL with its nonzero exit rather
than a distinct ERROR. A performance-budget failure remains separate from the recorded
child execution result, as in the existing performance log.

For provider observations, append strict event JSON using `append --ledger PATH
--event-json FILE`. Assign a distinct run to each provider response under its
owning attempt, with stable provider/account scope and response ID. Persist
observed usage and cost, including failed requests; never use cumulative status
counters as per-response usage. Duplicate identities are checked; conflicting
attribution is an accounting error. The schema has no prompt or API-key field.
Provider-reported cost is USD; absent cost is unknown, not a Codex subscription
charge estimate. A `PASS` here describes execution only, never a PCB verdict.

Summaries distinguish input, cached input, output and reasoning subsets, retain
unknown/partial coverage and incomparable authority/metric groups, and distinguish
observed interval union from summed worker duration. Neither is human active
labor or complete issue age. Provider wait, operator wait and issue-open/close
intervals are not inferred from gaps between calls. Missing child sessions are
not assumed to have zero usage.

Keep the durable ledger outside disposable `06_build`; the optional project
convention is `01_docs/issue_usage.jsonl` with a local ignored `.lock` sidecar.
Existing projects adopt the template allowance before using that path. Keep
raw session logs private and separate. Offline saved-record ingestion is now
available below. Live host-agent launch integration, automatic descendant-log
discovery and issue-state waiting intervals remain separate work; no complete
capture of all agents is claimed.


### Offline usage-source adapters

The source reader and ledger have separate interfaces:

- `openrouter_usage_adapter.parse_response(mapping)` returns only provider
  identity, model, status, usage, cost and observation time from a saved receipt.
- `pipeline_usage_import.prepare_import(manifest_path)` streams local Codex
  JSONL and reads saved OpenRouter JSON, returning normalized events plus source
  hashes and coverage. It does not write the ledger.
- `pipeline_issue_ledger.normalize_usage`, `normalize_event`,
  `validate_event_batch` and `equivalent_event` own common validation.
- `append_events(path, events)` validates the entire batch and existing history
  under the shared lock, then atomically replaces the ledger with its unchanged
  existing bytes plus new records. Identical responses are idempotent; conflicts
  abort the batch. Files and the containing directory are fsynced.

Use a local schema-1 manifest. Paths are relative to that manifest, or absolute.
Never put raw prompts or credentials into it. `provider_scope` must remain the
same for records from the same machine/account across parent and child logs:

```json
{
  "schema": 1,
  "provider_scope": "workstation-account-a",
  "expected_session_ids": ["parent-session", "child-session"],
  "sources": [
    {
      "format": "codex-rollout-v1",
      "path": "parent-snapshot.jsonl",
      "assignments": {
        "exact-turn-id": {"issue_id": "ISSUE-17", "attempt_id": "attempt-1"}
      }
    },
    {
      "format": "openrouter-response-v1",
      "path": "review-response.json",
      "issue_id": "ISSUE-17",
      "attempt_id": "review-1"
    }
  ]
}
```

This example deliberately lists an expected child whose file is absent;
coverage is PARTIAL until that session source is supplied. Codex assignments
are exact turn IDs, not keyword guesses. A long turn spanning several issues
belongs to an explicitly shared-overhead issue unless finer attribution exists.
Unassigned records and unused assignments are reported. Child files are explicit
sources; identical scoped response IDs count once across files and repeated
imports. Different observation clocks alone do not create a new response; the
first clock is retained. Conflicting issue, attempt, model, status or usage is
rejected. No source parser can prove it was given every descendant session.

```bash
python3 skills/pcb-design/scripts/pipeline_usage_import.py \
  --manifest /local/usage-import.json --ledger "$PROJECT/01_docs/issue_usage.jsonl" \
  --dry-run
python3 skills/pcb-design/scripts/pipeline_usage_import.py \
  --manifest /local/usage-import.json --ledger "$PROJECT/01_docs/issue_usage.jsonl" \
  --require-complete
```

Dry-run validates the import packet only, without creating the destination or
checking its existing conflicts. The real import also validates the destination.
`--require-complete` refuses missing/unexpected declared sessions, unassigned
records and unmatched assignments before writing. Its completeness claim is
only `DECLARED_SOURCES_COMPLETE`, always `all_descendants_verified: false`.
Use a stable source snapshot; incomplete trailing JSON is rejected rather than
silently discarded. Missing response IDs cannot be safely deduplicated.

The local `codex-rollout-v1` adapter recognizes observed per-response
`token_usage_record.payload.usage` fields. It excludes cumulative
`event_msg/token_count`, and uses model/effort only from the exact turn context.
It is a versioned local-log adapter, not a promise of a stable public log API.
Cache-write tokens are not separately summarized; uncached input includes all
input not reported as cached. No subscription pricing is inferred.

Schema-2 USAGE adds `observed_at` to the schema-1 fields, requires a scoped
response ID and null start/end/duration, and cannot share a run ID with execution
events. Provider completion status is not an engineering verdict. Missing usage,
cost and timing remain unknown. Execution timing coverage excludes usage-only
observations and reports their missing durations separately. Summaries separate
Codex and OpenRouter accounting authorities rather than inventing one bill.
