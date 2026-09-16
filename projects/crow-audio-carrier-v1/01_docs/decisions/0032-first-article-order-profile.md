---
id: 0032
date: 2026-09-16
status: accepted
---
# 0032 — Freeze the carrier first-article order profile

## Context

The reviewed carrier release is design-sound, publicly sourceable and intended
to produce five first articles, but its sealed README deliberately leaves the
live uploader choices and purchase authorization open. User directive D9 now
authorizes the prototype order after those checks. The order must also preserve
the release's selective Type VII via process and its split between 300
machine-placed top-side parts and 33 manually fitted parts per board.

## Options

- **Leave finish, mask, stack and via process to defaults** — lowest operator
  effort, rejected because a default can lose QFN planarity, change the modeled
  reference spacing or leave the twelve via-in-pad barrels open.
- **Lead-free HASL on a generic four-layer stack** — cheaper, rejected because
  its surface is less planar for the 0.4 mm-pitch QFN and it does not bind the
  stack used by the routed clock calculation.
- **ENIG on JLC04161H-7628 with selective epoxy fill and cap** — selected. It
  keeps a planar pad surface, preserves the modeled layer spacing and makes the
  via-in-pad instruction explicit.

## Decision

Order five carrier first articles as JLCPCB Standard PCBA using FR-4,
four copper layers, 1.6 mm finished thickness, JLC04161H-7628, 1 oz finished
outer copper, 0.5 oz inner copper, green solder mask, white silkscreen and ENIG
1 microinch. Select controlled impedance so the named stack is contractually
bound, while retaining the submitted artwork. Select epoxy-filled and
copper-capped vias and apply it only to the twelve 0.60/0.30 mm sites named in
`fab/order_notes.txt`; keep all 589 0.50/0.20 mm ordinary vias unfilled. Enable
production-file confirmation.

Upload only the Gerber ZIP, BOM and CPL from immutable release
`v0.1.7-2026-09-16`. JLC places its 300 CPL references on the top side. The
33 declared exclusions remain outside automated assembly and are fitted from
the exact manual-parts list. Any redirected code, substituted MPN, wrong side,
unapproved rotation or different via interpretation stops payment.

## Consequences

The order is authorized only as a supervised first-article build. It does not
change schematic, PCB, Gerber, BOM or CPL bytes and does not require a new
design release. JLC allocation, quote economics and CAM interpretation remain
live order evidence. Reset/TDM/audio, loaded copper temperature, cable mating,
fault behavior and environmental qualification remain post-delivery tests and
still block production or roof deployment.
