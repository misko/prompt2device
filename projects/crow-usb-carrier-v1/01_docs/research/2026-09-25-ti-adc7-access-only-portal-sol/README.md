# ADC7 access-only portal first-slice packet

**Isolated research, 2026-09-25.** [`portal.yaml`](portal.yaml) is an opt-in
source record for the SOL local-oscillator
[`candidate.kicad_pcb`](../2026-09-25-ti-adc7-local-osc-probe-sol/candidate.kicad_pcb)
(SHA-256 `c9b758d69867b274f0592bd2eceb9a26d64a80dd2daafa8ab9516d23d5925502`).
The packet does not edit canonical Crow source or PCB and is **not** a P1
attempt, route, DRC pass, or placement acceptance. The candidate retains 12
new silkscreen warnings and the broader ADC/audio floorplan remains open.

The record binds ADC7N/P's eight exact modular/source/native terminals:
six `analog_ch7` pads and `U_ADC_B.11/.10` in `adc_reference`. The local
portal `[166,83.9,167.12,85]` crosses analog's north edge into the
`audio_clock_tdm` *planning region*. Audio is named only as a non-electrical
planning overlap and owns no ADC7 signal endpoint. Each analog pad carries
`P2_REQUIRED` native-pad-to-local-port debt; the ADC pads carry separate
remote-route debt. An In1.Cu continuous filled-GND return is also debt,
not a measured return. The checker result is `INCOMPLETE` with
`capacity_slots: null`, `routing_realized: false`, `p1_accepted: false`.

The generic checker recognizes `access_only_portals` only when that source
key is present. It requires an exact field set, modular/source owner equality,
native pad multiset equality, positive transit-owner edge contact, exact
named planning overlap, no native body/pad/track/signal fill/rule-area
intrusion, and exact P2/return declarations. It reports the portal outside
allocation reservation and capacity accounting. Missing or extra endpoints,
an audio electrical-owner claim, a foreign planning overlap, or any source
success/capacity field fails closed. Absent the key, output shape is
unchanged.

Replay from repository root:

```sh
python3 -m unittest discover -s skills/kicad-pcb/scripts/tests -p 'test_p1_*.py' -q
```

The focused `test_p1_access_only_portal.py` loads the exact packet and board
by hash, exercises positive and negative native tests, and checks that an
opted-in fixture leaves legacy allocations, status, routing and P1 fields
unchanged. The first-slice packet hash is
`f1952e27cebd1eb3fa3b1ebc4863ed7d408f4b04d603a8c76454a063eff719ae`.
All 156 P1 checker tests passed in this replay.
