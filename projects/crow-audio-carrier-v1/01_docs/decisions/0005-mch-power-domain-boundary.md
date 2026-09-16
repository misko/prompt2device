# ADR-0005 — MCHStreamer independent-power boundary topology

Status: accepted for first-article source; physical and powered-state evidence OWED.

## Context

The MCHStreamer is normally USB-powered by the Raspberry Pi and can be on while the carrier is off, or off while the carrier is on. A series resistor on ADC DOUT cannot prevent back-power and an undriven clock-buffer input can create false clocks. The official miniDSP manual fixes TDM8 J1 as pins 2 input, 9 MCLK, 10 BCLK, 11 GND and 12 FSYNC; all are 3.3 V logic, and the TDM input is always treated as 24-bit. It also fixes J3 pin 1 GND and pin 2 as a 3.3 V output rated up to 200 mA.

## Decision

Use two distinct 2x6, 2.00 mm carrier headers and two selected Samtec
`TCSD-06-D-04.50-01` double-ended socket cables instead of anonymous kit
cables. J10 mates to MCHStreamer J1 for TDM/clocks. J11 mates to J3 and uses
only pin 1 GND and pin 2 `MCH_3V3_SENSE`; the other ten pins are no-connects.
J3 pin 2 is presence sense only through 300 Ω/10 kΩ, about 0.320 mA nominal,
and never powers the carrier rail.

SN74LVC3G34DCUR buffers the three incoming clocks with Ioff protection and
10 kΩ input pull-downs. ADC `TDM_RAW` passes through SN74LVC1G125DBVR,
also selected for Ioff. Its active-low OE is now driven push-pull by
`U_OE` Nexperia `74LVC1G14GV,125` (C131093), powered by `3V3_ADC` with
its own `C_OE` 100 nF bypass. J3 presence high produces OE low; absence
is pulled low at the Schmitt input and produces OE high. Pin1 is NC.
A 33 Ω series resistor remains damping after the TDM buffer, not a
power-boundary claim. The former Q_TDM_EN and R_TDM_OE_PU are removed.

## 2026-09-07 D-BACK — slow OE input corrected

The earlier pull-up/NMOS topology was not defensible: SCES223U p5 requires
10 ns/V maximum input transition time at local 3.3 V, including OE. Its
4 pF input capacitance is typical, not a maximum suitable for an RC proof.
The exact protected 2N7002K also has no guaranteed low-VDS on-resistance
at the available gate voltage. A higher DC gate voltage did not resolve
either source defect.

Nexperia 74LVC1G14 Rev19 p1 explicitly accepts unlimited input rise/fall
times; p5 has no input-transition ceiling. Its p5 full-temperature input
leakage limit is 1 µA including VCC=0, and Ioff is 2 µA. At 100 µA load
the output limits are VCC minus 0.1 V high and 0.1 V low. The screen budgets
25 µA on OE (5 µA receiver plus20 µA board allocation), giving 2.9 V high
at a conservative local3.0 V floor. This is an ordinary push-pull logic
connection, not an RC timing calculation. Keep it short and without a
shunt capacitor or external cable. Propagation delay is not relabeled an
output-slew guarantee.

The retained300 Ω/10 kΩ divider screens at0.206 V absent and2.901 V
present under the deliberately retained20 µA input/cable allocation.
The0.4 V low/2.8 V high targets cover the published discrete threshold
table extrema, but are engineering acceptance targets, not invented
interpolated manufacturer guarantees between supply-table points. Confirm
settled thresholds and actual OE edges in first article. Arbitrary slow
presence input is now intentionally handled by a genuine Schmitt input;
glitch-free brownout or hot insertion is not claimed.

The exact local Rev19 primary PDF was obtained through the ordinary LCSC
datasheet link after direct Nexperia download returned403. Browser-reopened
official Rev19.1 was also checked, but the stored bytes are honestly Rev19
and hash-bound in the dossier and `check_clock_defaults.py`.

## Earlier 2026-09-07 correction — leakage and loading (historical)

