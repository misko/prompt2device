# TPSM63603 joint local-cell source search — bounded result

Status: **NO LEGAL SOURCE POSE FOUND IN THE BOUNDED ALLOCATION; NOT A GLOBAL IMPOSSIBILITY CLAIM**.

The read-only search used accepted native board SHA-256 `c3d906591a343aea8949687c05c0f5ff4372e982c5af70a04df4828b7409fd93` and unchanged source floorplan SHA-256 `744c0f2e6e8737969495b1febdf2f80a6406db21d63c066a238f5e4ffc51490f`. It saved no board, generated no board, and edited no repository file.

## Joint predicate and bounded census

`/tmp/crow-power-joint-cell-search.py` jointly translated and rotated all 13 TPSM63603 satellites while holding `U_BUCK`, `J_PWR`, the 27 fixed anchors, all 16 hold capacitors, and every unowned reference invariant. Every trial used the footprint's transformed F.CrtYd polygon, not a body or bounding-box substitute, with 0.25 mm clearance against fixed geometry and the other twelve satellites. Functional scoring used the dossier's named TPSM63603 pins: RT 1, VIN 3/4/18/19, VOUT 7–15/30, VLDOIN 22, VCC 23, AGND 24/27, and FB 25.

The bounded run examined 430,486 joint states. Per-part fixed-obstacle-legal site counts were 364 each for `C_IN1/2/3` and 500 retained best sites for each other satellite. It found no mutually legal complete assignment inside these source-allocation bands:

* quiet/control: x 42.0–53.5, y 88.0–95.0 mm;
* input bank: x 39.0–55.5, y 96.0–104.0 mm;
* output bank: x 39.0–56.5, y 87.0–96.0 mm.

The machine-readable terminal record is `/tmp/crow-power-joint-cell-candidate.json`. The run was stopped at its computation boundary and was not extended.

## Exact residual carried from the preceding joint screen

The rejected local-output pose `C_OUT1 (52.600, 96.100, 90)` and retained `C_IN2 (54.000, 97.500, 0)` overlap in both courtyard and copper allocation. Their transformed courtyard bounds are `[50.875,93.325]–[54.325,98.875]` and `[51.675,95.875]–[56.325,99.125]`; `C_OUT1.1` (`N5V_BUCK`) and `C_IN2.1` (`N12V_PROTECTED`) have zero pad-edge separation. Moving them to `C_OUT1 (53.500,95.500,90)` and `C_IN2 (55.000,96.000,90)` clears pads by 0.225 mm but still fails the required 0.25 mm courtyard predicate. Moving `C_OUT1` down to `(53.200,92.700,0)` collides with the proposed feedback cell: its N5V pad reaches zero edge separation from `R_BUCK_FB_TOP.2` (`BUCK_FB`).

This identifies the residual as a power-owned allocation conflict between the input bank, output bank, and quiet feedback/control band. No ADC or other unowned block is the blocker.

## Required source-space allocation

A successor source pass must widen one power-owned band before another geometry search:

1. Move the input bank as a group, including `C_IN2`, upward/right within power-owned space and reserve the U3/U4/U18/U19-to-bank current-loop corridor. Do not move `U_BUCK`, `J_PWR`, or any unowned reference.
2. Move the output bank as a group, not `C_OUT1` alone, into the vacated right/lower island and reserve the U7–U15/U30-to-bank current-loop corridor.
3. Keep `C_VCC`, `C_VLDO`, both FB resistors, `R_RT`, and `R_AGND_JOIN` together in the quiet upper/lower control pocket, with a distinct AGND/FB return reservation and no input/output current-loop crossing.
4. Re-run all 47 existing numeric rows after any source pose change. The prior 47/47 result remains valid only for the accepted baseline bytes.

The next allocation may use power-owned `C_PWR_CT2` neighborhood space only if that timing/supervision cell is moved and revalidated as part of the same source-owner proposal. The search result does not authorize such a move; it names the smallest additional power-owned allocation that can be explored without unrelated block movement.

No source patch is emitted because every tested complete pose failed the joint predicate. Emitting a patch from a partial packing would misrepresent it as a candidate. Manufacturer requirements remain qualitative: the diagnostic pin spans guide compaction but are not invented TI millimetre limits. P3/FULL still owns actual current-loop copper, FB Kelvin sense, AGND/PGND treatment, return paths, and thermal vias.
