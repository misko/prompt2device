# Isolated XU DATA local-neck fabrication probe — 2026-09-25

**The 0.15-mm local neck passes this narrow geometry screen; return access and electrical qualification remain open.** This follows the [0.20-mm native clearance stop](../2026-09-25-ti-timing-route-return-sol/README.md) and the [public XMOS/JLC fabrication boundary](../2026-09-25-xu316-tq128-tdm-fanout-fabrication-terra.md). It is a scratch rule experiment on the exact coupled-placement board SHA-256 `53e6fb7809910946c36053e7ceeb77e7fc866456ff77775ed4c59b3e49278555`, with no Crow source, canonical board, USB rule, or P1/P2 release change.

`build_probe.py` places one 0.15-mm F.Cu segment on TDM_DATA_1V8 from U_XU.107 `(200.8375,97.6)` to the west mouth `(199.805,97.6)`. Its length is **1.0325 mm**, below the explicitly diagnostic 1.05-mm bound; that bound is not an XMOS timing allowance. The complete copper-stroke bounding rectangle `[199.73,97.525,200.9125,97.675]` is strictly within the named local rule area `[199.7,97.49,200.95,97.71]`. The scratch project retains the board setup **0.20-mm minimum track width** and **0.20-mm Default clearance**. Its only custom rule condition names this DATA net inside this area and overrides track-width minimum to 0.15 mm. The independent full-stroke check closes any gap between KiCad's `insideArea` match behavior and the intended exception scope. The rule changes no clearance or USB setting.

Native `kicad-cli pcb drc --refill-zones` reports **711→712** violations on baseline→local-neck board, with **499→499** unconnected items. The only new local item is the expected dangling end of an intentionally isolated stub. There is no new `track_width` or `clearance` item on the neck. The filled In1.Cu GND polygon covers the **entire stroke bounding rectangle** exactly: subtracting the filled polygon leaves zero area and zero outlines. Both ends lie in the same main filled polygon. The committed board stores the zone unfilled for byte-stable reproduction; the script fills it natively in memory and the comparative DRC refills both boards in temporary copies.

The nearest existing GND F.Cu-to-In1.Cu via or plated pad to U_XU.107 is the GND via at `(202.7,58.4)`, **39.2442 mm** from the pad. No local return transition has been established. No four-net route, source/receiver timing, neck electrical allowance, crystal-loop impact, USB pair/ESD return, or assembly-silk recovery is proved. A full route needs separately bounded launches, local GND transitions, actual timing and return checks, and the same strict shape/length scope before any source rule could be considered.

Reproduce from repository root:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-timing-data-neck-fab-probe-sol/build_probe.py
```

The script emits deterministic `local_neck.kicad_pcb` (SHA-256 `d2aea41931ffb0fff9e5c3cce46121d1e1a8379ce56fafaba749eb75e5076237`), `local_neck.kicad_dru`, and `result.json`; the scratch `.kicad_pro` is pinned in the packet.
