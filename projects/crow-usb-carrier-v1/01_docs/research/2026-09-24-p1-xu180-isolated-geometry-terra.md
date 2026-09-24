# Isolated 180-degree XU block geometry

The variant exists only at `/tmp/crow-p1-xu180-rigid-terra/projects/crow-usb-carrier-v1`. Its copied `floorplan.yaml` changed U_XU from `(208.5,100.0,90)` to `(208.5,100.0,180)` and rigidly rotated every `C_XU_*` coordinate and rotation +90 degrees around `(208.5,100.0)`. It was generated with `generate_board_generic.py <copied floorplan> --netlist <copied netlist> -o <copied 04_kicad board>`.

The isolated board SHA-256 is `24ade4c0b9b5c59783f41fd0ee3deb12a645bc3509c5296f4b5664e06d0562d0`; the generator saved 569 footprints without a P-COLLIDE failure. U_USB_ESD.1/.2 remained `(216.650,36.425)`/`(217.350,36.425)`. U_XU.60/.59 became `(203.900,92.338)`/`(204.300,92.338)`, while TDM MCLK/BCLK/FSYNC U_XU.23/.22/.20 became `(216.162,97.400)/(216.162,97.800)/(216.162,98.600)` and TDM_DATA U_XU.107 became `(206.300,107.662)`.

This is a geometry-only rejection: rotating the USB pins away from the ESD strip worsens the USB endpoint geometry. No native DRC, P-ADJ, reference-plane, or P1 acceptance is claimed.