The following records the preceding DC-only repair. Its MOSFET/OE-pull
topology and corresponding two OE rows are superseded by the Schmitt
correction above; they are not current design claims. Clock-pull and
divider arithmetic remain applicable. The current checker has nine checks
and five resistors; it binds the Nexperia PDF in place of the MOSFET PDF.

The previous 1 MΩ clock pull-downs were defective: TI SCES366L §§6.3/6.5
(local PDF pp.4–5) specifies 0.8 V maximum VIL, 2.0 V minimum VIH at
3–3.6 V VCC, and ±5 µA input leakage. A 1.01 MΩ resistor cannot sink
that leakage while remaining a valid low. This is not an Ioff question.

The related sense divider also needed correction, not a blanket exception:
Diodes DS30896 Rev.20-2 p.3 specifies **±10 µA** gate leakage for this
ESD-protected 2N7002K at ±20 V, not the nA often assumed for other MOSFETs.
Its old 100 kΩ/1 MΩ divider could not support an adequate corner budget.
The new 300 Ω series / 10 kΩ shunt uses already-selected exact resistors;
the clock pull-downs and OE pull-up also reuse the existing 10 kΩ MPN/code.
No pin connectivity or package changes are intended.

`03_src/check_clock_defaults.py` checks the actual native netlist values and
pins, reopens the three exact local PDF hashes, and computes these screens:

| Screen | Calculation / acceptance |
|---|---|
| Disconnected clock, receiver only | 5 µA × 10.3 kΩ = 0.0515 V, below 0.8 V VIL |
| Clock with additional leakage allowance | (5 + 20) µA × 10.3 kΩ = 0.2575 V, below the 0.4 V engineering target |
| External clock high-state DC burden | 3.6 V / 9.7 kΩ + 5 µA = 0.3762 mA per clock, below a 0.4 mA interface-load budget |
| Disconnected sense gate | 20 µA × 10.3 kΩ = 0.206 V, below the 0.4 V engineering target |
| Sense gate, module rail at 3.0 V | Worst divider tolerance and 20 µA sink leave about 2.901 V, above the 2.8 V engineering target |
| Disabled OE at local 3.0 V | (5 + 20 + 5) µA through 10.3 kΩ leaves 2.691 V, above 2.0 V VIH |
| Enabled OE current burden | Below 0.4 mA at local 3.6 V, including the TI input-leakage limit |

The ±3% resistance screen is an **engineering allowance**: 1% initial
tolerance plus 2% for drift/temperature, not newly asserted YAGEO data.
The 20 µA extra clock allowance includes the unpowered module, cable and
PCB together. The 20 µA gate and drain allocations and 5 µA PCB allocation
are also engineering budgets, not manufacturer all-temperature guarantees.
The Diodes table is explicitly at 25 °C; its 1 µA IDSS and threshold range
1.0–2.5 V are not a full-temperature, low-VDS on-resistance guarantee.
Accordingly, the calculations prove a prototype design margin under stated
bounds, not a production-qualified interlock or guaranteed hot-plug behavior.

The public miniDSP manual specifies 3.3 V logic but no exact clock-driver
MPN, VOH/IOH table or powered-off output leakage. The 0.4 mA load is a
prototype interface requirement, **not a claim miniDSP guarantees it**.
First article must confirm clock low below 0.4 V / high above 2.4 V under
the actual cable load, the TI 10 ns/V input-transition limit, no extra edges
in steady states, sense gate below 0.4 V absent / above 2.8 V present, and
OE above 2.4 V disabled / below 0.4 V enabled across the intended rail and
temperature range. Capture the power/cable transitions separately; do not
advertise glitch-free live insertion based on DC pull resistors. Stop and
redesign before qualification if any allocated leakage/load bound fails.

## Power-state contract

| Carrier | MCH | Required state |
|---|---|---|
| off | off | all lines unpowered |
| on | off | clock inputs pulled low; Schmitt inverter drives OE high and disables DOUT |
| off | on | Ioff on clock/TDM buffers and Schmitt sense input bounds back-drive; quantify actual current in first article |
| on | on | J3 sense enables DOUT; MCH remains clock master |

