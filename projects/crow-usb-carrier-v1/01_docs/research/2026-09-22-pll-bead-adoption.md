# PLL filter bead replacement — 2026-09-22

Replaced obsolete BKH1005LM601-T at FB_PLL with Murata BLM15AG601SN1D. The existing 0402 footprint, N0V9 to PLL_0V9 connection, local 1uF/100nF capacitors, and 100k/200k regulator divider are unchanged. Root full-source comparison found only FB_PLL manufacturer/supplier identity changed; all other expanded source bytes remain equal.

The retained manufacturer reference is JENF243A-0018AJ-01, 11 pages, at `02_parts/BLM15AG601SN1D/Murata_ENFA0018_AJ.pdf`, SHA256 `72584e2b0fad42b4fd0fc45b175151fa42acab38f373431d3f726f55317918aa`. Its exact page1 row specifies 600ohm ±25% at100MHz, 300mA rated current, maximum initial DCR0.52ohm and post-test DCR0.62ohm. Page4 gives 1.00±0.05 ×0.50±0.05 ×0.50±0.05mm. The retained AJ revision is distinguished from the later AP specification consulted online. These facts meet the XMOS published 600ohm-at100MHz and below1ohm DCR selection guidance; they do not prove equality of the entire impedance curve.

Independent SOL review accepted the final retained-primary and sourcing fixture. The owning two-source checker passes 1/1 exact selected parts for five boards using DigiKey and LCSC. Receipt: `06_build/verification/pll-bead-adoption/shopping-list.json`. LCSC C76884 catalog qualification does not promise JLC assembly allocation; the API assemblyComponentFlag is false. Incomplete Mouser lifecycle evidence was not used.

## Voltage calculation and remaining qualification

XMOS XM-014532-PC v2.0.0 gives PLL_AVDD operating limits0.855–0.945V and current0.2mA minimum/5mA typical, with no published maximum. TI TPS62825 SLVSEF9I gives PWM feedback594–606mV and up to0.05uA feedback leakage. For selected100k/200k ±0.1% resistors, conservatively allowing leakage either direction:

- Low DC source =0.594×(1+99.9/200.2)−0.05uA×99.9k =0.8854116V.
- High DC source =0.606×(1+100.1/199.8)+0.05uA×100.1k =0.9146116V.
- At5mA typical and0.62ohm post-test maximum DCR, low PLL pin DC =0.8823116V.
- A conservative high-pin DC bound retains0.9146116V: maximum DCR must not be subtracted to claim an upper bound because minimum DCR is not specified.

The typical-load lower point has27.31mV margin above the XMOS0.855V minimum before ripple. The source design's preferred0.88–0.92V window is a measured engineering target, not a proved all-condition guarantee. No divider change is justified by these calculations. A board-level measurement at U_XU pin41 must include supply/temperature corners, startup/reset, and active USB/audio operation. Ripple, transient response, layout voltage error, and the unpublished maximum PLL load remain explicitly unproven; the5mA case is not a worst-case current proof.
