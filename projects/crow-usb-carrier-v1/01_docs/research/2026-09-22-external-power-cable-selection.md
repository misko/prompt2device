# External power cable selection

Selected cable assembly: Molex `226206-1022`, Micro-Fit 3.0 female-to-female off-the-shelf cable assembly, single row, two circuits, 150 mm nominal length, tin contacts, black 18 AWG UL 1061 discrete wire.

Primary authority is Molex product customer drawing `2262061022`, document revision A1, released 2024-01-23:

<https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/226/226206/2262061022_sd.pdf?inline=>

The drawing's exact `2262061022` row specifies `L1 = 150 ± 4 mm`. Its bill of materials specifies two `436450200` housings and four `430300038` female crimp terminals. The wiring table specifies two black 18 AWG UL 1061 conductors with straight-through continuity `A1` to `B1` and `A2` to `B2`; the drawing also requires 100% continuity and polarity test. Thus either end is the already-selected `43645-0200 + 2x 43030-0038` mate for board header `43650-0200`, with the far-end female housing retained as part of the exact cable identity.

The cable conductors leave the rear of the mated housing away from the board connector, so the schema-1 exit relative to the board connector is `along_mating_axis`. This selects identity and axial exit only. Installed straight run, first bend, bend radius, strain relief, far-end termination/support, clearance, and simultaneous service remain physical qualification work. Pin 1 remains pin 1 through the harness and pin 2 remains pin 2; first-article polarity and continuity checks remain required before applying power.
