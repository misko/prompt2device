---
id: 0001
date: 2026-09-22
status: accepted
---
# 0001 — New carrier with onboard USB interface

## Context
The user explicitly requests a new Crow carrier with an onboard IC connecting
directly over USB to a Raspberry Pi. The previous carrier delegated USB to an
external MCHStreamer; that boundary cannot satisfy this request.

## Options
- Retain the external MCHStreamer: does not meet the requested onboard-IC boundary.
- Put an entire COTS bridge module on the carrier: useful implementation precedent,
  but does not satisfy the intended bare onboard interface IC without clarification.
- Integrate a USB-audio interface IC and support circuits: meets the requested
  boundary; exact IC, power, clock, firmware and sourcing remain under review.

## Decision
Create a separately commissioned carrier project and integrate the USB interface
at IC level. Do not copy an old solved board or treat its release evidence as
approval of the new circuitry. This ADR selects the boundary, not a particular IC.

## Consequences
The prior TDM/presence connector interface, independent-power protection and
clock ownership must be reconsidered. Requirements may be adopted explicitly
with provenance, but all changed electrical and physical paths need fresh
review. Firmware authorization and exact acquisition/configuration paths are
separate open dependencies. The new project remains under its commission hold.
