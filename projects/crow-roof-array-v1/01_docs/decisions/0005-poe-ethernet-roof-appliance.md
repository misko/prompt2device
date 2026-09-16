---
id: 0005
date: 2026-09-01
status: accepted
---
# 0005 — One external PoE/Ethernet roof-appliance uplink

## Context
The user can run Cat6 PoE to the device and asked whether external USB is
necessary. The candidate multichannel audio module exposes USB Audio Class 2,
not Ethernet. The user later explicitly permitted a short internal USB link,
then accepted this roof-appliance boundary and selected Raspberry Pi 5 as its
Linux host in BRIEF P8.
Local simultaneous ADC conversion must remain on one audio clock; network
packet timing is not an acoustic sampling clock.

## Options
- **PoE+ roof appliance with internal USB** — one genuine PoE/Ethernet uplink
  powers a Linux SBC, audio module and ADC carrier; a short sealed USB link is
  internal only. Lowest custom-software and PCB risk.
- **Direct TDM/I2S into a Linux SoM** — removes the USB module but adds a custom
  carrier, ALSA/device-tree/clock integration and wider software validation.
- **OEM Dante/AES67 module** — native network audio and PTP, but brings OEM
  licensing, carrier and procurement complexity disproportionate to v1.
- **One PoE/Ethernet node per microphone** — short analog paths, but requires
  multiple roof cables and PTP-disciplined sample clocks at every pod; rejected
  as the baseline.

## Decision
Use one standards-compliant Cat6 PoE/Ethernet uplink to a sealed Linux roof
appliance. Use a short internal USB link from an unchanged multichannel UAC2
module to the Raspberry Pi 5 selected by ADR 0008. Sample all channels from one
local ADC clock before packetization, and never derive TDOA from Ethernet
packet arrival time.

## Consequences
The external topology and internal-USB boundary are accepted; the power
implementation is not. Exact PSE, PD, PoE type, USB-C power advertisement,
cable length, conversion loss, thermal derating and auxiliary loads are owed
by Q6 and the commission fact lock. The currently listed Raspberry Pi PoE+
HAT is not accepted as a Pi 5 solution merely because its name is similar.
The building-facing RJ45
is genuine PoE/Ethernet. Every analog microphone spoke remains keyed and
non-Ethernet. Outdoor cable, connector, shield, surge protection, bonding and
building entry require a qualified system review; PoE isolation is not
lightning protection.
