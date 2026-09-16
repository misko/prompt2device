---
schema: 1
kind: pcb-human-report
report_id: 2026-09-01-within-file-stationary-caller-scope
title: Crow roof array — within-file stationary caller scope
subtitle: Anonymous 120-second source continuity without a biological-identity claim
project: crow-roof-array-v1
date: 2026-09-01
status: DRAFT
evidence_status: INCOMPLETE
---

## Executive conclusion

**CITED** — The user requires recognition to persist only within one
120-second recording and only if the crow does not move much. Recognition need
not persist across consecutive files, visits, hours, days or changed perches.

**PROPOSED** — Implement this as an anonymous spatial source track such as
`caller-A`, not as biological crow recognition. Maintain the label while the
calibrated position posterior remains inside an evidence-derived stationarity
gate. Expire it at file end. Material movement, overlap, ambiguity or low
confidence starts a new label or returns `unknown`.

**PROPOSED** — The planar eight-channel seven-outer-plus-center study remains
appropriate. It supplies a rich TDOA signature for stationary source continuity
without pretending to measure elevation or identify a bird after it moves.

**OWED** — The roof survey, position estimator, stationarity/confidence gate,
track-switch ceiling and unresolved-rate ceiling remain unmeasured. The project
stays `PCB-COMMISSION INCOMPLETE`.

## Question and scope

This report applies the user's final time and movement boundary to the array
output. It distinguishes a source-track label from a biological identity and
defines how that label begins, persists and expires.

**OWED** — It does not select a microphone, coordinate, PCB, connector, power
module, DSP algorithm or fixed movement distance. It does not claim that two
different crows occupying the same perch can be distinguished.

## Evidence boundary

**CITED** — The [project BRIEF](../BRIEF.md) retains the exact user statement.
[ADR 0007](../decisions/0007-within-file-stationary-caller-track.md) owns the
proposed label semantics. [ADR 0006](../decisions/0006-planar-signature-versus-3d.md)
continues to own the planar geometry and its no-elevation boundary.

**INFERRED** — A stable planar TDOA signature can associate successive calls
with one approximately stationary acoustic source. That is operational source
continuity, not proof of one biological individual.

**OWED** — No 120-second stationary-source capture, controlled motion trial,
crow-labelled track, overlap trial or roof impulse-response measurement exists.

## Findings

### 1. The required output is now a track, not a biometric

| Property | Required behavior | Explicit non-claim |
|---|---|---|
| Label lifetime | At most one 120-second file | No persistence across files |
| Persistence condition | Position posterior remains inside the calibrated stationary gate | No continuity after material movement |
| User-facing label | Anonymous `caller-A`, `caller-B`, and so on | No biological name or enrolled identity |
| Ambiguous/overlapping interval | `unresolved` or excluded with duration reported | No forced assignment |
| File boundary | Expire every label | No automatic carry into the next recording |

**INFERRED** — This removes the need for a crow voice-enrolment database,
cross-day training corpus and long-term biometric false-match target. It does
not remove the need to validate track switches and false continuity inside a
file.

### 2. Conservative track state machine

```text
no source
  -> detected candidate
  -> stable caller-A while position/confidence remain inside the gate
  -> moving or low confidence: unresolved / new candidate
  -> file end: expire all labels
```

**PROPOSED** — Derive the gate from the estimator's calibrated uncertainty,
not from an arbitrary distance typed before roof testing. It may combine
position displacement, posterior overlap, TDOA residual and confidence, with
thresholds frozen only after held-out stationary and moving-source trials.

**INFERRED** — A different crow taking the same perch could produce the same
spatial label. Conversely, one crow moving far enough will receive a new label.
Both are correct under the user's stated scope because the label denotes one
stationary source episode, not one animal.

### 3. Planar geometry remains sufficient for this narrower purpose

**PROPOSED** — Continue with the nominal 8 m-diameter, eight-channel planar
study: seven mildly irregular outer microphones plus one center reference.
Compare four-outer/four-inner if measured wind or high-frequency ambiguity makes
a compact inner group more valuable than perimeter redundancy.

**INFERRED** — The full 8 m baseline bounds acoustic delay at about 23.26 ms or
1,116 samples at 48 ksample/s. Planarity still prevents a robust elevation/3D
claim, but elevation is not needed to preserve an anonymous label for an
approximately stationary source during one file.

### 4. Hardware and network requirements are unchanged

**PROPOSED** — Retain all eight synchronized channels from one local audio
clock. A short internal USB link and one external PoE/Ethernet uplink are now
accepted under ADR 0005; Raspberry Pi 5 is the selected host platform under
ADR 0008. Exact power, storage, cooling and module variants remain unaccepted.

**INFERRED** — A 120-second eight-channel recording contains about 184.32 MB
of sample payload in 32-bit PCM containers. Track metadata should reference the
immutable file and sample intervals; it must never replace the raw channels.

## Recommendations

1. **PROPOSED — use anonymous within-file labels.** Do not build a biological
   identity model or carry a label across file boundaries.
2. **PROPOSED — reset safely.** Motion, overlap, ambiguity or confidence loss
   starts a new label or `unknown` rather than forcing continuity.
3. **PROPOSED — derive stationarity from evidence.** Calibrate the gate with
   fixed, slowly moving and abruptly relocated acoustic-source trials.
4. **PROPOSED — retain the planar seven-plus-center study.** Its geometry is
   adequate for this source-continuity objective while remaining mechanically
   simpler than a raised 3D array.
5. **OWED — survey before CAD.** Exact coordinates, cable routes and roof
   mounting remain prerequisites to simulation and hardware acceptance.

## Validation plan

| Test | Required evidence | Acceptance boundary before architecture lock | Failure implication |
|---|---|---|---|
| Stationary 120-second source | Surveyed source held at several admitted roof positions; all raw channels and track receipt retained | Track-switch and unresolved ceilings are numerically set, then met on held-out positions | Rework geometry, calibration or estimator |
| Slow and abrupt motion | Controlled trajectories across and beyond the candidate gate | New-track/reset behavior follows the frozen confidence gate without false persistence | Tighten gate or change estimator |
| Same-perch source substitution | Two distinct acoustic sources used sequentially at one position | Output remains an anonymous spatial track and makes no biological-identity claim | User-facing semantics are unsafe |
| Overlap | Two sources active over controlled intervals | Overlap is marked unresolved/excluded; no forced identity; duration retained | Add detection guard or narrow admitted operation |
| File boundary | Two adjacent 120-second files with the same stationary source | Every label expires at the boundary; no automatic cross-file association | Remove persistent state from host pipeline |
| Raw-capture integrity | Eight channels, fixed order, 120 seconds, retained file/sample census | Zero lost/duplicated frames under the admitted clock and storage load | Reject audio/module/storage path |

## Source register

- [Project BRIEF](../BRIEF.md) — **CITED**, exact user clarification and current commission facts.
- [ADR 0007](../decisions/0007-within-file-stationary-caller-track.md) — **PROPOSED**, within-file track semantics.
- [ADR 0006](../decisions/0006-planar-signature-versus-3d.md) — **PROPOSED**, planar geometry and claim limit.
- [ADR 0005](../decisions/0005-poe-ethernet-roof-appliance.md) and [ADR 0008](../decisions/0008-raspberry-pi-5-roof-appliance-host.md) — **ACCEPTED**, network/USB boundary and host platform.
- [Superseded planar/cross-file report](2026-09-01-planar-8m-diameter-120s-follow-up.md) — **CITED**, still-current geometry arithmetic and superseded identity interpretation.
