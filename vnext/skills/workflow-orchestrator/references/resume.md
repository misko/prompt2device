# Checkpoint and resume

Use the adapter's existing durable records, not a new status registry.

Before pausing, preserve:

- Current stage/task and the user's next stop boundary.
- Accepted source and evidence identities, plus any failed candidate.
- Open findings, causal hypothesis and charged/cumulative attempts.
- Exact next bounded action and the missing evidence or authority it needs.
- Required instruction and tool versions.

Validate resumable artifacts through the owning tools. The current progress
view must agree with its authoritative records; prose cannot promote a stage.
Mark inherited versus newly measured claims. Preserve failed evidence when it
explains a decision; a handoff is not a reset.

On resume, reopen the handoff and exact records, check freshness and dependencies,
then load the active stage contract and next action's procedures. Missing or
changed evidence requires revalidation before use. Do not reconstruct acceptance
from conversation history or a worker's reassuring summary.

If fresh explicit user direction authorizes another finite recovery window,
follow the [milestone gate's resume requirements](exploration.md#milestone-gate).
An ordinary resume does not renew an exhausted recovery deadline.

At a requested phase reflection, record what worked, failures, retries, loaded
context and concrete process changes worth testing. Reflection does not waive
engineering evidence. Report the boundary and stop before downstream work.
