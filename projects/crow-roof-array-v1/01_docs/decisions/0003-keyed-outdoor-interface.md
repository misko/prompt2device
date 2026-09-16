---
id: 0003
date: 2026-09-01
status: superseded
---
# 0003 — Keyed non-Ethernet outdoor interface and entry-safety boundary

> Superseded by ADR 0011. The anti-RJ45 and entry-safety conclusions remain;
> the board connector is now an internal Micro-Fit behind a sealed cable gland,
> not an unselected circular PCB mate.

## Context
The archived pod exposes custom power on RJ45 contacts and the archived
central board assigns those power contacts differently. A straight-through
cable therefore creates a hard short. Ordinary RJ45 also invites connection
to Ethernet/PoE equipment. Rooftop copper adds weather, surge, bonding and
building-entry obligations beyond ordinary board ESD.

## Options
- **Reuse custom RJ45** — cheap and easy to cable; rejected because the legacy
  map is destructive and the connector carries the wrong semantic affordance.
- **Keyed weather-resistant circular assembly** — distinguishes the system
  from Ethernet and supports sealing; exact M12 or alternative family is owed.
- **Wireless/digital pods** — avoids long analog copper but adds firmware,
  clock, radio, power and weather complexity outside this commission.

## Decision
Propose a keyed non-Ethernet circular cable assembly, one normative pin map
validated at both boards, per-port protection indoors, and an explicit rule
that PCB validation does not certify lightning/building-entry safety.

## Consequences
Connector, cable, backshell, shield and enclosure become one qualified
assembly. Stock Cat5e may be used only as internal conductor technology if the
selected assembly and pair map prove it; it is not an Ethernet interface.
Unattended roof deployment remains blocked until a qualified person reviews
entry bonding/surge protection and physical first articles pass weather tests.
