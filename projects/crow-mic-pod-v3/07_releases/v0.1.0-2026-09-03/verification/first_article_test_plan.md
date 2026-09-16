# Crow microphone pod v3 — first-article test plan

status: PLANNED — NO HARDWARE RESULT
order_status: DO-NOT-ORDER

## Authority and scope

This procedure governs one serialized, fully populated microphone pod. It is
not evidence that hardware exists or passed. The executable first-power
population and rail limits remain
[`03_src/rules/first_article.yaml`](../03_src/rules/first_article.yaml); the
shared spoke contract and exact electrical rule files remain authoritative.

The plan qualifies the PCB with its exact capsule, harness and carrier test
fixture. It does not create an IP rating, lightning/building-entry claim,
production process or unattended roof-deployment approval.

## Evidence record

Record article serial, revision, assembled BOM digest, operator, UTC times,
calibrated instrument IDs, probe configuration, ambient conditions and exact
capsule/cable/carrier identities. Put the structured first-power record at
`01_docs/journal/first_article.json`. Store raw waveforms, audio, spectra,
thermal images and photographs under `06_build/first_article/<serial>/`, then
hash them in a manifest referenced by the journal record. A release copies the
reviewed record, manifest and evidence into its verification directory.

Every pass belongs to one identified article and configuration. Missing data,
part substitution or an unratified numeric threshold is `BLOCKED`, not PASS.

## Preconditions and abort rules

- [ ] Exact source, schematic, PCB, BOM/CPL, live JLC decisions and human
      reviews are closed, or hand-assembly deviations are explicitly recorded.
- [ ] The literal 33-ref population matches `fully-populated-first-power`; U2
      exposed-pad soldering and every J1/MK1 manual joint are inspected.
- [ ] The exact AOM-5024L-HD-R capsule, 4 m and 15 m Belden harnesses, carrier
      receiver and enclosure fixture are serialized and their polarity known.
- [ ] Current-limited isolated supply, DMM, oscilloscope, audio
      generator/analyzer, capsule-equivalent source, acoustic calibrator,
      thermal camera and ESD/EMC equipment are calibrated.

Immediately remove power for wrong polarity, resistance outside the card,
smoke/odor, oscillation, unexpected current-limit operation, more than 20 mA
steady input current with no signal, any rail outside its card, output clipping
below the declared envelope, or excessive temperature. Do not change a limit
to make the article pass.

## 1. Inspection and unpowered checks

- [ ] Photograph both sides, serial label, J1/MK1 wiring, pin-1 marks and all
      manual/THT work.
- [ ] Confirm J1, D1, D2, U1, U2 and U3 orientation; confirm R14 is exact
      4.7 kΩ/1206 and confirm U2 exposed pad,
      DNC/NC treatment and exact capsule lead polarity.
- [ ] Reconcile the population to `first_article.yaml` with no missing or extra
      refdes. MK1 is the hand-wired landing identity, not a direct-placement
      claim for an undimensioned capsule footprint.
- [ ] Verify J1 pin 1=`12V_POD`, 2=`GND`, 3=`AUDIO_P`, 4=`AUDIO_N` end to end.
- [ ] After capacitors settle, measure every resistance probe/range in the card.
      Check D1 separately in diode mode; do not interpret its nonlinear path as
      an ordinary resistor.

## 2. Controlled first power and protection

1. Leave the audio cable and capsule stimulus inactive. Set the isolated supply
   to 0 V with a 0.030 A current limit and connect J1 with correct polarity.
2. Raise to 10.5 V while capturing startup voltage/current and inrush. After
   settling, record the same bench-supply current for each card rail; it must
   remain no more than 0.020 A.
3. Measure `VIN_PROTECTED`, `5V_QUIET` and `VREF` at the exact card probes and
   ranges. Repeat at 12.0 V and 13.2 V.
