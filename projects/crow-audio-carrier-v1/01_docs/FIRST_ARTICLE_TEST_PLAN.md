# Crow audio carrier v1 — first-article test plan

status: PLANNED — NO HARDWARE RESULT
order_status: FIRST-ARTICLE ORDER AUTHORIZED — LIVE UPLOADER CHECK REQUIRED

## Current shared-rail source — 2026-09-12

ADR0025 supersedes the former independent 5V_OPA supply and ninth reference
amplifier. Current population is 333 components: eight OPA2320 duals share
3V3_ADC with CS5308P, powered by LT3041ADE#TRPBF; the two external bias
banks are passive 1k/1k dividers. VMID1_EXT/VMID2_EXT retain the planned
1.60–1.70 V acceptance window. ADC_VMID1/2 are separate internal-reference
outputs. No removed VMID buffer or TPS7A92 rail is a current probe target.

The bounded steady estimates are 222.374 mA on shared3V3 (230 mA allocation),
250.414 mA on local5V (300 mA allocation) and 0.985346 A total with eight
0.10 A spokes. These are source calculations, not hardware readings.
The 0.20 A first-power current limit below is not proof of adequate startup
headroom. Qualify source foldback and an instrumented startup procedure
before physical power; never raise the limit during an unexplained failure.

Retain cold start, slow brownout, removal after a low-input dwell, correlated
restart, mute/reset/dump operation, reverse recovery and capacitor/thermal
qualification. Verify ADR0025's explicit 50 pC switch-charge, 100 mV return
error and 50 mV amplifier tracking allocations, including negative ADC-pin
excursions. Capture shared rail, held input, SET, external/internal references,
FILT banks, enables and all relevant currents. Validate all 32 grounded
filter shunts and their local return loops under full-level eight-channel
audio. The 8.389 ms charge/SET99 screen is not a guaranteed supply ramp.
Noise, distortion, settling, drift and actual LT3041 thermal behavior remain
measured obligations; no reference-board thermal or noise result is inherited.

## Authority and scope

This is the controlled procedure for one serialized, fully populated carrier.
It is source-side planning, not evidence that a board was fabricated or passed.
The executable first-power population and rail limits remain
[`03_src/rules/first_article.yaml`](../03_src/rules/first_article.yaml); the
spoke, power, protection and digital-interface rule files remain the design
authority. A result may be called `FIRST_ARTICLE_TESTED` only after every
applicable row below passes on the same identified article and the findings
ledger is deliberately updated.

The plan covers carrier electronics and its immediate COTS interfaces. It does
not establish weatherproofing, lightning or building-entry safety, a production
process, or biological crow identity.

## Evidence record

Before measuring, assign the PCB a serial number and record board revision,
assembled BOM digest, operator, UTC timestamps, calibrated instrument IDs,
probe configuration, ambient temperature and the exact MCHStreamer/cable/Pi
identities. Put the structured first-power record at
`01_docs/journal/first_article.json`, in the schema consumed by
`first_article_check.py`. Store raw waveforms, logic captures, audio files,
thermal images and photographs under `06_build/first_article/<serial>/`; write
a SHA-256 manifest and reference it from the journal record. A release copies
the record, manifest and reviewed evidence into its verification directory.

Never copy a reading from another board, combine partial-population evidence
with the fully populated stage, or convert a missing result into a pass.

## Preconditions

- [ ] Live JLCPCB pre-layout and final allocation holds are closed for the exact
      assembled identities, or this is an explicitly hand-assembled engineering
      article whose deviations are recorded.
- [ ] The exact schematic, netlist, PCB, BOM and CPL are immutable and have
      passed their required machine and human reviews.
- [ ] `first_article.yaml` exactly matches the installed reference-designator
      set; substitutions and rework are recorded before power.
- [ ] The purchased MCHStreamer, two exact `TCSD-06-D-04.50-01` cables and the
      miniDSP-authorized TDM8 image have recorded identities and provenance.
- [ ] The isolated bench supply has overvoltage protection and a known
      prospective-short-current envelope. The installed harness is never used
      for an 8 A trip-time experiment.
- [ ] DMM, oscilloscope, differential probes, logic analyzer, audio
      generator/analyzer, eight electronic loads, thermal camera and cable
      fixtures are in calibration and share a deliberate grounding plan.

## Immediate abort rules

De-energize and mark the run `ABORT` for unexpected polarity, wrong or unstable
resistance, visible assembly damage, smoke/odor, oscillation, any rail outside
its card limit, bench current above 0.120 A after startup with spokes unloaded,
current-limit operation that was not part of the declared step, excessive part
temperature, MCH/carrier back-power, or loss of protective earth/isolation.
Investigate and revise the design or plan; do not raise a limit to make a board
pass.

