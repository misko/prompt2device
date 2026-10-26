---
name: workflow-orchestrator
description: Coordinate a domain workflow through bounded tasks, evidence-based verification, recovery and resumable checkpoints. Use with a domain adapter that supplies stages, acceptance owners and durable records; not as a substitute for domain engineering rules.
---

# Workflow orchestrator

Control how work proceeds; let the domain define what passes.
This is a coordinator procedure, not an autonomous scheduler.

For independent whole-deliverable candidates and evidence-led global redesign,
read [exploration control](references/exploration.md). This is optional
fan-out/converge before acceptance, not parallel unbounded repair loops.

## Control graph

```text
select ready task -> dispatch gate -> bounded attempt -> owning verification
                                                            |
                                       accepted -> record -> next / stop
                                                            |
                                       not accepted -> diagnose
                                                        |
                                   repair / backtrack / escalate / pause
                                                        |
                                        justified new bounded attempt
```

## Always preserve

- Exact inputs, candidate outputs and the owning verifier's evidence.
- One writer per live subject; independent review when the domain requires it.
- Prior accepted artifacts until an authorized replacement succeeds.
- Failed attempts and cumulative decision budgets across workers and handoffs.
- User scope and stop boundaries. Missing authority or evidence is not a pass.
- Distinction between a selected plan, completed work and accepted evidence.

Read the domain entrypoint and active stage contract. Reopen current records
before choosing work. Treat unknown applicability as unresolved, not excluded.
The coordinator sequences verification; it cannot supply a missing verdict.
On changed inputs invalidate affected dependent acceptance, not unrelated work.
After the first unsuccessful attempt, reassess the approach; after at most two
on the same unresolved decision, stop routine retries and apply the
[stagnation checkpoint](references/recover.md#stagnation-checkpoint). More reports
or a new worker are not evidence of progress.

Choose tasks by the next deliverable's unresolved conditions, not local activity.
Every return from a parent attempt, including local success, research and timeout, goes
through the [milestone checkpoint](references/recover.md#milestone-plateau-despite-local-success)
before another attempt. Bounded helpers may continue under that live parent;
assess their recorded results together when the parent settles.
The adapter must refuse an unassessed continuation or
an unresolved plateau; a task PASS is not a bypass. Apply
[dispatch priority](references/dispatch.md) only after that gate permits work.

## Load only for the action

| Action | Read completely |
|---|---|
| First task or changed adapter | [Task interface](references/task-interface.md) |
| Assign bounded work | [Dispatch](references/dispatch.md) |
| Failure, plateau or escalation | [Recover](references/recover.md) |
| Checkpoint, handoff or restart | [Resume](references/resume.md) |

Select instructions by task, not the whole future workflow. Read each selected
instruction file completely. Keep raw history and large artifacts in durable
storage; load their relevant evidence when required. A summary locates authority
but does not replace it. Do not assume on-demand loading clears prior context.

## Report

### User decision prompts

Own the recommendation, not just the question. Whenever requesting a user
decision, explain why their input is needed and present the orchestrator's top
two feasible recommendations in ranked order. For each, briefly state the reason,
main tradeoff and what work it would enable next; clearly mark the preferred
option. If fewer than two feasible options exist, say so rather than inventing
an unsafe or unsupported alternative. Distinguish permission to investigate from
permission to adopt, purchase or release. Record the user's choice in the domain's
existing decision records and apply it before selecting the next task.

### Progress reporting

Name the current stage/task, verified evidence, open blocker, next action and
requested stop boundary. Mark inherited claims explicitly. Do not claim that
this procedure mechanically enforces budgets, resumes or promotion: the
adapter's existing tools and records provide those capabilities where present.
