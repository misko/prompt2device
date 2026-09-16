---
id: 0006
date: 2026-09-02
status: accepted
---
# 0006 — Public catalog is a pre-layout negative filter only

Timing clarification (2026-09-07): ADR-0007 supersedes the final paragraph's
requirement to finish physical/first-article tests before a prototype order.
The catalog-versus-allocation distinction and order authorization are unchanged.

## Context

The authenticated JLCPCB PCBA uploader is unavailable to this task. The exact
pre-layout request remains preserved, its operator response remains blank, and
no JLCPCB receipt exists. The user nevertheless directed: “please do this for
me , use only public information, lets keep moving”. Public JLC/LCSC catalog
stock can eliminate presently unavailable exact codes, but it cannot establish
assembly allocation, feeder availability, attrition, MOQ, fees, or price.

## Options

- Stop all design work until an authenticated uploader result exists.
- Fabricate a JLCPCB response from public stock. Rejected because it would
  misrepresent catalog data as provider allocation.
- Admit a fresh, exact-code public-catalog screen for pre-layout design work
  while retaining the authenticated sourcing and order gates.

## Decision

Accept the third option. A current `jlc_stock_check.py` PASS covering every
exact requested code and build quantity may unlock schematic review,
placement, routing, and fabrication-package preparation only. The board stays
`DO-NOT-ORDER`; the blank operator worksheet is not populated and no
`prelayout_receipt.json` is created.

## Consequences

Every continuation rechecks the frozen request and the public evidence's
limited scope and freshness. Public catalog data never authorizes a
substitution, purchase, PCBA allocation claim, release sourcing clearance, or
order. A logged-in JLCPCB result, exact economics, physical connector evidence,
and first-article testing remain mandatory before order or deployment.
