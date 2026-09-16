# ADR-0009 — quiet LDO, held energy and break-before-discharge analog boundary

Date: 2026-09-07. Status: source candidate; conditional screens, physical qualification OWED.
This supersedes only the local power implementation in ADR0003; ADC/reference
corrections in ADR0008 and hardware TDM/reset in ADR0001/0002/0005 remain binding.

## Authority and clock

Fresh source author started2026-09-07T21:36:55Z on engineering source
1f136d285f17be147195dbe2d884a90ee73bef3a, worktreeHEAD4a753d08.
Immutable task-envelope canonicalSHA256
9b4eebb548af7b7611cede771332b713dac9add9bb63888a98c7c0ee58a27363
and all five packet hashes verified; pcb_flow validate PASS before edits.
Absolute freeze deadline22:34:37Z. Source/outcome report records actual freeze.
No routing, independent review, release, purchase or canonical TaskAttempt telemetry.

Dated coordinator amendment received2026-09-07 during this attempt: local5V
steady allocation may be corrected from0.25A to0.30A because it is an internal
engineering allocation, not a user/commission fact lock. Preserve150mA ADC,
85C ambient, 1.0A upstream trunk, eight0.10A spokes and existing delivery proof.
The immutable packet remains unchanged. Executable all-channel screen is267.3mA;
using the full300mA allocation gives963.9mA upstream including800mA spokes and
1mA overhead. This does not change any external current/voltage claim.

## Selection and exact evidence

TPS7A9201DSKR replaces TPS7A2433DBVR. Primary TI SBVS318B is vendored in
02_parts/TPS7A9201DSKR: 2A,56.9C/W reference-board thetaJA,400mV max dropout,
4mA maximum ground-current screen. At85C/150mA and5.15V worst input,
including ground current, screen308.6mW and102.6C. Achieved-board thermal
resistance and EP solder remain unmeasured. Local47uF input/output ceramics
clear10uF/11uF effective requirements under declared derating. Unlike the old
TPS7A24, no50uF effective-output recommendation is imported into this part.

Exact TI DSK0010A, DSE0006A and DSG0008A primary land drawings were visually
inspected. Source-owned lands preserve DSK1.2x2.0 EP11, DSG0.9x1.6 EP9,
and DSE asymmetric0.8mm pin1 versus0.7mm other lands. No unadopted via-in-paste.
AO3400A/AO3401A primary exact G/S/D1/2/3, B340A band=cathode1. Exact public
catalog selection is recorded in dossiers; it is not PCBA allocation.

B340A-13-F isolates the held input. Two additional Panasonic EEEFK1A471P
470uF cans and47uF local ceramic store input energy. A pulse-rated Vishay
CRCW120622R0FKEAHP22ohm precharges this bank; AO3401A bypasses it only after
U_PWR delay. Reusing existing pulse-rated1ohm parts retains both FILT feeds
and supplies the separate output-dump resistor. A third added470uF can holds
raw5V/OPA during commanded isolation on normal J9 removal/slow brownout.
The two existing470uF FILT reservoirs are untouched.

U_PWR TPS389001DSER senses raw5V with30.9k/10k precision divider. Its1uF CT
minimum under the declared0.34425 capacitor factor is298.35ms, settling the
worst-high held bank to within1.82mV of the precharge asymptote. Q_PRE bypass
then avoids an unacceptable steady22ohm drop. B340A reverse20mA maximum at100C
is conservatively charged to hold calculations;0.5V Vf is a25C maximum only.
The4.10V held-input floor and hot PFET/diode drop are explicit measured-acceptance
requirements, not newly invented all-temperature manufacturer guarantees.

U_DUMP receives PWR_EN through two100k resistors in parallel and15nF C0G.
Its output drives AO3400A and a second Schmitt inverter U_LDO_EN. Thus the
intended valid-logic sequence disables the dump before enabling the LDO;
on shutdown it disables the LDO when the delayed dump turns on.
The 1.4..1.65V cold-start interval (LDO operational, Schmitt below recommended
supply) is expressly unqualified. Do not call this a guaranteed POR interlock.

U_AUDIO TPS389001DSER senses3V3 through17.4k/10k; MR=PWR_EN and2x1uF CT
delay keep analog isolation off while the external VMID dividers settle.
Eight TMUX2821DSGR dualSPSTs follow each COMPLETE AN0556 filter cell:
OPA ->10ohm -> FILTER;300ohm feedback also ends at FILTER;15nF differential
capacitance stays at FILTER; only then does the switch connect the ADC.
Neither feedback leg bypasses isolation. The OPA/filter remains closed-loop
while the switch is off. Every ADC input has100k toGND plus1nF C0G.

## Explicit state obligations

