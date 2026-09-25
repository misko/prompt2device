# D15 independent preflight review — PASS

**Signed review: Terra, 2026-09-25.** This is a pre-generation research review
under accepted D15. It authorizes neither a route nor fabrication, assembly,
qualification, release, order, or stage credit.

## Result

**PASS for the one D15 private generation to proceed, subject to D15's
post-generation stop rules.** The candidate remains an ignored copy at
`06_build/prototype_board_diagnostic/current-ti-4l-3313a-preflight-20260925`.
No generator was run by this review.

I reran:

```sh
/usr/bin/python3 01_docs/research/2026-09-25-d15-preflight-sol/verify_preflight.py
python3 01_docs/research/2026-09-25-ti-expanded-native-parity-probe/replay.py
```

The first returned `PREFLIGHT_CONTENT_CHECK_PASS`, reporting exactly four
changed copied-source files and `Generator not run`. The frozen native parity
replay reported KiCad 10.0.4, board SHA-256
`fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16`,
circuit JSON SHA-256
`580ac31b0de8d376d888caa1a342ae43c0636fbd13c74048392173acf718cb6d`,
netlist SHA-256
`a40b45c27b2169ed4f3dd43d72a1f4f7112d829985f98918a8855ed76735e9bd`,
zero native DRC violations, 499 unconnected items, and performed schematic
parity with zero issues.

## Bound checks

The manifest's frozen authority and generator hashes match the current files.
The copied PCB, `.kicad_pro`, and `.kicad_dru` are byte-identical to the frozen
reference before generation. The copied circuit and netlist also match. The
source tree has exactly the D15 allowlisted changes:

- `03_src/floorplan.yaml`: 3313A 1.58-mm stack fields and one F.Cu permissive
  `usb_pair_xu_launch` area `[215.3,95.0,217.1,95.8]`.
- `03_src/rules/nets.yaml`: USB pair 0.180/0.100 and the exact
  `USB_DP`/`USB_DN` scoped 0.100-mm clearance; generic foreign clearance
  remains 0.150 mm.
- `03_src/rules/rf.yaml`: 3313A private-screen cross-section plus retracted
  stale `USB2-CLAIM-ZDIFF` text/evidence.
- `03_src/rules/route_fab_overrides.txt`: stack-dependent aspect-ratio text.

Native U_XU pad boxes reopen as D15 states: 59 is
`[215.425,95.475,216.9,95.725]`, 60 is
`[215.425,95.075,216.9,95.325]`; 58/61 are outside the permitted area. The
private candidate still has 14 tracks, one copper zone, eight rule areas, and
six holes. The separate synthetic KiCad control establishes the intended
pair-only `.100 mm` override and foreign-net `.150 mm` negative control.

The preflight verifier enforces pre-generation byte identity for the native
output and source-change bounds. D15 remains the binding post-generation
write boundary: only private `.kicad_pcb`, `.kicad_pro`, `.kicad_dru`, TMUX
POFV areas, parity/DRC reports, and a receipt may be generated; no tracks,
arcs, vias, teardrops, fabrication exports, or canonical writes are allowed.
Any unallowlisted difference, failed parity, saved copper/zone fill, or native
defect is `FAILED_RESEARCH`.
