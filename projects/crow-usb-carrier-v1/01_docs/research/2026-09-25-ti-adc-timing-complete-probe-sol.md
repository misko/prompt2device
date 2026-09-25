# TI ADC timing bundle: complete endpoint denominator and bounded obstruction

Research only. `2026-09-25-ti-adc-timing-complete-probe-sol.py` binds the exact
TI unrouted diagnostic board (`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`),
its P1 requirements (`191e5580a6ddf56bc9670aff3593c9e9a02d91e75c0c79998b500955050e82a3`),
and modular interface plan (`75c3a517cea50dd6b5745fae96b051d334debd48aac143becaca3d5fe3fc35dc`).
The matching JSON is the measured result. This does not change a source
contract, route copper, pass P1, or authorize stock.

The authoritative `adc_timing_xmos_bundle` is **14 nets and 54 terminal
members**, all 54 of which have unique F.Cu native pads on the expected net.
The three ADC→TDM nets alone have 10 terminals: both ADCs' BCLK, FSYNC, and
DOUT1 pads, plus R_BCLK.2, R_FSYNC.2, R_ADC_DATA_PD.1, and U_TDM_XLATE.10.
The four TDM→XU nets have eight terminals. The seven local-control nets add
36 terminals, including `AUDIO_EN`'s 11 terminals from x=22.7 to 202.7 mm.
The earlier seven-member shared-port result covers seven terminals across
seven nets; it leaves 47 authoritative terminal members unmodeled. Dropping
`U_ADC_B.22` makes this probe fail its source/interface parity check.

For the bounded F.Cu TDM→XU west lane `[182.475,94,199.825,100]` mm, the
unexcluded native body/pad screen reports **1.515 mm / three 0.45 mm slots**
against the four-slot, 1.8 mm demand. At x=197.7525 mm, the physical bodies
of `C_XU_VDD_104` (`y=95.515..96.485`), `C_XU_VDD_106`
(`y=97.715..98.685`), and `C_XU_VDD_113` (`y=99.915..100.885`) split the
tested y=94..100 band into free intervals 94..95.515, 96.485..97.715, and
98.685..99.915 mm. The first is the widest, at 1.515 mm. This exact band
fails the four-slot demand with the current placements. Moving its P2
capacitors or allocating a different, fully checked edge is necessary before
claiming this band's capacity; the measurement does not rule out every
possible board path.

The broad ADC→TDM box `[140,92.5,174.35,111]` mm has an optimistic raw
4.55 mm / ten-slot horizontal interval. It is not a three-slot allocation:
the two ADC BCLK/FSYNC/DOUT pads lie at x=136.25..137.25, y=94.1/106.1,
outside this box; other terminal branches and local controls are outside it
too. A complete candidate must state branch/face access for every member,
nonoverlapping reservations for all 14 nets, physical obstacle clearance,
and native GND return continuity. The exact board's In1.Cu GND zone is
unfilled; its eight F.Cu zones are rule areas. The result therefore remains
`INCOMPLETE`, even though the probe proves the 54-pad denominator and a
specific lane failure.

Run the isolated check with:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-adc-timing-complete-probe-sol.py /tmp/ti-adc-timing-complete.json
```

The script imports the local P1 capacity helper and records its SHA in the
result. Its body/pad rectangle screen is a conservative negative diagnostic;
it does not establish route topology, pad fanout, DRC, or filled-reference
continuity.