The intended settled split-cable states are: J10 without J11 leaves DOUT
disabled; J11 without J10 enables only an unloaded buffer output and the
local clock pull-downs hold the disconnected inputs low. These are not
glitch-free hot-plug claims. J10 and J11 must be visibly distinguished and
physically qualified together because the selected TMM headers are unshrouded
and unkeyed.

## Rejected alternative

Feeding MCHStreamer J2 pin 12 from the carrier 5 V buck is supported by the manual and would diode-OR with USB, but it was rejected here. It couples USB-domain load/noise into the quiet carrier rail and still does not prove that the separate TDM cable is seated. The J3 sense interlock directly represents the remote logic domain while preserving independent USB operation.

## Evidence hold

Bench-test all four power states with current measured on carrier 3.3 V, MCH
3.3 V sense, and USB. Verify no false MCLK/BCLK/FSYNC edges with MCH off, no
DOUT drive with J3 absent, and correct TDM only with both cables present. The
TCSD identity and carrier-side TMM fit are drawing-backed, but miniDSP does not
publish its board-header MPN. Module-side post fit, one-to-one cable continuity,
socket rotation, retention, simultaneous service and labeling remain explicit
connector-contract holds.

## 2026-09-08 — CARRIER-TOPO-001 source amendment

Decision for prototype source: insert noninverting Nexperia74LVC1G17GV,125
(C6076) U_TDM_SCH between ADC DOUT1 and U_TDM.2. R_TDM_PD is exact selected
YAGEO RC0402FR-0710KL/C60490,10k1%; C_TDM_SCH is the existing Samsung
CL05B104KO5NNNC/C1525,100nF supply bypass. Pin1 is NC. No shunt capacitor or
cable is permitted on TDM_RAW/TDM_CLEAN. The new bias is not a transmission
line termination. All prior paragraphs describing direct TDM_RAW-to-U_TDM
are historical and superseded by this amendment.

The old source genuinely failed: only U_ADC.25 and U_TDM.2 shared TDM_RAW,
with no default. Disabling OE did not bias A. A resistor alone is rejected:
release from a transmitted high is a slow capacitive decay and SCES223U p5
limits the CMOS input transition. Exact Nexperia Rev16 p1 accepts unlimited
input rise/fall; p3 GV figure and p4Table4 independently establish the pinout
and noninversion. The stored primary PDF is Rev16, SHA256
3db133d57486306950ba1140ac13a8a0ea95509dcefb88db36c08423a819b163,
obtained from the public LCSC datasheet link. It is not web Rev16.1.

DC screen is CONDITIONAL, not an ADC guarantee. Nexperia input leakage1uA
is cited at its stated conditions. Another20uA for ADC Hi-Z output plus PCB
is an explicit qualification allocation: Cirrus DS1314F1 p12Table3-8 names
its10uA as INPUT leakage and omits output leakage and IOH/IOL test load.
Its16mA drive register is not a loadedVOH/VOL guarantee. The resistor corner
uses1% initial tolerance plus2% engineering drift, giving a calculated
0.2163V released node and0.372134mA high-state load. Qualification must show
the ADC meets high2.8V/low0.4V engineering targets under this added load.
Nexperia discrete threshold extrema motivate those targets; they are not
invented interpolated manufacturer limits between VCC table points.

Under the explicitly allocated20pF total raw capacitance, high-to-Hi-Z decay
from3.6V reaches the0.4V target after about600.165ns. This is a settling
estimate, not a requirement to settle within a TDM bit. The Schmitt input
accepts that slow decay and preserves the last valid bit until its threshold
is crossed; outside-transmission bits remain invalid. Upon transmission the
ADC actively drives again. Regenerative push-pull conditioning removes the
RC source from the CMOS input. Nexperia tpd is NOT a maximum output-slew
specification; actual U_TDM.2 transition compliance still needs evidence.
No glitch-free reset, brownout or live insertion claim follows.

