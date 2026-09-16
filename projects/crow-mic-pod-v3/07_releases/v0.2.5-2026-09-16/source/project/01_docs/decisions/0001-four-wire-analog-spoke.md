# ADR-0001 — freeze one straight-through four-wire analog-spoke topology

Status: accepted for first article
Date: 2026-09-01

## Decision

Use a four-position Molex Micro-Fit 3.0 spoke with fixed straight-through pin
identity: pin 1 `12V_POD`, pin 2 `GND`, pin 3 `AUDIO_P`, pin 4 `AUDIO_N`.
The PCB header is `43650-0400`; both cable ends use housing `43645-0400` and
four `43030-0007` contacts. Belden `6541PA` assigns one shielded pair to power
and one to audio. Shield drains terminate at carrier chassis before the PCB
header and are insulated at the pod.

The required installed spoke is 4.0 m. The circuit is designed for 15.0 m, but
the qualified maximum remains unknown until end-to-end tests pass. The exact
machine contract is `03_src/rules/spoke_interface.yaml` and must remain
byte-identical to the parent contract.

## Why

A passive analog pod keeps sampling clocks and network electronics out of the
roof node, lets one central ADC sample all channels coherently, and needs only
one robust cable. Four contacts are the minimum that preserve a differential
audio pair and a separate power pair.

## Consequences

The pod is not Ethernet or PoE equipment and cannot connect directly to the
server. Cable polarity, shield termination, analog performance and connector
assembly are system-level obligations. Generated-artifact checks must prove
the exact connector MPN, footprint and pad nets rather than trusting this ADR.

## Enforced invariants

- J1 pin 1 is `12V_POD`, pin 2 is `GND`, pin 3 is `AUDIO_P`, pin 4 is `AUDIO_N`.
- J1 is exact Molex `43650-0400` with the selected horizontal THT footprint.
- F1 is first in series from `12V_POD`; neither audio leg is AC-coupled on pod.
- Carrier `1812L035/60MR` is the 0.70 A-trip cable/pre-pod tier; pod
  `0ZCJ0010FF2E` is the 0.25 A-trip downstream-board tier. Physical
  time-current coordination remains owed.
