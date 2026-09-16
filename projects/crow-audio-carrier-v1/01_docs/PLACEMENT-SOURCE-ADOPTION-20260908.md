# Root adoption of local placement source — 2026-09-08

Disposition: source correction adopted for further engineering, NOT accepted
PCB placement or routing. The source author relinquished its exclusive lease
before root verification or project writes. No producer, checkpoint retirement,
PCB save, routing, fabrication, release, tag or push occurred in this adoption.

Root fully read the final 347-line
[author handback](SOURCE-CORRECTION-20260908-local-placement.md), SHA256
`91c7d4494c1747d94b48643b63988fd8b23fcd2bb7004b16bf7de8e11189d1ec`.
The preceding in-progress report was not used as terminal authority. Baseline
HEAD was `6545d7d15bda7645fe9424723583f865afd521e9`.

## Independently measured adoption checks

- At 05:31:31.563400Z, root verified all 11 immutable packet members, the
  exact envelope, all 722 archive files / 97,764,814 bytes and all 30 evidence
  files / 1,901,714 bytes. Exactly 20 of 407 authority inputs changed: the
  floorplan and layout subtrees of 19 dossiers; the other 387 are identical.
  All 25 Git-delta paths were within the commissioned writer scope.
- Dossier identity, pins, ratings, datasheets and all non-layout fields remain
  exact. Footprints/models, native topology, board outline/layers/mounts,
  all 11 connector datums, zones and fab rules remain unchanged. All recorded
  generated subjects, prior reports and checkpoint bytes are preserved.
- At 05:31:31–05:31:32Z, root independently ran all 95 source tests: PASS,
  0.694 seconds unittest time, 0.887 seconds bounded-runtime time, rc0,
  120-second deadline and 10-second heartbeat. Existing PROPERTY_ENUM and
  ResourceWarning messages are retained, not suppressed or relabelled.
- At 05:32:14.354961Z, root manually expanded the repeat schema, without
  the board producer, and independently loaded 32 exact library footprints.
  All 299 poses, 920 pad objects and 868 numbered pin/net coordinates agree
  with the final source data. All 325 centre-span relationships were
  recomputed: no discrepancies or proposed-budget exceedances; 128 capacitors
  and 297 references covered, with J10/J11 fixed external datums. This local
  read-only diagnostic returned rc0 in 3.041 seconds; it was not a producer
  or a generated-board gate.
- Root inspected all four final source-only whole/analog/ADC/power views and
  the complete floorplan diff. The corrected digital support, inward-facing
  coupling/hold-cap terminals and local support clusters match the source.
  Fuse-caption uniqueness and MAIN's new location are regression checked.
  These diagnostic reference texts are not generated fabrication silkscreen.

Exact root scripts, outputs and final source snapshot are retained in
`06_build/verification/local-placement-root-20260908/`. Author evidence remains
under `06_build/tmp/local-placement-20260908/evidence/`, with inventory SHA256
`420a4dfaa19452f03c50f588c19030e067d285587b65748c6af1b8c485b70d3a`.
The initial interim archive-scope rc1 is preserved: its allowlist omitted the
legitimate modified LDO regression test. Root fully reviewed that adaptation;
the corrected interim and terminal audits pass. It was not a design defect.
M-BEACON passed over 2/2 carrier/parent beacons (neither claims a seal).
The authored working diff passed whitespace checking. The full staged diff
returned rc2 solely for preserved raw-evidence formatting: trailing space in
the stale-board report's `Board graded` line and a final blank line in the
initial interim scope output. These bytes are retained; no full-staged
whitespace PASS is claimed.

Final floorplan SHA256:
`f5a897ea3afac77b7ef1291ebc3220a01495c0921f6728a2f4dbf3ef73b41d58`.
Final official parts digest:
`74b185decaf546b1230474ee1692c82d4c4d8e52b9add00f67a49c3740967c33`.
Native semantic netlist remains
`b6da08f18cecc93d43eb7b5ccd87ccbca01ed3c97c450add1e75ad9d6c88d369`.

## Limits and next owner

INHERITED from the exact author assessment, not regraded by root as a board:
0.30 mm minimum courtyard-box gap, 0.59 mm foreign-copper/body-graphic-box
gap, 1.325 mm copper-edge gap; 351 reached proximity declarations; source
policy PASS=2 and deliberate rejection of the stale PCB. Source budgets are
engineering policy, not manufacturer numerical trace-length guarantees.
The 86 ground-pocket candidates use 0.15 mm stubs / 0.127 mm clearance,
not current GROUND 0.30 mm width / route 0.25 mm clearance. No ground/thermal
path, exact 3D body, generated silkscreen, DRC or route is accepted here.

The next fresh source owner must correct exact-net groups and class coverage,
power widths/ownership, fine-pitch width AND clearance, paired via-annulus
geometry, public stack/50-ohm digital intent and physical return planning.
Any power-pour decision must reconcile the existing adjacency consumer's
poured-net exclusion without silently losing local support ownership.
Batch those owning-source corrections before one new governed producer and
fresh schematic-review cycle. Never restamp old reviews or checkpoints.

The unchanged saved PCB is stale/unaccepted; the carrier has no sealed release.
TOP77-Q1–Q5/N1, 0.20 A first-power HOLD, physical/service, sourcing/allocation
and publication obligations remain. ADR-0007 allows prototype progress before
physical qualification; it does not authorize power, ordering or production.
No main push until both child releases and exact-base/head P-PUBLISH pass.