| State | Intended source behavior | Evidence boundary |
|---|---|---|
| Cold input ramp | Hold bank precharges; dump on; LDO/audio off until delays | POWER-COLD interval and actual AP ramp OWED |
| Startup after raw valid | Precharge bypass; dump releases;47nF NR gives modeled3.917..9.999ms full rise | NR current table is atNR=0, not guaranteed complete ramp |
| Normal all-channel audio | 3V3 regulated, both switches on, complete active filter retained |267.3mA conservative supply screen; loadedTHD/stability OWED |
| Normal J9 removal | U_PWR asserts; U_AUDIO MR opens isolation; delayed output dump |100us detector allowance is an engineering budget, not a published maximum |
| Slow brownout | Raw threshold opens audio before OPA leaves4.5V operating region in scoped hold model |10.5mV conditional margin; simultaneous captures required |
| Rapid restart | Supervisor CT resets; precharge/bypass and dump sequenced again | Incomplete rearm/CT discharge and NR discharge qualification OWED |
| Converter disabled while OPA remains powered | TMUXoff and ADC100k bleeds bound DC leakage |0.1uA at85C specified testpoints; partialVDD/feedthrough OWED |
| MCH independent power | Existing Ioff clock/data and Schmitt presence boundaries unchanged | Existing ADR0005 physical tests remain owed |

Destructive internal5V short and externally back-driving local power rails are
not included in normal disconnect/brownout claims. No fault immunity is inferred.

## Executable models, limits and uncertainty

Run python3 -B 03_src/check_power_source.py after native regeneration.
It pins critical power pinmaps and component values plus the actual capacitor
inventory. The analog checker pins all8 complete filters/isolation/bleed networks.
Positive and hostile tests prove wrong diode polarity, feedback-bypass, wrong
programmer values, missing caps and faster buck ramp do not silently pass.

Panasonic positive capacitance envelope uses1.2 tolerance x1.3 endurance x1.1
solder. Negative hold envelope0.8 x0.7 x0.9 is likewise explicit. Ceramic
startup-high uses1.1 tolerance x1.15 temperature; hold-low uses0.34425.
The full conservative ADC charge inventory includes distinct internal/divider
banks, but is NOT a statement that they are all directly in the LDO feedback loop.
Both FILT feed/ESR paths are modeled separately for discharge, without credit
for ADC load current. With1.2ohm dump and2ohm total per-bank feed/ESR screen,
90–10 fall is about6.34ms at3V3 and8.02ms atFILT; tails to5%/1% are also
reported (FILT~11.02/16.90ms). Cirrus'10ms rise/fall requirement does not define
measurement endpoints here; 90–10 is a declared screen, not a silently assumed
vendor interpretation. Actual ramp compliance remains a first-article row.

AP63205 4ms soft start is TYPICAL, not a guaranteed minimum. The screen uses
raw capacitance plus the correct linear-ramp precharge current
C_hold*dV/dt*(1-exp(-T/(R*C_hold))). It includes min frequency, initial20%
inductance tolerance and an additional20% DC-bias engineering allowance.
The3.5ms known-bad must fail this assumed-startup screen. Hiccup is not a rescue
mechanism; the primary text's cycles-versus-milliseconds inconsistency is not
resolved by choosing the favorable line. Output-bank LDO charging is separately
screened against both2.3A LDO current limit and2.5A buck peak limit.

The full-state reverse model requires held input remain above LDO output;
nominal-model minimum margin~296mV with1.5ms delay and20mA hot diode leakage.
Dump resistor total energy is bounded by0.5*C*V^2; hot repetitive pulse/RDS
and1ohm feed pulses need actual current/time curves and temperature measurement.

Yageo RT primaryV17Feb12,2026 gives B=.1%, D=25ppm/C. The screen includes
65C temperature span and an additional0.05% PROTOTYPE engineering drift
allowance per resistor. This is NOT the primary life/reflow guarantee:
rated endurance and solder tests permit0.5%+0.05ohm individually.
Consequently long-life worst-extreme divider margins are NOT CLOSED by these
parts/values. Do not present current conditional prototype numbers as an
all-life guaranteed design. Primary drift extremes are an explicit hostile
contrast in tests and may require higher-stability parts before qualification.

At85C,0.1uA specified switch leakage times101k is10.1mV. Published5pC TYP
charge injection into0.95nF is5.26mV; this is not a worst-case bound.
Published70pF CS(OFF) is source capacitance, not a guaranteed S-to-D coupling
capacitance; no large-step feedthrough number is derived from it.
1nF each contributes0.5nF differential loading versus15nF original; measure
active-filter stability, gain/phase, THD/noise, crosstalk and turn-on pops.
TMUX THD at0.5Vpp/600ohm is typical and does not prove1.2Vrms carrier audio.
Charge-injection, large input step and partial-VDD behavior remain measurable
prototype obligations under ADR0007, not claimed laboratory results.

## Promotion boundary

Source-only candidate. POWER-COLD/START/FALL/LOOP/REVERSE/AUDIO/DRIFT/THERMAL
remain explicitly OWED; no reviewer approval or power-state qualification is
claimed. Source conditional screens do not authorize route, release or order.
All former PCB, ERC, catalog allocation, reviews and checkpoint receipts are
stale for the new population. Rebuild to its actual source gate and report that
gate exactly; do not resume through a review or sourcing stop in this task.
