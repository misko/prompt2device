---
schema: 1
kind: pcb-human-report
report_id: 2026-09-01-dimensionality-identity-and-poe-addendum
title: Crow roof array — dimensionality, identity and PoE addendum
subtitle: Aperture and height tradeoffs, source-track versus individual identity, and an Ethernet-only external boundary
project: crow-roof-array-v1
date: 2026-09-01
status: SUPERSEDED
evidence_status: INCOMPLETE
---

> **Superseded, 2026-09-01:** P7 subsequently limited recognition to one
> 120-second file while the crow remains approximately stationary. The
> persistent-biological-identity conclusions and recommendations below are no
> longer current. This report remains the historical dimensional comparison;
> the geometry update is the
> [planar 8 m-diameter follow-up](2026-09-01-planar-8m-diameter-120s-follow-up.md),
> and the latest recognition boundary is the
> [within-file stationary-caller report](2026-09-01-within-file-stationary-caller-scope.md).

> **Current-selection note:** ADRs 0006, 0007 and 0010 select an eight-channel
> planar 7+1 target, within-file stationary anonymous identity and one
> CS5308P. The 8/12/16 and multiple-ADC comparisons below are study history,
> not current v1 authority.

## Executive conclusion

**PROPOSED** — The appliance can be externally PoE/Ethernet-only. Use one
standards-compliant Cat6 PoE+ uplink to a sealed Linux roof appliance, then a
short internal USB link from the unchanged multichannel audio module to the
SBC. All microphone ADCs share one local sample clock before Ethernet
packetization, so network jitter does not corrupt inter-microphone TDOA.

**PROPOSED** — For 3D evidence, do not build a planar ring or rely on one raised
microphone. Compare three noncoplanar candidates: eight channels as the
minimum-cost experiment (five outer plus three raised), twelve as a balanced
study (eight outer plus four raised/inner), and sixteen as the full two-scale
study. Q1/Q5 must close before recommending one.

**PROPOSED** — Separate the desired identity result from its intermediate.
Persistent recognition of the same biological individual after it moves or
returns is the system goal and needs a host-side learned classifier, labelled
source-isolated held-out field evidence, and an explicit unknown class.
Anonymous spatial tracks are required to isolate and label calls, but do not
satisfy identity. A 3D position signature alone is not a biometric identifier.

**OWED** — Roof dimensions, allowable raised structure, identity meaning,
overlap requirement, PoE class/run/environment, exact hardware, weather and
building-entry safety remain open. No PCB or roof coordinate is locked.

## Question and scope

The user's follow-up asks how physical dimensions change array behavior,
whether a 3D or multi-position signature can identify the caller, and whether
one PoE/Ethernet cable can replace an external USB connection. This addendum
answers those architecture questions and updates the commission boundary.

**OWED** — It does not design an identity model, roof mount, lightning system,
schematic, PCB layout, enclosure or purchase list. It does not promise a
localization error from aperture arithmetic.

## Evidence boundary

**CITED** — The original
[architecture study](2026-09-01-star-array-architecture-study.md) established a
balanced analog star, central shared-clock conversion, the archived RJ45
pin-map hazard and absence of the archived XU316 application firmware.

**CITED** — miniDSP documents MCHStreamer as a UAC2/Linux multichannel audio
interface. Its manual specifies two TDM input data lines for the 16-channel
mode, eight 32-bit slots per line, clocks driven by the module, and 256-Fs BCLK.
TI documents TAA5242 as a hardware-controlled stereo ADC with TDM daisy-chain
support and a -40 to 125 °C operating range. These are candidate interface
facts, not an interoperability proof.

**CITED** — IEEE PoE ecosystem guidance identifies 25.5 W available at the PD
for Type 2 and up to 51 W for Type 3. The official Raspberry Pi PoE+ HAT is
rated only 0 to 50 °C; it is a bench/under-eave reference, not an exposed-roof
production choice.

**OWED** — Nothing here has been acoustically simulated against the actual
roof, bench-connected, power-measured, thermally tested, weather tested, or
evaluated on labelled crow calls.

## Findings

### 1. Outer aperture changes low-frequency leverage and field burden

