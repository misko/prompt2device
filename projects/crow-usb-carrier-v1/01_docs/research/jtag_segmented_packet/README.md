# Fixed 90° Crow JTAG segmented-access packet

**Disposition: standalone four-net source declaration `INCOMPLETE`; whole
59-net allocation `FAIL`.** This is an isolated research model of the unchanged
`J_JTAG` pose `(228, 50, 90)` on the native QSPI-gap board SHA-256
`fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27`.
It does not alter canonical source or PCB. The builder pins every source input
and the corrected segmented checker; [result.json](result.json) records the
generated source, floorplan, contract, and checker hashes.

The exact fixed endpoints and XU handoffs are:

| Net | Fixed physical pad | XU source handoff | Ordered access reservation |
| --- | --- | --- | --- |
| `JTAG_TMS` | `J_JTAG.2` | `U_XU.44` | `jtag_access_2` |
| `JTAG_TCK` | `J_JTAG.4` | `U_XU.51` | `jtag_access_4` |
| `JTAG_TDO` | `J_JTAG.6` | `U_XU.37` | `jtag_access_6` |
| `JTAG_TDI` | `J_JTAG.8` | `U_XU.36` | `jtag_access_8` |

The source-owned, disjoint `board_integration_jtag` strip is
`[221,65,226,84]` mm on F.Cu, with `In1.Cu` named as the return-reference
layer. The debug connector owns `[221,40,238,65]`; its south face is
`[221.1,64.7,225.9,65]`. The XU north face is
`[221.1,84,225.9,84.3]`. The preceding QSPI-gap declaration remains in the
packet. The USB frontend is reduced to `[200,35,238.5,40]` so the JTAG
connector source region has one owner. The four exact fixed pads use their
native pad bboxes as boundary witnesses; the four XU endpoints use declared
face handoffs. The physical exits are TMS east and TCK/TDO/TDI south. The
checker witness calls those contacts `west` and `north` respectively, because
it names the reservation-facing side of the source-pad contact. No connector
is moved or rotated.

Each `jtag_access_*` reservation lists two or more **ordered, positive-edge
joined, nonoverlapping axis-aligned segments**. The TMS chain exits east;
TCK, TDO and TDI leave the south pad edges through the inter-row opening and
dogleg around the native lower-row contacts. The final segment of every chain
contacts the JTAG strip. [coarse_jtag.json](coarse_jtag.json) contains exact
segment coordinates and envelopes; [result.json](result.json) records their
native pad boundaries, pairwise copper spacing (minimum 0.15 mm), and a
0.15-mm clearance screen against foreign native pads, front bodies/courtyards,
existing F.Cu, saved filled F.Cu, and F.Cu rule areas. These
chains encode the four simultaneous native Manhattan witnesses from Terra's
`5ad7dd9b` feasibility probe, with butt-jointed rectangular reservations for
the segmented checker. The origin connector courtyard requires the probe's
pad-escape exception; foreign bodies, other pads, rule areas, existing tracks,
saved filled copper, and competing reservation shapes are screened. The
checker assigns **no capacity slots** to fixed access or the integration strip.

The source corridor names eight exact endpoint obligations: four native
JTAG-pad-to-strip accesses and four XU-pad-to-north-face handoffs. All remain
`P2_REQUIRED`. Its separate `GND` obligation requires a continuous **filled**
`In1.Cu` reference; an unfilled F.Cu zone outline is not proof of copper or
return continuity. Effective width/clearance, physical routing, mating and
connector service, reset branch completion, crystal access, and DRC remain
unproved. This packet makes no P1 or P2 acceptance claim.

The checker sees the **full 59-net Crow denominator**: USB device 4, XMOS
service 13 (six QSPI, four JTAG, reset, two crystal), ADC timing 15, ADC analog
17, and power boundary 10. The standalone validation checks exactly four
fixed pad witnesses, four ordered chains, four XU handoffs, and all eight
source corridor obligations. The whole packet still fails at the unchanged
`U_XU.38` reset witness, which spans beyond its source region; the QSPI and
JTAG exact-endpoint denominator errors follow because that allocation stops
before consuming its handoffs. XTAL_IN/XTAL_OUT retain their unresolved
clock-cell access and filled-return debt. None of these nine remaining XMOS
service nets receives capacity credit from the JTAG declaration.

Reproduce with KiCad 10 `pcbnew` and PyYAML from the repository root:

```sh
/usr/bin/python3 projects/crow-usb-carrier-v1/01_docs/research/jtag_segmented_packet/build_packet.py
```

The source input is the pinned QSPI packet; this builder writes only this
research directory. The board is the separately regenerated QSPI-gap artifact
at `/tmp/crow-xu-qspi-gap-sol/project/04_kicad/crow_carrier.kicad_pcb`.
