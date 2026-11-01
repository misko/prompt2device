# TI clock qualification — 2026-11-01

Status: **PASS for prototype quotation; r8 prepared and independently audited.**
Not production or release-stage approval. r7 remains unchanged. User
authorized qualification and a new quote package only if it passes; no purchases.
Scope is 5 fabricated / 2 assembled carriers and 10 fabricated / 8 assembled pods.
X1 occurs once per assembled carrier: **2 installed**, zero on pods.

## Completed outcome

See [r8 instructions](../quote-draft/r8-2c8p-ti-clock/README.md),
[independent engineering review](lmk6c-engineering/review.json) and
[exact package audit](lmk6c-engineering/r8-audit.json).
New TI footprint, nearby 1uF bypass, local ground spreading and three vias are
implemented. Actual-layout model supports the two ADC loads: 26.352553 pF,
1.620671 mV sampled overshoot and 28.808318 ns minimum modeled high/low dwell.
The initial pre-layout analysis below is historical, not the final model.

Revised prototype allocations are 192 mA external3V3, 350 mA5V and 680 mA
whole-array12V. Independent review accepted their explicitly bounded source/
thermal models with first-article falsifiers; no measured guarantee is claimed.
Carrier ERC, strict DRC/refill/parity and via/land geometry checks passed under
the disclosed inherited ERC settings. Six regression tests pass, including
Gerber/drill replay, native/BOM/CPL consistency and tamper rejection.

111 payload files are bound by r8 manifest SHA256
`ee01e3f63a993af9a6088c352bc260bf9451293311b2e2aeee4dde3ee35b25a5`.
All 38 procurement identities / 524 installed parts reconcile. Pod native and
upload files, home-install list and retained THT lists are unchanged.
JLC still shows ten overseas/presale units at $4.9424 each, but **usable stock
date remains unconfirmed**. There is no zero-day availability claim or complete
PCBA quote. No JLC draft edits, purchases, reservations, messages or push.

## Exact subject and sources