## 1. Identity, inspection and unpowered checks

- [ ] Photograph both sides, serial label, pin-1 marks and all manual/THT work.
- [ ] Confirm J1–J8/J9/J10/J11 orientation, every polarized diode/capacitor,
      Q_IN orientation, ADC/reset/clock IC orientation and intended no-connects.
- [ ] Confirm exposed-pad soldering for Q_IN and U_ADC using the approved
      inspection method; record the method and images.
- [ ] Reconcile the literal population to `fully-populated-first-power` with no
      missing or extra refdes.
- [ ] With all external modules and loads disconnected, wait for capacitors to
      settle and measure every resistance probe/range in `first_article.yaml`.
- [ ] Verify J9 and all eight spoke pin identities end to end before mating any
      cable. Measure continuity of all sixteen RJ45 shell lands on CHASSIS, each jack
      to the bonded panel, and isolation from signal GND.

## 2. Controlled first power and rails

1. Set the isolated supply to 0 V and a 0.20 A current limit. Connect only J9,
   observing polarity; leave all spokes and both MCH cables disconnected.
2. Raise to 11.4 V while capturing input voltage/current and startup inrush.
   Inrush is a waveform result, not the steady-state `no_load_current` value.
3. After startup settles, record the same bench-supply current observation for
   every card rail. It must be no more than 0.120 A; the repeated card rows do
   not represent separate per-rail currents.
4. Measure `12V_PROTECTED`, `5V_BUCK`, `3V3_ADC`, `VMID1_EXT` and `VMID2_EXT` at
   the exact probes and limits in `first_article.yaml`. The protected rail floor
   is 11.16 V at the 11.4 V admitted input.
5. Repeat the steady-state rail/current observations at 12.0 V, removing power
   and rechecking resistance after any abnormal result. The present card limits
   several probe rows to 12.0 V input. The required 13.2 V functional corner
   needs a reviewed card/procedure update before that test; do not exceed the
   current card or copy a 12.0 V result into the 13.2 V acceptance row.
6. Run `first_article_check.py` against the complete structured record. Only
   `FIRST-ARTICLE AUTHORIZED` permits the powered functional tests below.

## 3. ADC reset and clocks

- [ ] Capture `3V3_ADC`, supervisor clear, monostable output and
      `ADC_RESET_N` from power application through steady operation at each
      admitted input corner.
- [ ] Confirm reset begins high, remains high for at least 2 ms after the ADC
      supply is valid, pulses low for at least 1 ms, then returns high without
      a second pulse or firmware action. Record measured extrema, not only a
      representative screenshot.
- [ ] Repeat cold-start and brownout/recovery cases sufficient to expose the
      supervisor and timing-capacitor corners. Any ambiguous reset is a hold.
- [ ] With the authorized MCH configuration connected, measure 24.576 MHz
      MCLK, 12.288 MHz BCLK, 48 kHz one-BCLK FSYNC and eight 32-bit TDM slots.
      Decode DOUT as 24-bit samples in the declared slot order.
- [ ] Retain at least one continuous 120-second eight-channel capture with no
      framing discontinuity, missing channel, repeated slot or clock-domain
      change. Network arrival time is not a sampling-time measurement.

## 4. MCHStreamer independent-power matrix

Retained digital-interface amendment: the current population includes U_TDM_SCH,
R_TDM_PD and C_TDM_SCH. Before acceptance, capture TDM_RAW and TDM_CLEAN
with reset asserted, clocks stopped and after a transmitted high releases.
Verify ADC-plus-PCB Hi-Z leakage allocation20uA, raw total capacitance20pF
allocation, raw settled low0.4V/high2.8V targets and the added0.4mA DC-load
budget at the actual ADC supply/temperature. Cirrus input leakage and drive
register are not output guarantees. No total-capacitance maximum follows
from the Nexperia5pF or TI4pF typical inputs.

Capture U_TDM.2 edges against the TI10ns/V requirement; Nexperia tpd is not
an output-slew bound. Measure the complete MCH-BCLK-to-returned-TDM path,
including both cables, U_CLK, ADC launch/Hi-Z enable, both data buffers,
series resistors, receiver thresholds, actual BCLK duty and remote setup/hold.
ADR0005's6ns path,5ns setup and45% phase allocations are not vendor limits.
Record the minimum real setup/hold margins, including the last transmitted
bit and post-reset first bit; a correct short digital capture alone is not
timing closure. Reserve5mA inside—not in addition to—the existing150mA
ADC/reference suballocation within the230mA shared3V3 budget, and capture slow-input/dynamic conditioner current.
Any failed allocation stops qualification and reopens source design.

