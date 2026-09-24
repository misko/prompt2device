# P1 ADC timing native corridor screen

Research only. `adc_timing_xmos_bundle` remains `geometry: null` and `INCOMPLETE` in the source requirements. No PCB, floorplan, routing, P1 dispatch, or acceptance source was changed.

I copied the live `03_src`, `02_parts`, and netlist into `/tmp/crow-p1-adc-sol-20260924/` and generated its native board with `generate_board_generic.py`. The 569-footprint board SHA-256 is `18e55f44d5c1a8f7a7dd050e12ca451f6e08932b8c79893a0ad74e3b18be861b`. It has one valid outline, zero rule areas, 14 pre-existing thermal vias, and one In1.Cu GND zone covering `[20,20,240,140]` mm with `IsFilled=false`. The native minimum width plus clearance is 0.24 mm, below the declared 0.45 mm timing-slot pitch. No filled-reference continuity is established.

Native F.Cu endpoint positions (mm; `ref.pad/net: x,y`) are:

| Sub-lane | Endpoints |
|---|---|
| `adc_to_tdm` BCLK | `U_ADC_A.22/ADC_BCLK: 136.750,94.100`; `U_ADC_B.22: 136.750,106.100`; `R_BCLK.2: 161.710,98.500` |
| FSYNC | `U_ADC_A.23/ADC_FSYNC: 136.250,94.100`; `U_ADC_B.23: 136.250,106.100`; `R_FSYNC.2: 173.510,92.000` |
| DOUT | `U_ADC_A.21/ADC_DOUT1: 137.250,94.100`; `U_ADC_B.21: 137.250,106.100`; `R_ADC_DATA_PD.1: 167.490,86.800`; `U_TDM_XLATE.10: 181.463,98.625` |
| `tdm_to_xmos` | `U_TDM_XLATE.6/AUDIO_MCLK_1V8: 175.738,97.975` → `U_XU.23: 211.100,107.662`; `.4/TDM_BCLK_1V8: 175.738,96.675` → `U_XU.22: 210.700,107.662`; `.7/TDM_DATA_1V8: 175.738,98.625` → `U_XU.107: 200.838,97.800`; `.5/TDM_FSYNC_1V8: 175.738,97.325` → `U_XU.20: 209.900,107.662` |

Native full footprint bounding boxes needed for exact pockets are `U_ADC_A [134.175,93.175,139.825,98.825]`, `U_ADC_B [134.175,105.175,139.825,110.825]`, `R_BCLK [160.245,98.005,162.155,98.995]`, `R_FSYNC [172.045,91.505,173.955,92.495]`, `R_ADC_DATA_PD [167.045,86.305,168.955,87.295]`, `U_TDM_XLATE [174.350,94.205,182.475,99.795]`, and `U_XU [199.825,91.325,217.175,108.675]` mm. The checker requires each pocket to contain the *whole* footprint, include an exact pad/net, touch the lane without overlapping it, and have at least two named endpoint pads per net. These separated ADC branches and the two XU sides do not yet have one valid through-lane/pocket construction. A pocket list therefore cannot honestly be entered into the contract.

Using `p1_corridor_capacity.py`'s `layer_obstacles` and `connected_capacity` on the isolated native board gives these **negative, provisional F.Cu rectangles**. Endpoint refs were excluded only to expose foreign-body bottlenecks; these are not valid checker allocations and the broad rows do not encode pocket access.

| Test rectangle `[x0,y0,x1,y1]` mm | Raw connected width / slots | Required | Native obstruction |
|---|---:|---:|---|
| ADC→TDM broad `[140.000,92.500,174.350,111.000]` | 1.030 mm / 2 | 3 × 0.45 = 1.35 mm | At x≈169.333 the best opening is y=94.385..95.415, bounded by `C_ADC_OUT` and `C_FSYNC_OR`; other openings are split by `R_FSYNC_RAW_PD`, `R_XU_RST_PU`, `R_1V8_OK_TOP`, `C_U_CORE_OUT_1`, and power capacitors. The best connected bottleneck is one slot short. |
| ADC A→mid `[139.825,93.000,160.245,99.300]` | 2.425 mm / 5 | 3 | Only a local slice; it stops at `R_BCLK` and omits `R_FSYNC`, DOUT branch, ADC B access, and translator. |
| ADC B→mid `[139.825,100.000,160.245,110.825]` | 2.610 mm / 5 | 3 | Only a local slice; power components intervene afterward. |
| TDM→XU narrow `[182.475,94.000,199.825,100.000]` | 1.515 mm / 3 | 4 × 0.45 = 1.80 mm | At x≈197.753, `C_XU_VDD_104`, `_106`, `_113` divide the interval; max opening y=94.000..95.515. |
| TDM→XU broad `[182.475,94.000,199.825,108.700]` | 6.715 mm / 14 | 4 | Optimistic only: three XU pads are on the south edge at y=107.662 while data is on the west edge at x=200.838. The broad interval does not prove a four-net fanout or pad-to-lane access. |

`local_control` remains unmeasured and `INCOMPLETE`. ADC I2C pads .17/.18 sit at y=95.250/94.750 on ADC A and y=107.250/106.750 on ADC B; `U_ADC_I2C_XLATE` occupies `[164.025,80.875,169.175,84.325]` mm. Its .8/.1 ADC-side pads are at `(168.150,81.850)` / `(165.050,81.850)`, and XU I2C .93/.94 are `(203.500,92.338)` / `(203.100,92.338)`. The READY, AUDIO_EN, and DIGITAL_BAD branches need separate local windows. Their capacity and reference are unmeasured.

Next placement work must choose branch and XU fanout geometry, then bind exact ref.pad/net pockets to a fresh board hash and independently expected contract hash. `p1_corridor_capacity.py` can reject insufficient raw width but deliberately cannot prove GND pour continuity or P1 acceptance. A separate native filled-reference and pad-access receipt is still required.
