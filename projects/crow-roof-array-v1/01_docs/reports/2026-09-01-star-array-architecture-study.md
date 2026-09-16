---
schema: 1
kind: pcb-human-report
report_id: 2026-09-01-star-array-architecture-study
title: Roof crow microphone star — architecture study
subtitle: Eight-channel practical baseline, sixteen-channel upgrade, and archived-system hazards
project: crow-roof-array-v1
date: 2026-09-01
status: DRAFT
evidence_status: INCOMPLETE
---

> **Updated scope:** The user's later 3D/identity/PoE directive is analyzed in
> the [dimensionality, identity and PoE addendum](2026-09-01-dimensionality-identity-and-poe-addendum.md).
> This report remains the original architecture checkpoint and is not silently
> rewritten as though those requirements were known at the time.

> **Current-selection note:** ADRs 0006, 0007, 0010 and 0011 now select eight
> planar channels on one CS5308P, anonymous identity only within one 120-second
> file, and internal Micro-Fit terminations behind sealed cable glands. Older
> multi-ADC, 12/16-channel and circular-connector rows below are retained as
> study history, not current implementation authority.

## Executive conclusion

**PROPOSED** — Build the first article as an eight-channel physical star of
balanced analog microphone home runs feeding simultaneous central ADCs on one
shared clock, then a hash-bound, unchanged multichannel USB-audio module image.
This is the lowest-risk candidate for localization-grade channel timing without
writing project firmware. Start with eight channels; treat sixteen channels as
an option that still needs a complete interface-control and bench proof.

**CITED** — Do not reuse the latest archived pod and central boards as a
straight-through system. The pod assigns RJ45 contacts 4/5 to `+5V_AUDIO` and
7/8 to ground, while the central source assigns 4/7 to protected +5 V and 5/8
to ground. The two local contracts are individually self-consistent but cross
connected they short each central port through its protection. The archived
central project's XU316 UAC2/TDM application is also explicitly not written.

**OWED** — No PCB, connector, roof coordinate set, power envelope, microphone,
ADC, enclosure, sourcing class, localization accuracy, or outdoor-safety claim
is locked. The project remains `PCB-COMMISSION INCOMPLETE`.

## Question and scope

The question is how to turn a star-shaped roof installation into synchronized
audio suitable for locating a calling crow and spatially focusing its audio.
This report compares geometry and electronics architecture only.

**PROPOSED** — “Which crow” is interpreted as the crow at a particular source
track or camera location. Biometric identification from voice is outside the
PCB claim. Published work demonstrates individual acoustic differences in
American crows, but that does not establish a dependable field identity
classifier for this system.

Excluded from this study are finished host DSP, animal-identification models,
custom embedded firmware, building lightning design, final enclosure CAD,
fabrication files, and a purchase decision.

## Evidence boundary

**CITED** — The repository contains two relevant archived design histories:

- [crow-mic-pod-v2 architecture](../../../../archived_projects/crow-mic-pod-v2/01_docs/ARCHITECTURE.md)
  and its frozen [v1.3 source](../../../../archived_projects/crow-mic-pod-v2/07_releases/crow-mic-pod-v2-v1.3-2026-07-27/source/crow_mic_pod_v2.tsx);
- [crow-recorder-central-v2 architecture](../../../../archived_projects/crow-recorder-central-v2/01_docs/ARCHITECTURE.md),
  [port-map checker](../../../../archived_projects/crow-recorder-central-v2/03_src/check_port_nets.py),
  and [firmware boundary](../../../../archived_projects/crow-recorder-central-v2/05_firmware/README.md).

**CITED** — Those projects document an analog balanced pod, centralized
shared-clock ADC concept, eight home-run ports, and a calibration transducer.
They do not contain an accepted full-system cross-board cable proof, completed
USB-audio firmware, or roof first-article measurements.

**OWED** — The proposed architecture has not been simulated, laid out,
fabricated, synchronized, acoustically calibrated, weather tested, or compared
against a camera-labelled crow corpus.

## Findings

