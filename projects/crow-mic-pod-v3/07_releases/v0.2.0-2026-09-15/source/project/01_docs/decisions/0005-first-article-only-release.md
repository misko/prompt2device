# ADR-0005 — release only as a non-orderable first-article candidate

Status: accepted
Date: 2026-09-01

## Decision

Every generated or bundled artifact from this design state is labeled
`FIRST-ARTICLE-ONLY / DO NOT ORDER`. The project may retain reviewable KiCad,
fabrication and release-candidate artifacts while connector operations,
sourcing, cable qualification, enclosure integration and bench evidence remain
open; none may be represented as a production release.

## Why

The schematic can be made internally coherent before the physical cable,
capsule, weatherproof enclosure and assembly process have been qualified.
Preserving that useful design state is honest only if unknowns remain visible
and the order boundary fails closed.

## Exit criteria

Close every `OWED`/`INCOMPLETE` row in `01_docs/STATUS.md`, pass the full governed
conductor, complete human schematic/PCB/fab reviews, seal from immutable source,
then deliberately revise this ADR and status. A clean ERC/DRC alone is insufficient.
