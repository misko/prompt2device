# Explore, converge, recover

Use when the domain permits candidate artifacts before acceptance. The domain
owns artifact content and engineering gates; this control is domain-neutral.

1. Fix raw requirements, a finite total worker-time allowance, maximum rounds,
   candidate width and deadlines. Reserve review and recovery capacity.
2. Dispatch isolated authors with identical inputs, no shared conclusions, and
   one bounded whole-deliverable attempt, not a chain of micro-reports.
3. Independently compare exact candidates. Select one repair baseline or none.
   Record why, outstanding blockers and alternatives. Selection is not acceptance.
4. Repair prioritized stable problem IDs. Reassess after one failure; at most
   two local attempts per problem before upstream recovery. Renaming does not
   erase its history. Do not maintain several parallel repair pipelines.
5. If architecture is the obstacle, start a new bounded round from a redesign
   brief, preserving previous candidates and cumulative spend.

Redesign pointers contain unchanged requirements, blocker IDs/evidence,
attempted remedies/outcomes, disproven assumptions versus unknowns, useful
retained facts, and freedom to replace architecture/parts. Do not pass the full
failure history or turn an unknown into a ban. Authors receive only this compact
pointer set plus original inputs. Recovery needs a decision-changing hypothesis
and allowance inside the remaining run budget. It can happen immediately for
a fatal approach. A new round does not replenish budgets. If it produces no
better path, escalate a focused question or ask the user, not recursive fan-out.

## Local execution adapter

`tools/exploration.py` manages one run.json execution journal and hash-bound
candidate/review snapshots. It checks transitions, reservations, round/repair
ceilings, milestone dispatch permission and freshness; it does NOT dispatch agents, verify engineering truth,
infer equivalent problem IDs or cancel workers. The coordinator binds real agent
handles, checks deadlines and interrupts at the boundary. Recorded actor names
are not identity authentication. No event issues engineering acceptance.

For new comparisons, `python3 tools/exploration.py subjects RUN` rehashes all
frozen candidates and returns compact candidate-to-snapshot digests for the
review's `subjects`. The full path/hash maps stay in run.json; older reviews
remain valid unchanged. Adoption and later reuse still recheck every file.
This avoids repeating large manifests, not reviewing the actual artifacts.

See the tool help/event API for initialization, dispatch/completion, comparison,
selection, repairs, redesign and pause/resume. At a user pause stop live workers;
recording completed results is still allowed. Resume only on explicit direction.
Use one current journal, not duplicate STATUS and per-worker execution ledgers.
At checkpoints report artifacts, selected baseline, blockers, actual next action,
budget and user stop. The domain's existing verifier alone accepts a stage.

### Milestone gate

