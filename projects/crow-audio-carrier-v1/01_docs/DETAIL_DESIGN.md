# Detailed design and first-article math

Current source: ADR0025 shared ADC/amplifier rail, ADR0027 fixed channel
association and ADR0028 factory RJ45 spokes. This living calculation map
supersedes the former TPS7A92, independent 5V_OPA, ninth reference buffer and
Micro-Fit/Belden screens. Their dated decisions, research and journal evidence
remain historical records. No measurement or release acceptance is claimed.

## Source and calculation authority

`03_src/check_power_source.py` and `03_src/check_protection_architecture.py`
own the bounded power and relative-pin screens; `check_analog_paths.py`
owns the actual filter/channel topology; `check_clock_defaults.py` owns the
MCH interface allocations. `03_src/rules/spoke_interface.yaml` is synchronized
with the pod and parent. Exact manufacturer citations and assumptions remain
in the part dossiers, rule files and accepted decisions. Running these checks
does not qualify the physical implementation.

## Shared rail and audio headroom

LT3041ADE#TRPBF powers CS5308P and eight OPA2320 duals from 3V3_ADC.
The two external bias banks use equal 1 kΩ, 0.1%, 25 ppm/°C dividers with
10 µF + 1 µF bypass. ADC_VMID1/2 remain separate internal-reference outputs.
There is no independent 5V_OPA domain or external VMID follower. The retained
R_OPA_BLEED1/2 names denote two 100 Ω series resistors across shared3V3.

At the 1.2 Vrms differential interface limit, each balanced leg swings
`1.2 × sqrt(2) / 2 = 0.84853 V peak`. ADR0025's initial/tolerance bias
screen is 1.60938–1.68068 V, giving a 0.76085–2.52921 V signal window on
the 3.23–3.35 V rail envelope. This is conditional headroom, not measured
noise, common-mode range over lifetime, stability or distortion acceptance.
The first-power card requires VMID1_EXT and VMID2_EXT at 1.60–1.70 V.

The receive path retains 1 µF coupling, 100 kΩ bias legs, 10 kΩ positive-input
limiters, same-leg unity/filter feedback and TMUX2821 isolation. Two 15 nF
grounded shunts per filter leg replace the old cross-leg capacitor; every
ADC pin has a 10 kΩ pulldown and 1 nF C0G shunt. The differential equivalent
of the filter capacitance is retained, but the common-mode loading changed.
All 32 filter-shunt placements and returns require native and bench review.

## Power-state bounds and measured obligations

The shared-rail correction removes the former independent amplifier/ADC
sequencing dependency. It retains precharge, held input, supervisors, dump,
mute/reset and isolation. ADR0025 explicitly charges retained coupling and
reference energy, regulator reverse recovery and ADC pin lag:

- The positive input-current envelope at a 3.4 V rail barrier leaves
  3.114 mA margin after bleed current and the declared unexplained-current
  reserve; per-input limiter currents remain below the cited device limit.
- The fast rail-discharge model charges the minimum dump resistance,
  derated local ceramics, 0.30 A extra load and 15 mA reverse-recovery sink.
  The 10 kΩ/1 nF ADC nodes must track within the relative-pin boundary.
- The combined relative-pin engineering allocation is 243.759 mV against
  300 mV: 41.127 mV filter lag, 52.632 mV switch-charge contribution,
  100 mV return error and 50 mV amplifier tracking. The 50 pC switch-charge
  budget and return/tracking allocations are falsifiable engineering bounds,
  not guaranteed manufacturer maxima.
- The charge inventory and SET99 allowance give an 8.389 ms startup screen.
  This is not a guaranteed LT3041 loaded ramp or ADC endpoint convention.

Measure cold starts, slow brownouts, ordinary removal, removal after dropout
and rapid correlated restart. Include negative ADC-pin excursions, partial
supplies, full-level eight-channel audio, all reference/filter reservoirs,
actual capacitor ESR/ESL, inrush and hot-board behavior. Historical TPS7A92
NR settling and independent OPA hold calculations cannot qualify this source.

## Steady power and carrier voltage delivery

ADR0025 bounds shared3V3 at 222.374 mA of 230 mA, and local5V at
250.414 mA of 300 mA, including regulator ground current. With eight 0.10 A
spokes, the upstream allocation is 0.985346 A, screened at a rounded 1.0 A.
The A-grade SET/resistor/offset allocation yields 3.255199–3.344999 V.
The reference-board thermal calculation is not an actual PCB temperature.