Exercise every row with both exact cables, then repeat the split-cable cases.
Record carrier 3.3 V, J3 sense, USB current and all four TDM lines.

| Carrier | MCHStreamer | Required observation |
|---|---|---|
| off | off | All interface lines unpowered. |
| on | off | Clock inputs remain low and DOUT buffer remains disabled. |
| off | on | Ioff boundary prevents carrier-rail back-power; no carrier logic becomes powered. |
| on | on | J3 sense enables DOUT and the MCHStreamer remains the sole clock master. |

- [ ] J10 without J11 leaves DOUT disabled.
- [ ] J11 without J10 creates no false clocks or driven remote load.
- [ ] Across the admitted temperature and 3.0–3.6 V interface-rail screen,
      measure each loaded clock low below 0.4 V and high above 2.4 V, with
      the TI maximum input-transition rate of 10 ns/V respected. Confirm
      the 0.4 mA per-clock DC load budget and total additional unpowered
      module/cable/PCB leakage allocation of 20 µA. Retain actual module
      hardware identity; the miniDSP manual does not guarantee those limits.
- [ ] Measure `TDM_SENSE_G` below 0.4 V absent and above 2.8 V present;
      measure `TDM_OE_N` above 2.4 V disabled and below 0.4 V enabled.
      Verify the retained20 µA Schmitt-input/module/cable allowance and
     25 µA total OE load budget under actual test conditions. U_OE is now
      a genuine Schmitt inverter, not the former protected MOSFET plus RC
      pull-up. Check actual U_TDM OE edges meet10 ns/V; no propagation-delay
      number has been substituted for a guaranteed output-slew maximum.
- [ ] Capture all power and cable transitions separately from settled-state
      tests. The DC bias calculation does not authorize glitch-free live
      insertion. Keep power off while changing cables until qualified.
- [ ] Continuity, pin 1, cable rotation, retention, labels and hot-plug/power
      ordering agree with the signed physical-qualification record.

## 5. Analog channel and slot qualification

Machine-readable capture identity is in `03_src/adc_channel_map.json` under
`capture_requirements`. `check_analog_paths.py --source-only` checks its exact
required fields and8/8 impulse obligations, emitting the current source
SHA256, ID, slot table and `capture_identity_status: OWED`. Carry that binding
into the bench record. `rules/first_article.yaml` remains the staged
first-power/rail card; it does not authorize a completed capture.


- [ ] Confirm both passive external VMID nodes remain 1.60–1.70 V over input corners,
      representative signal loading and the thermal screen.
- [ ] Inject a calibrated balanced signal into one spoke at a time. Verify
      connector polarity, ADC channel 1–8 and TDM slot 0–7 with an 8/8
      denominator; unstimulated channels must not be silently remapped.
      Use ADR0027 / `03_src/adc_channel_map.json`: slots0..7 must identify
      pods4,3,2,1,5,6,7,8. Retain map ID/digest and actual USB-channel/ADC-slot/
      pod-coordinate table with each stream epoch and120-second capture.
      Reject missing, duplicate, swapped, inverted or unstable channel identity.
      Do not silently apply the former pod-number-equals-slot-plus-one map.
- [ ] At low and mid frequencies, record gain, phase and leg symmetry for all
      eight AN0556 receiver cells and both VMID domains.
- [ ] Sweep amplitude through 1.2 Vrms differential at the carrier connector.
      Record THD+N, clipping margin and common-mode behavior. A numeric
      distortion/noise acceptance bound must be signed before the run; absent
      that system-level bound, data may be retained but this section is HOLD.
- [ ] With terminated inputs, record input-referred noise and the complete
      8-by-8 crosstalk matrix. Retain raw spectra and acquisition settings.

## 6. Exact cable and pod integration

- [ ] Repeat gain, phase, polarity, common mode, noise, stability and crosstalk
      with the exact selected 15 m factory cord. A nominal 4 m array radius does
      not select a 4 m cord; any shorter cord needs exact-source adoption first.
- [ ] Use serialized pods and record which pod/cable occupies each carrier
      port. Verify a 120-second all-channel file can be reopened with its
      channel/slot identity intact.
- [ ] Freeze quantitative phase/noise/crosstalk acceptance limits from the
      localization/DSP budget before declaring this step passed. The 15 m
      design boundary is not a qualified maximum until these results pass.

## 7. Spoke-power load, fault and recovery

- [ ] Apply 0.100 A to all eight spoke outputs simultaneously. At 11.4, 12.0
      and 13.2 V input, four-wire measure J9, `12V_PROTECTED` and every J1–J8
      header. Each carrier output must remain at least 10.8 V.
