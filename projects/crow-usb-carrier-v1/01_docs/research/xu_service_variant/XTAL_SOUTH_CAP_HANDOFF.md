# XTAL handoff below the retained XU decoupler — geometric candidate

This read-only study preserves the pinned `C_XU_VDDIO_35` pose. Its native
body/F.Courtyard envelope is `[217.495,104.845,218.505,106.755]` mm, so the
oscillator handoff begins at y=107.0, beyond the 0.15 mm stroked-courtyard
limit of y=106.905.

Two disjoint F.Cu 0.15 mm doglegs pass the exact XU pads to that handoff with
0.15 mm clearance. `XTAL_OUT` goes south along the cap's west side.
`XTAL_IN` goes north, crosses above the cap, then goes south on its east side.
The swept screen finds zero intersections with native bodies/courtyards, pads
other than the two intentional XU source pads, existing tracks, or all 27
P1-fixed references.

The source arrangement keeps the cap in a narrow `xmos_core_east` region
ending at y=107.0, adds `clock_oscillator_handoff [217.2,107.0,218.95,118.5]`,
and splits the remaining XU region west of x=217.2. QSPI shifts to
`[219.2,110.5,223.2,118.5]` with its XU face beginning at x=219.2. Its face
retains 3.6 mm raw width for the declared 2.7 mm demand; the pinned board has
no native footprint/courtyard or track in either shifted QSPI shape.

The 0.25 mm gap from the handoff to the shifted QSPI owner is only source
ownership geometry. It does not prove electrical clearance. This is a
P2-required geometric candidate: actual pad escapes, copper, DRC, the filled
`In1.Cu` reference, oscillator electrical checks, and P1 review remain open.

Reproduce with KiCad 10 `pcbnew` and PyYAML:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/xu_service_variant/xtal_south_cap_handoff.py
```

The generated receipt is
[xtal_south_cap_handoff.json](xtal_south_cap_handoff.json).
