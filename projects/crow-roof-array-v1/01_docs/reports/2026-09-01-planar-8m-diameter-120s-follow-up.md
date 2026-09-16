---
schema: 1
kind: pcb-human-report
report_id: 2026-09-01-planar-8m-diameter-120s-follow-up
title: Crow roof array — planar 8 m-diameter and 120-second identity follow-up
subtitle: Single-active-caller geometry, recording-held-out identity, and the user-permitted internal USB boundary
project: crow-roof-array-v1
date: 2026-09-01
status: SUPERSEDED
evidence_status: INCOMPLETE
---

> **Superseded, 2026-09-01:** The user subsequently clarified that recognition
> must persist only within one 120-second file while the crow does not move
> much. The current scope is the
> [within-file stationary-caller report](2026-09-01-within-file-stationary-caller-scope.md).
> This report remains the historical record of the broader cross-file
> interpretation and the still-current 8 m-diameter geometry arithmetic.

## Executive conclusion

**PROPOSED** — Yes, the array may be planar under the revised goal. Planarity
is compatible with a calibrated planar TDOA signature, 2D/source grouping and
single-active-caller spatial filtering. It cannot support a robust elevation or
3D claim. The user-facing output remains biological identity, not coordinates.

**PROPOSED** — Study eight synchronized channels as seven surveyed outer
microphones around a nominal 4 m radius plus one center reference. Avoid a
perfect regular heptagon; measure the actual membrane coordinates and use those
coordinates in DSP. This is the leading study, not a locked floorplan.

**CITED** — The user corrected the tentative size to 8 m diameter, requires
identity across separate 120-second recordings, does not require simultaneous
crow separation, and permits a short internal USB link.

**OWED** — The usable roof polygon, keep-outs, entry route, exact coordinates,
identity gap between recordings, label source, accepted errors, external PoE
architecture, power and outdoor safety remain open. The project stays
`PCB-COMMISSION INCOMPLETE`.

## Question and scope

This report answers whether the array can be planar after the user's aperture,
recording-duration, overlap and internal-USB clarifications. It compares planar
eight-channel layouts and defines what position and identity claims survive.

**OWED** — It does not select a microphone, ADC, connector, PoE PD, Linux SBC,
mounting coordinate, enclosure or identity model. It does not treat an 8 m
diameter as surveyed roof authority.

## Evidence boundary

**CITED** — The earlier
[dimensionality/identity/PoE addendum](2026-09-01-dimensionality-identity-and-poe-addendum.md)
compared 0.5–4 m radii, noncoplanar geometry, identity boundaries and PoE
options. The user now selects neither 3D nor a raised tier; instead, they ask
whether a planar signature is sufficient under a one-active-crow requirement.

**INFERRED** — Numeric delay and storage values below use 344 m/s, 48
ksample/s and eight channels. They are deterministic study arithmetic, not
measured roof performance.

**OWED** — No actual roof impulse response, wind field, coordinate survey,
120-second recording, crow label, identity holdout or power/thermal test exists.

## Findings

### 1. Planarity is acceptable only for the signature branch

| Property | Planar result | Consequence |
|---|---|---|
| Horizontal bearing/source grouping | Observable from broadband pair delays | Suitable for selecting the one active caller and grouping calls |
| Planar position signature | Observable after coordinate/environment calibration | Can be retained as context, but must not become the biological-ID feature |
| Elevation | Poorly conditioned; planar mirror ambiguity remains | No robust 3D/elevation claim |
| Single active crow | Compatible | Focus/choose calls, then aggregate vocal evidence |
| Simultaneous crows | Not required by the user | Mark overlap `unresolved` or exclude it and report the rate |

**INFERRED** — Knowing that birds are normally above the roof removes the
physically irrelevant below-roof half-space from operation, but it does not add
elevation information. Two crows at the same horizontal position and different
heights can still look similar to the planar array.

### 2. Seven outer microphones plus one center is the leading planar study

| Eight-channel layout | Benefit | Cost / weakness | Disposition |
|---|---|---|---|
| Seven outer + center | Best perimeter/reference compromise; center gives a stable reference and local audio channel | No true compact high-frequency subarray | **PROPOSED** leading study |
| Six outer + two inner | One inner pair | A pair is insufficient for useful 2D compact beamforming and costs one outer direction | Reject as baseline |
| Four outer + four compact inner | True multiscale planar array | Much weaker 8 m-scale perimeter redundancy | Retain only if later filtering tests demand it |
| Eight outer | Maximum perimeter count | No center reference and more repeated long-baseline behavior | Inferior to seven + center for this use case |

