# Verification journal

## 2026-09-08 15:10 UTC — iterate 1: standalone entry-point investigation

- did: Root independently copied the sealed pod archive into temporary
  directories, reopened both its flat and nested native board copies, and
  replotted the nested project with the actual export settings. The root's
  scope here is pod working documentation and diagnostic evidence only; no
  pod source, generated current board, release, or shared backend was edited.
- result: All 223 sealed payload hashes match, required membership is 37/37,
  design freshness passes, and realized paths pass 22/22. The flat convenience
  copy returns seven missing-library warnings; the existing nested project
  under `source/project/04_kicad` returns native DRC 0/0/0 without modification.
  Its nine Gerbers and two drills match 11/11 after excluding dated headers
  only. A separate one-coordinate Edge.Cuts mutation returns 10/11 and exit 1.
  Board SHA remains `a932200e0976418383fae0c131dfe2a5768c00ef261b611762ccd3507f05ca8f`.
- correction: The initial user-facing claim that the whole archive required
  library repair was too broad; the complete runnable project was already
  packaged. The root inspected the existing policy resolver and used its
  nested-project entry point, not a new waiver or checker change. The flat
  copy's warning remains real and the order README lacks opening instructions.
- next: Use the packaged native project and retain the dated
  `research/2026-09-08-standalone-release-entrypoint.md` evidence. Clarify the
  entry point in any future documentation successor; do not rewrite the sealed
  archive. Public stock remains the September 3 observation, not allocation.
  Both-child/main admission and all order/physical holds remain separate.

## 2026-09-08 15:14 UTC — finish: evidence preservation and working beacon

- did: Retained raw diagnostic captures under
  `06_build/verification/standalone-release-recheck-20260908-a17ede02/` and
  refreshed the pod and parent working beacons. No source/seal commit was
  made while the carrier author owns the fixed-HEAD source task.
- result: A final independent two-way membership/hash check passed223/223;
  all three live/flat/nested board copies have the same recorded SHA. Both
  beacons pass1/1 and authored whitespace passes. The first pod beacon check
  rejected a `Z`-suffixed time because this reader accepts local timestamps;
  the corrected frame records08:14 local time, not an altered gate. Pod
  source/current-board/release and shared backend Git diffs remain empty.
- next: Preserve the verified nested entry point and the real flat-copy
  caveat. Continue carrier completion; no new release, order, main push,
  allocation or physical readiness is asserted by this documentation pass.
