# Proposed coarse ADC/TDM P1 allocation

**Proposal only; current source remains `INCOMPLETE` with `geometry: null`.** This is an instance of the `boundary_witnesses`/reservation-bbox split in the [P1/P2 circularity audit](2026-09-24-p1-p2-stage-circularity-audit-terra.md), not a schema-1 `p1_corridor_capacity.py` contract, route, P1 receipt, or P2 placement approval. It retains the complete modular endpoint lists for later P2/P3 completion. The current native source board is SHA-256 `18e55f44d5c1a8f7a7dd050e12ca451f6e08932b8c79893a0ad74e3b18be861b`; source floorplan SHA-256 is `4a457c731c204084a83aa817a29ca8fc8acc07097723adefedc296eb4db37b98`.

The coarse allocation owns exactly these **14 nets**. Each listed `ref.pad` is confirmed F.Cu on the named net on that board. An owner-cell face bbox is a future interface datum; the listed pads are native witness identities near or inside their cells, not fabricated pad-to-face access proof.

| Nets | Provisional cross-block witness identities | Proposed face / reservation |
|---|---|---|
| `ADC_BCLK`, `ADC_FSYNC`, `ADC_DOUT1` | `U_ADC_A.22/.23/.21`, `U_ADC_B.22/.23/.21` → `R_BCLK.2`, `R_FSYNC.2`, `U_TDM_XLATE.10` respectively; `R_ADC_DATA_PD.1` is a DOUT local branch deferred to P2/P3 | ADC-A east face x=139.825, y=93.175..98.825; ADC-B east face x=139.825, y=105.175..110.825; clock/TDM entry face x≈174.350, y=91.505..99.795. Two ADC branch reservations join the broad ADC→TDM envelope below. |
| `AUDIO_MCLK_1V8`, `TDM_BCLK_1V8`, `TDM_DATA_1V8`, `TDM_FSYNC_1V8` | `U_TDM_XLATE.6/.4/.7/.5` → `U_XU.23/.22/.107/.20` respectively | Translator west face x=174.350, y=94.205..99.795; XU west face x=199.825, y=91.325..108.675; XU south face y=108.675, x=199.825..217.175. DATA is west-edge; the other three are south-edge exits. |
| `ADC_I2C_SCL`, `ADC_I2C_SDA` | `U_ADC_A.17/.18`, `U_ADC_B.17/.18` → `U_ADC_I2C_XLATE.8/.1` | ADC east faces as above; bridge cell `[164.025,80.875,169.175,84.325]`. Local branches/window unmeasured. |
| `ADC_READY` | `U_ADC_READY.4` → `U_ADC_I2C_XLATE.6` | ADC control cell near `(98.400,100.150)` to bridge cell near `(168.150,82.850)`; local window unmeasured. |
| `AUDIO_EN` | `U_AUDIO.6` → `U_ISO1..8.2` (all eight analog block faces, not just the two extremes) | Distributed quiet-power-to-analog enable boundary; eight separate local crossings unmeasured. |
| `XU_I2C_SCL_1V8`, `XU_I2C_SDA_1V8` | `U_ADC_I2C_XLATE.5/.4` → `U_XU.93/.94` | Bridge cell to XU north face y=91.325, x=202.975..203.625; local window unmeasured. |
| `ADC_DIGITAL_BAD` | `U_ADC_DIGITAL_BAD.4` → `U_ADC_CLOCK_OK.1` | ADC status cell near `(111.600,100.150)` to timing cell near `(159.400,83.550)`; local window unmeasured. |

Suggested `coarse_geometry.reservations` on F.Cu, all with required In1.Cu GND-reference **allocation** and `local_endpoint_completion: P2_P3_REQUIRED`:

| Reservation bbox `[x0,y0,x1,y1]` mm | Assigned nets / demand | Current native raw capacity | Coarse disposition |
|---|---|---|---|
| ADC-A branch `[139.825,93.000,160.245,99.300]` | ADC BCLK/FSYNC/DOUT; 3 × 0.45 = 1.35 mm | 2.425 mm / 5 optimistic slots | Nonzero branch envelope, but does not reach clock/TDM endpoints or ADC B. |
| ADC-B branch `[139.825,100.000,160.245,110.825]` | Same 3 nets; 3 slots | 2.610 mm / 5 slots | Nonzero branch envelope; downstream join unproved. |
| ADC common `[140.000,92.500,174.350,111.000]` | Same 3 nets; 3 slots | **1.030 mm / 2 slots: FAIL** | Its x≈169.333 bottleneck rejects the current placement. The broad bbox is a diagnostic envelope, not three simultaneous channels. |
| TDM west approach `[182.475,94.000,199.825,100.000]` | Four TDM nets; 4 × 0.45 = 1.80 mm | **1.515 mm / 3 slots: FAIL** | Current source cannot reserve this simple four-net strip. The separate three-post-anchor isolated test raised raw width to 2.615 mm / 5 slots, but those poses are not source and still lack the south-edge XU fanout. |
| ADC control, enable, XU I2C, status | Seven named nets above; at least seven independent signal obligations, with shared edges to be determined | Unmeasured | Keep per-net witness coverage; no zero-demand omission or invented shared 7-slot trunk. |

P2 may move the floating/localized `R_ADC_OK_BOT`, `C_FSYNC_OR`, `C_ADC_I2C_B`, `C_XLATE_A`, `Y_AUDIO`, and the ADC/clock/translator cells within reviewed boundaries, subject to their own analog, clock, and decoupling checks. `C_XU_VDD_104/_105/_106/_113` and `C_XU_VDDIO_109` are source-anchored but explicitly provisional XU decoupling poses; a P2 owner may propose a different pose only with renewed supply-fanout and return proof. The isolated three-move screen moved `C_FSYNC_OR`, `C_XU_VDD_104`, and `C_XU_VDD_106`, clearing the TDM raw screen but leaving ADC at 1.105 mm / 2 slots. In that moved board, `R_ADC_OK_BOT` splits the central opening at x≈162.890; its placement and the adjacent `Y_AUDIO`/`C_ADC_I2C_B` gap need a new joint window. Connector/board-edge/hold-bank mechanical anchors and the currently fixed `U_XU`, USB, and PLL block poses are outside this local move proposal; changing their face or an accepted coarse envelope backtracks to P1.

No current reservation earns a P1 coarse PASS: two common edges are below raw demand; face-to-pad access, control windows, effective rule-expanded capacity, shared allocation contention, and filled GND continuity are absent. The native unfilled source board has one In1.Cu GND zone with `IsFilled=false`. A successor coarse checker should record these 14-net witnesses and nonzero demands but return `INCOMPLETE`/the measured `FAIL` edges, `routing_realized=false`, and `p1_accepted=false` until the source geometry and independent evidence exist.
