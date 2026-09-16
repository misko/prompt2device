---
id: 0007
date: 2026-09-01
status: accepted
---
# 0007 — Within-file stationary caller track, not biological identity

## Context
The user clarified that recognition needs to persist only inside one
120-second recording and only if the crow does not move much. Cross-recording,
cross-visit, cross-day and changed-perch recognition are not required. A
position signature can maintain an anonymous source track under that boundary,
but cannot prove which biological bird occupies the position.

## Options
- **Within-file spatial track** — assign an anonymous label while the measured
  source signature remains in one calibrated stationary cluster; lowest model
  and labelling burden.
- **Within-file fused spatial/vocal identity** — add vocal embeddings to bridge
  small movements; adds training data and failure modes not requested.
- **Persistent biological identity across files** — requires labelled birds,
  context-held-out evaluation and an unknown-individual class; explicitly not
  required by the latest clarification.
- **No continuity label** — localize each call independently; simplest, but
  does not meet the requested within-file persistence.

## Decision
Use anonymous labels such as `caller-A` only within one 120-second file.
Maintain the label while the calibrated position posterior remains inside an
evidence-derived stationarity gate. Expire every label at file end. On material
movement, overlap, source ambiguity or confidence loss, reinitialize the track
or return `unknown`; do not infer biological continuity.

## Consequences
No crow enrolment database, voice biometric or cross-recording identity model
is required. The host still needs synchronized raw channels, surveyed
coordinates, calibrated timing, per-track confidence, and retained counts of
switches and unresolved intervals. A different crow arriving at the same perch
may receive the same anonymous spatial label; the system must never describe
that as proof of the same bird. The numeric stationarity/confidence gate is
derived from held-out stationary and moving-source tests before acceptance.
