# Crow XU USB launch geometry inventory

This is a board-pinned geometry input for later electromagnetic modeling, **not an impedance result or route acceptance**. It reads the scratch board at `/tmp/crow-usb-fcu-north-sol-20260924/04_kicad/crow_carrier.kicad_pcb`, SHA-256 `a822e3ddb355113cb8708ffdd3e3990aacc9b53bf214355d88d04a7e5a3bb435`, using native KiCad 10 `pcbnew`. The checked-in [inventory.py](inventory.py) refuses other board bytes and deterministically emits [geometry.json](geometry.json). Regenerate and validate with:

```sh
python3 research/crow_usb_launch/inventory.py /tmp/crow-usb-fcu-north-sol-20260924/04_kicad/crow_carrier.kicad_pcb > /tmp/crow-xu-launch-geometry.json
python3 research/crow_usb_launch/test_inventory.py
```

The six F.Cu segments below the nominal 0.410 mm width all leave `U_XU` pins 60/59. Their track centerlines are exact board coordinates, and their effective copper shapes are closed capsules with radius half the listed width. The complete USB_DP/USB_DN F.Cu track set is included so every width transition is explicit. The local F.Cu pad inventory includes round-rectangle size, corner radius, rotation, nearby nets, bounding boxes and mask openings. The filled In1.Cu GND plane's **all nine polygon contours (7,603 vertices)** are included, along with the F.Cu `usb_xu_launch_neck` rule area, stackup sexpr, and mask settings. These inputs retain the board's copper context without reducing it to a uniform line approximation.

| Net | 0.150 mm centerline length | 0.250 mm centerline length | Launch path to 0.410 mm |
| --- | ---: | ---: | --- |
| USB_DP | 0.585 mm (three segments) | 0.100 mm | U_XU.60 at (216.900, 95.400) → (217.125, 95.400) → (217.125, 95.240) → (217.325, 95.240) → (217.425, 95.240) |
| USB_DN | 0.425 mm (one segment) | 0.100 mm | U_XU.59 at (216.900, 95.800) → (217.325, 95.800) → (217.425, 95.800) |

The board stack specifies F.Cu 0.04064 mm, a 0.5124 mm prepreg to In1.Cu, prepreg relative permittivity 4.23666667 and loss tangent 0.02, In1.Cu 0.0152 mm, and F.Mask 0.01524 mm. It says `copper_finish "None"`. These are **design inputs**, not a measured manufactured stack. The local fill geometry is crucial: KiCad's In1.Cu reference is a filled GND zone, while a F.Cu rule area occupies the neck.

[openEMS](https://github.com/thliebig/openEMS) is a public open-source 3-D FDTD solver and its [CSXCAD model format](https://docs.openems.de/en/latest/concepts/model_io.html) can represent board geometry. Neither `openEMS`/`CSXCAD`, `gmsh`, `GetDP` nor a Python wrapper is installed here. This JSON is a backend-neutral **model input prototype**; it is not yet a runnable solver deck. A solver adapter still needs to map the KiCad pad round rectangles, track capsules, zone polygons and mask openings into 3-D conductor/dielectric solids, define launch and return ports and boundaries, mesh at the 0.150 mm neck and 0.01524 mm mask scale, and run convergence checks. The board does not supply frequency-dependent dielectric data, plating/finish, fabricated mask permittivity or package lead/connector models. Therefore no defensible impedance, eye, or S-parameter value follows from this inventory alone.
