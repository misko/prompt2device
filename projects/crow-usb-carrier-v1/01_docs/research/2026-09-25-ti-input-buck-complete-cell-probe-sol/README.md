# Complete input-buck cell partition attempt — stopped at J_PWR envelope

Run `python3 replay.py` to reconstruct this source-only trial. It begins with
the reviewed Q_PRE TI board and the earlier **in-memory** `C_PWR_CT2` +1.13 mm
y move; neither board nor canonical source is edited. The accepted 13
quiet-power cells (69 refs), plus six established cells, still pass strict
`_physical_cells` on that disposable board.

The candidate assigns all **20/20** native `input_buck` refs exactly once:
12 to the local primary `input_buck` core, four to a front-end cell, and one
each to `D_QIN_GS`, `C_IN3`, `C_OUT2`, and `J_PWR` cells. It retains all 569
native owners and the four complete power branch terminal counts of
42+27+68+34 = **171**. The packet records every cell's full native-envelope
hull and runs the actual checker.

The first hard failure is `input_buck_jpwr: physical cell off board outline`.
`J_PWR`'s body/courtyard envelope is [26.125, 19.955, 36.875, 30.955] mm;
the board outline begins at y=20.000 mm. Any rectangular cell that contains
the complete fixed J_PWR native envelope inherits this 0.045 mm overhang and
fails the strict outline test. The electrical pads are inside the outline,
but the current physical-cell grammar requires the full envelope. At least a
reviewed physical pose/outline correction is needed before this 20-ref cell
partition can be accepted. Other candidate cells and connectivity remain
unvalidated after that first failure.

As required, the trial stops there. It does not run four branch checks on an
invalid partition and claims no route, return, capacity, P2, or P1 credit.
