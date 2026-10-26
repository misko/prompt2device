# Whole-candidate routing review — behavioral test input

Use the local PCB skill and workflow orchestrator. Decide the next bounded task
and return a proposed journal entry. Do not execute it or mutate a board.
This is distilled from a real Crow checkpoint, not board acceptance evidence.

Two board types have current schematic, placement and nominal mating receipts.
The user requests routing development with a stop/reflection at acceptance.
The routing adapter refills native boards, runs all-track/all-severity DRC,
replays outputs and binds independent engineering review. No routing receipt exists.

An author repairs seven pod ground connections. Native DRC now reports zero
opens and zero physical faults, with 88 retained library/text/silkscreen warnings.
Accepted placement/pad/net identity is unchanged. A second build matches native
geometry, settings, plots and DRC under the adapter's permitted normalization.
The author's collision search checked each new via against all SMD pad lands.

An independent reviewer inspects the entire pod. Two inherited unfilled through
vias have drills intersecting SMD lands. They are nominally tented, but the pad
mask openings expose the overlapping bores. Neither the prior author check nor
the native DRC rules caught this. No filled/capped-via fabrication process is
specified. No placement collision or impossible pin escape is demonstrated.

The carrier is still incomplete: 92 opens and 52 dangling-track faults. Its
native geometry/settings/plots replay identically, but DRC reports select
different endpoint representatives for some remaining opens. The external
router exited zero and exported a session while logging an internal exception.
The imported native board is retained and was actually checked; no independent
review has approved it. Equal finding counts do not establish report equivalence.

One local pod repair allocation of 600 seconds remains; the author and reviewer
can be distinct. The orchestrator must preserve old sources, accepted receipts,
failed evidence and cumulative history. No fabrication or purchasing is authorized.

What next task should be dispatched, how should it be verified, and which stage
or reproducibility claims are justified now?
