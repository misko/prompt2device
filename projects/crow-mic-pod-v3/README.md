# Crow microphone pod v3

> **FIRST-ARTICLE-ONLY / DO NOT ORDER**

This child project is the remote analog microphone pod for one arm of the
8 m-diameter crow-roof array. One electret capsule is biased and amplified
locally; an active-balanced analog pair plus 12 V and return traverse one
straight-through four-conductor spoke to the central carrier.

The board intentionally contains no MCU, ADC, Ethernet, PoE, USB interface or
beeper. The Raspberry Pi 5 and audio conversion stay at the central carrier.

The electrical source of truth is
[`03_tscircuit/src/crow_mic_pod_v3.tsx`](03_tscircuit/src/crow_mic_pod_v3.tsx).
The exact inter-board contract is
[`03_src/rules/spoke_interface.yaml`](03_src/rules/spoke_interface.yaml).

Do not order from this repository state. The PCB design release is sealed, but
cable-length noise/headroom, capsule/enclosure integration, connector service
geometry, authenticated PCBA availability, thermal behavior and the full
first-article test matrix remain open. See
[`01_docs/STATUS.md`](01_docs/STATUS.md).

The corrected schematic, exact placement and routed board are frozen in the
[`v0.1.0-2026-09-03` design release](07_releases/v0.1.0-2026-09-03/).
Independent schematic reviews pass 2/2 and independent pin, layout, render and
model-registration placement reviews pass 4/4 against board SHA-256
`f27517687df124b8cab11830785659c69f1676e9d466adef4da1beacae133b22`.
The exact routed board SHA-256 is
`a932200e0976418383fae0c131dfe2a5768c00ef261b611762ccd3507f05ca8f`.
All 22 governed realized-path checks pass, route acceptance has zero FAIL,
native DRC is 0/0/0, and the layout-seal witness is valid. The rejected earlier
candidate remains quarantined history and is not release authority.

ADR-0006 allows design progression from a fresh exact-code public catalog screen while
keeping the logged-in JLCPCB allocation/economics workflow mandatory for order
readiness. The promoted route, Gerbers, BOM, CPL, drill files, source and review
evidence are now sealed as a hash-bound **design** release. Its included order
response is blank and its order receipt is incomplete, so it is not an
order-authorizing payload.

The 2026-09-03 public-catalog screen passes all 22 exact codes at the build-10
quantity floor. That public LCSC result is only a negative filter;
authenticated JLCPCB assembly allocation and order economics remain unproven
until the provider response/receipt workflow completes.
