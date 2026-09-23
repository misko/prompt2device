# D5 bounded OPA and XU316 crystal source selection — 2026-09-23

This selection covers U_AFE1..8 and Y_XU only. It changes the exact source
identities and the Y_XU land. The commission hold remains in force because
other non-through-hole sources and the ADC architecture are unresolved. JLC
catalog observations are time-bound, not uploader allocation or PCBA signoff.

| Function | Prior | Selected | Five-board demand | Direct JLC observation |
|---|---|---|---:|---:|
| Eight dual AFEs | OPA2320AID / C2861439 | OPA2320AIDR / C2863402 | 40 | 582 at 2026-09-23 02:51 UTC |
| XU316 24 MHz crystal | Epson FA-238 24.0000MD30X-W5 / C2650433 | YXC X322524MOB4SI / C70590 | 5 | 66,719 at 2026-09-23 02:50 UTC |

The direct JLC endpoint responses are retained in
`/tmp/crow-jlc-adc-20260923/raw/C2863402.json` and `C70590.json`.
[JLC C2863402](https://jlcpcb.com/partdetail/TexasInstruments-OPA2320AIDR/C2863402)
and [JLC C70590](https://jlcpcb.com/partdetail/YangxingTech-X322524MOB4SI/C70590)
identify SMT assembly catalog entries. Recheck exact BOM matching, population
eligibility, purchase quantity, and allocation in the uploader before order.

[TI's OPA2320 ordering table](https://www.ti.com/lit/gpn/OPA2320)
identifies OPA2320AID as SOIC(D)-8, tube of 75 and OPA2320AIDR as the same
SOIC(D)-8 silicon, reel of 2500. Both share the top-view pin table in retained
SBOS513F: 1 OUTA, 2 -INA, 3 +INA, 4 V-, 5 +INB, 6 -INB, 7 OUTB, 8 V+.
The `soic8` source land and all AFE connectivity remain unchanged. The new
exact dossier carries the same primary datasheet and layout obligations;
the original dossier is retained as a historical source record.

The [YXC YSX321SL manufacturer sheet](https://www.yxc.hk/uploadfiles/2021/11/YSX321SL.pdf)
and the retained [Epson FA-238 sheet](../../02_parts/FA-238-24.0000MD30X-W5/FA-238-24MHz.pdf)
were compared by drawing. Both have 3.2 x 2.5 mm bodies, diagonal crystal
terminals 1/3, case terminals 2/4, 24 MHz fundamental and 12 pF CL.
The YXC 24 MHz series ESR maximum is 50 ohm versus Epson 60 ohm.
YXC's exact catalog code is ±10 ppm initial, ±20 ppm stability over -40..85 C;
Epson's retained exact sheet gives ±20 ppm initial and ±20 ppm stability over
-30..80 C. The YXC sheet's recommended land is 1.4 x 1.2 mm at 2.2 x 1.7 mm
centers. The Epson recommendation is 1.4 x 1.2 mm at 2.2 x 1.6 mm centers;
the old native land used 1.2 x 1.1 mm pads at 2.4 x 1.9 mm centers. The
new TSX and native footprint use the YXC recommendation. Pad numbering
preserves the existing Y_XU nets: 1 XTAL_IN_R, 3 XTAL_OUT, 2/4 GND.
YXC's top view is upper 4/3 and lower 1/2. In the native KiCad footprint,
positive Y is down, so pads 1/2 are at Y=+0.85 mm and pads 4/3 at
Y=-0.85 mm. tscircuit is Y-up; its authored pad coordinates negate those
Y values, as the owning `circuit_json_to_kicad_pcb.py` converter does.
`03_src/tests/test_yxc_crystal_land.py` checks both coordinate sets and
the source net assignment against the manufacturer's drawing.

The current source has 22 pF from each crystal node to ground. For equal
capacitors, effective differential load is 22×22/(22+22) = 11 pF plus pin,
trace and package stray. Approximately 1 pF stray gives YXC's rated 12 pF.
The [XMOS XU316 hardware review](2026-09-22-xu316-hardware.md) records XMOS's
22 pF example for the 12 pF FA-238, so the selected part's rated load matches
that network. Actual parasitic capacitance is not yet measured or extracted;
first-article oscillator start, frequency over temperature, and drive level
remain required. The source selection does not claim USB clock measurement.
