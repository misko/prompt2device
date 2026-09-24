# P1 region-trim audit

**Verdict: do not change either source region edge.** This is a read-only audit of
`/tmp/crow-usb-coarse-sol/projects/crow-usb-carrier-v1/04_kicad/crow_carrier.kicad_pcb`,
SHA-256 `18e55f44d5c1a8f7a7dd050e12ca451f6e08932b8c79893a0ad74e3b18be861b`,
against the current source `03_src/floorplan.yaml`. It is not a P1 acceptance,
route, return, or placement claim.

The proposed `xmos_core` south edge at `y=112` would remove the current overlap
with `clock_flash_debug` by cutting these `xmos_core` anchor-footprint body
bboxes (board mm):

| Ref | Native body bbox `[x0,y0,x1,y1]` |
| --- | --- |
| `C_XU_VDDIO_10` | `[199.909,108.915,207.091,112.862]` |
| `C_XU_VDD_11` | `[198.616,108.915,208.435,114.861]` |
| `C_XU_USB18` | `[203.651,110.315,209.549,114.262]` |
| `C_XU_VDDIO_17` | `[207.409,108.915,214.591,112.862]` |
| `C_XU_VDD_14` | `[206.065,108.915,214.884,113.861]` |

Those are source anchors; `C_XU_VDD_14` and `C_XU_VDDIO_17` are also named in
`rules/xu_local_power_launches.yaml`. A cell edge through them would make their
unproved local supply/return and escape geometry appear to be a cross-block
handoff rather than P2 work.

The proposed `audio_clock_tdm` west edge at `x=145` would similarly cut the
current `adc_reference` / channel-6 cluster. Measured native footprint bboxes
that cross that line include:

| Owner | Ref | Native body bbox `[x0,y0,x1,y1]` |
| --- | --- | --- |
| `adc_reference` | `U_ADC_A` | `[126.668,93.175,147.332,100.162]` |
| `adc_reference` | `U_ADC_B` | `[126.668,105.175,147.332,114.049]` |
| `adc_reference` | `C_ADC_A_IOVDD_100N` | `[137.315,86.038,148.684,92.608]` |
| `adc_reference` | `C_ADC_A_IOVDD_10U` | `[138.722,91.256,149.899,99.662]` |
| `adc_reference` | `C_ADC_B_IOVDD_100N` | `[138.742,104.165,149.517,112.061]` |
| `adc_reference` | `C_ADC_B_IOVDD_10U` | `[139.245,99.220,152.002,106.980]` |
| `analog_ch6` | `C_ADC_AC6N2` | `[138.039,67.375,145.275,75.517]` |
| `analog_ch6` | `C_ADC_CM6N` | `[141.023,66.015,146.977,78.062]` |
| `analog_ch6` | `C_ISO6` | `[141.965,71.415,146.835,79.462]` |

No current `p1_fixed_refs` footprint intersects either proposed strip, and no
tracks do. The board's one GND zone spans both strips but is saved unfilled, so
it proves neither a conflict-free route nor a continuous return. No edge
connector is affected by either trim.

Keep the current overlapping architectural regions until P2 local placement
closes the affected cells. If non-overlap is later needed, use one of these
source-owned forms instead of a full straight trim: a **staggered boundary**
whose segments avoid every retained footprint envelope, with a named P2
pad-to-face obligation at each segment; or an explicit **shared transition
zone** that remains owned by `board_integration`, lists the affected refs and
nets, forbids P1 route/access claims, and is discharged only by P2 proximity,
pad-access, and return proof. Either form must retain exact modular endpoint
ownership and native pad/net parity. It cannot turn XU decoupler launches,
ADC decoupling, or channel-6 local access into accepted P1 corridors.
