# Isolated coarse-board P1 native preflight — 2026-09-24

**Scope and result: failed P1-class preflight; not P1 acceptance or a task dispatch.** This read-only check used `/tmp/crow-usb-coarse-sol/projects/crow-usb-carrier-v1/04_kicad/crow_carrier.kicad_pcb`, SHA-256 `18e55f44d5c1a8f7a7dd050e12ca451f6e08932b8c79893a0ad74e3b18be861b` before and after the checks. `kicad-cli pcb drc --severity-all --refill-zones --format json` did not save the board; raw output is `/tmp/crow-p1-native-preflight.InWK16/drc_refill.json`.

`placement_drc_check.py` classified all **245/245** native DRC violations as blocking `clearance` findings, with **499** unrouted connections and **0** KiCad schematic-parity rows. The zero parity count is not a source-to-board acceptance: this isolated tree has no `.kicad_sch` or `circuit.json` beside the board. A supplemental `pin_map_check.py` run against the workspace's external ADC65 circuit reported `79` multi-pin refs and `799` physical identities passing, but that circuit is not hash-bound to this board and supplies no acceptance evidence.

The clearance failures are predominantly package-internal and via-to-pad: `U_XU` accounts for 121 pad pairs at 0.150 mm versus 0.200 mm; every `U_ISO1` through `U_ISO8` accounts for 12 package-pad pairs plus one GND-via conflict each; ESD packages also contribute. The first failures include `U_ISO5.4 [ISO5P]` to a GND via, 0.100 mm actual against 0.200 mm required, and `U_ISO8` internal pads at 0.100/0.150 mm. These are native board-rule/package defects, not P2 relocation results.

The saved board has 569 footprints, 429 nets, 14 tracks, and one GND zone assigned to `In1.Cu`; `GetFilledPolysList(In1.Cu).OutlineCount()` is **0**. Therefore the saved board has no filled reference-plane witness. Refilled DRC does not turn that saved-state absence into P1 return evidence.

`model_coverage_check.py` resolved **569/569** fitted 3D models. The stronger model-registration and connector-orientation gates cannot grade this copy: it lacks `03_src/rules/model_registration.yaml`; the first reports `P-MODEL-REG N-A`, and the latter reports that it requires the board, model-registration YAML, and floorplan. No connector-mouth approval can be inferred from these invocations.

`placement_gates.py --courtyard` found no same-side courtyard-pair collision across 569 assembled envelopes, but failed `P-OUT` for all ten edge connectors: `J1`–`J8`, `J_PWR` have courtyards at 0.00 mm inside the outline rather than the default 0.15 mm, and `J_USB`'s courtyard is 0.50 mm off-outline. This direct generic-outline result does not replace an approved connector-mouth exception or the connector FULL gate.

The failures above leave P1 unavailable: the board has clearance defects, no saved filled-zone witness, and no usable connector-orientation/model-registration evidence. No source, board, checker, or task state was changed.