### 1. The archived system is useful evidence, not reusable hardware

| Finding | Evidence grade | Consequence |
|---|---|---|
| Pod contacts 4/5 are +5 V and 7/8 are ground; central contacts 4/7 are +5 V and 5/8 are ground. | **CITED** — frozen pod source and central `check_port_nets.py` | A normal straight-through cable creates two supply-to-ground crossings. Do not plug the archived pair together. |
| Custom powered RJ45 is visually compatible with Ethernet/PoE. | **CITED** — archived pod reviews and architecture | The successor should not repeat that semantic hazard. |
| Central conversion was intended to share MCLK/BCLK/LRCLK across two ADCs. | **CITED** — archived central architecture | **INFERRED** — shared conversion timing is a promising TDOA concept, with adequacy owed by measurement. |
| XU316 UAC2/TDM application is not written. | **CITED** — archived firmware README | Reuse would silently create a major firmware project contrary to this commission. |
| One shared calibration switch drives every pod together. | **CITED** — archived firmware README | It cannot independently identify a swapped channel or calibrate one acoustic path at a time. |

### 2. Electronics options

| Option | Benefits | Costs / failure modes | Disposition |
|---|---|---|---|
| Four hardware-controlled stereo ADCs feeding an 8-channel USB-audio module | One central sample clock; no project firmware; each pod stays analog and simple. | Indoor carrier must distribute clocks cleanly; four stereo data lines; module integration and exact ADC mode need proof. | **PROPOSED** practical v1. TI PCM1861 and miniDSP MCHStreamer are candidates, not selected parts. |
| Eight hardware-controlled stereo ADCs on a TDM chain for 16 channels | Multiscale array and future elevation/reference channels without pod firmware. | Higher clock/slot/configuration risk, more power and analog channels; exact clock authority, frame/slot/word format, vendor image and module interop remain unproved. | **PROPOSED** research option. TI TAA5242 is a coupon candidate, not a locked upgrade path. |
| ADC/MCU at each roof pod | Digitizes near the microphone; potentially long digital links. | Distributed-clock alignment, firmware, surge/isolation and outdoor power complexity. | **INFERRED** wrong first step under `firmware: forbidden`. |
| Restore the archived XU316 central board | Much prior PCB work exists. | Missing application firmware plus destructive cable-map mismatch and open first-article issues. | **CITED** reject as a system baseline. |

**CITED** — The MCHStreamer vendor describes UAC2 operation, Linux support,
eight-channel I2S input and higher-channel TDM modes. TI describes PCM1861 as a
two-channel hardware-controlled audio ADC and TAA5242 as a hardware-controlled
stereo ADC with I2S/TDM support. These are interface-level reasons to study the
parts; they are not compatibility or sourcing evidence.

**PROPOSED** — The initial signal chain is:

```text
microphone capsule
  -> low-noise bias/preamp
  -> balanced line driver
  -> keyed shielded home-run carrying audio + protected DC
  -> input ESD/common-mode/filter network
  -> simultaneous central ADC
  -> shared MCLK/BCLK/LRCLK
  -> vendor multichannel UAC2 module
  -> Linux PCM capture
```

The old electret/OPA1678 pod may inform a new front end, but its PCB, RJ45 map,
calibrator rail and rejection assumptions are not adopted.

### 3. Geometry options

| Geometry | What it answers best | Tradeoff | Status |
|---|---|---|---|
| Eight surveyed perimeter positions at mildly varied radii | Two-dimensional bearing/roof-surface tracking with angular redundancy. | Planar above/below ambiguity; no center reference. | **PROPOSED** if Q2 chooses 2D. |
| Six perimeter + center + genuinely raised reference | Adds center reference and weak elevation sensitivity with eight channels. | Fewer perimeter directions; one raised channel is not robust 3D geometry. | **PROPOSED** if Q2 requires mixed elevations on the first article. |
| Eight compact inner + eight roof-scale outer positions | Multiple spatial scales help broadband ambiguity and source separation. | Sixteen pods/channels and much more calibration, protection and cabling. | **PROPOSED** v2 research path. |

