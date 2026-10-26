# LS20 — whole-board construction/routing disposition

Astra, 2026-10-08. Owning engineering recommendation for independent review,
not a layout-seal receipt, fabricated-board guarantee or physical qualification.
Recommend acceptance of the isolated 7628A carrier and unchanged 7628 pod at
routing, subject to independent exact-subject review and root issue/check.

## Exact candidate and measured verification

Manifest: `03_src/recovery/ls20-routing/candidate1/manifest.json`.
Fresh output: `06_build/recovery/ls20-routing/build1`.
Carrier native SHA256 `f8604fc5c77afe89df9423c763f5e6ee807c38ec112f0bd1ed74b7e310bb5a98`;
pod `05006b0a049a88cdad87c33dd8cd9d2a61bae72491b208e1ff1e89e9c687119b`.
Build and root strict native replay finished exit0. Both boards have zero opens
and zero physical DRC faults, without ignored checks. Carrier395/pod88 library,
text-height and silk findings remain visible, to be resolved by the retained
LS16 finishing work after explicit layout re-adoption; this is not final DRC.

The independent inventory proves source equality outside the carrier stack,
including unchanged settings and pod. New refilled pod is byte-identical to
LS15 build3. The carrier has142 footprints,92nets,1171segments,182vias and23
rule areas. The new `layers1/native-evidence.json` independently extracts fresh
filled geometry/returns, and all eight individual copper PNGs were visually
inspected by the author. Both inner layers are GND reference planes with local
antipads and the retained Pico exclusion, not deliberately split signal planes.
F/B routes, power trunk, ADC cluster and repeated connector cells remain intact.
Fresh `carrier-geometry.json`/`pod-geometry.json` from tools/routing_geometry.py
have zero via-drill-in-SMD overlaps and zero annulus-to-land findings at the
inherited0.15mm allocation. Carrier has zero track/via incursions in the inherited
Pico rectangle156.91,2.05,173.09,53.05. These are native geometry checks, not3D
assembly proof. New nominal mating acceptance separately binds the same source.

## Construction and clock: explicit prototype design basis

Use named JLC04161H-7628A for carrier only: nominal1.6mm,four layers,1ozouter/
0.5ozinner. Native sequence matches the published0.218mm7628+0.0764mm1080
outer gaps,0.865mmcore,and mirrored lower gap. Public snapshot:
`06_build/recovery/ls20-routing/jlc-stack.html`, SHA256
`4684177be0c602d7195e537c0495764d9543b24128dbb0084fdc20d28c7219d4`.
The listed copper+dielectric sum is1.5542mm, not exactly1.6mm; do not invent
extra material to reconcile nominal finished thickness with the published table.
Order-day selection must explicitly retain this stack, layerroles,copper and
material basis. Reject/review substitutions or conflicting fabrication offers
before ordering. No per-ply min/max or guaranteed±20%dielectric tolerance is
asserted; no unnecessary precision-impedance requirement is introduced.

Adopt LS19's independently reviewed prototype application judgment on this
actual candidate, including its limitations. All four MCLK nets remain32.115mm
F.Cu, zero vias, with unchanged68/56/56ohm damping and both PCM1864receivers.
New25um center/edge sampling finds no uncovered MCLK sample over either GND
plane. LS17's changed-stack models therefore retain their actual geometry:
27.323pF under its jointly stressed0.8gap case against30pF rating; changed-stack
sampled SCKI overshoot24.414mV and minimum modeled high/low dwell24.846/33.160ns.
These are conditional models, not measurements or guaranteed part extremes.

Retain a SINGLE100mV combined residual source/receiver/reference allocation,
separate from simultaneous local3.0–3.6V operating rails. Same3V3/GND domain,
short same-side local bypass paths, two connected ground planes and independently
damped branches support the prototype allocation jointly. Increasing the outer
gap raises the modeled7.31mmtrace-only return term2.499→2.990nH; that is not
a full-loop maximum. The favorable capacitance change does not cancel this
inductance. I judge the modest absolute change compatible with the LS19 local
charge/storage/damping argument, not proof of every undocumented current pulse.
Do not claim coupled-PDN simulation,30pF/8ns maker guarantee, or physical absence
of repeated crossings. Existing source-model artifacts and failed sensitivities
remain retained. Actual rail-range violation, excess pin excursion or extra
threshold crossings invalidate this prototype admission and require correction.

## Every affected signal and return family

