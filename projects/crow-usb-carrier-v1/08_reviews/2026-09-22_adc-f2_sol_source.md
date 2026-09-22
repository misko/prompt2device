# Independent CS5308P DS1314F2 source review — 2026-09-22

**Verdict: ACCEPT**

Reviewed isolated commit: `3d54698cf169a53d2d90327d7dc11234cf3ca479`

The candidate correctly makes Cirrus Logic DS1314F2 the current CS5308P component authority while retaining DS1314F1 as historical/supporting evidence. The F2 PDF is an exact primary manufacturer document: SHA-256 `410a8b060d8daabbf7d4a541544049b6bc598a4ddcbd50aeaf50861e2069b6e4`; PDF metadata identifies Cirrus Logic, title `CS5308P_DS1314F2`, 94 pages, and January 2026. The retained F1 PDF remains byte-identical at SHA-256 `6ca42cc09ac47ebdacacaee435f05e3f9c34b83d5692e52a2d8a26533e810e57`, preserving prior moisture/search and design-research evidence without competing with F2 as the current `part.yaml` authority.

The source pin-name update preserves the exact electrical connections. Pin 36 is `SPI_SCK/HIZ_SEL` and remains connected to GND, selecting `HIZ_SEL=0`, mid input impedance in hardware mode. Pin 38 is `SPI_CS/BCLK_INV` and remains connected to `3V3_ADC`, selecting `BCLK_INV=1`, noninverted BCLK. The existing straps select:

- CONFIG1: 4.7 kΩ pull-down — ASP Secondary Mode, 44.1/48 kHz selection.
- CONFIG2: 0 Ω pull-up — TDM minimum-time-slot mode.
- CONFIG4: 4.7 kΩ pull-up — MCLK = 512 fs(base), PLL bypass, default channel order.

For this configuration, DS1314F2 §4.4.3 requires the active BCLK edge to align with the falling MCLK edge. Minimum-slot TDM with noninverted BCLK uses the falling BCLK edge as the active DOUT-launching edge, so the candidate correctly records that falling BCLK should align with falling MCLK at the ADC.

The hardware/software interface wording assigns firmware only the configuration of the clock-generation path. It leaves buffer and route timing realization to hardware and requires first-article confirmation at the ADC pins. A shared frequency source alone is explicitly insufficient. This does not claim that firmware directly controls physical waveform phase or that the requirement has already been measured.

Focused validation evidence supplied for the source candidate reports 489 source components, 85 exact MPNs, 1,619 ports, 1,490 traces, and zero source-render errors. `git diff --check` passed and the isolated worktree was clean. No full build, PCB generation, routing, or conductor work was performed for this review.

Physical qualification remains owed: measure MCLK and BCLK concurrently at the ADC pins after the real buffers and routes, confirm the required edge relationship across applicable operating conditions, and retain the first-article waveform and timing-budget evidence. This acceptance covers the source authority, pin names, strap interpretation, and stated ownership boundary only.
