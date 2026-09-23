# Crow first native block-floorplan trial

Status: generated diagnostic candidate; placement NOT accepted.

The accepted schematic (CJ `f4097cb0…`) now produces a native 568-component board using the shared generator's independently reviewed exact-part pad-alias fix (`f45f634b`). The runtime attempt `crow-p1-floorplan-20260923-8b6b938a768c499eab8b44415723b535` closed PASS for delivery only. The modular graph remains complete at 568/568 owned refs and 59/59 crossing nets. Its P1 row is WORK_RECORDED / engineering_acceptance NOT_EVALUATED; downstream READY delivery rows do not authorize P2 dispatch.

## Measured candidate

- Board SHA-256: `637e266594a8b89dc8ce93ed9dc38f2661dc250c8f593fcc2cd2a03c3be44d51`.
- Candidate floorplan SHA-256: `084063400a90dcaef9629ba8a98c3839d9ded6dbcb2431f551c2862fe5bc2bcd`.
- 568 components, 1,866 pads, 27 anchors: 16 hold capacitors and 11 connectors.
- Two eight-capacitor islands fit the proposed rectangles. Native drawn courtyard bounding boxes are 11.69 × 8.69 mm including line extent, leaving 0.41 mm neighbor gaps at the proposed 12.1 × 9.1 mm pitch. All capacitor pad-1 positions remain on the left at rotation zero.
- Remaining circuitry includes all 53 quiet-power support parts and all 64 ADC-reference parts; existence does not establish bypass, Kelvin, thermal, return-path or corridor acceptance.
- No mounting holes were generated.

## Failed checks and limits

Default-rule diagnostic KiCad DRC reports 443 violations and 499 unconnected items. It is not the prepared-board project gate: selected process rules must be applied before interpreting clearance, annular and via-size thresholds. Real copper shorts remain failures regardless of that qualification. The report includes 32 shorting items; independent source/geometry investigation is required before the next candidate.

The first producer invocation failed because moving the output outside `04_kicad` changed KIPRJMOD model resolution. The next exposed the documented USB pin aliases not being consumed by the old generator. Subsequent scratch alias-normalized experiments were diagnostic; the final saved candidate uses the exact accepted native netlist and adopted generator. Every claim above refers to that final candidate.

Native candidate files and the closed runtime receipt are retained under `06_build/modular/` and `06_build/task_runs/`. The saved board's model URIs require reopening exact bytes under the project's `04_kicad/` relative layout; the separate top preview is not complete model-coverage evidence.

The 19 connector physical targets remain open. Public CAD can support candidate geometry review but cannot establish exact fit, installed cable service, reaction or measured tolerances. CONNECTOR-FULL still blocks placement approval/routing and release under the current project contract. See `2026-09-23-placement-boundary-audit.md`.