**INFERRED** — The table assumes 344 m/s, 48 ksample/s and a representative
1.5 kHz wavelength. Maximum TDOA is diameter divided by sound speed. The
`lambda/D` angle is only an optimistic physical scale; reflections, source
range, SNR, geometry, wind and estimator bias can dominate actual error.

| Outer radius (m) | Diameter (m) | Max end-to-end TDOA (ms) | Samples at 48 kHz | `lambda/D` scale at 1.5 kHz | Easier | Harder |
|---:|---:|---:|---:|---:|---|---|
| 0.5 | 1 | 2.91 | 140 | 13.1° | Compact mount, short cables, easy survey and calibration | Weak low-frequency bearing/range signature; closely spaced sources look similar |
| 1 | 2 | 5.81 | 279 | 6.6° | Practical small-roof prototype; manageable weather structure | Still limited near-field range leverage; roof reflections remain coherent |
| 2 | 4 | 11.63 | 558 | 3.3° | Strong compromise for bearing, source-track separation and three-zone fingerprints | More cable, survey, wind, temperature and obstruction error |
| 4 | 8 | 23.26 | 1,116 | 1.6° | Best low-frequency leverage and separation of nearby tracks | Long exposed spokes, wider acoustic delay search, harder survey/environmental calibration, weather/surge/roof work and worse off-array conditioning |

**INFERRED** — Bigger is not uniformly better. A roof-scale sparse array has
many high-frequency ambiguous peaks; a compact inner group helps disambiguate
them. Broadband near-field SRP/GCC methods and measured calibration remain
mandatory.

### 2. Vertical baseline changes 3D observability

| Height separation (m) | Max vertical delay (ms) | Samples at 48 kHz | What improves | What gets harder |
|---:|---:|---:|---|---|
| 0 | 0 | 0 | Simplest planar installation | Elevation and mirror solutions remain poorly conditioned |
| 0.25 | 0.73 | 35 | Breaks exact coplanarity | Small relative to roof/reflection error; easy to overclaim 3D |
| 0.5 | 1.45 | 70 | Useful elevation/source-range signature | Raised wind load, structure-borne noise and survey burden |
| 1.0 | 2.91 | 140 | Stronger noncoplanar leverage | Highest visual, mechanical, lightning and wind exposure |

**PROPOSED** — Study at least three non-collinear raised microphones if the
first article has only eight channels. One raised reference creates a fragile
geometry. The 0.5 to 1 m rows are illustrative study points, not targets; Q1
and structural/safety analysis must derive the actual admitted height.

### 3. Other dimensional knobs

| Dimension or count | Increasing it helps | Increasing it hurts | Proposed treatment |
|---|---|---|---|
| Channel count | Pair redundancy grows as `N(N-1)/2`: 8/12/16 channels provide 28/66/120 pairs; improves outlier rejection and multi-source tracking | More ADCs, pod power, cable entries, calibration, storage and compute | Neutral candidates: 8 minimum-cost experiment; 12 balanced study; 16 full multiscale study |
| Compact inner spacing | Preserves useful high-frequency phase differences and cleaner audio/reference channels | Too compact adds little low-frequency direction leverage and increases acoustic shadowing | Combine it with a roof-scale outer aperture rather than using it alone |
| Mild radius/angle irregularity | Breaks repeated sidelobe symmetries | Harder fabrication, survey and model bookkeeping | Illustrative 5–15% perturbation only; derive it from simulation after Q1/Q5 |
| Coordinate accuracy | Better TDOA model and repeatability | More surveying cost | Illustrative 5 mm audit point equals about 14.5 microseconds or 0.7 sample; derive the real limit from the error budget |
| Stand-off above roof | Can reduce a planar mirror and supply 3D baseline | Adds wind load, reflections from the support, lightning exposure and vibration | Compare nearly flush with illustrative 0.5–1 m tiers; lock neither before Q1 and structural analysis |

### 4. “Which crow” has two different acceptance boundaries

| Output | What the array can use | Meaning | Evidence needed |
|---|---|---|---|
| Three calibrated position zones | A 28-pair TDOA fingerprint from eight channels | “The caller was at zone A/B/C,” not individual identity | Surveyed speaker/crow-labelled zone calibration plus held-out locations |
| Session-local spatial track | 3D TDOA vector, continuity and source-separated audio | “Track crow-A is calling now” while sources remain separable | Camera-labelled, time-synchronized encounters with unresolved/overlap reporting |
| Persistent individual identity | Isolated vocal features across call types, days, ranges and contexts | “This is the same biological crow as before” | Enrolment labels; day/context-held-out test; false-match, false-reject and unknown-individual metrics |

