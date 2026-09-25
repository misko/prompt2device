# XMOS oscillator source-owned handoff search — conditional repair

This research-only result is pinned to the isolated QSPI-gap board. It does
not modify the canonical floorplan, modular plan, board, route, P1 state, or
acceptance.

The exact denominator is seven native pads: `U_XU.34`, `R_XTAL_DRIVE.1`, and
`R_XTAL_FB.1` on `XTAL_IN`; `U_XU.33`, `C_XTAL_OUT.1`, `R_XTAL_FB.2`, and
`Y_XU.3` on `XTAL_OUT`. The board SHA-256 is
`fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27`; the
QSPI-gap floorplan and source-packet hashes are checked by the accompanying
script.

There is no legal source-local handoff with the pinned regions. The current
`board_integration_qspi [199.8,110.5,223.2,118.5]` covers every north/south
path between the XU's east-facing oscillator pads and the lower
`clock_flash_debug` region. The native F/B-courtyard-aware envelope of
`C_XU_VDDIO_35 [217.495,104.845,218.505,106.755]` also blocks the immediate
east exit from `U_XU.34 [215.425,105.675,216.900,105.925]` and
`U_XU.33 [215.425,106.075,216.900,106.325]`.

The smallest coherent source change has two parts:

1. Move only the QSPI integration region's left edge to its existing south
   face: `board_integration_qspi [219.0,110.5,223.2,118.5]`. Its raw width is
   still 4.2 mm, above the declared 2.7 mm six-lane demand, and the pinned
   native board has no body, courtyard, pad, copper, or fixed reference inside
   the shifted rectangle.
2. Move the non-fixed `C_XU_VDDIO_35` to a newly proved local decoupling pose.
   Then split the present `xmos_core` rectangle into west/east source regions
   and declare a `clock_oscillator_handoff [217.2,105.5,218.95,118.5]` owned
   by the clock/oscillator source. It touches the XU owner at an east-face
   boundary and the lower `clock_flash_debug` region at y=118.5, without
   positive-area overlap with the shifted QSPI region.

This is only a source-geometry repair candidate. It leaves the actual crystal,
feedback, drive, and capacitor placements unapproved. In particular, the two
XTAL lanes still require P2 pad escape/clearance and P3 electrical validation;
their `In1.Cu` GND reference remains a debt requiring native filled-plane
continuity evidence. The candidate is not a route, a P1 admission, or an
acceptance claim.

Reproduce from the repository root with KiCad 10 `pcbnew` and PyYAML:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/xu_service_variant/xtal_region_handoff_search.py
```

The generated, hash-pinned receipt is
[xtal_region_handoff_search.json](xtal_region_handoff_search.json).
