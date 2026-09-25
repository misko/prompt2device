# XTAL physical-cell source packet — declaration valid, allocation fails

**Research disposition: FAIL closed; no P1 or P2 admission.** This isolated
packet combines the retained-cap XTAL handoff with the shifted QSPI corridor
using the optional `physical_cells` checker extension in commit `291ebf80`.
Both corridor declarations pass native source validation. The whole 59-net
coarse contract still fails at the unchanged JTAG witness `U_XU.51`, which
bridges too far across its source region. Because allocation stops there, the
global exact-endpoint check reports both QSPI and XTAL
`integration affected endpoint/layer denominator mismatch`. Those two errors
are consequences of the JTAG abort, not missing QSPI or XTAL declaration pads.
The canonical source, board, task state, and P1 attempt count are unchanged.

The packet pins retained-cap geometric candidate `988a43c1` and its board
SHA-256 `fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27`.
`C_XU_VDDIO_35` remains at `[218.0,105.8,90]` with native envelope
`[217.495,104.845,218.505,106.755]` mm. The XTAL handoff is
`[217.2,107,218.95,118.5]`; the disjoint QSPI region and its XU-facing edge
begin at x=219.2. The shifted QSPI face has 3.6 mm raw span against 2.7 mm
declared demand. Raw span is not effective routing capacity.

The source declares three physical cells under the **same** modular owner
`xmos_core`:

| Cell | Rectangle (mm) | Native refs |
| --- | --- | ---: |
| `xmos_core` | `[190,84,217.2,110.5]` | 19, including `U_XU` |
| `xmos_core_east` | `[217.2,84,224,107]` | 10, including retained cap and `FB_PLL` |
| `xmos_core_qspi_south` | `[218.95,107,232,110.5]` | 0; declared transit cell |

All 29 native XU-owned refs are assigned exactly once; their full body,
courtyard and pad envelopes fit their cells. The east cell is edge-connected
to the main cell and the south transit cell. Each cell is disjoint from the
XTAL and QSPI integration corridors and from foreign source regions. Native
inspection finds no footprint/courtyard in either corridor. The cell IDs bind
the corridor faces and witnesses; they never become endpoint owners or a
shared-zone alias.

The exact XTAL endpoint set is `U_XU.34`, `R_XTAL_DRIVE.1`, `R_XTAL_FB.1`
on `XTAL_IN`, and `U_XU.33`, `C_XTAL_OUT.1`, `R_XTAL_FB.2`, `Y_XU.3` on
`XTAL_OUT`. The two XU pads remain owned by `xmos_core`; the five oscillator
endpoints remain owned by `clock_flash_debug`. Native validation checks all
seven exact ref.pad/net witnesses, their cell faces, and `P2_REQUIRED`
pad-to-face obligations. The QSPI declaration likewise checks its exact 13
endpoints and obligations. Both carry a separate `In1.Cu` filled GND-return
obligation. The XTAL main-cell face is a 0.004 mm declaration strip between
the native U_XU envelope ending at x=217.195 and the x=217.2 cell edge; it
establishes no copper clearance or effective lane width. The retained-cap
dogleg screen is separately recorded in `../xtal_south_cap_handoff.json`.

The complete checker result is:

| Allocation | Status | First reason |
| --- | --- | --- |
| `usb_device_pair` | INCOMPLETE | `U_USB_ESD.1` still needs a virtual P2 face |
| `xmos_service_escape` | FAIL | `U_XU.51` witness is a nonlocal bridge |
| `adc_timing_xmos_bundle` | INCOMPLETE | `U_ADC_A.22` still needs a virtual P2 face |
| `adc_analog_boundary` | INCOMPLETE | `C_ADC_AC1N1.2` witness is a nonlocal bridge |
| `power_boundary_windows` | INCOMPLETE | `C_ADC_3V3X_OK_VDD.2` witness is a nonlocal bridge |

The next isolated packet must repair JTAG/reset handoffs while retaining this
exact XTAL/QSPI source and then rerun whole allocation; these rows are
diagnostics, not accepted child work. Actual pad escapes, copper, effective
capacity, crystal electrical performance, filled reference, DRC and routing
remain open.

Run from this worktree root with KiCad 10 `pcbnew` and PyYAML:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/xu_service_variant/p1_xtal_packet/build_packet.py
```

The builder checks all parent input hashes, regenerates the isolated source,
floorplan and coarse contract, validates exact native endpoints, and demands
the same whole-contract failure. Its machine-readable result is
`validation.json`.

| Artifact | SHA-256 |
| --- | --- |
| `p1_source_xtal.yaml` | `a159d4ac25f8c13a81ea79e76ad5eac023349a169119feadf7ff04d8e7c15c36` |
| `floorplan_xtal.yaml` | `41632157eda6c65721d33d8aa04c6295569f1a8d8d926de25c8cf95b465e890e` |
| `coarse_contract_xtal.json` | `99bb672774e24cc0e1fbc443a9de727304b812ba3168dcdfbce00e4959d2702c` |
| modular plan | `7201aa55cffefca99f9f27e92711cbbcf28387432523a8c960b5cd71e973170e` |

The QSPI parent source, floorplan, contract, aliases and native board digests
are pinned in `build_packet.py` and in `validation.json`. No route, filled
reference, P1 acceptance or P2 completion is claimed.
