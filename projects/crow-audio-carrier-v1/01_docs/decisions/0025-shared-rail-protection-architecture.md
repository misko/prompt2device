---
id: '0025'
date: 2026-09-09
status: accepted
tags: [analog, power, protection, topology]
---
# ADR-0025 — shared ADC/amplifier rail with passive external bias

## Context and decision boundary

The fresh, time-bounded D-BACK commission selects and implements an electrical
source correction, not a routed or qualified board. CAR-F12 remains REASSESS4/6,
one non-improving attempt, no pending launch; no investigation or milestone
is created. D6/ADR0007 and all existing release/order holds remain binding.
The exact brief, eight CS5308P channels, 1.2 Vrms differential input, eight
0.10 A spokes, header minimum10.8 V, unchanged pod, no hot plug and no
firmware are preserved. Correct audio during shutdown is not required.

## Three arrangements considered

| Arrangement | Deciding dependency | Decision |
| --- | --- | --- |
| Existing independent5V amplifier and held3V3 ADC with switch/dump sequencing | Relative rail, retained reference and isolation states must keep ADC pins in range | Not selected. Missing timing maxima alone are not a demonstrated failure. |
| Shared3V3 ADC and eight OPA2320 duals; reverse-protected regulator; passive external bias; bounded rail bleed | Realized amplifier/ADC rail tracking and node discharge must satisfy the explicit relative-voltage budget | Selected and electrically implemented. Fewer independent energy domains; physical-source integration remains open. |
| Independent5V driver with passive ADC attenuation/current limiting | A fixed ratio guaranteeing3.4V from a5.4V source is at most0.63, incompatible with the retained unity1.2Vrms receive function without another gain stage | Not selected; no wider catalogue search. |

## Implemented source correction

This supersedes ADR0023's independent-rail/ninth-buffer arrangement and
ADR0024's10k retained-reference divider selection. OPA2320 identity and0.1%
precision requirements are retained here; their former topology is not live.

U_LDO is exact A-grade LT3041ADE#TRPBF, ADI LT3041 Rev.A April2026,
DFN14 plus EP15. IN1/2/3 and PGFB8 connect to5V_LDO_HOLD; EN5 remains
LDO_EN; ILIM7, GND10/11 and EP15 are GND; OUTS12 and OUT13/14 connect
to3V3_ADC; VIOC4 and PG6 float. PGFB=IN disables fast startup.
R_LDO_SET is exact RT0603BRD0733KL,33k,0.1%,25ppm/C. C_LDO_NR4/5
each1nF remain SET bypass; this does not inherit the vendor1uVrms noise claim.
The two distinct local output positions C_LDO_OUT and C_OPA_BULK each use
the existing47uF X7R part. Each must realize at least10uF, ESR<20mohm and
ESL<2nH with the manufacturer's local return/Kelvin topology.

All eight OPA2320 supply pins and their100nF bypasses now share3V3_ADC.
The separate5V_OPA feed, its470uF reservoir, second surplus47uF and third
bleed resistor are removed. R_OPA_BLEED1/2 are now100ohm each in series
across3V3_ADC. The name is retained only for stable source references.

U_AFE9 and its isolated4.7uF output reservoirs are removed, not left as
unpowered output-pin energy paths. Each external bank is a passive equal
1k/1k divider using RT0603BRD071KL,0.1%,25ppm/C, bypassed by its existing
10uF+1uF. Eight100k bias legs load each bank. ADC VMID1/2 remain separate,
locally bypassed internal reference outputs. All16 positive-input10k current
limiters and the actual Cirrus-derived unity/filter feedback topology remain.
All16 ADC-side pulldowns become10k RC0402FR-0710KL; each1nF C0G remains.
TMUX2821, held control rail, supervisors and the1ohm switched dump remain
for mute/reset/discharge operation. Their relative disable time is no longer
the primary ADC voltage barrier.

