# Crow upstream contract and model repairs

MEASURED on 2026-09-23; this is source repair after two rejected P1 trials,
not a new placement attempt or admission.

## USB source contracts

Reopened TI SLVSAC2G page 3 Figure 5-1/Table 5-1: TPD2EUSB30ADRTR DRT
pins 1/2 are independent ESD ports, pin 3 is ground. Added missing
`layout.route_topology` metadata to the existing dossier without changing
its revision, pins, limits or selected part. The dossier deviation register
records this incomplete-extraction correction. The owning endpoint predicate,
reopened on candidate `37b455203fcdae0c20880a94b17a4bcfb61103fa2b8b9df9ecf095c9c97aa519`,
now passes 1/1 row; saved diagnostic `06_build/modular/endpoint-topology-repaired.json`.
This does not prove a routed ESD return path.

SOL repaired shared critical-pair name recognition consistently in discovery
and declaration, covering `_DP/_DN` alongside `_P/_N` and `+/-`. It rejects
wrong stems, reversed polarity, duplicates, and a false no-critical declaration
when independent length-match rules require a pair. Fresh Terra code review
found no actionable defects. The current Crow declaration passes 1/1 pair
on the unchanged saved board, retaining F.Cu and no-via requirements.

Producer shared tests: 146/146 pass. Root broader T1 first found an obsolete
clean fixture whose no-critical declaration contradicted its own length-match
rule. SOL corrected that fixture and preserved the contradiction as a new
known-bad test. Root rerun: 10/10 pass, including 7 known-bad cases. No checker
bypass was restored to satisfy the old fixture.

The dossier edit correctly stales both canonical schematic reviews on
`parts_sha256`. Existing reviewed artifacts remain unchanged and historical;
PR-REVIEW is currently FAIL until an independent carryover review binds the
finished source-repair bundle. Do not silently refresh review hashes.

## Model identity repair

The complete SOL census covers all five authored override groups and the
73 unresolved model instances. It also identifies ten incorrect bodies hidden
inside the previous 495/568 file-resolution result: two old Cirrus QFN48 bodies
on current TI WQFN24 ADCs, and eight old DSG8 bodies on current YBH9 TMUX parts.
Removed those two override groups from authored floorplan. Their exact native
footprints provide no model fallback, so correct models remain owed. Do not
reuse the old candidate floorplan recipe without merging this source correction.

Restored `03_src/lib/3dmodels/kicad/R_0603_1608Metric.step` at the path already
referenced by the exact Yageo 0603 source footprint. This unmodified KiCad
package model comes from the installed KiCad 10 library, SHA-256
`1875571c326d0d9e96f36b4efeb8094068ef7619f0a449c781caf0b49c2e5861`.
The adjacent KiCad library license is retained. It is a generic package model,
not manufacturer-registered CAD. Nine instances consume that URI. Source file
resolution is repaired; assembled placement/orientation remains to be graded.

No PCB was regenerated. The projected file-resolution count would be
495 - 10 + 9 = 494/568, not a new measured native coverage result. File presence
alone cannot establish mechanical identity or correct registration.

## Process reassessment and next boundary

The accompanying corrected Terra memo reconciles the retained TMUX coupon
with current public JLC BGA/POFV guidance. The center via is a deliberate
0.35/0.20 proposal, not an accidental ordinary-via size. A narrow named
pad-specific process profile is supported as a documented engineering
inference; its implementation and native verification remain owed. Generic
board rules must not be broadly relaxed, and enlarging the center via fails
neighbor clearance. Actual supplier acceptance remains at its existing
order-time boundary; this review introduces no authenticated-JLC prerequisite.

DMQ and USB connector package/process gaps still require an evidenced repair
or disposition. Complete correct model/courtyard assets and enforce support
space around the capacitor islands before a reviewed campaign reassessment.
Physical CONNECTOR-FULL evidence remains owed under its existing gate.
Neither source repairs nor advisory reviews reset the consumed P1 budget or
admit P2, routing, a release or an order.
