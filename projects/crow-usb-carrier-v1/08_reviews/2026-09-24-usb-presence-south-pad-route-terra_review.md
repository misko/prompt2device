# Independent review: USB VBUS_PRESENT_N south-pad probe

**Verdict: retain as a sound, narrow P2/P3 research input.** It does not close
the VBUS_PRESENT_N net or support P1 acceptance.

I inspected SOL commit `4a32abc7` and its retained disposable boards under
`/tmp/crow-presence-route-probe-sol`. The source board hash is the Q_VBUS-move
candidate `60a903b5ae5c7c7ef084fb3bd5dd50abf26e1e0e134a928f46107a6c90934b17`.
The signal route is physically continuous: Q_VBUS.3 at `(212.9375,74.5)` joins
the first 0.60/0.30-mm via at `(214.5,74.5)`, a 0.20-mm B.Cu diagonal reaches
the second via at `(204.75,110.4)`, and the 0.15-mm F.Cu escape terminates on
U_XU.8 `(205.1,107.6625)`. The documented B.Cu diagonal is 37.2004 mm; the
retained endpoints reproduce that length.

The south escape does not conceal a new native clearance problem. U_XU.8 has
the expected 0.25-mm-wide pad between pads 7 and 9 at 0.40-mm pitch, so its
existing 0.15-mm pad-to-pad violations remain. The routed 0.15-mm escape adds
no VBUS_PRESENT_N clearance row. The two nearby decoupler bodies end at
`x=204.435` and `x=205.065`; their pads end at y=109.710, while the signal via
at y=110.400 begins 0.390 mm below that copper. Its copper edge is also 0.215
mm below the lower body edge y=109.885. The via is therefore outside both
decoupler bodies and pads; the stated 0.630-mm lateral body gap is real.

The native DRC receipts agree with the claimed delta. The unfilled baseline and
signal-only board each have 438 rows (225 clearance, 199 library-footprint,
14 dangling-via); the signal probe has no new short or clearance row. The
intermediate return trial correctly records one short and is not evidence.
The final unfilled return board has two additional dangling GND vias. After
filling In1.Cu, both the baseline and final return board have 424 rows (225
clearance, 199 library-footprint), with no dangling via, new short, or new
clearance. That demonstrates local contact of both GND vias to the existing
filled plane only.

The limiting facts are material: R_VBUS_PU.2 is still disconnected, so this is
not a complete VBUS_PRESENT_N net. The filled-zone comparison has no
hash-bound polygon/continuity proof along the 37.2-mm signal path, no
impedance or return-current analysis, and no all-terminal or local-decoupling
acceptance. The 0.15-mm pad escape relies on the current minimum rule and
cannot be generalized without an owned package-escape review. Keep the probe
as evidence for a later P2/P3 route study; do not use it for P1 capacity,
route acceptance, or a canonical board edit.