**PROPOSED** — The seven outer microphones should be mildly irregular in angle
and, where the roof permits, radius. The 4 m value is a nominal maximum radius,
not permission to fabricate nominal coordinates. Survey the microphone
membranes after installation.

### 3. Corrected 8 m-diameter arithmetic

| Quantity | Study value |
|---|---:|
| Outer radius / diameter | 4 m / 8 m |
| Center-to-outer maximum delay | 11.63 ms / 558 samples |
| Absolute diameter-bound delay | 23.26 ms / 1,116 samples |
| Regular-heptagon adjacent chord | 3.47 m |
| Regular-heptagon longest chord | 7.80 m |
| Samples per channel in 120 s | 5,760,000 |
| Eight-channel packed 24-bit file payload | 138.24 MB |
| Eight-channel 24-in-32 file payload | 184.32 MB |
| Eight-channel 24-in-32 network payload | 12.288 Mbit/s |

**PROPOSED** — Use pair-specific correlation windows derived from surveyed
separation. As an initial software test point, center-to-outer pairs need about
plus/minus 650 samples and outer-to-outer pairs about plus/minus 1,300 samples,
including modest environmental/search margin. Recompute these windows from the
admitted sound-speed and wind model; do not publish them as fixed hardware
limits.

**INFERRED** — At 1.5 kHz, `lambda/D` for an 8 m diameter is about 1.64°.
This is an optimistic physical scale, not expected accuracy. Multi-metre outer
spacing is heavily ambiguous at crow-call frequencies; mildly irregular
geometry and broadband GCC/SRP-style delay evidence are required. Process
individual detected calls rather than correlating an entire 120-second file.

**INFERRED** — Across the full 8 m baseline, an illustrative 1 °C sound-speed
error shifts delay by roughly two samples, while a 5 m/s along-baseline wind can
bias it by roughly sixteen samples. Temperature, wind, strong-rain exclusion
and fractional-sample fitting therefore remain part of the signature contract.

**INFERRED** — Seven nominal 4 m spokes require at least 28 m of pod cable;
routing and service loops increase that. Cable electrical delay is not the
acoustic limitation under central shared-clock conversion, but exposed copper,
gain/phase match, voltage drop, surge, water ingress and service access scale
with total length.

### 4. Identity is evaluated across whole 120-second recordings

**CITED** — The user requires identity to persist across recordings that are
each 120 seconds long. The maximum time gap between files remains unknown.

**CITED** — A mixed-context American-crow study reported about 24% cross-
validated individual classification versus about 6% chance across caw types.
That is evidence that vocal identity exists, but also a warning that context
and call type materially limit a field classifier.

**PROPOSED** — Treat an entire 120-second recording as the minimum indivisible
identity unit. Calls extracted from one file may be aggregated to improve the
file-level identity probability, but may not be divided between training and
test. Consecutive files from one encounter or visit must also remain in the
same split; Q7 defines how far that grouping must extend.

**PROPOSED** — The processing chain is:

1. retain all eight synchronous raw channels;
2. detect call segments and estimate a planar source signature;
3. reject or label overlapping-call segments unresolved;
4. align/focus or select the cleanest channel for the one active source;
5. aggregate vocal embeddings across the 120-second file;
6. compare identity across held-out recording files and return `unknown` when
   evidence is insufficient.

**PROPOSED** — Do not train persistent identity directly on TDOA or position.
That teaches the model the crow's perch. Hold out complete files and, once Q7
defines the horizon, hold out visits, positions and weather contexts needed to
prove the claimed persistence.

### 5. Internal USB is now permitted; external PoE remains proposed

**CITED** — The user explicitly permits a short internal USB link. This removes
the main need for a custom direct-TDM Linux carrier.

**PROPOSED** — Continue studying one genuine PoE/Ethernet uplink to a local
Linux roof appliance, with all eight channels sampled on one shared clock,
MCHStreamer connected by a short retained USB cable, and Ethernet carrying
recordings/control back indoors. Packet timing is never the TDOA clock.

