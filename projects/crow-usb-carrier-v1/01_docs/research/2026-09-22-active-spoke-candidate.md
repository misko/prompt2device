# Active spoke protection candidate — TPS26625DRCR

Status: bounded source candidate; fault containment is not admitted.

This candidate replaces each `1812L035/60MR` spoke PPTC with one
`TPS26625DRCR` and its required programming, ramp and local bypass parts. It
keeps J1–J8, their pin maps, all audio nets, 0.10 A per-spoke loads, CHASSIS,
the 11.4–13.2 V input boundary and the 10.8 V connector-plane requirement.
There is no PCB, conductor, thermal, source-load-line or fault-containment
claim in this directory.

## Why this is the finite candidate

The old PPTC does not establish fault isolation. Its 0.15 s maximum trip time
is specified only at 8 A at room temperature, while its 70 C hold-current
reference is 0.20 A. The exact external source prospective current, foldback
or hiccup behavior, harness impedance and input-PPTC coordination are absent.
The selected eFuse offers a programmed current-control architecture, reverse
current protection and automatic retry while preserving the spoke interface.
It is a better architecture to qualify, but the available datasheet evidence
does not yet prove the complete system requirement.

The sole active candidate is Texas Instruments `TPS26625DRCR`, DRC0010J
VSON-10. The retained primary source is TI datasheet
[SLVSDT4F](https://www.ti.com/lit/ds/symlink/tps2662.pdf). The local PDF and
SHA-256 are recorded in `02_parts/TPS26625DRCR/part.yaml`.

## Exact channel implementation

Each channel contains six parts, replacing one PPTC: one TPS26625, one 44.2 kΩ
ILIM resistor, one 1 MΩ UVLO resistor, one 10 nF dVdT capacitor, and 100 nF
input and output bypass capacitors. Across eight channels this is 48 parts in
place of eight, for a net increase of 40 placements.

`RT0603BRD0744K2L` is 44.2 kΩ, ±0.1%, 25 ppm/°C. Its exact Yageo primary PDF
and mounting source are retained. `RC0402FR-071ML` is 1 MΩ, ±1%, 100 ppm/°C.
The local input/output capacitor is exact Yageo `CC0805KRX7R9BB104`, 100 nF,
±10%, 50 V, X7R. The 10 nF dVdT part remains the existing exact Samsung
`CL05B103KB5NNNC` dossier. No effective-capacitance or transient-current
guarantee is inferred from nominal capacitance.

IN and SHDN connect to `12V_PROTECTED`. UVLO has 1 MΩ to IN. OVP connects to
the local RTN island. ILIM has 44.2 kΩ to RTN. dVdT has 10 nF to RTN. FLT is
the sole unconnected device pin because TI directs leaving this open-drain
output floating when unused. OUT supplies `12V_PODx`. GND connects to board GND.
RTN and the exposed PowerPAD share the local RTN plane, while pin 5 provides
the separate required electrical RTN connection. No required device pin is
floating. RTN is deliberately not shorted to GND because that would defeat
the device's reverse-protection topology.

## Bounds and evidence limits

TI specifies 800 mΩ maximum on-resistance over –40 to 125 °C. At the preserved
0.10 A normal spoke current, the eFuse contribution is therefore at most
80 mV. TI's electrical table gives 482 µA maximum quiescent current per device
under its 24 V global condition. Using that table-conditioned value, eight
devices add 3.856 mA to the inherited 2.12 A load allocation and produce a
2.123856 A source-side planning screen. The exact 11.4–13.2 V supply-current
bound remains open. The already identified upstream 55 mΩ
input PPTC plus 25 mΩ PFET then contribute at most 169.908 mV, so those three
known elements consume 249.908 mV of the 600 mV input-to-connector budget.
This is the only new complete normal-path bound. Copper, joints, connector
contacts, drive-state proof and
thermal realization remain unbounded; the 10.8 V connector-plane minimum is
therefore still an open system requirement.

With 44.2 kΩ ILIM, TI's electrical table gives 0.145/0.152/0.159 A
minimum/typical/maximum. The table's global condition is VIN = 24 V and the row
condition is VIN − VOUT = 1 V. This is an engineering screen for resistor and
load planning. It is not a guaranteed current range for a 12 V hard short.
The resistor's ±0.1% initial tolerance and 25 ppm/°C TCR are explicit inputs,
but no synthetic tighter current guarantee is calculated beyond TI's table.

The fast-trip comparator threshold shown as 1.6 A has no minimum or maximum in
the electrical table. The 220 ns short-circuit response is explicitly typical
in sections 9.1 and 9.3.5.2. Neither value is a guaranteed transient bound.
The 512 ms current-limit and thermal-retry entries are nominal, and section
9.3.5.1 states that current-limit duration changes with CdVdT. For a hard short
with VIN − VOUT at least 2.6 V, behavior is dominated by power dissipation and
thermal shutdown rather than the sub-2.6 V current-limit timing row. None of
these values bounds common-bus disturbance without the source, cable, copper
and thermal model.

## Source and upstream protection requirement

The external supply may be identified by exact MPN and configuration or by a
compliance envelope enforced at J_PWR: 11.4-13.2 V under at least 2.185 A at
70 C after cable loss. Its current-limit and foldback/hiccup thresholds,
output-capacitor discharge, cold and hot harness impedance, bus droop and
recovery must be bounded through normal startup, hot short, powered-on short,
retry and short removal. Seven healthy spokes plus the approximately 1.32 A
digital allocation consume 2.02 A. Adding the table-conditioned 0.159 A
maximum fault output current and all eight devices' 3.856 mA maximum
quiescent current gives 2.182856 A, rounded upward to the 2.185 A engineering
screen. That total is only a planning screen because the 12 V hard-short
current is unqualified.

The input `2920L330/24DR` PPTC must be replaced by an input protection element
with a guaranteed 70 °C continuous rating above 2.185 A plus engineering
margin and a trip curve coordinated with a 0.159 A spoke limiter. Its 70 °C
reference hold current of 2.25 A leaves only 65 mA above the unqualified
2.185 A screen, before production spread, enclosure heating, retry dynamics or
source interaction. No coordination claim is made.

## Required delta tests

Before electrical admission, test the exact source, harness, input protection,
eight populated channels and intended enclosure at 70 °C. Exercise every
simultaneous pod startup/load/capacitance state, one hot short on every spoke,
power-up into a short, repeated automatic retry, short removal, input ramp and
brownout, and externally powered pod/reverse-current states. Record minimum
healthy-spoke connector voltage, every digital rail minimum, source-mode
transitions, fault and healthy branch currents, retry timing, junction or
validated case/board temperatures, and recovery without a system reset.

The exposed-pad land pattern is retained as native KiCad source and as the
source-owned JSX footprint. Board admission still requires TI layout-rule
review, separate RTN pin continuity, via/copper realization, and a thermal
model or measurement at 70 °C. Allocation and price are also open: TI's store
was observed active/production but out of stock with no public unit price on
2026-09-22.
