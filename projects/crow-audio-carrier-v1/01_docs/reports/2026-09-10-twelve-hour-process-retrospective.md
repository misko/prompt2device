---
schema: 1
kind: pcb-human-report
report_id: 2026-09-10-twelve-hour-process-retrospective
title: Twelve-hour PCB development process retrospective
subtitle: Preserve the engineering gates while reducing tool repair and coordination overhead
project: crow-audio-carrier-v1
date: 2026-09-10
status: REVIEWED
evidence_status: INCOMPLETE
---

## Executive conclusion

**INFERRED:** We should change the process. This run delivered an independently
accepted schematic and useful checker repairs, but too much of its effort went
into developing the verification infrastructure during the board's release
path. Repeated agent transfers and manually assembled evidence amplified small
execution mistakes. Stronger native tests found real defects; bypassing those
tests would have concealed the problems rather than finished the board.

**PROPOSED:** Qualify the toolchain before starting a board, retain one capable
implementation owner through a bounded repair, and automate evidence collection
and handoff validation. Reserve fresh independent reviewers for engineering
judgment and admission boundaries. Change the skill through a tested revision;
this report does not silently override its current mandatory handoff rules.

## Question and scope

The user asked what the last twelve hours teach us about making this run and
future uses of the PCB skill easier. The fixed observation window is
2026-09-10 06:10:57 to 18:10:57 PDT (13:10:57Z to01:10:57Z next day).
Subject: this worktree's branch through c04caa91, the schematic and placement
journals, preserved failed attempts, and the latest interrupted review.

This is a workflow assessment. It does not change electrical requirements,
waive a failed check, approve connector orientation, or admit a release.

## Evidence boundary

**MEASURED:** Git contains48 commits in this window. Commit count measures
activity, not board completion. Journal milestones put the resumed ownership
at07:42PDT, initial accepted schematic review at10:46, canonical schematic
acceptance at12:26, the next placement stop at P-LAND around12:29, and the
last committed generic checker repair at16:23. The intervals below are elapsed
calendar spans, not measured CPU time, billing or uninterrupted active work.

**MEASURED:** The latest reviewer is now errored due to a provider usage limit;
no final result or output manifest was delivered. The latest observed recorded
child ended around16:23. Its exact failure time and the intervening idle time
are unknown. The full twelve-hour window must not be described as twelve
hours of productive engineering. See the [interruption record](../evidence/pland-backtrack-20260910/kernel-contract-interruption.md).

## Findings

| Period, PDT | Measured outcome | Process implication (inferred) |
|---|---|---|
| 07:42–10:46 | Fresh reviewers launched; repeated delivered-PDF/native ink, clipping, polarity and identity defects corrected; schematic review accepted | Native rendering qualification was incomplete before board review. Reviewers repeatedly became exporter testers. |
| 10:46–12:26 | Placement/source repair and canonical regeneration; exact new PDF reviewed again | Some review work was correctly invalidated by changed output. Producer churn and broad source fingerprints increased repeat work. |
| 12:29–16:12 | P-LAND diagnosis, rejected method/witness authors, native API/fixture/output/schema repairs, incomplete kernel author | The gate needed product-level tool engineering. Broad implementation commissions preceded a stable native compatibility contract. |
| By16:23 | Five baseline checker-contract failures repaired; affected suites70/70, gate-contract37/37, structure17/17 passed | A startup health check could have found these before the board reached this boundary. |
| Review interrupted | Native semantic counterexamples and override controls retained, no final judgment | Completion must be a machine-checked result, and executor health must be separate from the last running beacon. |

**MEASURED board status:** The accepted canonical schematic witness covers
19/19 pages and19/19 native regions,333 components and937 pins. The retained
native board remains unrouted: the earlier complete gap census was514 gaps
across220 nets, and it has no accepted placement/routing result. These board
counts are retained measurements, not a fresh DRC run for this report. There
is no minted release;07_releases contains only its contract.

