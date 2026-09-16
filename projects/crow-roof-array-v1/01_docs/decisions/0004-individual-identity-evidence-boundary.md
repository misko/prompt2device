---
id: 0004
date: 2026-09-01
status: superseded-by-0007
---
# 0004 — Spatial tracking as an intermediate to persistent biological identity

> **P7 disposition:** The user later restricted recognition to one 120-second
> file while the crow remains approximately stationary. ADR 0007 supersedes
> this persistent-biological-identity proposal; this file remains the historical
> record of the broader option.

## Context
The user wants to know which crow is calling and is willing to use a 3D
position or multi-position signature. A microphone array can associate calls
with simultaneous spatial source tracks. Position alone cannot prove that a
bird which moves or returns later is the same biological individual. Persistent
voice identity also varies with call type, context, distance, weather and the
quality of source separation.

## Options
- **Session-local source identity** — report stable anonymous tracks such as
  `crow-A` and `crow-B` while their trajectories remain separable.
- **Persistent voice-only identity** — train an individual classifier from
  labelled isolated calls; highest dependence on representative field data.
- **Camera-assisted enrolment and audio inference** — use synchronized visual
  labels to construct the training/evaluation corpus, then attempt audio-only
  inference with an explicit unknown class.
- **Position-zone labels only** — classify one of several calibrated perch
  zones; useful operationally, but it identifies a zone rather than a bird.

## Decision
Propose two separately graded outputs. Persistent biological identity is the
desired system result. Session-local spatial source tracking is a mandatory
isolation, labelling and ground-truth intermediate, but does not satisfy the
identity goal. Persistent identity may be reported only after camera- or
marked-bird labels, source-isolated audio, a day/context-held-out evaluation,
declared false-match and false-reject ceilings, and a genuine unknown-individual
class.

## Consequences
The PCB must preserve synchronized raw channels and enough surveyed geometry
for the selected spatial-signature branch, but it does not certify identity.
The user now requires identity across separate 120-second recordings and does
not require simultaneous-crow separation. Therefore whole recordings are the
minimum indivisible unit, while recordings from one encounter or visit must be
kept in the same validation group. Overlapping calls may be unresolved or
excluded with their rate reported, and training positions may not be reused as
the only identity holdout. A confident source track and an uncertain individual
classifier are reported separately. Q4/Q7 must define the inter-recording time
span, enrolment evidence and acceptable errors before this ADR can be accepted.
