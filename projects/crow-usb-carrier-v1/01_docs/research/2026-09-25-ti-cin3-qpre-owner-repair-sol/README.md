# Isolated C_IN3/Q_PRE owner-collision repair

**Research geometry result only.** The exact subject is the 15-part board
SHA-256 `d0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7`.
Terra's global census `e8d59a10` found one cross-owner full-envelope pair:
`C_IN3` (`input_buck`) and `Q_PRE` (`quiet_power`) overlap by 0.020 mm at a
courtyard corner, with no body or pad overlap. This packet tests one source
`post_anchor`: **`Q_PRE` from `(46.00,106.85,0°)` to `(46.00,107.15,0°)`**.
The 0.30 mm south move is smaller and less disruptive to the input capacitor
bank than moving `C_IN3`; at fixed x, y=107.15 balances the two nearest
full-envelope gaps at **0.260 mm** each (`C_IN3` north, `D_HOLD` south).
The 0.26 mm is a measured courtyard margin, not a qualified assembly
tolerance or route clearance.

`generator_overlay.yaml` derives from the frozen TI source and carries the
previous four ADC7 and 15 channel-8 poses plus this one Q_PRE change. The
hash-bound `regenerate.py` rebuilds both boards from the frozen TI netlist,
parts, library, and assembly profile. Baseline regeneration exactly matches
all 569 footprint poses and every pad number/net/layer/shape and relative-pad
position on the 15-part subject. Candidate board SHA-256 is
`e07ed8bc663fdfd4ce39477165b656b0dcf2bfbae54d84ec501bfccf326d22ef`.
Only `Q_PRE` moves; the 27 P1-fixed refs are unchanged.

Native full-envelope enumeration removes exactly `C_IN3`/`Q_PRE` and adds no
new pair. There are no Q_PRE inter-footprint pad overlaps before or after.
The native P-COLLIDE source pass reports zero pad shorts and zero fixed
courtyard overlaps. Same-net pad-center distances change modestly:

| Pair | Baseline → trial (mm) |
| --- | ---: |
| `Q_PRE.1` → `R_PRE_G.1` gate | 2.447 → 2.742 |
| `Q_PRE.2` → `D_HOLD.1` feed | 3.562 → 3.299 |
| `Q_PRE.2` → `R_PRE_G.2` feed | 4.553 → 4.838 |
| `Q_PRE.3` → `R_PRE.2` hold | 7.039 → 7.053 |
| `C_IN3` input/GND pads → matching `C_IN2` pads | 3.500 → 3.500 |

Native `kicad-cli pcb drc --format json` on the two regenerated boards,
without zone refill, yields **699 violations and 499 unconnected items on
each**, with identical violation type/description/item-UUID sets. Generator
silk-ownership warning refs are also unchanged at 279. No copper, body,
pad, or silk DRC issue is added by this move.

`census_replay.py` reruns Terra's full 569-ref checker-envelope census on the
candidate. Cross-owner native interaction pairs fall **1 → 0**; body and pad
overlap pairs remain zero. The other census counts do not change: 115 refs
remain outside their primary owner rectangle, and 139 refs still enter a
foreign planning region. `Q_PRE` itself remains in the overlapping
`input_buck` planning rectangle while staying fully inside its functional
`quiet_power` owner. Thus this move removes one obstacle to future physical
cell work; it does not create exclusive source cells, a route, a continuous
return, P1 acceptance, or P2 electrical/assembly qualification. The GND
zone is still unfilled.

Reproduce from this directory with `python3 regenerate.py --baseline`,
`python3 regenerate.py`, `python3 analyze.py > receipt.json`, and
`python3 census_replay.py`. The detailed [receipt](receipt.json) and
`census_delta.json` bind the exact board and checker hashes. No canonical
source, PCB, or stock was changed.