**INFERRED** — The electrical topology can be a perfect star while microphone
locations are deliberately nonperiodic. Exact positions should follow roof
constraints, not a cosmetic regular polygon.

**INFERRED** — At 48 ksample/s one sample is 20.83 microseconds, about 7.2 mm
of sound path at 344 m/s. A 4 m aperture can produce roughly 11.6 ms (about 558
samples) of end-to-end TDOA. Fractional-delay estimation is still required;
sample period is not the final location resolution.

**INFERRED** — Using 344 m/s as the study sound speed, the simple
half-wavelength spacings are about 86 mm at 2 kHz, 43 mm at 4 kHz and 29 mm at
6 kHz. These figures illustrate why a roof-scale sparse array cannot be treated
as uniformly alias-free through the full band; they are not a decisive spatial
Nyquist rule for this finite, broadband, near-field array. The proposed
response is broadband localization, sidelobe handling and measured calibration,
not a promised unique single-frequency beam.

**CITED** — A published four-microphone field system is useful precedent that
outdoor passive acoustic localization can achieve metre-scale results in a
bounded test geometry; it is not an accuracy prediction for this roof.

### 4. Recording, localization and “isolation”

**PROPOSED** — Host processing should retain raw synchronized channels and use
this evidence ladder:

1. band-limit/detect crow-like events without discarding raw audio;
2. estimate multi-peak GCC-PHAT delays;
3. search a surveyed near-field SRP-PHAT grid using temperature-adjusted sound
   speed;
4. reject inconsistent channel pairs, cluster peaks and track sources;
5. spatially focus with delay-and-sum first;
6. try MVDR/LCMV or source separation only after measured calibration and use
   an explicit unresolved-overlap result when two crows cannot be separated.

**INFERRED** — A synchronized camera is the practical way to map a source track
to a physical crow. Audio alone may say “the source at the north chimney spoke”
without proving that bird's individual identity.

### 5. Outdoor and calibration boundary

**PROPOSED** — Use a keyed weather-resistant circular connector assembly, with
M12 only a candidate. The selected connector, backshell, cable, pair assignment,
shield termination, grip, bend and enclosure must be one qualified assembly.

**PROPOSED** — Distribute a higher SELV voltage from the indoor hub and regulate
quietly at each pod rather than repeat the old long 5 V rail. Exact voltage,
current, drop, heat and noise corners are OWED.

**OWED** — A qualified building-entry and surge/bonding review is mandatory for
unattended roof copper. Per-port PCB ESD/TVS/fusing is not lightning approval.

**PROPOSED** — Omit the electrically driven pod beeper from the first PCB or
make each pod independently addressable. Use a surveyed portable speaker/chirp
at several positions for the first calibration so electrical feedthrough cannot
masquerade as acoustic timing.

## Recommendations

1. **PROPOSED — answer BRIEF Q1-Q3 first.** Roof dimensions, required output,
   cable lengths and budget decide the geometry and power/protection envelope.
2. **PROPOSED — commission two new board roles, not a legacy respin.** One
   outdoor analog pod and one indoor eight-channel carrier, with one shared
   connector contract compiled against both ends.
3. **PROPOSED — breadboard the clock/data architecture before PCB layout.** Use
   the exact USB module plus four ADC evaluation channels, capture all eight
   channels, inject one signal into every input, and measure inter-channel
   delay/skew over reconnect and temperature.
4. **PROPOSED — build one cable/pod coupon.** Measure noise, CMRR, frequency and
   phase match, 50/60 Hz rejection, cable drop, surge response, wind noise and
   water management at the longest home-run.
5. **PROPOSED — use eight perimeter mics for a 2D first article; otherwise do
   not pretend one raised mic closes 3D.** If robust elevation or overlapping
   sources are required, move directly to a surveyed sixteen-channel multiscale
   experiment.

## Validation plan