- [ ] Record cold and hot branch/common-path resistance, input/PPTC/PFET loss,
      copper/header drop and temperature. Do not average eight ports to hide a
      failed port.
- [ ] In a separately risk-reviewed, current-bounded fixture, fault one branch
      at a time and prove the other seven remain powered and recover cleanly.
      Record source foldback, branch/common-PPTC selectivity, trip energy and
      recovery. Prospective fault current must not exceed the selected part's
      10 A rating, and no 8 A installed-harness trip test is authorized.
- [ ] Repeat the one-fault/seven-healthy observation for all eight branch
      positions, with no damaged cable, connector or protection device.

## 8. Thermal and closeout

- [ ] Soak unloaded and all-eight-loaded configurations at each admitted input
      corner and the approved first-article ambient points. Record equilibrium
      temperatures for F_IN, Q_IN, U_BUCK, U_LDO, U_ADC, all branch PPTCs,
      connectors and representative analog channels.
- [ ] Confirm rail, reset, clock and analog limits remain valid during and after
      thermal soak. Component temperatures must remain below their cited
      ratings with the declared measurement uncertainty.
- [ ] Power-cycle and reinspect the article; record permanent resistance,
      polarity, connector or solder-joint changes.
- [ ] Review every row as PASS, FAIL, BLOCKED or NOT-APPLICABLE with rationale.
      Hash the record and raw-evidence manifest. Open failures in
      `findings.yaml`; never edit a raw result into compliance.

Passing this plan permits only a `FIRST_ARTICLE_TESTED` carrier claim. Outdoor
deployment and production release remain separate system/environmental gates.

## ADR0022 — local buck input reverse isolation

On the generated/assembled candidate, capture12V_PROTECTED,12V_BUCK_IN,
BUCK_SW,5V_BUCK,3V3_ADC,5V_LDO_HOLD,PWR_EN,AUDIO_EN and feed/diode
current for ordinary J9 removal, slow brownout through dropout, removal after
a low-input dwell, and rapid restart with partial CT/ADC discharge. Verify no
sustained shared-spoke backfeed through D_BUCK_IN. Check100uA leakage,
100nC integrated reverse-recovery charge,1mA equivalent local reverse-port
control budget and320us isolation against the4.501285V conditional screen.
These are application budgets, not guarantees inferred from50ns trr. Preserve
exact recovery waveform, temperature, current and probe bandwidth in evidence.

Measure D_BUCK_IN cold/hot forward drop<=1.3V engineering allowance,
terminal temperature and repetitive startup current. The3x10uF input bank
upper initial37.95uF stores500.94uC/3.306204mJ at13.2V, not a bounded
inrush peak. Compare actual waveform with the exact US1B ratings; no arbitrary
pulse qualification from30A8.3ms half-sine. Verify the unchanged spoke floor,
1A common allocation and full ADC/OPA startup under minimum source input.


## RJ45 candidate qualification (supersedes former spoke harness instructions)

For the source-adopted Würth615008160221 jack and exact Weidmüller8909650150 cord, identify and serialize every sample. Inspect power-off T568B continuity1..8, shield continuity and absence of cross-shorts before power. Pin5 is AUDIO+,4 AUDIO−;1/3/7 are+12V and2/6/8 return. Verify all three power conductors individually before applying the combined100mA load. Measure finished15m hot loop at the admitted temperature; it must be≤2.2ohm and preserve≥10.5V at the pod from≥10.8V at the carrier. Contact allocation0.300ohm remains unmeasured.

Determine manufactured plug/latch/boot/sleeve axial and radial variation separately from jack seating, PCB/enclosure exposure and registration. Use calibrated dimensional instruments, sample identities, extrema and uncertainty; record bounds in the corresponding installed axial/radial tolerance rows. Compare the entire nominal end, including sleeve, to the reviewed model. Verify full mating, latch travel, release and restraint with all required neighboring connectors populated. Nominal CAD is not a zero-tolerance physical limit. Verify minimum67mm planned cable bend, straight run and dry IP20 zones.

Inspect bottom-side ESD clamp soldering, THT-tail separation, paste/fillets, access and rework. Verify carrier CHASSIS continuity and panel bond independently of GND; pod POD_SHIELD must remain isolated from signal GND. A pin-net label is not a measured shield bond.

UV resistance is not established by the exact primary sources. Obtain exact manufacturer environmental qualification or a suitable documented UV/weather qualification before outdoor deployment. A short fit test and PUR material name cannot close this hold. Known unsuitable material requires source/design correction. Retain ESD/noise/crosstalk/temperature and one-fault/seven-healthy tests. This plan authorizes no production purchase, powered fault test, or unattended outdoor deployment; the exact release may separately authorize only its controlled five-board first-article lot.
