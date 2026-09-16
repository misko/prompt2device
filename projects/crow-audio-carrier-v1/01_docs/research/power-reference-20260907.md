# Power/reference correction and unadopted successor architecture — 2026-09-07

This is research, not source acceptance, a BOM substitution, a physical
qualification waiver or a TaskAttempt receipt. The live regulator remains
TPS7A2433DBVR. ADR0008 adopts only the external VMID/direct-return correction
and larger positive feed resistors. A fresh author must complete the power
architecture before schematic review or routing. Locked requirements remain
150 mA on 3V3_ADC, 85 C ambient, 0.25 A steady 5 V allocation, two 470 uF FILT
reservoirs and the existing hardware/TDM8/audio contract.

## Actual source and repeatable evidence

Run `python3 projects/crow-audio-carrier-v1/03_src/check_power_source.py`
from the repository. It intentionally returns 1 with OPEN_SOURCE_FAILURE.
The current thermal screen gives 283.6875 mW, 132.6028 C junction on the
datasheet reference board, versus a 238.379 mW / 125 C budget at 85 C.
Ground current is omitted from that original failure screen; including it
cannot cure the failure. Do not relabel the source failure as a bench hold.

The checker now parses the current generated native netlist and lists every
capacitor connected to direct 3V3_ADC, both positive FILT banks, internal
ADC reference/LDO outputs, external VMID dividers and the reset timing pair.
It deliberately separates those branches: full summed charge inventory is
not an equivalent small-signal LDO loop capacitance. Buffered VMID output
reservoirs are powered by 5V_OPA and excluded. Its initial upper model uses
bulk +20%, other capacitors +10% tolerance and +15% temperature; that is not
an all-life bound. The unchanged TPS7A24 recommended effective output range
and uncontrolled reverse discharge remain unresolved regardless of E-CAP
minimum-capacitance passes.

## Concrete successor proposal — NOT ADOPTED