At the 11.4 V J9 input floor, the common path charges 0.075 Ω input PPTC,
0.025 Ω PFET and 0.100 Ω copper at 1.0 A, plus 20%. This gives
11.16 V at 12V_PROTECTED. Each branch charges 1.700 Ω PPTC, 0.400 Ω
copper/joints and 0.100 Ω header at 0.10 A, plus 20%, giving 10.896 V
at the carrier output, above its 10.8 V minimum. The separately isolated
buck input has a 9.86 V planning floor after the 1.3 V diode allowance.
Keep carrier-output and complete-cord measurement planes distinct.

F_IN 2920L260/33 has published 1.60 A hold at 70 °C and 1.27 A at
85 °C. Each 1812L035/60MR branch has 0.20/0.16 A hold at those points,
0.70 A trip at 20 °C and 1.700 Ω R1max. Pod 0ZCJ0010FF2E is the
downstream tier. Thermal PPTCs do not establish selectivity or interrupting
capacity from their nominal currents. Verify source foldback, hot drop,
trip energy and one-fault/seven-healthy behavior without applying the
datasheet's 8 A test stimulus to an installed cord.

Q_IN blocks static reverse hookup with input on drain, load on source and
a gate-source clamp. It does not block every downstream backfeed state.
The input TVS is transient protection, not sustained-overvoltage cutoff.

## Exact factory cord

Würth 615008160221 jacks mate to the complete Weidmüller 8909650150
factory 15 m Cat6A S/FTP PUR cord. Pins 1/3/7 carry +12 V, 2/6/8 return,
5 AUDIO+ and 4 AUDIO−. Orange, green and brown pairs each carry power
and return; blue carries balanced audio. Shell pads 9/10 join CHASSIS at
the carrier and isolated POD_SHIELD at the pod; neither joins GND.
These are custom analog/power ports, labelled NOT ETHERNET OR POE.

The conditional hot-loop calculation is
`290 Ω/km × 0.015 km / 3 × 1.25 + 0.300 Ω = 2.1125 Ω`.
At 0.10 A from 10.8 V this yields 10.58875 V at the pod. The 0.300 Ω
contact allocation remains unmeasured; the complete finished hot loop must
be at most 2.2 Ω. Equal power sharing, AWG26/7 conductor/plug fault behavior
and the jack's 1.5 A/contact rating require separate interpretation and
physical tests. Do not inherit the former cable or Micro-Fit ratings.

No accepted pair-capacitance value exists for this exact cord. Measure
capacitance, gain, relative phase, noise, crosstalk and stability under power
load; the former Belden 90.2 pF/m and 0.59 MHz calculation does not apply.
The 4 m acoustic radius does not select an alternate 4 m cable SKU.

Nominal manufacturer STEP gives the complete 57.98 mm plug end and
22.986 mm grip cylinder. Manufactured tolerance, seating, full latch motion,
populated service and dry IP20 entry remain owed. Retain 67 mm bend planning
for 6.1–6.5 mm cable OD. UV is unestablished and requires qualification
before outdoor deployment. Mate with power off.

## TDM, reset and independent power

At 48 ksample/s, eight 32-bit slots require 12.288 MHz BCLK (256 Fs);
24.576 MHz MCLK is 512 Fs. FSYNC is one BCLK high per frame. Verify actual
launch/sample edges and MCHStreamer's intended signed 24-bit extraction.
ADR0027 maps logical pods1–8 to physical ADC4,3,2,1,5,6,7,8; TDM slots0–7
therefore carry pods4,3,2,1,5,6,7,8. Record map ID
`crow-carrier-channel-map-20260912`, source digest and actual USB/slot/pod
identity. An eight-channel impulse test must verify this mapping.

The reset candidate uses 100 kΩ and 220 nF: nominal RC is 22 ms;
component-only low is 19.602 ms before voltage/temperature effects.
The historical K=0.5 screen gives 9.801 ms, but TI does not guarantee that
coefficient or the required minimum pulse from this arithmetic. Measure
initial high ≥2 ms, low ≥1 ms and stable final high across the admitted
power/temperature conditions. Supervisor delay alone does not prove audio
reference settling or startup readiness.

MCH J3 pin2 supplies presence sense through 300 Ω/10 kΩ, nominal
0.320 mA; it does not power the carrier. Schmitt OE control and Ioff buffers
must pass off/off, on/off, off/on, on/on and split-cable tests. Clock pull-down
screens are 0.0515 V receiver-only and 0.2575 V with the extra leakage
allocation. Actual driver strength, transition rate, back-power and timing
remain measured obligations; no glitch-free hot-plug claim follows.

The current `FIRST_ARTICLE_TEST_PLAN.md` and `rules/first_article.yaml` own
the controlled measurement procedure. ADR0007 separates prototype design,
order authorization and physical qualification. All required exact schematic,
layout, fabrication and release gates remain mandatory before release.
