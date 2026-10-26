# Evaluate one candidate channel

Deliver a reproducible feasibility calculation, not a frozen circuit. Begin
with an applicable analog signal path's retained topology and exact component
revisions. Use only the stages and interconnects present in that design; this
procedure does not require a sensor, cable or converter. Cite manufacturer
limits with operating conditions; distinguish typical from guaranteed limits.
Do not substitute new parts or fill missing circuit values silently.

1. Define the actual supply and signal measurement planes: input source,
   protection/interconnect, local rails, signal source, driver and load as
   applicable. List known values,
   proposed values, tolerances/temperature, and unknowns before calculating.
2. Expand each present load by its instance count: maximum quiescent current,
   regulator/bias currents, signal load and peak demand. Avoid
   counting a load twice. If a maximum is unavailable, report a sensitivity
   case and the maximum allowable load, not a guaranteed supply margin.
3. Calculate applicable interconnect/contact/protection drops, minimum device
   supply, regulator headroom and heat. Unknown protection loss stays symbolic or as a remaining
   budget. Check upper voltage and fault exposure separately from lower-margin
   arithmetic; nominal input voltage alone cannot qualify the input.
4. Derive loaded gain, input common mode and output swing at each
   stage. Include source/series resistance and receiver input impedance. If
   the receiver or bias/filter values are absent, show the dependency and
   report UNKNOWN; do not equate unloaded gain with loaded receiver input swing.
5. Separate DC/quasi-static results from bandwidth, cable stability, startup,
   clipping, integrated noise and faults. An RC pole or noise-density number
   alone proves none of these. Calculate only what defined inputs support.
6. Give each check PASS (only under stated bounded inputs), FAIL, or UNKNOWN.
   Record equations/units and a rerunnable arithmetic snippet or permitted
   calculation source. Do not use PASS as the report's overall admission state.

Independent review must check at least supply/load accounting and loaded
signal-path equations against exact sources. Retain failures and source gaps.
End with a small actionable decision: keep the candidate conditionally, repair
it, or request the missing fact. No integrated schematic or purchases follow
automatically. Missing guaranteed data cannot be repaired by more decimals.
