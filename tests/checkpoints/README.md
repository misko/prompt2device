# PCB checkpoint regression tests

These tests ask whether an agent can solve a bounded engineering problem after
resuming a saved board checkpoint with the current PCB skill. They complement
the from-brief `tests/t5_skill_canary` tests. They do not authorize production
gate reuse, release acceptance or changes to sealed releases.

## Boundaries

| Component | Owns | Does not own |
|---|---|---|
| `runner.py`, `schema.py` | Restore, current skill context, deadlines, scope and results | Board-specific solutions |
| `cases/<name>/` | Snapshot, graph state, investigation history, objective, allowed edits | Provider selection |
| Case grader | Independent artifact properties and owning gate invocation | Solver narrative or exact reference output |
| `agent_run.py` | Explicit one-attempt Codex invocation and reported usage | Automatic retries or escalation |
| `select_cases.py`, `suites.json` | Small named selections and conservative change hints | A production dependency engine |

The runner reuses `pipeline_runtime.run_stage` for bounded execution. The
current `skill-authority-map.json` supplies workflow identities and context;
the test framework does not maintain another PCB stage graph.

## Run without model spending

From the repository root, use `/usr/bin/python3` for native KiCad cases:

```bash
/usr/bin/python3 tests/t1_checkpoint_framework.py
/usr/bin/python3 tests/t2_checkpoint_cases.py
/usr/bin/python3 tests/checkpoints/select_cases.py --suite smoke
/usr/bin/python3 tests/checkpoints/runner.py prepare \
  --case tests/checkpoints/cases/crow_assembly_population \
  --run-dir /tmp/checkpoint-assembly-001
```

The run directory must not exist. Preparation copies the snapshot to
`workspace/`, supplies task/current skill context, runs trusted preparation and
requires the documented initial failure. A broken baseline is an infrastructure
error, not a solver failure. Read the generated context entrypoint and task in
that workspace. After making a repair there:

```bash
/usr/bin/python3 tests/checkpoints/runner.py grade \
  --run-dir /tmp/checkpoint-assembly-001
```

`runner.py run --case … --run-dir … -- COMMAND ARG…` runs an external solver
command under the same protocol. Commands are argument lists, not shell strings.
The workspace is the command's working directory. Manual prepare/grade records
execution and usage as unknown; it must not be represented as a measured agent run.

## Opt-in solving trial

```bash
/usr/bin/python3 tests/checkpoints/agent_run.py --allow-agent \
  --case tests/checkpoints/cases/crow_assembly_population \
  --run-dir /tmp/checkpoint-assembly-agent-001 \
  --model gpt-5.6-luna --effort medium
```

The model must be explicitly selected and available to the installed CLI/account.
This example is not a promise of provider availability. The adapter performs
one attempt, uses workspace-write sandboxing, ignores user configuration, and
does not grant approval bypasses. Case deadlines bound elapsed execution; they
are not hard token or dollar limits. Do not retry unchanged failures blindly.
The Linux adapter first probes the required bubblewrap network namespace
primitive without invoking a model. An unavailable nested sandbox fails before
model spending. This preflight catches that host limitation, not every possible
CLI failure. On hosts where it fails, use `prepare` and a separately supervised
agent, then `grade`; do not disable the sandbox to make the CLI test green.

The CLI contract is based on local `codex exec --help` and the
[official non-interactive documentation](https://developers.openai.com/codex/noninteractive).
Raw event logs remain local to the run directory. Completed-turn token counts
are provider-reported; interrupted-turn usage may be missing. Cost stays unknown
unless separately measured. Never commit credentials or raw solver conversations.
Malformed or incomplete completed-turn usage is labeled PARTIAL. Externally
supervised agent runs may record their provider/model and observed handback, but
must not claim subprocess cleanup, measured token usage or hard cost bounds.

## Case authoring

Each `case.json` contains schema version, stable identity, tags, provenance,
checkpoint graph states/history, task and snapshot paths, editable patterns,
trusted preparation/grader argv, expected initial findings and deadlines.
History records the attempt, result, disposition and reconsideration condition.
Use current graph IDs. An incompatible stage is an error requiring an explicit
case migration, not an automatic claim that old acceptance still applies.

Command placeholders are `{repo}`, `{case}` and `{workspace}`. Grader output ends
with one JSON object: `schema: 1`, `outcome: PASS|FAIL|ERROR`, and
`findings: [{code, message}]`; optional `evidence` describes measurements. Exit
codes are respectively 0, 1 and 2. The grader must check artifacts independently
of the solver's text and refuse stale or invalid evidence.

Keep reference repairs in the case's trusted driver, outside the snapshot.
Reference controls establish solvability; they are not agent-solving evidence.
Before a paid run, demonstrate initial FAIL, valid repair PASS and an invalid
shortcut FAIL. Permit alternate valid repairs through property checks rather
than matching historical output bytes. Native geometry cases must grade actual
copper/connectivity/constraints, not merely source configuration text.

Adding a case normally requires only its packet, controls and suite entry.
Clearly label synthetic reductions and scope: a tiny Crow-inspired coupon is
not a complete historical Crow board or full-release replay.

## Results and limitations

`state.json` binds the original packet and restored context. `result.json`
records final engineering verdict and execution evidence separately. A failed
or timed-out command cannot become an overall success because it left plausible
files. Missing handoff, out-of-scope edits and grader failures are explicit.

Hash checks detect changes after execution; they are not a hostile-code security
boundary. Workspace-write limits writes, not all host reads. Reference solutions
are excluded from supplied context, but this local runner is not a hermetic
benchmark against an agent intentionally seeking answer files. Use an isolated
container/host for that stronger claim.

Case-only change hints can select those cases. Shared or unknown changed paths
retain the requested full suite. Empty selections are errors. These hints select
tests; they do not prove production dependencies or waive any board gate.

## Initial validation

`evidence/2026-09-20-validation.json` retains the three independently graded
Luna-medium solutions, packet/tool identities, source changes and limitations.
All three passed via external supervised agents. The first nested CLI trial
failed at its host sandbox; that failed trial and its reported usage are retained
separately. The subsequent preflight rejects this host without invoking a model.
Sixteen framework tests and five case-control tests passed. The complete repository
suite is not claimed green: a broader run was interrupted after historical/project
contract failures. Run the focused checks above to reproduce this framework's
deterministic validation.
