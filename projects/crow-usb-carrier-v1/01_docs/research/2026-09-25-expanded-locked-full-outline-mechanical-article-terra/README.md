# Expanded-locked full-outline connector mechanical article

**RESEARCH-ONLY / UNPOWERED / NO FABRICATION PAYLOAD / NO CONNECTOR FULL CREDIT.**

This packet prepares a reproducible *measurement subject*, not a manufacturable
PCB. It binds the ignored private expanded-locked board
`06_build/prototype_board_diagnostic/current-ti-mounting-expanded-locked-20260925/04_kicad/crow_carrier.kicad_pcb`
at SHA-256 `fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16`.
It neither copies that PCB nor creates Gerber, drill, pick-and-place, BOM,
assembly, fabrication, or order input. The only generated output is
[`native_geometry.json`](native_geometry.json), a coordinate and nominal
courtyard-screen manifest.

The bound board has a 230 by 130 mm outline (`x=10..240`, `y=20..150`), four
copper layers, a 1.63 mm KiCad thickness target, eleven native connector
instances, and six existing `MountingHole_3.2mm_M3` footprints. The extractor
requires every connector's native library identity and pose, the outline,
layer count, thickness target, and every mounting-hole pose. It also records
the three nearest nonconnector F.CrtYd bounding boxes for each connector.
Those boxes are nominal interference screens only: they do not represent
assembled bodies, mates, cables, fasteners, standoffs, fixture clamps,
tolerances, force paths, or enclosure geometry.

Run from the repository root:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-expanded-locked-full-outline-mechanical-article-terra/verify_packet.py
```

The verifier regenerates the JSON manifest and checks the saved private DRC
report for zero violations and 499 unconnected items. It deliberately makes
no schematic-parity claim: the private DRC log says the schematic netlist was
unavailable for parity tests.

## Possible observations after separate authorization

If a later electrical/mechanical owner explicitly authorizes an **unpowered**
article manufactured from an accepted, hash-bound revision with this same full
field, the article could record formative measurements and negative findings
for all eleven connectors under the existing
[connector physical qualification plan](../2026-09-22-connector-physical-qualification-plan.md):

- exact connector seating, rotation, visible solder/edge damage, and
  immediate connector-to-connector interference;
- normal-service and bench-service hand/grip/latch access with the plan's
  simultaneous population groups installed;
- board-edge/mating-plane and shell/stake registration observations;
- cable exit direction and initial neighbor interference; and
- fixture-reaction observations only after a restraint drawing is approved.

The [19-target measurement matrix](measurement_matrix.md) states the precise
observation and non-credit boundary for each target family. It can close
**none** of the 19 `connector_full` targets as currently bound.
The observations would need the actual board/coupon, connector/mate/cable lots,
process stack, enclosure configuration, calibrated instruments, and approved
limits. A finding from this subject cannot establish USB electrical operation,
system ESD behavior, D13 transient coordination, routing, P1/P2/P3, release,
or order readiness.

## Fixture and acceptance data still owed

| Needed before an article can be interpreted | Why |
| --- | --- |
| Explicit narrow fabrication/test-article authorization | D13 and D14 permit no fabrication or order; the authorization must keep the article unpowered and exclude release/FULL credit. |
| Accepted exact board hash, controlled four-layer stackup, finished thickness and routed-edge/slot tolerances | A KiCad 1.63 mm target is not a finished board/process specification. |
| Exact mates, cable assemblies, connector lots, assembly method/profile | The plan requires part- and lot-bound observations. |
| Enclosure, cable exits, straight runs, bends, strain relief and far-end supports | Service and cable targets are installed-state predicates. |
| M3 hardware and restraint drawing with support surfaces and allowed clamp/standoff locations | Reaction must pass through PCB mounting features, never a connector, cable, solder joint, component, or trace. |
| Approved loads, cycle count, deflection/registration limits and measurement uncertainty | The plan intentionally has no invented numerical PASS limits. |

## Authority boundary

D14 allows an ignored, private **unrouted geometry diagnostic** only and says
that no board from its producer may be fabrication input. D13 retains
`USB-ESD-selection-transient` as an open `DESIGN_CLEAN` blocker and grants no
fabrication, assembly, order, release, or electrical-survival claim. Therefore
this packet stops at a reproducible measurement definition. Copying the D14
subject into a coupon directory, exporting manufacturing files, or treating
this geometry manifest as an article authorization would violate that boundary.

Relevant sources: [D13](../../decisions/0013-usb-esd-prototype-boundary.md),
[D14](../../decisions/0014-private-native-diagnostic.md), the
[full-outline feasibility audit](../2026-09-25-full-outline-connector-coupon-feasibility-terra.md),
and the earlier [connector fit prototype](../2026-09-24-connector-fit-prototype.md).
