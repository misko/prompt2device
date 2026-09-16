---
id: 0010
date: 2026-09-01
status: accepted
---
# 0010 — Use one CS5308P for the eight-channel carrier

## Context
The earlier studies compared several four-stereo-ADC arrangements. Further
primary-source review found that a four-device TAA5242 hardware daisy chain is
not supported; using four devices would require software slot programming,
contrary to the no-project-firmware boundary. Multiple ADCs would also leave a
reset-to-reset inter-device phase question that is unnecessary for eight
channels.

Cirrus Logic's CS5308P integrates eight differential ADC channels on one die
and supports processor-free hardware control. In secondary, TDM
minimum-time-slot mode at 48 ksample/s it uses one data output with eight
32-bit slots and accepts BCLK at 256 times the sample rate. Those values match
the MCHStreamer TDM8 clocks exactly: 24.576 MHz MCLK, 12.288 MHz BCLK and
48 kHz FSYNC.

## Options
- **Four independent stereo ADCs** — more available assembly options, but
  requires multiple data lanes or unsupported hardware chaining and adds
  inter-device reset/phase risk.
- **One software-controlled multichannel ADC** — flexible, but requires a
  processor and project-authored initialization firmware.
- **One hardware-controlled CS5308P** — one clocked conversion domain and one
  TDM8 lane, with no runtime control firmware; currently requires consigned or
  manual assembly.

## Decision
Use one `CS5308P-DN` on `crow-audio-carrier-v1`. Strap it for 44.1/48 kHz ASP
secondary mode, TDM minimum slots, default channel order and one fixed
linear-phase filter. Connect MCHStreamer TDM8 J1 MCLK, BCLK, FSYNC, ground and
input-data signals over a retained internal cable. Use the Cirrus-recommended
buffer/filter topology and buffered VMID for all eight differential inputs.

## Consequences
The carrier needs a hardware sequencer for the CS5308P's specified startup
sequence: RESET high after power, wait at least 2 ms, assert low for at least
1 ms, then return high. The exact sequencer timing, MCHStreamer TDM8 vendor
image, data edge, channel order, 32-to-24-bit interpretation, fixed group delay
and reset/temperature repeatability remain first-article proof obligations.
The current JLC catalog record is not allocated, so the release must remain
`DO-NOT-ORDER` until authorized sourcing or an accepted consignment/manual
placement path is captured. This decision supersedes the earlier TAA5242 and
four-PCM1861 carrier candidates; their dated reports remain historical studies.

## Evidence
- Cirrus Logic, `CS5308P_DS1314F1`, SHA-256
  `6ca42cc09ac47ebdacacaee435f05e3f9c34b83d5692e52a2d8a26533e810e57`,
  accessed 2026-09-01:
  <https://statics.cirrus.com/pubs/proDatasheet/CS5308P_DS1314F1.pdf>
- miniDSP, `MCHStreamer User Manual`, SHA-256
  `2cf36d628df68607d007b971a13a3a578916d74629d6660571daf218cfbc6edd`,
  accessed 2026-09-01:
  <https://www.minidsp.com/images/documents/MCHStreamer%20User%20Manual.pdf>
- TI support clarification that TAA5242 hardware daisy chain is limited to two
  devices, accessed 2026-09-01:
  <https://e2e.ti.com/support/audio-group/audio/f/audio-forum/1487177/tac5242-tdm-8-and-application-circuits>
