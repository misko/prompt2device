# Independent review — TPS26625 U.1 pad-launch screen

**Subject:** SOL packet `daba0ce1`,
`2026-09-25-ti-tps26625-input-pad-launch-sol`. The result is a useful
native-geometry witness only; it is not a current, thermal, process, P1, or
P2 qualification.

## Reproduced selected pose

I rebuilt the selected 1.20-mm F.Cu track in a temporary board from the pinned
partial-return artifact, with centerline x=188.350 mm and U-end y=46.025 mm.
Native round-rect polygon intersection reproduces **0.09134743 mm²** overlap
of U.1's **0.14062127 mm²** land, or **64.9599%**. The effective copper shape
contains U.1's center and connects exactly `U_SPOKE8.1` and
`C_SPOKE_IN8.1` on `N12V_PROTECTED`.

The selected full-width track keeps **0.255065 mm** to U.2 (`SPOKE_UVLO8`) and
**0.269714 mm** to PowerPAD.11 (`SPOKE_RTN8`). The packet's 1.655273-mm
U.1-to-C(IN).1 direct-gap check remains inside the existing project 2.5-mm
ceiling. Its GND return/fill and GND/RTN separation are inherited from the
pinned return trial; no source part moves or width exception is introduced.

I independently replayed the archived profile in a temporary directory. The
before/after boards both give **199 violations / 499 opens**, **+0/-0** issue
identities, and no via-process failures.

## Bound of the result

The overlap is a KiCad polygon approximation at 0.005-mm inside error. It is
appropriate for the stated geometry screen, not a solder-joint area,
current-sharing, or process-margin calculation. The reported finite search is
only 195 poses: x=187.9–188.5 mm in 0.05-mm steps and U-end y=45.85–46.20 mm
in 0.025-mm steps. It proves the selected feasible pose within that grid; it
does not establish a global optimum or rule out a better pose outside it.

The grid maximum contact reaches 84.55% pad overlap but retains only
0.205077 mm U.2 clearance. The selected pose has just 0.055065 mm above the
0.20-mm clearance rule. No center-contained grid point reaches 0.30-mm
foreign-copper clearance. These facts rule out treating the screen as robust
production margin.

The source `INPUT_TRUNK` 1.20-mm width / 0.20-mm clearance / 2.85-A allocation
still requires the separate current-allocation reconciliation, stackup copper,
DC resistance/voltage-drop/temperature analysis, and PowerPAD/RTN thermal
island evidence defined in the U.1 launch rubric. The output, ILIM, dVdT, and
UVLO loops remain unfinished. Retain this as a constrained no-neck geometry
candidate, with no canonical promotion or P2 claim.