4. Run `first_article_check.py` against the complete structured record. Only
   `FIRST-ARTICLE AUTHORIZED` permits the functional tests below.
5. With a separately declared 0.020 A current limit, apply reverse polarity at
   ambient and the admitted +70 °C hot boundary. Verify `VIN_PROTECTED` stays between
   -0.25 V and +0.05 V, the quiet rail remains off, and no component is
   damaged. Restore correct polarity and repeat the rail checks.
6. Load `5V_QUIET` to 20 mA; record regulation, ripple, dropout behavior and U2
   temperature rise. Protection waveforms or ESD tests require confirmed TVS,
   diode and PTC identities/polarities first.

## 3. Bias, gain and headroom

- [ ] With the exact capsule connected, measure its filtered bias plane,
      current and loading at input-voltage corners; compare to the characterized
      nominal 3 V through 2.2 kΩ condition.
- [ ] Confirm VREF and output common mode remain 2.35–2.65 V with no signal and
      throughout the declared signal sweep.
- [ ] Inject a traceable low-level sine through the capsule-equivalent source.
      Confirm AUDIO_P/AUDIO_N have equal magnitude, opposite polarity and the
      intended 18/11 V/V differential gain. Record gain and phase, not only a
      visual waveform.
- [ ] Sweep amplitude through the maximum 1.2 Vrms differential output. Confirm
      no clipping below that boundary and retain THD+N/headroom data. A numeric
      distortion/noise acceptance limit must be signed before the run; absent
      that system-level limit, the measurement is evidence but the step is HOLD.
- [ ] Measure quiet-capsule self-noise, frequency response and clipping through
      the admitted acoustic range, including the planned 110 dB SPL screen.
- [ ] Confirm acoustic polarity from pressure stimulus through carrier PCM; a
      wiring inversion may not be repaired only in an undocumented channel map.

## 4. Exact harness and carrier integration

- [ ] With the exact 4 m harness, measure gain, phase, common mode, noise,
      CMRR, stability and interference while the carrier and all other channels
      operate. Retain raw audio and spectra.
- [ ] Repeat the complete matrix with the exact 15 m boundary harness. The
      15 m value remains an unqualified design boundary until this passes.
- [ ] Exercise cable motion, mate/unmate cycles only while de-energized, and the
      approved shield/drain termination. Record connector latch, strain-relief
      and continuity observations.
- [ ] Repeat on the planned pod sample set and map every serialized pod to a
      carrier port. Freeze numeric gain/phase/noise/CMRR/crosstalk limits from
      the localization budget before declaring the matrix passed.

## 5. Thermal, ESD/EMC and mechanical enclosure

- [ ] Soak at input-voltage corners, representative signal/load and approved
      first-article ambient points. Record equilibrium temperature for U1, U2,
      F1, D1, D2, connector and capsule region; repeat rail/audio checks hot.
- [ ] Use a qualified, current/energy-limited facility procedure for ESD/EMC at
      the complete enclosure/cable boundary. Record waveforms and recovery.
      The selected TVS waveform is not a lightning-survival claim.
- [ ] Qualify capsule mount, acoustic port, windscreen, wire dress, strain
      relief, drainage, condensation path and connector service clearance.
- [ ] Cycle representative humidity/temperature and inspect for condensation,
      corrosion, acoustic drift and insulation damage. This engineering screen
      does not itself establish an IP rating or production lifetime.

## 6. Closeout

- [ ] Power-cycle, reinspect and repeat unpowered resistance/polarity checks.
- [ ] Mark every row PASS, FAIL, BLOCKED or NOT-APPLICABLE with rationale and
      evidence IDs. Hash the structured record and raw-evidence manifest.
- [ ] Open every failure in `findings.yaml`; do not edit raw data into
      compliance or promote the board based on a subset of tests.

Passing this plan permits only a `FIRST_ARTICLE_TESTED` pod claim. Roof
deployment and production release remain separate environmental, harness and
manufacturing gates.
