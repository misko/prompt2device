# Island reservation source-proposal review (read-only)

**Disposition: ACCEPTABLE AS A SOURCE PROPOSAL.** It is correctly limited to a
future source change. It provides neither a new native board nor any P1, routing,
or physical-connector acceptance.

## Evidence-subject correction

This supersedes the earlier evidence binding while preserving its static-source
conclusion. The proposal diff is unchanged at SHA-256
`085a0f47dea38f0305d643238e8e7bba1a174379e0ee01c88e4701b98f40a543`.
The author report reviewed here is SHA-256
`2307951251fd30f86124fdc4c4c85ab77a9fe51b0692222b34e1f1c2b3ad8058` and
its sole native-evidence subject is the second repaired-trial board
`/tmp/crow-p1-repaired-trial-20260923/04_kicad/crow_carrier.kicad_pcb`, SHA-256
`37b455203fcdae0c20880a94b17a4bcfb61103fa2b8b9df9ecf095c9c97aa519`.
The first candidate SHA `637e…` is not accepted as repair evidence.

The reviewed base is the current
`03_src/floorplan.yaml` SHA-256
`62be425f350d8d0c9bd33834f99d3d1827e5f190480e4bb75ad95a70830e53af`.
`git apply --check` passes. Applying the diff synthetically parses as YAML and
reproduces the stated proposed SHA-256
`26686cd23dd26e945d855c49f6413795519a4ab1b98f191bea9b3aa8fa4106b8`.

## Static checks

* The proposal has 27 anchors: all 16 C_HOLD entries and 11 connectors
  (J1–J8, J_PWR, J_USB, J_JTAG), plus 46 seeds.
* The left bank contains exactly C_HOLD1–8; the right contains exactly
  C_HOLD9–16. No non-can anchor lies in either island.
* The anchors preserve the specified two-row can centers, rotation zero,
  12.10 mm column pitch and 9.10 mm row pitch. With the retained measured
  11.69 x 8.69 mm courtyards, this is consistent with the recorded
  0.41 mm nearest courtyard gaps and bank bounds.
* The three forbid rectangles are exact, contiguous 50 mm + 2 mm + 50 mm
  x 24 mm reservations. The generator checks every floating footprint's
  centered bounding-box proxy against each rectangle plus 0.25 mm margin;
  anchored/kept footprints are bypasses, as the proposal says.
* The diff does not remove or alter the existing root thermal-via field
  configuration (nine fields remain) or model overrides (five patterns remain).
  It also removes all 16 cans from the broad quiet-power pattern and assigns
  every can to exactly one bank pattern.
* The corrected report's displacement census is accurately scoped to the
  second board: 23 support courtyards intersect the left bank and one the
  right. Four ADC courtyards intersect the right bank; `U_ADC_READY_BAD` is a
  fifth *footprint bounding-box* intersection, not a courtyard finding.
  No ADC box intersects the left bank.

## Limits retained correctly

The supporting memo is candid that the exclusions reserve only floating-part
legalizer search space. They do not make a KiCad keepout, prove courtyard/body
clearance for every footprint, establish a copper corridor, prove analog/power
adjacency, or establish connector mating/service clearance. Its capacity figures
are presented as lower-bound packing loads, not a proof; its count distinction
for the right-bank ADC intrusion is explicit. Six ADC footprints lack F.CrtYd
on this stale board; I independently observed zero courtyard outlines for
`U_ADC_A`, `U_ADC_B`, `U_ADC_DIGITAL_BAD`, `U_ADC_PWR_BAD`, `U_ADC_READY`, and
`U_ADC_READY_BAD`. Commit `7193695a` contains the source courtyard repair, so
regenerated native evidence remains owed. The 120-ring setting has only a
59.5 mm search radius, so it remains a bounded search parameter, not capacity
evidence.

The proposal does not imply a generation rerun, P1 budget reset, route result,
or acceptance claim. Its requested later checks are appropriate.

## Required source-coherence follow-up

J_USB's proposed anchor remains `[230, 23.675, 180]`, inherited from the
rejected candidate. Because its connector footprint is being replaced
separately, retain this coordinate only as a provisional source intent. The
coherent updated source review must reassess the new USB footprint's board-edge
datum, pad/NPTH clearance, mating direction and physical service envelope before
treating that anchor as fixed. The same later check must retain the existing
connector FULL hold; this reservation proposal cannot waive it.
