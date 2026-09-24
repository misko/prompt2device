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
