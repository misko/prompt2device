# TI lower TDM/XU neck source probe

Research only. `build_probe.py` makes an isolated schema-2 packet from the
exact TI board `8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`.
It changes no canonical source or board, preserves all 27 P1-fixed references,
and leaves `p1_accepted: false`.

The packet changes `audio_clock_tdm` only to x2=188 and declares the empty
source-owned integration cell `[188,94,190,99.84]`. Its eight affected endpoint
records are the exact pairs for `AUDIO_MCLK_1V8`, `TDM_BCLK_1V8`,
`TDM_DATA_1V8`, and `TDM_FSYNC_1V8`:

* audio: `U_TDM_XLATE.6/.4/.7/.5`;
* XU: `U_XU.23/.22/.107/.20`.

All eight have explicit `P2_REQUIRED` pad-to-face debt and the cell has the
required `In1.Cu` continuous-filled-GND return obligation. The existing XU
physical-cell partition remains complete; the XU face names `xmos_core`.

The integration-cell validator accepts this body-plus-courtyard ownership
model. It does not make the neck a route or capacity credit. The stricter
`GetBoundingBox(True, True)` screen in the companion joint map still finds
`C_XU_VDD_105` `[188.579999,96.538400,198.934524,99.108250]` and
`C_XU_VDDIO_109` `[187.222857,98.738400,198.934524,101.308250]` in the
neck, leaving 2.538400 mm/five connected 0.45-mm slots. A future source model
must state which full-footprint definition governs the integration-cell
emptiness test; this packet claims neither a clear empty corridor nor routing.

The full checker exits 1 as required: the deliberately isolated four-net
slice omits boundary witnesses for the other ten nets in
`adc_timing_xmos_bundle`, so it reports `missing per-net boundary witness`.
It earns no partial allocation result. Channel 7 remains covered by the
reduced audio region (x=153..188) and channel 8 remains covered by audio/XU;
no ADC local portals were added or credited.

Run:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-tdm-xu-lower-neck-source-probe-terra/build_probe.py
```
