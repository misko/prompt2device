# XU reset source-region repair (research only)

This packet repairs a source-region ownership defect in the pinned QSPI-gap
native board without changing the board, canonical floorplan, modular plan, or
P1 status.

The two foreign-region pads were:

| digital-power pad | native bounding box (mm) |
| --- | --- |
| `R_XU_RST_PU.2` | `[170.440, 100.080, 170.980, 100.720]` |
| `U_XU_3V3_OK.6` | `[165.250, 108.875, 165.950, 109.125]` |

They were inside the former `audio_clock_tdm` rectangle. The proposal divides
the two source rectangles at y=`99.84` mm. That is between the audio owner
envelope maximum y=`99.795` mm (`U_TDM_XLATE`) and digital-power owner envelope
minimum y=`99.885` mm (`R_XU_3V3_OK_TOP`), leaving 0.090 mm of native measured
separation. Both new rectangles start at x=`145` mm so they meet
`adc_reference` at its x=`145` edge without an interior overlap.

`verify.py` recreates the derived floorplan and contract in a temporary
directory, verifies all pinned hashes, audits every audio/digital owner
envelope and copper pad, and runs the existing coarse checker. It intentionally
reports the pre-existing `U_XU.51` nonlocal-witness failure; this packet makes
no capacity, routing, filled-reference, or P1-acceptance claim.

Run from the repository root containing this project:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-24-xu-reset-region-repair-terra/verify.py
```