**INFERRED** — One 120-second 24-in-32 recording is about 184 MB. Continuous
capture would be about 5.53 GB/hour or 133 GB/day before filesystem/container
overhead, so event clips or a bounded local ring buffer are likely preferable.
Network bandwidth is easy; storage policy and outage behavior are the larger
open questions.

**OWED** — PSE/PD class, total Cat6 run, roof temperature/exposure, SBC load,
pod current, storage retention, UPS behavior and surge/bonding still block the
external architecture from acceptance.

## Recommendations

1. **PROPOSED — use planar as the active study branch.** Remove elevation and
   robust 3D from its claim; retain planar spatial signature and source grouping.
2. **PROPOSED — simulate seven outer plus center first.** Compare it against
   four-outer/four-inner using the surveyed roof polygon and measured/synthetic
   reflections before locking coordinates.
3. **PROPOSED — keep eight synchronized channels.** No overlap separation is
   required, but channel diversity supports robust call selection and identity
   evidence.
4. **PROPOSED — validate identity by grouped whole recordings.** The same bird
   label must survive held-out 120-second files, with every encounter/visit kept
   within one split, overlaps unresolved and `unknown` available.
5. **OWED — answer Q7 and survey the roof.** The gap between recordings and the
   actual mounting polygon are now the two highest-value clarifications.

## Validation plan

| Test | Required evidence | Acceptance boundary before architecture lock | Failure implication |
|---|---|---|---|
| Roof survey | Coordinate polygon, keep-outs, entry route, service loops and membrane coordinates | Every proposed point and cable route fits with stated tolerance | Reduce aperture or change layout |
| Planar simulation | Broadband direct-plus-reflection corpus over admitted source region and weather cases | Pair-delay association and unresolved limits OWED by Q2/Q5 | Change irregularity, multiscale allocation or restore height |
| 120-second capture | Eight synchronized channels, file identity, no frame loss and fixed order | Zero lost/duplicated frames in retained test; skew/drift ceiling OWED | Reject clock/module mode |
| Single-source grouping | Surveyed speaker/camera-labelled calls with overlap cases tagged | Required association and unresolved-rate limits OWED | Spatial signature cannot support isolation/labels |
| Persistent identity | Whole recording files held out at the Q7 time/position horizon | False-match, false-reject and unknown limits OWED by Q4/Q7 | No persistent biological-ID claim |
| PoE/thermal/storage | Exact PSE/PD/cable/load plus 120-second files and outage/ring-buffer test | No brownout, throttling, dropped audio or unsafe temperature at admitted corner | Change power class, compute placement or storage policy |
| Outdoor boundary | Wind/rain/temperature, ingress, cable protection and qualified bonding/surge review | Written disposition and no unsafe degradation | No unattended roof use |

## Source register

### Repository evidence

- [Project BRIEF](../BRIEF.md) — **CITED**, exact user corrections and open questions.
- [Dimensionality/identity/PoE addendum](2026-09-01-dimensionality-identity-and-poe-addendum.md) — **CITED**, prior comparison table and evidence boundary.
- [ADR 0004](../decisions/0004-individual-identity-evidence-boundary.md) — **PROPOSED**, persistent-identity evidence boundary.
- [ADR 0005](../decisions/0005-poe-ethernet-roof-appliance.md) — **PROPOSED**, external PoE/internal USB topology.
- [ADR 0006](../decisions/0006-planar-signature-versus-3d.md) — **PROPOSED**, planar branch and claim limit.

### External primary sources

- [miniDSP MCHStreamer product page](https://www.minidsp.com/products/usb-audio-interface/mchstreamer) and [user manual](https://www.minidsp.com/images/documents/MCHStreamer%20User%20Manual.pdf) — **CITED**, UAC2/Linux and TDM interface behavior.
- [TI TAA5242 product page](https://www.ti.com/product/TAA5242) — **CITED**, hardware-controlled stereo ADC/TDM candidate.
- [Yorzinski et al., individual discrimination in American crow calls](https://doi.org/10.1093/condor/108.3.518) — **CITED**, acoustic-individuality precedent, not a field-ready classifier.
- [Mates et al., acoustic profiling in the American crow](https://pmc.ncbi.nlm.nih.gov/articles/PMC4237024/) — **CITED**, mixed-context caller-identity performance and context dependence.
- [Dmochowski, Benesty and Affès, spatial aliasing in microphone arrays](https://doi.org/10.1109/TSP.2008.2010596) — **CITED**, sparse-array ambiguity context.
