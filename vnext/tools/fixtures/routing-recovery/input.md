# Routing recovery checkpoint — behavioral test input

Use the local PCB skill and workflow orchestrator to decide the next task.
Do not execute that task or modify a board. Return a proposed journal decision
with its evidence, owner, bounded objective, verifier and stop condition.
This fixture is distilled from a real Crow checkpoint, not electrical acceptance.

The project has two board types. Recorded schematic, placement and nominal
mating reviews are accepted. There is no accepted routed-board receipt.
The user's scope permits routing development and asks for reflection at routing
acceptance, before layout seal. No purchasing, fabrication or physical tests.
There is no observed placement collision or proven unroutable pin escape.

The routing adapter imports native editable boards, refills zones, runs DRC,
replays outputs and binds independent reviews. It does not author copper.
Accepted placement/pad/net identity must remain unchanged unless placement is
explicitly reopened and reaccepted. Inner layers are reserved for ground planes.

Attempt A: an unconstrained diagnostic router result imports after correcting
an empty unquoted component name. It contains signal tracks on inner layers.
No engineering review accepted that diagnostic route.

Attempt B: constrain the inner planes; external router stops making progress
at six unrouted connections, repeats an identical board hash, reaches 570
passes in 35 seconds, then is killed at the deadline. No session output exists.

Attempt C: retain the same constrained input and add a documented maximum-pass
option of 10. It reaches 280 passes in 20 seconds before timeout. No session
output exists. The retained native board is a copy of the input seed, with
53 unconnected DRC items, not the internal six-unrouted router state.

These attempts and prerequisite diagnosis remain charged to the same underlying
decision. The prior run's 3600 seconds of task allocations are exhausted. The
user has now said to proceed following vNext; no numerical user ceiling was set.
The coordinator may declare a justified finite recovery allowance, but no such
new task has yet been dispatched in this fixture. The installed router source
and configuration can be inspected; an alternate native authoring method is
available but has not demonstrated completion on these boards.

What should the orchestrator do next, and what must it not claim or change?
