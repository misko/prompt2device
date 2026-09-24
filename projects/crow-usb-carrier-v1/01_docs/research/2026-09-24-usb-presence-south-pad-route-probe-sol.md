# USB presence-sense south-pad route probe

**Research only; P1 remains INCOMPLETE.** This probe changes only disposable
boards under `/tmp/crow-presence-route-probe-sol`. The source board is the
isolated Q_VBUS move at SHA-256
`60a903b5ae5c7c7ef084fb3bd5dd50abf26e1e0e134a928f46107a6c90934b17`.
No canonical board, floorplan, P1 attempt, or P3 route was changed.

The earlier `presence_xu_entry` F.Cu rectangle `[204.8,91.3,205.4,106.8]`
cannot reach U_XU.8 from the north: it crosses the U_XU body and pads 88–90.
U_XU.8 is on the **south** edge at `(205.1,107.6625)`, with copper bbox
`[204.975,106.925,205.225,108.4]`. A disposable two-via route connected
Q_VBUS.3 to that pad:

| Part | Native path, board mm | Width / via |
| --- | --- | --- |
| F.Cu source | Q_VBUS.3 `(212.9375,74.5)` → `(214.5,74.5)` | 0.20-mm track |
| First transition | `(214.5,74.5)` | 0.60-mm through via, 0.30-mm drill |
| B.Cu trunk | `(214.5,74.5)` → `(204.75,110.4)` | 0.20-mm track, 37.2004 mm long |
| Second transition | `(204.75,110.4)` | 0.60-mm through via, 0.30-mm drill |
| F.Cu pad escape | `(204.75,110.4)` → `(204.75,108.93)` → `(205.1,108.58)` → U_XU.8 | 0.15-mm track |

The B.Cu route bbox has no native body, pad, or track obstacles in the
`x=204..215, y=74..111` search window. South of U_XU, the opposing
C_XU_VDDIO_10 and C_XU_VDD_11 body edges are `x=204.435` and `x=205.065`:
a 0.630-mm gap. With the default netclass 0.20-mm clearance and the board's
0.15-mm minimum track, the F.Cu escape has only 0.080 mm of lateral placement
range. A 0.60-mm via plus two 0.20-mm clearances needs 1.00 mm, so the second
via sits beyond the decouplers at `y=110.4`. U_XU pads 7/8/9 are on 0.40-mm
pitch with 0.25-mm copper width. They already have 0.15-mm pad-to-pad clearance
violations against the 0.20-mm netclass rule; the 0.15-mm trace from pad 8 adds
no new local violation. A default-width 0.20-mm trace would leave only 0.175 mm
at the pad end. The target-pad escape is a local exception to the coarse
checker’s whole-U_XU-body obstacle rectangle, not a through-body corridor.

For a return-transition probe, F.Cu GND stubs connect Q_VBUS.2 to a GND via
at `(215.5,75.6)` and C_XU_VDDIO_10.2 to a GND via at `(203.85,110.4)`.
Both are 0.60/0.30-mm through vias. The first trial return via at
`(214.5,75.6)` shorted the diagonal B.Cu signal trunk and was discarded.
The two final GND vias have no new native spacing or short violation.

Using the same `.kicad_pro`, `kicad-cli pcb drc --severity-all --format json`
reported 438 violations on both the unfilled baseline and signal-only probe:
225 clearance, 199 library-footprint, and 14 dangling-via findings. Native
connectivity reduced total unconnected edges from 1,358 to 1,357, and both
Q_VBUS.3 and U_XU.8 gained a connected track. R_VBUS_PU.2 remains unconnected
to this probe. Adding the two return vias to the **unfilled** board produced
two additional `via_dangling` findings, one per new GND via; the saved In1.Cu
GND zone was unfilled and provided no native copper connection.

A second, disposable, saved **filled** comparison produced 424 violations on
both baseline and signal-plus-return boards: 225 clearance and 199 library
footprint findings, with no new dangling vias, shorts, or clearances. Native
unconnected edges decreased from 1,321 to 1,318. The filled comparison shows
that the two local GND vias can contact the existing In1.Cu pour in this
isolated board. It does not establish full path return continuity, impedance,
all-terminal access, or a P1/P3 acceptance. Those still need a board-hash-bound
filled-polygon path check and independent native review.