**MEASURED avoidable friction:** The retained attempts include a producer
failing because the worker created a directory that the producer expected to
create itself; unsupported SWIG container APIs; incomplete netclass schemas
that changed native class assignment; missing --all-track-errors in an exact
pair-count test; temporary directories deleting failed native evidence; a test
entry point discarding its failure return value; and several premature author
handbacks with unfinished original scope. These are different causes and should
not all become expensive engineering backtracks. Their records are in the
[source register](#source-register).

**INFERRED ownership problem:** I contributed to the overhead. I commissioned
broad kernel work before the compatibility fixture and supported rule semantics
were fully established, relied too much on prose reminders for process closure,
and repeatedly asked for completion from an owner that was not delivering the
required artifact. Preserving failures was correct; repeatedly rebuilding the
administration around them was expensive. This was not caused by insufficient
user direction.

**INFERRED premise problem:** Passing a useful36-case matrix was treated too
readily as evidence that the language model was sufficiently established. Later
private native controls challenged string matching, Boolean precedence and area
boundary behavior. Those latest results are not yet adopted, but they show why
broad prose claims about KiCad semantics need small native discriminating tests
before implementing another parser.

## Recommendations

| Priority | Proposed change | Benefit and tradeoff | Owning home |
|---|---|---|---|
| 1 | One startup toolchain qualification command: pinned KiCad/Python versions, API smoke test, serialize/reload fixture with full classes, native positive/negative DRC, gate-contract audit and one fresh reviewer launch | Exposes infrastructure failures before a board is in its release path; small up-front cost | Existing skill startup/authority checks and maintained fixtures |
| 1 | One standard execution/evidence runner using the existing bounded process infrastructure: allocate output directory, retain every child artifact, capture argv/PID/times/rc, verify outputs, write manifest last | Eliminates repeated handwritten wrappers and lost evidence; requires one well-tested implementation | Existing pipeline_execution/process_runner authority, not a competing runner |
| 1 | Qualify native rule semantics before authoring a replacement gate; keep source-backed positive/hostile fixtures in a small reusable maintained corpus | Prevents costly implementation against an incorrect oracle; requires deliberate compatibility maintenance when KiCad changes | Native rule adapter and tests, sanitized reusable fixtures outside project archives |
| 2 | Keep one capable implementation owner for a bounded source transaction; deterministic retries for cwd, directory, serialization and test-runner mistakes stay within its execution budget | Fewer repeated context transfers; independent judgment still required for changed engineering assumptions | Revise lifecycle/backtrack classification with regression tests; no ad hoc bypass |
| 2 | Replace prose-only handback requirements with machine-checked acceptance: required outputs, completed guard rows, source identity, suite exit status, process closure | Prevents premature “done” reports from consuming coordinator cycles; machine checks still cannot judge scientific correctness | Existing TaskEnvelope/TaskAttempt and completion validator |
| 2 | Track engineering hypothesis attempts separately from process setup errors, while bounding both total time and retries | A mkdir or wrong executable does not consume the same scientific budget as a disproven design hypothesis; prevents infinite cheap-error loops too | Existing investigation/execution schemas, preserving history |
| 2 | One immutable artifact store with manifests referencing previous blobs, plus a concise generated handoff view | Retains provenance without repeatedly packing earlier evidence into new archives; closure computation must be tested | Existing artifact bundle/identity machinery |
| 3 | Stabilize canonical generation and define dependency-scoped invalidation; still review every changed visible output | Avoids redoing unrelated review when only presentation-neutral metadata changes; equivalence must be independently demonstrated first | Generator, semantic identities and review contract |
| 3 | Report accepted milestones, blocker age and time spent in engineering/tool repair/admin/idle; monitor executor failure and quota signals | Makes poor progress visible early; do not equate hashes, archives or test counts with board advancement | Existing beacon/journal/execution receipts |

**PROPOSED immediate application:** Keep the accepted schematic fixed. Reopen
and adjudicate the latest partial native evidence before any new broad authoring
commission. Implement the smallest verified rule/candidate adapter, exercise the
real old-behavior regression and compatibility corpus, and only then restart the
canonical board flow. Reuse the newly repaired repository contract checks. Do
not tune placement or routing around a gate whose semantics remain unresolved.

**PROPOSED future ordering:** First automate execution/handback and establish the
native compatibility fixture. Then revise handoff granularity. Adding another
long checklist to the skill would reproduce the coordination problem.

## Validation plan

**OWED:** The process changes above are proposals, not implemented skill policy.
Evaluate them on one small representative board and one dense carrier fixture:

1. Deliberately inject each observed setup failure. It must yield an accurate
   non-pass receipt with preserved outputs, without requiring a new judgment
   agent merely to diagnose an output-directory or runner error.
2. Every admitted native rule behavior needs a positive and a discriminating
   hostile control against the pinned KiCad executable. Unknown syntax and
   untested semantics must block by name.
3. A clean run must reach the same existing engineering gates. No lower DRC,
   unconnected, review, orientation or release bar is permitted.
4. Record stage-accepted outcomes, repair/admin elapsed time and fresh reviewer
   count before/after. Target no repeated handoffs caused solely by execution
   setup errors. Do not claim a percentage speedup without measuring it.
5. Simulate failed/idle agents and missing handbacks. The coordinator must expose
   terminal state promptly and preserve partial work without inventing a review.

## Source register

- [Schematic journal](../journal/schematic.md): ownership, repeated native/PDF defects and exact accepted review boundaries.
- [Placement journal](../journal/placement.md): actual stage stops, fixture failures, author handbacks and transfers.
- [Native interface output failure](../evidence/pland-backtrack-20260910/native-interface-adoption.md): directory ownership error before native execution.
- [Fixture diagnosis](../evidence/pland-backtrack-20260910/fixture-dback-adoption.md): native API admission and exhausted local probes.
- [Complete-class admission](../evidence/pland-backtrack-20260910/native-complete-classes-adoption.md): full class schema and missing complete-track reporting flag.
- [Rejected kernel and measured controls](../evidence/pland-backtrack-20260910/native-kernel-adoption.md): exact final WIP, incomplete guards, transient evidence losses and source restoration.
- [Checker-contract repair](../evidence/pland-backtrack-20260910/checker-contract-repair.md): actual RED/GREEN and unchanged audit thresholds.
- [Interrupted reviewer](../evidence/pland-backtrack-20260910/kernel-contract-interruption.md): missing final result and provider failure.
- Git window: `git log --since=2026-09-10T13:10:57Z --until=2026-09-11T01:10:57Z --format='%h %s'`,48 commits through c04caa91. This is an activity census, not elapsed-time attribution.
