# D15 single private 3313A unrouted generation — FAILED_RESEARCH

The independent [preflight review](../2026-09-25-d15-independent-preflight-review-terra.md)
signed PASS before generation. One private board generation, rule generation,
and TMUX POFV pass were run in the ignored
`06_build/prototype_board_diagnostic/current-ti-4l-3313a-preflight-20260925`
copy. An initial command rejected a wrongly rooted netlist path before writing
the board; the frozen board hash was rechecked, then the single actual
generation ran. There was no further generation or candidate retry.

The [native object diff](object_diff.json), reproducible with [audit.py](audit.py),
finds no footprint/pad identity or pose delta, no saved track/via or existing
zone/outline delta, and only the D15 `usb_pair_xu_launch` rule area added.
There are 569 electrical footprints, six holes, 14 original GND vias, nine
rule areas, one GND zone, and no saved zone fill. KiCad's raw native pad count
is 1,872 on non-hole footprints in **both** boards; this is a different
denominator from D15's stated 1,810 electrical-pad figure and is not used as
an unsupported count claim here.

Count parity is 569/569 and pin-map parity covers 799 physical identities.
The [disposable refilled native DRC report](../../06_build/prototype_board_diagnostic/current-ti-4l-3313a-preflight-20260925/drc_disposable_refill.json)
shows zero violations, 499 unconnected items and zero *performed*
schematic-parity issues. The saved candidate remains unfilled.

[V-PROCESS](../../06_build/prototype_board_diagnostic/current-ti-4l-3313a-preflight-20260925/via_process.json)
graded all 14 vias but returned `TMUX-DRU: foreign clearance/via/hole
constraint`. The unchanged checker treats the D15-authorized exact DP/DN
scoped-clearance rule as a foreign clearance constraint. This is a gate
failure, so the [receipt](receipt.json) is `FAILED_RESEARCH`; no rule,
checker, source, or board was modified to make it pass. Terra is independently
reviewing the boundary. No P1/P2/P3/P5, connector FULL, route, fabrication,
assembly, release, or order credit follows.

From the worktree root, the read-only receipt check is:

```sh
/usr/bin/python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-d15-postgen-sol/verify_postgen.py
```