The15nF cross-leg filter capacitor in each channel is replaced by four
instances of the existing GRM2195C1H153JA01D/C97907: two15nF shunts from
each FILTER leg to GND,30nF per leg. Differential equivalent remains15nF.
This is a deliberate common-mode loading change, not an exact vendor filter
copy. Root's read-only check exposed why the bridge could not support the
earlier passive bound: simultaneous outputs collapsing to zero can discharge
common mode faster than stored differential charge, producing a negative
filter voltage even when both driver outputs are nonnegative. That is a
counterexample to the proposed assumption, not a measured/reachable silicon
waveform. Independent grounded RC legs remove this cross-leg transfer; they
remain in the convex range of their own initial/input voltage. The22-test
suite includes that algebraic counterexample and rejects bridge restoration.
Common-mode stability, increased ground return load, all32 capacitor positions
and their actual local loops require fresh physical-source/first-article review.

This supersedes the independent rail and buffered external-reference choices
in ADR0008/0009/0021/0023/0024 only where changed above. Upstream input
reverse isolation, spoken power protection, ADC mode/reset and clock contracts
are retained. Historical numerical screens are not evidence for this source.

## Bounded electrical argument

`03_src/check_protection_architecture.py` validates the actual333 components /
937 pins, all retained power pin/value guards, eight ADC/amplifier shared
supplies, and the existing analog topology checker. It performs algebra only.

- Cold start and correlated restart: unchanged pods are bounded0..5.5V at
  their outputs. Coupling-cap retained voltage is conservatively bounded
  +/-5.605V using an explicit1uA per-leg leakage screen and105k bias path.
  All16 positive input currents at a3.4V rail barrier total12.977mA; the
 200ohm rail bleed at its+5% limit sinks16.190mA. After another100uA total
  unexplained-current reserve,3.114mA margin remains. Each passive bank is
  below the rail at this barrier (2.08V), so its top resistor cannot pump it.
  Worst positive/negative input limiter currents are1.169/0.590mA, below
  OPA2320's10mA input-current limit. This is an envelope argument, not a
  correlated proprietary startup simulation. The old500ohm bleed fails it.
- Removal/brownout: ADC and drivers lose the same rail, including when
  their bias capacitors retain charge. A dump at minimum0.95ohm with only
  two47uF ceramics credited at0.34425 effective factor has30.742us passive
  rail time constant. An additional0.30A rail load PLUS up15mA LT3041
  reverse-overshoot recovery sink is charged, not omitted. Maximum rail
  slew is120334V/s. The16 ADC10k/1nF nodes have maximum10.605us time
  constant. At Vpin=Vrail+0.3, both affine derivative coefficients point
  inward; positive rail voltage only strengthens that result. Old100k
  pulldowns fail this conservative discharge boundary.
- With the switch conducting,10ohm output-filter lag is bounded41.127mV
  using each30nF shunt plus1nF ADC capacitor at maximum tolerance.
  The combined relative-pin engineering allocation is243.759mV:
  41.127mV filter lag +52.632mV from50pC switch charge +100mV return
  error +50mV amplifier output tracking/overshoot. This is below300mV,
  with56.241mV unused margin. The50pC allocation is NOT the vendor's
  guaranteed maximum (5pC is typical); likewise50mV output tracking is
  NOT an ideal clamp guarantee. These are explicit falsifiable first-article
  envelopes, including negative pin excursions and partial-supply operation.
- LT3041 explicitly protects OUT against IN being grounded, intermediate
  or open. This removes TPS7A92's OUT<=IN+0.3 dependency. It does not
  imply zero output discharge: SET/OUTS paths and up15mA recovery remain.
  Positive residual FILT/reference return energy only slows the conservatively
  fast discharge bound; it still belongs in full startup charge accounting.
