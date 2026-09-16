---
id: 0006
date: 2026-09-01
status: accepted
---
# 0006 — Planar signature branch versus robust 3D

> **P7 scope note:** Caller continuity is now limited to one 120-second file
> while the position signature remains sufficiently stationary. ADR 0007 owns
> that label boundary; this ADR continues to own planar geometry and its lack of
> elevation evidence.

## Context
The user corrected the available study aperture to 8 m diameter, asks whether
the array can remain planar, and does not require simultaneous crows to be
separated. The later P7 clarification limits caller continuity to one
120-second file while the source remains approximately stationary. A planar
array is mechanically simpler but cannot close elevation or robust 3D.

## Options
- **Seven outer microphones plus one center, planar** — strongest single-source
  perimeter coverage and a stable center reference with eight channels.
- **Six outer plus two inner, planar** — gives one inner pair but loses an outer
  direction; the pair is not a useful compact array by itself.
- **Four outer plus four compact inner, planar** — better multiscale spatial
  filtering, but substantially less outer-aperture redundancy.
- **Shallow noncoplanar eight/twelve/sixteen-channel array** — restores
  elevation leverage at the cost of raised structure, wind and safety burden.

## Decision
Adopt an eight-channel planar seven-outer-plus-center v1 target at a nominal 4 m
outer radius. Survey and mildly de-periodize the actual outer coordinates. Use
the result only for a calibrated planar spatial signature, 2D/source grouping
and single-active-caller filtering; make no robust-3D or elevation claim. The
eight-channel count is locked; exact coordinates remain owed to the roof survey
and acoustic simulation.

## Consequences
The maximum study baseline is 8 m, corresponding to approximately 23.26 ms or
1,116 samples at 48 ksample/s. The sparse outer geometry has crow-band spatial
ambiguities, so the DSP must use broadband, pair-bounded delay estimation and
measured coordinates rather than narrowband phase steering. Overlap may be
reported unresolved or excluded, with its rate retained. Biological identity
is not claimed. A position-dependent anonymous caller label may persist only
under ADR 0007's within-file stationarity boundary. Elevation becoming required
reopens this decision.
