---
id: 0026
date: 2026-09-10
status: accepted
---
# 0026 — Exact distributor stock can admit regulator design work

## Context

The exact LT3041ADE#TRPBF / C7452883 has no stock in the current public JLC
catalog screen. A current public authorized-distributor product page identifies the same A-grade
MPN and package, with stock recorded separately in `manual_quotes.yaml`.
In response to the explicit request for a design-only distributor exception,
the user directed: “please verify public stock and contunue”.

## Options

- Keep waiting for the JLC catalog listing to change: no engineering progress.
- Replace the regulator: reopens electrical/package/thermal qualification when
  an exact-part supply lead already exists.
- Admit exact distributor evidence for design work while retaining every
  assembly and purchase gate: selected under the user's direction.

## Decision

Extend ADR0006's public-catalog pre-layout negative filter only for the exact
rows in `01_docs/sourcing/public-distributor-policy.yaml`. Its sole authorized
identity is U_LDO / LT3041ADE#TRPBF / C7452883, unchanged grade and package.
The provider row may move between exact public authorized-distributor listings
when the previous listing cannot cover the five-board quantity; the current
observation is Mouser cut tape. This is not a substituted BOM identity.

The checker requires an exact source/dossier/MPN/manufacturer/footprint/refdes
match, explicit brief and decision authority, an exact public product URL,
Active lifecycle and a timezone-stamped observation no older than24hours.
Observed stock must cover the build after supplier minimum/multiple expansion.
All other JLC rows must pass the existing exact-code screen. The original JLC
FAIL and its zero-stock row remain unchanged; the composed design result names
the distributor coverage separately. Network failures and missing codes are
not converted into stock evidence.

## Consequences

This admits schematic review, placement, routing and fabrication preparation
only. DO-NOT-ORDER remains mandatory. The operator worksheet stays blank; no
PCBA receipt is fabricated. This is not Q-2SOURCE, JLC global-sourcing acceptance,
allocation, quoted landed cost, lead-time assurance, release sourcing clearance,
or permission to spend. Procurement limits remain zero. Authenticated JLC
assembly/allocation/economics and separate purchase approval remain required
before ordering; all source/layout/review and later first-article obligations
are unchanged. New parts or non-authorized providers need another explicit policy decision.

The supporting workflow validates the recorded public observation and its
scope, not whether a human copied the website correctly or stock is reserved.
Refresh the observation at continuation and again before any order claim.