Read [the recovery rule](recover.md#milestone-plateau-despite-local-success).
Before the first dispatch, record `milestone-checkpoint` with one stable `milestone`,
`result: baseline`, `tasks: []`, `reason` and `path` to retained starting evidence.
The adapter hashes evidence and rechecks it before later transitions. After work
settles, checkpoint every newly finished task exactly once (sorted IDs), with
`result: advanced | prerequisite | unchanged`, reason and immutable evidence path.
`advanced` additionally needs nonempty `closed` milestone conditions, the owning
`verifier` and `regressions: false`. A local test PASS alone is `prerequisite`.
These declarations are coordinator/domain judgments, not authenticated verdicts.

Before continuing a stalled milestone, record `reassess` with `action`, `reason`,
`hypothesis` and the discriminating `check`. After one no-progress checkpoint,
`continue` may be justified; after two it is denied. Choose `change`, `backtrack`,
`escalate` or `pause`. Non-pause recovery then requires `deadline` (finite Unix
seconds). This bounds the whole recovery, including setup/reviews/waits; later
reassessments can shorten but not extend it while stalled. Existing task limits,
repair ceilings, cumulative budgets and user stops still apply. Settle results
even when late; no task may be launched with a deadline beyond this limit.

Fresh explicit user direction may authorize another bounded recovery after a
pause. Only on an already paused run with all results settled and assessed,
`resume` may include `user_authorized: true`, a finite future `deadline`, `reason`
and project-local `path` to retained evidence of that new user direction. The
adapter hashes and rechecks this evidence; it cannot authenticate user authority.
Each authority evidence hash can authorize only one new window, even if copied
to another path; a later window needs retained evidence of another user direction.
Do not manufacture it from an old instruction, a coordinator decision or a new
worker. Preserve any user-set limit unless the user actually changes it. This
replaces only the active recovery window, retains every old event, plateau,
attempt and charge, and requires a new causal `reassess` before dispatch. Plain
`resume` does not renew a deadline; reassessment alone cannot renew it either.

One checkpoint may assess a settled fan-out together; do not batch unfinished
sequential attempts to bypass the dispatch check. Reviews/helpers are assessed
without double-counting an author attempt. All actual launches must first obtain
a successful `start` transition; recording a `note` about an external launch is
not a supported dispatch path. This gate cannot prevent arbitrary shell bypasses
or cancel an already running worker; the coordinator still owns supervision.

Counters are derived from existing events, not stored in a second progress file.
An old journal without checkpoints fails closed on dispatch; it needs reviewed
migration preserving prior outcomes, not a fresh baseline hiding spent attempts.
For a stalled legacy journal, `progress-migration` binds an immutable reviewed
history report (`path`), milestone, all retained task IDs, reviewer, reason and
`prior_stalled >= 2`. It preserves every old event, task, repair count, selection
and charge, and still requires explicit reassessment before dispatch. It is
one-time adoption, not recovery authority. A `start` of kind `recovery` then
requires that plateau decision, an objective and project-local write scopes;
it does not alter exploration phase, repair ceilings or engineering acceptance.
The recovery parent may cover a long-running tool plus review inside its fixed
recovery deadline; ordinary worker segments retain their1200-second ceiling.
Historical domain events named `checkpoint` remain opaque and unchanged; they
are not the new namespaced `milestone-checkpoint` records.
Use it for a different authorized strategy, never a renamed third local repair.
Frozen projects do not inherit this change automatically. A user pause cannot
be cleared by progress or recovery events. Test offline with
`python3 -m unittest discover -s tools -p test_progress.py -v` from the vNext root.

For ordinary domain work, including the next task after verified advancement,
`start` kind `work` takes an `objective`, project-local `writes` and explicit
positive integer `seconds`. It preserves exploration phase, selection and reviews;
it is not another candidate or an engineering acceptance. Start only with prior
tasks settled and the milestone dispatch gate open. Like a recovery parent, its
fully charged duration may cover several worker segments; total budget and any
active recovery deadline still apply. Its own deadline bounds its helpers, and
while it is live only its helpers may start. This is not a new retry allowance.

An active repair, recovery or work parent may delegate bounded `assist` tasks (for example sourcing or
rendering), with explicit non-overlapping writes and deadlines inside the parent
deadline. Charge their allowances to the same run and preserve the independent
review reserve. Helpers are neither new candidates nor independent acceptance
reviewers. Stop/settle all helpers before freezing the parent's exact artifacts.
Finishing a helper records its result without closing the parent attempt. Further
`assist` tasks with that same live parent may start while its helper results await
assessment; other pending results still block them. Once the parent finishes,
one `milestone-checkpoint` must cover it and every newly finished helper exactly
once. Helper success cannot reset the plateau or renew any deadline or allowance.
Use `note` for coordinator decisions and corrected assumptions; it cannot promote
a stage, reset a budget or replace a review. Charged time includes reservations
and late settlement, not an authenticated measurement of model compute time.

At a settled review, `diagnose` reserves a focused, read-only expert task against
a named subject and blocking finding without opening another repair. Record its
question, real worker handle and report; the coordinator evaluates the report
before choosing recovery. It preserves selection, review and repair counts and
cannot confer acceptance. Only one diagnosis per exact subject/problem is
allowed; renaming an equivalent question does not permit repeated escalation.
New diagnostic evidence may justify reopening independent comparison on the
unchanged subjects with an explicit reason. The same two-comparison ceiling and
cumulative budget still apply; a diagnosis does not itself regrade a finding.

Bind a real handle whenever dispatch occurs, including provider failures. A
terminal failed review without any handle represents a canceled/failed dispatch,
not an executed comparison; it retains its full budget charge and history but
does not consume the two-comparison ceiling. Never omit a handle to reset retries.

At a settled independent-review checkpoint, a coordinator-chosen pilot allowance
may be reconsidered under the user's continuing task authorization. Use an
explicit `allowance` event with the old/new finite total, evidence-led reason and
authority; retain cumulative spend, attempts and round ceilings. This is not an
automatic retry replenishment. A user-set limit needs explicit user permission
to increase. The adapter records the stated authority; it cannot authenticate it.
If a provider failure prevents reaching that checkpoint, `allowance` may name
`failed_review` once for that terminal failed task on the unchanged subjects,
with evidence that a bounded recovery is now feasible and the same authority.
It cannot adopt a review, change selection, refund spend or relax comparison/
repair ceilings. A completed comparison must go through normal review adoption.
