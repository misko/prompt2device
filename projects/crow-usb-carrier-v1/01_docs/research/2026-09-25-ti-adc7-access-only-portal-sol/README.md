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
not a measured return. The local portal record is `INCOMPLETE` with
`capacity_slots: null`; the overall checker retains `routing_realized: false`
and `p1_accepted: false`.

The generic checker recognizes `access_only_portals` only when that source
key is present. It requires an exact field set, modular/source owner equality,
native pad multiset equality, positive transit-owner edge contact, exact
named planning overlap, no native body/pad/track/signal fill/rule-area
intrusion, and exact P2/return declarations. It also rejects overlapping
same-layer ordinary reservations, integration corridors, linked physical
stages, and foreign physical cells. It reports the portal outside allocation
reservation and capacity accounting. Missing or extra endpoints,
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
All 157 P1 checker tests passed in this replay.

## Independently reviewed four-part board replay

The isolated [four-part board](../2026-09-25-ti-adc7-four-part-margin-sol/README.md)
SHA-256 `046019a13094764baef313d62611b137e0f0af971079734c71ab050dbf46b3a0`
was replayed with this unchanged portal declaration. The deterministic
[`replay_four_part.py`](replay_four_part.py) merges the base research P1 source
and `portal.yaml`, rebinds the old coarse contract to the new board/source,
then runs the **full** coarse evaluator. The [receipt](four_part_result.json)
binds the merged source SHA-256
`553b062a963f139cac9a9d987635861e56849dc040fc2602f9be8891a12ea9d7`
and contract SHA-256
`409f8221f8afcbdd372b9bd46912dffdb34f8e415f56538afbf4e22ea5e7e357`,
plus the board, modular-plan, floorplan, alias and portal hashes. The local
portal screen still binds eight exact ADC7N/P native terminals, eight P2 pad
obligations, and In1.Cu filled-return debt with `INCOMPLETE` and null
capacity. The **full contract now correctly fails** with
`adc7_local_portal: overlaps ordinary reservation analog_5_8`: that
unmodified F.Cu reservation is `[113.25,71,201,85]` and covers the portal.
`routing_realized` and `p1_accepted` remain false. No same-layer co-use is
admitted in this first slice. The next source step is to redesign the analog
reservation and rerun its complete net/witness/capacity checks; this packet
does not carve an exception or claim the redesign is feasible.

The nearest physical body/pad to `[166,83.9,167.12,85]` is `Y_AUDIO` in
both boards. Its full physical-envelope gap grows from **0.105 mm** on the
three-part board to **0.255 mm** on the four-part board, a **0.150 mm** gain.
This measures geometry only. The four-part board still has 15 silkscreen
warnings and unresolved pad access, native route, and filled-return proof;
the 0.25-mm illustrative margin is not an admitted P1 design rule.

Replay from repository root without writing source or board files:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-adc7-access-only-portal-sol/replay_four_part.py
```