**CITED** — Published crow-call work supports the existence of individual
acoustic cues, but reported performance depends on call/context and does not
constitute a field-ready identity system for this roof. Therefore biological
identity stays the desired system output but is not a PCB acceptance claim.

**PROPOSED** — Preserve all raw synchronized channels. Localize and separate
first, then run the identity model on the focused source track. Keep the source
track confidence and identity confidence separate; never force a known name
when the evidence supports `unknown`.

### 5. One PoE/Ethernet cable is sufficient at the building boundary

```text
indoor PoE+ switch
  -> one outdoor Cat6 uplink
  -> sealed roof appliance
       -> PoE PD and filtered rails
       -> shared-clock ADC carrier
       -> MCHStreamer
       -> short internal USB
       -> Linux SBC
       -> multichannel PCM over Ethernet
  -> keyed non-Ethernet analog spokes to the microphone pods
```

**INFERRED** — Eight channels at 24 bit/48 ksample/s contain 9.216 Mbit/s of
raw sample payload; sixteen contain 18.432 Mbit/s. Stored in 32-bit containers
they are 12.288 and 24.576 Mbit/s. Even with ordinary packet overhead this is
comfortable on 100BASE-T; Gigabit Ethernet is preferred for operational
headroom, other services and easier SBC sourcing.

**PROPOSED** — Use Type 2 PoE+ as the minimum study point. It is likely enough
for an SBC, MCHStreamer, ADCs and modest analog pods, but “likely” is not a
power budget. Measure startup/peak/continuous draw and worst-case enclosure
temperature. Move to Type 3 if a camera, heater or other significant auxiliary
load is added.

**CITED** — MCHStreamer itself is USB, so Ethernet-only externally requires
the local Linux bridge. Removing all USB is technically possible with a direct
TDM/I2S Linux SoM, but it exchanges a proven UAC2 boundary for a custom carrier,
ALSA/device-tree/clock bring-up and wider software validation. Dante/AES67 is a
capable OEM alternative but brings licensing, module and procurement overhead.

**PROPOSED** — For eight channels, place four stereo TAA5242 candidates on one
8-channel TDM input lane. Twelve would use the module's 16-channel mode with one
full lane and one lane carrying four used plus four unused slots; that partial
lane is unproved. Sixteen uses two full parallel lanes of four stereo ADCs
each. Do not assume one undocumented 16-slot serial chain. Exact module image,
register straps, word/slot alignment, clock authority, channel order and
24-hour continuity still require a retained bench proof.

**OWED** — Use outdoor-rated shielded Cat6, a weather-rated Ethernet mate,
PoE-compatible surge protection at the appliance and building entry, and a
qualified bond/ground plan. PoE magnetics are not lightning protection.

## Recommendations

1. **PROPOSED — adopt the externally PoE/Ethernet-only boundary.** Permit the
   short internal USB link for v1 unless Q6 explicitly forbids it.
2. **PROPOSED — keep 8/12/16 neutral until Q1/Q5.** Compare five-outer/three-
   raised, eight-outer/four-raised, and eight-outer/eight-inner candidates in
   the actual roof model before selecting a channel count.
3. **PROPOSED — treat position and identity as a cascade.** First produce a
   camera-checked source track and focused audio; then evaluate persistent
   identity with held-out labels and `unknown`.
4. **PROPOSED — build an indoor/under-eave electronics bench first.** Prove the
   PoE power budget, exact 8/12/16-channel clock/data mode, Linux channel order,
   uninterrupted network recording and thermal margin before roof CAD.
5. **OWED — answer BRIEF Q1 and Q4-Q6.** Roof envelope, identity meaning,
   multi-source requirement and PoE/environmental boundary decide whether the
   physical array is 8, 12 or 16 channels.

## Validation plan

