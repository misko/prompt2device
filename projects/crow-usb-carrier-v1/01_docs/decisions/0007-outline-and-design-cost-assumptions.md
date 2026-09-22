---
id: 0007
date: 2026-09-22
status: accepted
---
# 0007 — Outline and design cost assumptions

## Context

The user authorized a new Crow carrier with an onboard USB IC and a cable
connection to the Raspberry Pi. No Pi HAT, enclosure, mounting-hole pattern,
maximum board dimensions, or numeric design budget was supplied. The current
source already describes a rectangular 220 × 120 mm board. That dimension
needs an explicit design owner rather than inheriting authority from the old
carrier. ADR 0006 owns the four-layer stack and proposed advanced process.

## Options

- Adopt the current 220 × 120 mm outline as a reversible first-placement
  assumption. This gives the eight analog channels, eleven connectors, digital
  section and power section a concrete placement domain without asserting fit.
- Treat the old carrier outline and holes as mandatory. Rejected because the
  new cable-connected design has no stated mechanical interface requiring them.
- Shrink the board before placement. Deferred: no placed escape, connector
  service-space or routing evidence yet supports a smaller outline.
- Set an invented numeric budget ceiling. Rejected because no user budget or
  final manufacturing quotation supports a number.

## Decision

Adopt the source rectangle x=20..240 mm, y=20..140 mm as the initial design
outline, with no inherited mounting holes. It is an engineering assumption for
placement, not a maximum dimension, product-fit guarantee or fabrication seal.
Change it through a recorded placement backtrack if actual spacing or routing
requires it; revisit unnecessary area after a viable placement exists.

The design-stage cost posture has no supplied hard numeric ceiling. Seek the
least costly process supported by actual engineering evidence, using ADR 0006
as the current candidate. This does not set an unlimited purchasing budget:
authorized expenditure remains zero. Obtain and compare quotations for the
realized board and populated BOM before any request to spend. A future user
budget or quote that makes the design unsuitable reopens this assumption.

## Consequences

The floorplan coordinates become explicit current design intent without
changing source geometry. Connector placement, handling/service clearance,
escape, routing, losses and thermal performance still require native evidence.
There is no claimed enclosure or Raspberry Pi mounting compatibility.

This closes only the outline/cost-posture disclosure. It does not remove the
commissioning hold, approve source selection, lock placement, accept the
proposed selective via process, authorize firmware, or authorize an order.