Use TPS7A9201DSKR, not TPS7A91: the 2 A part offers charging-current margin
while keeping the quiet linear rail. Public exact candidate code is C882405;
the -HX lookalike is not interchangeable authority. Primary SBVS318B has
RthetaJA 56.9 C/W, 125 C operating junction limit, 4 mA ground-current maximum
at its stated table conditions, and output capacitor guidance supporting
22 uF nominal / 11 uF effective for loads above 1 A. Proposed local IN/OUT
capacitors are existing 47 uF GRM32ER71A476KE15L. No numerical maximum Cout
was found; large mixed-bank stability still needs analysis and measurement.
Pins: 1/2 OUT, 3 FB, 4 GND, 5 PG, 6 SS_CTRL, 7 EN, 8 NR/SS, 9/10 IN,
11 exposed-pad GND. Ground SS_CTRL for the slow NR current mode; PG can be
left open per primary instructions. Proposed feedback is 3.57k/1.15k,
0.1% Yageo RT0603BRD073K57L/C861380 and RT0603BRD071K15L/C861192, giving
3.28348 V nominal; exact manufacturer ordering and temperature coefficients
must be retained in dossiers. [TI primary](https://www.ti.com/lit/ds/symlink/tps7a92.pdf).

DSK0010A is WSON 2.5 x 2.5 mm, not a convenient DSQ substitute. The installed
`Package_SON:WSON-10-1EP_2.5x2.5mm_P0.5mm_EP1.2x2mm` has compatible pad
numbers/body but different lands (x +/-1.2125 mm, 0.825 x 0.25 mm pads).
It must not silently substitute for the TI example. The next author must independently
view top/land/stencil drawings and create a dossier-bound footprint: proposed
pad-center rows x +/-1.15 mm, five pads at 0.5 mm pitch; pads 0.6 x 0.25 mm,
exposed pad 1.2 x 2.0 mm. These are drawing notes, not a verified model.
Thermal copper, solder coverage and vias remain placement requirements.

Supply its IN from a diode-isolated `5V_LDO_HOLD`, not directly from raw
`5V_BUCK`. The same held node should power the shutdown supervisor and
discharge-control Schmitt inverter; raw 5 V remains the sensing authority.
Use two additional exact EEEFK1A471P input reservoirs plus local ceramic,
or investigate exact EEEFK1A102P (10 x 10.2 mm standard size G). The two 470s
provide 752 uF initial lower capacitance before ceramics, not a lifetime
minimum. Panasonic permits endurance and soldering-induced capacitance
changes; the initial +/-20% tolerance alone is insufficient for lifecycle
hold-up or startup acceptance. Its cold 120 Hz impedance ratios are not a
blanket scaling rule for 100 kHz ESR. The retained primary now closes the
previously missing local PDF evidence for the selected 470 uF part.
[Panasonic primary](https://industrial.panasonic.com/cdbs/www-data/pdf/RDE0000/ABA0000C1181.pdf).

Candidate input diode B340A-13-F/C85098 is SMA; DS30891 Rev19-2 April2026
states 0.50 V maximum at 3 A and 25 C, NOT an all-temperature forward bound.
Its hot rated-voltage leakage limit is 20 mA at 100 C; include leakage in
hold-up until lower-voltage behavior is adequately bounded. At 752 uF,
20 mA for 10 ms alone costs about 0.266 V. Capacitive-load current derating
also applies. Do not add an OUT-to-IN Schottky and claim it guarantees the
LDO's OUT <= IN+0.3 V absolute maximum: its forward drop does not establish
that protection. Holding IN above OUT during shutdown is the intended
alternative; cold VF, ESR step, leakage and abort latency need a combined
margin calculation. [Diodes primary](https://www.diodes.com/datasheet/download/B340A.pdf).

Candidate TPS389001DSER/C1509297 is the adjustable 1.15 V supervisor, NOT
a 0.5 V variant. Pin 1 SENSE from raw5V with 30k/10k divider (three existing
10k series parts can supply the top leg); pin 2 GND; pins3 MR and4 VDD to
held5V; pin5 CT to a grounded timing capacitor; pin6 RESET to PWR_EN with
47k pull-up to held5V. PWR_EN drives LDO EN. The nominal sense threshold is
4.6 V; verify tolerance, hysteresis, divider leakage and input-floor margins.
47 nF CT targets roughly 50 ms release delay. Existing 220 nF gives a longer
delay and avoids a new SKU; calculate its derated minimum. RESET VOL has
margin against the LDO's 0.4 V low limit at the specified sink conditions.
This WSON6 DSE needs its own independently verified land and pin model.
Installed `Package_SON:WSON-6_1.5x1.5mm_P0.5mm` differs from the TI land
example, notably its longer pin1; adjudicate the actual drawings and model.
No maximum falling detection delay was found; typical delay is not a
guaranteed abort-time budget. [TI primary](https://www.ti.com/lit/ds/symlink/tps3890.pdf).

PWR_EN -> 10k -> DUMP_DELAY with 10 nF to GND is a proposed delayed inverse
control. Existing exact 74LVC1G14GV,125 on held5V senses DUMP_DELAY; output
through 100 Ohm drives AOS AO3400A/C20917 gate, with 100k gate-to-GND.
AO3400A pin1 gate, pin2 source GND, pin3 drain through a pulse-qualified
resistor to 3V3_ADC. This NMOS/SOT23 identity is AOS, not similarly named
other manufacturers. Its hot low-gate-voltage resistance must not be
claimed from the 25 C / 2.5 V maximum alone. A 1 Ohm CRCW12061R00FKEAHP
is a candidate shunt resistor, but the actual pulse must be checked against
the retained Vishay curves and assembled thermal conditions. Proposed RC
dead time is about 100 us; missing maximum LDO disable time prevents a
guaranteed no-overlap claim. Measure both shutdown and startup overlap,
and ensure gate/control supply survives until the output is discharged.
[AOS primary](https://www.aosmd.com/sites/default/files/res/datasheets/AO3400A.pdf).

## Numerical proposal screens, not accepted bounds

These initial-only proposal numbers preceded the final increase of external
VMID bypass to 10 uF + 1 uF per divider; recalculate from the live inventory.
An initial-only 1.3 mF charge inventory and 33 nF C0G +/-5%, 30 ppm/K NR
capacitor gave a roughly 2.78–6.94 ms soft-start model, using the specified
4–9 uA NR-current endpoints as an engineering approximation. This is not
a guaranteed transient simulation: the table current is characterized at
VNR=0 and the final reference tail differs. Record 10–90%, time to the ADC
3.13 V valid floor, and the final settling tail separately. CS5308P's ramp
table does not define the endpoints; do not invent an impossible mathematical
0–100% requirement. Internal LDO_D_FILT follows the mandated manufacturer
connection and capacitance; missing internal sink maxima alone is not proof
that the recommended IC architecture is impossible.

Root's independent symmetric two-bank RK4 initial-only screen used each
FILT bank 577.915 uF, direct remainder 144.17 uF, each feed 2 Ohm including
an engineering ESR/wire allowance, and shunt 1.2 Ohm including a 0.2 Ohm
FET/copper allowance. It gave ADC 90–10% about4.62 ms, bank90–10% about5.80 ms,
and bank5% about7.99 ms; bank1% was about12.24 ms. Those margins are not
datasheet corner guarantees. Stored energy is about7.2 mJ at1.3mF/3.327V.
The scratch model was `/tmp/carrier-power-research.rYok3w/discharge_screen.py`;
fresh work must reconstruct/check it rather than treat a temporary path as
portable authority. Positive endurance drift may raise the upper inventory
toward1.65mF, invalidating both the initial discharge result and the 33nF
charging-current margin. Rough39–40nF NR proposals need exact-part selection
and a revised full-lifecycle inventory before adoption.
Root's subsequent positive-endurance sensitivity used 1.65 mF total and
470*1.2*1.3 uF per electrolytic: ADC90–10% 5.9025 ms, FILT90–10% 7.453 ms,
FILT5% 10.245 ms and FILT1% 15.704 ms. The 33 nF charging model reaches
2.1238 A including 150 mA load; a hypothetical40nF gives1.7784 A and
3.371–8.416 ms linear ramp. These counterexamples demonstrate why the
initial-only model cannot be promoted unchanged. Root cross-checked
0.5us/1us steps and energy balance; this is still not a physical guarantee.

The ideal RC discharge screen omits a further important path: still-powered
5V_OPA followers and externally powered pod signals may drive ADC analog
pins while 3V3_ADC falls. External VMID bypass now has a nominal55ms time
constant; a slow raw5V brownout through the proposed4.6V threshold can leave
OPA devices powered. Reopen the Cirrus analog-pin absolute maxima and power
sequencing, include buffer output/clamp/back-power paths and actual5V decay,
and test the corresponding states before adopting active discharge. This
is an incomplete model, not a confirmed physical violation.

The AP63205 must also survive charging the input hold-up bank. Its 4 ms
soft start is typical; continuous peak limit can produce hiccup. Delayed LDO
enable separates input-bank charging from the ADC-bank current pulse, but
does not prove cold startup or loop stability. Keep the 0.25 A steady
allocation and explicitly model the larger short transient demand; do not
silently reinterpret the locked load requirement. Next source work must
close the model, exact parts/pins/lands, circuit/rules and full regeneration
together. No power component above was substituted by this attempt.

## Primary snapshot hashes for fresh revalidation

- TPS7A92 SBVS318B: `e0c0a695e933d9656a7c6fefad654c5129d76a22ac8398d26eacfb844dd4532e`.
- TPS3890 SLVSD65A: `ee79599730e7606ba9718d9820b411020e3dcd9ff7d44572f8ee63fead15b9d0`.
- AO3400A: `9c60d0b6c1ddc7609a4b788a91181468d8ffe6c3e9ba425c3d8ffc5ba88c5033`.
- B340A DS30891 Rev19-2: `453cbd34d996482abd07ac694c4e2d812d26b1d679d05ee325acc5c3eeb79917`.
- Panasonic and Vishay selected-part primary hashes are in their live dossiers.

## Coordinator follow-up — analog power ordering remains to be analyzed

MEASURED by reopening local primary text and the frozen TSX on 2026-09-07:
DS1314F1 Table 3-3, page 9, specifies analog input voltage between -0.3 V
and VDD_A + 0.3 V, and analog input current within +/-10 mA. The actual
sixteen R_OUT parts are only 10 Ohm. They are output damping, not demonstrated
unpowered-input current protection. OPA1656 SBOS901C sections 7.3.3 and its
continuation on pages 16-17 explicitly discuss steering-diode conduction,
unpowered input drive and back-power; its input-current limit is 10 mA.

INFERENCE / OPEN MODEL PATH: a slow raw-5V brownout can trigger the proposed
3V3 dump while 5V_OPA, the buffered references and driven pod signals remain
active. The ideal two-node discharge model omits this possible source of
current into the ADC. Evaluate startup, abrupt removal, slow brownout,
interrupted startup and rapid restart with all relevant analog and digital
driver states. Do not assume op-amp outputs become high impedance below
their normal supply range. This observation does not yet establish a measured
violation; it is an obligation for the next coherent power-source design,
not permission to declare that design safe or to require vendor access.
