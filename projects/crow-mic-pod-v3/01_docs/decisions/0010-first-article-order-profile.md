---
id: 0010
date: 2026-09-16
status: accepted
---
# 0010 — Authorize the pod first-article order profile

## Context

ADR0005 correctly prevented an unreviewed design from being ordered, but the
pod now has immutable release `v0.2.5-2026-09-16`, DRC 0/0/0, accepted
connector orientation, top-only SMD placement and surplus-backed public
sourcing. User directive D7 authorizes ordering ten first articles after the
remaining live uploader checks. Measurements cannot precede fabrication of the
articles they will qualify.

## Options

- **Keep the blanket no-order state** — rejected because it makes physical
  qualification impossible after the design and release gates have closed.
- **Order production quantity immediately** — rejected because cable, audio,
  thermal, enclosure and environmental tests remain open.
- **Order ten controlled first articles** — selected; this matches the existing
  eight installed plus two spare build quantity and retains all physical tests.

## Decision

Order ten pod first articles as JLCPCB Economic PCBA using FR-4, two copper
layers, 1.6 mm finished thickness, 1 oz finished copper, green solder mask,
white silkscreen and ENIG 1 microinch. Use the standard two-layer construction,
no controlled-impedance service and ordinary tented vias. Enable production-file
confirmation and stop if the interpreted outline, drills or copper differ from
immutable release `v0.2.5-2026-09-16`.

JLC places the 31 CPL references on the top side. J1 remains a manually fitted
exact Würth 615008160221 jack, MK1 remains the off-board exact
AOM-5024L-HD-R capsule, and TP1–TP7 remain bare probe pads. Any redirected
code, substituted MPN, wrong side or unapproved U1/U2 rotation stops payment.

## Consequences

ADR0005 is superseded only at the first-article purchase boundary. This order
does not authorize production or deployment. J1/cable continuity, capsule
polarity and strain relief, rail/noise/gain/clipping, thermal behavior, EMC and
roof environmental qualification remain required after delivery.
