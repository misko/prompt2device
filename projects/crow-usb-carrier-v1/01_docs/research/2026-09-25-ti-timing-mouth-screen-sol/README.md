# Bounded native TDM physical-mouth search — 2026-09-25

**Stop at coupled P2 placement.** `build_screen.py` reopens the exact 15-part candidate board from the unified packet (`d0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7`), its P1 source and floorplan by pinned SHA-256, verifies all eight exact F.Cu pad/net identities, and writes `result.json`. It does not edit a board, add tracks, refill copper, or dispatch P1. The source has exactly 27 P1-fixed refs; none intersects the three searched mouths. U_TDM_XLATE, U_XU, and the local bypass/translator neighbors are P2-movable in that source, but no move receives capacity credit here.

The current floorplan regions meet at x=190: `audio_clock_tdm` `[145,72,190,99.84]` and `xmos_core` `[190,84,217.2,110.5]`. The exact four paths run from U_TDM_XLATE.6/.4/.7/.5 at `(175.3375,95.875)/(175.3375,94.575)/(175.3375,96.525)/(175.3375,95.225)` to U_XU.23/.22/.107/.20 at `(211.1,107.6625)/(210.7,107.6625)/(200.8375,97.8)/(209.9,107.6625)`, respectively. The data pin leaves the XU west edge; the other three leave its south edge. The translator pads lie on its west side. Therefore one straight four-track body-to-body mouth is not supplied by these endpoints.

The replay scans native F.CrtYd/body and F.Cu pad bounding envelopes in three deliberately bounded rectangles, retaining all placed obstacles. It uses the source rough 0.45-mm slot pitch to screen full-envelope apertures; it does not apply effective per-net rules or prove copper access. Courtyards conservatively reserve assembly space, so these widths do not bound every possible copper escape. Intersecting F.Cu rule areas and source regions are inventoried separately.

| Mouth window (board mm) | Full-envelope connected width | Rough slots / need | Decisive current obstacle |
| --- | ---: | ---: | --- |
| Translator west `[172.5,94.2,174.305,96.8]` | 1.295 mm | 2 / 4 | C_ADC_I2C_B courtyard and pads split the four-pad exit span |
| XU west DATA `[197.5,97.695,199.805,98.705]` | 0.000 mm | 0 / 1 | C_XU_VDD_106 courtyard and pads close the direct west aperture |
| XU south MCLK/BCLK/FSYNC `[209.5,108.7,212.5,109.9]` | 0.545 mm | 1 / 3 | C_XU_VDDIO_17 courtyard and pads split the three-pad exit span |

The XU south screen bounds the current common mouth; separate traces might turn within the package escape field, but that requires exact pad-access and clearance work. The XU west screen bounds the direct DATA mouth; a turn around C106 or a layer transition is not established by these rectangles. No F.Cu native rule area intersects the three screens. The saved In1.Cu GND zone is **unfilled**, so no continuous return can be credited even if a later aperture opens.

This stop reuses the earlier [XU fanout probe](../2026-09-24-xu-fanout-isolated-probe-sol.md) and [split-lane rejection](../2026-09-24-p1-isolated-native-sublane-measurement-terra.md). That probe moved C_XU_VDD_106 and C_XU_VDDIO_17 to open separate diagnostic stubs, but their pad-1-to-owning-XU-pad distances grew from **2.8328 to 3.3158 mm** and **2.5162 to 3.9814 mm** respectively; its MCLK exit remained unproved and its In1.Cu samples did not establish continuous return. The current board's same native distances were recomputed here as 2.8328 and 2.5162 mm. Repeating those moves without a coupled bypass/supply-return review would trade one blocked mouth for unqualified local power. The prior XU rotation, simple split rectangle, and one-edge remap diagnostics also do not supply this board with four valid mouths.

A constructive P2 continuation must jointly place translator neighbor C_ADC_I2C_B, west-side C_XU_VDD_106 (and its C105/C104/109 bypass context), and south-side C_XU_VDDIO_17/C_XU_VDD_14 while preserving their owning-pin distances and local return. Then regenerate one source-bound native board, measure exact pad entrances, full courtyards, effective F.Cu rules, and a filled In1.Cu reference along any staged path. Only after that may a physical two-terminal corridor be proposed. This packet makes no claim that arbitrary multilayer routing is impossible; it rules out the three direct full-envelope mouths on the unchanged candidate and stops before unsupported placement changes or P1 credit.

Reproduce from repository root:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-timing-mouth-screen-sol/build_screen.py
```
