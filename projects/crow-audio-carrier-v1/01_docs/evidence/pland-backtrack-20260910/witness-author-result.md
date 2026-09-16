# P-LAND witness author handback — incomplete, cap exhausted

No finite-witness production patch was produced. The checker is restored to
exact original SHA256 `cb0d0cf6cb593b5f231fa372920e7dc6adf10bce95c0d734fac0900d3fd3ddf3`.
The only live implementation WIP is the 73-line addition to
`tests/t1_escape_tier.py`; root will preserve and adjudicate/revert it.

## Verified inputs

- Envelope SHA256 `30eafbd595d8ee283ae2303a2047a0f8805d47eefcd70a7d877f9c7d670a0630`.
- 483/483 source preimages, including 470 frozen inputs, matched before edits.
- Archive `887c61662cbdc291a68c03bdbfb4569d5c93eb830989f31393338c14a128b3db`:
  161/161 member SHA/size matches; no links or traversal members.
- Captured post-restore packet check `003_packet_verify_exact_source` is
  636/636, rc0, 2026-09-10T21:14:19Z. Full argv/start/rc/duration/source hash
  metadata and output are in this private directory.

## Actual attempt record

1. Sampling disclosure edit changed `MAX_LAUNCH_PTS` 25→37, accidentally
   changing `sqrt(max_pts)` from five to six intervals and the retained sample
   set. It was restored. The uninstrumented mixed-source t1 log records
   U_MCU.46 0.308 rather than the retained 0.300; it is not a baseline/GREEN.
2. Captured full suite `004_public_path_red_cb0d0` (rc1, 52.36s) added the
   first fixture, whose `A.Type` condition is unsupported by the old parser.
   Its actual result is 0 graded / 4 floorless, therefore it is not behavioral
   RED evidence.
3. Captured `005_public_path_red_cb0d0_fixed_fixture` (rc1, 0.415s) changed
   the fixture condition but its actual stdout still reports 0 graded / 4 no
   declared floor. It is also not behavioral RED evidence. The earlier claim
   that it established RED is withdrawn.

There is no valid maintained RED, GREEN, native fixture result, full t1
result, t1_gate_contract result, or t1_contracts result to claim.

## WIP inventory and limits

The complete current diff is the 73 added test lines (`git diff --numstat`:
73/0). The private scratch fixture directories created by the tests used the
`tmpdir` mechanism and are available only if not removed by its cleanup; no
fixture is represented as retained evidence beyond the captured stdout. The
diagnostic prototype and historical evidence remain untouched. No board,
rules, source geometry, checkpoint, model, routing, review, release, or source
checker change remains.

The intended architecture and seven guards remain open: native final
start/shape/layer checks, full fail-closed supported AST, A/B/order semantics,
native effective/local clearance bounds and absolute minima, truthful
witness/no-witness output, and governed documentation/test migration. Frozen
checkpoints remain stale; canonical restart is still owed after a future
accepted source change.

## Administrative closure

Interim snapshots are preserved unchanged as
`result.interim-20260910T211623Z.md` and
`project-result.interim-20260910T211623Z.md`.

`pcb_flow handoff` captured as `006_compact_handoff` rc0/1.167s and
`pcb_flow validate` as `007_compact_handoff_validate` rc0/1.117s. STATUS and
the placement journal were appended with the actual cap-exhausted state. No
author subprocess remains; all author writes cease with this report.
