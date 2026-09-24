# Independent review: complete VBUS_PRESENT_N probe

**Verdict: ACCEPT only as an isolated P2/P3 research input.** It establishes
the three-pad disposable route and a local filled-plane witness. It does not
promote P1, P3, or the canonical board.

I inspected SOL follow-up `fcd83937` and the retained boards in
`/tmp/crow-presence-route-probe-sol`. After `Connectivity.Build`, each of
`R_VBUS_PU.2`, `Q_VBUS.3`, and `U_XU.8` has the same exact connected-pad set:
all three pads. The baseline has three singleton sets. The added F.Cu branch is
exactly `(208.01,72.0)` → `(214.5,72.0)` → `(214.5,74.5)`, 0.20 mm wide, then
uses the already-reviewed via/trunk/south-pad escape.

The saved unfilled DRC delta is exact: baseline 438 rows (225 clearance, 199
library-footprint, 14 dangling-via) and all-terminal probe 440 (the same 225
clearance and 199 library rows plus the two expected unfilled GND-via
findings). The filled baseline and filled all-terminal probe both have 424 rows
(225 clearance, 199 library-footprint). A fresh CLI rerun of the filled probe
matches that count and finds no VBUS_PRESENT_N track clearance, width, or short
row; the two matching VBUS rows are pre-existing U_XU pad-7/8 and pad-8/9
0.150-mm pad-spacing violations.

The In1 claim is supported at the stated local scope. The two GND via centers
`(215.5,75.6)` and `(203.85,110.4)`, plus the B.Cu trunk midpoint, are inside
the same filled GND outline (index 8); the two signal-via centers are outside.
An independent 1.0-mm strip sample over the 37.200437-mm B.Cu line, trimmed
1.116 mm at each end, found all 1,111 points inside that outline. This is a
useful saved-board local reference witness, not proof of impedance, via-field
behavior, whole-path return continuity, or simultaneous allocation capacity.

The filled/unfilled distinction remains binding: without fill the GND vias are
dangling. The probe also inherits 424 native violations and needs an owned
source/route, local decoupling, rule-class, and final reference analysis before
any production or acceptance claim.
