# Exact TI expanded-board native schematic parity

**Research diagnostic only.** The expanded locked private board did not include
the exact prototype schematic in its KiCad project copy, so its earlier DRC
run could not execute KiCad schematic parity. [The replay](replay.py) binds
the board, effective rules, footprint library table and custom libraries to
their exact hashes, verifies the `PROTOTYPE_ONLY` receipt plus exact circuit
and netlist hashes, and pairs the board with that prototype schematic in a
fresh temporary KiCad project, and runs KiCad 10.0.4 DRC with schematic parity.
It leaves the source board and canonical project unchanged.

The native result is **0 DRC violations, 499 unconnected items, and 0 schematic
parity issues**. Unlike the earlier empty parity list, this run explicitly
reported `Found 0 schematic parity issues` after loading the schematic. The
separate 569/569 count and 799-identity pin-map checks remain documented in
the [expanded candidate packet](../2026-09-25-ti-expanded-locked-p1-sol/README.md).
The board is still unrouted, P1 is incomplete, the TI ESD selection remains
`prototype_only`, and no connector, release, fabrication or order credit follows.

From the repository root, run:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-expanded-native-parity-probe/replay.py
```