The following tests can falsify this proposal. **OWED** — Q2 must supply the
numerical localization error and overlap requirements before any row can close
G1/G2. Until then this is a protocol skeleton, not an acceptance specification.

| Test | Required evidence | Acceptance boundary at commission | Failure implication |
|---|---|---|---|
| Cross-board cable contract | Machine census of every conductor at both PCB connectors plus a physical continuity coupon | Exact identity at both ends; zero unintended shorts/opens; deterministic channel labels. | Any mismatch blocks power and mating. |
| Shared-clock capture | Hash-bound vendor module image/configuration; eight-channel loopback; frame continuity, channel order, inter-channel impulse skew and drift over reconnect, temperature and 24 h | All eight channels present in fixed order with zero lost/duplicated frames in the retained run; maximum skew/drift is **OWED by Q2**. | If timing is not stable, the ADC/module architecture is rejected. |
| Analog home-run | Calibrated amplitude/phase/CMRR/noise across the full cable length and environment | Numeric phase/noise/match limits are **OWED by Q2** and the microphone-band lock. | If mismatch cannot be calibrated, move conversion toward the pod. |
| Geometry calibration | Surveyed membrane coordinates plus chirps from at least three surveyed source positions and elevations | Survey tolerance and residual ceiling are **OWED by Q1/Q2**. | Large residuals require geometry, reflection or per-channel model changes. |
| Blind localization | Camera-labelled held-out calls, reporting median/95th/worst error and unresolved rate | Error and unresolved-rate ceilings are **OWED by Q2**; training locations may not be reused as the holdout. | The array cannot claim “which source” without held-out closure. |
| Overlap | Two controlled simultaneous acoustic sources at varied separation | Required source separation, level difference and success rate are **OWED by Q2**. | Failure limits v1 to one active crow and triggers the 16-channel study. |
| Outdoor first article | Retained rain/wind/UV/condensation/drainage/strain-relief protocol plus professional entry-safety review | Duration/severity are **OWED by Q1/Q3**; no unattended use without written disposition. | No unattended roof use. |

## Source register

### Repository evidence

- [Archived pod v1.3 source](../../../../archived_projects/crow-mic-pod-v2/07_releases/crow-mic-pod-v2-v1.3-2026-07-27/source/crow_mic_pod_v2.tsx) — **CITED**, exact pod connector nets.
- [Archived central port checker](../../../../archived_projects/crow-recorder-central-v2/03_src/check_port_nets.py) — **CITED**, exact central connector-net expectation.
- [Archived central firmware README](../../../../archived_projects/crow-recorder-central-v2/05_firmware/README.md) — **CITED**, absent application firmware and shared calibration switch.
- [Project BRIEF](../BRIEF.md) — **CITED**, commission assumptions, questions and acceptance boundary.

### External primary sources

- [miniDSP MCHStreamer product page](https://www.minidsp.com/products/usb-audio-interface/mchstreamer) — **CITED**, vendor USB/I2S/TDM interface capabilities; accessed 2026-09-01.
- [TI PCM1861 product page](https://www.ti.com/product/PCM1861) — **CITED**, hardware-controlled stereo ADC capabilities; accessed 2026-09-01.
- [TI TAA5242 product page](https://www.ti.com/product/TAA5242) and [datasheet](https://www.ti.com/lit/ds/symlink/taa5242.pdf) — **CITED**, hardware-control and TDM candidate capabilities; accessed 2026-09-01.
- [Mates et al., “Acoustic Cues for Individual Discrimination in Calls of the Common American Crow”](https://doi.org/10.1093/condor/108.3.518) — **CITED**, evidence of individual call variation, not a deployed identifier.
- [Mennill et al., field test of a passive acoustic location system](https://www.bioacoustics.info/article/field-test-accuracy-passive-acoustic-location-system) — **CITED**, outdoor localization precedent.
- [Dmochowski, Benesty and Affès, “On Spatial Aliasing in Microphone Arrays”](https://doi.org/10.1109/TSP.2008.2010596) — **CITED**, cautions and analysis around microphone-array spatial aliasing.
