# D15 private 3313A source preflight — generation stopped

The only prepared candidate is the ignored private copy
`06_build/prototype_board_diagnostic/current-ti-4l-3313a-preflight-20260925/`
under the Crow project. Its `.kicad_pcb`, `.kicad_pro` and `.kicad_dru` are
still byte-for-byte the frozen **7628G reference**. They are **not** generated
3313A outputs. No board/rule generation, routing, fabrication export or stock
check has run. The accepted [D15](../../decisions/0015-private-4l-3313a-unrouted-screen.md)
requires independent hash-bound preflight before that one allowed generation.

Review the exact [preflight manifest](preflight_manifest.json) and
[four-file source diff](source_diff.patch). Only copied
`03_src/floorplan.yaml`, `03_src/rules/nets.yaml`, `03_src/rules/rf.yaml` and
`03_src/rules/route_fab_overrides.txt` differ from the frozen private project.
The floorplan adds exactly one F.Cu permissive area
`usb_pair_xu_launch=[215.3,95.0,217.1,95.8]`; the exact DP/DN pair class
sets 0.180-mm width and 0.100-mm gap, and only the scoped DP/DN clearance
exception applies inside that area. Generic 0.150-mm clearance to foreign
objects remains. The RF copy labels the JLC
3313A result as an unqualified research hypothesis. Native reference boxes
for U_XU.59/.60 are enclosed and 58/61 lie outside the area, as recorded in
the manifest. Terra's [disposable KiCad precedence control](../2026-09-25-d15-pair-clearance-review-terra.md)
provides the required generic-versus-exact-pair and foreign-net check.

Independent preflight, from the worktree root, should run the read-only
manifest verifier and the hash-pinned baseline parity probe:

```sh
/usr/bin/python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-d15-preflight-sol/verify_preflight.py
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-expanded-native-parity-probe/replay.py
```

The reviewer must inspect the source diff, synthetic control, JLC packet and
every manifest hash, then sign a separate exact preflight receipt. The
verifier and these commands do **not** generate a 3313A board. Stop on any
drift or unexpected source change. This packet carries no P1/P2/P3/FULL,
route, assembly, fabrication, release or order credit.

Author replay of both commands passed on 2026-09-25: the content verifier
printed `PREFLIGHT_CONTENT_CHECK_PASS`; the frozen-board parity probe reported
KiCad 10.0.4, zero violations, 499 unconnected items and zero *performed*
schematic-parity issues. This author replay is not the independent signature.
