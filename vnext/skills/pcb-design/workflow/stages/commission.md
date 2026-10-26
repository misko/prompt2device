# PCB-COMMISSION — local research contract

## Inputs

Original brief and chronological decisions, capability profile, current status,
journal, hold, relevant research, and project file contracts. Reopen these;
do not reconstruct missing engineering evidence from conversation memory.
Preserve user quotes and prompt hashes. Later user decisions supersede earlier
ones explicitly, never by quietly rewriting history.

## Allowed work

Consolidate facts and execute bounded feasibility calculations. Separate
user-confirmed requirements, proposed engineering assumptions and open facts.
Each open item gets a question, evidence owner and closure condition. Do not
repeat answered questions. Unknown current, voltage tolerance, component limit
or applicability remains unknown unless a cited source or explicit bounded
assumption resolves it. A sensitivity case is not a guaranteed envelope.

When an analog signal path needs feasibility analysis, use
[channel-margin](../../procedures/commission/channel-margin.md). Add the
[channel-design](../../procedures/commission/channel-design.md) extension when
the missing inputs are circuit choices the designer owns, not external facts.
Do not repeatedly label a designable resistor/bias value as missing user input.
For rail conversion and branch protection, use
[power-design](../../procedures/commission/power-design.md) without the channel procedures.
Use the [project binding](../../bindings/project.md) for records and review. No purchase,
vendor message, firmware change, CAD production or hardware experiment is
implicitly authorized by a calculation task.

For remaining cross-block connections, reset/configuration or shared budgets,
use [integration-design](../../procedures/commission/integration-design.md).
This extends candidate research only; the admission boundary below is unchanged.
For an explicitly authorized isolated one-channel drawing, use
[schematic-draft](../../procedures/schematic/draft.md), subject to a reviewed
project source-contract exception. This is a commission task, not a new graph
stage or permission to accept the complete project schematic.
For part-availability screening, apply the entrypoint's
[design-stage sourcing policy](../../procedures/part-recheck.md).

## Task completion versus stage completion

A research task is complete when its exact inputs, equations, results, unknowns
and next discriminating action are recorded and independently reviewed. It may
complete with FAIL or UNKNOWN engineering findings. Neither is stage acceptance.

Commission admission requires traceable scope and acceptance criteria; resolved
or explicitly bounded critical input/load/protection/interface facts; assessed
spec tensions and capability applicability; and independent review on exact
evidence. Architecture and sourcing retain distinct graph boundaries and need
their own accepted evidence before schematic. Use the local
[admission route](../../procedures/commission/admission.md) only after independent
review of the required adopted source. A completed research task is insufficient.
The coordinator records promotion only on a current reviewed certificate;
keep the hold through upstream admission and never delete it to make a conductor run.

If a calculation contradicts a candidate, return it to the candidate's owner.
If a supplier or user fact is absent, record the gap and pause that question;
independent work can proceed. Do not repeat unchanged investigations.