Timing screen includes the whole clock-to-returned-data path, not just the
new gate: remote BCLK through cable/J10/U_CLK/R_BCLK/ADC, ADC launch or
Hi-Z enable, U_TDM_SCH, U_TDM/R_TDM/J10 and return cable to MCH. Device
terms are TI3G34 4.1ns(-40..85C,3.0..3.6V,50pF), Cirrus10ns(25C,
3.3V,half-cycle50pF), Nexperia5.5ns(-40..85C,3.0..3.6V,50pF) and
TI1G1254.5ns(-40..85C,3.0..3.6V,50pF). These conditions do not establish
an all-temperature system guarantee. Nexperia/TI fast-input test conditions
and actual load must be satisfied; typical4pF/5pF do not prove a maximum.
The engineering allocations are6ns total PCB/cable/threshold/series-delay,
5ns remote setup and45% minimum launch-to-sample phase at12.288MHz.
The calculated residual is1.521094ns. Setup/hold, actual clock duty, edge
rate and cable load are unqualified; this thin positive screen is not SI
acceptance and doubling BCLK fails it. Release-to-Hi-Z can occur after the
latching edge; remote hold time must be established, not assumed zero.

Power ownership is unchanged: local3V3_ADC supplies both conditioners and
the tri-state device. Carrier-on/MCH-off still disables output through OE;
carrier-off/MCH-on still ends at the original TI output Ioff boundary;
both-off is unpowered; both-on has biased raw data even during reset or
unused slots. J10-only leaves OE disabled; J11-only enables an unloaded
output. The added gate has4uA static ICC at rail inputs, but its midrail
supply transient and dynamic current are not bounded by that static number.
Keep the existing150mA total3V3_ADC allocation unchanged, reserve5mA within
it for added bias/conditioning, and measure actual slow-release transient.
The power helper inventories the added100nF from the fresh native netlist;
no inherited capacitor census may certify the changed source.

The source adapter checks exact identities, PDF hashes, source/native pins,
all three raw-node endpoints, no extra load, six bias resistors and the
conditional corner calculations. New source path inventory names the bias
leaf; native footprint/seed/launch screens must include the three new parts.
Old299-ref geometry remains unchanged. Physical current, leakage, timing,
threshold/slew and all four power states remain explicit blocking first-
article work; independent schematic acceptance is also still required.

<!-- bound: TDM_BIAS_MAX -->
```yaml
id: TDM_BIAS_MAX
claim: Maximum nominal pull under the conditional21uA leakage and3percent resistance allocation, not an ADC guarantee
relation: "<="
value: 18492.83402681461
unit: Ohm
corner: worst_case
command: /usr/bin/python3 -B -c 'print(.4/(21e-6*1.03))'
governs:
  evaluate: /usr/bin/python3 -B -c 'import sys; sys.path.insert(0,"projects/crow-audio-carrier-v1/03_src"); from check_clock_defaults import tdm_screen; print(tdm_screen(r_ohm={value})["measurements"]["released_raw_V"])'
  budget: "<= 0.4"
  unit: V
standard_value:
  explicit: [10000]
  series_why: Exact already-selected YAGEO RC0402FR-0710KL C60490 is the only proposed stocked pull in this amendment; no silent alternate series
chosen: 10000
grade: CITED
```

<!-- bound: TDM_BIAS_MIN -->
```yaml
id: TDM_BIAS_MIN
claim: Minimum nominal pull under the conditional0.4mA ADC added-load allocation and3percent resistance corner
relation: ">="
value: 9301.604526780871
unit: Ohm
corner: worst_case
command: /usr/bin/python3 -B -c 'print(3.6/((.0004-.000001)*.97))'
governs:
  evaluate: /usr/bin/python3 -B -c 'import sys; sys.path.insert(0,"projects/crow-audio-carrier-v1/03_src"); from check_clock_defaults import tdm_screen; print(tdm_screen(r_ohm={value})["measurements"]["adc_high_load_A"])'
  budget: "<= 0.0004"
  unit: A
standard_value:
  explicit: [10000]
  series_why: Exact already-selected YAGEO RC0402FR-0710KL C60490 is the only proposed stocked pull in this amendment; no silent alternate series
chosen: 10000
grade: CITED
```
