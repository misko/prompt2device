---
id: 0031
date: 2026-09-16
status: accepted
---
# 0031 — Exact authorized public stock uses the configured surplus

## Context

The carrier's exact LT3041ADE#TRPBF and TMUX2821DSGR identities are electrically
and geometrically frozen. Public JLC catalog stock is below the configured
five-board requirement plus 150 units, although current exact-part inventory is
available through the authorized distribution channel. The standing user
directive is “please verify public stock and contunue”; the current instruction
also requires the process and skill to use a configured surplus of 150.

## Decision

The design-only public-catalog pre-layout stock screen may cover a JLC
`LOW_STOCK` line with an
exact-MPN observation from a supported public distributor product page or a
narrowly validated ECIA TrustedParts authorized-only aggregate. The checker
must match manufacturer, MPN, footprint, designators, public URL and a fresh
observation to current source and dossier authority. It must require:

`public stock >= build required quantity + assembly.public_stock_surplus`

For this project the thresholds are 155 LT3041 regulators and 190 TMUX2821
switches. Current observations report 1,965 and 2,449 respectively.

## Consequences

This closes the design-time public-stock shortages without changing either
part, footprint, schematic, PCB, BOM, CPL or fabrication output. It does not
prove a reservation, JLC assembly availability, consignment receipt, price,
lead time, or authority to spend. `DO-NOT-ORDER` and the first-article boundary
remain. Order admission still requires exact allocation or acquired exact
parts, uploader evidence, procurement economics and the normal order gates.
