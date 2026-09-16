---
id: 0008
date: 2026-09-01
status: accepted
---
# 0008 — Raspberry Pi 5 Model B as roof-appliance host

## Context
ADR 0005 requires a Linux roof appliance between the internal USB Audio Class
2 module and the building Ethernet link. The user explicitly selected
Raspberry Pi 5 for that role. The Pi must capture and spool the already
sample-synchronous channel stream without becoming the acoustic sampling clock.

## Options
- **Raspberry Pi 5 Model B** — user-selected, standard Gigabit Ethernet and
  Linux USB Audio Class 2 support, with official cooling and PCIe-storage
  accessories; exact RAM and storage remain selectable.
- **Compute Module 5 carrier** — cleaner embedded packaging, but adds a custom
  high-speed carrier and materially more bring-up and mating risk.
- **Direct-TDM Linux SoM** — removes the USB module, but adds ALSA, device-tree,
  clock and carrier integration not required by the user.
- **Earlier Raspberry Pi** — adequate for basic capture, but contrary to the
  selected platform and with less compute/storage headroom.

## Decision
Use the Raspberry Pi 5 Model B family as the roof-appliance Linux host. Connect
the unchanged multichannel audio module over a short internal USB link and use
the Pi's wired Ethernet interface for the single external network path. Keep
the local audio module and ADC clock as timing authority.

## Consequences
The exact RAM SKU, board revision, boot/storage medium, cooler, PoE PD or
splitter, power-delivery mode, enclosure and service stack remain commission
facts rather than implied parts. Mechanical CAD must bind the current official
STEP and a measured physical unit, not treat a reference drawing as production
authority. Host software may capture, checksum, buffer and upload recordings;
it is not project-authored embedded firmware and its output cannot substitute
for raw synchronized channels. Bench qualification must prove uninterrupted
capture, file integrity, network recovery, power margin and thermal behavior
before any roof installation. Direct-hardware PCM continuity, ADC interchannel phase
after resets, analog quality under concurrent compute/storage/network load,
crash-recovery-tested local spooling and conflict-detecting retry-safe upload are explicit proof
obligations; an exact frame count or successful network acknowledgement alone
is insufficient.
