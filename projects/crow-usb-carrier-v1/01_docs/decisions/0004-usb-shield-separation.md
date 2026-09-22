---
id: 0004
date: 2026-09-22
status: accepted
---
# 0004 — Keep USB shell separate from the Crow spoke shield network

## Context
The retained interface requires CHASSIS (all eight RJ45 shells) to remain separate from circuit GND. Mapping the USB shell to CHASSIS would extend this network onto a host cable whose shield can bond to USB ground. Merely retaining the net name does not preserve the original boundary.

## Decision
The complete carrier shall connect the USB receptacle shell directly to local GND at the USB connector and keep the RJ45 shells on CHASSIS. Do not route a USB shell connection into the spoke CHASSIS copper. This is an explicit engineering topology choice; no physical chassis/enclosure is assumed. The frontend guard permits shield=ground while rejecting any shield short to VBUS, either CC or either data net. The composed source must implement this decision before adoption.

## Evidence and qualification
TI applications support discusses Type-C plug shield/ground bonding and direct-ground versus RC choices at https://e2e.ti.com/support/interface-group/interface/f/interface-forum/1572741/tusb320evm-type-c-connector-shield-shell-grounding-methods (accessed2026-09-22). This is vendor guidance, not Crow EMC validation. The retained Crow interface requirement is recorded in 2026-09-22-crow-requirements.md, S1.

Provide a short local shell/ESD return with continuous ground and keep its currents away from the analog input/reference area through placement. Board-level ESD survival, conducted noise, cable current paths and EMC performance remain verification obligations. A direct USB shell bond must not be described as galvanic isolation from the Pi; USB signal ground already joins the device and host.
