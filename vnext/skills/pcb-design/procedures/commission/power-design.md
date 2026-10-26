# Propose one power path

Use for a DC power path requiring conversion or protection analysis. Use retained
load/interconnect/circuit evidence and name the actual measurement planes from
the input source to device supply pins, including branches or remote loads only
when present. Separate actual source facts from a
proposed required source envelope; do not wait for a label to choose circuit
values, or treat the proposed envelope as evidence about the user's adapter.

Give a connection/value table with exact candidate devices or module variants,
control states, ratings and tolerances. Prefer modules for conversion under the
project's integration posture; disclose any bare-IC alternative as unadopted.
Expand simultaneous loads without double counting. Separate maximum ratings,
guaranteed operating limits, typical values and assumed load allocations.
Unknown loads stay symbolic; a conditional capacity calculation is not a
complete system power budget.

Before relying on a tight component window to close a critical power check,
show a practical implementation with evidence for that window. For storage
capacitors, include effective tolerance, bias, temperature and relevant ESR;
parallel nominal values alone do not establish the bank's bounds. Check the
parts that control the conclusion, not every ordinary passive in advance.
If the available implementation misses designer-owned bounds, revisit those
bounds and their coupled startup/fault calculations before affected integration;
do not accumulate compensating circuitry or silently narrow component variation.
Separate guaranteed limits from credible prototype models with later falsifiers;
missing manufacturer maxima alone do not impose a new pre-schematic bench gate.
Apply the existing part recheck when an exact candidate or quantity changes.

Check lower supply/dropout and upper voltage separately. Include cable,
contacts, switch resistance at its stated temperature, fuse/filter losses,
regulator tolerance and load regulation. Check protection threshold tolerance
against both normal operation and the weakest downstream limit. Current-limit
settings need min/max limits, normal-load margin and short/startup behavior;
TVS breakdown voltage is not its clamp voltage or a sustained-OV cutoff.
Account for power dissipation and capacitor charging, including simultaneous
startup; do not infer thermal or transient survival from DC resistance alone.
Distinguish the interval requiring valid operation from safe startup/shutdown.
Do not turn a recommended performance limit outside that interval into a stress
rating or add sequencing solely to preserve performance the user does not need.
Still obey absolute limits and explicit manufacturer shutdown/recovery sequences;
an invalid-data interval does not waive electrical safety or reliable restart.

State what happens for reverse input, output short, converter input-to-output
fault and unpowered/output-backfeed conditions within the project's fault scope.
Evaluate alternate power sources, including USB-only power, when present.
A missing fault rating or
timing specification is an open qualification item, not silently defended.
When installation conditions expose signal/return paths to grounding, surge or
lightning risks, give those risks their own boundary: low-voltage branch
protection does not close them. Derive environmental exposure from the project,
not from a previous installation.

Provide short reproducible calculations and a disposition per check. The
independent reviewer rederives at least the worst supported drop, threshold
window and fault path from primary sources on exact report bytes. End with
one feasible candidate or a named contradiction and smallest upstream change;
do not repeat an unchanged search. Keep the existing report/retry/hold rules.
No purchase, hardware experiment, CAD production or stage admission follows.
