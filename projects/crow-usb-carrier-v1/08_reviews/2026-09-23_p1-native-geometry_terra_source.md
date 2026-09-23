# P1 native geometry review — REJECTED / engineering INCOMPLETE

Reviewed exact candidate `04_kicad/p1_trial.kicad_pcb`, SHA-256
`637e266594a8b89dc8ce93ed9dc38f2661dc250c8f593fcc2cd2a03c3be44d51`,
staged before review from the retained P1 candidate. The floorplan source
SHA-256 is `084063400a90dcaef9629ba8a98c3839d9ded6dbcb2431f551c2862fe5bc2bcd`.

Native reopen with KiCad 10.0.4 found 568 footprints, 1,866 physical pads and
426 nets. The required 27 anchors exactly match `floorplan.yaml`; the 16 hold
capacitors occupy their declared two islands, at the recorded 12.10 mm x 9.10
mm pitch with 0.41 mm courtyard gaps. The top render supports the intended
coarse organisation: eight channel bays across the upper board, ADC/digital
blocks in their prescribed regions, hold banks in the lower islands, and USB/
debug at the right. This confirms only that the coarse placement was saved.

## Blocking P1 geometry defects

All 32 `shorting_items` in the native DRC are real different-net copper
overlaps, not unrouted-board noise.

* `J_JTAG`: seven overlaps. The Samtec 1.27 mm-pitch footprint has 1.50 mm
  pads in the pitch direction after the board's 90 degree rotation. In
  particular pad 7 (`KEY_NC`) overlaps pad 9 (`GND`), and pad 8
  (`JTAG_TDI`) overlaps pad 10 (`XU_RESET_N`). The originally queried
  7-to-9 short is therefore real; it is neither a valid no-connect treatment
  nor an alias.
* Six `TI_DCK0005A_SC70_5` instances create 12 shorts and two
  `TI_DCT0008A_SM8` instances create 10. Their lead pitch is 0.65 mm while
  their pad length in the pitch direction is respectively 1.00 mm and 1.20
  mm. Each observed pair is different-net copper overlap, including supply,
  ground, logic and intentionally NC pads.
* Three GND thermal vias in the U_LDO seed land on distinct U_LDO pads: pad 9
  `N3V3_ADC`, pad 10 `N3V3_ADC`, and pad 6 `LDO_PGFB`.

The footprint owners are `03_src/lib/crow_usb_digital.pretty/`
`Samtec_FTSH_105_01_L_DV_K.kicad_mod`, `TI_DCK0005A_SC70_5.kicad_mod`, and
`TI_DCT0008A_SM8.kicad_mod`; the via conflict is owned by the U_LDO thermal
via placement in `03_src/floorplan.yaml`. Correct the source geometry from
the manufacturer land patterns, then regenerate the native board and repeat
P1. Do not patch this frozen board.

## Net identity and DRC classification

Direct native-pad versus accepted-netlist comparison gives 1,762 exact
`REF.pad` net matches and no mismatches. The remaining 17 are all the
explicit J_USB numeric-to-land aliases (A1/A4/A5/A6/A7/A8/A9/A12,
B1/B4/B5/B6/B7/B8/B9/B12, SH); their native names have the same accepted net
as their corresponding numeric schematic pin. P-PINMAP also passed 793
declared physical pin identities. Thus the shorts arise from geometry, not a
netlist/pad reassignment.

The 443 diagnostic DRC violations are not a placement or fabrication receipt:
this board is intentionally unrouted and was checked under generated default
rules, yielding 499 unconnected items. The 499 unconnected items are expected
at this P1 state. Default-profile-only findings (silk-over-copper, via
diameter/annulus, and the J_USB NPTH-to-contact 0.1944 mm hole clearance
against a default 0.25 mm threshold) need regrading under the owning prepared
rules. They do not erase the 32 direct copper overlaps. The 260 clearance, 40
hole-clearance, and 33 mask rows include consequences of those bad pad and via
geometries; a proper rule profile is still required to classify their remaining
rows.

## Corridors and physical integration

The named regions support the claimed coarse block allocation, but no P1
acceptance follows. The fixed connector bodies/bounding boxes place J_PWR and
J1–J8 slightly beyond the top board datum (bbox y=19.975 mm for a y=20.000 mm
edge), while J_USB extends to y=19.470 mm. Such edge-nose placement can be
intentional, but no native mate/latch/grip/cable/strain/service proof was
provided. The declared USB and debug regions also overlap as 2D allocations;
their coexistence has not been proved with operational envelopes. All 19
physical connector FULL targets remain INCOMPLETE and are not waived by this
review.

P2 remains responsible for local bypass/thermal/Kelvin placement, bank feeds,
the eight analog differential paths and return corridors. This review did not
undertake routing feasibility.

## Verdict and backtrack

Candidate verdict: **REJECTED for P1 acceptance; engineering INCOMPLETE.**
Backtrack first to source footprint geometry and U_LDO thermal-via coordinates,
then regenerate and re-open native DRC under the prepared profile. Re-run the
P1 fixed-feature/corridor review after the real shorts are absent. Keep
connector FULL and P2/P3 work pending; do not promote the candidate or infer
route/fabrication readiness.