| Test | Required evidence | Pass boundary before architecture acceptance | Failure implication |
|---|---|---|---|
| PoE power/thermal | Exact PSE/PD/cable, startup and continuous current, all-channel capture, enclosure temperatures | No brownout, throttling or audio discontinuity at worst admitted cable/temperature/load; numeric margins are OWED by Q6 | Raise PoE class, reduce load or relocate compute |
| Shared-clock capture | Selected 8/12/16-channel impulse injection, reconnects, 24 h run and temperature sweep | Fixed order; zero lost/duplicated frames in retained run; skew/drift ceiling OWED by Q2/Q5 | Reject module/ADC mode or clock topology |
| Geometry survey | Membrane coordinates and chirps from surveyed 3D positions | Coordinate residual and localization error ceilings OWED by Q1/Q2 | Change geometry, survey or reflection model |
| Three-zone signature | Held-out speaker/crow calls from each target zone plus off-zone cases | Confusion and unknown-zone limits OWED by Q5 | Signature identifies neither zone nor bird reliably |
| Session tracking | Synchronized camera plus one- and two-source crow-like events | Track switches, unresolved rate and overlap separation limits OWED by Q4/Q5 | Limit claim to one source or increase geometry/channels |
| Persistent identity | Labelled isolated calls held out by bird, day, call type and location as appropriate | False-match, false-reject and unknown-individual limits OWED by Q4 | Retain anonymous tracks only; no biological-ID claim |
| Entry/weather safety | Cable/connector/surge/bonding review plus retained rain/wind/thermal/condensation tests | Qualified written disposition and no unsafe degradation | No unattended roof deployment |

## Source register

### Repository evidence

- [Original architecture study](2026-09-01-star-array-architecture-study.md) — **CITED**, prior system comparison and archived-system hazards.
- [Project BRIEF](../BRIEF.md) — **CITED**, verbatim directive, assumptions and open commission facts.
- [ADR 0004](../decisions/0004-individual-identity-evidence-boundary.md) — **PROPOSED**, identity claim boundary.
- [ADR 0005](../decisions/0005-poe-ethernet-roof-appliance.md) — **PROPOSED**, external network/power boundary.

### External primary sources

- [miniDSP MCHStreamer product page](https://www.minidsp.com/products/usb-audio-interface/mchstreamer) and [user manual](https://www.minidsp.com/images/documents/MCHStreamer%20User%20Manual.pdf) — **CITED**, UAC2/Linux and TDM interface behavior; accessed 2026-09-01.
- [TI TAA5242 product page](https://www.ti.com/product/TAA5242) — **CITED**, hardware control, TDM daisy-chain and temperature range; accessed 2026-09-01.
- [Ethernet Alliance PoE technical brief](https://ethernetalliance.org/wp-content/uploads/2020/02/EthernetAlliance_Gen2PoECertProgram_techbrief-FINAL-19DEC19.pdf) — **CITED**, PD power levels by IEEE PoE type.
- [Raspberry Pi PoE+ HAT](https://www.raspberrypi.com/products//poe-plus-hat/) — **CITED**, official interface and operating-temperature boundary.
- [Silver Telecom Ag5300 datasheet](https://www.silvertel.com/images/datasheets/Ag5300-datasheet-smallest-30W-Power-Over-Ethernet-Plus-Module-PoEplusPD.pdf) — **CITED**, an industrial-temperature 12 V/24 W-class candidate only; accessed 2026-09-01.
- [NXP i.MX 8M Mini](https://www.nxp.com/products/i.MX8MMINI) — **CITED**, direct Linux multichannel-audio SoM alternative; accessed 2026-09-01.
- [Audinate Brooklyn 3 datasheet](https://www.getdante.com/docs/dante-brooklyn-datasheet/) and [Dante clock synchronization](https://dev.audinate.com/GA/dante-controller/userguide/webhelp/content/clock_synchronization.htm) — **CITED**, OEM network-audio/PTP alternative and synchronization boundary.
- [Yorzinski et al., individual discrimination in American crow calls](https://doi.org/10.1093/condor/108.3.518) — **CITED**, individual acoustic-cue precedent, not a field-ready classifier.
- [Three-dimensional localization of flying songbirds with a microphone array](https://www.bioacoustics.info/article/pinpointing-position-flying-songbirds-wireless-microphone-array-three-dimensional) — **CITED**, noncoplanar outdoor localization precedent.
- [Dmochowski, Benesty and Affès, spatial aliasing in microphone arrays](https://doi.org/10.1109/TSP.2008.2010596) — **CITED**, array-spacing ambiguity context.
