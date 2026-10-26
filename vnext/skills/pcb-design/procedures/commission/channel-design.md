# Propose a calculable channel

Use for an applicable analog signal path when its source/load interfaces,
topology or component values need selection;
a preceding margin report is not required.
Retain the commissioned architecture and shortlist unless a calculation rejects
them; disclose any proposed substitution and why. External supply specifications
remain unknown, but selecting circuit values is design work, not a user question.

When endpoint parts are unselected, begin with a bounded part/reference screen
under the [part recheck](../part-recheck.md), then establish their actual signal
type, sensitivity/level, bias, impedance and supply requirements before detailed
gain/corner work. That screen is a valid first task, not a complete circuit.
Cheap ideal models may answer a named feasibility question, but do not optimize
an invented source interface and later search for a part to fit it. Derive the
candidate connection/value table below from the screened interfaces.

Produce one candidate connection/value table covering the actual signal chain:
input coupling, bias source and impedance, gain/feedback, output isolation,
interconnect load and receiving circuitry as applicable. Include a converter
interface only when present in the chosen design. Give endpoints (named nets or
device functions), values, tolerances, voltage ratings and per-channel quantity;
include supply/bias requirements. A family name without a circuit is not a
deliverable. Mark unselected ordering/package details rather than inventing them.
This report is a proposed circuit, not executable CAD source or adopted values.

Use manufacturer reference circuits as evidence, not unexplained copyable
values. Check actual part/revision and derive the changed circuit's loaded
transfer, including driver/source resistance, coupling and differential versus
per-output loading. Calculate operating points, bandwidth, sensitivity to
tolerance, receiver full-scale/clipping and input common mode where applicable.
State the assumed signal band and explain it; do not invent a user requirement.

Use the existing [margin procedure](channel-margin.md) for supply/load checks.
Allocate a proposed maximum protection/filter voltage loss as a requirement on
the later branch circuit, not proof a chosen device meets it. Keep input-fault,
surge, startup, stability and integrated-noise qualification distinct from this
linear model. A typical device curve is not a guaranteed margin.

Provide a short executable calculation with assertions or tabulated outputs.
The independent reviewer checks topology first, then rederives loaded gain,
per-leg load/swing and at least one corner calculation. If an essential reference
or topology cannot be established within the bounded attempt, name the exact
gap and pause; do not produce another broad study with no new circuit choices.
Keep the commissioning hold; no purchase, integrated schematic, placement or
stage promotion follows from accepting the report as a faithful proposal.
