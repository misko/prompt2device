---
id: 0012
date: 2026-09-12
status: accepted
---
# 0012 — Shielded Cat5e pod cable with the existing board connectors

## Decision and scope

The user requested Cat cable for the pods and authorized implementation.
Use Belden7939A, black ordering variant7939A0101000: outdoor-rated,
shielded Cat5e with four24AWG stranded bare-copper pairs. Retain Molex
43650-0400 board headers,43645-0400 housings and43030-0007 contacts.
This supersedes the6541PA cable choice in ADR0011. Internal connectors,
sealed cable glands, carrier-entry chassis bond and pod-end shield isolation
remain. The existing PCB footprints and electrical pin maps do not change.

The implementation assumption announced to the user is bulk Cat cable with
Micro-Fit terminations. Ready-madeRJ45 patch leads are a separate prospective
option, not silently selected by this decision. No RJ45 or archived pin map
is introduced; no Ethernet, standardPoE or hot-plug capability is claimed.

## Wiring — identical at both ends

The authoritative machine-readable map is
[`spoke_interface.yaml`](../../03_src/rules/spoke_interface.yaml), mirrored
byte-for-byte in both child projects and checked against actual PCB/schematic
connector pads. Colours below name the physical paired conductors, not RJ45
pin numbers. Orient housing cavities by the manufacturer's numbered drawing.

| Cable conductors | Function | Micro-Fit cavity |
|---|---|---|
| White/blue | AUDIO+ | 3 |
| Blue | AUDIO− | 4 |
| White/orange, white/green, white/brown | Three parallel +12V conductors | 1 through positive join/pigtail |
| Orange, green, brown | Three parallel return conductors | 2 through return join/pigtail |
| Foil/drain | Carrier chassis at enclosure entry; insulated at pod | None |

Each power pair contains one positive and one return conductor. At each end,
two separate WAGO221-415 five-port joins combine the three positive wires
and the three return wires respectively. Each join has three24AWG cable
wires and one22AWG Belden8503 pigtail, in four separate ports. The fifth port
is empty with its lever closed. Use red positive and black return pigtails,
maximum150mm each. Only one wire enters each Molex contact. Audio uses one
24AWG conductor per contact; keep its pair twisted close to the termination.
Do not use the shield as return or put several wires into one crimp barrel.

Selected quantities per complete spoke: one cut-to-length cable, two housings,
eight contacts, four WAGO joins and four power pigtails. These are off-board
harness items, not JLC PCB assembly BOM additions. Exact gland, restraint,
join mounting and enclosure service-space qualification remain owed.

## Electrical screening

Manufacturer cable DCR ceiling:93.8ohm/km. Three conductors in parallel per
rail at15m give `2 × 15 / 1000 × 93.8 / 3 = 0.938ohm` cable loop.
The design uses a conservative1.25 hot-resistance multiplier for20to75C and
allocates0.30ohm for all pigtails, joins and connector contacts combined:
`0.938 × 1.25 + 0.30 = 1.4725ohm`. At100mA the drop is0.14725V, leaving
10.65275V from the existing10.8V minimum carrier output. The original
2.2ohm whole-loop ceiling and10.5V pod minimum are unchanged.

The temperature factor and0.30ohm allowance are design bounds, not measured
manufacturer connector resistances. Finished harness measurement must confirm
them. The cable's75C operating range does not change its separate60C UL
temperature row. Fifteen metres remains a qualification reference, not a
tested maximum; actual installed lengths remain surveyed facts owed.

The four-pair cable has an overall shield instead of the old individual pair
shields. Audio capacitance, balance, power-to-audio coupling and phase must
be requalified. The published capacitance-unbalance field is not pair
capacitance. No old6541PA analog calculation or qualification transfers.

## Mechanical and first-article acceptance

The nominal cable diameter rises from5.44to7.49mm. Use a gland actually
qualified for this jacket and diameter. Retain a conservative53mm bend and
straight-run planning allowance despite the manufacturer's15mm stationary
minimum; this is not installed-fit evidence. All-eight carrier access must
include the16 internal WAGO joins and pigtails. Pod access includes two.

Before building/qualifying the harness:

1. Verify cable identity, copper construction, jacket, pair colours and
   actual insulation OD after bonded-pair separation; audio insulation must
   fit the selected contact's1.85mm maximum without damage. Complete the
   selected63819-0000 tool's separate24AWG and22AWG crimp setup/pull tests.
2. Verify every power conductor end-to-end before paralleling. Verify final
   cavities1–1,2–2,3–3,4–4; reject shorts, audio polarity swaps, split pairs
   and shield continuity to any cavity. Confirm the carrier chassis bond and
   pod shield isolation independently.
3. Measure complete loop resistance and pod voltage at maximum intended
   cable temperature and100mA. Demonstrate the non-cable0.30ohm allocation
   and whole-loop2.2ohm ceiling; continuity alone cannot detect a missing
   parallel conductor after joining.
4. On4m and15m specimens, measure audio gain, noise, crosstalk, polarity,
   relative phase and startup with all eight channels powered/recording.
   Check one faulted spoke against seven healthy spokes and retain existing
   inrush, fault-energy, recovery and outdoor entry-protection requirements.
5. Qualify strain relief, retained joins, bend clearance, pull resistance,
   all-connected service access, weather sealing and actual rooftop thermal
   conditions. Outdoor cable alone does not qualify the appliance.

## Evidence and release impact

Exact manufacturer facts and decodedPDFs are retained in
`02_parts/7939A/`, `02_parts/8503/` and the WAGO page-fact record in
`02_parts/221-415/`. No stock allocation or physical pass is claimed.

Source changes apply prospectively to the parent and both child projects.
The existing pod release remains immutable and describes the previous
harness. Board pad compatibility does not revise that release's contract.
Renew affected schematic/source and connector-service reviews through the
normal gates; previous whole-contract reviews are stale. The carrier remains
DO-NOT-ORDER and still needs layout/routing/release closure.
