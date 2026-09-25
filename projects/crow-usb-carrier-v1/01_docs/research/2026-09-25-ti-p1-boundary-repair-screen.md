# TI board P1 boundary repair screen — 2026-09-25 UTC

**Research only.** Every variant below is bound to the same isolated, unrouted
TI diagnostic board (`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`)
and the 59-net source candidate described in
`2026-09-25-ti-p1-coarse-contract-screen-sol.md`. No variant changes the
canonical P1 source, board, placement or routing, and none earns P1 credit.

| Variant | Contract SHA-256 | Checker result | Next exposed defect |
| --- | --- | --- | --- |
| `2026-09-25-ti-p1-adc-timing-virtual-terra.json` | `6f613de0cebd6219bf6e0cf4c6dae3a8f0560e5dee1e5a87ae1ba9c9ab62eecf` | `INCOMPLETE`, zero global errors | `U_ADC_A.22` accepts a typed east-region virtual face; `U_ADC_A.23` then needs its own virtual face. |
| `2026-09-25-ti-p1-adc-analog-virtual-terra.json` | `c1dff26664c530e879a02a4f078f5b10d6344a4c81213747b402500ccd3baf39` | `INCOMPLETE`, zero global errors | `C_ADC_AC1N1.2` accepts a typed south-region virtual face; `C_ADC_AC1P1.2` is then nonlocal. Timing next stops at `U_XU.93`. |
| `2026-09-25-ti-p1-power-gnd-variant-root.json` | `fdda3d8e54775e4436cf762581c7850ae9cb07c953298617cd94ce60924d27a8` | `INCOMPLETE`, zero global errors | A local north-region GND virtual face at `C_ADC_A_AVDD_10U.2` avoids overlap with `adc_common`; the next power witness `C_CORE_FF.1` is nonlocal. |
| `2026-09-25-ti-p1-adc-timing-all-virtual-terra.json` | `ae05db8f138bb7fd3c68cc67f0d053ff619debfa845d9f32ed42b3c5a6672193` | `INCOMPLETE`, zero global errors | All 14 timing witnesses have typed P2 virtual faces; `U_ADC_A.22` now fails because its east block face does not contact the west edge of the old `adc_common` reservation. |

Each variant has a same-stem `-evaluation-*.json` checker receipt. The virtual
faces bind a named native pad, source block, region face, layer, reservation and
explicit `P2_REQUIRED` pad-to-face obligation. They are source reservations,
not copper or proof of a completed return path. For the GND trial, the initial
east-face rectangle overlapped the named ADC timing allocation and failed
globally. The tested north-face reservation was disjoint and advanced the
checker without hiding that overlap.

The all-timing variant exposes a group-level boundary error: `adc_reference`
ends at x=145, while the existing `adc_common` reservation starts at x=140.
The checker requires the virtual block face to contact the assigned
reservation boundary. A reworked, adjoining transition reservation or a
typed integration handoff is needed; converting pad witnesses alone cannot
make this allocation coherent.

The next source task is to enumerate **all** movable endpoints in the four
allocation groups and assign local virtual faces or justified fixed-access
handoffs as a single coherent geometry. Running this checker one offending
pad at a time is useful for diagnosis but will not advance the release until
the whole allocation and board-level separation are modeled. On the current
board, the checker still rejects the fixed `J_USB.4` bridge; XMOS service
capacity and return are incomplete. The board also has 499 native unconnected
items, no signal tracks, unfilled saved zones, and ten P-OUT connector cases.

The power group has a tractable ownership split. Native pad-bbox comparison
against the pinned floorplan puts **nine of its ten named pads inside their
declared source regions**; `J1.10` is the exception, because the fixed RJ45
connector sits north of `analog_ch1`. The power failures are therefore mostly
long witness rectangles from a movable pad to a distant reservation, not a
missing native pad. A coherent repair must replace those rectangles with
local virtual faces and independently reserved inter-region paths, while
`J1.10` needs the fixed connector edge-owner treatment. Merely converting one
GND witness exposed `C_CORE_FF.1` as the next nonlocal bridge.

No P1 attempt was admitted. Do not use these diagnostic evaluations as a
routing, DRC, connector FULL, or release receipt.