**BCK/LRCK/TDM:** actual summed lengths131.312/121.877/129.398mm, two vias each.
Fresh native extraction retains six nearest GND stitching ties0.8,0.800001,
1.74039,0.8,1.2,1.5mm, connected into both filled planes. Do not repeat RT7's
inaccurate shorthand1.5mm maximum. Increased outer separation changes impedance
and loop area but introduces no new gap, branch, layer change or load. At a
deliberately high effective er5.4, a0.132m propagation scale is about1.02ns,
small compared with81.38ns nominal BCK halfperiod and16.38ns margin over the
65ns minimum; this is not an edge/setup-hold proof. The unchanged short local
branches, explicit return stitches and low loading support prototype routing;
fast edges and TDM slot ownership still require the retained first-article
timing/firmware qualification. No claim follows from clock frequency alone.

**I2C and buzzer controls:** SCL/SDA221/198mm with5/4vias are unchanged open-drain
control routes. Larger plane separation reduces their distributed capacitive
component; pullups, receiver count and external cable topology do not change.
Eight BUZZ_GPIO routes22–170mm charge local MOSFET gates; they do not carry the
30mA pod buzzer current. Eight cable BUZZ_N paths39–45mm retain their independent
returns and default-off control. Their state-transition interference remains a
qualification case, not inferred absent. USB D+/D− remain on the Pico module;
there is no newly altered carrier USB controlled pair to qualify.

**All16ADClegs and eight cable cells:** ADCleg lengths39.5–93.6mm,0–5vias and
unchanged input protection/coupling/2.7kohm/2.2nF filtering are explicitly covered.
The changed dielectric lowers the board-to-ground capacitive contribution rather
than altering the dominant2200pF filters or cable model. Millimeter-scale mismatch
is insignificant as flight time at8kHz; component/filter mismatch, noise and
frequency-dependent phase remain real. The stack increases field spread and
potential lateral coupling, but no analog trace is newly moved alongside the
digital bundle and both reference planes remain. This is a reasonable prototype
audio layout, not measured crosstalk/SNR or guaranteed localization performance.
Port shunts return near cable-entry cells, ADC bypass/reference returns remain
at the ADC cluster, and the existing plane topology does not force buzzer/power
current through a narrow analog-reference neck. No split ground is introduced.

**Power, thermal and interplane effects:** retain protected12V input and eight
fused50mA pod allocations,630mA total planning load,140mA external3V3 and300mA
5V model. Copper widths/cross-sections and lateral current paths are unchanged:
0.6mm12Vtrunk,0.3mm3V3,0.4mm5V/VSYS. For scale only,0.2925m of0.6mm×35um
copper at0.0175ohm·mm²/m is0.244ohm; putting the entire0.63A through its whole
summed length gives0.097W distributed loss at room temperature. Actual branch
currents are distributed. This is not a full hot-copper or connector loss bound.
The substrate change does not increase these Joule losses; it can change heat
transfer into the planes and HF return inductance. Retained surface copper,
through-via thermal paths and plane areas therefore support the same prototype
power allocation, but unchangedXY is not claimed to prove identical temperature.
RECOMcase<=90C, diode heating and loaded rail measurements remain explicit
qualification limits. Pod LDO construction and94.9C modeled junction at60Cair
are unchanged, not recalculated as a carrier result.

Both inner planes are GND, so reducing core1.065→0.865mm increases GND-to-GND
coupling, not power-to-ground decoupling. Plane stitches still provide galvanic
return; no power-plane capacitance is silently credited. Local oscillator and
ADC decoupling must carry switching charge, with operating limits retained.
12V-only operation, moduleD1-only removal, external reverse diode and off-state
charge-sink protections are circuit invariants, unchanged by this construction.

## Boundaries and next owner

Keep pod7628: its source, settings and refilled native are unchanged and no
clock-driven construction benefit applies. Its four layers were nevertheless
rebuilt/replayed and inspected, including microphone/buzzer separation and GND.
Carrier/Pico nominal thickness, reliefs,23keepouts and source-defined pad/group
identity remain. Actual module seating, hand solder, connector/cable access,
enclosure/weather/thermal/acoustic qualification remain required; unspecified
enclosure fit is not certified.

This report recommends accepting the complete changed-stack routing prototype
case, not deferring a discovered contradiction. An independent rejection names
its causal owner. After root routing issue/check, layout must explicitly adopt
the new receipt and replay preserved LS16 cosmetic finishing, with all four
layout obligations independently dispositioned. No old layout hash is refreshed
to masquerade as changed-board acceptance. Firmware, physical measurements,
manufacturing exports and final release remain separate, incomplete gates.
