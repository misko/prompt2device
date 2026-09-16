# Fresh mechanical native-interface admission result

Run `pland-native-owned-output-20260910T215831Z` executed exactly once from source commit `aac84f5b5c83c3324f919237391260a2f942adbd`.

## Launch (MEASURED)

Exact argv was `/usr/bin/python3 /tmp/pland-native-owned-output-20260910T215831Z/producer/execute.py /home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901 /tmp/pland-native-owned-output-20260910T215831Z`.
Start `2026-09-10T21:59:41.468561+00:00`, PID `2109688`, duration `0.4536894899792969s`, return code `1`, timeout `false`. Full stdout/stderr are in `admin/stdout.txt` and `admin/stderr.txt`.

Producer-owned `OUTPUT_DIRECTORY` was `/tmp/pland-native-owned-output-20260910T215831Z/native-interface-run-jp3a0oer`.

## Outcomes (MEASURED)

Fixture child PID 2109689 returned 0 and was reaped; checker SHA before/after was `cb0d0cf6cb593b5f231fa372920e7dc6adf10bce95c0d734fac0900d3fd3ddf3`. Census child PID 2109722 returned 0 and was reaped. The producer stopped at its first assertion in `execute.py:54`:

`AssertionError: (copper_pads, graded, floorless) != (5, 2, 3)`.

Actual base census was `copper_pads=5`, `graded=0`, `floorless=5`, `tracks=0`, `vias=0`, `pours=0`; all five floor rows had `old_declared_floor=null` and `rule=null`. No public checker, native DRC, hostile census, or parity assertion ran. Therefore expected X1.1/public and DRC claims are unresolved, and this is not an admission pass.

## Integrity and closure

The handoff envelope SHA256 is `776ef035b042ca141ba31514ec0fde754c62180fb4b9252328563dab3c0498bf`; all 654 input members matched path, size, and SHA. The fixture archive SHA256 is `08251554658e563c958f1be34e468c1b3658a87f901c15aeb3b252ffbb8402d4`, size 5022; exactly three regular members were extracted and matched the native manifest. Input and process audits are `input-audit.json` and `process-audit.json`.

The live repository was not written. The producer files remain exact. No matching producer processes remain. This report and both audits were written before the output manifest.
