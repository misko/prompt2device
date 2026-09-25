# 3313A controlled USB pair, unadopted source packet

**Status: research only, unadopted.** This packet binds the exact expanded-locked private board/source to a four-file 3313A stack, USB class, route wave and RF *hypothesis* [patch](source_diff.patch), SHA-256 `707d8b94075190bf601aba410738b5fbefbd7036ca539ff967c9ae1fd90f7d82`. It does not change canonical Crow source or board, supersede D15's failed historical receipt, admit D18 P1/P2, route, fabricate or order.

Run from the repository root:

```sh
/usr/bin/python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-unadopted-3313a-controlled-pair-sol/replay.py
/usr/bin/python3 -m unittest skills/jlcpcb-fab/scripts/tests/test_via_pair_scoped_clearance.py
```

The replay is read-only for the repository and writes disposable KiCad boards under `/tmp`; by default it prints JSON only. Its optional `--write-result NEW_PATH` refuses an existing file. The final author [native replay capture](native-replay-full-sidecar-20260925.json), SHA-256 `ec9cfedff7b1c6d408e71355c53f87686ed3d1150120d515467ead1e15a589fd`, records KiCad CLI/pcbnew 10.0.4, exact input/proposal/replay hashes, generated rule hash and the DRC coupon hashes. Native board UUIDs make byte hashes of new scratch boards nonreproducible between runs; compare rule identity and clearance assertions, and preserve captures unchanged. The earlier [six-control capture](native-replay-20260925.json) remains historical.

The final capture is `PASS`: F.Cu DP/DN at 0.100 mm has no clearance violation; F.Cu DP/DN at 0.099 mm fails under the 0.100-mm exact-pair rule. F.Cu DP/FOREIGN at 0.140 mm and DP/DN at 0.140 mm on In1.Cu, In2.Cu and B.Cu fail at 0.150 mm with the **full generated** project/rule sidecars. The F.Cu pair pass/fail checks also use those full sidecars. Minimal DRU controls also preserve foreign and B.Cu isolation. Generator negatives reject a widened selector, second pair and B.Cu declaration; the independent process guard re-derives the four exact DRU rules. The focused unit suite passed 9 tests.

Terra independently reran the exact proposal and replay and approved this narrow research/process capability. Its [independent native capture](native-replay-full-sidecar-independent-terra.json), SHA-256 `2ef86d1c3b69c4e00e9013d9588bd0bc048ef33983a8936f8b27d0bd79358819`, has the same clearance outcomes; scratch board hashes differ because KiCad regenerates UUIDs.

The [engineering disposition](../2026-09-25-unadopted-3313a-usb-pair-domain-sol.md) separates this rule feasibility from the still missing full four-leaf merge, ESD tap, XU transition, In1.Cu return, stack/order, connector and ESD evidence. Independent review is required before any source adoption or new Crow native experiment.