- Normal1.2Vrms differential audio gives0.84853V peak per leg. The
  initial/tolerance reference screen is1.60938..1.68068V and signal window
 0.76085..2.52921V on3.23..3.35V supplies. Post10ohm feedback retains
  unity gain; extra10k shunt loading changes switch-only gain by no more
 31.6ppm under the0.3ohm Ron allocation. Pulldown DC load is2.863mA;
  the all16-leg audio supply triangle bound is21.012mA. This does not
  promise unmeasured distortion, stability or production noise.
- Shared3V3 steady budget is222.374mA of230mA; local5V is250.414mA
  of300mA including25mA regulator ground current. Upstream bound remains
 0.985346A below1A; the unchanged header budget remains10.896V.
  A-grade SET/resistor/offset allocation yields3.255199..3.344999V;
  engineering upper rail allowance changes3.34 to3.35V, not the brief.
  Reference-board thermal arithmetic gives0.556W and105.6C junction at
 85C ambient/37C/W; actual copper/thermal performance is not established.
- Actual nominal charge inventory is1109.36uF; declared tolerance,
  soldering/endurance upper inventory is1827.280uF. A1A available-charge
  engineering allocation minus0.23A load plus SET99% allowance gives
 8.389ms. It is not a guaranteed LT3041 startup-current trajectory nor a
  proof of the ADC's exact supply-ramp endpoint convention. Existing dump,
  precharge and capacitor pulse/thermal behavior still require qualification.

## Physical-source stop and next executable action

Generation is NOT admitted by this ADR. The old `route.yaml` owning
`prep.seed_stubs.stubs` block formerly around lines165-225 connected
TPS OUT1/2,IN9/10,GND4/6/EP11 and R_LDO_BOT/C_LDO_NR returns. Those
entries are removed, along with every old3V3 seed and TPS-specific width/
quiet-pour exceptions. Replaying them would connect new input/output/control
pins incorrectly. New floorplan anchors are provisional, not accepted copper.

Next source owner must reconcile selected-part adjacency/keep-short/thermal
rules and source fixtures for the333-component LT3041/passive-reference
population; create and grade the exact IN1/2/3, OUT13/14, OUTS12, SET9,
GND10/11/EP15 and two output-capacitor local loops. Reopen all3V3 branches
for230mA total allocation and actual pin/return currents. Run focused source
tests and full package/placement/route-contract tests with ZERO unresolved
identity, missing-owner, collision or incompatible-rule failures. Do not merely
update old expected counts or waive missing routes. Only then may the owner
archive the prior prelayout cohort and regenerate under its own authority,
followed by independent native pin-map/package/parity/placement review.

Later controlled first-article validation must falsify the explicit startup,
rail-relative tracking,50pC/100mV/50mV budgets, ADC supply ramp, all8channel
audio stability/distortion/crosstalk, capacitor ESR/ESL and hot thermal/drop
allocations. This is separate from physical-source integration and cannot be
substituted for it. Exact public LCSC identity was found for LT3041 but stock
was zero; no PCBA allocation, order, upload, native mutation or release occurred.

## Evidence

### Source-integration follow-through — 2026-09-10 01:48 UTC

The source owner completed the local LT3041 IN/OUT/OUTS/SET/GND geometry,
dual output-capacitor returns, thermal hosts and shared-rail amplifier branches.
The full source suite passes 309/309, including exact native-library geometry,
current net ownership and hostile pin/value/clearance cases. The earlier
physical-source stop above records the decision's original handback, not the
current work queue. See the schematic journal for command/log identities.

The existing protection checker now runs before TSX on the fresh arm and on
exported native pins before downstream work on all full/resume/reuse arms.
Its source-only command passes; the actual stale TPS native netlist is rejected.
No independent native review, routing, filled-return qualification, release or
order follows from these source results. Archive and replace the obsolete
prelayout/generated cohort through the full conductor next; do not replay its
old checkpoint or restore its retired parts to satisfy historical fixtures.

See the dated protection-architecture report, exact part dossiers and
`06_build/verification/protection-architect-20260909-*` receipts. The
accepted decision is a useful partial source correction, not CAR-F12 closure.
