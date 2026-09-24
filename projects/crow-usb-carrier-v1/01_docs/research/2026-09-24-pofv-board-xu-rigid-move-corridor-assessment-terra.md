# Conditional-POFV board: XU rigid-move corridor assessment — 2026-09-24

This is a read-only geometry diagnostic of
`/tmp/crow-pofv-conditional-sol/04_kicad/crow_carrier.kicad_pcb`, SHA-256
`4d645bcefd2bfe11e243fac74b8b485f7f059b8c9f11435bf6680af553011eef`.
The POFV source change is unrelated to these corridors.  No source or board
file was changed, no P1 attempt was consumed, and this is not P1 acceptance.

## Measured current endpoints

| Bundle | Endpoint centres (mm) | Direct separation (mm) |
|---|---|---:|
| USB DP | U_USB_ESD.1 `(216.650,36.425)` → U_XU.60 `(216.162,95.400)` | 58.977 |
| USB DN | U_USB_ESD.2 `(217.350,36.425)` → U_XU.59 `(216.162,95.800)` | 59.387 |
| TDM MCLK | U_TDM_XLATE.6 `(175.738,97.975)` → U_XU.23 `(211.100,107.662)` | 36.665 |
| TDM BCLK | U_TDM_XLATE.4 `(175.738,96.675)` → U_XU.22 `(210.700,107.662)` | 36.648 |
| TDM FSYNC | U_TDM_XLATE.5 `(175.738,97.325)` → U_XU.20 `(209.900,107.662)` | 35.692 |
| TDM DATA | U_TDM_XLATE.7 `(175.738,98.625)` → U_XU.107 `(200.838,97.800)` | 25.114 |

The required native corridor widths remain 0.97 mm for USB and 1.80 mm for
the four TDM signals.  The XU remains at `(208.5,100.0,90°)`.  The current
USB screening strip is only a diagnostic: `x=216.10..217.40`,
`y=36.75..91.30` mm.  It excludes foreign F.Cu bodies/pads but still needs
separate ESD/XU pockets, connector entry, In1 fill and route proof.

TDM is physically split by the frozen pin plan.  DATA leaves west at pad 107;
MCLK/BCLK/FSYNC leave the south edge at pads 23/22/20.  The existing data
screen intersects `C_XU_VDD_105`, `C_XU_VDD_106`, and `C_XU_VDDIO_109`; the
clock fanout screen meets the XU body/pads.  This board's In1 GND zone is
unfilled, so it cannot demonstrate the required continuous reference plane.

## Rigid-move result

No simple rigid `U_XU` translation or rotation improves the USB pair and all
four TDM endpoints together.

* Moving the present 90° XU pose in **-Y** moves USB pads toward the ESD and
  moves the three south-edge clock pads toward their translator pads.  It also
  moves west-edge DATA pad 107 farther below U_TDM_XLATE.7, worsening its
  already obstructed escape.  A +Y move improves DATA only until its
  0.825-mm Y offset is consumed, while worsening USB and all three clocks.
* Moving XU **east** reduces the USB pair's small X mismatch (0.488/1.188 mm)
  but lengthens every TDM run.  Moving it west helps TDM X distance but makes
  USB X mismatch worse; it cannot resolve the opposite Y requirements above.
* Of the four orientations, 90° is the USB-facing pose.  At the same centre,
  0° puts the USB pad near `(203.9,92.338)`, 180° near `(213.1,107.662)`, and
  270° near `(200.838,104.6)`: each is materially farther from the ESD in X,
  Y, or both.  Rotation cannot join DATA and clock pins onto one edge because
  their relative package edges are invariant.

## Recommendation

Do **not** make an XU rigid-block floorplan change.  The minimal productive
backtrack is source-owned XU decoupler-ring/fanout redesign: preserve the
90° USB-facing XU pose and create two separate local TDM exits, one westward
from pad 107 and one southward from pads 20/22/23.  It must relocate the
specific `C_XU_VDD_105`, `C_XU_VDD_106`, and `C_XU_VDDIO_109` blockers with
new P-ADJ and return-path evidence; it is P2 work, not a P1 corridor pass.
Only then should an isolated board measure two L-shaped lanes with endpoint
pockets and filled In1 GND.  A single four-track `tdm_to_xmos` reservation
would require an authorized schematic/firmware pin remap (the documented
pad-19 option), not floorplan placement.