- Candidate TI LMK6CE012288CDLFR, JLC C36974742, DLF 4-pin 2.5 x 2 mm.
- Original CTS CB3LV-3I-12M288000, 7 x 5 mm, retained in r7.
- [TI datasheet SNAS826G](https://www.ti.com/lit/ds/symlink/lmk6c.pdf),
  sections 6.4, 6.6, 6.7 and 9.3; [exact ordering identity](https://www.ti.com/product/LMK6C/part-details/LMK6CE012288CDLFR).
- [Pico datasheet](https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf),
  retained P031 manufacturer.pdf SHA256
  `757ff485227493b9fcc0c2c96c4dea9de020e1d8b2b11e2aa4f9ee8b25aa89eb`.
- [Richtek RT6150A/B DS6150AB-06](https://www.richtek.com/assets/product_file/RT6150A=RT6150B/DS6150AB-06.pdf).
- r7 native carrier SHA256
  `481f857c0ea682e537a0b08dd0218dea0afc397e906f927c4dcaeba5f32f7bda`;
  `r7-validation/carrier-r7.xml` confirms connectivity.
- Existing physical/model review: release historical documentation carrier
  `process/59-2026-10-23-first-run-d3-layout.md`, especially clock and power.
  Historical sources: `/home/mouse9911/gits/crow-first-run-5c10p-20261022/project/03_src/recovery/first-run-r3-engineering/`.

## Requirements and affected boundary

12.288 MHz shared clock drives both PCM1864 SCKI inputs. X1 output -> R3 68 ohm
-> R4/R5 56 ohm branches -> ADC pins 15. No Pico clock input on this net.
Pico SC0915 pin 36 supplies X1, both ADC AVDD/DVDD/IOVDD, and two 4.7k I2C
pullups. TRACO 5 V -> D2 Schottky -> Pico VSYS; original Pico D1 removed.
No separate external USB power path or new sequencing is proposed.

Retained sensitivity load is 27.3230495 pF; allocated, not measured or a TI
guaranteed receiver maximum. Clock runs on F.Cu, 32.115128409 mm with no vias.
Old model allowed simultaneous local rails 3.0..3.6 V and a single 100 mV
combined residual-reference allowance. These are engineering allocations, not
measured Pico rail extremes. They must not be silently narrowed or treated as
immutable user requirements. Prototype local-air envelope is -20..60 C.
Old planning allocations: external 3V3 140 mA, 5 V 300 mA, 12 V whole-array
630 mA. They are not manufacturer current guarantees.

## Screen so far

| Check | Evidence / disposition |
| --- | --- |
| Frequency, logic, enable | 12.288 MHz LVCMOS; pin functions preserved (1 OE, 2 GND, 3 OUT, 4 VDD). OE tied to supply. No new firmware frequency required. |
| Capacitive load | TI 30 pF below 50 MHz exceeds retained 27.3230495 pF by 2.6769505 pF. Rating screen passes, not waveform acceptance. |
| Output / timing | TI Rout 40..60 ohm; duty 45..55%. Edge max 1 ns applies at 2 pF, not at our load. New waveform calculation needed with changed native geometry. |
| Supply | TI operating 2.37..3.5 V, absolute max 3.63 V. Old 3.6 V model cannot transfer. Establish justified actual Pico supply envelope; no evidence yet of an actual overvoltage. |
| Current | TI LVCMOS table 62 mA max at 100 MHz, 71 at 156.25, 77 at 200, with stated load. These are not guaranteed 12.288 MHz maxima. Could use a clearly labelled conservative prototype allocation, but must expand the actual upstream budget. Pico recommends external load below 300 mA, conditional on VSYS and RP2040 load. |
| Ramp / restart | TI supply ramp 0.1..100 ms; startup 5 ms at approximately 200 us test ramp. Richtek soft-start typical .65 ms, maximum 1 ms at no load, not minimum or all-state module ramp guarantee. Startup/restart must be assessed; generic invalid audio during startup is not a defect. |
| Bypass | Existing C4 100 nF. TI recommends 1 uF, nearby on same side with short ground path. New local layout required. |
| Thermal | DLF published thetaJA 128.1 C/W is a reference-board metric, not guaranteed carrier thermal resistance. Increased consumption needs a bounded prototype thermal screen. |
| Jitter | Headline 500 fs maximum is at 100 MHz, not 12.288. Typical low-frequency curve exists. Do not invent exact-frequency max or turn typical performance into guarantee. |
| Fit | Different pad pattern; new footprint, source/schematic, local routing/fills, BOM/CPL, Gerbers and affected native checks required. No BOM-only adoption. |

## JLC browser follow-up and reconciliation

Completed read-only [run d5269f3a](https://agent.tinyfish.ai/runs/d5269f3a-9ea6-490f-8794-412c156dee48)
on November 1: exact TI identity, 10 displayed, MOQ 1, $4.9424/unit, generic
SMT/Economic/Standard compatibility. Two installed units cost $9.8848 before
spares, fees and tax; not a complete quote or reservation.

The browser reports **no published usable-warehouse date**. Its inference
"0 days" is rejected: retained raw fields in `LMK6C-STOCK-20261101.json`
identify overseasStockCount=10 and canPresaleNumber=10, overlapping pools, not
confirmed factory inventory. The generic three-day assembly advertisement is
not a component-arrival commitment. Lead time remains **unconfirmed**.

It also reports default order-guide attrition 4 and minimum assembly quantity
5 without a job calculation. Its concluding 5+4=9 demand is rejected: bare
boards do not consume clocks. If those defaults apply, max(2+4,5)=6, but that
is a scenario, NOT verified gross demand. Keep installed need 2 and actual
job attrition unknown. No browser draft edits, order flow, messages or commitments.

## Bounded engineering decision

### New calculation — pre-layout clock screen

Executed `lmk6c_clock_screen.py` with numpy 2.3.3 / scipy 1.16.2. Results in
`LMK6C-CLOCK-SCREEN-20261101.json`: 12 fast and 48 periodic sensitivity cases,
27.3230495 pF maximum modeled load, 0.014649 mV maximum physical-pad overshoot,
28.747485 ns minimum modeled valid high and low dwell. This is encouraging
feasibility evidence, not full qualification: retained CTS geometry, proposed
3.135..3.465 V supply sensitivity, extended 80/20% source-level model, no
post-layout extraction or guaranteed exact-frequency edge shape. Positive dwell
is not a new or claimed TI ADC pulse-width requirement. Model limitations and
source hashes are retained in the output. No CAD changed to obtain this result.

### Expanded power arithmetic under review

The old 140 mA external allocation was not a measured load. Its derivation used
82 mA **typical** combined ADC draw and margin. TI's ADC table actually lists
31 + .01 + 10 = 41.01 mA per four-channel device (48 kHz test conditions), plus
2 mA when master mode is enabled; these are not guaranteed maxima.

An explicit candidate prototype allocation is 110 mA for the ADC pair and their
digital activity, 80 mA for LMK including its load, and 2 mA for the pullups/OE:
192 mA external. Add retained 80 mA Pico allocation = 272 mA from the converter.
At 3.465 V, 70% modeled efficiency and VSYS >=4.0 V, required VSYS current is
336.6 mA; round the 5 V allocation to 350 mA. This fits TRACO capacity and
Pico's recommended external-current guidance, but does not inherit the old
300 mA upstream acceptance. With 5.16375 V steady upper module output,
70% efficiency and protected input >=9.8 V: .350*5.16375/(.70*9.8)+.400
= .66346 A. A .68 A input allocation is proposed, not accepted.

At .68 A and retained .75 V D3 drop allocation, dissipation .510 W gives
136.1 C under the retained 60 C local air +20 C neighbor +110 K/W model;
130 K/W sensitivity gives 146.3 C; 150 K/W fails at 156.5 C. These are modeled
temperatures, not measurements or actual guaranteed thermal resistances.

D2 is a separate affected boundary: native .9 x 1.2 mm lands and .4 mm traces
to vias; no 5 V/VSYS spreading zones. A large manufacturer reference-copper
theta cannot be silently applied. Its increased loss/local thermal support,
and LMK local ground/thermal layout, remain part of the qualification review.

Continue this exact candidate assessment with an independent power/clock
review required by vNext power-design. Question: can evidence support a small
local redesign under credible prototype bounds, or does a concrete unresolved
constraint prevent adoption? Missing guaranteed maxima alone must not create
a new bench-before-design gate; unsupported invented bounds cannot create a pass.
Next discriminating check is the actual source-voltage/current budget and the
source/receiver waveform model. Preserve all unrelated board acceptance.
Review deadline: 2026-11-01 18:12 UTC; no third unchanged sourcing search.
If no defensible engineering path is established, preserve r7 and report the
precise remaining check instead of issuing an upload-ready r8.
