# TMUX4827 B2 POFV source/native-fixture review — PASS

**Review scope:** implementation commit `28954702cbbe9c45491d3332667475157030b361` in
`/tmp/crow-tmux-profile-20260923`; source/schema and synthetic native-fixture
review only.  This is advisory source-code review, not P1 generation or PCB
runtime admission.

## Verdict

PASS within the requested scope.  I found no actionable source or native-test
defect in the final commit.

## What is bound and checked

* `assembly.yaml` permits exactly one named profile with the exact ID, eight
  ordered `U_ISO1..U_ISO8` references, pad `5`, `GND`, advanced four-layer
  tier, ENIG, Type-VII filled/capped process, eight-site count, and the
  qualified `0.35/0.20` geometry (`0.075` annulus; `0.25` mask/paste; `0.10`
  B2-neighbor clearance).
* The contract rejects changed identities, dimensions, tier, coupon hash, and
  native-footprint hash.  It now also rejects source-floor changes: floorplan
  must retain `0.45` via diameter, `0.13` annulus, and `0.15` clearance; the
  generated project is independently checked for the two via floors.
* The board checker requires all eight live TMUX footprints and their exact
  nine-pad map, B2/5 GND land, exact co-located GND F.Cu-to-B.Cu via, fill and
  cap flags, and rejects missing/doubled/offset/extra protected `0.35/0.20`
  vias.  It also verifies each tiny producer-owned area against the live pad
  and rejects foreign vias that overlap it.
* The generated native DRU holds the ordinary `0.45/0.13` floor and narrow
  per-reference B2 overrides.  It limits the 0.10-mm relation to B2 and its
  four orthogonal same-footprint neighbors in both operand orders.  The
  checker requires every exact generated rule once at a line start and rejects
  foreign clearance/via/hole constraints.
* Both rebuild conductors invoke the producer after every generic-rule pass,
  including immediately before their final route-acceptance native DRC.

## Independent evidence

* `/usr/bin/python3 -m unittest tests.t1_tmux4827_pofv` — **7 tests, OK**.
  This performs native `kicad-cli pcb drc`: B2 passes only with its local
  override; removing it exposes ordinary via/annulus failures; a misplaced
  ordinary `0.35/0.20` via fails the ordinary rule.  It also covers wrong
  net/ref/pad, diameter/drill, missing/fill/cap/offset, neighbor, stale area,
  extra protected via, changed footprint/coupon, and foreign/global DRU
  constraints.
* `/usr/bin/python3 tests/t1_via_process.py` — **16 passed, 0 failed**
  (13 expected-failure mutations rejected).
* `git diff --check` for the reviewed commit — clean.

No product PCB/P1 generation, authority re-pin, source edit, or remote action
was performed by this review.  The test fixture establishes native rule
semantics, but it does not make a generated Crow board accepted; that remains
for the later board/runtime gate and the retained supplier acceptance process.
