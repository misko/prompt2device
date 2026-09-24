# Isolated native P1 sub-lane measurement

This diagnostic generated an isolated board only. It did not modify the project board, route copper, run DRC, create a P1 attempt, or establish P1 acceptance.

The command was:

```sh
python3 skills/kicad-pcb/scripts/generate_board_generic.py \
  /tmp/crow-p1-sublane-native-20260924-terra-3/projects/crow-usb-carrier-v1/03_src/floorplan.yaml \
  --netlist /tmp/crow-p1-sublane-native-20260924-terra-3/projects/crow-usb-carrier-v1/06_build/netlists/crow_carrier.net \
  -o /tmp/crow-p1-sublane-native-20260924-terra-3/projects/crow-usb-carrier-v1/04_kicad/crow_carrier.kicad_pcb
```

The resulting board SHA-256 is `ce589f8a4889854946ef9a1c234ed57de89bfbf220e60f72cd6d818734d8813e`.

Native pad centres in mm were U_USB_ESD.1 USB_DP (216.650, 36.425), U_USB_ESD.2 USB_DN (217.350, 36.425), U_USB_ESD.3 GND (217.000, 35.575), U_XU.60 USB_DP (216.162, 95.400), and U_XU.59 USB_DN (216.162, 95.800). The proposed USB screening strip x=216.10..217.40, y=36.75..91.30 had no foreign F.Cu body or pad intersection; the only intersection when its lower endpoint is extended is U_USB_ESD's own body. That is expected and requires a separate endpoint pocket. This screen has not established the J_USB-to-ESD entry, endpoint pockets, In1 filled GND continuity, impedance, or route legality.

The TDM pad map rejects the earlier single 2.20-mm reservation proposal. U_TDM_XLATE.4/.5/.6/.7 are at x=175.738 and y=96.675/97.325/97.975/98.625, while U_XU.107 TDM_DATA_1V8 is (200.838, 97.800) but U_XU.20/.22/.23 are (209.900,107.662), (210.700,107.662), and (211.100,107.662). A horizontal 2.20-mm test rectangle x=190..192.2, y=96..108 had no foreign-body/pad obstruction, but it does not contact either full endpoint set and therefore proves no TDM lane. The next proposal must first choose a common translator/XU-side breakout ordering or split the data lane from the MCLK/BCLK/FSYNC group; no single four-track reservation is supported by this measurement.

The required next P1 diagnostic is a hash-bound capacity contract with endpoint pockets and native In1-GND fill checks. P1 remains false.

## TDM split-lane follow-up

The same board SHA was screened for a data-only path from U_TDM_XLATE.7 TDM_DATA_1V8 (175.738, 98.625) to U_XU.107 TDM_DATA_1V8 (200.838, 97.800), using x=176.0..200.5 and y=97.5..98.9. It intersects the intended endpoint bodies and pads, but also foreign C_XU_VDD_105, C_XU_VDD_106, C_XU_VDDIO_109 and their pads. It is not an open data corridor.

For MCLK/BCLK/FSYNC, the translator pads are U_TDM_XLATE.6/.4/.5 at (175.738,97.975)/(175.738,96.675)/(175.738,97.325); XU pads are U_XU.23/.22/.20 at (211.100,107.662)/(210.700,107.662)/(209.900,107.662). A conservative trunk box x=176.0..209.5, y=96.35..99.0 intersects C_XU_VDD_104/.105/.106/.109 and XU-side pads. The required XU fanout box x=209.4..211.6, y=99.0..107.4 intersects the U_XU body and pads 19..24/129. These are endpoint and decoupling barriers, not a route result, but they disprove both simple rectangular split-lane candidates.

The board's In1 GND zone reports `IsFilled=false`; therefore it cannot provide the required continuous native filled-reference evidence for either split candidate. A constructive next move must rearrange or separately reserve the XU south/east decoupler fanout before measuring an L-shaped TDM escape. No TDM lane is proposed from this board.
